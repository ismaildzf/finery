"""Placement test: G wing art at reference scale, several boxes."""
import sys
import pathlib

import numpy as np
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import angelwing_v3 as av
import render_mesh as rm

BG_TOP = np.array([196, 200, 232])
BG_BOT = np.array([108, 112, 158])
UNIT_PX = 19.0
CY = 17.63


def fixed_render(atlas, quads, out=1000, S=2600):
    tex = np.asarray(atlas.convert("RGBA"), float)
    v, f, u, c = av.to_arrays(quads)
    pv, pf, pu, pc = av.body_proxy()
    allv = np.vstack([pv, v])
    allf = np.array(pf + [(a + len(pv), b + len(pv), c2 + len(pv)) for a, b, c2 in f],
                    np.int64)
    allu = np.vstack([pu, u])
    allc = np.vstack([pc, c])
    rgba = rm.render_view(allv, allf, allu, tex, np.eye(3), S, alpha=True,
                          shade_lo=0.90, shade_hi=0.10, colors=allc)
    lo, hi = allv.min(0), allv.max(0)
    span = max(hi[0] - lo[0], hi[1] - lo[1])
    k = S * 0.88 / span
    cx, cy = (lo[0] + hi[0]) * 0.5, (lo[1] + hi[1]) * 0.5
    rx = (0 - cx) * k + S * 0.5
    ry = S * 0.5 - (CY - cy) * k
    half = (out / UNIT_PX) * k * 0.5
    x0, x1 = int(round(rx - half)), int(round(rx + half))
    y0, y1 = int(round(ry - half)), int(round(ry + half))
    pl, pt = max(0, -x0), max(0, -y0)
    pr, pb = max(0, x1 - S), max(0, y1 - S)
    canvas = np.zeros((S + pt + pb, S + pl + pr, 4), np.float64)
    canvas[pt:pt + S, pl:pl + S] = rgba
    crop = canvas[y0 + pt:y1 + pt, x0 + pl:x1 + pl]
    im = Image.fromarray(crop.astype(np.uint8), "RGBA").resize((out, out), Image.LANCZOS)
    bg = np.zeros((out, out, 3), np.float64)
    yy = np.linspace(0, 1, out)[:, None, None]
    bg[:] = BG_TOP * (1 - yy) + BG_BOT * yy
    base = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    base.alpha_composite(im)
    return base.convert("RGB")


def main():
    wing, overlay, atlas = av.build_wing_texture()
    variants = [
        ("wide22 h28", -23.5, -1.55, 35.74, 7.79),
        ("wide26 h30", -26.0, -1.55, 37.5, 7.5),
        ("wide25 h33", -25.0, -1.55, 40.0, 7.0),
        ("wide24 h31", -24.9, -1.55, 38.6, 7.4),
        ("wide22 h31", -23.5, -1.55, 38.6, 7.4),
    ]
    imgs = []
    for name, xo, xi, yt, yb in variants:
        av.set_box(xo, xi, yt, yb)
        quads = av.all_quads(wing, overlay)
        img = fixed_render(atlas, quads)
        img.save(ROOT / "_design" / f"angel_place_{name.replace(' ', '_')}.png")
        imgs.append((name, img))
        print("done", name, len(quads))
    ref = Image.open(ROOT / "_design" / "angel_ref_big.png").convert("RGB")
    cols = 3
    rows = 2
    cell = 520
    sheet = Image.new("RGB", (cols * cell, rows * (cell + 26)), (22, 24, 30))
    d = ImageDraw.Draw(sheet)
    items = [("LUNAR reference", ref)] + imgs
    for i, (name, im) in enumerate(items):
        x, y = (i % cols) * cell, (i // cols) * (cell + 26)
        sheet.paste(im.resize((cell, cell), Image.LANCZOS), (x, y + 26))
        d.text((x + 8, y + 7), name, fill=(235, 230, 210))
    sheet.save(ROOT / "_design" / "angel_place_sheet.png")
    print("sheet saved")


if __name__ == "__main__":
    main()
