from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path("work/report_assets")
OUT.mkdir(parents=True, exist_ok=True)

INK = "#17221f"
MUTED = "#5c6d67"
GREEN = "#0d7a55"
GREEN_LIGHT = "#e5f4ec"
BLUE_LIGHT = "#eaf2f8"
ORANGE_LIGHT = "#fff0e5"
LINE = "#cbd7d2"
WHITE = "#ffffff"

FONT_REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


def font(size: int, bold: bool = False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REGULAR, size)


def rounded_box(draw, xy, title, subtitle, fill, outline=LINE, title_size=30, subtitle_size=22):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=24, fill=fill, outline=outline, width=3)
    draw.text((x1 + 28, y1 + 24), title, font=font(title_size, True), fill=INK)
    if subtitle:
        lines = wrap_text(draw, subtitle, font(subtitle_size), x2 - x1 - 56)
        draw.multiline_text((x1 + 28, y1 + 68), lines, font=font(subtitle_size), fill=MUTED, spacing=6)


def wrap_text(draw, text, text_font, width):
    words = text.split()
    lines = []
    current = []
    for word in words:
        candidate = " ".join(current + [word])
        if draw.textbbox((0, 0), candidate, font=text_font)[2] <= width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return "\n".join(lines)


def arrow(draw, start, end, label=None):
    sx, sy = start
    ex, ey = end
    draw.line((sx, sy, ex, ey), fill=GREEN, width=5)
    if abs(ex - sx) >= abs(ey - sy):
        direction = 1 if ex > sx else -1
        points = [(ex, ey), (ex - direction * 18, ey - 10), (ex - direction * 18, ey + 10)]
    else:
        direction = 1 if ey > sy else -1
        points = [(ex, ey), (ex - 10, ey - direction * 18), (ex + 10, ey - direction * 18)]
    draw.polygon(points, fill=GREEN)
    if label:
        mx, my = (sx + ex) / 2, (sy + ey) / 2
        box = draw.textbbox((0, 0), label, font=font(19, True))
        w, h = box[2] - box[0], box[3] - box[1]
        draw.rounded_rectangle((mx - w / 2 - 10, my - h / 2 - 7, mx + w / 2 + 10, my + h / 2 + 7), radius=10, fill=WHITE)
        draw.text((mx - w / 2, my - h / 2), label, font=font(19, True), fill=GREEN)


def build_architecture():
    image = Image.new("RGB", (1800, 1080), WHITE)
    draw = ImageDraw.Draw(image)
    draw.text((90, 64), "CertaRig system architecture", font=font(52, True), fill=INK)
    draw.text((90, 126), "AI assisted reasoning remains separate from deterministic execution and independent safety.", font=font(25), fill=MUTED)

    rounded_box(draw, (570, 210, 1230, 360), "Browser review interface", "Rig map, plan, telemetry, alarms, evidence, and human approval", BLUE_LIGHT)
    arrow(draw, (900, 360), (900, 425), "review and approval")

    service_titles = ["Discovery", "Rig model", "Experiment", "Diagnosis"]
    service_subtitles = [
        "Collects configuration and channel evidence",
        "Maintains versions, limits, and confidence",
        "Compiles a bounded commissioning plan",
        "Compares expected and measured response",
    ]
    for index, (title, subtitle) in enumerate(zip(service_titles, service_subtitles)):
        x1 = 90 + index * 420
        rounded_box(draw, (x1, 440, x1 + 360, 620), title, subtitle, GREEN_LIGHT)

    arrow(draw, (900, 620), (900, 695), "validated plan only")

    rounded_box(draw, (130, 720, 610, 930), "Versioned evidence store", "Rig graph, source records, plans, telemetry, decisions, code and configuration versions", "#f5f7f6")
    rounded_box(draw, (660, 720, 1140, 930), "Deterministic runtime", "State machine, schema checks, timeout, abort, replay, and safe default output", "#f5f7f6")
    rounded_box(draw, (1190, 720, 1670, 930), "Independent safety boundary", "Output limits, emergency cutoff, relief path, fuse, and protected driver", ORANGE_LIGHT, outline="#e6c5ad")

    arrow(draw, (610, 825), (660, 825))
    arrow(draw, (1140, 825), (1190, 825))
    draw.text((90, 1005), "Phase 2 PoC boundary: synthetic browser simulator with no live controller or actuator connection.", font=font(23, True), fill=GREEN)
    image.save(OUT / "architecture_diagram.png", quality=95)


def build_data_flow():
    image = Image.new("RGB", (1800, 980), WHITE)
    draw = ImageDraw.Draw(image)
    draw.text((90, 64), "CertaRig data flow", font=font(52, True), fill=INK)
    draw.text((90, 126), "A traceable path from source records to a reviewed evidence bundle.", font=font(25), fill=MUTED)

    stages = [
        ("1. Ingest", "Configuration, calibration, procedures, telemetry"),
        ("2. Normalize", "Typed devices, channels, units, ranges, limits"),
        ("3. Compare", "Version changes and invalidated evidence"),
        ("4. Plan", "Prerequisites, checks, acceptance and abort rules"),
        ("5. Execute", "Deterministic states and simulated measurements"),
        ("6. Report", "Outcome, diagnosis, evidence and unresolved items"),
    ]
    coordinates = [
        (90, 230, 540, 420),
        (675, 230, 1125, 420),
        (1260, 230, 1710, 420),
        (1260, 575, 1710, 765),
        (675, 575, 1125, 765),
        (90, 575, 540, 765),
    ]
    fills = [BLUE_LIGHT, GREEN_LIGHT, "#f5f7f6", GREEN_LIGHT, BLUE_LIGHT, "#f5f7f6"]
    for stage, xy, fill in zip(stages, coordinates, fills):
        rounded_box(draw, xy, stage[0], stage[1], fill)

    arrow(draw, (540, 325), (675, 325))
    arrow(draw, (1125, 325), (1260, 325))
    arrow(draw, (1485, 420), (1485, 575))
    arrow(draw, (1260, 670), (1125, 670))
    arrow(draw, (675, 670), (540, 670))

    draw.rounded_rectangle((310, 855, 1490, 925), radius=22, fill=ORANGE_LIGHT, outline="#e6c5ad", width=3)
    draw.text((900, 890), "Stop and request human evidence whenever a material claim is unresolved.", anchor="mm", font=font(25, True), fill=INK)
    image.save(OUT / "data_flow_diagram.png", quality=95)


if __name__ == "__main__":
    build_architecture()
    build_data_flow()
    print(f"Wrote diagrams to {OUT.resolve()}")
