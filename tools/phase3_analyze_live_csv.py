#!/usr/bin/env python3
"""Create a deterministic summary and SVG plot from a Phase 3 live CSV run."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--output-dir", type=Path)
    return parser.parse_args()


def number(row: dict[str, str], key: str) -> float | None:
    try:
        return float(row[key])
    except (KeyError, TypeError, ValueError):
        return None


def stats(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {"min": None, "max": None, "mean": None}
    return {
        "min": round(min(values), 6),
        "max": round(max(values), 6),
        "mean": round(sum(values) / len(values), 6),
    }


def path_for(rows: list[dict[str, str]], key: str, width: int, left: int, right: int, top: int, bottom: int, maximum: float) -> str:
    points = [(number(row, "elapsed_s"), number(row, key)) for row in rows]
    points = [(x, y) for x, y in points if x is not None and y is not None]
    if len(points) < 2:
        return ""
    first = points[0][0]
    last = max(first + 0.001, points[-1][0])
    commands = []
    for index, (x_value, y_value) in enumerate(points):
        x = left + (x_value - first) / (last - first) * (width - left - right)
        y = bottom - max(0.0, min(maximum, y_value)) / maximum * (bottom - top)
        commands.append(f"{'M' if index == 0 else 'L'}{x:.1f},{y:.1f}")
    return " ".join(commands)


def make_svg(rows: list[dict[str, str]]) -> str:
    width, height, left, right = 1200, 520, 70, 30
    pressure_top, pressure_bottom = 55, 225
    flow_top, flow_bottom = 300, 470
    pressure_y = pressure_bottom - 4.2 / 10 * (pressure_bottom - pressure_top)
    flow_y = flow_bottom - 15 / 20 * (flow_bottom - flow_top)
    pressure_path = path_for(rows, "pressure_bar", width, left, right, pressure_top, pressure_bottom, 10)
    flow_path = path_for(rows, "flow_l_min", width, left, right, flow_top, flow_bottom, 20)
    event_lines = []
    elapsed = [number(row, "elapsed_s") for row in rows]
    valid_elapsed = [value for value in elapsed if value is not None]
    first = valid_elapsed[0] if valid_elapsed else 0.0
    last = max(first + 0.001, valid_elapsed[-1] if valid_elapsed else 1.0)
    for row in rows:
        event = row.get("event", "")
        at = number(row, "elapsed_s")
        if not event or at is None:
            continue
        x = left + (at - first) / (last - first) * (width - left - right)
        event_lines.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{pressure_top}" y2="{flow_bottom}" class="event"/><title>{event}</title>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">
<style>text{{font-family:Arial,sans-serif;fill:#33443e}}.grid{{stroke:#dbe4df}}.limit{{stroke:#b34d47;stroke-dasharray:7 6}}.pressure{{fill:none;stroke:#23765a;stroke-width:3}}.flow{{fill:none;stroke:#466f9f;stroke-width:3}}.event{{stroke:#d28a31;stroke-width:1;opacity:.55}}.small{{font-size:14px;fill:#66746f}}.title{{font-size:18px;font-weight:700}}</style>
<rect width="1200" height="520" fill="#f8fbf9" rx="18"/>
<text x="{left}" y="30" class="title">CertaRig Phase 3 live evidence</text>
<text x="{left}" y="49" class="small">Pressure · 4.2 bar deterministic guardrail</text>
<line x1="{left}" x2="{width-right}" y1="{pressure_top}" y2="{pressure_top}" class="grid"/><line x1="{left}" x2="{width-right}" y1="{pressure_bottom}" y2="{pressure_bottom}" class="grid"/>
<line x1="{left}" x2="{width-right}" y1="{pressure_y:.1f}" y2="{pressure_y:.1f}" class="limit"/><path d="{pressure_path}" class="pressure"/>
<text x="{left}" y="294" class="small">Flow · 15 L/min deterministic guardrail</text>
<line x1="{left}" x2="{width-right}" y1="{flow_top}" y2="{flow_top}" class="grid"/><line x1="{left}" x2="{width-right}" y1="{flow_bottom}" y2="{flow_bottom}" class="grid"/>
<line x1="{left}" x2="{width-right}" y1="{flow_y:.1f}" y2="{flow_y:.1f}" class="limit"/><path d="{flow_path}" class="flow"/>
{''.join(event_lines)}
<text x="{left}" y="505" class="small">Orange vertical lines mark recorded events. Relay and lamp fields are command/contact-model expectations unless feedback is fitted.</text>
</svg>'''


def main() -> int:
    args = parse_args()
    rows = list(csv.DictReader(args.csv_path.open(newline="", encoding="utf-8")))
    if not rows:
        raise SystemExit("CSV contains no data rows")
    output_dir = args.output_dir or args.csv_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = args.csv_path.stem
    pressure = [value for row in rows if (value := number(row, "pressure_bar")) is not None]
    flow = [value for row in rows if (value := number(row, "flow_l_min")) is not None]
    events = Counter(row.get("event", "") for row in rows if row.get("event", ""))
    forced_safe = [row for row in rows if row.get("event", "").endswith("forced_safe")]
    latencies: list[float] = []
    for index, row in enumerate(rows):
        if not row.get("event", "").endswith("forced_safe"):
            continue
        at = number(row, "elapsed_s")
        for previous in reversed(rows[:index]):
            if previous.get("gpio23_command_high") == "true":
                before = number(previous, "elapsed_s")
                if at is not None and before is not None:
                    latencies.append(max(0.0, at - before))
                break
    summary = {
        "source_csv": args.csv_path.name,
        "sha256": hashlib.sha256(args.csv_path.read_bytes()).hexdigest(),
        "rows": len(rows),
        "duration_s": round((number(rows[-1], "elapsed_s") or 0) - (number(rows[0], "elapsed_s") or 0), 6),
        "pressure_bar": stats(pressure),
        "flow_l_min": stats(flow),
        "events": dict(sorted(events.items())),
        "forced_safe_events": len(forced_safe),
        "trip_latency_s": stats(latencies),
        "final_gpio23_command_high": rows[-1].get("gpio23_command_high"),
        "final_trip_latched": rows[-1].get("trip_latched"),
    }
    json_path = output_dir / f"{stem}_analysis.json"
    md_path = output_dir / f"{stem}_analysis.md"
    svg_path = output_dir / f"{stem}_plot.svg"
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(
        "\n".join(
            [
                f"# CertaRig live-run analysis: {args.csv_path.name}",
                "",
                f"- Samples: {summary['rows']}",
                f"- Duration: {summary['duration_s']} s",
                f"- Pressure range: {summary['pressure_bar']['min']} to {summary['pressure_bar']['max']} bar",
                f"- Flow range: {summary['flow_l_min']['min']} to {summary['flow_l_min']['max']} L/min",
                f"- Forced-safe events: {summary['forced_safe_events']}",
                f"- Trip latency range: {summary['trip_latency_s']['min']} to {summary['trip_latency_s']['max']} s",
                f"- Final GPIO23 command high: {summary['final_gpio23_command_high']}",
                f"- Final trip latched: {summary['final_trip_latched']}",
                f"- Source SHA256: `{summary['sha256']}`",
                "",
                "Relay and indicator states in the CSV are expected values derived from the command and K1 contact model. They are not physical feedback measurements.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    svg_path.write_text(make_svg(rows), encoding="utf-8")
    print(json.dumps({"analysis": str(json_path), "report": str(md_path), "plot": str(svg_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
