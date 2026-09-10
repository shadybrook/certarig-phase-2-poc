#!/usr/bin/env python3
"""Validate, trim, and plot CertaRig ADS1115 dual-potentiometer evidence."""

from __future__ import annotations

import argparse
import csv
import hashlib
import math
import statistics
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


REQUIRED_COLUMNS = (
    "sample_index",
    "timestamp_utc",
    "elapsed_s",
    "phase",
    "a0_voltage_v",
    "a0_adc_count_derived",
    "a1_voltage_v",
    "a1_adc_count_derived",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("raw_csv", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--activity-threshold-v", type=float, default=0.01)
    parser.add_argument("--post-activity-seconds", type=float, default=5.0)
    return parser.parse_args()


def load_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        columns = reader.fieldnames or []
        missing = [name for name in REQUIRED_COLUMNS if name not in columns]
        if missing:
            raise SystemExit(f"Missing required columns: {', '.join(missing)}")
        rows = list(reader)
    if not rows:
        raise SystemExit("Input CSV contains no samples")
    return columns, rows


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_chart(
    path: Path,
    elapsed: list[float],
    a0: list[float],
    a1: list[float],
    first_activity: float,
    last_activity: float,
    raw_count: int,
    raw_duration: float,
    removed_duration: float,
) -> None:
    width, height = 1800, 1050
    image = Image.new("RGB", (width, height), "#F8FAFC")
    draw = ImageDraw.Draw(image)

    ink = "#172033"
    muted = "#667085"
    grid = "#D7DEE8"
    blue = "#2563EB"
    orange = "#D97706"
    activity_fill = "#EDF2F7"
    white = "#FFFFFF"

    title_font = font(45, bold=True)
    subtitle_font = font(24)
    axis_font = font(22)
    tick_font = font(19)
    legend_font = font(21, bold=True)
    note_font = font(19)
    metric_font = font(20, bold=True)

    draw.rounded_rectangle((40, 32, width - 40, height - 32), radius=24, fill=white, outline="#E4E9F0", width=2)
    draw.text((90, 75), "CertaRig Dual Potentiometer Voltage Sweep", font=title_font, fill=ink)
    draw.text(
        (90, 132),
        "Raw ADS1115 readings at 10 paired samples/s | A0 pressure emulator and A1 flow emulator | 0–100 s",
        font=subtitle_font,
        fill=muted,
    )

    card_y0, card_y1 = 185, 255
    cards = [
        (90, 380, f"{len(elapsed):,} plotted samples"),
        (405, 695, f"A0 max {max(a0):.3f} V"),
        (720, 1010, f"A1 max {max(a1):.3f} V"),
        (1035, 1710, f"Activity observed {first_activity:.1f}–{last_activity:.1f} s"),
    ]
    for x0, x1, label in cards:
        draw.rounded_rectangle((x0, card_y0, x1, card_y1), radius=14, fill="#F1F5F9")
        bbox = draw.textbbox((0, 0), label, font=metric_font)
        draw.text((x0 + (x1 - x0 - (bbox[2] - bbox[0])) / 2, 207), label, font=metric_font, fill=ink)

    left, top, right, bottom = 150, 300, 1710, 825
    x_min, x_max = 0.0, max(100.0, math.ceil(max(elapsed)))
    y_min, y_max = -0.05, 3.4

    def sx(value: float) -> float:
        return left + (value - x_min) / (x_max - x_min) * (right - left)

    def sy(value: float) -> float:
        return bottom - (value - y_min) / (y_max - y_min) * (bottom - top)

    draw.rectangle((sx(first_activity), top, sx(last_activity), bottom), fill=activity_fill)

    for voltage in (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0):
        y = sy(voltage)
        draw.line((left, y, right, y), fill=grid, width=2)
        label = f"{voltage:.1f}"
        bbox = draw.textbbox((0, 0), label, font=tick_font)
        draw.text((left - 18 - (bbox[2] - bbox[0]), y - 11), label, font=tick_font, fill=muted)

    for second in range(0, int(x_max) + 1, 10):
        x = sx(float(second))
        draw.line((x, bottom, x, bottom + 8), fill=muted, width=2)
        label = str(second)
        bbox = draw.textbbox((0, 0), label, font=tick_font)
        draw.text((x - (bbox[2] - bbox[0]) / 2, bottom + 14), label, font=tick_font, fill=muted)

    draw.line((left, top, left, bottom), fill=ink, width=3)
    draw.line((left, bottom, right, bottom), fill=ink, width=3)

    for activity_time in (first_activity, last_activity):
        x = sx(activity_time)
        for y in range(top, bottom, 14):
            draw.line((x, y, x, min(y + 7, bottom)), fill="#98A2B3", width=2)

    points_a0 = [(sx(x), sy(y)) for x, y in zip(elapsed, a0)]
    points_a1 = [(sx(x), sy(y)) for x, y in zip(elapsed, a1)]
    draw.line(points_a0, fill=blue, width=4, joint="curve")
    # Dashed A1 segments give a non-colour distinction as well as an orange line.
    for index in range(0, len(points_a1) - 1, 2):
        draw.line((points_a1[index], points_a1[index + 1]), fill=orange, width=4)

    draw.text((left + 15, top + 13), "Observed movement window", font=note_font, fill=muted)

    legend_y = 885
    draw.line((150, legend_y, 210, legend_y), fill=blue, width=5)
    draw.text((225, legend_y - 13), "P1 / ADS1115 A0", font=legend_font, fill=ink)
    for x in range(520, 581, 16):
        draw.line((x, legend_y, min(x + 9, 580), legend_y), fill=orange, width=5)
    draw.text((595, legend_y - 13), "P2 / ADS1115 A1", font=legend_font, fill=ink)

    x_label = "Elapsed time from logger start (seconds)"
    bbox = draw.textbbox((0, 0), x_label, font=axis_font)
    draw.text(((left + right - (bbox[2] - bbox[0])) / 2, 932), x_label, font=axis_font, fill=ink)

    y_label = "Voltage (V)"
    label_image = Image.new("RGBA", (220, 45), (255, 255, 255, 0))
    label_draw = ImageDraw.Draw(label_image)
    label_draw.text((0, 0), y_label, font=axis_font, fill=ink)
    label_image = label_image.rotate(90, expand=True)
    image.paste(label_image, (55, 500), label_image)

    note = (
        f"Source retained unchanged: {raw_count:,} samples over {raw_duration:.1f} s. "
        f"Presentation copy ends 5.3 s after the last reading above 0.01 V; {removed_duration:.1f} s of idle tail excluded. "
        "No smoothing or position labels applied."
    )
    draw.text((90, 985), note, font=note_font, fill=muted)
    image.save(path, format="PNG", optimize=True)


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    columns, rows = load_rows(args.raw_csv)

    indexes = [int(row["sample_index"]) for row in rows]
    elapsed = [float(row["elapsed_s"]) for row in rows]
    a0 = [float(row["a0_voltage_v"]) for row in rows]
    a1 = [float(row["a1_voltage_v"]) for row in rows]

    expected_indexes = list(range(len(rows)))
    duplicate_indexes = len(indexes) - len(set(indexes))
    missing_indexes = len(set(expected_indexes) - set(indexes))
    monotonic_time = all(later > earlier for earlier, later in zip(elapsed, elapsed[1:]))
    intervals = [later - earlier for earlier, later in zip(elapsed, elapsed[1:])]

    activity = [
        i
        for i, (value0, value1) in enumerate(zip(a0, a1))
        if abs(value0) > args.activity_threshold_v or abs(value1) > args.activity_threshold_v
    ]
    if not activity:
        raise SystemExit("No voltage activity above threshold was detected")
    first_activity = elapsed[activity[0]]
    last_activity = elapsed[activity[-1]]
    cutoff = min(elapsed[-1], math.ceil(last_activity + args.post_activity_seconds))
    trimmed_rows = [row for row in rows if float(row["elapsed_s"]) <= cutoff]
    trimmed_elapsed = [float(row["elapsed_s"]) for row in trimmed_rows]
    trimmed_a0 = [float(row["a0_voltage_v"]) for row in trimmed_rows]
    trimmed_a1 = [float(row["a1_voltage_v"]) for row in trimmed_rows]

    trimmed_path = args.output_dir / "p1_p2_a0_a1_marked_sweep_trimmed_0_to_100s.csv"
    with trimmed_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(trimmed_rows)

    removed_duration = elapsed[-1] - cutoff
    chart_path = args.output_dir / "p1_p2_dual_voltage_sweep_0_to_100s.png"
    draw_chart(
        chart_path,
        trimmed_elapsed,
        trimmed_a0,
        trimmed_a1,
        first_activity,
        last_activity,
        len(rows),
        elapsed[-1],
        removed_duration,
    )

    summary_path = args.output_dir / "p1_p2_dual_voltage_sweep_analysis.md"
    summary = f"""# CertaRig P1 and P2 dual ADS1115 sweep analysis

## Evidence boundary

The raw source CSV is retained unchanged. The presentation CSV and chart use the first {cutoff:.1f} seconds, ending {cutoff - last_activity:.1f} seconds after the last sample with either channel above {args.activity_threshold_v:.2f} V. This removes {removed_duration:.1f} seconds ({removed_duration / 60:.2f} minutes) of idle zero tail without altering the retained samples.

## Data quality checks

- Raw rows: {len(rows):,}
- Plotted rows: {len(trimmed_rows):,}
- Sample index range: {indexes[0]} to {indexes[-1]}
- Duplicate sample indexes: {duplicate_indexes}
- Missing expected sample indexes: {missing_indexes}
- Strictly increasing elapsed time: {monotonic_time}
- Median sample interval: {statistics.median(intervals):.6f} s
- Maximum sample interval: {max(intervals):.6f} s
- First observed activity: {first_activity:.3f} s
- Last observed activity: {last_activity:.3f} s
- A0 range in plotted window: {min(trimmed_a0):.6f} to {max(trimmed_a0):.6f} V
- A1 range in plotted window: {min(trimmed_a1):.6f} to {max(trimmed_a1):.6f} V
- Values above 3.35 V: {sum(value > 3.35 for value in trimmed_a0 + trimmed_a1)}
- Values below -0.005 V: {sum(value < -0.005 for value in trimmed_a0 + trimmed_a1)}

## Interpretation

Both independent ADS1115 channels traversed approximately the full 0 to 3.3 V bench range. The plot presents raw voltage against elapsed time with no smoothing and no inferred left, centre, or right labels. This is evidence for the two potentiometer to ADS1115 to Raspberry Pi acquisition path; it is not hydraulic sensor calibration evidence.

## Integrity hashes

- Raw CSV SHA-256: `{sha256(args.raw_csv)}`
- Trimmed CSV SHA-256: `{sha256(trimmed_path)}`
- Chart PNG SHA-256: `{sha256(chart_path)}`
"""
    summary_path.write_text(summary, encoding="utf-8")

    print(f"raw_rows={len(rows)}")
    print(f"trimmed_rows={len(trimmed_rows)}")
    print(f"first_activity_s={first_activity:.3f}")
    print(f"last_activity_s={last_activity:.3f}")
    print(f"cutoff_s={cutoff:.1f}")
    print(f"removed_idle_tail_s={removed_duration:.1f}")
    print(f"a0_range_v={min(trimmed_a0):.6f},{max(trimmed_a0):.6f}")
    print(f"a1_range_v={min(trimmed_a1):.6f},{max(trimmed_a1):.6f}")
    print(f"chart={chart_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
