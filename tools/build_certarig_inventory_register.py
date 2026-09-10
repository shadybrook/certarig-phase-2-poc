from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

from PIL import Image as PILImage, ImageOps
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    LongTable,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
PHOTO_DIR = ROOT / "work" / "inventory_assets_ql"
ASSET_DIR = ROOT / "tmp" / "pdfs" / "certarig_inventory_assets"
OUTPUT_DIR = ROOT / "output"
PDF_DIR = OUTPUT_DIR / "pdf"
PDF_PATH = PDF_DIR / "CertaRig_Phase_3_Hardware_Inventory_Register_2026-09-06.pdf"
MD_PATH = OUTPUT_DIR / "CertaRig_Phase_3_Hardware_Inventory_Register_2026-09-06.md"

NAVY = colors.HexColor("#102A43")
TEAL = colors.HexColor("#087F8C")
GREEN = colors.HexColor("#238B66")
AMBER = colors.HexColor("#D68C1F")
RED = colors.HexColor("#B73A3A")
INK = colors.HexColor("#243B53")
MUTED = colors.HexColor("#627D98")
LINE = colors.HexColor("#D9E2EC")
PALE_BLUE = colors.HexColor("#EAF4F8")
PALE_GREEN = colors.HexColor("#EAF7F1")
PALE_AMBER = colors.HexColor("#FFF6E5")
PALE_RED = colors.HexColor("#FDECEC")
WHITE = colors.white


INVENTORY = [
    dict(id="R01", code="1364532", item="Green 3-9 V, 6 mm metal indicator with 15 cm cable", qty=1, total="INR 68.00", role="Healthy / permitted-state indicator", photos="IMG_1837", wave="Wave 1", status="Received - visual match", acceptance="Polarity and current test"),
    dict(id="R02", code="1364728", item="Yellow 3-9 V, 8 mm metal indicator with 15 cm cable", qty=1, total="INR 79.00", role="Warning / inhibited-state indicator", photos="IMG_1837", wave="Wave 1", status="Received - visual match", acceptance="Polarity and current test"),
    dict(id="R03", code="24438", item="MB102 830-point solderless breadboard", qty=1, total="INR 63.00", role="Low-voltage prototype interconnect", photos="IMG_1850", wave="Wave 1", status="Received - visual match", acceptance="Rail continuity and split-rail map"),
    dict(id="R04", code="R185776", item="Rubycon 100 uF, 50 V radial electrolytic capacitor", qty=1, total="INR 11.00", role="Local low-voltage bulk decoupling", photos="IMG_1841", wave="Wave 1 support", status="Received - visual match", acceptance="Capacitance / condition; observe polarity"),
    dict(id="R05", code="1897057", item="BF-013A 5 x 20 mm fuse holder", qty=1, total="INR 14.00", role="Fused low-voltage actuator branch", photos="IMG_1839", wave="Wave 1", status="Received - visual match", acceptance="Continuity and mechanical retention"),
    dict(id="R06", code="R257326", item="24 AWG silicone wire - red", qty=1, total="INR 13.00", role="Labelled positive low-voltage wiring", photos="IMG_1842", wave="Wave 1", status="Received - visual match", acceptance="Inspect insulation; label both ends"),
    dict(id="R07", code="1825005", item="24 AWG flexible silicone wire - green", qty=2, total="INR 18.00", role="Labelled signal / interconnect wiring", photos="IMG_1842", wave="Wave 1", status="Received - visual match", acceptance="Inspect insulation; do not rely on colour alone"),
    dict(id="R08", code="R165252", item="LANBOO LB16SM 16 mm latching emergency-stop switch, stated 2C-2NC", qty=1, total="INR 285.00", role="Two independent low-voltage inhibit / sense loops", photos="IMG_1846", wave="Wave 1", status="Received - visual match", acceptance="Map both NC contact pairs with multimeter"),
    dict(id="R09", code="R195523", item="ALPS RK09K1130A5R 10 kohm rotary potentiometer", qty=3, total="INR 213.00", role="Breadboard calibration controls and spares", photos="IMG_1838", wave="Wave 1 support", status="Received - visual match", acceptance="End-to-end resistance and smooth wiper sweep"),
    dict(id="R10", code="R122767", item="Littelfuse 0217001.MXP, fast-acting 1 A, 250 V, 5 x 20 mm", qty=5, total="INR 21.30", role="Low-voltage branch protection", photos="IMG_1845", wave="Wave 1", status="Received - visual match", acceptance="Continuity; confirm fit in holder"),
    dict(id="R11", code="662929", item="100 nF, 50 V through-hole disc capacitor", qty=8, total="INR 10.00", role="Local logic / ADC decoupling", photos="IMG_1840", wave="Wave 1 support", status="Received - visual match", acceptance="Visual condition; install close to load"),
    dict(id="R12", code="R181433", item="Murata 22 pF, 50 V, 0402 C0G SMD capacitor", qty=6, total="Complimentary", role="Parts stock; not required for the Phase 3 bench", photos="IMG_1844", wave="Deferred", status="Received - visual match", acceptance="No bench test required"),
    dict(id="R13", code="43582", item="ADS1115 16-bit, 4-channel I2C ADC module", qty=2, total="INR 238.00", role="Two analogue sensor-emulation channels; one spare module", photos="IMG_1836", wave="Wave 1", status="Received - headers loose", acceptance="Solder header, 3.3 V power, I2C scan, stable readings"),
    dict(id="R14", code="R260139", item="2-channel 5 V relay module with optocouplers and guide rail", qty=1, total="INR 489.00", role="Low-voltage output switching for indicators only", photos="IMG_1849", wave="Wave 1", status="Received - visual match", acceptance="Document pins; test coils from separate 5 V supply"),
    dict(id="R15", code="1163662", item="TE 23ESA103MMF50AF 10 kohm panel potentiometer", qty=3, total="INR 1,080.00", role="Panel controls: pressure, flow and spare / fault injection", photos="IMG_1835", wave="Wave 1", status="Received - exact code visible", acceptance="End-to-end resistance, wiper sweep, terminal map"),
    dict(id="R16", code="169868", item="Raspberry Pi 3 Model A+", qty=1, total="INR 3,211.00", role="Edge computer, deterministic interlocks, logs and API", photos="IMG_1847, IMG_1848", wave="Wave 1", status="Received - board and model confirmed", acceptance="Boot, power stability, Wi-Fi, SSH, GPIO and I2C"),
    dict(id="R17", code="R224115", item="BC547-TA NPN transistor", qty=3, total="INR 10.95", role="Protected relay-input interface / spares", photos="IMG_1843", wave="Wave 1 support", status="Received - exact code visible", acceptance="Identify E-B-C pinout; diode-test junctions"),
]

PHOTO_MAP = [
    ("IMG_1835", "R15", "Three TE 23ESA panel potentiometers", "Exact Robu code 1163662 is visible on all three bags."),
    ("IMG_1836", "R13", "Two ADS1115 ADC modules", "Exact Robu code 43582 is visible. Loose header strips are present and must be soldered."),
    ("IMG_1837", "R01, R02", "Green and yellow metal indicators", "Exact Robu codes 1364532 and 1364728 are visible."),
    ("IMG_1838", "R09", "Three ALPS RK09 10 kohm potentiometers", "Exact Robu code R195523 and quantity 3 are visible."),
    ("IMG_1839", "R05", "BF-013A fuse holder", "Exact Robu code 1897057 is visible."),
    ("IMG_1840", "R11", "Eight 100 nF disc capacitors", "Exact Robu code 662929 and quantity 8 are visible."),
    ("IMG_1841", "R04", "Rubycon 100 uF radial electrolytic capacitor", "Exact Robu code R185776 and quantity 1 are visible."),
    ("IMG_1842", "R06, R07", "Red and green 24 AWG silicone wire", "Exact Robu codes R257326 and 1825005 are visible."),
    ("IMG_1843", "R17", "Three BC547-TA NPN transistors", "Exact Robu code R224115 and quantity 3 are visible."),
    ("IMG_1844", "R12", "Six complimentary 22 pF 0402 SMD capacitors", "Exact Robu code R181433 and quantity 6 are visible."),
    ("IMG_1845", "R10", "Five Littelfuse 1 A fast-acting fuses", "Exact Robu code R122767 and quantity 5 are visible."),
    ("IMG_1846", "R08", "LANBOO latching emergency-stop switch", "Exact Robu code R165252 is visible; electrical contact arrangement remains to be measured."),
    ("IMG_1847", "R16", "Raspberry Pi 3 Model A+ retail box", "Model identity is clearly visible."),
    ("IMG_1848", "R16", "Raspberry Pi 3 Model A+ board", "Board marking and Robu code 169868 are visible."),
    ("IMG_1849", "R14", "Two-channel 5 V optocoupled relay module", "Exact Robu code R260139 is visible."),
    ("IMG_1850", "R03", "MB102 solderless breadboard", "Product format and MB-102 marking are visible."),
]

OWNED = [
    ("32 GB Class 10 A1/A2 microSD card", "Available"),
    ("USB microSD card reader", "Available"),
    ("Official 5 V, 2.5 A micro-USB Raspberry Pi supply", "Available"),
    ("Male-male, male-female and female-female Dupont jumpers", "Available"),
    ("MB102 power module or suitable supply breakout", "Available"),
    ("Additional black and blue/yellow 24 AWG wire", "Available"),
    ("2N2222 transistors", "Available; BC547 units also received"),
    ("2.54 mm male header strip", "Available; ADS1115 headers also pictured loose"),
    ("Screw terminals or lever connectors", "Available"),
    ("Heat-shrink tubing, cable ties and labels", "Available"),
    ("Rigid non-conductive mounting plate or ABS enclosure", "Available"),
    ("Digital multimeter", "Available"),
    ("Wire tools, screwdrivers and soldering equipment", "Available"),
    ("Separate regulated 5 V, 1-2 A supply for relay and indicators", "NOT EVIDENCED - confirm or obtain before output test"),
]

PENDING = [
    ("ELEGOO 17-value 1% resistor assortment", "Pending Amazon", "Useful for 1 kohm base resistors, 10 kohm pull-downs and indicator current limiting. Does not block Pi-only setup."),
    ("10 uF, 16 V electrolytic capacitors, pack of 8", "Pending Amazon", "Optional local bulk decoupling; the received 100 uF capacitor is sufficient for initial low-voltage bench checks."),
    ("1000 uF, 25 V electrolytic capacitors, pack of 10", "Pending Amazon", "Not required for Wave 1. Hold for later supply-transient experiments or Wave 2."),
]

TIMELINE = [
    ("6 Sep", "Receive and control", "Freeze inventory, quarantine untested parts, inspect Pi and relay, identify pin labels, prepare microSD."),
    ("7 Sep", "Professor scope freeze", "Confirm whether a hardware-in-loop dry bench is sufficient for Phase 3, and whether the water loop is explicitly required."),
    ("8-9 Sep", "Component acceptance", "Continuity tests, potentiometer sweeps, transistor diode tests, solder ADS1115 headers, Pi boot and I2C detection."),
    ("10 Sep", "Software safety gate", "Correct E-stop and feedback polarity configuration, add stale-sample and raw-range faults, and pass automated tests before outputs."),
    ("11-12 Sep", "Input integration", "Wire two panel potentiometers to ADS1115 at 3.3 V, collect raw data, perform 3-point calibration and log evidence."),
    ("13-14 Sep", "Output and safety integration", "Use a separate regulated 5 V supply, transistor interface and 1 A fused branch. Drive only low-voltage indicators."),
    ("15 Sep", "Integrated tests", "Run normal, threshold, E-stop, broken-wire, stale-data, relay-feedback and restart tests; then perform a 60-minute soak."),
    ("16 Sep", "Evidence capture", "Photograph wiring, export CSV logs, screenshots and test results; record exact software commit and configuration."),
    ("17-18 Sep", "Phase 3 report", "Populate the template only with achieved evidence, limitations and measured results; advisor review on 18 Sep."),
    ("19 Sep", "Submission rehearsal", "Fresh clone, clean installation, signed-out link check, PDF review and buffer for corrections."),
    ("20 Sep", "Submit", "Submit the verified report, repository tag, evidence package and video/link set requested by the professor."),
]


def p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def fit_image(path: Path, max_w: float, max_h: float) -> Image:
    with PILImage.open(path) as im:
        w, h = im.size
    scale = min(max_w / w, max_h / h)
    return Image(str(path), width=w * scale, height=h * scale)


def prepare_images() -> dict[str, Path]:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    result: dict[str, Path] = {}
    for stem, *_ in PHOTO_MAP:
        src = PHOTO_DIR / f"{stem}.HEIC.png"
        if not src.exists():
            raise FileNotFoundError(src)
        dst = ASSET_DIR / f"{stem}.jpg"
        with PILImage.open(src) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
            im.thumbnail((1500, 1500), PILImage.Resampling.LANCZOS)
            im.save(dst, "JPEG", quality=86, optimize=True, progressive=True)
        result[stem] = dst
    return result


class NumberedCanvasMixin:
    pass


class InventoryDocTemplate(BaseDocTemplate):
    def __init__(self, filename: str, **kwargs):
        super().__init__(filename, **kwargs)
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="normal")
        self.addPageTemplates(PageTemplate(id="inventory", frames=frame, onPage=self._decorate))

    def _decorate(self, canvas, doc):
        canvas.saveState()
        page_w, page_h = self.pagesize
        canvas.setFillColor(NAVY)
        canvas.rect(0, page_h - 10 * mm, page_w, 10 * mm, fill=1, stroke=0)
        canvas.setFont("Helvetica-Bold", 7.5)
        canvas.setFillColor(WHITE)
        canvas.drawString(self.leftMargin, page_h - 6.5 * mm, "CERTARIG  |  PHASE 3 HARDWARE INVENTORY REGISTER")
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(self.leftMargin, 7 * mm, "Controlled working document  |  Baseline 06 Sep 2026  |  Electrical acceptance remains pending unless stated")
        canvas.drawRightString(page_w - self.rightMargin, 7 * mm, f"Page {doc.page}")
        canvas.restoreState()


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("Title", parent=base["Title"], fontName="Helvetica-Bold", fontSize=25, leading=29, textColor=NAVY, alignment=TA_LEFT, spaceAfter=8),
        "subtitle": ParagraphStyle("Subtitle", parent=base["Normal"], fontName="Helvetica", fontSize=12, leading=17, textColor=MUTED),
        "h1": ParagraphStyle("H1", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=16, leading=20, textColor=NAVY, spaceBefore=2, spaceAfter=8),
        "h2": ParagraphStyle("H2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=TEAL, spaceBefore=4, spaceAfter=5),
        "body": ParagraphStyle("Body", parent=base["BodyText"], fontName="Helvetica", fontSize=8.8, leading=12, textColor=INK, spaceAfter=5),
        "small": ParagraphStyle("Small", parent=base["BodyText"], fontName="Helvetica", fontSize=7.2, leading=9.2, textColor=INK),
        "tiny": ParagraphStyle("Tiny", parent=base["BodyText"], fontName="Helvetica", fontSize=6.3, leading=7.8, textColor=INK),
        "white": ParagraphStyle("White", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=WHITE),
        "center": ParagraphStyle("Center", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=9, leading=11, textColor=NAVY, alignment=TA_CENTER),
        "caption": ParagraphStyle("Caption", parent=base["BodyText"], fontName="Helvetica", fontSize=6.7, leading=8.4, textColor=INK),
    }


def section_banner(title: str, st) -> Table:
    t = Table([[p(title, st["white"])]], colWidths=[190 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), NAVY), ("BOX", (0, 0), (-1, -1), 0, NAVY), ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    return t


def callout(title: str, body: str, bg, st, width=61 * mm) -> Table:
    data = [[p(title, st["center"])], [p(body, st["small"])]]
    t = Table(data, colWidths=[width])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), bg), ("BOX", (0, 0), (-1, -1), 0.6, LINE), ("LINEBELOW", (0, 0), (-1, 0), 0.5, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    return t


def simple_table(rows: Iterable[Iterable], widths, st, header=True, font="small") -> LongTable:
    converted = []
    for r_idx, row in enumerate(rows):
        converted.append([v if hasattr(v, "wrap") else p(str(v), st["white"] if header and r_idx == 0 else st[font]) for v in row])
    t = LongTable(converted, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.35, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if header:
        commands += [("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), WHITE)]
    for i in range(1 if header else 0, len(converted)):
        if i % 2 == 0:
            commands.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F6F9FC")))
    t.setStyle(TableStyle(commands))
    return t


def photo_card(stem: str, ids: str, title: str, note: str, image_path: Path, st) -> Table:
    im = fit_image(image_path, 83 * mm, 47 * mm)
    caption = p(f"<b>{stem} | {ids}</b><br/>{title}<br/><font color='#627D98'>{note}</font>", st["caption"])
    t = Table([[im], [caption]], colWidths=[88 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.white), ("BOX", (0, 0), (-1, -1), 0.6, LINE), ("ALIGN", (0, 0), (-1, 0), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    return t


def build_pdf(photo_paths: dict[str, Path]) -> None:
    st = styles()
    doc = InventoryDocTemplate(
        str(PDF_PATH),
        pagesize=landscape(A4),
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=16 * mm,
        bottomMargin=13 * mm,
        title="CertaRig Phase 3 Hardware Inventory Register",
        author="CertaRig project",
        subject="Delivered hardware, photographic evidence, acceptance controls and Phase 3 commissioning plan",
    )
    story = []

    story += [Spacer(1, 16 * mm), p("CertaRig Phase 3", st["title"]), p("Hardware Inventory, Evidence and Commissioning Register", st["title"]), Spacer(1, 5 * mm), p("Baseline: 06 September 2026  |  Phase 3 deadline: 20 September 2026", st["subtitle"]), Spacer(1, 12 * mm)]
    story.append(Table([[callout("17 / 17", "Robu product lines visually mapped to uploaded photographs.", PALE_GREEN, st), callout("0 / 17", "Items electrically accepted so far. Receipt is not a functional test.", PALE_AMBER, st), callout("1 open gate", "A separate regulated 5 V, 1-2 A relay and indicator supply is not evidenced.", PALE_RED, st)]], colWidths=[64 * mm] * 3, hAlign="LEFT", style=TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 3)])))
    story += [Spacer(1, 10 * mm), p("Control statement", st["h2"]), p("This register reconciles the Robu invoice against the supplied photographs. It deliberately separates visual receipt from electrical acceptance and integrated test evidence. The source invoice contains personal contact and address information; those details have been intentionally excluded from this project-facing register.", st["body"]), Spacer(1, 5 * mm)]
    meta = [
        ["Source", "Supplier", "Invoice date", "Invoice reference", "Hardware value", "Invoice total"],
        ["Robu_ItemsList_CertaRig.pdf", "Robu.in / Macfos Limited", "04 Sep 2026", "INV2627/225826", "INR 5,824.25 incl. tax", "INR 6,072.25 incl. freight and COD"],
    ]
    story.append(simple_table(meta, [43 * mm, 35 * mm, 28 * mm, 36 * mm, 40 * mm, 48 * mm], st))
    story += [Spacer(1, 6 * mm), p("Safety boundary", st["h2"]), p("Phase 3 Wave 1 is a low-voltage educational proof of concept. Do not connect the relay contacts to mains, pumps or a claimed 30 A load. The emergency-stop switch is a demonstration interlock until its two NC contacts are mapped and tested; it is not treated as a certified safety component.", st["body"]), PageBreak()]

    story += [section_banner("1. Readiness decision and wave boundary", st), Spacer(1, 4 * mm)]
    story.append(Table([[callout("Proceed now", "Pi provisioning, visual inspection, continuity tests and potentiometer characterisation can start immediately. The Amazon delivery is not a blocker for these activities.", PALE_GREEN, st), callout("Hold outputs", "Do not energise the relay or indicators until a separate regulated 5 V supply is available and the relay pinout, input polarity and fuse path are documented.", PALE_AMBER, st), callout("Defer water loop", "Pumps, reservoirs, hoses and real fluid sensors belong to Wave 2. Purchase only after the professor confirms they are required for the 20 Sep evidence.", PALE_BLUE, st)]], colWidths=[64 * mm] * 3, hAlign="LEFT", style=TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 3)])))
    story += [Spacer(1, 7 * mm), p("Wave 1 - mandatory dry hardware-in-loop bench", st["h2"]), p("Raspberry Pi 3 Model A+ running the edge service; two 10 kohm panel controls representing pressure and flow; ADS1115 at 3.3 V; dual-NC latching emergency stop; protected relay inputs; 1 A fused, separate 5 V low-voltage output branch; green and yellow indicators; dashboard and logs on the laptop over Wi-Fi.", st["body"]), p("Wave 2 - optional real open-reservoir water loop", st["h2"]), p("A small low-voltage pump, two open reservoirs, tubing, clamps, leak tray, compatible flow and pressure sensors, return path and physical mounting. It demonstrates real fluid behaviour, but adds leakage, priming, electrical isolation and calibration risk. It should not displace the Wave 1 evidence unless explicitly required by the advisor.", st["body"]), Spacer(1, 3 * mm)]
    meeting_rows = [
        ["Meeting question", "Why it must be frozen on 7 Sep"],
        ["Is the dry hardware-in-loop bench sufficient for Phase 3, or is a real water loop mandatory by 20 Sep?", "Defines whether Wave 2 is purchased and built."],
        ["Which evidence is graded: report, repository, test logs, photos, live demo, and/or video?", "Prevents spending the remaining time on the wrong artefact."],
        ["Are potentiometers accepted as pressure and flow sensor emulators for the Phase 3 prototype?", "Confirms the stated abstraction."],
        ["Is Raspberry Pi 3 Model A+ an acceptable substitute for the unavailable Zero 2 W?", "Records the compute-platform change."],
        ["Should the AI layer remain advisory while deterministic interlocks retain authority?", "Freezes the safety and agentic-system boundary."],
        ["What minimum test cases and pass metrics should appear in the template?", "Freezes acceptance criteria before testing."],
    ]
    story.append(simple_table(meeting_rows, [118 * mm, 112 * mm], st, font="small"))
    story.append(PageBreak())

    story += [section_banner("2. Robu shipment reconciliation", st), Spacer(1, 4 * mm), p("Status vocabulary: Received - visual match means the item or exact package code is visible. It does not mean electrically accepted or safe to energise.", st["body"])]
    inv_rows = [["ID", "Robu code", "Item", "Qty", "Role", "Photo", "Wave", "Current status"]]
    for x in INVENTORY:
        inv_rows.append([x["id"], x["code"], x["item"], x["qty"], x["role"], x["photos"], x["wave"], x["status"]])
    story.append(simple_table(inv_rows, [11 * mm, 18 * mm, 52 * mm, 9 * mm, 50 * mm, 25 * mm, 23 * mm, 42 * mm], st, font="tiny"))
    story += [Spacer(1, 5 * mm), p("Reconciliation result: all 17 invoiced physical product lines are represented in the 16 uploaded photographs. The invoice quantity of 43 includes 41 physical product units plus one freight and one COD-charge line.", st["body"]), PageBreak()]

    story += [section_banner("3. Electrical acceptance register", st), Spacer(1, 4 * mm), p("Complete each row only after a measured test. Record the date, instrument or command, measured result, pass/fail and evidence filename in the generated Markdown companion or the next revision of this PDF.", st["body"])]
    acc_rows = [["ID", "Component", "Acceptance check", "Status at baseline", "Evidence to retain"]]
    for x in INVENTORY:
        acc_rows.append([x["id"], x["item"], x["acceptance"], "NOT TESTED", "Photo + reading / terminal output"])
    story.append(simple_table(acc_rows, [12 * mm, 66 * mm, 70 * mm, 28 * mm, 54 * mm], st, font="tiny"))
    story.append(PageBreak())

    story += [section_banner("4. Existing support inventory and remaining procurement gate", st), Spacer(1, 4 * mm)]
    owned_rows = [["Support item", "Baseline status"]] + [list(x) for x in OWNED]
    story.append(simple_table(owned_rows, [136 * mm, 94 * mm], st, font="small"))
    story += [Spacer(1, 6 * mm), p("Amazon delivery status", st["h2"])]
    pending_rows = [["Item", "Status", "Phase 3 decision"]] + [list(x) for x in PENDING]
    story.append(simple_table(pending_rows, [72 * mm, 35 * mm, 123 * mm], st, font="small"))
    story += [Spacer(1, 6 * mm), p("Blocking decision", st["h2"]), p("Confirm or obtain one regulated 5 V, 1-2 A supply dedicated to the relay coils and indicators. A reputable 5 V USB adapter or power bank can be used only with a secure breakout and measured output. Keep the Raspberry Pi on its official supply. Do not infer isolation from the word optocoupler; first document the relay module VCC, JD-VCC, GND and input arrangement.", st["body"]), PageBreak()]

    story += [section_banner("5. Photographic evidence catalogue", st), Spacer(1, 4 * mm), p("Each photo is mapped by filename to the inventory ID. Packaging visibility is evidence of receipt, not proof of rating, authenticity or electrical performance.", st["body"])]
    cards = [photo_card(stem, ids, title, note, photo_paths[stem], st) for stem, ids, title, note in PHOTO_MAP]
    for i in range(0, len(cards), 4):
        subset = cards[i:i + 4]
        while len(subset) < 4:
            subset.append(Spacer(1, 1))
        grid = Table([[subset[0], subset[1]], [subset[2], subset[3]]], colWidths=[94 * mm, 94 * mm], rowHeights=[76 * mm, 76 * mm], hAlign="LEFT")
        grid.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 2), ("RIGHTPADDING", (0, 0), (-1, -1), 2), ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
        story.append(KeepTogether(grid))
        if i + 4 < len(cards):
            story.append(PageBreak())
            story += [section_banner("5. Photographic evidence catalogue - continued", st), Spacer(1, 4 * mm)]
    story.append(PageBreak())

    story += [section_banner("6. Commissioning workflow - evidence before integration", st), Spacer(1, 4 * mm)]
    workflow_rows = [
        ["Gate", "Action", "Pass condition", "Do not proceed if"],
        ["A - Quarantine", "Keep all outputs unpowered; inspect for damage and label every bag / board.", "No visible damage; exact ID retained.", "Cracked board, bent connector, exposed conductor or uncertain identity."],
        ["B - Passive checks", "Test fuses, holder, both E-stop NC circuits, pot end-to-end resistance / wiper sweep and transistor junctions.", "Measurements match expected behaviour and are recorded.", "Contact state is ambiguous, pot is open/intermittent, or fuse does not seat."],
        ["C - Pi only", "Flash Raspberry Pi OS Lite 64-bit, boot on official supply, configure Wi-Fi / SSH, record OS and IP.", "Stable boot and 20-minute idle run; no undervoltage report.", "Power warning, thermal issue, corrupt card or unstable network."],
        ["D - ADC input", "Solder ADS1115 header; power from Pi 3.3 V; scan I2C; connect one pot, then two.", "Address detected; raw values move monotonically; no out-of-range voltage.", "Header bridge, wrong rail, missing ground or unstable samples."],
        ["E - Software safety", "Pass unit tests for E-stop polarity, broken wire, stale data, raw range, restart default and relay feedback mismatch.", "All safety tests pass with outputs de-energised on every fault.", "Any fault can energise or retain an output."],
        ["F - Output branch", "With Pi isolated from coil power as designed, use separate 5 V supply, transistor interface, flyback protection if not on module, 1 A fuse and indicators only.", "Each channel follows command and de-energises on E-stop / process fault.", "Relay input current / polarity is unknown or the separate supply is absent."],
        ["G - Integrated proof", "Run named test cases and 60-minute soak; collect CSV, screenshots, photos and commit ID.", "All pass criteria and recovery rules are evidenced.", "Results exist only as narration or simulation."],
    ]
    story.append(simple_table(workflow_rows, [22 * mm, 84 * mm, 66 * mm, 58 * mm], st, font="small"))
    story += [Spacer(1, 7 * mm), p("Critical software gate", st["h2"]), p("Before any relay is energised, make the E-stop and feedback polarities configurable and verify the intended dual-NC fail-safe behaviour on the actual GPIO wiring. Add raw ADC guard bands, stale-sample detection, feedback mismatch detection and a safe de-energised start state. The AI layer may recommend or explain; it must not bypass deterministic interlocks.", st["body"]), PageBreak()]

    story += [section_banner("7. Minimum evidence package for 20 September", st), Spacer(1, 4 * mm)]
    evidence_rows = [
        ["Evidence group", "Minimum artefact", "Acceptance statement"],
        ["Physical build", "Dated overview and close-up photographs; labelled wiring diagram; component map.", "A reviewer can identify Pi, ADS1115, two controls, E-stop, relay, fuse and indicators."],
        ["Pi deployment", "Fresh-install commands, service status, OS / Python versions and network/API proof.", "The PoC runs on Raspberry Pi hardware, not only the laptop simulator."],
        ["Analogue path", "I2C scan; raw and converted values; three-point calibration for two channels.", "Both channels are monotonic, bounded and repeatable within the declared tolerance."],
        ["Safety path", "E-stop normal/pressed, one broken NC wire, startup/restart, stale sample and ADC raw-range tests.", "Every unsafe or uncertain state de-energises outputs and records a reason."],
        ["Output path", "Two relay-channel tests using low-voltage indicators plus commanded-versus-feedback evidence.", "Outputs cannot remain energised when the safety decision is false."],
        ["Reliability", "A 60-minute timestamped soak log and summary of errors / restarts.", "No unexplained output transition; failures are disclosed rather than hidden."],
        ["Repository", "Public commit/tag, README, wiring, configuration example, tests, deployment script and evidence folder.", "A fresh clone can reproduce the software and locate the hardware evidence."],
        ["Report / demo", "Phase 3 template completed only with achieved results, limitations, repository link and any requested video link.", "Claims match recorded evidence and the frozen advisor scope."],
    ]
    story.append(simple_table(evidence_rows, [38 * mm, 104 * mm, 88 * mm], st, font="small"))
    story += [Spacer(1, 6 * mm), p("Suggested named test cases", st["h2"]), p("TC01 normal operating range; TC02 warning threshold; TC03 trip threshold; TC04 E-stop press and latch; TC05 one NC wire disconnected; TC06 stale ADC sample; TC07 raw ADC below/above guard band; TC08 relay feedback mismatch; TC09 process restart with fault present; TC10 network loss while edge interlock remains active.", st["body"]), PageBreak()]

    story += [section_banner("8. Schedule and change-control baseline", st), Spacer(1, 4 * mm)]
    timeline_rows = [["Date", "Milestone", "Deliverable"]] + [list(x) for x in TIMELINE]
    story.append(simple_table(timeline_rows, [23 * mm, 48 * mm, 159 * mm], st, font="small"))
    story += [Spacer(1, 7 * mm), p("How to update this register", st["h2"]), p("Use the inventory ID as the permanent key. When an item is tested, append the date, measured value, pass/fail result and evidence filename. When the hardware changes, create a new dated revision rather than overwriting the baseline. Never mark an item accepted solely because the package label matches.", st["body"]), Spacer(1, 5 * mm)]
    change_rows = [
        ["Revision", "Date", "Change", "Evidence / approver"],
        ["1.0", "06 Sep 2026", "Initial Robu shipment reconciliation, 16-photo mapping and Phase 3 commissioning baseline.", "Robu invoice + IMG_1835 to IMG_1850"],
        ["1.1", "", "", ""],
        ["1.2", "", "", ""],
    ]
    story.append(simple_table(change_rows, [24 * mm, 28 * mm, 113 * mm, 65 * mm], st, font="small"))
    story += [Spacer(1, 8 * mm), p("Immediate decision", st["h2"]), p("Start passive acceptance and Raspberry Pi provisioning now. The only procurement gate for Wave 1 output testing is the separate regulated 5 V supply. Do not purchase Wave 2 water-loop hardware until the 7 September meeting freezes the deliverable.", st["body"])]

    doc.build(story)


def build_markdown() -> None:
    lines = [
        "# CertaRig Phase 3 Hardware Inventory Register",
        "",
        "Baseline: 06 September 2026  ",
        "Deadline: 20 September 2026  ",
        "Source: Robu invoice INV2627/225826 dated 04 September 2026",
        "",
        "> Receipt, electrical acceptance and integrated verification are separate statuses. This editable companion is the working register; generate a new dated PDF revision after material updates.",
        "",
        "## Status snapshot",
        "",
        "- 17 of 17 Robu physical product lines are visually mapped to photographs.",
        "- 0 of 17 items have recorded electrical acceptance tests in this baseline.",
        "- The separate regulated 5 V, 1-2 A relay and indicator supply is not evidenced and is the only Wave 1 output-test procurement gate.",
        "- Three Amazon listings remain pending; none blocks Pi provisioning or passive testing.",
        "- Wave 2 water-loop hardware is deferred until advisor scope is frozen on 07 September.",
        "",
        "## Robu inventory",
        "",
        "| ID | Robu code | Item | Qty | Role | Photo | Wave | Receipt status | Electrical acceptance | Evidence file |",
        "|---|---|---|---:|---|---|---|---|---|---|",
    ]
    for x in INVENTORY:
        lines.append(f"| {x['id']} | {x['code']} | {x['item']} | {x['qty']} | {x['role']} | {x['photos']} | {x['wave']} | {x['status']} | NOT TESTED - {x['acceptance']} | |")
    lines += ["", "## Photo mapping", "", "| Photo | Inventory ID | Identification | Evidence basis |", "|---|---|---|---|"]
    for row in PHOTO_MAP:
        lines.append("| " + " | ".join(row) + " |")
    lines += ["", "## Existing support inventory", "", "| Item | Status |", "|---|---|"]
    for row in OWNED:
        lines.append("| " + " | ".join(row) + " |")
    lines += ["", "## Amazon pending", "", "| Item | Status | Decision |", "|---|---|---|"]
    for row in PENDING:
        lines.append("| " + " | ".join(row) + " |")
    lines += [
        "",
        "## Immediate commissioning sequence",
        "",
        "1. Quarantine outputs and label all components.",
        "2. Perform passive continuity, resistance and transistor junction checks.",
        "3. Provision the Raspberry Pi on its official supply and record boot, Wi-Fi, SSH and stability evidence.",
        "4. Solder the ADS1115 headers, power one module at 3.3 V and verify its I2C address.",
        "5. Integrate one potentiometer, then two; record raw ranges and three-point calibration.",
        "6. Fix and test E-stop polarity, raw-range, stale-data and feedback guards in software before outputs.",
        "7. Obtain or confirm the separate regulated 5 V supply, then test the fused relay branch with low-voltage indicators only.",
        "8. Run the named fault tests and 60-minute soak; capture photos, CSV logs, screenshots and commit ID.",
        "",
        "## Schedule",
        "",
        "| Date | Milestone | Deliverable |",
        "|---|---|---|",
    ]
    for row in TIMELINE:
        lines.append("| " + " | ".join(row) + " |")
    lines += [
        "",
        "## Change log",
        "",
        "| Revision | Date | Change | Evidence / approver |",
        "|---|---|---|---|",
        "| 1.0 | 06 Sep 2026 | Initial inventory, photo mapping and commissioning baseline | Robu invoice and IMG_1835 to IMG_1850 |",
        "| 1.1 | | | |",
        "",
        "## Safety boundary",
        "",
        "This is a low-voltage educational proof of concept. Do not connect the relay contacts to mains or a high-current load. Do not treat the emergency-stop switch as certified safety equipment. The AI layer is advisory; deterministic edge interlocks retain authority.",
        "",
    ]
    MD_PATH.write_text("\n".join(lines), encoding="utf-8")


def main():
    os.environ.setdefault("TZ", "Asia/Kolkata")
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    photos = prepare_images()
    build_markdown()
    build_pdf(photos)
    print(PDF_PATH)
    print(MD_PATH)


if __name__ == "__main__":
    main()
