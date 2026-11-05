"""Angel v11 - restore the approved v3 silhouette, now as a thick curved mesh
with a visible ivory/gold armature (bones) over it.

The v3 art (base wing + raised covert sheet) stays exactly as approved; the
mesh adds a front surface, a dark underside, a rim for thickness, and the
shoulder->elbow->wrist->hand->fingers skeleton.
"""
import math
import pathlib
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parents[1]
ART = ROOT / "art-wings" / "angel"
OUT = ROOT / "_design"
sys.path.insert(0, str(ROOT / "tools"))
import render_mesh as rm  # noqa: E402
import angelrig_v3 as rig  # noqa: E402

BASE_PNG = ART / "angel_v3_wing.png"
COVERT_PNG = ART / "angel_v3_covert.png"
ATLAS = ART / "angel_v3_atlas.png"
AW = AH = 1024
X_OUT = 23.35
Y_TOP, Y_BOT = 11.6, -19.6
BASE_U0 = 8.0
COVERT_U0 = 516.0
TEX_V0 = 8.0
WING_W, WING_H = 500, 628

BONE = (0.95, 0.92, 0.83)
GOLD = (0.98, 0.76, 0.30)
BONE_DARK = (0.80, 0.76, 0.66)

# skeleton in wing-local coords (x outboard, y up)
SHOULDER = (0.9, -4.4, 1.90)
ELBOW = (4.1, 0.1, 1.90)
WRIST = (7.9, 4.3, 1.90)
HAND = (11.3, 6.7, 1.90)
FINGERS = [((11.3, 6.7), (15.2, 7.6)), ((11.3, 6.7), (18.4, 5.4)),
           ((11.3, 6.7), (20.8, 3.0)), ((11.3, 6.7), (21.8, 0.4))]


OUTLINE = [(7.0, 11.6), (7.6, 11.2), (10.8, 9.61), (13.54, 7.63),
           (16.34, 5.64), (18.26, 3.65), (20.13, 1.66), (20.87, -0.32),
           (22.0, -2.31), (22.84, -4.3), (23.35, -6.29), (23.35, -8.27),
           (22.3, -13.1), (21.4, -15.9), (20.45, -18.5), (17.5, -19.2),
           (14.62, -19.25), (12.4, -18.4), (10.51, -17.2), (9.0, -15.9),
           (7.85, -14.3), (6.6, -12.9), (5.46, -11.4), (4.7, -9.7),
           (4.02, -7.97), (4.1, -6.3), (4.4, -5.3), (4.1, -3.3),
           (3.1, -2.3), (2.8, 0.7), (1.7, 1.7), (1.4, 2.7), (1.1, 3.6),
           (0.2, 4.6), (0.4, 5.6), (1.7, 6.6), (3.6, 7.6), (4.4, 8.6),
           (4.7, 9.6), (5.0, 10.6), (6.3, 11.6)]


def solid_mask():
    img = Image.new("L", (WING_W, WING_H), 0)
    d = ImageDraw.Draw(img)
    pts = [((WING_W - x / X_OUT * WING_W), (Y_TOP - y) / (Y_TOP - Y_BOT) * WING_H)
           for x, y in OUTLINE]
    d.polygon(pts, fill=255)
    return np.asarray(img) > 127


def mirror(p):
    return (-p[0], p[1], p[2])


def surface_z(x, y, lift=0.0):
    xn = min(max(x / X_OUT, 0.0), 1.0)
    yn = min(max((y - Y_BOT) / (Y_TOP - Y_BOT), 0.0), 1.0)
    return 0.20 + 0.85 * math.sin(math.pi * xn * 0.9) + 0.40 * yn + 1.00 * xn * xn + lift


def uv_of(u0, v):
    return ((u0 + 0.0) / AW, (TEX_V0 + v) / AH)


def grid_quads(img, u0_cell, side, cell, lift=0.0, back_off=0.0,
               back_tint=(0.55, 0.62, 0.80), rim=True, tint=(1, 1, 1), mask=None):
    rgba = np.asarray(img.convert("RGBA"))
    alpha = rgba[:, :, 3]
    H, W = alpha.shape
    if mask is None:
        mask = alpha > 200
    inside = {}
    for v0 in range(0, H - cell + 1, cell):
        for u0 in range(0, W - cell + 1, cell):
            inside[(u0, v0)] = bool(mask[v0, u0] and mask[v0, u0 + cell - 1]
                                    and mask[v0 + cell - 1, u0]
                                    and mask[v0 + cell - 1, u0 + cell - 1])

    def pos(u, v, dz=0.0):
        x = (W - u) / W * X_OUT
        y = Y_TOP - v / H * (Y_TOP - Y_BOT)
        z = surface_z(x, y, lift) + dz
        if side < 0:
            x = -x
        return (x, y, z)

    quads = []
    for (u0, v0), ok in inside.items():
        if not ok:
            continue
        u1, v1 = u0 + cell, v0 + cell
        uv4 = [uv_of(u0_cell + u0, v0), uv_of(u0_cell + u1, v0),
               uv_of(u0_cell + u1, v1), uv_of(u0_cell + u0, v1)]
        front = [pos(u0, v0), pos(u1, v0), pos(u1, v1), pos(u0, v1)]
        quads.append((front, uv4, tint, "shell"))
        if back_off:
            back = [pos(u0, v0, -back_off), pos(u1, v0, -back_off),
                    pos(u1, v1, -back_off), pos(u0, v1, -back_off)]
            quads.append((back, uv4, back_tint, "shell"))
        if rim:
            for (du, dv) in ((cell, 0), (-cell, 0), (0, cell), (0, -cell)):
                if inside.get((u0 + du, v0 + dv), False):
                    continue
                if (du, dv) == (cell, 0):
                    a, b = pos(u1, v0), pos(u1, v1)
                elif (du, dv) == (-cell, 0):
                    a, b = pos(u0, v0), pos(u0, v1)
                elif (du, dv) == (0, cell):
                    a, b = pos(u0, v1), pos(u1, v1)
                else:
                    a, b = pos(u0, v0), pos(u1, v0)
                if back_off:
                    a2 = (a[0], a[1], a[2] - back_off)
                    b2 = (b[0], b[1], b[2] - back_off)
                    quads.append(([a, b, b2, a2], None, (0.86, 0.91, 0.99), "rim"))
    return quads


def rod_quads(side):
    rods = [((8.5, 1.6), (8.95, -0.7), 0.075, 0.035),
            ((15.0, 0.2), (16.35, -2.6), 0.085, 0.040)]
    quads = []
    for a, b, r0, r1 in rods:
        za = surface_z(a[0], a[1]) + 0.32
        zb = surface_z(b[0], b[1]) + 0.32
        pa = (a[0] if side > 0 else -a[0], a[1], za)
        pb = (b[0] if side > 0 else -b[0], b[1], zb)
        quads += [(v, None, t, "rod")
                  for v, _u, t in rig.tube(pa, pb, r0, r1, sides=5, segs=3,
                                           tint=(0.20, 0.20, 0.24))]
    return quads


def bone_quads(side):
    def m(p):
        return p if side > 0 else mirror(p)

    quads = []

    def p3(p):
        return (p[0], p[1], p[2] if len(p) > 2 else 1.90)

    def mm(p):
        q = p3(p)
        return q if side > 0 else (-q[0], q[1], q[2])

    segments = [(SHOULDER, ELBOW, 0.46, 0.34), (ELBOW, WRIST, 0.34, 0.26),
                (WRIST, HAND, 0.26, 0.17)]
    segments += [(a, b, 0.16, 0.09) for a, b in FINGERS]
    for a, b, r0, r1 in segments:
        quads += [(v, None, t, "bone")
                  for v, _u, t in rig.tube(mm(a), mm(b), r0, r1, sides=8, segs=4,
                                           tint=BONE)]
    for c, r in ((SHOULDER, 0.52), (ELBOW, 0.40), (WRIST, 0.32), (HAND, 0.24)):
        quads += [(v, None, t, "bone")
                  for v, _u, t in rig.ball(mm(c), r, tint=GOLD, sides=9, rings=5)]
    return quads


def assemble(quads, side_offsets=True):
    verts, faces, uvs, cols = [], [], [], []
    white = (972.0 / AW, 672.0 / AH)
    for verts4, uv4, tint, _tag in quads:
        base = len(verts)
        for i, p in enumerate(verts4):
            side = 1 if p[0] >= 0 else -1
            x = p[0] + (side * 1.55 if side_offsets else 0.0)
            verts.append([x, p[1] + 27.0, p[2] + 2.6])
            uvs.append(uv4[i] if uv4 else white)
            cols.append(tint)
        faces.append((base, base + 1, base + 2))
        faces.append((base, base + 2, base + 3))
    return (np.array(verts, float), np.array(faces, np.int64),
            np.array(uvs, float), np.array(cols, float))


def proxy_boxes():
    pv, pf, pu, pc = [], [], [], []
    boxes = [((-4, 24, -4), (4, 32, 4), (0.34, 0.24, 0.16)),
             ((-4, 12, -2), (4, 24, 2), (0.16, 0.62, 0.66)),
             ((-4, 0, -2), (0, 12, 2), (0.20, 0.22, 0.72)),
             ((0, 0, -2), (4, 12, 2), (0.20, 0.22, 0.72)),
             ((-8, 12, -2), (-4, 24, 2), (0.74, 0.54, 0.40)),
             ((4, 12, -2), (8, 24, 2), (0.74, 0.54, 0.40))]
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
                pu.append((0.945, 0.655))
                pc.append(col)
            pf += [(base, base + 1, base + 2), (base, base + 2, base + 3)]
    return np.array(pv, float), pf, np.array(pu, float), np.array(pc, float)


def render(quads, atlas, body=True, out=1000):
    verts, faces, uvs, cols = assemble(quads)
    if body:
        pv, pf, pu, pc = proxy_boxes()
        allv = np.vstack([pv, verts])
        allf = np.array(pf + [(a + len(pv), b + len(pv), c + len(pv)) for a, b, c in faces],
                        np.int64)
        allu = np.vstack([pu, uvs])
        allc = np.vstack([pc, cols])
    else:
        allv, allf, allu, allc = verts, faces, uvs, cols
    tex = np.asarray(atlas.convert("RGBA"), float)
    rgba = rm.render_view(allv, allf, allu, tex, np.eye(3), 2200, alpha=True,
                          shade_lo=0.70, shade_hi=0.38, colors=allc)
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
    verts, faces, uvs, cols = assemble(quads)
    pv, pf, pu, pc = proxy_boxes()
    allv = np.vstack([pv, verts])
    allf = np.array(pf + [(a + len(pv), b + len(pv), c + len(pv)) for a, b, c in faces],
                    np.int64)
    allu = np.vstack([pu, uvs])
    allc = np.vstack([pc, cols])
    tex = np.asarray(atlas.convert("RGBA"), float)
    views = [("back", np.eye(3)), ("3/4", rm.rot_y(-38) @ rm.rot_x(-8)),
             ("side", rm.rot_y(90)), ("under", rm.rot_y(155) @ rm.rot_x(8))]
    sheet = Image.new("RGB", (size * 4, size + 30), (24, 26, 33))
    d = ImageDraw.Draw(sheet)
    for i, (name, R) in enumerate(views):
        img = rm.render_view(allv, allf, allu, tex, R, size, alpha=True,
                             shade_lo=0.70, shade_hi=0.38, colors=allc)
        tile = Image.new("RGB", (size, size), (24, 26, 33))
        a = Image.fromarray(img, "RGBA")
        tile.paste(a, (0, 0), a)
        sheet.paste(tile, (i * size, 30))
        d.text((i * size + 10, 10), name, fill=(220, 214, 200))
    if out is not None:
        sheet.save(out)
    return sheet


def main():
    atlas = Image.open(ATLAS).convert("RGBA")
    patch = Image.new("RGBA", (24, 24), (255, 255, 255, 255))
    atlas.paste(patch, (960, 660))
    base = Image.open(BASE_PNG).convert("RGBA")
    covert = Image.open(COVERT_PNG).convert("RGBA")
    sil = solid_mask()
    quads = []
    for side in (1, -1):
        quads += grid_quads(base, BASE_U0, side, 10, 0.0, back_off=1.0, rim=False,
                            mask=sil)
        quads += grid_quads(covert, COVERT_U0, side, 10, 0.72, back_off=0.0,
                            rim=False, tint=(0.985, 0.99, 1.0))
        quads += rod_quads(side)
    print("quads", len(quads))
    back = render(quads, atlas)
    back.save(OUT / "angel_v13_back.png")
    render(quads, atlas, body=False).save(OUT / "angel_v13_clean.png")
    view_sheet(quads, atlas, out=OUT / "angel_v13_views.png")
    ref = Image.open(OUT / "angel_ref_big.png").convert("RGB").resize((800, 800), Image.LANCZOS)
    new_img = back.resize((800, 800), Image.LANCZOS)
    sheet = Image.new("RGB", (1620, 860), (24, 26, 33))
    sheet.paste(ref, (10, 50))
    sheet.paste(new_img, (810, 50))
    d = ImageDraw.Draw(sheet)
    d.text((12, 22), "LUNAR REFERENCE", fill=(220, 214, 200))
    d.text((812, 22), "ANGEL v13 - approved v3 shape, thick mesh + reference bone rods",
           fill=(220, 214, 200))
    sheet.save(OUT / "angel_v13_compare.png")
    print("saved")


if __name__ == "__main__":
    main()
