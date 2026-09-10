#!/usr/bin/env python3
"""Record marked ADS1115 A0/A1 evidence until the operator stops the run."""

from __future__ import annotations

import argparse
import csv
import select
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from certarig_edge.hardware.raspberry_pi import ADS1115Reader


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--rate", type=float, default=10.0, help="Paired A0/A1 samples per second")
    parser.add_argument("--bus", type=int, default=1)
    parser.add_argument("--address", type=lambda value: int(value, 0), default=0x48)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.rate <= 0:
        raise SystemExit("rate must be positive")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    adc = ADS1115Reader(args.bus, args.address)
    interval = 1.0 / args.rate
    started = time.monotonic()
    sample_index = 0
    phase = "baseline_switches_off"
    stop_reason = "operator_stop"

    print(
        f"DUAL_LOGGING_IS_ON output={args.output} rate={args.rate:.1f}Hz channels=A0,A1",
        flush=True,
    )
    print("Commands: mark <label> | stop", flush=True)
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
                    "a0_adc_count_derived",
                    "a1_voltage_v",
                    "a1_adc_count_derived",
                ]
            )
            while True:
                readable, _, _ = select.select([sys.stdin], [], [], 0)
                if readable:
                    command = sys.stdin.readline().strip()
                    if command.lower() == "stop":
                        break
                    if command.lower().startswith("mark "):
                        requested = command[5:].strip()
                        if requested:
                            phase = requested.replace(" ", "_")
                            print(f"MARK_SET phase={phase}", flush=True)

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
                        round(a0 * 32768.0 / 4.096),
                        f"{a1:.6f}",
                        round(a1 * 32768.0 / 4.096),
                    ]
                )
                handle.flush()
                sample_index += 1
                sleep_for = interval - ((time.monotonic() - started) % interval)
                time.sleep(max(0.0, sleep_for))
    except KeyboardInterrupt:
        stop_reason = "keyboard_interrupt"
    finally:
        adc.close()

    elapsed = time.monotonic() - started
    print(
        f"DUAL_LOGGING_COMPLETE samples={sample_index} elapsed_s={elapsed:.3f} "
        f"reason={stop_reason} output={args.output}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
