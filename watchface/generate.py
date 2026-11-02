#!/usr/bin/env python3
"""Generates res/raw/watchface.xml + bolt.png for the KGH Neon Ring watch face.
Run: python3 generate.py   (needs Pillow for the bolt icon)"""
import math, os
from xml.sax.saxutils import quoteattr

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app/src/main/res")
C = 240  # centre of the 480x480 virtual canvas
MONO, GROTESK = "space_mono_bold", "space_grotesk_bold"

out = []
def w(s, ind=0): out.append("  " * ind + s)

def arc(name, r, start, end, color, thick, cap="ROUND", dash=None, tx=None, ind=3):
    """Arc with radius r (centre-line), degrees clockwise from 12 o'clock.
    tx = {'startAngle': expr, 'endAngle': expr, 'alpha': expr}"""
    d = 2 * r
    attrs = f'centerX="{C}" centerY="{C}" width="{d}" height="{d}" startAngle="{start}" endAngle="{end}" direction="CLOCKWISE"'
    dash_attr = f' dashIntervals="{dash}"' if dash else ""
    w(f'<PartDraw name="{name}" x="0" y="0" width="480" height="480">', ind)
    w(f'<Arc {attrs}>', ind + 1)
    for t, v in (tx or {}).items():
        if t != "alpha":
            w(f'<Transform target="{t}" value={quoteattr(v)}/>', ind + 2)
    w(f'<Stroke color="{color}" thickness="{thick}" cap="{cap}"{dash_attr}/>', ind + 2)
    w('</Arc>', ind + 1)
    w('</PartDraw>', ind)

def group_open(name, alpha=None, ambient_hide=False, ind=2):
    w(f'<Group name="{name}" x="0" y="0" width="480" height="480">', ind)
    if ambient_hide:
        w('<Variant mode="AMBIENT" target="alpha" value="0"/>', ind + 1)

def text(name, x, y, wd, ht, content_xml, font, size, color, align="CENTER", spacing=0, ind=3, tx=None, upper=False):
    w(f'<PartText name="{name}" x="{x}" y="{y}" width="{wd}" height="{ht}">', ind)
    for t, v in (tx or {}).items():
        w(f'<Transform target="{t}" value={quoteattr(v)}/>', ind + 1)
    w(f'<Text align="{align}">', ind + 1)
    ls = f' letterSpacing="{spacing}"' if spacing else ""
    w(f'<Font family="{font}" size="{size}" color="{color}"{ls}>', ind + 2)
    w(content_xml, ind + 3)
    w('</Font>', ind + 2)
    w('</Text>', ind + 1)
    w('</PartText>', ind)

def tpl(fmt, *exprs, upper=False):
    p = "".join(f'<Parameter expression={quoteattr(e)}/>' for e in exprs)
    t = f'<Template>{fmt}{p}</Template>'
    return f'<Upper>{t}</Upper>' if upper else t

def circ_text(name, cx, cy, r, start, end, direction, content, font, size, color, ind=3, h=30, align="CENTER", spacing=0):
    d = 2 * r
    w(f'<PartText name="{name}" x="0" y="0" width="480" height="480">', ind)
    w(f'<TextCircular centerX="{C}" centerY="{C}" width="{d}" height="{d}" startAngle="{start}" endAngle="{end}" direction="{direction}" align="{align}">', ind + 1)
    ls = f' letterSpacing="{spacing}"' if spacing else ""
    w(f'<Font family="{font}" size="{size}" color="{color}"{ls}>', ind + 2)
    w(content, ind + 3)
    w('</Font>', ind + 2)
    w('</TextCircular>', ind + 1)
    w('</PartText>', ind)

GREEN, GREEN_DK = "#00F5A0", "#06362A"
RED, RED_DK = "#FF2D46", "#3B1226"
ORANGE = "#FF7A1A"
TICK_GRAY = "#4A4A4A"

w('<?xml version="1.0" encoding="utf-8"?>')
w('<WatchFace width="480" height="480">')
w('<Metadata key="CLOCK_TYPE" value="DIGITAL"/>', 1)
w('<Metadata key="PREVIEW_TIME" value="10:10:00"/>', 1)
w('<Scene backgroundColor="#FF000000">', 1)

# ---------------- seconds tick ring ----------------
R_T = 224
circ = 2 * math.pi * R_T
pitch = circ / 60
tick_w = 3
dash = f"{tick_w} {pitch - tick_w:.3f}"
half = math.degrees((tick_w / 2) / R_T)  # centre the first dash on 12 o'clock
group_open("ticks", ambient_hide=True)
arc("ticks_gray", R_T, round(-half, 3), round(360 - half, 3), TICK_GRAY, 13, cap="BUTT", dash=dash)
arc("ticks_orange", R_T, round(-half, 3), round(360 - half, 3), ORANGE, 13, cap="BUTT", dash=dash,
    tx={"endAngle": f"-{half:.3f} + [SECOND]*6 + 2"})
# bright "now" marker on the current second
w('<Group name="sec_marker" x="0" y="0" width="480" height="480" pivotX="0.5" pivotY="0.5">', 3)
w('<Transform target="angle" value="[SECOND]*6"/>', 4)
w('<PartDraw x="0" y="0" width="480" height="480">', 4)
w('<RoundRectangle x="237" y="4" width="6" height="26" cornerRadiusX="3" cornerRadiusY="3">', 5)
w('<Fill color="#FFFFFF"/>', 6)
w('</RoundRectangle>', 5)
w('</PartDraw>', 4)
w('</Group>', 3)
# the little orange dot at 9 o'clock
w('<PartDraw name="dot9" x="0" y="0" width="480" height="480">', 3)
w('<Ellipse x="5" y="232" width="16" height="16">', 4)
w(f'<Fill color="{ORANGE}"/>', 5)
w('</Ellipse>', 4)
w('</PartDraw>', 3)
w('</Group>', 2)

# ---------------- battery arc (top, -45..+45 deg) ----------------
R_B = 200
group_open("battery", ambient_hide=True)
arc("batt_track", R_B, -45, 45, GREEN_DK, 12, ind=3)
arc("batt_fill", R_B, -45, 45, GREEN, 12, ind=3, tx={"endAngle": "-45 + 90*[BATTERY_PERCENT]/100"})
# charging shimmer: a pale segment that sweeps over the filled part (only while charging)
w('<Group name="shimmer" x="0" y="0" width="480" height="480">', 3)
w('<Transform target="alpha" value="clamp([BATTERY_CHARGING_STATUS]*255,0,255)"/>', 4)
sweep_s = "-45 + fract([SECOND_MILLISECOND]/2500)*max_(90*[BATTERY_PERCENT]/100-14,0)"
# 'max' isn't in WFF -> use clamp(x,0,360)
sweep_s = "-45 + fract([SECOND_MILLISECOND]/2500)*clamp(90*[BATTERY_PERCENT]/100-14,0,90)"
sweep_e = "-45 + fract([SECOND_MILLISECOND]/2500)*clamp(90*[BATTERY_PERCENT]/100-14,0,90) + 14"
arc("shimmer_arc", R_B, 0, 14, "#C9FFE9", 12, ind=4, tx={"startAngle": sweep_s, "endAngle": sweep_e})
w('</Group>', 3)
# bolt badge
w('<PartDraw name="bolt_bg" x="0" y="0" width="480" height="480">', 3)
w('<Ellipse x="216" y="13" width="48" height="48">', 4)
w('<Fill color="#1B1B1B"/>', 5)
w('</Ellipse>', 4)
w('</PartDraw>', 3)
w('<PartDraw name="bolt_ring" x="0" y="0" width="480" height="480">', 3)
w('<Ellipse x="216" y="13" width="48" height="48">', 4)
w('<Stroke color="#555555" thickness="2"/>', 5)
w('</Ellipse>', 4)
w('</PartDraw>', 3)
w('<PartImage name="bolt" x="228" y="21" width="24" height="32">', 3)
w('<Image resource="bolt"/>', 4)
w('</PartImage>', 3)
text("batt_pct", 140, 62, 200, 30, tpl("%d%%", "[BATTERY_PERCENT]"), MONO, 22, GREEN)
text("batt_state_on", 140, 90, 200, 20, "CHARGING", MONO, 13, GREEN, spacing=1,
     tx={"alpha": "clamp([BATTERY_CHARGING_STATUS]*255,0,255)"})
text("batt_state_off", 140, 90, 200, 20, "BATTERY", MONO, 13, "#7FD9B8", spacing=1,
     tx={"alpha": "255-clamp([BATTERY_CHARGING_STATUS]*255,0,255)"})
w('</Group>', 2)

# ---------------- heart-rate arc (right) ----------------
R_H = 205
H0, H1 = 22, 152          # track spans 22..152 deg (1 o'clock .. ~5 o'clock)
group_open("heart", ambient_hide=True)
arc("hr_track", R_H, H0, H1, RED_DK, 12, ind=3)
# red fill grows upward from the bottom end as BPM rises (40..180 bpm)
arc("hr_fill", R_H, H0, H1, RED, 12, ind=3,
    tx={"startAngle": f"{H1} - {H1-H0}*clamp(([HEART_RATE]-40)/140,0.04,1)"})
w('<PartDraw name="heart_icon" x="0" y="0" width="480" height="480">', 3)
w('<Ellipse x="381" y="142" width="9" height="9"><Fill color="#FF2D46"/></Ellipse>', 4)
w('<Ellipse x="388" y="142" width="9" height="9"><Fill color="#FF2D46"/></Ellipse>', 4)
w('<RoundRectangle x="382" y="147" width="14" height="9" cornerRadiusX="3" cornerRadiusY="3"><Fill color="#FF2D46"/></RoundRectangle>', 4)
w('</PartDraw>', 3)
circ_text("hr_text", C, C, 168, 112, 62, "COUNTER_CLOCKWISE", tpl("%d BPM", "[HEART_RATE]"), MONO, 17, RED)
w('</Group>', 2)

# ---------------- left rings (steps etc.) ----------------
L0, L1 = 247, 312
group_open("left", ambient_hide=True)
for i, (r, trackc) in enumerate(((205, "#2A2D14"), (197, "#3A1230"), (189, "#0E2A24"))):
    arc(f"left_track{i}", r, L0, L1, trackc, 5, ind=3)
arc("steps_fill", 205, L0, L1, "#26D07C", 5, ind=3,
    tx={"startAngle": f"{L0}", "endAngle": f"{L0} + {L1-L0}*clamp([STEP_PERCENT]/100,0.03,1)"})
circ_text("kcal_txt", C, C, 168, 285, 308, "CLOCKWISE", 'KCAL', MONO, 13, "#FF5FA8")
circ_text("steps_txt", C, C, 168, 262, 284, "CLOCKWISE", tpl("%d STEPS", "[STEP_COUNT]"), MONO, 13, "#26D07C")
w('</Group>', 2)

# ---------------- sleep (bottom) ----------------
group_open("sleep", ambient_hide=True)
arc("sleep_arc", 195, 130, 230, "#2CCF9A", 14, ind=3)
circ_text("sleep_txt", C, C, 168, 212, 148, "COUNTER_CLOCKWISE", 'SLEEP', MONO, 15, "#2CCF9A", spacing=1)
w('</Group>', 2)

# ---------------- date + time ----------------
text("date", 90, 118, 300, 30,
     tpl("%s %d %s", "[DAY_OF_WEEK_S]", "[DAY]", "[MONTH_S]", upper=True), MONO, 21, "#FFFFFF", spacing=2)
w('<DigitalClock x="60" y="150" width="360" height="120">', 2)
w('<TimeText format="h:mm" hourFormat="SYNC_TO_DEVICE" align="CENTER" x="0" y="0" width="360" height="120">', 3)
w(f'<Font family="{GROTESK}" size="96" color="#FFFFFF"/>', 4)
w('</TimeText>', 3)
w('</DigitalClock>', 2)

# ---------------- complications ----------------
def slot(sid, cx, ring, fill, default, dtype, display):
    r = 41
    w(f'<PartDraw name="ring{sid}" x="0" y="0" width="480" height="480">', 2)
    w(f'<Ellipse x="{cx-r+3}" y="{337-r+3}" width="{2*r-6}" height="{2*r-6}">', 3)
    w(f'<Stroke color="{ring}" thickness="6"/>', 4)
    w('</Ellipse>', 3)
    w('</PartDraw>', 2)
    x, y, s = cx - 36, 337 - 36, 72
    w(f'<ComplicationSlot slotId="{sid}" name="slot{sid}" displayName={quoteattr(display)} x="{x}" y="{y}" width="{s}" height="{s}" supportedTypes="SHORT_TEXT SMALL_IMAGE MONOCHROMATIC_IMAGE" isCustomizable="TRUE">', 2)
    w(f'<DefaultProviderPolicy defaultSystemProvider="{default}" defaultSystemProviderType="{dtype}"/>', 3)
    w(f'<BoundingOval x="0" y="0" width="{s}" height="{s}"/>', 3)
    # SHORT_TEXT: big value + small title
    w('<Complication type="SHORT_TEXT">', 3)
    w(f'<PartText x="0" y="12" width="{s}" height="28"><Text align="CENTER">', 4)
    w(f'<Font family="{MONO}" size="19" color="#FFFFFF">', 5)
    w('<Template>%s<Parameter expression="[COMPLICATION.TEXT]"/></Template>', 6)
    w('</Font>', 5)
    w('</Text></PartText>', 4)
    w(f'<PartText x="0" y="38" width="{s}" height="20"><Text align="CENTER">', 4)
    w(f'<Font family="{MONO}" size="12" color="#E6E6E6">', 5)
    w('<Template>%s<Parameter expression="[COMPLICATION.TITLE]"/></Template>', 6)
    w('</Font>', 5)
    w('</Text></PartText>', 4)
    w('</Complication>', 3)
    w('<Complication type="SMALL_IMAGE">', 3)
    w(f'<PartImage x="6" y="6" width="{s-12}" height="{s-12}"><Image resource="[COMPLICATION.SMALL_IMAGE]"/></PartImage>', 4)
    w('</Complication>', 3)
    w('<Complication type="MONOCHROMATIC_IMAGE">', 3)
    w(f'<PartImage x="14" y="14" width="{s-28}" height="{s-28}" tintColor="#FFFFFF"><Image resource="[COMPLICATION.MONOCHROMATIC_IMAGE]"/></PartImage>', 4)
    w('</Complication>', 3)
    w('</ComplicationSlot>', 2)

slot(1, 149, "#10304A", "#FFFFFF", "APP_SHORTCUT", "SMALL_IMAGE", "Left (Spotify)")
slot(2, 240, "#FFC400", "#FFFFFF", "SUNRISE_SUNSET", "SHORT_TEXT", "Middle (Weather)")
slot(3, 331, "#4A3C00", "#FFFFFF", "APP_SHORTCUT", "SMALL_IMAGE", "Right (Buds)")

w('</Scene>', 1)
w('</WatchFace>')

os.makedirs(f"{OUT}/raw", exist_ok=True)
with open(f"{OUT}/raw/watchface.xml", "w") as f:
    f.write("\n".join(out) + "\n")

# ---- bolt icon ----
try:
    from PIL import Image, ImageDraw
    S = 8
    im = Image.new("RGBA", (24 * S, 32 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = [(14, 0), (2, 18), (10, 18), (8, 32), (22, 12), (13, 12)]
    d.polygon([(x * S, y * S) for x, y in pts], fill=(255, 255, 255, 255))
    im = im.resize((48, 64), Image.LANCZOS)
    os.makedirs(f"{OUT}/drawable", exist_ok=True)
    im.save(f"{OUT}/drawable/bolt.png")
except ImportError:
    print("Pillow missing: skipped bolt.png")
