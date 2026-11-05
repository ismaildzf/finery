"""Angel wing v7 - curved 3D feather shell + relief feathers + armature.

The approved 2D art (angel_v3_wing.png) is mapped onto a genuinely curved,
thick shell (front surface + underside + rim), so the feather detail survives
while the wing gains volume. Relief feathers break the silhouette and add
layered depth on the covert cap; the humerus/radius/hand armature sits inside.
"""
import math
import pathlib
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parents[1]
ART = ROOT / "art-wings" / "angel"
OUT = ROOT / "_design"
sys.path.insert(0, str(ROOT / "tools"))
import render_mesh as rm  # noqa: E402
import angelrig_v3 as rig  # noqa: E402

WING_ART = ART / "angel_v3_wing.png"
ATLAS = ART / "angel_v3_atlas.png"
X_OUT = 23.35
Y_TOP, Y_BOT = 11.6, -19.6
X_SHIFT = 2.0
X_SCALE = (X_OUT - X_SHIFT) / X_OUT
ATLAS_SIZE = 1024.0
WING_U0, WING_V0 = 8.0, 8.0
WHITE_UV = (972.0 / ATLAS_SIZE, 672.0 / ATLAS_SIZE)

SHOULDER = (0.8, -4.0, 0.10)
ELBOW = (3.0, -0.6, 0.14)
WRIST = (5.6, 2.6, 0.18)
HAND = (8.2, 5.4, 0.22)
JOINTS = [("shoulder", SHOULDER, 0.30), ("elbow", ELBOW, 0.22),
          ("wrist", WRIST, 0.17), ("hand", HAND, 0.11)]

BONE = (0.93, 0.90, 0.82)
GOLD = (0.94, 0.74, 0.34)


def mirror(p):
    return (-p[0], p[1], p[2])


def fill_holes(mask):
    """True outside the silhouette, then invert; fills interior transparent gaps."""
    from collections import deque
    h, w = mask.shape
    outside = np.zeros((h, w), bool)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if not mask[y, x] and not outside[y, x]:
                outside[y, x] = True
                q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if not mask[y, x] and not outside[y, x]:
                outside[y, x] = True
                q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and not mask[ny, nx] and not outside[ny, nx]:
                outside[ny, nx] = True
                q.append((ny, nx))
    return ~outside


OUTLINE_OUTER = [(7.0, 11.6), (7.6, 11.2), (10.8, 9.61), (13.54, 7.63),
                 (16.34, 5.64), (18.26, 3.65), (20.13, 1.66), (20.87, -0.32),
                 (22.0, -2.31), (22.84, -4.3), (23.35, -6.29), (23.35, -8.27),
                 (22.9, -10.6)]
OUTLINE_BOTTOM = [(22.3, -13.1), (21.4, -15.9), (20.45, -18.5), (17.5, -19.2),
                  (14.62, -19.25), (12.4, -18.4), (10.51, -17.2), (9.0, -15.9),
                  (7.85, -14.3), (6.6, -12.9), (5.46, -11.4), (4.7, -9.7),
                  (4.02, -7.97)]
OUTLINE_INNER = [(4.1, -6.3), (4.4, -5.3), (4.1, -3.3), (3.1, -2.3),
                 (2.8, 0.7), (1.7, 1.7), (1.4, 2.7), (1.1, 3.6),
                 (0.2, 4.6), (0.4, 5.6), (1.7, 6.6), (3.6, 7.6),
                 (4.4, 8.6), (4.7, 9.6), (5.0, 10.6), (6.3, 11.6)]


def art_uv(x, y):
    return (500.0 - x / X_OUT * 500.0, (Y_TOP - y) / (Y_TOP - Y_BOT) * 628.0)


def outline_mask():
    pts = OUTLINE_OUTER + OUTLINE_BOTTOM + OUTLINE_INNER
    img = Image.new("L", (500, 628), 0)
    d = ImageDraw.Draw(img)
    poly = [art_uv(x, y) for x, y in pts]
    d.polygon(poly, fill=255)
    return np.asarray(img) > 127


def prepare_texture():
    art = Image.open(WING_ART).convert("RGBA")
    rgba = np.asarray(art, float)
    alpha = rgba[:, :, 3] / 255.0
    sil = outline_mask()
    base = np.array([214.0, 228.0, 246.0])
    rgb = rgba[:, :, :3] * alpha[:, :, None] + base * (1 - alpha[:, :, None])
    out = np.zeros((rgba.shape[0], rgba.shape[1], 4), np.uint8)
    out[:, :, :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    out[:, :, 3] = np.where(sil, 255, 0).astype(np.uint8)
    atlas = Image.open(ATLAS).convert("RGBA")
    atlas.paste(Image.fromarray(out, "RGBA"), (int(WING_U0), int(WING_V0)))
    patch = Image.new("RGBA", (24, 24), (255, 255, 255, 255))
    atlas.paste(patch, (960, 660))
    return atlas, sil


def warp_x(x):
    return X_SHIFT + x * X_SCALE


def shell_pos(u, v, side, dz=0.0):
    xn = min(max((500 - u) / 500.0, 0.0), 1.0)
    yn = min(max(1.0 - v / 628.0, 0.0), 1.0)
    x = warp_x(xn * X_OUT)
    y = Y_BOT + yn * (Y_TOP - Y_BOT)
    z = 0.18 + 0.38 * math.sin(math.pi * xn * 0.85) + 0.34 * yn + 0.46 * xn * xn
    z += dz
    if side < 0:
        x = -x
    return (x, y, z)


def uv_of(u, v):
    return ((WING_U0 + u) / ATLAS_SIZE, (WING_V0 + v) / ATLAS_SIZE)


def shell_quads(side, mask, cell=10):
    H, W = mask.shape
    quads = []
    inside = {}
    for v0 in range(0, H - cell + 1, cell):
        for u0 in range(0, W - cell + 1, cell):
            ok = bool(mask[v0, u0] and mask[v0, u0 + cell - 1]
                      and mask[v0 + cell - 1, u0] and mask[v0 + cell - 1, u0 + cell - 1])
            inside[(u0, v0)] = ok
    for (u0, v0), ok in inside.items():
        if not ok:
            continue
        u1, v1 = u0 + cell, v0 + cell
        uv4 = [uv_of(u0, v0), uv_of(u1, v0), uv_of(u1, v1), uv_of(u0, v1)]
        front = [shell_pos(u0, v0, side), shell_pos(u1, v0, side),
                 shell_pos(u1, v1, side), shell_pos(u0, v1, side)]
        quads.append((front, uv4, (1.0, 1.0, 1.0), "shell"))
        back = [shell_pos(u0, v0, side, -0.55), shell_pos(u1, v0, side, -0.55),
                shell_pos(u1, v1, side, -0.55), shell_pos(u0, v1, side, -0.55)]
        quads.append((back, uv4, (0.55, 0.62, 0.78), "shell"))
        # rim along missing neighbours
        for (du, dv) in ((cell, 0), (-cell, 0), (0, cell), (0, -cell)):
            if inside.get((u0 + du, v0 + dv), False):
                continue
            if (du, dv) == (cell, 0):
                edge = [uv_of(u1, v0), uv_of(u1, v1)]
                fe = [shell_pos(u1, v0, side), shell_pos(u1, v1, side)]
            elif (du, dv) == (-cell, 0):
                edge = [uv_of(u0, v0), uv_of(u0, v1)]
                fe = [shell_pos(u0, v0, side), shell_pos(u0, v1, side)]
            elif (du, dv) == (0, cell):
                edge = [uv_of(u0, v1), uv_of(u1, v1)]
                fe = [shell_pos(u0, v1, side), shell_pos(u1, v1, side)]
            else:
                edge = [uv_of(u0, v0), uv_of(u1, v0)]
                fe = [shell_pos(u0, v0, side), shell_pos(u1, v0, side)]
            a, b = fe
            a2 = (a[0], a[1], a[2] - 0.55)
            b2 = (b[0], b[1], b[2] - 0.55)
            quads.append(([a, b, b2, a2], [edge[0], edge[1], edge[1], edge[0]],
                          (0.72, 0.77, 0.90), "shell"))
    return quads


# ── relief feathers (sit proud of the shell) ─────────────────────────────
def relief_feathers(side):
    quads = []

    def add_feather(root_uv, tip_uv, width, lift, tint, rounded=False, bow=0.2):
        r = shell_pos(root_uv[0], root_uv[1], side)
        t = shell_pos(tip_uv[0], tip_uv[1], side)
        z0 = r[2] + lift
        z1 = t[2] + lift * 0.55
        r = (r[0], r[1], z0)
        t = (t[0], t[1], z1)
        if side < 0:
            bow = -bow
        q = rig.feather(r, t, width, bow=bow, z0=z0, z1=z1, zbulge=0.10,
                        thick=0.09, rounded=rounded, segs=3, tint=tint)
        for verts, _uv, tnt in q:
            quads.append((verts, None, tnt, "feather"))

    # bottom tips: extend the art's feather points a little past the shell
    bottom = [(22.3, -13.1), (21.4, -15.9), (20.45, -18.5), (17.5, -19.2),
              (14.62, -19.25), (12.4, -18.4), (10.51, -17.2), (9.0, -15.9),
              (7.85, -14.3), (6.6, -12.9), (5.46, -11.4), (4.7, -9.7),
              (4.02, -7.97)]
    for i, (x, y) in enumerate(bottom):
        u = 500 - x / X_OUT * 500
        v = (Y_TOP - y) / (Y_TOP - Y_BOT) * 628
        drop = 0.7 + 0.4 * math.sin(i * 1.1)
        tip_v = min(627, v + drop / (Y_TOP - Y_BOT) * 628)
        root_v = max(0, v - (2.6 + 0.4 * math.sin(i * 0.7)) / (Y_TOP - Y_BOT) * 628)
        add_feather((min(499, u + 10), root_v), (min(499, u - 4), tip_v),
                    1.35 + 0.25 * math.sin(i * 0.9), 0.16 + 0.008 * i,
                    0.985 - 0.005 * i, rounded=False, bow=-0.18)

    # outer / leading edge tufts
    outer = [(23.35, -8.3), (22.0, -2.3), (20.1, 1.7), (18.3, 3.7),
             (16.3, 5.6), (13.5, 7.6), (10.8, 9.6)]
    for i, (x, y) in enumerate(outer):
        u = 500 - x / X_OUT * 500
        v = (Y_TOP - y) / (Y_TOP - Y_BOT) * 628
        root_v = min(627, v + 60)
        add_feather((min(499, u + 6), root_v), (max(0, u - 12), max(0, v - 16)),
                    1.30, 0.16 + 0.010 * i, 0.975 - 0.005 * i,
                    rounded=False, bow=0.18)

    # covert cap relief rows
    cap = [
        ((470, 100), (435, 70), (400, 135), (365, 105), (330, 150)),
        ((480, 190), (445, 155), (410, 215), (375, 180), (340, 230), (305, 200)),
        ((485, 280), (450, 245), (415, 300), (380, 265), (345, 315), (310, 290)),
    ]
    for ri, row in enumerate(cap):
        for i, (u, v) in enumerate(row):
            add_feather((u, v + 55), (u - 22, v - 42), 1.55,
                        0.14 + 0.008 * i, 0.985 - 0.012 * ri + 0.007 * (i % 2),
                        rounded=True, bow=0.08)
    return quads


def bone_quads(side):
    def m(p):
        q = (warp_x(p[0]), p[1], p[2])
        return q if side > 0 else mirror(q)

    out = []
    for a, b, r0, r1, tag in ((SHOULDER, ELBOW, 0.30, 0.22, "humerus"),
                              (ELBOW, WRIST, 0.22, 0.16, "radius"),
                              (WRIST, HAND, 0.15, 0.08, "hand")):
        out += [(v, None, t, tag) for v, _u, t in rig.tube(m(a), m(b), r0, r1, segs=3)]
    for name, c, r in JOINTS:
        tag = "root" if name == "shoulder" else (
            "humerus" if name == "elbow" else ("radius" if name == "wrist" else "hand"))
        out += [(v, None, t, tag) for v, _u, t in rig.ball(m(c), r)]
    return out


# ── rendering ────────────────────────────────────────────────────────────
def uv_for(q):
    uv = q[1]
    if uv is None:
        return [WHITE_UV] * 4, (0.5, 0.5)
    if isinstance(uv[0], tuple):
        return uv, uv[0]
    return [uv] * 4, uv


def world_quads(quads):
    out = []
    for verts4, uv, tint, *rest in quads:
        side = 1 if float(np.mean([p[0] for p in verts4])) >= 0 else -1
        w4 = [(p[0] + side * 1.55, p[1] + 27.0, p[2] + 2.6) for p in verts4]
        out.append((w4, uv, tint, *rest))
    return out


def to_arrays(quads):
    verts, faces, cols, uvs = [], [], [], []
    for q in quads:
        base = len(verts)
        uv4, _center = uv_for(q)
        for p, uv in zip(q[0], uv4):
            verts.append([p[0], p[1], p[2]])
            uvs.append(uv)
            cols.append(q[2])
        faces.append((base, base + 1, base + 2))
        faces.append((base, base + 2, base + 3))
    return (np.array(verts, float), np.array(faces, np.int64),
            np.array(uvs, float), np.array(cols, float))


def setup(quads, body=True, atlas=None):
    quads = world_quads(quads)
    verts, faces, uv, cols = to_arrays(quads)
    if atlas is None:
        atlas, _ = prepare_texture()
    tex = np.asarray(atlas.convert("RGBA"), float)
    if body:
        pv, pf, pc = rig.proxy_boxes()
        allv = np.vstack([pv, verts])
        allf = np.array(pf + [(a + len(pv), b + len(pv), c + len(pv)) for a, b, c in faces],
                        np.int64)
        allu = np.vstack([np.full((len(pv), 2), WHITE_UV), uv])
        allc = np.vstack([pc, cols])
    else:
        allv, allf, allu, allc = verts, faces, uv, cols
    return allv, allf, allu, allc, tex


def render(quads, body=True, out=1000, atlas=None):
    allv, allf, allu, allc, tex = setup(quads, body, atlas)
    rgba = rm.render_view(allv, allf, allu, tex, np.eye(3), 2200, alpha=True,
                          shade_lo=0.70, shade_hi=0.36, colors=allc)
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


def view_sheet(quads, size=620, out=None, atlas=None):
    allv, allf, allu, allc, tex = setup(quads, True, atlas)
    views = [("back", np.eye(3)),
             ("3/4", rm.rot_y(-38) @ rm.rot_x(-8)),
             ("side", rm.rot_y(90)),
             ("under 3/4", rm.rot_y(150) @ rm.rot_x(10))]
    sheet = Image.new("RGB", (size * 4, size + 30), (24, 26, 33))
    d = ImageDraw.Draw(sheet)
    for i, (name, R) in enumerate(views):
        img = rm.render_view(allv, allf, allu, tex, R, size, alpha=True,
                             shade_lo=0.70, shade_hi=0.36, colors=allc)
        tile = Image.new("RGB", (size, size), (24, 26, 33))
        a = Image.fromarray(img, "RGBA")
        tile.paste(a, (0, 0), a)
        sheet.paste(tile, (i * size, 30))
        d.text((i * size + 10, 10), name, fill=(220, 214, 200))
    if out is not None:
        sheet.save(out)
    return sheet


def main():
    atlas, sil = prepare_texture()
    shell = shell_quads(1, sil) + shell_quads(-1, sil)
    relief = relief_feathers(1) + relief_feathers(-1)
    bones = bone_quads(1) + bone_quads(-1)
    quads = shell + relief + bones
    print("quads", len(quads), "shell", len(shell), "relief", len(relief))
    back = render(quads, body=True, atlas=atlas)
    back.save(OUT / "angel_v8_back.png")
    render(quads, body=False, atlas=atlas).save(OUT / "angel_v8_clean.png")
    view_sheet(quads, out=OUT / "angel_v8_views.png", atlas=atlas)
    view_sheet(bones + shell_quads(1, sil, 24) + shell_quads(-1, sil, 24),
               out=OUT / "angel_v8_armature.png", atlas=atlas)
    ref = Image.open(OUT / "angel_ref_big.png").convert("RGB").resize((800, 800), Image.LANCZOS)
    new_img = back.resize((800, 800), Image.LANCZOS)
    sheet = Image.new("RGB", (1620, 860), (24, 26, 33))
    sheet.paste(ref, (10, 50))
    sheet.paste(new_img, (810, 50))
    d = ImageDraw.Draw(sheet)
    d.text((12, 22), "LUNAR REFERENCE", fill=(220, 214, 200))
    d.text((812, 22), "ANGEL v8 - solid 3D shell + relief feathers + armature",
           fill=(220, 214, 200))
    sheet.save(OUT / "angel_v8_compare.png")
    print("saved")


if __name__ == "__main__":
    main()
