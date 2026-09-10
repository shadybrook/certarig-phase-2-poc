from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
ASSET = ROOT / "tmp" / "docx" / "certarig_wave1_wiring"
DOCX = OUT / "CertaRig_Wave_1_Wiring_and_Circuit_Guide_2026-09-07.docx"

NAVY = "#102A43"
TEAL = "#087F8C"
GREEN = "#238B66"
AMBER = "#D68C1F"
RED = "#B73A3A"
INK = "#243B53"
MUTED = "#627D98"
LINE = "#D9E2EC"
PALE_BLUE = "#EAF4F8"
PALE_GREEN = "#EAF7F1"
PALE_AMBER = "#FFF6E5"
PALE_RED = "#FDECEC"
WHITE = "#FFFFFF"
LIGHT = "#F6F9FC"


PIN_ROWS = [
    (1, "3V3", "POWER", "USED: ADS VDD", 2, "5V", "POWER", "DO NOT USE for relay supply"),
    (3, "GPIO2 / SDA1", "I2C", "USED: ADS SDA", 4, "5V", "POWER", "DO NOT USE for relay supply"),
    (5, "GPIO3 / SCL1", "I2C", "USED: ADS SCL", 6, "GND", "GROUND", "USED: ADS ground"),
    (7, "GPIO4", "GPIO", "Spare", 8, "GPIO14 / TXD", "UART", "Reserved diagnostics"),
    (9, "GND", "GROUND", "USED: P2 analogue-pot ground", 10, "GPIO15 / RXD", "UART", "Reserved diagnostics"),
    (11, "GPIO17", "GPIO", "Spare", 12, "GPIO18 / PWM0", "GPIO", "Spare"),
    (13, "GPIO27", "GPIO", "Spare", 14, "GND", "GROUND", "USED: P1 analogue-pot ground"),
    (15, "GPIO22", "GPIO", "Spare", 16, "GPIO23", "OUTPUT", "USED: relay command"),
    (17, "3V3", "POWER", "USED: analogue-pot 3.3 V feed", 18, "GPIO24", "INPUT", "USED: E-stop sense"),
    (19, "GPIO10 / MOSI", "SPI", "Spare", 20, "GND", "GROUND", "USED: E-stop/common ground"),
    (21, "GPIO9 / MISO", "SPI", "Spare", 22, "GPIO25", "INPUT", "RESERVED: safe relay feedback"),
    (23, "GPIO11 / SCLK", "SPI", "Spare", 24, "GPIO8 / CE0", "SPI", "Spare"),
    (25, "GND", "GROUND", "Spare ground", 26, "GPIO7 / CE1", "SPI", "Spare"),
    (27, "GPIO0 / ID_SD", "HAT ID", "Do not use", 28, "GPIO1 / ID_SC", "HAT ID", "Do not use"),
    (29, "GPIO5", "GPIO", "Spare", 30, "GND", "GROUND", "Spare ground"),
    (31, "GPIO6", "GPIO", "Spare", 32, "GPIO12 / PWM0", "GPIO", "Spare"),
    (33, "GPIO13 / PWM1", "GPIO", "Spare", 34, "GND", "GROUND", "Spare ground"),
    (35, "GPIO19 / PCM_FS", "GPIO", "Spare", 36, "GPIO16", "GPIO", "Spare"),
    (37, "GPIO26", "GPIO", "Spare", 38, "GPIO20 / PCM_DIN", "GPIO", "Spare"),
    (39, "GND", "GROUND", "Spare ground", 40, "GPIO21 / PCM_DOUT", "GPIO", "Spare"),
]


WIRE_ROWS = [
    ("W01", "Pi physical 1 (3V3)", "ADS1115 VDD", "3.3 V", "Red", "ADC supply"),
    ("W02", "Pi physical 6 (GND)", "ADS1115 GND", "0 V", "Black", "ADC return"),
    ("W03", "Pi physical 3 (GPIO2/SDA1)", "ADS1115 SDA", "I2C data", "Green", "No pull-up added initially"),
    ("W04", "Pi physical 5 (GPIO3/SCL1)", "ADS1115 SCL", "I2C clock", "Yellow/blue", "No pull-up added initially"),
    ("W05", "ADS1115 ADDR", "ADS1115 GND", "Address strap", "Black", "Selects address 0x48"),
    ("W06", "Pi physical 17 (3V3) via distribution node", "Pressure pot measured high track end A", "3.3 V", "Red", "Terminal must be measured"),
    ("W07", "Pi physical 14 (GND)", "Pressure pot measured low track end C", "0 V", "Black/orange", "Dedicated P1 ground; terminal measured"),
    ("W08", "Pressure pot measured wiper B", "ADS1115 A0", "0-3.3 V analogue", "Yellow/green", "Pressure emulator"),
    ("W09", "Same physical-17 3V3 distribution node", "Flow pot measured high track end A", "3.3 V", "Red", "Characterise this pot separately"),
    ("W10", "Pi physical 9 (GND)", "Flow pot measured low track end C", "0 V", "Black/orange", "Dedicated P2 ground; characterise this pot separately"),
    ("W11", "Flow pot measured wiper B", "ADS1115 A1", "0-3.3 V analogue", "Blue/yellow", "Flow emulator"),
    ("W12", "100 nF capacitor", "ADS VDD to GND", "Decoupling", "N/A", "Fit close to ADS module"),
    ("W13", "Pi physical 18 (GPIO24)", "E-stop measured NC pair 1 terminal A", "3.3 V logic", "Yellow", "NC fail-safe sense loop"),
    ("W14", "E-stop measured NC pair 1 terminal B", "Pi physical 20 (GND)", "0 V", "Black", "Normal closed = LOW"),
    ("W15", "Pi physical 16 (GPIO23)", "1 kohm resistor", "3.3 V command", "Green", "Resistor then transistor base"),
    ("W16", "1 kohm resistor", "BC547 base", "Base drive", "Green", "Verify E-B-C pinout"),
    ("W17", "BC547 base", "10 kohm resistor to emitter", "Pull-down", "N/A", "Keeps command off at boot"),
    ("W18", "BC547 emitter", "Common ground point", "0 V", "Black", "Logic/external supply reference"),
    ("W19", "BC547 collector", "Relay IN1", "Low-side input", "Green", "Relay must be set for LOW trigger"),
    ("W20", "External regulated +5 V", "1 A fuse holder input", "+5 V", "Red", "Separate supply, not Pi 5 V pin"),
    ("W21", "Fuse holder output", "Fused +5 V rail", "+5 V fused", "Red", "Install 1 A fast fuse"),
    ("W22", "Fused +5 V rail", "E-stop measured NC pair 2 terminal A", "+5 V", "Red", "Hardwired output inhibit"),
    ("W23", "E-stop measured NC pair 2 terminal B", "Relay module DC+ or VCC terminal as marked", "+5 V switched", "Red", "Relay loses power on E-stop"),
    ("W24", "External 5 V ground", "Relay module GND", "0 V", "Black", "External supply return"),
    ("W25", "External 5 V ground", "Pi ground at one point", "0 V reference", "Black", "Required for transistor interface"),
    ("W26", "Fused +5 V rail", "Relay contact COM1", "+5 V", "Red", "Indicator source"),
    ("W27", "Relay contact NC1", "Yellow indicator +", "+5 V when safe/off", "Yellow", "Default inhibited indication"),
    ("W28", "Relay contact NO1", "Green indicator +", "+5 V when permitted", "Green", "Energized indication"),
    ("W29", "Both indicator negative leads", "External 5 V ground", "0 V", "Black", "Verify polarity first"),
    ("W30", "100 uF capacitor + / -", "Fused +5 V rail / ground", "Bulk decoupling", "N/A", "Before E-stop split; observe polarity"),
]


def font(size: int, bold: bool = False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for item in candidates:
        if Path(item).exists():
            return ImageFont.truetype(item, size)
    return ImageFont.load_default()


def rr(draw, box, fill, outline=LINE, radius=24, width=3):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def center_text(draw, box, text, fnt, fill=INK, line_gap=5):
    x1, y1, x2, y2 = box
    lines = text.split("\n")
    dims = [draw.textbbox((0, 0), line, font=fnt) for line in lines]
    heights = [d[3] - d[1] for d in dims]
    total = sum(heights) + line_gap * (len(lines) - 1)
    y = (y1 + y2 - total) / 2
    for line, d, h in zip(lines, dims, heights):
        w = d[2] - d[0]
        draw.text(((x1 + x2 - w) / 2, y), line, font=fnt, fill=fill)
        y += h + line_gap


def arrow(draw, a, b, color=TEAL, width=7, label=None):
    draw.line([a, b], fill=color, width=width)
    x2, y2 = b
    x1, y1 = a
    dx, dy = x2 - x1, y2 - y1
    mag = max((dx * dx + dy * dy) ** 0.5, 1)
    ux, uy = dx / mag, dy / mag
    px, py = -uy, ux
    size = 18
    p1 = (x2, y2)
    p2 = (x2 - ux * size + px * size * 0.55, y2 - uy * size + py * size * 0.55)
    p3 = (x2 - ux * size - px * size * 0.55, y2 - uy * size - py * size * 0.55)
    draw.polygon([p1, p2, p3], fill=color)
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        bbox = draw.textbbox((0, 0), label, font=font(23, True))
        draw.rounded_rectangle((mx - (bbox[2]-bbox[0])/2 - 10, my - 24, mx + (bbox[2]-bbox[0])/2 + 10, my + 12), 8, fill=WHITE)
        draw.text((mx - (bbox[2]-bbox[0])/2, my - 20), label, font=font(23, True), fill=color)


def canvas(title: str, subtitle: str):
    im = Image.new("RGB", (1800, 1100), WHITE)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 1800, 96), fill=NAVY)
    d.text((55, 24), title, font=font(38, True), fill=WHITE)
    d.text((55, 112), subtitle, font=font(23), fill=MUTED)
    return im, d


def build_diagrams():
    ASSET.mkdir(parents=True, exist_ok=True)

    im, d = canvas("Wave 1 system architecture", "Two power domains, one common reference, deterministic software and a hardwired inhibit")
    boxes = {
        "pi": (90, 280, 410, 520),
        "adc": (560, 245, 865, 425),
        "pots": (1030, 210, 1690, 460),
        "driver": (560, 650, 865, 835),
        "relay": (1040, 620, 1360, 850),
        "lights": (1480, 620, 1710, 850),
    }
    rr(d, boxes["pi"], PALE_BLUE, TEAL); center_text(d, boxes["pi"], "Raspberry Pi 3 A+\nCertaRig edge service\nGPIO + I2C", font(28, True))
    rr(d, boxes["adc"], PALE_GREEN, GREEN); center_text(d, boxes["adc"], "ADS1115\n3.3 V / I2C\n0x48", font(29, True))
    rr(d, boxes["pots"], PALE_GREEN, GREEN); center_text(d, boxes["pots"], "Pressure emulator P1 -> A0\nFlow emulator P2 -> A1\n0-3.3 V only", font(27, True))
    rr(d, boxes["driver"], PALE_AMBER, AMBER); center_text(d, boxes["driver"], "1 kohm + BC547\n10 kohm pull-down\nGPIO23 interface", font(27, True))
    rr(d, boxes["relay"], PALE_AMBER, AMBER); center_text(d, boxes["relay"], "5 V relay CH1\nE-stop cuts DC+ / VCC\n1 A fused", font(27, True))
    rr(d, boxes["lights"], PALE_BLUE, TEAL); center_text(d, boxes["lights"], "Yellow = inhibited\nGreen = permitted", font(27, True))
    arrow(d, (410, 340), (560, 340), label="I2C")
    arrow(d, (1030, 340), (865, 340), label="analogue")
    arrow(d, (410, 455), (560, 735), label="GPIO23")
    arrow(d, (865, 735), (1040, 735), label="IN1")
    arrow(d, (1360, 735), (1480, 735), label="contacts")
    d.line((100, 935, 1710, 935), fill=INK, width=5)
    d.text((100, 950), "Common 0 V reference (single tie point)", font=font(25, True), fill=INK)
    d.text((115, 555), "Pi power: official 5 V / 2.5 A micro-USB", font=font(23, True), fill=TEAL)
    d.text((1010, 555), "Output power: separate regulated 5 V / 1-2 A", font=font(23, True), fill=AMBER)
    im.save(ASSET / "01_architecture.png")

    im, d = canvas("Raspberry Pi 3 Model A+ 40-pin header", "Abstract header view. Use physical pin number first; BCM GPIO number second.")
    used = {1: GREEN, 3: GREEN, 5: GREEN, 6: INK, 16: AMBER, 18: RED, 20: INK, 22: MUTED}
    for row, pins in enumerate(PIN_ROWS):
        y = 180 + row * 41
        lpin, lname, _, lnote, rpin, rname, _, rnote = pins
        for x, pin, name, note in [(560, lpin, lname, lnote), (910, rpin, rname, rnote)]:
            color = used.get(pin, LINE)
            d.ellipse((x, y, x + 27, y + 27), fill=color, outline=NAVY, width=2)
            if x == 560:
                d.text((x - 480, y - 1), f"{pin:>2}  {name}", font=font(20, pin in used), fill=INK)
                d.text((x - 250, y + 1), note, font=font(16), fill=MUTED)
            else:
                d.text((x + 44, y - 1), f"{pin:<2}  {name}", font=font(20, pin in used), fill=INK)
                d.text((x + 365, y + 2), note, font=font(14), fill=MUTED)
    d.text((735, 172), "ODD", font=font(22, True), fill=MUTED)
    d.text((865, 172), "EVEN", font=font(22, True), fill=MUTED)
    d.rounded_rectangle((90, 1025, 1710, 1075), 12, fill=PALE_RED, outline=RED, width=2)
    d.text((120, 1038), "Never apply 5 V to a GPIO or ADS1115 input. Pins 2 and 4 are not the external relay-supply connection.", font=font(23, True), fill=RED)
    im.save(ASSET / "02_gpio_header.png")

    im, d = canvas("Circuit A  Pi, ADS1115 and two sensor emulators", "All analogue values stay inside the ADS1115 3.3 V supply rails")
    pi = (75, 235, 430, 850); adc = (690, 235, 1060, 850)
    p1 = (1330, 250, 1690, 500); p2 = (1330, 610, 1690, 860)
    rr(d, pi, PALE_BLUE, TEAL); rr(d, adc, PALE_GREEN, GREEN); rr(d, p1, LIGHT, GREEN); rr(d, p2, LIGHT, GREEN)
    center_text(d, (75, 245, 430, 330), "Raspberry Pi 3 A+", font(31, True))
    labels = [(370, "Pin 1  3V3"), (455, "Pin 6  GND"), (540, "Pin 3  SDA1"), (625, "Pin 5  SCL1")]
    for y, txt in labels: d.text((125, y), txt, font=font(25, True), fill=INK)
    center_text(d, (690, 245, 1060, 330), "ADS1115  0x48", font(31, True))
    for y, txt in [(370,"VDD"),(455,"GND"),(540,"SDA"),(625,"SCL"),(710,"A0"),(790,"A1")]: d.text((740, y), txt, font=font(25, True), fill=INK)
    d.text((740, 850), "ADDR -> GND    ALERT: NC", font=font(21, True), fill=MUTED)
    center_text(d, p1, "P1 PRESSURE\nterminal A = 3.3 V\nwiper B -> A0\nterminal C = GND", font(26, True))
    center_text(d, p2, "P2 FLOW\nterminal A = 3.3 V\nwiper B -> A1\nterminal C -> Pi pin 9 GND", font(26, True))
    for y, color, lab in [(383, GREEN, "W01"),(468, INK, "W02"),(553, TEAL, "W03"),(638, TEAL, "W04")]: arrow(d,(430,y),(690,y),color=color,label=lab)
    arrow(d, (1330, 375), (1060, 720), color=GREEN, label="W08")
    arrow(d, (1330, 735), (1060, 800), color=GREEN, label="W11")
    d.line((1090, 300, 1260, 300), fill=GREEN, width=6); d.text((1090, 245), "3.3 V distribution", font=font(20, True), fill=GREEN); d.text((1090, 270), "from Pi physical 17", font=font(17, True), fill=GREEN)
    d.line((1090, 930, 1260, 930), fill=INK, width=6); d.text((1090, 945), "P1 GND: Pi pin 14   P2 GND: Pi pin 9", font=font(18, True), fill=INK)
    d.rounded_rectangle((75, 930, 930, 1035), 18, fill=PALE_AMBER, outline=AMBER, width=3)
    d.text((105, 950), "Fit 100 nF across ADS VDD-GND close to the board.\nIdentify each pot wiper with a multimeter before connecting it.", font=font(23, True), fill=INK)
    im.save(ASSET / "03_adc_pots.png")

    im, d = canvas(
        "ADS1115 physical placement on an MB102 830 point breadboard",
        "Use the central five-hole terminal strips; do not use the long side power rails at this stage",
    )
    rr(d, (65, 220, 400, 850), PALE_BLUE, TEAL)
    center_text(d, (65, 235, 400, 320), "Raspberry Pi 3 A+", font(29, True))
    for y, text_value, wire_id, colour in [
        (390, "Pin 1  3V3", "W01", GREEN),
        (500, "Pin 6  GND", "W02", INK),
        (610, "Pin 3  SDA1", "W03", TEAL),
        (720, "Pin 5  SCL1", "W04", TEAL),
    ]:
        d.text((110, y), text_value, font=font(24, True), fill=INK)
        d.text((305, y + 2), wire_id, font=font(20, True), fill=colour)

    rr(d, (535, 185, 1725, 920), WHITE, MUTED, radius=26, width=4)
    d.text((575, 205), "MB102 830 point breadboard", font=font(29, True), fill=NAVY)
    d.text((575, 250), "Each strip shown below represents one five-hole shared electrical node.", font=font(21), fill=MUTED)

    node_rows = [
        (365, "VDD node", "ADS VDD", GREEN),
        (485, "GND node", "ADS GND", INK),
        (605, "SDA node", "ADS SDA", TEAL),
        (725, "SCL node", "ADS SCL", TEAL),
    ]
    for y, node_name, ads_pin, colour in node_rows:
        d.rounded_rectangle((600, y, 1645, y + 58), 16, fill=LIGHT, outline=colour, width=4)
        for x in range(650, 1580, 92):
            d.ellipse((x, y + 18, x + 21, y + 39), fill=WHITE, outline=colour, width=3)
        d.text((620, y - 34), node_name, font=font(19, True), fill=colour)
        d.text((1460, y - 34), ads_pin, font=font(19, True), fill=colour)

    for y, colour, label in [(394, GREEN, "W01"), (514, INK, "W02"), (634, TEAL, "W03"), (754, TEAL, "W04")]:
        arrow(d, (400, y), (600, y), color=colour, label=label)

    rr(d, (1340, 300, 1665, 820), PALE_GREEN, GREEN, radius=22, width=4)
    center_text(d, (1340, 315, 1665, 360), "ADS1115 module", font(25, True))
    for y, pin_name in [(382, "VDD"), (502, "GND"), (622, "SDA"), (742, "SCL")]:
        d.text((1480, y), pin_name, font=font(22, True), fill=INK)

    # Capacitor legs terminate in the same strips as ADS VDD and ADS GND.
    d.line((1060, 405, 1060, 440), fill=AMBER, width=7)
    d.line((1015, 440, 1105, 440), fill=AMBER, width=7)
    d.line((1015, 458, 1105, 458), fill=AMBER, width=7)
    d.line((1060, 458, 1060, 485), fill=AMBER, width=7)
    d.text((830, 292), "100 nF ceramic", font=font(23, True), fill=AMBER)
    d.text((790, 323), "parallel across VDD and GND", font=font(19), fill=INK)
    d.text((1115, 438), "W12", font=font(20, True), fill=AMBER)

    d.rounded_rectangle((600, 825, 1645, 890), 15, fill=PALE_AMBER, outline=AMBER, width=3)
    d.text((625, 843), "ADDR uses a short jumper to the GND node. Leave ALERT/RDY and A0-A3 open for this stage.", font=font(20, True), fill=INK)
    d.rounded_rectangle((65, 960, 1725, 1035), 15, fill=PALE_RED, outline=RED, width=3)
    d.text((95, 982), "Do not force female-to-female connectors into breadboard holes. Use female-to-male leads, or a male-to-male adapter only while unpowered.", font=font(21, True), fill=RED)
    im.save(ASSET / "03b_ads_breadboard.png")

    im, d = canvas("Circuit B  fail-safe command, relay power and indicators", "Dry low-voltage test only. No pump, mains voltage or water loop in Wave 1.")
    d.rounded_rectangle((60, 170, 1740, 1030), 25, fill=LIGHT, outline=LINE, width=3)
    # command branch
    rr(d, (95, 255, 320, 390), PALE_BLUE, TEAL); center_text(d,(95,255,320,390),"Pi GPIO23\nphysical 16",font(25,True))
    rr(d, (430, 255, 640, 390), PALE_AMBER, AMBER); center_text(d,(430,255,640,390),"1 kohm\nbase resistor",font(25,True))
    rr(d, (760, 220, 1030, 430), PALE_AMBER, AMBER); center_text(d,(760,220,1030,430),"BC547 NPN\nB: from resistor\nE: GND\nC: relay IN1",font(23,True))
    rr(d, (1210, 220, 1630, 430), PALE_AMBER, AMBER); center_text(d,(1210,220,1630,430),"Relay module logic\nIN1 set LOW-trigger\nDC+ / VCC via NC pair 2",font(23,True))
    arrow(d,(320,322),(430,322),label="HIGH permits")
    arrow(d,(640,322),(760,322),label="base")
    arrow(d,(1030,322),(1210,322),label="pull LOW")
    d.text((745, 455), "10 kohm B-E pull-down", font=font(21, True), fill=AMBER)
    # power branch
    rr(d,(95,600,340,770),PALE_BLUE,TEAL); center_text(d,(95,600,340,770),"Separate regulated\n5 V / 1-2 A\nsupply",font(25,True))
    rr(d,(450,600,650,770),PALE_RED,RED); center_text(d,(450,600,650,770),"1 A fuse\nand holder",font(25,True))
    rr(d,(760,570,1030,800),PALE_RED,RED); center_text(d,(760,570,1030,800),"E-STOP NC2\nnormal: closed\npressed/broken:\nrelay power removed",font(23,True))
    rr(d,(1190,560,1430,810),PALE_AMBER,AMBER); center_text(d,(1190,560,1430,810),"Relay CH1 contacts\nCOM = fused 5 V\nNC = yellow\nNO = green",font(23,True))
    rr(d,(1535,535,1695,835),PALE_GREEN,GREEN); center_text(d,(1535,535,1695,835),"YELLOW\nsafe/off\n\nGREEN\npermitted",font(22,True))
    arrow(d,(340,685),(450,685),color=RED,label="+5 V")
    arrow(d,(650,685),(760,685),color=RED,label="fused")
    arrow(d,(1030,685),(1190,685),color=RED,label="VCC + COM")
    arrow(d,(1430,685),(1535,685),color=GREEN,label="contacts")
    d.line((110, 900, 1680, 900), fill=INK, width=7)
    d.text((115, 920), "0 V common: external supply GND + relay GND + BC547 emitter + ONE Pi GND tie", font=font(24, True), fill=INK)
    d.rounded_rectangle((1075, 840, 1480, 875), 9, fill=PALE_AMBER, outline=AMBER, width=2)
    d.text((1092, 847), "100 uF across fused rail before E-stop split", font=font(17, True), fill=INK)
    im.save(ASSET / "04_safety_output.png")

    im, d = canvas("Commissioning sequence", "Advance only after the evidence gate for the current stage passes")
    steps = [
        ("1", "OFFLINE", "Label and inspect\nContinuity checks\nPot terminal map", MUTED),
        ("2", "PI ONLY", "microSD boot\nWi-Fi and SSH\nI2C enabled", TEAL),
        ("3", "ADC", "ADS at 3.3 V\nDetect 0x48\nStable baseline", GREEN),
        ("4", "INPUTS", "One pot at a time\nRecord endpoint\nvoltages", GREEN),
        ("5", "E-STOP", "Correct software\npolarity and prove\nopen-wire trip", RED),
        ("6", "OUTPUT", "Separate 5 V\nFuse and transistor\nIndicators", AMBER),
        ("7", "INTEGRATED", "Cases and restart\nEvidence bundle\n60-minute soak", NAVY),
    ]
    for i, (num, name, desc, color) in enumerate(steps):
        x = 70 + (i % 4) * 430
        y = 210 + (i // 4) * 390
        rr(d,(x,y,x+360,y+245),WHITE,color,radius=20,width=5)
        d.ellipse((x+20,y+20,x+85,y+85),fill=color)
        center_text(d,(x+20,y+20,x+85,y+85),num,font(28,True),WHITE)
        d.text((x+110,y+26),name,font=font(27,True),fill=color)
        center_text(d,(x+30,y+95,x+330,y+225),desc,font(22,True),INK)
        if i < len(steps)-1 and i not in (3,): arrow(d,(x+360,y+123),(x+420,y+123),color=color,width=5)
    d.rounded_rectangle((930, 905, 1700, 1015), 18, fill=PALE_RED, outline=RED, width=3)
    d.text((960, 930), "STOP if any voltage, polarity, terminal identity,\nor software state is unexpected.", font=font(26, True), fill=RED)
    im.save(ASSET / "05_commissioning.png")


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill.lstrip("#"))


def set_cell_border(cell, **kwargs):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        if edge in kwargs:
            tag = "w:" + edge
            element = borders.find(qn(tag))
            if element is None:
                element = OxmlElement(tag)
                borders.append(element)
            for key, value in kwargs[edge].items():
                element.set(qn("w:" + key), str(value).lstrip("#") if key == "color" else str(value))


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def keep_with_next(paragraph):
    p_pr = paragraph._p.get_or_add_pPr()
    keep = OxmlElement("w:keepNext")
    p_pr.append(keep)


def set_cell_text(cell, text, size=8.2, bold=False, color=INK):
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(str(text))
    r.bold = bold
    r.font.name = "Arial"
    r.font.size = Pt(size)
    r.font.color.rgb = RGBColor.from_string(color.lstrip("#"))
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def add_table(doc, headers: list[str], rows: Iterable[Iterable], widths=None, font_size=8.2):
    rows = list(rows)
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    for i, header in enumerate(headers):
        set_cell_text(table.rows[0].cells[i], header, size=8.2, bold=True, color=WHITE)
        set_cell_shading(table.rows[0].cells[i], NAVY)
        if widths: table.rows[0].cells[i].width = widths[i]
    set_repeat_table_header(table.rows[0])
    for ridx, row in enumerate(rows):
        cells = table.add_row().cells
        for i, value in enumerate(row):
            set_cell_text(cells[i], value, size=font_size)
            if widths: cells[i].width = widths[i]
            if ridx % 2: set_cell_shading(cells[i], LIGHT)
    for row in table.rows:
        for cell in row.cells:
            set_cell_border(cell, top={"val":"single","sz":"4","color":LINE}, bottom={"val":"single","sz":"4","color":LINE}, left={"val":"single","sz":"4","color":LINE}, right={"val":"single","sz":"4","color":LINE})
    return table


def add_callout(doc, title, text, fill=PALE_BLUE, accent=TEAL):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    set_cell_shading(cell, fill)
    set_cell_border(cell, top={"val":"single","sz":"8","color":accent}, bottom={"val":"single","sz":"8","color":accent}, left={"val":"single","sz":"20","color":accent}, right={"val":"single","sz":"8","color":accent})
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run(title)
    r.bold = True; r.font.name = "Arial"; r.font.size = Pt(10); r.font.color.rgb = RGBColor.from_string(accent.lstrip("#"))
    p2 = cell.add_paragraph()
    p2.paragraph_format.space_after = Pt(0)
    r2 = p2.add_run(text)
    r2.font.name = "Arial"; r2.font.size = Pt(9); r2.font.color.rgb = RGBColor.from_string(INK.lstrip("#"))
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def add_heading(doc, text, level=1):
    if level == 1:
        spacer = doc.add_paragraph()
        spacer.paragraph_format.space_after = Pt(8)
        spacer.add_run("\u00a0").font.size = Pt(1)
    p = doc.add_heading(text, level=level)
    keep_with_next(p)
    return p


def add_bullets(doc, items, level=0):
    for item in items:
        p = doc.add_paragraph(style="List Bullet" if level == 0 else "List Bullet 2")
        p.add_run(item)


def add_numbered(doc, items):
    for item in items:
        p = doc.add_paragraph(style="List Number")
        p.add_run(item)


def add_figure(doc, filename, caption, width=7.0):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(ASSET / filename), width=Inches(width))
    cap = doc.add_paragraph(caption)
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.style = doc.styles["Caption"]


def build_docx():
    doc = Document()
    doc.settings.odd_and_even_pages_header_footer = False
    sec = doc.sections[0]
    sec.different_first_page_header_footer = False
    sec.top_margin = Cm(1.7); sec.bottom_margin = Cm(1.6); sec.left_margin = Cm(1.65); sec.right_margin = Cm(1.65)
    sec.header_distance = Cm(0.7); sec.footer_distance = Cm(0.7)

    normal = doc.styles["Normal"]
    normal.font.name = "Arial"; normal.font.size = Pt(9.5); normal.font.color.rgb = RGBColor.from_string(INK.lstrip("#"))
    normal.paragraph_format.space_after = Pt(5); normal.paragraph_format.line_spacing = 1.08
    for name, size, color in [("Title",28,NAVY),("Heading 1",17,NAVY),("Heading 2",12,TEAL),("Heading 3",10,INK)]:
        s = doc.styles[name]; s.font.name = "Arial"; s.font.size = Pt(size); s.font.bold = True; s.font.color.rgb = RGBColor.from_string(color.lstrip("#"))
        s.paragraph_format.space_before = Pt(8); s.paragraph_format.space_after = Pt(5)
    cap = doc.styles["Caption"]; cap.font.name="Arial"; cap.font.size=Pt(8); cap.font.italic=True; cap.font.color.rgb=RGBColor.from_string(MUTED.lstrip("#"))

    # Cover
    doc.add_paragraph().paragraph_format.space_after = Pt(36)
    t = doc.add_paragraph("CertaRig Phase 3")
    t.style = doc.styles["Title"]
    st = doc.add_paragraph("Wave 1 Wiring and Circuit Guide")
    st.style = doc.styles["Title"]
    st.runs[0].font.size = Pt(24); st.runs[0].font.color.rgb = RGBColor.from_string(TEAL.lstrip("#"))
    doc.add_paragraph("Raspberry Pi 3 Model A+ dry hardware-in-the-loop bench")
    doc.add_paragraph("Prepared for controlled assembly, commissioning evidence, and the 20 September Phase 3 submission")
    doc.add_paragraph().paragraph_format.space_after = Pt(18)
    add_callout(doc, "CONTROL STATUS  ANALOGUE INPUT PATH VERIFIED", "Pi boot, SSH, I2C, ADS1115 address 0x48, and both 0-3.3 V potentiometer acquisition paths have measured evidence. E-stop contacts, transistor pinout, relay logic, fused output supply, and indicator polarity remain gated until measured and recorded.", PALE_GREEN, GREEN)
    add_table(doc, ["Field", "Value"], [
        ("Project", "CertaRig"),
        ("Scope", "Wave 1 dry low-voltage bench only"),
        ("Controller", "Raspberry Pi 3 Model A+"),
        ("Analogue interface", "ADS1115 at 3.3 V, I2C address 0x48"),
        ("Safety concept", "NC E-stop sense loop plus independent NC relay-power inhibit"),
        ("Output", "Low-voltage green/yellow indicators through relay channel 1"),
        ("Excluded", "Mains, pump, solenoid valve, pressurised plumbing, water loop"),
    ], [Cm(4.1), Cm(13.1)], 9)
    doc.add_page_break()

    add_heading(doc, "1. Purpose and non-negotiable boundaries")
    doc.add_paragraph("This document is the single wiring reference for the CertaRig Wave 1 dry bench. It translates the received inventory and the current repository configuration into a labelled circuit, a staged assembly method, and evidence gates. It does not claim that the hardware is already electrically verified.")
    add_callout(doc, "SAFE SCOPE", "Use only SELV low-voltage sources: the official Raspberry Pi supply and a separate regulated 5 V supply for the relay and indicators. Do not connect mains voltage, a pump, a solenoid valve, or any water-bearing equipment during Wave 1.", PALE_GREEN, GREEN)
    add_callout(doc, "STOP CONDITIONS", "Stop immediately for heat, smell, smoke, unstable Pi power, an unexpected voltage, unclear terminal labels, a non-latching E-stop, an indicator that does not match the state, or any software state that disagrees with the physical state.", PALE_RED, RED)
    add_heading(doc, "What Wave 1 can prove", 2)
    add_bullets(doc, [
        "Real Pi deployment, I2C acquisition, analogue scaling, deterministic safety logic, dashboard/API behaviour, event logs, and repeatable test evidence.",
        "Healthy, warning, threshold-trip, E-stop, broken-wire, restart, and output-indication behaviours on a low-voltage dry bench.",
        "A controlled substitution boundary: potentiometers emulate sensor voltages and indicators emulate an actuator command.",
    ])
    add_heading(doc, "What Wave 1 cannot prove", 2)
    add_bullets(doc, [
        "Pressure or flow accuracy, leaks, priming, cavitation, surge, pump inrush, hydraulic dynamics, EMI in a field installation, or long-duration wet operation.",
        "Formal TRL certification. The defensible wording is evidence consistent with laboratory breadboard readiness.",
    ])
    doc.add_page_break()

    add_heading(doc, "2. System architecture and power domains")
    add_figure(doc, "01_architecture.png", "Figure 1. Wave 1 architecture. The Pi and output circuit use separate supplies; only the reference ground is shared for the transistor interface.")
    add_table(doc, ["Domain", "Source", "Loads", "Rule"], [
        ("Pi / logic", "Official 5 V, 2.5 A micro-USB supply into PWR IN", "Pi, ADS1115, two potentiometers", "ADS uses physical pin 1; pots use physical pin 17 via the verified splitter"),
        ("Output", "Separate regulated 5 V, 1-2 A supply", "Relay module and two 3-9 V indicators", "Pass +5 V through the 1 A fuse and E-stop power loop"),
        ("Common reference", "One controlled ground tie", "Pi GND, transistor emitter, relay/external GND", "Never join the external +5 V rail to Pi 5 V pins"),
    ], [Cm(3), Cm(4.5), Cm(4.1), Cm(5.7)], 8.4)
    add_callout(doc, "Why two supplies", "The relay board can draw far more current and create switching noise. A separate supply keeps that load away from the Pi rail, while a single ground tie gives the BC547 interface a defined reference.", PALE_BLUE, TEAL)
    doc.add_page_break()

    add_heading(doc, "3. Raspberry Pi GPIO naming")
    doc.add_paragraph("Every connection in this guide uses both the physical header pin and the BCM GPIO number. Physical pin 16 and BCM GPIO23 are the same conductor; they are not two different pins. Never wire by BCM number alone while the Pi is unpowered.")
    add_figure(doc, "02_gpio_header.png", "Figure 2. Abstract 40-pin header map. Confirm orientation from the square pin-1 pad and later with the Raspberry Pi pinout command.", 7.1)
    add_callout(doc, "Used pins", "Pin 1 = 3V3; pin 3 = GPIO2/SDA1; pin 5 = GPIO3/SCL1; pin 6 = GND; pin 16 = GPIO23 relay command; pin 18 = GPIO24 E-stop input; pin 20 = GND. Pin 22/GPIO25 is reserved but left unconnected for the first build.", PALE_GREEN, GREEN)
    doc.add_page_break()

    add_heading(doc, "4. Complete 40-pin allocation table")
    pin_rows = []
    for row in PIN_ROWS:
        pin_rows.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
    add_table(doc, ["Phys", "Odd pin", "Type", "CertaRig use", "Phys", "Even pin", "Type", "CertaRig use"], pin_rows,
              [Cm(1.0),Cm(2.4),Cm(1.3),Cm(3.7),Cm(1.0),Cm(2.5),Cm(1.3),Cm(4.1)], 6.9)
    doc.add_paragraph("GPIO electrical rule: Raspberry Pi GPIO operates at 3.3 V. GPIO pins and ADS inputs must never receive 5 V. Power pins 2 and 4 are 5 V rails, not general outputs and not the external relay supply connection.")
    doc.add_page_break()

    add_heading(doc, "5. Circuit A: ADS1115 and sensor-emulation inputs")
    add_figure(doc, "03_adc_pots.png", "Figure 3. Pi-to-ADS1115 I2C wiring and two 10 kohm potentiometer sensor emulators.")
    add_heading(doc, "Connection intent", 2)
    add_bullets(doc, [
        "Power the ADS1115 from 3.3 V so its input range is naturally bounded to the Pi logic domain.",
        "Tie ADDR to GND for decimal address 72, hexadecimal 0x48. Leave ALERT/RDY unconnected during initial commissioning.",
        "Use A0 for pressure and A1 for flow. Reserve A2/A3 until the two-channel baseline is stable.",
        "Place one 100 nF ceramic capacitor directly across ADS VDD and GND.",
        "Characterise each potentiometer separately. In the measured CertaRig convention, A is the high track end, B is the wiper, and C is the low track end; manufacturer markings and measurements override this illustration.",
    ])
    add_callout(doc, "WAVE 1 CONFIGURATION", "Use the dedicated Wave 1 configuration with measured endpoints near 0-3.3 V. The original 0.5-4.5 V example is retained only as a future sensor-interface reference and must not be used for the present potentiometer bench.", PALE_BLUE, TEAL)
    doc.add_page_break()

    add_heading(doc, "5.1 ADS1115 physical placement on the MB102 breadboard")
    add_figure(doc, "03b_ads_breadboard.png", "Figure 3A. Physical node layout for the ADS-only commissioning stage on an MB102 830 point breadboard.")
    add_heading(doc, "How to assemble this stage", 2)
    add_bullets(doc, [
        "Use the MB102 central terminal area, not the long red and blue side rails. On a typical MB102, holes A-E in one numbered row form one five-hole node, and holes F-J form a separate node across the centre channel. Verify this pattern with the multimeter because board variants differ and the long power rails may be split.",
        "Insert the ADS1115 male header along one terminal-strip bank so every labelled module pin occupies a different numbered five-hole row. Never place two ADS pins in the same connected row. Follow the ADS board silkscreen because breakout-board pin order varies.",
        "Use female-to-male jumper leads: the female end fits the Raspberry Pi GPIO header and the male end enters the breadboard strip shared with the matching ADS1115 pin.",
        "Place one leg of the 100 nF ceramic capacitor in the same strip as ADS VDD and the other leg in the same strip as ADS GND. The capacitor is parallel with the supply, not inserted in series with either wire, and it has no polarity.",
        "Connect ADS ADDR to the same ground strip with a short male-to-male jumper to select address 0x48.",
        "Leave ALERT/RDY and analogue inputs A0-A3 open. Do not connect the potentiometers until ADS-only detection has passed.",
    ])
    p = doc.add_paragraph()
    p.add_run("Direct female-to-female alternative. ").bold = True
    p.add_run("The four Pi-to-ADS connections can be made directly only if the external capacitor is omitted or attached through a purpose-built splitter. Do not twist the capacitor around exposed header pins. For this controlled build, use the breadboard arrangement above.")
    doc.add_page_break()

    add_heading(doc, "6. Circuit B: E-stop, relay interface, fuse and indicators")
    add_figure(doc, "04_safety_output.png", "Figure 4. Intended fail-safe low-voltage output path. Exact module terminal order remains a measurement gate.")
    add_heading(doc, "Dual-contact E-stop allocation", 2)
    add_table(doc, ["Contact set", "Circuit", "Normal condition", "Pressed or broken wire", "Purpose"], [
        ("Measured NC pair 1", "GPIO24 to GND sense loop", "Closed; input LOW", "Open; input HIGH", "Software detects E-stop and wiring break"),
        ("Measured NC pair 2", "Fused +5 V to relay DC+ or VCC", "Closed; relay can energize", "Open; relay power removed", "Independent hardware inhibit"),
    ], [Cm(2),Cm(4.1),Cm(3.2),Cm(3.5),Cm(4.4)], 8.2)
    add_callout(doc, "FAIL-SAFE POLARITY CONTRACT", "The Wave 1 adapter uses a pull-up input with explicit active-high fault interpretation. The measured NC loop therefore has this electrical truth: normal/closed is LOW and healthy; pressed, open, or broken-wire is HIGH and active. Automated tests must pass before connecting the E-stop or enabling any output.", PALE_RED, RED)
    add_heading(doc, "Relay and indicator behaviour", 2)
    add_bullets(doc, [
        "GPIO23 HIGH drives the BC547 through 1 kohm. The transistor pulls IN1 LOW, so the relay board must be configured for low-level trigger.",
        "A 10 kohm base-to-emitter resistor keeps the transistor off while GPIO23 floats during boot.",
        "Relay de-energized: COM1 connects to NC1 and the yellow safe/inhibited indicator is on. Relay energized: COM1 connects to NO1 and the green permitted indicator is on.",
        "Install the 100 uF electrolytic across the fused 5 V rail before the E-stop branch split. Observe polarity. Do not put it after NC2 because stored energy could delay relay drop-out.",
        "Leave relay channel 2 unused in the first build.",
    ])
    doc.add_page_break()

    add_heading(doc, "7. Wire identification schedule")
    doc.add_paragraph("Label both ends with the W-number. Colour is a convenience, never proof of function. The schedule becomes the continuity checklist and the final as-built record.")
    add_table(doc, ["ID", "From", "To", "Signal", "Colour", "Control note"], WIRE_ROWS,
              [Cm(1.0),Cm(3.5),Cm(3.7),Cm(2.5),Cm(1.5),Cm(5.0)], 6.6)
    doc.add_page_break()

    add_heading(doc, "8. Terminal verification register")
    add_table(doc, ["Item", "Do not assume", "Multimeter or visual test", "Record before wiring"], [
        ("E-stop", "Printed NC claim or terminal position", "Continuity in released and latched states for both independent pairs", "NC1-A/B and NC2-A/B labels; released/pressed resistance"),
        ("TE / ALPS pots", "Centre terminal is always the wiper", "End-to-end resistance and wiper-to-end sweep", "A, B, C labels and rotation direction"),
        ("BC547", "Flat-face lead order across vendors", "Part marking, datasheet package, diode-mode junction check", "E, B, C on the actual pieces"),
        ("Relay module", "VCC/GND/IN order, trigger jumper, COM/NC/NO order", "Read silkscreen; unpowered contact continuity; powered coil test only after supply check", "Connector map and low-trigger setting"),
        ("Indicators", "Wire colour means polarity; internal resistor value", "Current-limited 3-5 V polarity test", "+/- wire and observed current/brightness"),
        ("Fuse path", "Holder clips make reliable contact", "Continuity through installed 1 A fuse", "Resistance and fuse identity"),
        ("Breadboard", "Power rails are continuous end-to-end", "Continuity map, including any centre rail splits", "Rail split drawing"),
        ("External supply", "Label voltage equals measured voltage", "Measure unloaded and with relay load", "Voltage, polarity, current rating"),
    ], [Cm(2.1),Cm(4.0),Cm(5.9),Cm(5.2)], 7.4)
    add_callout(doc, "Before wiring each remaining stage", "Use the available multimeter to identify terminals and record the result before connecting them to the Pi. Do not assemble or energize the E-stop, transistor, relay, indicator, or fused external-supply circuit until its specific acceptance gate has passed.", PALE_AMBER, AMBER)
    doc.add_page_break()

    add_heading(doc, "9. Step-by-step assembly and commissioning SOP")
    add_figure(doc, "05_commissioning.png", "Figure 5. Controlled commissioning sequence. Each stage creates evidence before the next stage is allowed.")
    stages = [
        ("Stage 0  Work area", "Both supplies disconnected; remove jewellery; dry non-conductive surface; label W01-W30; photograph the empty board."),
        ("Stage 1  Component acceptance", "Map breadboard rails, pot terminals, E-stop pairs, relay terminals, transistor leads, indicator polarity, fuse continuity, and external supply voltage."),
        ("Stage 2  Pi-only boot", "Flash Raspberry Pi OS, boot from PWR IN, join Wi-Fi, enable SSH and I2C, update hostname/time, and record OS plus software commit."),
        ("Stage 3  ADS-only", "Power down. Wire W01-W05 and W12. Inspect. Power the Pi. Confirm I2C address 0x48 and stable open-channel behaviour. Power down."),
        ("Stage 4  One analogue channel", "Wire pressure pot W06-W08. Check 0 V and 3.3 V rails before inserting ADS. Sweep slowly; record minimum/mid/maximum. Repeat for flow W09-W11."),
        ("Stage 5  Software safety", "Implement NC-loop polarity and tests. Set relay_feedback_gpio to null initially. Create measured 0-3.3 V Wave 1 calibration. Prove output defaults safe after service start/restart."),
        ("Stage 6  E-stop input", "Power down. Wire W13-W14 only. Validate released, pressed, and one-wire-disconnected states. All pressed/broken states must block the command."),
        ("Stage 7  Relay logic interface", "With external supply still off, wire W15-W19 and W25. Confirm GPIO23 is LOW at boot and transistor is off. Verify no 5 V reaches the GPIO side."),
        ("Stage 8  Fused output circuit", "Wire W20-W24 and W26-W30. Inspect polarity. Energize the external 5 V supply with Pi command forced safe. Yellow must be on, green off."),
        ("Stage 9  Integrated cases", "Run normal, warning, trip, E-stop, broken loop, process restart, command rejection and 60-minute soak. Save logs, screenshots, wiring photos and measured results."),
    ]
    add_table(doc, ["Gate", "Action and acceptance"], stages, [Cm(3.4),Cm(13.8)], 8.1)
    doc.add_page_break()

    add_heading(doc, "10. Software-to-wire contract")
    add_table(doc, ["Software field", "Current value", "Physical meaning", "Required action before bench"], [
        ("i2c_bus", "1", "GPIO2/SDA1 and GPIO3/SCL1", "Keep"),
        ("ads1115_address", "72 / 0x48", "ADDR tied to GND", "Keep; confirm with I2C scan"),
        ("valve_output_gpio", "23", "Pi physical pin 16 to BC547 interface", "Keep; Wave 1 load is indicators only"),
        ("emergency_stop_gpio", "24", "Pi physical pin 18 NC loop to ground", "Keep; validated in automated polarity tests"),
        ("emergency_stop_active_high", "true", "LOW = healthy; HIGH/open = active", "Keep for the measured fail-safe NC loop"),
        ("relay_feedback_gpio", "null", "Pi physical pin 22 remains disconnected", "Keep disabled for the initial Wave 1 bench"),
        ("output_active_high", "true", "GPIO23 HIGH commands transistor/low-trigger relay", "Keep only after measured truth-table test"),
        ("pressure raw range", "Wave 1: 0.0-3.3 V", "A0 pot is limited to the 3.3 V rail", "Use rig.wave1.json; preserve raw voltage evidence"),
        ("flow raw range", "Wave 1: 0.0-3.3 V", "A1 pot is limited to the 3.3 V rail", "Use rig.wave1.json; preserve raw voltage evidence"),
    ], [Cm(3.0),Cm(2.7),Cm(5.1),Cm(6.3)], 7.8)
    add_callout(doc, "Why GPIO25 stays disconnected", "A relay contact may carry the external 5 V rail. Directly connecting that voltage to GPIO25 would damage the Pi. Feedback can be added later only as a 3.3 V dry-contact circuit or through an appropriately isolated/translated interface.", PALE_RED, RED)
    add_heading(doc, "Current repository evidence", 2)
    doc.add_paragraph("The adapter initializes its output safe and reads ADS1115 A0/A1. The Wave 1 configuration uses GPIO23 for output command, GPIO24 for the fail-safe NC E-stop loop, no GPIO25 feedback, and 0-3.3 V analogue scaling. Automated tests verify that LOW means healthy and HIGH/open means E-stop active before physical input commissioning.")
    doc.add_page_break()

    add_heading(doc, "11. Acceptance tests and evidence")
    tests = [
        ("T01", "Pi boot", "Pi powered only through PWR IN; stable power; SSH reachable", "Boot log + photo"),
        ("T02", "I2C", "ADS1115 appears at 0x48 repeatedly", "Command output + photo"),
        ("T03", "Pressure input", "A0 sweep monotonic; min/mid/max recorded; no value above VDD", "CSV + screenshot"),
        ("T04", "Flow input", "A1 sweep monotonic; min/mid/max recorded; no value above VDD", "CSV + screenshot"),
        ("T05", "Normal state", "E-stop released; yellow on until a valid permit; no unsolicited relay action", "Video + event log"),
        ("T06", "E-stop", "Pressing E-stop removes relay power and software reports active", "Video + timestamps"),
        ("T07", "Broken sense wire", "Opening either NC1 conductor creates the same inhibited software state", "Video + event log"),
        ("T08", "Threshold trip", "Pressure above 4.2 bar equivalent rejects/de-energizes permit", "CSV + decision record"),
        ("T09", "Invalid input", "Out-of-range/stale input prevents output", "Test result + event log"),
        ("T10", "Restart", "After service/Pi restart the relay is de-energized and yellow is on", "Video + boot log"),
        ("T11", "Indicator truth", "NC/off = yellow; NO/on = green; states match dashboard", "Photo/video matrix"),
        ("T12", "Soak", "60 min with no unexplained reset, overheating, or state divergence", "CSV summary + photos"),
    ]
    add_table(doc, ["ID", "Test", "Pass condition", "Evidence"], tests, [Cm(1.2),Cm(3.0),Cm(8.5),Cm(4.4)], 7.6)
    add_heading(doc, "Minimum evidence pack", 2)
    add_bullets(doc, [
        "One labelled overhead wiring photograph and close-ups of Pi header, ADS, E-stop, transistor, fuse, relay, and indicator terminals.",
        "Multimeter acceptance sheet, measured supply voltages, potentiometer endpoint readings, and E-stop contact truth table.",
        "Exact configuration file, software commit hash, automated test output, I2C scan, CSV logs, screenshots, and short demo clips.",
        "A limitations statement preserving the dry-bench versus hydraulic boundary.",
    ])
    doc.add_page_break()

    add_heading(doc, "12. Troubleshooting by symptom")
    add_table(doc, ["Symptom", "Most likely checks", "Do not do"], [
        ("Pi red LED only / no network", "Confirm bootable microSD, correct PWR IN cable/supply, OS image, Wi-Fi config, router client list", "Do not expect USB-A host cable to make the Pi a normal USB peripheral"),
        ("ADS not at 0x48", "Power off; check W01-W05, common ground, I2C enabled, ADDR strap, solder joints", "Do not move wires while powered"),
        ("ADC value jumps", "Check breadboard rail continuity, 100 nF decoupling, short signal leads, secure pot wiper", "Do not add random capacitors before a baseline log"),
        ("Pot direction reversed", "Swap only its two end terminals after power-off; keep wiper on A0/A1", "Do not alter software sign to hide a wiring ambiguity"),
        ("Relay always on", "Disconnect external supply; verify LOW-trigger selection, 10 kohm pull-down, transistor E-B-C, GPIO boot state", "Do not connect load until the input truth table passes"),
        ("Pi resets when relay switches", "Stop output; verify separate supply, common tie, supply voltage, wiring, decoupling and shorts", "Do not power relay from Pi 3.3 V"),
        ("E-stop reads backwards", "Stop commissioning; correct NC-loop software polarity and rerun unit tests", "Do not rewire to non-fail-safe semantics just to match current code"),
        ("Green/yellow reversed", "Power off; verify COM/NC/NO and indicator polarity", "Do not assume relay terminal order from appearance"),
    ], [Cm(4.0),Cm(8.2),Cm(4.9)], 7.5)
    doc.add_page_break()

    add_heading(doc, "13. Build checklist and as-built sign-off")
    checklist = [
        ("C01", "All parts labelled and photographed", "", ""),
        ("C02", "Breadboard rails mapped", "", ""),
        ("C03", "Each pot high end / wiper / low end recorded", "", ""),
        ("C04", "E-stop NC1/NC2 truth table recorded", "", ""),
        ("C05", "BC547 E/B/C verified", "", ""),
        ("C06", "Relay VCC/GND/IN and COM/NC/NO verified", "", ""),
        ("C07", "External 5 V voltage/polarity/load rating verified", "", ""),
        ("C08", "1 A fuse path continuity verified", "", ""),
        ("C09", "NC E-stop polarity software change tested", "", ""),
        ("C10", "Wave 1 0-3.3 V config frozen", "", ""),
        ("C11", "W01-W30 point-to-point inspection complete", "", ""),
        ("C12", "T01-T12 evidence archived", "", ""),
    ]
    add_table(doc, ["ID", "Control", "Result / measured value", "Evidence filename"], checklist, [Cm(1.2),Cm(7.0),Cm(4.5),Cm(4.4)], 8.2)
    add_heading(doc, "As-built declaration", 2)
    doc.add_paragraph("The circuit was assembled to this revision, all deviations were recorded, and all required gates were passed before integrated testing.")
    add_table(doc, ["Role", "Name", "Date", "Signature / review note"], [
        ("Builder", "Chintan Dedhia", "", ""),
        ("Advisor review", "Prof. Raj Kumar", "", ""),
    ], [Cm(3),Cm(4.8),Cm(3.2),Cm(6.1)], 8.5)
    add_heading(doc, "Revision history", 2)
    add_table(doc, ["Revision", "Date", "Status", "Change"], [
        ("0.4", "10 Sep 2026", "Dual input verified", "Recorded 4,457 paired samples; A0 reached 0-3.302 V and A1 reached 0-3.300 V; updated software and E-stop gates"),
        ("0.3", "10 Sep 2026", "P2 ground allocation", "P1 low terminal uses physical 14 GND; P2 low terminal uses physical 9 GND; both share the Pi ground plane"),
        ("0.2", "09 Sep 2026", "As-built analogue correction", "Use physical 17 for pot 3.3 V distribution and measured terminal convention A = high, B = wiper, C = ground"),
        ("0.1", "07 Sep 2026", "Pre-commissioning", "Initial controlled wiring design based on current inventory and repository contract"),
    ], [Cm(2),Cm(3),Cm(3.4),Cm(8.7)], 8.2)
    doc.add_page_break()

    add_heading(doc, "14. References")
    refs = [
        "Raspberry Pi documentation, GPIO and 40-pin header: https://www.raspberrypi.com/documentation/computers/raspberry-pi.html",
        "Raspberry Pi configuration documentation, enabling I2C: https://www.raspberrypi.com/documentation/computers/configuration.html",
        "Raspberry Pi 3 Model A+ product page: https://www.raspberrypi.com/products/raspberry-pi-3-model-a-plus/",
        "Texas Instruments ADS1115 data sheet: https://www.ti.com/lit/ds/symlink/ads1115.pdf",
        "onsemi BC546/BC547/BC548/BC549/BC550 data sheet: https://www.onsemi.com/pdf/datasheet/bc550-d.pdf",
        "Local project source: work/certarig-poc/certarig_edge/hardware/raspberry_pi.py",
        "Local project configuration: work/certarig-poc/config/rig.example.json",
        "CertaRig Phase 3 hardware inventory register, baseline 06 Sep 2026.",
    ]
    add_numbered(doc, refs)
    add_callout(doc, "Document control note", "Manufacturer data sheets and measured terminal identities override illustrative diagrams. Update this document to an as-built revision after component acceptance and before Phase 3 submission.", PALE_BLUE, TEAL)

    OUT.mkdir(parents=True, exist_ok=True)
    doc.save(DOCX)


if __name__ == "__main__":
    build_diagrams()
    build_docx()
    print(DOCX)
