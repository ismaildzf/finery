"""Angel v10 - dense textured-feather wing on the proven v8 feather engine.

Layout follows the approved Lunar silhouette: long leading feathers fan along
the top/outer edge, long primaries hang in a bottom fan, secondaries fill the
inner edge, and four rows of covert sprites build the rounded shoulder cap.
Feathers are layered in z with a backward sweep, so the wing has real volume.
"""
import json
import math
import pathlib
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parents[1]
ART = ROOT / "art-wings" / "feathers"
OUT = ROOT / "_design"
sys.path.insert(0, str(ROOT / "tools"))
import render_mesh as rm  # noqa: E402
import seraph_v8 as s8  # noqa: E402

s8.SWEEP_DEG = 9.0
s8.ROOT_X = 0.0
ATLAS_W = ATLAS_H = 1024
ROOT_X = 1.55
ROOT_Y = 27.0
ROOT_Z = 2.60
X_OUT = 23.35
Y_TOP, Y_BOT = 11.6, -19.6
X_SHIFT = 2.0
X_SCALE = (X_OUT - X_SHIFT) / X_OUT


def warp_x(x):
    return X_SHIFT + x * X_SCALE


def lerp(a, b, u):
    return a + (b - a) * u


def resample(points, n):
    pts = np.array(points, float)
    d = np.sqrt(((pts[1:] - pts[:-1]) ** 2).sum(1))
    cum = np.concatenate([[0.0], np.cumsum(d)])
    out = []
    for k in range(n):
        sdist = cum[-1] * k / (n - 1)
        i = min(max(int(np.searchsorted(cum, sdist) - 1), 0), len(pts) - 2)
        t = (sdist - cum[i]) / max(d[i], 1e-9)
        q = pts[i] + (pts[i + 1] - pts[i]) * t
        out.append((float(q[0]), float(q[1])))
    return out


OUTER = [(7.0, 11.6), (7.6, 11.2), (10.8, 9.61), (13.54, 7.63),
         (16.34, 5.64), (18.26, 3.65), (20.13, 1.66), (20.87, -0.32),
         (22.0, -2.31), (22.84, -4.3), (23.35, -6.29), (23.35, -8.27)]
BOTTOM = [(22.3, -13.1), (21.4, -15.9), (20.45, -18.5), (17.5, -19.2),
          (14.62, -19.25), (12.4, -18.4), (10.51, -17.2), (9.0, -15.9),
          (7.85, -14.3), (6.6, -12.9), (5.46, -11.4), (4.7, -9.7), (4.02, -7.97)]
INNER = [(1.0, 2.2), (1.6, 0.2), (2.2, -1.8), (2.9, -3.8), (3.7, -5.8), (4.2, -7.4)]


def feather_entry(base, tip, width, z, cup, twist, sprite, tag, tint):
    dx, dy = tip[0] - base[0], tip[1] - base[1]
    return dict(base=(warp_x(base[0]), base[1]), angle=math.degrees(math.atan2(dy, dx)),
                length=math.hypot(dx, dy), width=width, z=z, cup=cup, twist=twist,
                sprite=sprite, tag=tag, tint=tint)


def layout(rects):
    pa = s8.sprite_aspect(rects, "primary")
    sa = s8.sprite_aspect(rects, "secondary")
    ca = s8.sprite_aspect(rects, "covert")
    fe = []
    L = 12

    # leading fan: the long feathers that draw the top and outer edge
    tips = OUTER
    roots = resample([(6.2, 6.8), (6.6, 6.4), (6.9, 5.9), (7.2, 5.4),
                      (7.5, 4.9), (7.8, 4.4), (8.0, 3.9), (8.2, 3.4),
                      (8.4, 2.9), (8.6, 2.4), (8.7, 1.9), (8.7, 1.4)], L)
    for i, (r, t) in enumerate(zip(roots, tips)):
        ln = math.hypot(t[0] - r[0], t[1] - r[1])
        fe.append(feather_entry(r, t, ln * pa * 0.80, 0.52 + 0.015 * i,
                                0.30, 0.10, "primary", "primary",
                                (0.88 - 0.004 * i, 0.935 - 0.003 * i, 1.06)))

    # primaries: bottom fan from the folded hand
    roots = resample([(9.6, 0.9), (9.0, 0.4), (8.4, -0.1), (7.7, -0.7),
                      (7.0, -1.4), (6.2, -2.1), (5.5, -2.9), (4.8, -3.5),
                      (4.4, -3.8)], 18)
    tips = resample(BOTTOM, 18)
    for i, (r, t) in enumerate(zip(roots, tips)):
        ln = math.hypot(t[0] - r[0], t[1] - r[1])
        fe.append(feather_entry(r, t, ln * pa * 0.86, 0.34 + 0.012 * i,
                                0.34, 0.12, "primary", "primary",
                                (0.85, 0.91, 1.06)))

    # secondaries: short inner feathers closing the body side
    roots = resample([(5.4, 2.6), (5.0, 1.4), (4.6, 0.2), (4.2, -1.0),
                      (3.9, -2.2), (3.6, -3.2)], 8)
    tips = resample(INNER, 8)
    for i, (r, t) in enumerate(zip(roots, tips)):
        ln = math.hypot(t[0] - r[0], t[1] - r[1])
        fe.append(feather_entry(r, t, ln * sa * 0.95, 0.50 + 0.02 * i,
                                0.24, 0.10, "secondary", "secondary",
                                (0.78, 0.855, 1.04)))

    # covert rows over the shoulder cap (top to bottom)
    rows = [
        # (y base line start/end, count, length, z, angle range, sprite, width factor)
        ((1.6, 7.4), (6.8, 5.6), 8, 1.9, 1.52, (56, 26), "covert", 0.92),
        ((1.4, 5.4), (7.4, 3.8), 10, 2.6, 1.34, (64, 26), "covert", 0.90),
        ((1.6, 3.2), (7.8, 1.6), 13, 3.1, 1.16, (72, 24), "secondary", 0.80),
        ((1.9, 0.8), (8.0, -1.3), 14, 3.1, 0.96, (78, 22), "secondary", 0.78),
    ]
    for ri, (a, b, n, ln0, z, (a0, a1), sprite, wf) in enumerate(rows):
        aspect = s8.sprite_aspect(rects, sprite)
        for i in range(n):
            u = i / (n - 1)
            bx = lerp(a[0], b[0], u)
            by = lerp(a[1], b[1], u)
            ang = math.radians(lerp(a0, a1, u) + 1.8 * math.sin(i * 2.1 + ri))
            ln = ln0 * (0.94 + 0.08 * math.sin(i * 1.7 + ri))
            tip = (bx + math.cos(ang) * ln, by + math.sin(ang) * ln)
            shade = (0.82, 0.88, 1.0) if ri == 3 else (0.93 - 0.012 * ri, 0.955 - 0.010 * ri, 1.05)
            fe.append(feather_entry((bx, by), tip, ln * aspect * wf,
                                    z + 0.012 * i, 0.22, 0.10, sprite, "covert", shade))

    # three long spikes above the covert crown (the Lunar signature)
    for i, (bx, by, ang, ln) in enumerate(((6.0, 5.4, 80, 7.0),
                                           (6.7, 4.9, 71, 7.4),
                                           (7.4, 4.4, 61, 7.2))):
        a = math.radians(ang)
        tip = (bx + math.cos(a) * ln, by + math.sin(a) * ln)
        fe.append(feather_entry((bx, by), tip, ln * pa * 0.40, 1.84 + 0.02 * i,
                                0.20, 0.06, "primary", "spike",
                                (0.90, 0.945, 1.03)))

    # armpit feathers closing the notch under the covert rows
    for i, (r, t_pt) in enumerate((((4.6, -0.8), (3.9, -5.6)),
                                   ((5.3, -1.6), (4.7, -6.6)),
                                   ((6.0, -2.4), (5.7, -7.6)),
                                   ((6.7, -3.2), (6.8, -8.6)))):
        ln = math.hypot(t_pt[0] - r[0], t_pt[1] - r[1])
        fe.append(feather_entry(r, t_pt, ln * sa * 0.72, 0.66 + 0.02 * i,
                                0.20, 0.08, "secondary", "secondary",
                                (0.80, 0.87, 1.03)))

    return fe


# ── preview ──────────────────────────────────────────────────────────────
def proxy_boxes():
    boxes = [((-4, 24, -4), (4, 32, 4), (0.34, 0.24, 0.16)),
             ((-4, 12, -2), (4, 24, 2), (0.16, 0.62, 0.66)),
             ((-4, 0, -2), (0, 12, 2), (0.20, 0.22, 0.72)),
             ((0, 0, -2), (4, 12, 2), (0.20, 0.22, 0.72)),
             ((-8, 12, -2), (-4, 24, 2), (0.74, 0.54, 0.40)),
             ((4, 12, -2), (8, 24, 2), (0.74, 0.54, 0.40))]
    pv, pf, pu, pc = [], [], [], []
    for frm, to, col in boxes:
        corners = [(frm[0], frm[1], frm[2]), (to[0], frm[1], frm[2]),
                   (to[0], to[1], frm[2]), (frm[0], to[1], frm[2]),
                   (frm[0], frm[1], to[2]), (to[0], frm[1], to[2]),
                   (to[0], to[1], to[2]), (frm[0], to[1], to[2])]
        for q in ((0, 1, 2, 3), (5, 4, 7, 6), (4, 5, 1, 0),
                  (2, 3, 7, 6), (4, 0, 3, 7), (1, 5, 6, 2)):
            base = len(pv)
            for idx in q:
                pv.append(list(corners[idx]))
                pu.append((0.88, 0.88))
                pc.append(col)
            pf += [(base, base + 1, base + 2), (base, base + 2, base + 3)]
    return np.array(pv, float), pf, np.array(pu, float), np.array(pc, float)


def assemble(quads, body=True):
    verts, uvs, faces, cols = [], [], [], []
    for verts4, uv4, tint in quads:
        base = len(verts)
        for (x, y, z), (u, v) in zip(verts4, uv4):
            verts.append([x + ROOT_X, y + ROOT_Y, z + ROOT_Z])
            uvs.append([u / ATLAS_W, v / ATLAS_H])
            cols.append(tint)
        faces.append((base, base + 1, base + 2))
        faces.append((base, base + 2, base + 3))
    verts = np.array(verts, float)
    faces = np.array(faces, np.int64)
    uvs = np.array(uvs, float)
    cols = np.array(cols, float)
    if body:
        pv, pf, pu, pc = proxy_boxes()
        allv = np.vstack([pv, verts])
        allf = np.array(pf + [(a + len(pv), b + len(pv), c + len(pv)) for a, b, c in faces],
                        np.int64)
        allu = np.vstack([pu, uvs])
        allc = np.vstack([pc, cols])
    else:
        allv, allf, allu, allc = verts, faces, uvs, cols
    return allv, allf, allu, allc


def render(quads, atlas, body=True, out=1000):
    allv, allf, allu, allc = assemble(quads, body)
    tex = np.asarray(atlas.convert("RGBA"), float)
    rgba = rm.render_view(allv, allf, allu, tex, np.eye(3), 2200, alpha=True,
                          shade_lo=0.66, shade_hi=0.42, colors=allc)
    lo, hi = allv.min(0), allv.max(0)
    span = max(hi[0] - lo[0], hi[1] - lo[1])
    k = 2200 * 0.88 / span
    cx, cy = (lo[0] + hi[0]) * 0.5, (lo[1] + hi[1]) * 0.5
    rx = (0 - cx) * k + 1100
    ry = 1100 - (17.63 - cy) * k
    half = (out / 19.0) * k * 0.5
    x0, x1 = int(round(rx - half)), int(round(rx + half))
    y0, y1 = int(round(ry - half)), int(round(ry + half))
    pl, pt = max(0, -x0), max(0, -y0)
    pr, pb = max(0, x1 - 2200), max(0, y1 - 2200)
    canvas = np.zeros((2200 + pt + pb, 2200 + pl + pr, 4), np.float64)
    canvas[pt:pt + 2200, pl:pl + 2200] = rgba
    crop = canvas[y0 + pt:y1 + pt, x0 + pl:x1 + pl]
    im = Image.fromarray(crop.astype(np.uint8), "RGBA").resize((out, out), Image.LANCZOS)
    bg = np.zeros((out, out, 3), np.float64)
    yy = np.linspace(0, 1, out)[:, None, None]
    bg[:] = np.array([196, 200, 232]) * (1 - yy) + np.array([108, 112, 158]) * yy
    base = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    base.alpha_composite(im)
    return base.convert("RGB")


def view_sheet(quads, atlas, size=620, out=None):
    allv, allf, allu, allc = assemble(quads, True)
    tex = np.asarray(atlas.convert("RGBA"), float)
    views = [("back", np.eye(3)),
             ("3/4", rm.rot_y(-38) @ rm.rot_x(-8)),
             ("side", rm.rot_y(90)),
             ("3/4 low", rm.rot_y(40) @ rm.rot_x(12))]
    sheet = Image.new("RGB", (size * 4, size + 30), (24, 26, 33))
    d = ImageDraw.Draw(sheet)
    for i, (name, R) in enumerate(views):
        img = rm.render_view(allv, allf, allu, tex, R, size, alpha=True,
                             shade_lo=0.66, shade_hi=0.42, colors=allc)
        tile = Image.new("RGB", (size, size), (24, 26, 33))
        a = Image.fromarray(img, "RGBA")
        tile.paste(a, (0, 0), a)
        sheet.paste(tile, (i * size, 30))
        d.text((i * size + 10, 10), name, fill=(220, 214, 200))
    if out is not None:
        sheet.save(out)
    return sheet


def main():
    atlas = Image.open(ART / "seraph_feather_atlas.png").convert("RGBA")
    rects = json.loads((ART / "seraph_atlas_rects.json").read_text())
    feathers = layout(rects)
    quads = []
    for side in (1, -1):
        for f in feathers:
            quads += s8.feather_quads(f, rects, side)
    print("feathers", len(feathers), "quads", len(quads))
    back = render(quads, atlas)
    back.save(OUT / "angel_v10_back.png")
    render(quads, atlas, body=False).save(OUT / "angel_v10_clean.png")
    view_sheet(quads, atlas, out=OUT / "angel_v10_views.png")
    ref = Image.open(OUT / "angel_ref_big.png").convert("RGB").resize((800, 800), Image.LANCZOS)
    new_img = back.resize((800, 800), Image.LANCZOS)
    sheet = Image.new("RGB", (1620, 860), (24, 26, 33))
    sheet.paste(ref, (10, 50))
    sheet.paste(new_img, (810, 50))
    d = ImageDraw.Draw(sheet)
    d.text((12, 22), "LUNAR REFERENCE", fill=(220, 214, 200))
    d.text((812, 22), "ANGEL v10 - 100 textured feathers/wing", fill=(220, 214, 200))
    sheet.save(OUT / "angel_v10_compare.png")
    print("saved")


if __name__ == "__main__":
    main()
