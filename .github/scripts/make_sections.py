import math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
from text2path import render

ORB = os.path.join(ROOT, ".fonts", "Orbitron.ttf")
JBM = os.path.join(ROOT, ".fonts", "JetBrainsMono.ttf")

V_MID = "#7C3AED"
V_BRIGHT = "#A855F7"
V_LIGHT = "#C4B5FD"
FUCHSIA = "#E879F9"
DIM = "#7E6BA0"

W, H = 1000, 56


def heptagon(cx, cy, r, rot=-90):
    return " ".join(
        f"{cx + r*math.cos(math.radians(rot + i*360/7)):.2f},"
        f"{cy + r*math.sin(math.radians(rot + i*360/7)):.2f}"
        for i in range(7)
    )


def section(idx, title, sub, fname):
    o = []
    a = o.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
      f'fill="none" role="img" aria-label="{title}">')
    a('<defs>')
    a(f'''<linearGradient id="r{idx}" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{V_BRIGHT}" stop-opacity="0.85"/>
      <stop offset="45%" stop-color="{FUCHSIA}" stop-opacity="0.30"/>
      <stop offset="100%" stop-color="{FUCHSIA}" stop-opacity="0"/>
    </linearGradient>''')
    a(f'''<linearGradient id="t{idx}" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#FFFFFF"/>
      <stop offset="100%" stop-color="{V_LIGHT}"/>
    </linearGradient>''')
    a(f'''<linearGradient id="h{idx}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{FUCHSIA}"/>
      <stop offset="100%" stop-color="{V_MID}"/>
    </linearGradient>''')
    a('<filter id="g" x="-70%" y="-70%" width="240%" height="240%">'
      '<feGaussianBlur stdDeviation="4"/></filter>')
    a('</defs>')

    # measure the chip width first so it works on light AND dark GitHub themes
    _, _wi = render(JBM, idx, 600, 13, 0.8)
    _, _wt = render(ORB, title, 700, 21, 1.6)
    _, _ws = render(JBM, sub, 400, 12, 0.4) if sub else (None, 0)
    chip_w = 46 + _wi + 14 + _wt + 16 + (_ws + 10 if sub else 0)
    a(f'<rect x="2" y="6" width="{chip_w:.0f}" height="44" rx="12" fill="#11071E"/>')
    a(f'<rect x="2.5" y="6.5" width="{chip_w-1:.0f}" height="43" rx="11.5" fill="none" '
      f'stroke="{V_MID}" stroke-opacity="0.40"/>')

    # heptagon bullet
    a(f'<polygon points="{heptagon(20, 28, 12)}" fill="none" stroke="url(#h{idx})" stroke-width="2" '
      f'stroke-linejoin="round"/>')
    a(f'<polygon points="{heptagon(20, 28, 12)}" fill="none" stroke="{V_BRIGHT}" stroke-opacity="0.7" '
      f'stroke-width="3" filter="url(#g)"/>')
    a(f'<circle cx="20" cy="28" r="3" fill="{FUCHSIA}">'
      f'<animate attributeName="opacity" values="0.4;1;0.4" dur="3s" repeatCount="indefinite"/></circle>')

    x = 46
    # index number
    di, wi = render(JBM, idx, 600, 13, 0.8)
    a(f'<g transform="translate({x},33)"><path d="{di}" fill="{FUCHSIA}" fill-opacity="0.9"/></g>')
    x += wi + 14

    # title
    dt, wt = render(ORB, title, 700, 21, 1.6)
    a(f'<g transform="translate({x},35)"><path d="{dt}" fill="{V_BRIGHT}" opacity="0.5" '
      f'filter="url(#g)"/><path d="{dt}" fill="url(#t{idx})"/></g>')
    x += wt + 16

    # subtitle
    if sub:
        ds, ws = render(JBM, sub, 400, 12, 0.4)
        a(f'<g transform="translate({x},33)"><path d="{ds}" fill="{DIM}"/></g>')
        x += ws + 16

    # gradient rule
    a(f'<rect x="{x+6}" y="27" width="{max(W - x - 22, 10)}" height="1.6" fill="url(#r{idx})"/>')
    a('</svg>')

    svg = "\n".join(o)
    with open(os.path.join(ROOT, "assets", fname), "w") as f:
        f.write(svg)
    print(fname, len(svg))


SECTIONS = [
    ("01", "ABOUT", "// whoami", "sec-about.svg"),
    ("02", "STACK", "// tools i build with", "sec-stack.svg"),
    ("03", "PROJECTS", "// things i shipped", "sec-projects.svg"),
    ("04", "STATS", "// the numbers", "sec-stats.svg"),
    ("05", "ACTIVITY", "// commit trail", "sec-activity.svg"),
    ("06", "CONNECT", "// say hi", "sec-connect.svg"),
]

for s in SECTIONS:
    section(*s)


# ---------------- footer ----------------
FW, FH = 1000, 150
o = []
a = o.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {FW} {FH}" width="{FW}" height="{FH}" '
  f'fill="none" role="img" aria-label="footer">')
a('<defs>')
a(f'''<linearGradient id="fg" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0%" stop-color="#5B21B6"/>
  <stop offset="45%" stop-color="#A855F7"/>
  <stop offset="100%" stop-color="#E879F9"/>
</linearGradient>''')
a(f'''<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0%" stop-color="#A855F7" stop-opacity="0"/>
  <stop offset="48%" stop-color="#A855F7" stop-opacity="0.30"/>
  <stop offset="100%" stop-color="#A855F7" stop-opacity="0"/>
</linearGradient>''')
a('<filter id="fgl" x="-50%" y="-50%" width="200%" height="200%">'
  '<feGaussianBlur stdDeviation="6"/></filter>')
a('</defs>')

# stacked waves
wave1 = ("M0 70 C 140 30, 250 106, 400 70 S 660 24, 810 62 S 940 96, 1000 74 "
         f"L1000 {FH} L0 {FH} Z")
wave2 = ("M0 92 C 160 58, 280 124, 430 92 S 680 50, 830 86 S 950 112, 1000 96 "
         f"L1000 {FH} L0 {FH} Z")
a(f'<path d="{wave2}" fill="url(#fade)" opacity="0.55"/>')
a(f'<path d="{wave1}" fill="url(#fade)" opacity="0.75"/>')
a(f'<path d="M0 70 C 140 30, 250 106, 400 70 S 660 24, 810 62 S 940 96, 1000 74" '
  f'stroke="url(#fg)" stroke-width="2.4" fill="none" filter="url(#fgl)" opacity="0.85"/>')
a(f'<path d="M0 70 C 140 30, 250 106, 400 70 S 660 24, 810 62 S 940 96, 1000 74" '
  f'stroke="url(#fg)" stroke-width="1.8" fill="none"/>')

# center heptagon mark
a(f'<g><polygon points="{heptagon(500, 108, 15)}" fill="none" stroke="#A855F7" stroke-opacity="0.9" '
  f'stroke-width="1.6" stroke-linejoin="round"/>'
  f'<animateTransform attributeName="transform" type="rotate" from="0 500 108" to="360 500 108" '
  f'dur="24s" repeatCount="indefinite"/></g>')
a('<circle cx="500" cy="108" r="3.2" fill="#E879F9">'
  '<animate attributeName="opacity" values="0.4;1;0.4" dur="2.6s" repeatCount="indefinite"/></circle>')

d, w = render(JBM, "> keep shipping.", 500, 14, 1.2)
a(f'<g transform="translate({500 - w/2:.1f},142)"><path d="{d}" fill="#8B5CF6" fill-opacity="0.95"/></g>')
a('</svg>')
svg = "\n".join(o)
with open(os.path.join(ROOT, "assets", "footer.svg"), "w") as f:
    f.write(svg)
print("footer.svg", len(svg))
