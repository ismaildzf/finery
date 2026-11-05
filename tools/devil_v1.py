"""Devil v1: bat/demon wing matching the Lunar Devil Wings silhouette.

Wing-local space: X outboard, Y up, Z backward (toward a back-view camera).
1 unit = 1 texel.  The wing is a folding fan of four curved finger bones off a
high wrist apex, a thick arm bone rooted at the spine, and a ragged crimson
membrane with a black leading edge and ankle-length torn fringe.
"""
import json
import math
import pathlib
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parents[1]
ART = ROOT / "art-wings" / "devil"
OUT = ROOT / "_design"
sys.path.insert(0, str(ROOT / "tools"))
import render_mesh as rm  # noqa: E402

ATLAS = 512
ROOT_X = 1.6
W = (6.2, 12.2)

# arm: shoulder root -> elbow -> wrist apex (wing-local 2D)
ARM = [(0.0, 0.0), (1.1, 2.3), (2.6, 6.0), (4.2, 9.6), W]

# four curved fingers fanning down from the wrist apex, outermost first
F0 = [W, (8.9, 10.9), (12.4, 4.8), (14.8, -1.5), (15.9, -8.0), (16.2, -12.5)]
F1 = [W, (8.0, 11.0), (10.7, 5.0), (12.6, -1.5), (13.3, -8.0), (13.1, -12.0)]
F2 = [W, (7.3, 10.2), (9.2, 4.0), (10.5, -2.5), (10.7, -8.5), (10.2, -11.2)]
F3 = [W, (6.7, 9.4), (7.8, 3.0), (8.3, -3.5), (8.0, -9.0), (7.3, -10.4)]

# inner attachment: wrist -> spine root -> lower back
BODY_EDGE = [W, (5.4, 9.5), (4.2, 2.0), (1.8, -2.0), (-0.2, -3.4)]
SIDE_INNER = list(reversed(ARM)) + [(-0.2, -3.4)]

# rects in the 512 atlas
MEM_ZONE = (8, 8, 448, 504)
MEM_V = (10, 500)
BONE_RECT = (448, 0, 512, 256)
PLATE_RECT = (448, 256, 512, 320)
GRAY_RECT = (384, 256, 448, 320)
GRAY_UV = ((GRAY_RECT[0] + GRAY_RECT[2]) * 0.5 / ATLAS,
           (GRAY_RECT[1] + GRAY_RECT[3]) * 0.5 / ATLAS)


# ── texture ─────────────────────────────────────────────────────────────────
def _block_noise(rng, h, w, cell, sigma):
    small = rng.normal(0.0, sigma, (h // cell + 2, w // cell + 2))
    big = np.kron(small, np.ones((cell, cell), np.float32))
    return big[:h, :w]


def _membrane_zone(rng):
    x0, y0, x1, y1 = MEM_ZONE
    w, h = x1 - x0, y1 - y0
    stops = [(0.00, (6, 1, 2)), (0.16, (16, 2, 3)), (0.32, (36, 4, 5)),
             (0.48, (66, 6, 7)), (0.60, (110, 11, 12)), (0.70, (160, 18, 19)),
             (0.78, (205, 28, 28)), (0.86, (245, 46, 42)), (0.92, (255, 60, 50)),
             (0.97, (200, 24, 24)), (1.00, (96, 8, 10))]
    yy = np.linspace(0.0, 1.0, h, dtype=np.float32)
    rows = np.zeros((h, 3), np.float32)
    for c in range(3):
        rows[:, c] = np.interp(yy, [s[0] for s in stops], [s[1][c] for s in stops])
    mem = np.repeat(rows[:, None, :], w, axis=1)

    n1 = _block_noise(rng, h, w, 16, 0.065)
    n2 = _block_noise(rng, h, w, 48, 0.08)
    mem *= (1.0 + n1 + n2)[..., None]
    # warm embers bias toward the bottom
    warm = np.clip((yy - 0.70) / 0.30, 0, 1)[:, None]
    mem[..., 0] += 16.0 * warm * np.clip(_block_noise(rng, h, w, 16, 0.9), 0, 1.5)
    # inner half of the texture is the darker, recessed spine membrane
    fold = np.clip((np.arange(w, dtype=np.float32) - 160.0) / 64.0, 0.0, 1.0)
    mem *= (0.68 + 0.32 * fold)[None, :, None]
    mem = np.clip(mem, 0, 255)

    img = Image.fromarray(np.dstack([mem.astype(np.uint8),
                                     np.full((h, w), 255, np.uint8)]), "RGBA")
    d = ImageDraw.Draw(img)

    # heavy black veins running from the wrist edge into the membrane
    for _ in range(10):
        x = float(rng.integers(0, w))
        y = 0.0
        width = int(rng.integers(2, 7))
        end = float(rng.uniform(0.55, 0.9)) * h
        while y < end:
            step = float(rng.uniform(18, 34))
            nx = min(max(x + float(rng.normal(0, 4)), 1), w - 2)
            d.line([(x, y), (nx, y + step)], fill=(5, 1, 2, 215), width=width)
            x, y = nx, y + step
    # faint crimson capillaries in the bright lower half
    for _ in range(18):
        x = float(rng.integers(0, w))
        y = float(rng.uniform(0.62, 0.86)) * h
        d.line([(x, y), (x + rng.uniform(-10, 10), y + rng.uniform(10, 26))],
               fill=(150, 26, 26, 80), width=int(rng.integers(1, 3)))

    # blocky ember clusters
    for _ in range(34):
        cx = float(rng.integers(0, w))
        cy = float(rng.uniform(0.72, 0.96)) * h
        for _ in range(int(rng.integers(2, 6))):
            bw = int(rng.integers(3, 11))
            bh = int(rng.integers(2, 7))
            col = [(232, 44, 34, 220), (188, 22, 24, 220), (130, 10, 14, 220),
                   (255, 84, 48, 190), (68, 4, 8, 230)][int(rng.integers(0, 5))]
            px = min(max(cx + float(rng.normal(0, 12)), 0), w - bw)
            py = min(max(cy + float(rng.normal(0, 16)), 0), h - bh)
            d.rectangle([px, py, px + bw, py + bh], fill=col)

    # ragged bottom edge: big chunky teeth, triangular tears, hanging strands
    edge_y = int(h * 0.87)
    mask = Image.new("L", (w, h), 255)
    md = ImageDraw.Draw(mask)
    col = 16
    for x in range(0, w, col):
        e = edge_y + int(rng.integers(-16, 28))
        if rng.random() < 0.20:
            e += int(rng.integers(24, 52))
        e = min(e, h - 2)
        md.rectangle([x, e, x + col - 1, h], fill=0)
        # black torn lip sits on the opaque side of the edge
        d.rectangle([x, max(0, e - 8), x + col - 1, e - 1],
                    fill=(8, 1, 2, 255) if rng.random() < 0.55 else (52, 4, 7, 255))
    # triangular tears cut up into the membrane
    for _ in range(10):
        nw = int(rng.integers(24, 52))
        x = int(rng.integers(0, max(1, w - nw)))
        depth = int(rng.integers(18, 52))
        md.polygon([(x, edge_y + 18), (x + nw // 2, edge_y - depth),
                    (x + nw, edge_y + 18)], fill=0)
        d.line([(x, edge_y + 18), (x + nw // 2, edge_y - depth),
                (x + nw, edge_y + 18)], fill=(8, 1, 2, 255), width=6)
    # hanging red strands, wide and tapered like torn cloth
    for _ in range(30):
        x = int(rng.integers(0, w - 24))
        sw = int(rng.integers(12, 30))
        sy = edge_y + int(rng.integers(-6, 20))
        sy2 = min(h - 1, sy + int(rng.integers(36, 110)))
        tip = x + sw // 2 + int(rng.integers(-6, 6))
        md.polygon([(x, sy), (x + sw, sy), (tip, sy2)], fill=255)
        colr = ((124, 9, 13, 255) if rng.random() < 0.6 else
                (44, 3, 5, 255))
        d.polygon([(x, sy), (x + sw, sy), (tip, sy2)], fill=colr)
        if rng.random() < 0.55:
            d.polygon([(tip - 4, sy2 - 8), (tip + 4, sy2 - 8),
                       (tip, sy2)], fill=(238, 40, 34, 255))
        if rng.random() < 0.35:
            nx = min(w - 12, x + sw + int(rng.integers(2, 16)))
            ny = min(h - 1, sy + int(rng.integers(20, 60)))
            md.polygon([(nx, sy + 8), (nx + 10, sy + 8), (nx + 4, ny)], fill=255)
            d.polygon([(nx, sy + 8), (nx + 10, sy + 8), (nx + 4, ny)],
                      fill=(96, 6, 10, 255))

    a = np.array(img)
    a[..., 3] = np.asarray(mask)
    return Image.fromarray(a, "RGBA")


def _bone_zone(rng):
    x0, y0, x1, y1 = BONE_RECT
    w, h = x1 - x0, y1 - y0
    img = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)
    # rounded black bone: dark edges, a thin cold sheen, plenty of soot
    for x in range(w):
        t = x / max(1, w - 1)
        g = int(3 + 13 * math.sin(math.pi * min(1.0, t / 0.62)) ** 1.5)
        if 0.15 < t < 0.24:
            g += 13
        d.line([(x, 0), (x, h)], fill=(g, g, g + 3, 255))
    for _ in range(22):
        x = int(rng.integers(0, w))
        y = int(rng.integers(0, h))
        ww = int(rng.integers(1, 3))
        hh = int(rng.integers(4, 16))
        g = int(rng.integers(16, 28))
        d.rectangle([x, y, x + ww, y + hh], fill=(g, g, g + 3, 150))
    for _ in range(60):
        x = int(rng.integers(0, w))
        y = int(rng.integers(0, h))
        d.rectangle([x, y, x + int(rng.integers(2, 6)), y + int(rng.integers(2, 7))],
                    fill=(3, 3, 4, 255))
    # distal heat: the last stretch of every bone picks up a dull red glint
    tip = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    td = ImageDraw.Draw(tip)
    for y in range(int(h * 0.9), h):
        f = (y - h * 0.9) / (h * 0.1)
        td.line([(0, y), (w, y)], fill=(78, 6, 9, int(120 * f)))
    for _ in range(18):
        x = int(rng.integers(0, w - 2))
        y = int(rng.integers(int(h * 0.88), h - 2))
        td.rectangle([x, y, x + int(rng.integers(1, 4)), y + 1],
                     fill=(210, 46, 38, 200))
    img.alpha_composite(tip)
    return img


def _plate_zone(rng):
    x0, y0, x1, y1 = PLATE_RECT
    w, h = x1 - x0, y1 - y0
    img = Image.new("RGBA", (w, h), (9, 9, 11, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w - 1, h - 1], outline=(34, 34, 40, 255), width=2)
    d.rectangle([4, 4, w - 5, h - 5], outline=(17, 17, 21, 255), width=2)
    for _ in range(9):
        x = int(rng.integers(8, w - 16))
        y = int(rng.integers(6, h - 14))
        pts = [(x, y)]
        for _ in range(int(rng.integers(2, 5))):
            pts.append((min(w - 2, max(1, pts[-1][0] + int(rng.integers(-10, 12)))),
                        min(h - 2, pts[-1][1] + int(rng.integers(3, 12)))))
        col = (120 + int(rng.integers(0, 90)), 14, 16, 255)
        d.line(pts, fill=col, width=int(rng.integers(1, 3)))
    return img


def build_atlas():
    rng = np.random.default_rng(20261020)
    atlas = Image.new("RGBA", (ATLAS, ATLAS), (0, 0, 0, 0))
    atlas.alpha_composite(_membrane_zone(rng), MEM_ZONE[:2])
    atlas.alpha_composite(_bone_zone(rng), BONE_RECT[:2])
    atlas.alpha_composite(_plate_zone(rng), PLATE_RECT[:2])
    ImageDraw.Draw(atlas).rectangle(
        [GRAY_RECT[0], GRAY_RECT[1], GRAY_RECT[2] - 1, GRAY_RECT[3] - 1],
        fill=(96, 100, 110, 255))
    # every panel fades to near-black where it meets a bone
    arr = np.array(atlas).astype(np.float32)
    ys, ye = MEM_ZONE[1], MEM_ZONE[3]
    for name, (sx0, sx1) in SLICES.items():
        ax0, ax1 = MEM_ZONE[0] + sx0, MEM_ZONE[0] + sx1
        xs = np.arange(ax0, ax1)
        dist = np.minimum(xs - ax0, ax1 - 1 - xs)
        f = 0.74 + 0.26 * np.clip(dist / 8.0, 0, 1) ** 0.8
        arr[ys:ye, ax0:ax1, :3] *= f[None, :, None]
        if name == "inner":
            arr[ys:ye, ax0:ax1, :3] *= 0.62
    atlas = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")
    ART.mkdir(parents=True, exist_ok=True)
    atlas.save(ART / "devil_atlas_512.png")
    atlas.save(OUT / "devil_atlas_512.png")
    return atlas


# ── geometry helpers ────────────────────────────────────────────────────────
def poly_prep(pts):
    p = np.asarray(pts, float)
    seg = np.linalg.norm(np.diff(p, axis=0), axis=1)
    return p, seg, np.concatenate([[0.0], np.cumsum(seg)])


def poly_at(prep, t):
    p, seg, cum = prep
    d = float(np.clip(t, 0.0, 1.0)) * cum[-1]
    i = int(np.searchsorted(cum, d, side="right") - 1)
    i = min(max(i, 0), len(p) - 2)
    f = (d - cum[i]) / max(seg[i], 1e-9)
    return p[i] + (p[i + 1] - p[i]) * f


def poly_tan(prep, t):
    p, seg, cum = prep
    a, b = poly_at(prep, max(0.0, t - 0.01)), poly_at(prep, min(1.0, t + 0.01))
    v = b - a
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else np.array([0.0, -1.0])


def smoothstep(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3.0 - 2.0 * t)


PREP_F0 = poly_prep(F0)
PREP_F1 = poly_prep(F1)
PREP_F2 = poly_prep(F2)
PREP_F3 = poly_prep(F3)
PREP_ARM = poly_prep(ARM)
PREP_SIDE_INNER = poly_prep(SIDE_INNER)

# panel side curves (inner first so it gets the darkest atlas slice)
# name, side A, side B, flip U, sag scale, V range
PANELS = [
    ("inner", PREP_SIDE_INNER, PREP_F3, True, 1.05, 0.84),
    ("p2", PREP_F2, PREP_F3, False, 1.02, 1.00),
    ("p1", PREP_F1, PREP_F2, True, 1.00, 1.00),
    ("p0", PREP_F0, PREP_F1, False, 1.00, 1.00),
]


def _panel_slices():
    """Give each panel a proportional horizontal slice so texels stay square."""
    widths = []
    for name, a, b, _flip, _sg, _vr in PANELS:
        ds = [np.linalg.norm(poly_at(a, t) - poly_at(b, t))
              for t in np.linspace(0.12, 1.0, 8)]
        widths.append(float(np.mean(ds)))
    scale = 23.0
    x = 14
    out = {}
    for (name, *_rest), wd in zip(PANELS, widths):
        px = int(max(36, round(wd * scale)))
        out[name] = (x, min(x + px, 440))
        x += px + 8
    if x > 442:
        k = 428.0 / (x - 14)
        x = 14
        for (name, *_rest), wd in zip(PANELS, widths):
            px = int(max(32, round(wd * scale * k)))
            out[name] = (x, min(x + px, 440))
            x += px + 8
    return out


SLICES = _panel_slices()


def _uv(u, v, x0, x1, flip=False, vmax=1.0):
    su = 1.0 - u if flip else u
    px = x0 + 1.5 + su * (x1 - x0 - 3.0)
    py = MEM_V[0] + v * vmax * (MEM_V[1] - MEM_V[0])
    return (px / ATLAS, py / ATLAS)


def membrane_panel(name, prep_a, prep_b, flip, sag_scale, vmax):
    nu, nv = 7, 10
    x0, x1 = SLICES[name]
    verts, uvs = [], []
    for j in range(nv + 1):
        v = j / nv
        pa = poly_at(prep_a, 0.03 + 0.97 * v)
        pb = poly_at(prep_b, 0.03 + 0.97 * v)
        row_v, row_u = [], []
        for i in range(nu + 1):
            u = i / nu
            p = pa + (pb - pa) * u
            span = np.linalg.norm(pb - pa)
            sag = (0.45 + 2.8 * math.sin(math.pi * u)) \
                * smoothstep(0.38, 1.0, v) ** 1.35 \
                * min(1.45, span / 3.2) * sag_scale
            toward = np.array(W) - p
            n = np.linalg.norm(toward)
            p = p + toward / max(n, 1e-6) * sag
            z = 0.28 + 0.95 * math.sin(math.pi * u) * math.sin(math.pi * min(1.0, v * 0.94)) \
                + 0.035 * math.sin(2.2 * math.pi * u + 1.7 * v)
            row_v.append((float(p[0]), float(p[1]), float(z)))
            row_u.append(_uv(u, v, x0, x1, flip, vmax))
        verts.append(row_v)
        uvs.append(row_u)
    quads = []
    for j in range(nv):
        for i in range(nu):
            quads.append(([verts[j][i], verts[j][i + 1], verts[j + 1][i + 1],
                           verts[j + 1][i]],
                          [uvs[j][i], uvs[j][i + 1], uvs[j + 1][i + 1],
                           uvs[j + 1][i]]))
    return quads


def _bone_uv(u, v):
    x0, y0, x1, y1 = BONE_RECT
    return ((x0 + 0.5 + u * (x1 - x0 - 1.0)) / ATLAS,
            (y0 + 0.5 + v * (y1 - y0 - 1.0)) / ATLAS)


def ribbon_prism(pts, width_fn, thickness, z=1.42, samples=10):
    prep = poly_prep(pts)
    ts = np.linspace(0.0, 1.0, samples + 1)
    P = [poly_at(prep, t) for t in ts]
    T = [poly_tan(prep, t) for t in ts]
    lengths = [0.0]
    for i in range(samples):
        lengths.append(lengths[-1] + float(np.linalg.norm(P[i + 1] - P[i])))
    total = max(lengths[-1], 1e-6)
    vs = [d / total for d in lengths]
    LF, RF, LB, RB = [], [], [], []
    for i, t in enumerate(ts):
        w = width_fn(t) * 0.5
        n = np.array([-T[i][1], T[i][0]])
        l = P[i] + n * w
        r = P[i] - n * w
        zf, zb = z + thickness * 0.5, z - thickness * 0.5
        LF.append((float(l[0]), float(l[1]), zf))
        RF.append((float(r[0]), float(r[1]), zf))
        LB.append((float(l[0]), float(l[1]), zb))
        RB.append((float(r[0]), float(r[1]), zb))
    quads = []
    for i in range(samples):
        v0, v1 = vs[i], vs[i + 1]
        # back face (toward the back-view camera)
        quads.append(([RB[i], LB[i], LB[i + 1], RB[i + 1]],
                      [_bone_uv(0, v0), _bone_uv(1, v0), _bone_uv(1, v1),
                       _bone_uv(0, v1)]))
        # front face
        quads.append(([LF[i], RF[i], RF[i + 1], LF[i + 1]],
                      [_bone_uv(1, v0), _bone_uv(0, v0), _bone_uv(0, v1),
                       _bone_uv(1, v1)]))
        # left edge
        quads.append(([LB[i], LF[i], LF[i + 1], LB[i + 1]],
                      [_bone_uv(0, v0), _bone_uv(1, v0), _bone_uv(1, v1),
                       _bone_uv(0, v1)]))
        # right edge
        quads.append(([RF[i], RB[i], RB[i + 1], RF[i + 1]],
                      [_bone_uv(0, v0), _bone_uv(1, v0), _bone_uv(1, v1),
                       _bone_uv(0, v1)]))
    return quads


def arm_width(t):
    return 1.45 + 0.55 * math.sin(math.pi * min(1.0, t / 0.8)) - 0.22 * t


def finger_width(t):
    return 0.10 + 1.18 * (1.0 - t) ** 0.55


def spike(base, direction, length, width, z=1.38):
    p0 = np.array(base, float)
    d = np.array(direction, float)
    d /= max(np.linalg.norm(d), 1e-6)
    pts = [tuple(p0), tuple(p0 + d * length * 0.55),
           tuple(p0 + d * length + np.array([-d[1], d[0]]) * 0.35)]
    return ribbon_prism(pts, lambda t: width * (1.0 - t) ** 0.7 + 0.02, 0.18,
                        z=z, samples=3)


def membrane_quads():
    quads = []
    for name, a, b, flip, sg, vr in PANELS:
        quads += membrane_panel(name, a, b, flip, sg, vr)
    return quads


def bone_quads():
    quads = []
    quads += ribbon_prism(ARM, arm_width, 0.55, z=1.42, samples=11)
    for pts in (F0, F1, F2, F3):
        quads += ribbon_prism(pts, finger_width, 0.36, z=1.42, samples=10)

    # wrist knuckle: a heavy black boss where every finger meets
    knuckle = [(5.45, 11.2), (6.2, 12.35), (6.55, 13.05)]
    quads += ribbon_prism(knuckle, lambda t: 2.0 * (1 - t) + 0.9, 0.72,
                          z=1.46, samples=4)

    # apex claw and inner barb
    claw = [W, (6.5, 13.2), (6.8, 13.9), (7.05, 14.35)]
    quads += ribbon_prism(claw, lambda t: 1.45 * (1 - t) ** 0.5 + 0.10, 0.44,
                          z=1.44, samples=4)
    barb = [(6.65, 13.4), (6.35, 13.9), (6.2, 14.2)]
    quads += ribbon_prism(barb, lambda t: 0.78 * (1 - t) ** 0.65 + 0.04, 0.28,
                          z=1.40, samples=3)

    # jagged spurs along the outside of the leading finger
    for t, ln, wd in ((0.27, 1.35, 0.62), (0.49, 1.55, 0.68), (0.70, 1.25, 0.54)):
        p = poly_at(PREP_F0, t)
        tan = poly_tan(PREP_F0, t)
        out = np.array([-tan[1], tan[0]])
        base = p + out * (finger_width(t) * 0.35)
        direction = out * 0.8 + tan * 0.9
        quads += spike(base, direction, ln, wd)
    # tip barb
    tip = np.array(F0[-1], float)
    quads += spike(tip + np.array([0.0, 0.35]), np.array([0.25, -1.0]), 1.5, 0.42)

    # root plate: small armored cap bridging the two wings at the spine
    x0, y0, x1, y1 = PLATE_RECT
    def puv(u, v):
        return ((x0 + 2 + u * (x1 - x0 - 4)) / ATLAS,
                (y0 + 2 + v * (y1 - y0 - 4)) / ATLAS)
    for zz in (1.30, 1.48):
        quads.append(([(-1.05, -0.85, zz), (1.15, -0.65, zz),
                       (1.05, 1.85, zz), (-0.95, 1.65, zz)],
                      [puv(0, 0), puv(1, 0), puv(1, 1), puv(0, 1)]))
    return quads


def build_model():
    mem = membrane_quads()
    bones = bone_quads()
    out = []
    for side in (1, -1):
        for verts, uv in mem + bones:
            vv = [(side * (x + ROOT_X), y, z) for x, y, z in verts]
            if side < 0:
                vv = list(reversed(vv))
                uu = list(reversed(uv))
            else:
                uu = uv
            out.append((vv, uu))
    return out


# ── preview ─────────────────────────────────────────────────────────────────
def to_arrays(quads):
    verts, uvs, faces = [], [], []
    for verts4, uv4 in quads:
        base = len(verts)
        for (x, y, z), (u, v) in zip(verts4, uv4):
            verts.append([x, y, z])
            uvs.append([u, v])
        faces.append((base, base + 1, base + 2))
        faces.append((base, base + 2, base + 3))
    return np.array(verts, float), np.array(faces, np.int64), np.array(uvs, float)


def proxy_boxes(shoulder_y=24.0, root_z=2.6):
    boxes = [((-4, 24, -4), (4, 32, 4)), ((-4, 12, -2), (4, 24, 2)),
             ((-4, 0, -2), (0, 12, 2)), ((0, 0, -2), (4, 12, 2)),
             ((-8, 12, -2), (-4, 24, 2)), ((4, 12, -2), (8, 24, 2))]
    pv, pf, pu = [], [], []
    for frm, to in boxes:
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
                pu.append(GRAY_UV)
            pf += [(base, base + 1, base + 2), (base, base + 2, base + 3)]
    return np.array(pv, float), pf, np.array(pu, float)


def render_sheet(atlas, path):
    tex = np.asarray(atlas.convert("RGBA"), float)
    quads = build_model()
    v, f, u = to_arrays(quads)
    v = v + np.array([0.0, 22.4, 4.2])
    pv, pf, pu = proxy_boxes()
    allv = np.vstack([pv, v])
    allf = np.array(pf + [(a + len(pv), b + len(pv), c + len(pv)) for a, b, c in f],
                    np.int64)
    allu = np.vstack([pu, u])

    size = 760
    views = [("back", np.eye(3)),
             ("3/4 back", rm.rot_y(-32) @ rm.rot_x(-6)),
             ("side", rm.rot_y(-82)),
             ("back low", rm.rot_x(10))]
    sheet = Image.new("RGB", (size * 2, (size + 26) * 2), (17, 18, 22))
    d = ImageDraw.Draw(sheet)
    for i, (label, R) in enumerate(views):
        img = rm.render_view(allv, allf, allu, tex, R, size,
                             shade_lo=0.72, shade_hi=0.32)
        x, y = (i % 2) * size, (i // 2) * (size + 26)
        sheet.paste(Image.fromarray(img), (x, y + 26))
        d.text((x + 10, y + 7), f"Devil v1 - {label}", fill=(240, 233, 208))
    sheet.save(path)
    return sheet


def main():
    OUT.mkdir(exist_ok=True)
    atlas = build_atlas()
    quads = build_model()
    print("panels", {k: v for k, v in SLICES.items()})
    print("quads", len(quads), "tris", len(quads) * 2)
    render_sheet(atlas, OUT / "devil_v1_preview.png")
    print("saved", OUT / "devil_v1_preview.png")
    (ART / "devil_v1_meta.json").write_text(json.dumps(
        {"slices": SLICES, "quads": len(quads), "root_x": ROOT_X}, indent=1))


if __name__ == "__main__":
    main()
