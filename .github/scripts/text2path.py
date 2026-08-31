import sys, json
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform


def render(font_path, text, wght, size, letter_spacing=0.0):
    """Return (svg_path_d, advance_width) with baseline at y=0, text starting at x=0,
    scaled so that 1 em == `size` units, y flipped (SVG coords)."""
    f = TTFont(font_path)
    if "fvar" in f:
        f = instancer.instantiateVariableFont(f, {"wght": wght})
    upem = f["head"].unitsPerEm
    scale = size / upem
    cmap = f.getBestCmap()
    gs = f.getGlyphSet()
    hmtx = f["hmtx"]

    parts = []
    x = 0.0
    for ch in text:
        gname = cmap.get(ord(ch))
        if gname is None:
            gname = ".notdef"
        adv = hmtx[gname][0] * scale
        pen = SVGPathPen(gs, ntos=lambda v: f"{v:.2f}")
        tpen = TransformPen(pen, Transform(scale, 0, 0, -scale, x, 0))
        gs[gname].draw(tpen)
        d = pen.getCommands()
        if d:
            parts.append(d)
        x += adv + letter_spacing
    if text:
        x -= letter_spacing
    return " ".join(parts), x


if __name__ == "__main__":
    cfg = json.loads(sys.argv[1])
    d, w = render(cfg["font"], cfg["text"], cfg.get("wght", 700),
                  cfg.get("size", 100), cfg.get("ls", 0.0))
    print(json.dumps({"d": d, "w": w}))
