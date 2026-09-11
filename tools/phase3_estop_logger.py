#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import signal
import time
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Log the fail-safe CertaRig E-stop sense input without commanding an output."
    )
    parser.add_argument("--gpio", type=int, default=24, help="BCM GPIO number; default 24")
    parser.add_argument("--rate-hz", type=float, default=20.0, help="Sample rate; default 20 Hz")
    parser.add_argument(
        "--duration",
        type=float,
        default=0.0,
        help="Seconds to record; 0 records until Control-C",
    )
    parser.add_argument("--output", type=Path, default=Path("phase3-estop-input.csv"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.rate_hz <= 0:
        raise SystemExit("--rate-hz must be greater than zero")
    if args.duration < 0:
        raise SystemExit("--duration may not be negative")

    try:
        from gpiozero import DigitalInputDevice
    except ImportError as exc:
        raise SystemExit("gpiozero is required; run this script on the Raspberry Pi") from exc

    stop = False

    def request_stop(_signum: int, _frame: object) -> None:
        nonlocal stop
        stop = True

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)

    sensor = DigitalInputDevice(args.gpio, pull_up=True, bounce_time=0.02)
    interval = 1.0 / args.rate_hz
    start = time.monotonic()
    next_sample = start
    index = 0
    last_state: str | None = None
    args.output.parent.mkdir(parents=True, exist_ok=True)

    print("LOGGING ACTIVE: GPIO LOW=healthy; GPIO HIGH/open=E-stop active")
    print("No output GPIO is commanded by this logger. Press Control-C to stop.")

    try:
        with args.output.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(
                ["sample", "elapsed_s", "captured_at_utc", "gpio_bcm", "raw_level", "estop_active"]
            )
            while not stop:
                now = time.monotonic()
                elapsed = now - start
                if args.duration and elapsed >= args.duration:
                    break
                # Read the electrical GPIO level. DigitalInputDevice.value is
                # inverted by gpiozero when pull_up=True.
                raw_high = bool(sensor.pin.state)
                state = "active" if raw_high else "healthy"
                writer.writerow(
                    [
                        index,
                        f"{elapsed:.6f}",
                        datetime.now(timezone.utc).isoformat(),
                        args.gpio,
                        "HIGH" if raw_high else "LOW",
                        "true" if raw_high else "false",
                    ]
                )
                if state != last_state:
                    print(f"{elapsed:8.3f}s  {state.upper()}  raw={'HIGH' if raw_high else 'LOW'}")
                    last_state = state
                index += 1
                next_sample += interval
                time.sleep(max(0.0, next_sample - time.monotonic()))
            stream.flush()
    finally:
        sensor.close()

    print(f"LOGGING STOPPED: {index} samples saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
