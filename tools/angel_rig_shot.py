"""Rig proof image: the 14-bone armature drawn over the v10 feather wing."""
import json
import math
import pathlib
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import render_mesh as rm  # noqa: E402
import angelv10 as av  # noqa: E402
import angelrig_v3 as rig  # noqa: E402

ARTS = ROOT / "art-wings" / "feathers"
BONE = (0.95, 0.90, 0.78)
GOLD = (1.00, 0.78, 0.30)

# finalized armature chain in wing-local coords (matches the Blockbench rig)
CHAIN = [(0.0, -3.0), (0.0, 0.0), (3.49, 3.99), (7.00, 7.19), (10.0, 8.99)]
FINGERS = [((10.0, 8.99), (13.49, 10.49)), ((10.0, 8.99), (14.02, 6.97)),
           ((10.0, 8.99), (12.48, 4.53))]


def bone_quads():
    quads = []
    for side in (1, -1):
        def m(p, z=5.0):
            x = p[0] if side > 0 else -p[0]
            return (x + 1.55, p[1] + 27.0, z + 2.6)

        segs = [(CHAIN[0], CHAIN[1], 0.34, 0.30),
                (CHAIN[1], CHAIN[2], 0.34, 0.26),
                (CHAIN[2], CHAIN[3], 0.26, 0.21),
                (CHAIN[3], CHAIN[4], 0.21, 0.16)]
        segs += [(a, b, 0.13, 0.07) for a, b in FINGERS]
        for a, b, r0, r1 in segs:
            for v, _u, t in rig.tube(m(a), m(b), r0, r1, sides=7, segs=4, tint=BONE):
                quads.append((v, None, t, "bone"))
        for p, r in ((CHAIN[0], 0.40), (CHAIN[1], 0.36), (CHAIN[2], 0.30),
                     (CHAIN[3], 0.26), (CHAIN[4], 0.22)):
            for v, _u, t in rig.ball(m(p), r, tint=GOLD, sides=8, rings=5):
                quads.append((v, None, t, "bone"))
    return quads


def main():
    rects = json.loads((ARTS / "seraph_atlas_rects.json").read_text())
    feathers = av.layout(rects)
    fq = []
    for side in (1, -1):
        for f in feathers:
            fq += av.s8.feather_quads(f, rects, side)
    bones = bone_quads()
    allv, allf, allu, allc = [], [], [], []
    for verts4, uv4, tint in fq:
        base = len(allv)
        for (x, y, z), (u, v) in zip(verts4, uv4):
            allv.append([x + av.ROOT_X, y + av.ROOT_Y, z + av.ROOT_Z])
            allu.append([u / av.ATLAS_W, v / av.ATLAS_H])
            allc.append(tint)
        allf += [(base, base + 1, base + 2), (base, base + 2, base + 3)]
    for verts4, _uv, tint, _tag in bones:
        base = len(allv)
        for x, y, z in verts4:
            allv.append([x, y, z])
            allu.append([0.5, 0.5])
            allc.append(tint)
        allf += [(base, base + 1, base + 2), (base, base + 2, base + 3)]
    allv = np.array(allv, float)
    allf = np.array(allf, np.int64)
    allu = np.array(allu, float)
    allc = np.array(allc, float)
    tex = np.asarray(Image.open(ARTS / "seraph_feather_atlas.png").convert("RGBA"), float)
    rgba = rm.render_view(allv, allf, allu, tex, np.eye(3), 2200, alpha=True,
                          shade_lo=0.66, shade_hi=0.42, colors=allc)
    lo, hi = allv.min(0), allv.max(0)
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
    bg[:] = np.array([30, 34, 46]) * (1 - yy) + np.array([16, 18, 26]) * yy
    base = Image.fromarray(bg.astype(np.uint8), "RGB").convert("RGBA")
    base.alpha_composite(im)
    out = base.convert("RGB")
    d = ImageDraw.Draw(out)
    d.text((24, 24), "ANGEL v10 ARMATURE - 14 bones (root, humerus, radius, hand, 3 fingers per wing)",
           fill=(235, 228, 205))
    out.save(ROOT / "_design" / "angel_v10_rig.png")
    print("saved rig")


if __name__ == "__main__":
    main()
