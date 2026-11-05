"""Angel wing v2 - pixel-art layered wing clone (reference style).

Reference: Lunar Store white angel wings (reference only; original procedural
texture).  The wing is a pixel-art texture (shingled feather rows, armature rod,
shoulder puff) mapped onto a gently curved plane with a darker back layer.
Coordinates: player units, feet y=0, head top y=32, +z toward the back camera.
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

T = 512          # texture working resolution
X0, X1 = 3.0, 24.8
Y0, Y1 = 7.6, 36.0
Z_BASE = 3.10

WHITE = (246, 248, 252)
WHITE_HI = (253, 254, 255)
BLUE = (214, 221, 234)
BLUE_D = (186, 195, 212)
EDGE = (168, 177, 194)
SHADOW = (150, 159, 176)
ROOT_SH = (196, 203, 218)
ROD = (52, 54, 60)
ROD_HI = (108, 112, 122)


def tx(x):
    return (x - X0) / (X1 - X0) * T


def ty(y):
    return (Y1 - y) / (Y1 - Y0) * T


def feather_poly(a, b, width, n=14):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    ln = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / ln, dx / ln
    left, right = [], []
    for k in range(n + 1):
        t = k / n
        w = width * 0.5 * (0.34 + 0.76 * math.sin(math.pi * min(1.0, t * 1.04)) ** 0.6)
        w *= 1.0 - 0.88 * max(0.0, (t - 0.80) / 0.20) ** 1.4
        w = max(w, 0.5)
        x = ax + dx * t
        y = ay + dy * t
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    return left + right[::-1]


def draw_feather(d, md, root, tip, width):
    rx, ry = tx(root[0]), ty(root[1])
    tx_, ty_ = tx(tip[0]), ty(tip[1])
    poly = feather_poly((rx, ry), (tx_, ty_), width)
    md.polygon(poly, fill=255)
    sh = [(x + 3, y + 4) for x, y in poly]
    d.polygon(sh, fill=SHADOW)
    d.polygon(poly, fill=BLUE_D)
    inner = feather_poly((rx + 1, ry - 1), (tx_ + 1, ty_ - 1), width * 0.86)
    d.polygon(inner, fill=BLUE)
    core = feather_poly((rx + 2, ry - 2), (tx_ + 2, ty_ - 2), width * 0.60)
    d.polygon(core, fill=WHITE)
    dx, dy = tx_ - rx, ty_ - ry
    ln = math.hypot(dx, dy) or 1.0
    ux, uy = dx / ln, dy / ln
    bx, by = rx + ux * ln * 0.13, ry + uy * ln * 0.13
    band = feather_poly((rx - ux * 3, ry - uy * 3), (bx, by), width * 0.95)
    d.polygon(band, fill=ROOT_SH)
    d.line([(rx, ry), (tx_, ty_)], fill=WHITE_HI, width=max(1, int(width * 0.05)))
    px, py = -uy, ux
    for k in range(1, max(4, int(ln / 11))):
        f = k / max(4, int(ln / 11))
        cx = rx + dx * f
        cy = ry + dy * f
        bl = width * 0.38 * (1 - 0.55 * f)
        d.line([(cx - px * bl, cy - py * bl), (cx + px * bl, cy + py * bl)],
               fill=(228, 233, 244), width=1)
    d.line([(rx + 1, ry - 1), (tx_ + 1, ty_ - 1)], fill=WHITE_HI,
           width=max(1, int(width * 0.05)))


def wing_texture():
    img = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    mask = Image.new("L", (T, T), 0)
    md = ImageDraw.Draw(mask)
    hub = (9.0, 33.2)
    fan = [(14.8, 34.6), (17.2, 33.6), (19.4, 31.8), (21.2, 29.4), (22.6, 26.6),
           (23.6, 23.4), (24.1, 20.2), (23.9, 16.8), (23.0, 13.6), (21.6, 10.8),
           (19.6, 8.9), (17.2, 7.8), (14.7, 7.8), (12.2, 8.7), (10.2, 10.4)]
    inner = [(8.0, 12.2), (6.5, 15.0), (5.6, 18.5), (5.2, 22.0), (5.6, 25.5),
             (6.6, 28.6), (7.8, 31.0)]
    fan_in = [(hub[0] + (p[0] - hub[0]) * 0.80, hub[1] + (p[1] - hub[1]) * 0.80) for p in fan]
    poly = [hub] + fan_in + inner
    pts = [(tx(x), ty(y)) for x, y in poly]
    d.polygon(pts, fill=(226, 231, 241, 255))
    md.polygon(pts, fill=255)
    # fan primaries from the high hand
    for i, tip in enumerate(fan):
        t = i / (len(fan) - 1)
        root = (hub[0] - 0.3 + 0.7 * t, hub[1] - 0.2)
        draw_feather(d, md, root, tip, 92)
    # inner secondaries along the arm
    sec = [(6.5, 15.0), (8.0, 12.2), (10.2, 10.4), (12.2, 8.7), (14.7, 7.8)]
    for i, tip in enumerate(sec):
        t = i / (len(sec) - 1)
        root = (5.8 + 2.8 * t, 25.8 + 6.2 * t)
        draw_feather(d, md, root, tip, 78)
    # middle shingle row
    for i in range(14):
        t = i / 13
        k = min(len(fan) - 1, int(round(t * (len(fan) - 1))))
        tip = fan[k]
        tip2 = (hub[0] + (tip[0] - hub[0]) * 0.60,
                hub[1] + (tip[1] - hub[1]) * 0.60)
        root = (hub[0] + (tip[0] - hub[0]) * 0.05,
                hub[1] + (tip[1] - hub[1]) * 0.05)
        draw_feather(d, md, root, tip2, 78)
    # short coverts
    for i in range(11):
        t = i / 10
        k = min(len(fan) - 1, int(round(t * (len(fan) - 1))))
        tip = fan[k]
        tip2 = (hub[0] + (tip[0] - hub[0]) * 0.33,
                hub[1] + (tip[1] - hub[1]) * 0.33)
        root = (hub[0] + (tip[0] - hub[0]) * 0.03,
                hub[1] + (tip[1] - hub[1]) * 0.03)
        draw_feather(d, md, root, tip2, 60)
    # shoulder puff near the inner edge
    for dx, dy, ln in ((-0.4, 0.3, 2.3), (0.2, 0.8, 2.6), (0.8, 1.4, 2.3),
                       (0.3, 2.0, 2.0)):
        root = (5.8 + dx, 25.8 + dy)
        tip = (root[0] + ln, root[1] - ln * 0.2)
        draw_feather(d, md, root, tip, 54)
    # armature rod along the leading edge
    rod = [(5.8, 26.4), (6.6, 29.2), (7.8, 31.4), (9.2, 33.2), (11.6, 34.2),
           (14.4, 34.6)]
    rp = [(tx(x), ty(y)) for x, y in rod]
    d.line(rp, fill=ROD, width=3, joint="curve")
    d.line([(x + 1, y - 1) for x, y in rp], fill=ROD_HI, width=1, joint="curve")
    img.putalpha(mask)
    return img.resize((T * 2, T * 2), Image.NEAREST)


# ------------------------------------------------------------------ mesh

def plane_quads():
    quads = []
    nx, ny = 12, 10
    for j in range(ny):
        for i in range(nx):
            quad = []
            for du, dv in ((0, 0), (1, 0), (1, 1), (0, 1)):
                u = (i + du) / nx
                v = (j + dv) / ny
                x = X0 + (X1 - X0) * u
                y = Y1 - (Y1 - Y0) * v
                z = Z_BASE + 0.30 * math.sin(math.pi * u) * (1 - 0.5 * v) \
                    - 0.45 * v + 0.10 * math.sin(math.pi * v)
                quad.append((x, y, z))
            quads.append((quad,
                          [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]))
    return quads


def build_model():
    quads = []
    for side in (1, -1):
        for verts, _ in plane_quads():
            vv = [(side * x, y, z) for x, y, z in verts]
            vb = [(side * (x + 0.10), y, z - 0.30) for x, y, z in verts]
            def uvf(p, z):
                u = (abs(p) - X0) / (X1 - X0)
                v = (Y1 - z) / (Y1 - Y0)
                return (0.002 + 0.996 * u, 0.002 + 0.996 * v)
            uv4 = [uvf(p[0], p[1]) for p in verts]
            quads.append((vv, uv4, (1.0, 1.0, 1.0)))
            quads.append((vb, uv4, (0.72, 0.75, 0.85)))
    return quads


def to_arrays(quads):
    verts, uvs, faces, cols = [], [], [], []
    for verts4, uv4, tint in quads:
        base = len(verts)
        for (x, y, z), (u, v) in zip(verts4, uv4):
            verts.append([x, y, z])
            uvs.append([u, v])
            cols.append(list(tint))
        faces.append((base, base + 1, base + 2))
        faces.append((base, base + 2, base + 3))
    return (np.array(verts, float), np.array(faces, np.int64),
            np.array(uvs, float), np.array(cols, float))


def proxy_boxes(root_z=2.6):
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
                pu.append((0.96, 0.96))
                pc.append(col)
            pf += [(base, base + 1, base + 2), (base, base + 2, base + 3)]
    return np.array(pv, float), pf, np.array(pu, float), np.array(pc, float)


def render_img(tex, quads, size=900, with_body=True, R=None):
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
    rgba = rm.render_view(allv, allf, allu, tex, np.eye(3) if R is None else R,
                          size, alpha=True, shade_lo=0.97, shade_hi=0.62, colors=allc)
    bg = np.zeros((size, size, 3), np.float64)
    yy = np.linspace(0, 1, size)[:, None, None]
    bg[:] = np.array([196, 200, 232]) * (1 - yy) + np.array([118, 122, 168]) * yy
    base = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    base.alpha_composite(Image.fromarray(rgba, "RGBA"))
    return base.convert("RGB")


def main():
    OUT.mkdir(exist_ok=True)
    ART.mkdir(parents=True, exist_ok=True)
    wing = wing_texture()
    wing.save(ART / "angel_wing_tex.png")
    tex = np.asarray(wing.convert("RGBA"), float)
    quads = build_model()
    print("quads", len(quads))
    size = 780
    sheet = Image.new("RGB", (size * 2, (size + 26) * 2), (28, 30, 38))
    d = ImageDraw.Draw(sheet)
    views = [("back", None), ("3/4 back", rm.rot_y(-24) @ rm.rot_x(-4)),
             ("side", rm.rot_y(-70)), ("back low", rm.rot_x(10))]
    for i, (label, R) in enumerate(views):
        img = render_img(tex, quads, size=size, with_body=True, R=R)
        x, y = (i % 2) * size, (i // 2) * (size + 26)
        sheet.paste(img, (x, y + 26))
        d.text((x + 10, y + 7), f"Angel wing v2 - {label}", fill=(230, 226, 214))
    sheet.save(OUT / "angel_v2_preview.png")
    back = render_img(tex, quads, size=1000, with_body=True)
    ref = Image.open(OUT / "angel_ref_big.png").convert("RGB")
    h = 780
    ref_img = ref.resize((h, h), Image.LANCZOS)
    new_img = back.resize((h, h), Image.LANCZOS)
    cmp_img = Image.new("RGB", (ref_img.width + new_img.width + 42, h + 70), (24, 26, 33))
    cmp_img.paste(ref_img, (14, 52))
    cmp_img.paste(new_img, (28 + ref_img.width, 52))
    dc = ImageDraw.Draw(cmp_img)
    dc.text((16, 22), "LUNAR REFERENCE - white angel wings", fill=(220, 214, 200))
    dc.text((30 + ref_img.width, 22), "NEW - pixel-art angel clone", fill=(220, 214, 200))
    cmp_img.save(OUT / "angel_v2_compare.png")
    print("saved", OUT / "angel_v2_preview.png")


if __name__ == "__main__":
    main()
