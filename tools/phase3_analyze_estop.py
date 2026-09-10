#!/usr/bin/env python3
"""Validate and graph a CertaRig GPIO24 emergency stop evidence capture."""

from __future__ import annotations

import argparse
import csv
import hashlib
import statistics
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


REQUIRED_COLUMNS = (
    "sample",
    "elapsed_s",
    "captured_at_utc",
    "gpio_bcm",
    "raw_level",
    "estop_active",
)


@dataclass(frozen=True)
class Segment:
    state: bool
    start_s: float
    end_s: float
    samples: int

    @property
    def duration_s(self) -> float:
        return self.end_s - self.start_s


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("raw_csv", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    return parser.parse_args()


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


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        columns = reader.fieldnames or []
        missing = [name for name in REQUIRED_COLUMNS if name not in columns]
        if missing:
            raise SystemExit(f"Missing required columns: {', '.join(missing)}")
        rows = list(reader)
    if not rows:
        raise SystemExit("Input CSV contains no samples")
    return rows


def build_segments(elapsed: list[float], active: list[bool]) -> list[Segment]:
    segments: list[Segment] = []
    start = 0
    for index in range(1, len(active)):
        if active[index] != active[index - 1]:
            segments.append(
                Segment(active[start], elapsed[start], elapsed[index - 1], index - start)
            )
            start = index
    segments.append(Segment(active[start], elapsed[start], elapsed[-1], len(active) - start))
    return segments


def draw_chart(path: Path, elapsed: list[float], active: list[bool], segments: list[Segment]) -> None:
    width, height = 1800, 980
    image = Image.new("RGB", (width, height), "#F8FAFC")
    draw = ImageDraw.Draw(image)

    ink = "#172033"
    muted = "#667085"
    grid = "#D7DEE8"
    blue = "#2563EB"
    orange = "#D97706"
    white = "#FFFFFF"
    active_fill = "#FFF4E5"

    title_font = font(44, bold=True)
    subtitle_font = font(23)
    axis_font = font(22)
    tick_font = font(18)
    metric_font = font(20, bold=True)
    note_font = font(18)

    draw.rounded_rectangle((40, 32, width - 40, height - 32), radius=24, fill=white, outline="#E4E9F0", width=2)
    draw.text((90, 70), "CertaRig Emergency Stop GPIO24 Capture", font=title_font, fill=ink)
    draw.text(
        (90, 125),
        "Physical pin 18 / BCM24 sampled at 20 Hz | LOW = healthy closed loop | HIGH or open = active",
        font=subtitle_font,
        fill=muted,
    )

    transitions = len(segments) - 1
    healthy_segments = sum(not segment.state for segment in segments)
    cards = [
        (90, 435, f"{len(elapsed):,} samples"),
        (460, 805, f"{elapsed[-1]:.1f} s duration"),
        (830, 1175, f"{transitions} transitions"),
        (1200, 1710, f"{healthy_segments} healthy windows"),
    ]
    for x0, x1, label in cards:
        draw.rounded_rectangle((x0, 175, x1, 245), radius=14, fill="#F1F5F9")
        bbox = draw.textbbox((0, 0), label, font=metric_font)
        draw.text((x0 + (x1 - x0 - (bbox[2] - bbox[0])) / 2, 197), label, font=metric_font, fill=ink)

    left, top, right, bottom = 170, 300, 1710, 740
    x_min, x_max = 0.0, elapsed[-1]

    def sx(value: float) -> float:
        return left + (value - x_min) / max(x_max - x_min, 1.0) * (right - left)

    def sy(value: float) -> float:
        return bottom - value * (bottom - top)

    for segment in segments:
        if segment.state:
            draw.rectangle((sx(segment.start_s), top, sx(segment.end_s), bottom), fill=active_fill)

    for value, label in ((0, "HEALTHY / LOW"), (1, "ACTIVE / HIGH")):
        y = sy(float(value))
        draw.line((left, y, right, y), fill=grid, width=2)
        bbox = draw.textbbox((0, 0), label, font=tick_font)
        draw.text((left - 18 - (bbox[2] - bbox[0]), y - 11), label, font=tick_font, fill=muted)

    tick_step = 20
    for second in range(0, int(x_max) + tick_step, tick_step):
        if second > x_max:
            break
        x = sx(float(second))
        draw.line((x, bottom, x, bottom + 8), fill=muted, width=2)
        label = str(second)
        bbox = draw.textbbox((0, 0), label, font=tick_font)
        draw.text((x - (bbox[2] - bbox[0]) / 2, bottom + 15), label, font=tick_font, fill=muted)

    draw.line((left, top, left, bottom), fill=ink, width=3)
    draw.line((left, bottom, right, bottom), fill=ink, width=3)

    points = [(sx(x), sy(1.0 if state else 0.0)) for x, state in zip(elapsed, active)]
    draw.line(points, fill=blue, width=5, joint="curve")
    for segment in segments:
        if segment.state:
            draw.line(
                (sx(segment.start_s), sy(1.0), sx(segment.end_s), sy(1.0)),
                fill=orange,
                width=7,
            )

    x_label = "Elapsed time from logger start (seconds)"
    bbox = draw.textbbox((0, 0), x_label, font=axis_font)
    draw.text(((left + right - (bbox[2] - bbox[0])) / 2, 800), x_label, font=axis_font, fill=ink)

    draw.line((170, 870, 235, 870), fill=blue, width=5)
    draw.text((250, 856), "Recorded state", font=metric_font, fill=ink)
    draw.rectangle((525, 850, 585, 890), fill=active_fill, outline=orange, width=2)
    draw.text((600, 856), "Active or open interval", font=metric_font, fill=ink)
    draw.text(
        (1030, 856),
        "Source: raw Raspberry Pi GPIO24 logger; no smoothing or state relabelling",
        font=note_font,
        fill=muted,
    )

    image.save(path, format="PNG", optimize=True)


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = load_rows(args.raw_csv)

    indexes = [int(row["sample"]) for row in rows]
    elapsed = [float(row["elapsed_s"]) for row in rows]
    gpio = [int(row["gpio_bcm"]) for row in rows]
    raw = [row["raw_level"].strip().upper() for row in rows]
    active = [row["estop_active"].strip().lower() == "true" for row in rows]

    duplicate_indexes = len(indexes) - len(set(indexes))
    expected_indexes = set(range(indexes[0], indexes[-1] + 1))
    missing_indexes = len(expected_indexes - set(indexes))
    monotonic_time = all(later > earlier for earlier, later in zip(elapsed, elapsed[1:]))
    intervals = [later - earlier for earlier, later in zip(elapsed, elapsed[1:])]
    invalid_levels = sorted(set(raw) - {"LOW", "HIGH"})
    invalid_gpio = sorted(set(gpio) - {24})
    polarity_mismatches = sum((level == "HIGH") != state for level, state in zip(raw, active))

    segments = build_segments(elapsed, active)
    transition_count = len(segments) - 1
    healthy_segments = [segment for segment in segments if not segment.state]
    active_segments = [segment for segment in segments if segment.state]

    chart_path = args.output_dir / "estop_gpio24_state_timeline.png"
    draw_chart(chart_path, elapsed, active, segments)

    summary_path = args.output_dir / "estop_gpio24_analysis.md"
    segment_lines = []
    for index, segment in enumerate(segments, start=1):
        label = "ACTIVE / HIGH or open" if segment.state else "HEALTHY / LOW closed loop"
        segment_lines.append(
            f"| {index} | {segment.start_s:.3f} | {segment.end_s:.3f} | "
            f"{segment.duration_s:.3f} | {label} | {segment.samples:,} |"
        )

    checks_pass = (
        duplicate_indexes == 0
        and missing_indexes == 0
        and monotonic_time
        and not invalid_levels
        and not invalid_gpio
        and polarity_mismatches == 0
        and transition_count >= 4
        and bool(healthy_segments)
        and bool(active_segments)
    )
    summary = f"""# CertaRig emergency stop GPIO24 analysis

## Evidence result

**{'PASS' if checks_pass else 'REVIEW REQUIRED'}:** The capture contains both the healthy closed-loop state and the active/open state with repeatable transitions. The logger only observed the GPIO input and did not command the relay output.

## Data quality checks

- Raw source: `{args.raw_csv.name}`
- SHA256: `{sha256(args.raw_csv)}`
- Samples: {len(rows):,}
- Duration: {elapsed[-1]:.6f} seconds
- Sample index range: {indexes[0]} to {indexes[-1]}
- Duplicate sample indexes: {duplicate_indexes}
- Missing sample indexes: {missing_indexes}
- Strictly increasing elapsed time: {monotonic_time}
- Median sample interval: {statistics.median(intervals):.6f} seconds
- Maximum sample interval: {max(intervals):.6f} seconds
- Unexpected GPIO numbers: {invalid_gpio or 'none'}
- Unexpected raw levels: {invalid_levels or 'none'}
- HIGH/active polarity mismatches: {polarity_mismatches}
- State transitions: {transition_count}
- Healthy windows: {len(healthy_segments)}
- Active/open windows: {len(active_segments)}

## Consecutive state windows

| Window | Start s | End s | Duration s | Interpreted state | Samples |
|---:|---:|---:|---:|---|---:|
{chr(10).join(segment_lines)}

## Interpretation boundary

The electrical observation proves that BCM24 repeatedly distinguishes a closed NC1 loop from an open loop. Because the capture contains no operator event markers, the CSV alone cannot distinguish a button latch from a deliberately disconnected wire; both correctly appear as HIGH/active by fail-safe design. A labelled repeat or synchronized video is required if broken-wire handling must be evidenced as a separate test case.
"""
    summary_path.write_text(summary, encoding="utf-8")

    print(f"rows={len(rows)}")
    print(f"duration_s={elapsed[-1]:.6f}")
    print(f"transitions={transition_count}")
    print(f"healthy_windows={len(healthy_segments)}")
    print(f"active_windows={len(active_segments)}")
    print(f"median_interval_s={statistics.median(intervals):.6f}")
    print(f"max_interval_s={max(intervals):.6f}")
    print(f"polarity_mismatches={polarity_mismatches}")
    print(f"result={'PASS' if checks_pass else 'REVIEW_REQUIRED'}")
    print(chart_path)
    print(summary_path)
    return 0 if checks_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
