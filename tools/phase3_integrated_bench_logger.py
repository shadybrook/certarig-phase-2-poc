#!/usr/bin/env python3
"""Record Phase 3 analogue, E-stop, and explicitly armed GPIO23 evidence."""

from __future__ import annotations

import argparse
import csv
import json
import select
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from certarig_edge.commissioning import DryBenchInterlock
from certarig_edge.hardware.raspberry_pi import ADS1115Reader


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--config", type=Path, default=Path("config/rig.wave1.json"))
    parser.add_argument("--rate", type=float, default=10.0)
    parser.add_argument("--allow-output", action="store_true")
    parser.add_argument(
        "--acknowledge-dry-bench",
        action="store_true",
        help="Required with --allow-output; confirms low-voltage indicator-only scope",
    )
    return parser.parse_args()


def scale(voltage: float, channel: dict[str, object]) -> float:
    raw_min = float(channel["raw_min_v"])
    raw_max = float(channel["raw_max_v"])
    engineering_min = float(channel["engineering_min"])
    engineering_max = float(channel["engineering_max"])
    return engineering_min + (voltage - raw_min) / (raw_max - raw_min) * (
        engineering_max - engineering_min
    )


def main() -> int:
    args = parse_args()
    if args.rate <= 0:
        raise SystemExit("--rate must be positive")
    if args.allow_output and not args.acknowledge_dry_bench:
        raise SystemExit("--allow-output requires --acknowledge-dry-bench")

    config = json.loads(args.config.read_text(encoding="utf-8"))
    hardware = config["hardware"]
    channels = {int(item["adc_channel"]): item for item in config["channels"]}
    if int(hardware["valve_output_gpio"]) != 23:
        raise SystemExit("Wave 1 commissioning requires BCM GPIO23 for the relay command")
    if int(hardware["emergency_stop_gpio"]) != 24:
        raise SystemExit("Wave 1 commissioning requires BCM GPIO24 for E-stop sense")
    if hardware.get("relay_feedback_gpio") is not None:
        raise SystemExit("relay_feedback_gpio must remain null for this commissioning stage")
    if not bool(hardware.get("emergency_stop_active_high")):
        raise SystemExit("Wave 1 requires HIGH/open to mean E-stop active")

    try:
        from gpiozero import DigitalInputDevice, OutputDevice
    except ImportError as exc:
        raise SystemExit("gpiozero is required; run this logger on the Raspberry Pi") from exc

    args.output.parent.mkdir(parents=True, exist_ok=True)
    output = OutputDevice(23, active_high=True, initial_value=False)
    estop = DigitalInputDevice(24, pull_up=True, bounce_time=0.02)
    adc = ADS1115Reader(int(hardware["i2c_bus"]), int(hardware["ads1115_address"]))
    interlock = DryBenchInterlock(allow_output=args.allow_output)
    phase = "boot_safe"
    interval = 1.0 / args.rate
    started = time.monotonic()
    sample_index = 0
    pending_event = "logger_started_output_safe"
    stop_reason = "operator_stop"

    print(
        "INTEGRATED_LOGGING_IS_ON "
        f"mode={'armed' if args.allow_output else 'monitor_only'} output={args.output}",
        flush=True,
    )
    print("Commands: mark <label> | safe | reset | permit | stop", flush=True)
    print("A permit never re-arms automatically after an E-stop/open-loop event.", flush=True)

    try:
        with args.output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(
                [
                    "sample_index",
                    "timestamp_utc",
                    "elapsed_s",
                    "phase",
                    "a0_voltage_v",
                    "pressure_emulator_bar",
                    "a1_voltage_v",
                    "flow_emulator_l_min",
                    "gpio24_raw_level",
                    "estop_active",
                    "permit_requested",
                    "trip_latched",
                    "gpio23_command_high",
                    "event",
                ]
            )
            while True:
                # Read the electrical GPIO level. DigitalInputDevice.value is
                # inverted by gpiozero when pull_up=True.
                raw_high = bool(estop.pin.state)
                observed = interlock.observe(raw_high)
                if observed.event:
                    pending_event = observed.event
                    print(f"INTERLOCK_EVENT {observed.event}", flush=True)

                readable, _, _ = select.select([sys.stdin], [], [], 0)
                if readable:
                    command = sys.stdin.readline().strip()
                    lowered = command.lower()
                    if lowered == "stop":
                        break
                    if lowered.startswith("mark "):
                        label = command[5:].strip()
                        if label:
                            phase = label.replace(" ", "_")
                            pending_event = f"mark:{phase}"
                            print(f"MARK_SET phase={phase}", flush=True)
                    elif lowered in {"safe", "reset", "permit"}:
                        result = interlock.command(lowered)
                        pending_event = result.event
                        print(
                            f"COMMAND_RESULT command={lowered} event={result.event} "
                            f"drive_high={result.drive_high}",
                            flush=True,
                        )
                    elif command:
                        pending_event = "unknown_command"
                        print("UNKNOWN_COMMAND", flush=True)

                if interlock.drive_high:
                    output.on()
                else:
                    output.off()

                elapsed = time.monotonic() - started
                a0 = adc.read_voltage(0)
                a1 = adc.read_voltage(1)
                writer.writerow(
                    [
                        sample_index,
                        datetime.now(timezone.utc).isoformat(),
                        f"{elapsed:.6f}",
                        phase,
                        f"{a0:.6f}",
                        f"{scale(a0, channels[0]):.5f}",
                        f"{a1:.6f}",
                        f"{scale(a1, channels[1]):.5f}",
                        "HIGH" if raw_high else "LOW",
                        str(raw_high).lower(),
                        str(interlock.permit_requested).lower(),
                        str(interlock.trip_latched).lower(),
                        str(bool(output.value)).lower(),
                        pending_event,
                    ]
                )
                pending_event = ""
                handle.flush()
                sample_index += 1
                sleep_for = interval - ((time.monotonic() - started) % interval)
                time.sleep(max(0.0, sleep_for))
    except KeyboardInterrupt:
        stop_reason = "keyboard_interrupt"
    finally:
        output.off()
        adc.close()
        estop.close()
        output.close()

    print(
        f"INTEGRATED_LOGGING_COMPLETE samples={sample_index} reason={stop_reason} "
        f"output={args.output} gpio23_final=LOW",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
