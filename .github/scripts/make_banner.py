import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
from text2path import render

ORB = os.path.join(ROOT, ".fonts", "Orbitron.ttf")
JBM = os.path.join(ROOT, ".fonts", "JetBrainsMono.ttf")

W, H = 1000, 260

# ---------- palette ----------
BG0 = "#0B0614"
BG1 = "#170B2B"
BG2 = "#0D0718"
V_DEEP = "#5B21B6"
V_MID = "#7C3AED"
V_BRIGHT = "#A855F7"
V_LIGHT = "#C4B5FD"
FUCHSIA = "#E879F9"
DIM = "#6D5A8C"

out = []
A = out.append

A(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
  f'fill="none" role="img" aria-label="Heptagon372 - Full-stack Developer">')

# ---------- defs ----------
A('<defs>')
A(f'''<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0%" stop-color="{BG0}"/>
  <stop offset="48%" stop-color="{BG1}"/>
  <stop offset="100%" stop-color="{BG2}"/>
</linearGradient>''')
A(f'''<linearGradient id="nameGrad" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0%" stop-color="#FFFFFF"/>
  <stop offset="42%" stop-color="{V_LIGHT}"/>
  <stop offset="78%" stop-color="{V_BRIGHT}"/>
  <stop offset="100%" stop-color="{FUCHSIA}"/>
</linearGradient>''')
A(f'''<linearGradient id="ruleGrad" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0%" stop-color="{V_BRIGHT}" stop-opacity="0.9"/>
  <stop offset="60%" stop-color="{FUCHSIA}" stop-opacity="0.35"/>
  <stop offset="100%" stop-color="{FUCHSIA}" stop-opacity="0"/>
</linearGradient>''')
A(f'''<radialGradient id="glowL" cx="0.5" cy="0.5" r="0.5">
  <stop offset="0%" stop-color="{V_MID}" stop-opacity="0.55"/>
  <stop offset="100%" stop-color="{V_MID}" stop-opacity="0"/>
</radialGradient>''')
A(f'''<radialGradient id="glowR" cx="0.5" cy="0.5" r="0.5">
  <stop offset="0%" stop-color="{FUCHSIA}" stop-opacity="0.40"/>
  <stop offset="100%" stop-color="{FUCHSIA}" stop-opacity="0"/>
</radialGradient>''')
A(f'''<linearGradient id="scan" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0%" stop-color="{V_LIGHT}" stop-opacity="0"/>
  <stop offset="50%" stop-color="{V_LIGHT}" stop-opacity="0.55"/>
  <stop offset="100%" stop-color="{V_LIGHT}" stop-opacity="0"/>
</linearGradient>''')
A(f'''<linearGradient id="hepStroke" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0%" stop-color="{FUCHSIA}"/>
  <stop offset="55%" stop-color="{V_BRIGHT}"/>
  <stop offset="100%" stop-color="{V_DEEP}"/>
</linearGradient>''')
A(f'''<pattern id="grid" width="26" height="26" patternUnits="userSpaceOnUse">
  <path d="M26 0H0V26" fill="none" stroke="{V_MID}" stroke-opacity="0.13" stroke-width="1"/>
</pattern>''')
A('''<filter id="soft" x="-60%" y="-60%" width="220%" height="220%">
  <feGaussianBlur stdDeviation="7"/>
</filter>''')
A('''<filter id="soft2" x="-80%" y="-80%" width="260%" height="260%">
  <feGaussianBlur stdDeviation="3"/>
</filter>''')
A(f'<clipPath id="card"><rect x="0" y="0" width="{W}" height="{H}" rx="16"/></clipPath>')
A('</defs>')

# ---------- styles / keyframes ----------
A(f'''<style>
  .flick {{ animation: flick 4.2s ease-in-out infinite; }}
  @keyframes flick {{ 0%,100%{{opacity:.85}} 45%{{opacity:.35}} 52%{{opacity:.95}} 60%{{opacity:.5}} }}
  .pulse {{ animation: pulse 3.4s ease-in-out infinite; }}
  @keyframes pulse {{ 0%,100%{{opacity:.30}} 50%{{opacity:.85}} }}
  .rise {{ animation: rise .9s cubic-bezier(.22,.9,.3,1) both; }}
  @keyframes rise {{ from{{opacity:0; transform:translateY(14px)}} to{{opacity:1; transform:translateY(0)}} }}
  .d1{{animation-delay:.05s}} .d2{{animation-delay:.28s}} .d3{{animation-delay:.5s}} .d4{{animation-delay:.72s}}
  .grow {{ transform-origin: 0 0; animation: grow 1s cubic-bezier(.22,.9,.3,1) .5s both; }}
  @keyframes grow {{ from{{transform:scaleX(0)}} to{{transform:scaleX(1)}} }}
</style>''')

A('<g clip-path="url(#card)">')

# ---------- background ----------
A(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
A(f'<rect width="{W}" height="{H}" fill="url(#grid)"/>')
A(f'<ellipse cx="120" cy="40" rx="360" ry="230" fill="url(#glowL)"/>')
A(f'<ellipse cx="812" cy="130" rx="330" ry="250" fill="url(#glowR)"/>')

# scanline sweep
A(f'<rect x="-260" y="0" width="260" height="{H}" fill="url(#scan)" opacity="0.30">')
A(f'  <animate attributeName="x" values="-260;{W}" dur="6s" repeatCount="indefinite"/>')
A('</rect>')

# faint horizontal HUD rules
for y, op in ((36, .16), (H - 36, .16)):
    A(f'<path d="M40 {y}H{W-40}" stroke="{V_MID}" stroke-opacity="{op}" stroke-width="1" stroke-dasharray="2 6"/>')

# ---------- heptagon HUD (right) ----------
CX, CY = 812, 130


def hep(r, rot=0.0):
    pts = []
    for i in range(7):
        a = math.radians(rot - 90 + i * 360 / 7)
        pts.append(f"{CX + r*math.cos(a):.2f},{CY + r*math.sin(a):.2f}")
    return " ".join(pts)


A('<g opacity="0.95">')
# outer glow ring
A(f'<circle cx="{CX}" cy="{CY}" r="104" fill="none" stroke="{V_MID}" stroke-opacity="0.22" stroke-width="1"/>')
A(f'<circle cx="{CX}" cy="{CY}" r="120" fill="none" stroke="{V_MID}" stroke-opacity="0.12" '
  f'stroke-width="1" stroke-dasharray="3 9"/>')

# rotating dashed arc ring
A(f'<g><circle cx="{CX}" cy="{CY}" r="112" fill="none" stroke="{FUCHSIA}" stroke-opacity="0.5" '
  f'stroke-width="1.6" stroke-linecap="round" stroke-dasharray="46 300" />'
  f'<animateTransform attributeName="transform" type="rotate" from="0 {CX} {CY}" to="360 {CX} {CY}" '
  f'dur="9s" repeatCount="indefinite"/></g>')
A(f'<g><circle cx="{CX}" cy="{CY}" r="112" fill="none" stroke="{V_LIGHT}" stroke-opacity="0.35" '
  f'stroke-width="1.6" stroke-linecap="round" stroke-dasharray="18 320" />'
  f'<animateTransform attributeName="transform" type="rotate" from="200 {CX} {CY}" to="-160 {CX} {CY}" '
  f'dur="13s" repeatCount="indefinite"/></g>')

# blurred heptagon halo
A(f'<polygon points="{hep(92)}" fill="none" stroke="{V_BRIGHT}" stroke-opacity="0.55" '
  f'stroke-width="6" filter="url(#soft)"/>')

# main heptagon, slow counter-rotation
A('<g>')
A(f'  <polygon points="{hep(92)}" fill="none" stroke="url(#hepStroke)" stroke-width="2.2" '
  f'stroke-linejoin="round"/>')
A(f'  <polygon points="{hep(64)}" fill="none" stroke="{V_MID}" stroke-opacity="0.55" stroke-width="1.2"/>')
# spokes + vertex nodes
for i in range(7):
    a = math.radians(-90 + i * 360 / 7)
    x1, y1 = CX + 64 * math.cos(a), CY + 64 * math.sin(a)
    x2, y2 = CX + 92 * math.cos(a), CY + 92 * math.sin(a)
    A(f'  <path d="M{x1:.2f} {y1:.2f}L{x2:.2f} {y2:.2f}" stroke="{V_MID}" stroke-opacity="0.45" stroke-width="1"/>')
    A(f'  <circle cx="{x2:.2f}" cy="{y2:.2f}" r="3.6" fill="{FUCHSIA}">'
      f'<animate attributeName="opacity" values="0.35;1;0.35" dur="2.6s" '
      f'begin="{i*0.24:.2f}s" repeatCount="indefinite"/></circle>')
A(f'  <animateTransform attributeName="transform" type="rotate" from="360 {CX} {CY}" to="0 {CX} {CY}" '
  f'dur="34s" repeatCount="indefinite"/>')
A('</g>')

# inner rotating triad + core
A(f'<g><polygon points="{hep(34, 25)}" fill="{V_MID}" fill-opacity="0.10" stroke="{V_LIGHT}" '
  f'stroke-opacity="0.5" stroke-width="1"/>'
  f'<animateTransform attributeName="transform" type="rotate" from="0 {CX} {CY}" to="360 {CX} {CY}" '
  f'dur="18s" repeatCount="indefinite"/></g>')
A(f'<circle cx="{CX}" cy="{CY}" r="15" fill="{FUCHSIA}" opacity="0.22" filter="url(#soft2)"/>')
A(f'<circle cx="{CX}" cy="{CY}" r="5.5" fill="{V_LIGHT}"><animate attributeName="r" '
  f'values="4.6;7;4.6" dur="2.8s" repeatCount="indefinite"/></circle>')

# HUD tick marks around the ring
for i in range(28):
    a = math.radians(i * 360 / 28)
    r1, r2 = (126, 134) if i % 7 == 0 else (128, 132)
    op = 0.6 if i % 7 == 0 else 0.22
    A(f'<path d="M{CX + r1*math.cos(a):.2f} {CY + r1*math.sin(a):.2f}'
      f'L{CX + r2*math.cos(a):.2f} {CY + r2*math.sin(a):.2f}" '
      f'stroke="{V_LIGHT}" stroke-opacity="{op}" stroke-width="1.4" stroke-linecap="round"/>')
A('</g>')

# ---------- left: text block ----------
LX = 62

# eyebrow
d_eb, w_eb = render(JBM, "> whoami", 500, 15, letter_spacing=1.6)
A(f'<g class="rise d1"><g transform="translate({LX},72)"><path d="{d_eb}" fill="{FUCHSIA}" '
  f'fill-opacity="0.95"/></g>')
A(f'<rect x="{LX + w_eb + 8}" y="59" width="9" height="16" fill="{FUCHSIA}" class="flick"/></g>')

# name
NAME = "HEPTAGON372"
d_nm, w_nm = render(ORB, NAME, 800, 46, letter_spacing=1.5)
A(f'<g class="rise d2"><g transform="translate({LX},128)">'
  f'<path d="{d_nm}" fill="{V_BRIGHT}" opacity="0.55" filter="url(#soft)"/>'
  f'<path d="{d_nm}" fill="url(#nameGrad)"/></g></g>')

# rule
A(f'<g class="rise d3"><rect x="{LX}" y="146" width="{w_nm:.0f}" height="2" fill="url(#ruleGrad)" '
  f'class="grow"/></g>')

# subtitle
SUB = "Full-Stack Developer  ·  Seoul, KR"
d_sb, w_sb = render(JBM, SUB, 450, 16, letter_spacing=0.4)
A(f'<g class="rise d3"><g transform="translate({LX},180)"><path d="{d_sb}" fill="{V_LIGHT}" '
  f'fill-opacity="0.86"/></g></g>')

# chips
chips = ["Next.js", "Supabase", "Python", "Infra"]
cx = LX
A('<g class="rise d4">')
for c in chips:
    dc, wc = render(JBM, c, 500, 12, letter_spacing=0.6)
    cw = wc + 22
    A(f'<rect x="{cx:.1f}" y="200" width="{cw:.1f}" height="24" rx="12" fill="{V_MID}" '
      f'fill-opacity="0.16" stroke="{V_BRIGHT}" stroke-opacity="0.42"/>')
    A(f'<g transform="translate({cx + 11:.1f},216)"><path d="{dc}" fill="{V_LIGHT}"/></g>')
    cx += cw + 9
A('</g>')

# corner brackets
for (bx, by, sx, sy) in ((22, 22, 1, 1), (W - 22, 22, -1, 1), (22, H - 22, 1, -1), (W - 22, H - 22, -1, -1)):
    A(f'<path d="M{bx} {by + sy*20}V{by}H{bx + sx*20}" stroke="{V_BRIGHT}" stroke-opacity="0.55" '
      f'stroke-width="1.6" fill="none" stroke-linecap="round"/>')

A(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="{V_MID}" '
  f'stroke-opacity="0.45"/>')
A('</g></svg>')

svg = "\n".join(out)
with open(os.path.join(ROOT, "assets", "header.svg"), "w") as f:
    f.write(svg)
print("bytes:", len(svg))
