"""v13 rig proof: the internal 14-bone armature drawn over the restored v3 wing."""
import pathlib
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import render_mesh as rm  # noqa: E402
import angelv13 as av  # noqa: E402
import angelrig_v3 as rig  # noqa: E402

BONE = (0.96, 0.93, 0.84)
GOLD = (1.0, 0.78, 0.30)
CHAIN = [(0.0, -4.4), (0.0, -1.9), (2.8, 1.6), (6.17, 4.43), (9.12, 6.5)]
FINGERS = [((9.12, 6.5), (12.3, 8.0)), ((9.12, 6.5), (13.1, 6.5)),
           ((9.12, 6.5), (12.3, 5.0))]
Z = 2.9


def bone_quads(side):
    def m(p):
        x = p[0] if side > 0 else -p[0]
        return (x, p[1], Z)

    out = []
    segs = [(CHAIN[0], CHAIN[1], 0.34, 0.30), (CHAIN[1], CHAIN[2], 0.34, 0.25),
            (CHAIN[2], CHAIN[3], 0.25, 0.20), (CHAIN[3], CHAIN[4], 0.20, 0.15)]
    segs += [(a, b, 0.12, 0.06) for a, b in FINGERS]
    for a, b, r0, r1 in segs:
        out += [(v, None, t, "bone") for v, _u, t in
                rig.tube(m(a), m(b), r0, r1, sides=7, segs=4, tint=BONE)]
    for c, r in ((CHAIN[0], 0.42), (CHAIN[1], 0.36), (CHAIN[2], 0.30),
                 (CHAIN[3], 0.24), (CHAIN[4], 0.18)):
        out += [(v, None, t, "bone") for v, _u, t in
                rig.ball(m(c), r, tint=GOLD, sides=8, rings=4)]
    return out


def main():
    base = Image.open(av.BASE_PNG).convert("RGBA")
    covert = Image.open(av.COVERT_PNG).convert("RGBA")
    sil = av.solid_mask()
    quads = []
    for side in (1, -1):
        quads += av.grid_quads(base, av.BASE_U0, side, 10, 0.0, back_off=1.0,
                               rim=False, mask=sil)
        quads += av.grid_quads(covert, av.COVERT_U0, side, 10, 0.72,
                               rim=False, tint=(0.985, 0.99, 1.0))
        quads += av.rod_quads(side)
        quads += bone_quads(side)
    verts, faces, uvs, cols = av.assemble(quads)
    atlas = Image.open(av.ATLAS).convert("RGBA")
    patch = Image.new("RGBA", (24, 24), (255, 255, 255, 255))
    atlas.paste(patch, (960, 660))
    tex = np.asarray(atlas, float)
    rgba = rm.render_view(verts, faces, uvs, tex, np.eye(3), 2200, alpha=True,
                          shade_lo=0.70, shade_hi=0.38, colors=cols)
    lo, hi = verts.min(0), verts.max(0)
    span = max(hi[0] - lo[0], hi[1] - lo[1])
    k = 2200 * 0.88 / span
    cx, cy = (lo[0] + hi[0]) * 0.5, (lo[1] + hi[1]) * 0.5
    rx = (0 - cx) * k + 1100
    ry = 1100 - (17.63 - cy) * k
    half = (1000 / 19.0) * k * 0.5
    x0, x1 = int(round(rx - half)), int(round(rx + half))
    y0, y1 = int(round(ry - half)), int(round(ry + half))
    pl, pt = max(0, -x0), max(0, -y0)
    pr, pb = max(0, x1 - 2200), max(0, y1 - 2200)
    canvas = np.zeros((2200 + pt + pb, 2200 + pl + pr, 4), np.float64)
    canvas[pt:pt + 2200, pl:pl + 2200] = rgba
    crop = canvas[y0 + pt:y1 + pt, x0 + pl:x1 + pl]
    im = Image.fromarray(crop.astype(np.uint8), "RGBA").resize((1000, 1000), Image.LANCZOS)
    bg = np.zeros((1000, 1000, 3), np.float64)
    yy = np.linspace(0, 1, 1000)[:, None, None]
    bg[:] = np.array([28, 32, 44]) * (1 - yy) + np.array([14, 16, 24]) * yy
    out = Image.fromarray(bg.astype(np.uint8), "RGB").convert("RGBA")
    out.alpha_composite(im)
    out = out.convert("RGB")
    d = ImageDraw.Draw(out)
    d.text((22, 22), "ANGEL v13 - restored v3 silhouette + internal 14-bone rig", fill=(235, 228, 205))
    out.save(ROOT / "_design" / "angel_v13_rig.png")
    print("saved")


if __name__ == "__main__":
    main()
