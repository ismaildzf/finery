"""Angel wing v1 - pixel-feather angel wing with a hidden armature.

Reference: Lunar Store white angel wings (reference only; original procedural
build).  Each wing is a fan of layered pixel feather cards over a dark base,
with a thin bone rod along the leading edge.  Coordinates: player units,
feet y=0, head top y=32, +z toward the back camera.
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

AW = AH = 1024
CELLS = {
    "primary": (8, 8, 340, 640),
    "secondary": (348, 8, 660, 540),
    "covert": (668, 8, 1016, 320),
    "down": (8, 650, 340, 980),
    "bone": (348, 650, 660, 980),
    "solid": (668, 948, 688, 968),
}

S = (4.4, 24.0)
E = (6.8, 28.8)
W = (9.2, 33.0)
H = (13.0, 33.2)
ZS, ZE, ZW, ZH = 3.05, 3.30, 3.55, 3.55

PRIMARY_TIPS = [
    (18.5, 30.5), (20.6, 27.6), (21.6, 24.2), (21.6, 20.6), (20.8, 17.0),
    (19.2, 13.8), (16.8, 11.2), (14.0, 9.8), (11.0, 10.0),
]
PRIMARY_WIDTHS = [4.0, 4.1, 4.2, 4.2, 4.1, 4.0, 3.8, 3.6, 3.4]
SECONDARY_TIPS = [
    (12.6, 20.2), (10.6, 17.6), (8.8, 15.6), (7.2, 14.6), (5.8, 15.2),
    (4.8, 16.8), (4.2, 19.0), (3.9, 21.2), (3.8, 23.4),
]
SECONDARY_WIDTHS = [3.8, 3.7, 3.6, 3.5, 3.4, 3.3, 3.2, 3.1, 3.0]
MEDIAN_TIPS = [(15.0, 29.8), (16.0, 27.0), (15.8, 24.0), (14.6, 21.2),
               (12.8, 19.0), (10.4, 17.6)]

BASE_BOUNDARY = [
    (4.3, 21.8), (4.1, 19.2), (4.7, 16.5), (6.2, 14.2), (8.5, 12.0),
    (11.2, 10.6), (14.0, 10.2), (16.6, 11.0), (18.8, 12.9), (20.4, 15.7),
    (21.2, 18.9), (21.3, 22.1), (20.8, 25.2), (19.8, 27.9), (18.0, 30.2),
    (15.2, 31.8),
]

TINTS = {
    "primary": (1.0, 1.0, 1.02),
    "secondary": (0.96, 0.97, 1.0),
    "median": (0.98, 0.99, 1.0),
    "covert": (1.0, 1.0, 1.0),
    "puff": (0.97, 0.98, 1.0),
    "back": (0.58, 0.60, 0.70),
}
WHITE = (1.0, 1.0, 1.0)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def uv(name, u, v):
    x0, y0, x1, y1 = CELLS[name]
    pad = 2
    return (x0 + pad + u * (x1 - x0 - 2 * pad),
            y0 + pad + v * (y1 - y0 - 2 * pad))


# ------------------------------------------------------------------ textures

def pixel_feather(pw, ph, variant):
    im = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    px = im.load()
    for y in range(2, ph - 2):
        t = (y - 2) / max(1, ph - 4)
        if variant == "covert":
            half = 2 + (pw * 0.47 - 2) * math.sin(math.pi * min(1.0, t * 1.06)) ** 0.45
        elif variant == "secondary":
            half = 2 + (pw * 0.46 - 2) * (0.30 + 0.70 * math.sin(math.pi * t) ** 0.55)
        else:
            half = 2 + (pw * 0.45 - 2) * (0.38 + 0.62 * math.sin(math.pi * t) ** 0.55)
        if t > 0.86:
            half *= 1.0 - 0.45 * (t - 0.86) / 0.14
        half = max(2, int(half))
        cx = pw // 2
        for x in range(cx - half, cx + half + 1):
            d = abs(x - cx) / max(1, half)
            if d > 0.94:
                col = (176, 184, 201)
            elif x < cx:
                col = (233, 238, 247)
            else:
                col = (247, 249, 253)
            if (x * 3 + y) % 9 == 0:
                col = (214, 221, 234)
            if x == cx:
                col = (253, 254, 255)
            px[x, y] = (col[0], col[1], col[2], 255)
    # stepped tip notch
    cx = pw // 2
    for k, y in enumerate(range(ph - 8, ph - 2)):
        for x in range(cx - 3 + k, cx + 4 - k):
            if 0 <= x < pw:
                px[x, y] = (0, 0, 0, 0)
    # dark root band (shadow under the layer above)
    for y in range(0, 2):
        for x in range(pw):
            if px[x, y][3]:
                px[x, y] = (188, 196, 213, 255)
    return im


def make_down(w, h):
    rng = np.random.default_rng(17)
    arr = np.zeros((h, w, 3), np.float32)
    arr[:] = (206, 210, 222)
    arr += rng.normal(0, 5.0, (h, w, 1))
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(22):
        x = rng.uniform(0, w)
        y = rng.uniform(0, h)
        r = rng.uniform(12, 36)
        d.ellipse([x - r, y - r * 0.6, x + r, y + r * 0.6],
                  fill=(235, 238, 246, 20), outline=(180, 187, 202, 24), width=1)
    return img.filter(ImageFilter.GaussianBlur(1.2))


def make_bone(w, h):
    rng = np.random.default_rng(9)
    xx = np.linspace(-1, 1, w, dtype=np.float32)[None, :]
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    ridge = np.clip(1 - np.abs(xx) ** 1.7, 0, 1)
    lum = np.broadcast_to(48 + 96 * ridge, (h, w)).copy()
    lum += 8 * np.sin(yy * 44.0) * ridge
    lum = np.clip(lum, 0, 255)
    rgb = np.stack([lum, lum * 0.99, lum * 0.97], -1)
    return Image.fromarray(rgb.astype(np.uint8), "RGB")


def build_atlas():
    ART.mkdir(parents=True, exist_ok=True)
    atlas = Image.new("RGBA", (AW, AH), (0, 0, 0, 0))
    parts = {
        "primary": pixel_feather(32, 72, "primary"),
        "secondary": pixel_feather(32, 56, "secondary"),
        "covert": pixel_feather(40, 34, "covert"),
        "down": make_down(308, 308),
        "bone": make_bone(308, 436),
    }
    for name, (x0, y0, x1, y1) in CELLS.items():
        if name == "solid":
            ImageDraw.Draw(atlas).rectangle([x0, y0, x1 - 1, y1 - 1],
                                            fill=(96, 100, 110, 255))
            continue
        im = parts[name].convert("RGBA")
        if name in ("primary", "secondary", "covert"):
            im = im.resize((x1 - x0, y1 - y0), Image.NEAREST)
        else:
            im = im.resize((x1 - x0, y1 - y0), Image.LANCZOS)
        atlas.alpha_composite(im, (x0, y0))
    atlas.save(ART / "angel_atlas.png")
    atlas.resize((512, 512), Image.LANCZOS).save(ART / "angel_atlas_view.png")
    return atlas


# ------------------------------------------------------------------ cards

def _add_quad(quads, pts, uvs, tint, front=True):
    (x0, y0, _), (x1, y1, _), (x2, y2, _) = pts[0], pts[1], pts[2]
    nz = (x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0)
    if (front and nz < 0) or (not front and nz > 0):
        pts = pts[::-1]
        uvs = uvs[::-1]
    quads.append((pts, uvs, tint))


def card_quads(root, tip, width, cell, tint, curve=0.10, offset=0.0, segs=3):
    quads = []
    rx, ry, rz = root
    tx, ty, tz = tip
    dx, dy = tx - rx, ty - ry
    ln = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / ln, dx / ln
    cx = (rx + tx) * 0.5 + nx * curve * ln
    cy = (ry + ty) * 0.5 + ny * curve * ln
    half = width * 0.5
    rows = []
    for i in range(segs + 1):
        t = i / segs
        x = (1 - t) ** 2 * rx + 2 * t * (1 - t) * cx + t * t * tx
        y = (1 - t) ** 2 * ry + 2 * t * (1 - t) * cy + t * t * ty
        dxp = 2 * (1 - t) * (cx - rx) + 2 * t * (tx - cx)
        dyp = 2 * (1 - t) * (cy - ry) + 2 * t * (ty - cy)
        l2 = math.hypot(dxp, dyp) or 1.0
        px, py = -dyp / l2, dxp / l2
        z = rz + (tz - rz) * t + offset
        rows.append((x, y, z, px, py, t))
    for i in range(segs):
        a, b = rows[i], rows[i + 1]
        A = (a[0] - a[3] * half, a[1] - a[4] * half, a[2])
        B = (a[0] + a[3] * half, a[1] + a[4] * half, a[2])
        C = (b[0] + b[3] * half, b[1] + b[4] * half, b[2])
        D = (b[0] - b[3] * half, b[1] - b[4] * half, b[2])
        v0, v1 = a[5] * 0.98 + 0.01, b[5] * 0.98 + 0.01
        uvs = [uv(cell, 0.01, v0), uv(cell, 0.99, v0),
               uv(cell, 0.99, v1), uv(cell, 0.01, v1)]
        _add_quad(quads, [A, B, C, D], uvs, tint, front=True)
        A2 = (A[0], A[1], A[2] - 0.06)
        B2 = (B[0], B[1], B[2] - 0.06)
        C2 = (C[0], C[1], C[2] - 0.06)
        D2 = (D[0], D[1], D[2] - 0.06)
        _add_quad(quads, [A2, B2, C2, D2], uvs, TINTS["back"], front=False)
    return quads


# ------------------------------------------------------------------ armature

def resample3(path, n):
    pts = []
    for i in range(len(path) - 1):
        a, b = path[i], path[i + 1]
        for k in range(n):
            if i and k == 0:
                continue
            f = k / n
            pts.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f,
                        a[2] + (b[2] - a[2]) * f))
    pts.append(path[-1])
    return pts


def tube(path, r0, r1, tex, tint, sides=6, n=10, bulge=(), bulge_amt=0.25):
    pts = resample3(path, n)
    rings = []
    for i, p in enumerate(pts):
        t = i / (len(pts) - 1)
        a = pts[max(0, i - 1)]
        b = pts[min(len(pts) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / ln, dx / ln
        r = r0 + (r1 - r0) * t
        for bt in bulge:
            r *= 1 + bulge_amt * math.exp(-((t - bt) / 0.05) ** 2)
        ring = []
        for k in range(sides):
            th = 2 * math.pi * k / sides
            ring.append((p[0] + nx * r * math.cos(th),
                         p[1] + ny * r * math.cos(th),
                         p[2] + r * math.sin(th)))
        rings.append((ring, t))
    quads = []
    for i in range(len(rings) - 1):
        ra, ta = rings[i]
        rb, tb = rings[i + 1]
        for k in range(sides):
            k2 = (k + 1) % sides
            quads.append(([ra[k], ra[k2], rb[k2], rb[k]],
                          [uv(tex, k / sides, ta), uv(tex, (k + 1) / sides, ta),
                           uv(tex, (k + 1) / sides, tb), uv(tex, k / sides, tb)], tint))
    return quads


def armature_quads():
    quads = []
    arm = [(S[0], S[1], ZS), (E[0], E[1], ZE), (W[0], W[1], ZW), (H[0], H[1], ZH)]
    quads += tube(arm, 0.34, 0.20, "bone", (0.44, 0.45, 0.50), sides=5, n=12,
                  bulge=(0.30, 0.65, 0.95), bulge_amt=0.3)
    quads += tube([(W[0] - 0.35, W[1] - 0.12, ZW), (W[0] + 0.35, W[1] + 0.12, ZW)],
                  0.45, 0.40, "bone", (0.62, 0.63, 0.68), sides=5, n=4)
    return quads


def wing_base_quads():
    quads = []
    for i in range(len(BASE_BOUNDARY) - 1):
        a = BASE_BOUNDARY[i]
        b = BASE_BOUNDARY[i + 1]
        m0 = (W[0] + (a[0] - W[0]) * 0.55, W[1] + (a[1] - W[1]) * 0.55)
        m1 = (W[0] + (b[0] - W[0]) * 0.55, W[1] + (b[1] - W[1]) * 0.55)
        p0 = (W[0] + (a[0] - W[0]) * 0.12, W[1] + (a[1] - W[1]) * 0.12)
        p1 = (W[0] + (b[0] - W[0]) * 0.12, W[1] + (b[1] - W[1]) * 0.12)
        u0 = i / (len(BASE_BOUNDARY) - 1)
        u1 = (i + 1) / (len(BASE_BOUNDARY) - 1)
        quads.append(([(p0[0], p0[1], 2.02), (p1[0], p1[1], 2.02),
                       (m1[0], m1[1], 1.98), (m0[0], m0[1], 1.98)],
                      [uv("down", u0, 0.1), uv("down", u1, 0.1),
                       uv("down", u1, 0.5), uv("down", u0, 0.5)],
                      (0.86, 0.88, 0.95)))
        quads.append(([(m0[0], m0[1], 1.98), (m1[0], m1[1], 1.98),
                       (b[0], b[1], 2.02), (a[0], a[1], 2.02)],
                      [uv("down", u0, 0.5), uv("down", u1, 0.5),
                       uv("down", u1, 0.95), uv("down", u0, 0.95)],
                      (0.80, 0.82, 0.90)))
    return quads


def wing_quads():
    quads = wing_base_quads()
    for i, (tip, w) in enumerate(zip(PRIMARY_TIPS, PRIMARY_WIDTHS)):
        t = i / (len(PRIMARY_TIPS) - 1)
        root = lerp(W, H, min(1.0, t * 1.15))
        quads += card_quads((root[0], root[1] - 0.2, ZH - 0.05),
                            (tip[0], tip[1], 2.62), w, "primary",
                            TINTS["primary"], curve=0.08 + 0.02 * i,
                            offset=0.20 - 0.015 * i)
    for i, (tip, w) in enumerate(zip(SECONDARY_TIPS, SECONDARY_WIDTHS)):
        t = i / (len(SECONDARY_TIPS) - 1)
        root = lerp(E, W, t)
        quads += card_quads((root[0] + 0.1, root[1] + 0.15, ZE + (ZW - ZE) * t),
                            (tip[0], tip[1], 2.78), w, "secondary",
                            TINTS["secondary"], curve=-0.07 - 0.015 * i,
                            offset=0.06)
    for i, tip in enumerate(MEDIAN_TIPS):
        t = i / (len(MEDIAN_TIPS) - 1)
        root = lerp(E, W, 0.15 + 0.7 * t)
        quads += card_quads((root[0] + 0.15, root[1] + 0.1, ZE + (ZW - ZE) * t),
                            (tip[0], tip[1], 2.95), 3.4, "secondary",
                            TINTS["median"], curve=0.04, offset=0.12)
    n_cov = 8
    for i in range(n_cov):
        t = 0.03 + 0.94 * i / (n_cov - 1)
        root = lerp(S, W, t)
        zr = ZS + (ZW - ZS) * t
        end = (root[0] + 3.4 + 1.1 * math.sin(i * 0.8),
               root[1] + 1.9 - 0.6 * i, zr)
        quads += card_quads((root[0], root[1], zr + 0.28), end, 3.1, "covert",
                            TINTS["covert"], curve=0.12, offset=0.36)
    for i in range(6):
        t = 0.08 + 0.8 * i / 5
        root = lerp(S, W, t)
        zr = ZS + (ZW - ZS) * t
        end = (root[0] + 2.2, root[1] + 1.1, zr)
        quads += card_quads((root[0], root[1], zr + 0.42), end, 2.7, "covert",
                            TINTS["puff"], curve=0.08, offset=0.22)
    for i, (dx, dy, ln, w) in enumerate(((-0.2, 0.2, 3.2, 3.6), (0.5, 0.9, 3.6, 3.5),
                                        (1.1, 1.7, 3.1, 3.3), (0.3, 2.4, 2.6, 3.0))):
        root = (S[0] + dx, S[1] + dy, ZS + 0.45 + 0.04 * i)
        end = (root[0] + ln * 0.7, root[1] + ln * 0.62, ZS + 0.58)
        quads += card_quads(root, end, w, "covert", TINTS["puff"],
                            curve=0.05, offset=0.12)
    for i in range(3):
        root = (S[0] + 0.3 + i * 0.45, S[1] + 2.6 - i * 0.3, ZS + 0.32)
        end = (root[0] + 2.2, root[1] + 1.3, ZS + 0.46)
        quads += card_quads(root, end, 2.6, "covert", TINTS["covert"],
                            curve=-0.05, offset=0.06)
    return quads


def build_model():
    quads = []
    for side in (1, -1):
        for verts, uvs, tint in (wing_quads() + armature_quads()):
            quads.append(([(side * x, y, z) for x, y, z in verts], uvs, tint))
    return quads


# ------------------------------------------------------------------ render

def to_arrays(quads):
    verts, uvs, faces, cols = [], [], [], []
    for q in quads:
        verts4, uv4, tint = q[0], q[1], q[2]
        base = len(verts)
        for (x, y, z), (u, v) in zip(verts4, uv4):
            verts.append([x, y, z])
            uvs.append([u / AW, v / AH])
            cols.append([min(1.12, c) for c in tint])
        faces.append((base, base + 1, base + 2))
        faces.append((base, base + 2, base + 3))
    return (np.array(verts, float), np.array(faces, np.int64),
            np.array(uvs, float), np.array(cols, float))


def proxy_boxes(root_z=2.6):
    skin_uv = ((CELLS["solid"][0] + 8) / AW, (CELLS["solid"][1] + 8) / AH)
    boxes = [((-4, 24, -4), (4, 32, 4)), ((-4, 12, -2), (4, 24, 2)),
             ((-4, 0, -2), (0, 12, 2)), ((0, 0, -2), (4, 12, 2)),
             ((-8, 12, -2), (-4, 24, 2)), ((4, 12, -2), (8, 24, 2))]
    colors = [(0.34, 0.24, 0.16), (0.16, 0.62, 0.66), (0.20, 0.22, 0.72),
              (0.20, 0.22, 0.72), (0.74, 0.54, 0.40), (0.74, 0.54, 0.40)]
    pv, pf, pu, pc = [], [], [], []
    for (frm, to), col in zip(boxes, colors):
        corners = [(frm[0], frm[1], frm[2]), (to[0], frm[1], frm[2]),
                   (to[0], to[1], frm[2]), (frm[0], to[1], frm[2]),
                   (frm[0], frm[1], to[2]), (to[0], frm[1], to[2]),
                   (to[0], to[1], to[2]), (frm[0], to[1], to[2])]
        for q in ((0, 1, 2, 3), (5, 4, 7, 6), (4, 5, 1, 0),
                  (2, 3, 7, 6), (4, 0, 3, 7), (1, 5, 6, 2)):
            base = len(pv)
            for idx in q:
                x, y, z = corners[idx]
                pv.append([x, y, z + root_z - 2.0])
                pu.append(skin_uv)
                pc.append(col)
            pf += [(base, base + 1, base + 2), (base, base + 2, base + 3)]
    return np.array(pv, float), pf, np.array(pu, float), np.array(pc, float)


def render_single(atlas, quads, size=900, with_body=True):
    tex = np.asarray(atlas.convert("RGBA"), float)
    v, f, u, c = to_arrays(quads)
    if with_body:
        pv, pf, pu, pc = proxy_boxes()
        allv = np.vstack([pv, v])
        allf = np.array(pf + [(a + len(pv), b + len(pv), c2 + len(pv)) for a, b, c2 in f],
                        np.int64)
        allu = np.vstack([pu, u])
        allc = np.vstack([pc, c])
    else:
        allv, allf, allu, allc = v, f, u, c
    rgba = rm.render_view(allv, allf, allu, tex, np.eye(3), size, alpha=True,
                          shade_lo=0.94, shade_hi=0.55, colors=allc)
    bg = np.zeros((size, size, 3), np.float64)
    yy = np.linspace(0, 1, size)[:, None, None]
    bg[:] = np.array([196, 200, 232]) * (1 - yy) + np.array([118, 122, 168]) * yy
    base = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    base.alpha_composite(Image.fromarray(rgba, "RGBA"))
    return base.convert("RGB")


def render_sheet(atlas, quads, path, with_body=True, size=780):
    tex = np.asarray(atlas.convert("RGBA"), float)
    v, f, u, c = to_arrays(quads)
    if with_body:
        pv, pf, pu, pc = proxy_boxes()
        allv = np.vstack([pv, v])
        allf = np.array(pf + [(a + len(pv), b + len(pv), c2 + len(pv)) for a, b, c2 in f],
                        np.int64)
        allu = np.vstack([pu, u])
        allc = np.vstack([pc, c])
    else:
        allv, allf, allu, allc = v, f, u, c
    views = [("back", np.eye(3)), ("3/4 back", rm.rot_y(-28) @ rm.rot_x(-6)),
             ("side", rm.rot_y(-76)), ("back low", rm.rot_x(10))]
    sheet = Image.new("RGB", (size * 2, (size + 26) * 2), (28, 30, 38))
    d = ImageDraw.Draw(sheet)
    bg = np.zeros((size, size, 3), np.float64)
    yy = np.linspace(0, 1, size)[:, None, None]
    bg[:] = np.array([196, 200, 232]) * (1 - yy) + np.array([118, 122, 168]) * yy
    for i, (label, R) in enumerate(views):
        rgba = rm.render_view(allv, allf, allu, tex, R, size, alpha=True,
                              shade_lo=0.94, shade_hi=0.55, colors=allc)
        base = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
        base.alpha_composite(Image.fromarray(rgba, "RGBA"))
        x, y = (i % 2) * size, (i // 2) * (size + 26)
        sheet.paste(base.convert("RGB"), (x, y + 26))
        d.text((x + 10, y + 7), f"Angel wing v2 - {label}", fill=(230, 226, 214))
    sheet.save(path)
    return sheet


def render_compare(atlas, quads):
    ref = Image.open(OUT / "angel_ref_big.png").convert("RGB")
    new = render_single(atlas, quads, size=1000, with_body=True)
    h = 780
    pad = 14
    ref_img = ref.resize((int(ref.width * h / ref.height), h), Image.LANCZOS)
    new_img = new.resize((int(new.width * h / new.height), h), Image.LANCZOS)
    sheet = Image.new("RGB", (ref_img.width + new_img.width + pad * 3, h + 70),
                      (24, 26, 33))
    sheet.paste(ref_img, (pad, 52))
    sheet.paste(new_img, (pad * 2 + ref_img.width, 52))
    d = ImageDraw.Draw(sheet)
    d.text((pad + 2, 22), "LUNAR REFERENCE - white angel wings", fill=(220, 214, 200))
    d.text((pad * 2 + ref_img.width + 2, 22), "NEW - pixel-feather angel (back view)",
           fill=(220, 214, 200))
    sheet.save(OUT / "angel_v2_compare.png")
    return sheet


def main():
    OUT.mkdir(exist_ok=True)
    atlas = build_atlas()
    quads = build_model()
    print("quads", len(quads))
    render_sheet(atlas, quads, OUT / "angel_v2_preview.png", with_body=True)
    render_sheet(atlas, quads, OUT / "angel_v2_clean.png", with_body=False)
    render_compare(atlas, quads)
    print("saved", OUT / "angel_v2_preview.png")


if __name__ == "__main__":
    main()
