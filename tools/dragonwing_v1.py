"""Dragon Wings (Black) v1 - skeletal bat/dragon wing.

Reference: Lunar Client Store "Dragon Wings (Black)" (reference only; original
procedural build).  Structure: shoulder arm -> wrist at head height, four long
finger bones with knuckles and claws, wrist thumb claw, outer spikes, and a
dark leathery membrane with scalloped trailing edge.  Coordinates: player
units, feet y=0, head top y=32, +z toward the back camera.
"""
import json
import math
import pathlib
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parents[1]
ART = ROOT / "art-wings" / "dragon"
OUT = ROOT / "_design"
sys.path.insert(0, str(ROOT / "tools"))
import render_mesh as rm  # noqa: E402

AW = AH = 1024
CELLS = {
    "membrane": (8, 8, 700, 700),
    "scale": (708, 8, 1016, 316),
    "bone": (708, 324, 1016, 760),
    "claw": (708, 768, 1016, 940),
    "solid": (708, 948, 728, 968),
}

# key points (right wing)
S = (3.9, 24.4)      # shoulder root
E = (5.8, 29.1)      # elbow (straight arm midpoint)
W = (6.9, 33.8)      # wrist / knuckle, above head
TIPS = {
    1: (16.9, 14.0),  # outer / leading finger
    2: (14.4, 11.5),
    3: (11.0, 10.0),
    4: (7.5, 14.0),
}
HIP = (3.6, 17.6)
Z_W = 3.62
Z_S = 2.92
Z_HIP = 2.72
Z_TIP = {1: 1.92, 2: 2.15, 3: 2.42, 4: 2.72}

A6_TINTS = {
    "membrane": (1.0, 1.0, 1.0),
    "scale": (0.55, 0.58, 0.66),
    "bone": (0.24, 0.25, 0.29),
    "bone_hi": (0.46, 0.48, 0.54),
    "claw": (0.50, 0.50, 0.49),
    "spike": (0.42, 0.44, 0.52),
}


def mesh_line(p0, p1, n):
    return [(p0[0] + (p1[0] - p0[0]) * i / (n - 1),
             p0[1] + (p1[1] - p0[1]) * i / (n - 1)) for i in range(n)]


def bezier(a, b, c, n, pull=0.0, hub=W):
    if pull:
        mx, my = (a[0] + b[0]) * 0.5, (a[1] + b[1]) * 0.5
        c = (mx + (hub[0] - mx) * pull, my + (hub[1] - my) * pull)
    out = []
    for i in range(n):
        u = i / (n - 1)
        x = (1 - u) ** 2 * a[0] + 2 * u * (1 - u) * c[0] + u * u * b[0]
        y = (1 - u) ** 2 * a[1] + 2 * u * (1 - u) * c[1] + u * u * b[1]
        out.append((x, y))
    return out


def boundary_points():
    segs = [
        (mesh_line(S, HIP, 9)[:-1], Z_S, Z_HIP),
        (bezier(HIP, TIPS[4], (0, 0), 10, pull=0.15)[:-1], Z_HIP, Z_TIP[4]),
        (bezier(TIPS[4], TIPS[3], (0, 0), 9, pull=0.17)[:-1], Z_TIP[4], Z_TIP[3]),
        (bezier(TIPS[3], TIPS[2], (0, 0), 9, pull=0.20)[:-1], Z_TIP[3], Z_TIP[2]),
        (bezier(TIPS[2], TIPS[1], (0, 0), 9, pull=0.15), Z_TIP[2], Z_TIP[1]),
    ]
    out = []
    for pts, za, zb in segs:
        for i, p in enumerate(pts):
            f = i / max(1, len(pts) - 1)
            out.append((p[0], p[1], za + (zb - za) * f))
    return out


BOUNDARY = boundary_points()
F1_PATH2D = [W, (10.3, 31.2), (13.2, 27.2), (15.6, 22.0), (16.8, 17.2), TIPS[1]]


def f1_point(s):
    segs = [math.dist(F1_PATH2D[i], F1_PATH2D[i + 1]) for i in range(len(F1_PATH2D) - 1)]
    total = sum(segs) or 1.0
    d = min(max(s, 0.0), 1.0) * total
    for i, ln in enumerate(segs):
        if d <= ln or i == len(segs) - 1:
            f = d / ln if ln else 0.0
            a, b = F1_PATH2D[i], F1_PATH2D[i + 1]
            return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
        d -= ln
    return F1_PATH2D[-1]


def boundary_at(u):
    x = min(max(u, 0.0), 1.0) * (len(BOUNDARY) - 1)
    i = int(x)
    f = x - i
    a = BOUNDARY[i]
    b = BOUNDARY[min(i + 1, len(BOUNDARY) - 1)]
    return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f,
            a[2] + (b[2] - a[2]) * f)


INNER_PATH = bezier(W, S, (2.6, 27.2), 9)


def inner_point(s):
    x = min(max(s, 0.0), 1.0) * (len(INNER_PATH) - 1)
    i = int(x)
    f = x - i
    a = INNER_PATH[i]
    b = INNER_PATH[min(i + 1, len(INNER_PATH) - 1)]
    return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)


def membrane_point(s, u):
    b = boundary_at(u)
    if u <= 1e-6:
        p = inner_point(s) + (Z_W + (Z_S - Z_W) * s,)
    elif u >= 1 - 1e-6:
        fx, fy = f1_point(s)
        p = (fx, fy, Z_W + (Z_TIP[1] - Z_W) * s)
    else:
        p = (W[0] + (b[0] - W[0]) * s, W[1] + (b[1] - W[1]) * s,
             Z_W + (b[2] - Z_W) * s)
    sag = 0.34 * math.sin(math.pi * s) * (0.35 + 0.65 * math.sin(math.pi * u))
    return (p[0], p[1], p[2] - sag)


# ------------------------------------------------------------------ atlas

def _noise(rng, h, w, amp):
    return rng.normal(0, amp, (h, w, 1)).astype(np.float32)


def make_membrane(w, h):
    rng = np.random.default_rng(21)
    top = np.array([36, 37, 42], np.float32)
    bot = np.array([12, 12, 15], np.float32)
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    arr = top * (1 - yy) + bot * yy
    arr = np.repeat(arr, w, axis=1)
    xx = np.linspace(0, 1, w, dtype=np.float32)[None, :, None]
    # pleats where the membrane gathers at each finger bone
    for c in (0.41, 0.60, 0.79, 0.94):
        arr *= 1 - 0.06 * np.exp(-((xx - c) / 0.060) ** 2)
        arr += 2.5 * np.exp(-((xx - (c + 0.034)) / 0.018) ** 2)
    arr += 4.5 * (1 - yy) ** 2
    arr += _noise(rng, h, w, 2.6)
    mottle = rng.normal(0, 1, (h // 8 + 1, w // 8 + 1, 1)).astype(np.float32)
    mottle = np.repeat(np.repeat(mottle, 8, 0), 8, 1)[:h, :w]
    arr += mottle * 3.0
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(img, "RGBA")
    # faint leathery creases radiating from the wrist
    hub = (w * 0.5, -10)
    for ang in np.linspace(-70, 70, 8):
        a = math.radians(ang)
        end = (hub[0] + math.sin(a) * h * 1.5, hub[1] + math.cos(a) * h * 1.5)
        d.line([hub, end], fill=(58, 59, 66, 10), width=1)
    img = img.filter(ImageFilter.GaussianBlur(1.1))
    return img


def make_scales(w, h):
    rng = np.random.default_rng(5)
    arr = np.zeros((h, w, 3), np.float32)
    arr[:] = (28, 30, 36)
    arr += _noise(rng, h, w, 2.0)
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(img, "RGBA")
    for row in range(-1, 9):
        y = row * 36
        off = 22 if row % 2 else 0
        for x in range(-40, w + 40, 44):
            cx = x + off
            d.rounded_rectangle([cx, y, cx + 38, y + 30], radius=12,
                                fill=(44, 47, 56, 200), outline=(9, 10, 13, 170), width=2)
            d.arc([cx + 4, y + 2, cx + 34, y + 26], 200, 340,
                  fill=(120, 124, 140, 170), width=2)
    return img


def make_bone(w, h):
    rng = np.random.default_rng(9)
    xx = np.linspace(-1, 1, w, dtype=np.float32)[None, :]
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    ridge = np.clip(1 - np.abs(xx) ** 1.7, 0, 1)
    lum = np.broadcast_to(38 + 112 * ridge, (h, w)).copy()
    lum += 10 * np.sin(yy * 52.0) * ridge
    for gy in np.linspace(0.06, 0.94, 9):
        lum -= 26 * np.exp(-((yy - gy) / 0.008) ** 2)
    for _ in range(18):
        cx = rng.uniform(-0.7, 0.7)
        cy = rng.uniform(0.03, 0.97)
        ln = rng.uniform(0.008, 0.030)
        amp = rng.uniform(12, 32)
        lum -= amp * np.exp(-((xx - cx) / 0.03) ** 2) * np.exp(-((yy - cy) / ln) ** 2)
    lum = np.clip(lum, 0, 255)
    rgb = np.stack([lum * 1.0, lum * 0.99, lum * 0.97], -1)
    return Image.fromarray(rgb.astype(np.uint8), "RGB")


def make_claws(w, h):
    xx = np.linspace(-1, 1, w, dtype=np.float32)[None, :]
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    ridge = np.clip(1 - np.abs(xx) ** 1.5, 0, 1)
    base = 40 + 85 * yy
    lum = np.broadcast_to(22, (h, w)).astype(np.float32) + ridge * base
    for gy in np.linspace(0.12, 0.9, 5):
        lum -= 38 * np.exp(-((yy - gy) / 0.012) ** 2)
    rgb = np.stack([lum * 1.0, lum * 0.975, lum * 0.93], -1)
    return Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8), "RGB")


def build_atlas():
    ART.mkdir(parents=True, exist_ok=True)
    atlas = Image.new("RGBA", (AW, AH), (0, 0, 0, 0))
    parts = {
        "membrane": make_membrane(692, 692),
        "scale": make_scales(308, 308),
        "bone": make_bone(308, 436),
        "claw": make_claws(308, 172),
    }
    for name, (x0, y0, x1, y1) in CELLS.items():
        if name == "solid":
            ImageDraw.Draw(atlas).rectangle([x0, y0, x1 - 1, y1 - 1],
                                            fill=(96, 100, 110, 255))
            continue
        im = parts[name].convert("RGBA")
        im = im.resize((x1 - x0, y1 - y0), Image.LANCZOS)
        atlas.alpha_composite(im, (x0, y0))
    atlas.save(ART / "dragon_atlas.png")
    atlas.resize((512, 512), Image.LANCZOS).save(ART / "dragon_atlas_view.png")
    (ART / "dragon_atlas_rects.json").write_text(json.dumps(CELLS, indent=1))
    return atlas


def uv(name, u, v):
    x0, y0, x1, y1 = CELLS[name]
    pad = 2
    return (x0 + pad + u * (x1 - x0 - 2 * pad),
            y0 + pad + v * (y1 - y0 - 2 * pad))


# ------------------------------------------------------------------ membrane

def crease_quads():
    quads = []
    for u in (0.28, 0.62):
        pts = []
        for j in range(6):
            s = 0.10 + 0.82 * j / 5
            p = membrane_point(s, u)
            pts.append((p[0], p[1], p[2] + 0.025))
        quads += ridge(pts, 0.045, (0.38, 0.40, 0.49))
    return quads


def membrane_quads(nu=56, ns=14):
    quads = []
    front, back = [], []
    for j in range(ns + 1):
        s = j / ns
        rowf, rowb = [], []
        for i in range(nu + 1):
            u = i / nu
            p = membrane_point(s, u)
            rowf.append(p)
            rowb.append((p[0], p[1], p[2] - 0.17))
        front.append(rowf)
        back.append(rowb)
    for j in range(ns):
        for i in range(nu):
            u0, u1 = i / nu, (i + 1) / nu
            v0, v1 = j / ns, (j + 1) / ns
            f = [front[j][i], front[j][i + 1], front[j + 1][i + 1], front[j + 1][i]]
            b = [back[j][i], back[j + 1][i], back[j + 1][i + 1], back[j][i + 1]]
            uvf = [uv("membrane", u0, v0), uv("membrane", u1, v0),
                   uv("membrane", u1, v1), uv("membrane", u0, v1)]
            quads.append((f, uvf, A6_TINTS["membrane"]))
            quads.append((b, uvf, (0.42, 0.44, 0.52)))
    # thickness rim along the trailing/body boundary
    for i in range(nu):
        p0 = front[ns][i]
        p1 = front[ns][i + 1]
        q0 = back[ns][i]
        q1 = back[ns][i + 1]
        u0, u1 = i / nu, (i + 1) / nu
        quads.append(([p0, q0, q1, p1],
                      [uv("membrane", u0, 0.99), uv("scale", u0, 0.1),
                       uv("scale", u1, 0.1), uv("membrane", u1, 0.99)],
                      (0.45, 0.47, 0.55)))
    # jagged sawtooth fins along the outer trailing edge
    fin_start = 17
    for i in range(fin_start, len(BOUNDARY) - 1, 2):
        a = BOUNDARY[i]
        b = BOUNDARY[i + 1]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy) or 1.0
        nx, ny = dy / ln, -dx / ln
        mx, my = (a[0] + b[0]) * 0.5, (a[1] + b[1]) * 0.5
        if nx * (mx - W[0]) + ny * (my - W[1]) < 0:
            nx, ny = -nx, -ny
        grow = (i - fin_start) / max(1, len(BOUNDARY) - fin_start - 2)
        hgt = 0.70 + 1.10 * grow * grow
        p0 = (mx - dx / ln * 0.55 + nx * 0.02, my - dy / ln * 0.55 + ny * 0.02, a[2])
        p1 = (mx + dx / ln * 0.55 + nx * 0.02, my + dy / ln * 0.55 + ny * 0.02, b[2])
        tip = (mx + nx * hgt, my + ny * hgt, (a[2] + b[2]) * 0.5 - 0.02)
        quads.append(([p0, p1, tip],
                      [uv("membrane", 0.2, 0.85), uv("membrane", 0.8, 0.85),
                       uv("membrane", 0.5, 0.98)], (0.55, 0.57, 0.65)))
        quads.append(([p1, p0, tip],
                      [uv("membrane", 0.8, 0.85), uv("membrane", 0.2, 0.85),
                       uv("membrane", 0.5, 0.98)], (0.36, 0.38, 0.46)))
    return quads


# ------------------------------------------------------------------ bones

GAME_LOD = 1.0


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


def ridge(pts, width, tint):
    """Flat highlight ribbon along a bone path."""
    out = []
    for i in range(len(pts) - 1):
        p0, p1 = pts[i], pts[i + 1]
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        ln = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / ln, dx / ln
        w = width * 0.5
        a = (p0[0] + nx * w, p0[1] + ny * w, p0[2] + 0.02)
        b = (p0[0] - nx * w, p0[1] - ny * w, p0[2] + 0.02)
        c = (p1[0] - nx * w, p1[1] - ny * w, p1[2] + 0.02)
        d = (p1[0] + nx * w, p1[1] + ny * w, p1[2] + 0.02)
        out.append(([a, b, c, d],
                    [uv("bone", 0.1, 0.2), uv("bone", 0.9, 0.2),
                     uv("bone", 0.9, 0.8), uv("bone", 0.1, 0.8)], tint))
    return out


def tube(path, r0, r1, tex, tint, sides=8, n=16, bulge=(),
         bulge_amt=0.22, cap_start=False, highlight=False):
    pts = resample3(path, n)
    if GAME_LOD < 1.0:
        keep = max(3, int(round(len(pts) * GAME_LOD)))
        idx = np.linspace(0, len(pts) - 1, keep).round().astype(int)
        pts = [pts[i] for i in idx]
        sides = max(5, int(round(sides * 0.75)))
    rings = []
    for i, p in enumerate(pts):
        t = i / (len(pts) - 1)
        a = pts[max(0, i - 1)]
        b = pts[min(len(pts) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / ln, dx / ln
        r = (r0 + (r1 - r0) * t) ** 1.0
        for bt in bulge:
            r *= 1 + bulge_amt * math.exp(-((t - bt) / 0.045) ** 2)
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
            q = [ra[k], ra[k2], rb[k2], rb[k]]
            u0, u1 = k / sides, (k + 1) / sides
            quads.append((q, [uv(tex, u0, ta), uv(tex, u1, ta),
                             uv(tex, u1, tb), uv(tex, u0, tb)], tint))
    if highlight:
        hpath = [(p[0], p[1], p[2] + max(0.04, 0.17)) for p in pts]
        quads += ridge(pts, 0.18, (0.78, 0.79, 0.84))
    return quads


def cone(base, tip, r, tex, tint, sides=5):
    path = [(base[0], base[1], base[2]), (tip[0], tip[1], tip[2])]
    pts = resample3(path, 4)
    dx, dy = tip[0] - base[0], tip[1] - base[1]
    ln = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / ln, dx / ln
    rings = []
    for i, p in enumerate(pts):
        t = i / (len(pts) - 1)
        rr = r * (1 - t) + 0.015
        ring = []
        for k in range(sides):
            th = 2 * math.pi * k / sides
            ring.append((p[0] + nx * rr * math.cos(th),
                         p[1] + ny * rr * math.cos(th),
                         p[2] + rr * math.sin(th)))
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


def path2(pts, zfun):
    return [(p[0], p[1], zfun(p[0], p[1])) for p in pts]


def finger_path(tip, bend=0.0):
    mid = ((W[0] + tip[0]) * 0.5, (W[1] + tip[1]) * 0.5)
    mx, my = mid[0] + (W[1] - tip[1]) * bend, mid[1] - (W[0] - tip[0]) * bend
    pts = bezier(W, tip, (mx, my), 8)
    z_tip = Z_TIP if False else 0
    return [(p[0], p[1], Z_W + (0 - Z_W) * 0.0) for p in pts]


def rib(path2d, tip_z):
    pts = []
    for i, (x, y) in enumerate(path2d):
        t = i / (len(path2d) - 1)
        z = Z_W + (tip_z - Z_W) * t
        pts.append((x, y, z + 0.24))
    return pts


def bone_quads():
    quads = []
    # arm: shoulder -> wrist (thick, straight)
    arm = [(S[0], S[1], Z_S + 0.12), (E[0], E[1], (Z_S + Z_W) / 2 + 0.15),
           (W[0], W[1], Z_W + 0.12)]
    quads += tube(arm, 1.55, 1.05, "bone", A6_TINTS["bone"], sides=8, n=12,
                  bulge=(0.12, 0.55, 0.96), bulge_amt=0.36, highlight=True)
    quads += tube([(S[0] - 0.1, S[1] - 0.1, Z_S + 0.12),
                   (S[0] + 0.25, S[1] + 0.35, Z_S + 0.12)],
                  0.82, 0.72, "scale", (0.55, 0.57, 0.64), sides=8, n=6)
    # shoulder bone cap
    quads += tube([(S[0] - 0.35, S[1] - 0.35, Z_S + 0.12),
                   (S[0] + 0.45, S[1] + 0.45, Z_S + 0.12)],
                  0.98, 0.82, "bone", (0.45, 0.47, 0.52), sides=8, n=6)
    quads += ridge([(S[0] - 0.15, S[1] - 0.1, Z_S + 0.65),
                    (S[0] + 0.3, S[1] + 0.35, Z_S + 0.65)], 0.09, (0.60, 0.61, 0.65))
    # wrist carpal cluster (big hand block)
    quads += tube([(W[0] - 0.55, W[1] - 0.2, Z_W + 0.12),
                   (W[0] + 0.55, W[1] + 0.18, Z_W + 0.12)],
                  1.15, 0.95, "bone", A6_TINTS["bone_hi"], sides=8, n=6,
                  bulge=(0.3, 0.7), bulge_amt=0.18)
    # main thumb hook: thick and curled inward over the head
    thumb = [(W[0] - 0.05, W[1] + 0.25, Z_W + 0.45),
             (W[0] - 0.12, W[1] + 1.10, Z_W + 0.52),
             (W[0] - 0.45, W[1] + 1.85, Z_W + 0.48),
             (W[0] - 1.05, W[1] + 2.30, Z_W + 0.36),
             (W[0] - 1.70, W[1] + 2.55, Z_W + 0.28)]
    quads += tube(thumb, 0.46, 0.04, "claw", A6_TINTS["claw"], sides=6, n=14,
                  bulge=(0.28,), bulge_amt=0.25)
    # two knuckle prongs on the outer wrist
    for ang, ln in ((-0.25, 1.35), (0.30, 1.10)):
        b = (W[0] + 0.5, W[1] + 0.75, Z_W + 0.55)
        quads += tube([b, (b[0] + math.sin(ang) * ln, b[1] + math.cos(ang) * ln,
                           Z_W + 0.85)],
                      0.26, 0.03, "claw", A6_TINTS["claw"], sides=5, n=6)

    # four fingers
    for idx, tip in TIPS.items():
        if idx == 1:
            pts2 = [f1_point(i / 12) for i in range(13)]
        else:
            bend = {2: -0.06, 3: 0.06, 4: 0.09}[idx]
            mid = ((W[0] + tip[0]) * 0.5, (W[1] + tip[1]) * 0.5)
            mx = mid[0] + (W[1] - tip[1]) * bend
            my = mid[1] - (W[0] - tip[0]) * bend
            pts2 = bezier(W, tip, (mx, my), 9)
        zt = Z_TIP[idx] + 0.10
        path = rib(pts2, zt)
        r0 = 1.05 if idx != 1 else 1.12
        quads += tube(path, r0, 0.34, "bone", A6_TINTS["bone"], sides=6, n=12,
                      bulge=(0.26, 0.56, 0.82), bulge_amt=0.55, highlight=True)
        # knuckle rings
        quads += ridge(path, 0.14, (0.62, 0.63, 0.68))
        # curved claw at the tip
        dx, dy = tip[0] - W[0], tip[1] - W[1]
        ln = math.hypot(dx, dy) or 1
        ux, uy = dx / ln, dy / ln
        px, py = -uy, ux
        if py > 0:
            px, py = -px, -py
        ln_claw = 1.25 + 0.10 * (idx - 1)
        base = (tip[0], tip[1], zt + 0.02)
        mid = (tip[0] + ux * ln_claw * 0.55 + px * 0.10,
               tip[1] + uy * ln_claw * 0.55 + py * 0.10, zt + 0.10)
        end = (tip[0] + ux * ln_claw + px * 0.32,
               tip[1] + uy * ln_claw + py * 0.32, zt + 0.03)
        quads += tube([base, mid, end], 0.32, 0.02, "claw", A6_TINTS["claw"],
                      sides=6, n=8)
    # outer wing spikes along the curved F1
    for t, ln, tilt in ((0.14, 2.20, 0.70), (0.30, 2.00, 0.55), (0.46, 1.70, 0.62),
                        (0.62, 1.45, 0.48), (0.78, 1.10, 0.56)):
        x, y = f1_point(t)
        z = Z_W + (Z_TIP[1] - Z_W) * t + 0.26
        quads += cone((x, y, z), (x + ln * 0.82, y - ln * tilt, z + 0.05),
                      0.42, "scale", A6_TINTS["spike"], sides=5)
    return quads


# --------------------------------------------------------------- scales/plates

def scale_plates():
    quads = []
    # overlapping armour plates along the arm
    for i in range(6):
        t = 0.06 + i * 0.16
        x = S[0] + (W[0] - S[0]) * t
        y = S[1] + (W[1] - S[1]) * t
        z = (Z_S + (Z_W - Z_S) * t) + 0.48
        w = 1.55 + 0.20 * math.sin(i)
        h = 1.85
        ang = math.atan2(W[1] - S[1], W[0] - S[0])
        nx, ny = -math.sin(ang), math.cos(ang)
        dx, dy = math.cos(ang), math.sin(ang)
        verts = [(x - nx * w * 0.5, y - ny * w * 0.5, z - 0.08),
                 (x + nx * w * 0.5, y + ny * w * 0.5, z - 0.08),
                 (x + nx * w * 0.3 + dx * h, y + ny * w * 0.3 + dy * h, z + 0.10),
                 (x - nx * w * 0.3 + dx * h, y - ny * w * 0.3 + dy * h, z + 0.10)]
        quads.append((verts, [uv("scale", 0.1, 0.1), uv("scale", 0.9, 0.1),
                              uv("scale", 0.9, 0.9), uv("scale", 0.1, 0.9)],
                      (0.52, 0.54, 0.62)))
    # shoulder plate cluster
    for i, (dx, dy, w, h) in enumerate(((-0.35, 0.02, 2.5, 2.0), (0.55, 0.5, 2.0, 1.7),
                                       (0.2, 1.15, 1.5, 1.3))):
        p = (S[0] + dx, S[1] + dy, Z_S + 0.48 + i * 0.03)
        quads.append(([(p[0] - w * 0.5, p[1] - h * 0.2, p[2]),
                       (p[0] + w * 0.5, p[1] - h * 0.2, p[2]),
                       (p[0] + w * 0.25, p[1] + h * 0.8, p[2] + 0.10),
                       (p[0] - w * 0.25, p[1] + h * 0.8, p[2] + 0.10)],
                      [uv("scale", 0.1, 0.1), uv("scale", 0.9, 0.1),
                       uv("scale", 0.9, 0.9), uv("scale", 0.1, 0.9)],
                      (0.50, 0.52, 0.60)))
    # pauldron horn
    quads += cone((S[0] + 0.15, S[1] + 0.85, Z_S + 0.55),
                  (S[0] + 0.95, S[1] + 2.05, Z_S + 0.70),
                  0.36, "scale", A6_TINTS["spike"], sides=5)
    # jagged crest along the leading arm
    for i in range(3):
        t = 0.32 + i * 0.20
        x = S[0] + (W[0] - S[0]) * t
        y = S[1] + (W[1] - S[1]) * t
        z = Z_S + (Z_W - Z_S) * t + 0.45
        quads += cone((x, y, z), (x + 1.40, y - 0.10, z + 0.12),
                      0.32, "scale", A6_TINTS["spike"], sides=5)
    # wrist scale spike cluster
    for i in range(3):
        p = (W[0] - 0.45 + i * 0.45, W[1] + 0.30 + i * 0.18, Z_W + 0.50)

        quads.append(([(p[0] - 0.65, p[1] - 0.2, p[2]),
                       (p[0] + 0.65, p[1] - 0.2, p[2]),
                       (p[0] + 0.15, p[1] + 1.15, p[2] + 0.12),
                       (p[0] - 0.35, p[1] + 0.85, p[2] + 0.12)],
                      [uv("scale", 0.1, 0.1), uv("scale", 0.9, 0.1),
                       uv("scale", 0.9, 0.9), uv("scale", 0.1, 0.9)],
                      (0.55, 0.57, 0.64)))
    return quads


# ------------------------------------------------------------------ build

def leading_bands():
    quads = []

    def band(path2d, tipz, width):
        pts = []
        for i, (x, y) in enumerate(path2d):
            t = i / (len(path2d) - 1)
            pts.append((x, y, Z_W + (tipz - Z_W) * t))
        for i in range(len(pts) - 1):
            p0, p1 = pts[i], pts[i + 1]
            dx, dy = p1[0] - p0[0], p1[1] - p0[1]
            ln = math.hypot(dx, dy) or 1.0
            nx, ny = dy / ln, -dx / ln
            if nx > 0:
                nx, ny = -nx, -ny
            a = (p0[0] + nx * 0.1, p0[1] + ny * 0.1, p0[2] + 0.12)
            b = (p0[0] + nx * width, p0[1] + ny * width, p0[2] + 0.10)
            c = (p1[0] + nx * width, p1[1] + ny * width, p1[2] + 0.10)
            d = (p1[0] + nx * 0.1, p1[1] + ny * 0.1, p1[2] + 0.12)
            u0 = 0.1 + 0.8 * i / (len(pts) - 1)
            u1 = 0.1 + 0.8 * (i + 1) / (len(pts) - 1)
            quads.append(([a, b, c, d],
                          [uv("scale", 0.15, u0), uv("scale", 0.85, u0),
                           uv("scale", 0.85, u1), uv("scale", 0.15, u1)],
                          (0.60, 0.63, 0.72)))

    f1 = [f1_point(i / 10) for i in range(11)]
    band(f1, Z_TIP[1], 0.85)
    # scale plates along the leading bands
    for i in range(4):
        t = 0.18 + i * 0.18
        x, y = f1_point(t)
        z = Z_W + (Z_TIP[1] - Z_W) * t + 0.26
        quads.append(([(x - 0.55, y - 0.15, z), (x + 0.25, y - 0.45, z),
                       (x + 0.45, y + 0.55, z + 0.10), (x - 0.30, y + 0.35, z + 0.10)],
                      [uv("scale", 0.1, 0.1), uv("scale", 0.9, 0.1),
                       uv("scale", 0.9, 0.9), uv("scale", 0.1, 0.9)],
                      (0.55, 0.57, 0.65)))
    return quads


def build_model():
    quads = []
    for side in (1, -1):
        for verts, uvs, tint, *rest in (membrane_quads() + bone_quads() + scale_plates() + leading_bands()):
            quads.append(([(side * x, y, z) for x, y, z in verts], uvs, tint,
                          "bone" if rest and rest[0] == "bone" else "part"))
    return quads


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


def render_sheet(atlas, quads, path, with_body=True):
    tex = np.asarray(atlas.convert("RGBA"), float)
    v, f, u, c = to_arrays(quads)
    if with_body:
        pv, pf, pu, pc = proxy_boxes()
        allv = np.vstack([pv, v])
        allf = np.array(pf + [(a + len(pv), b + len(pv), c + len(pv)) for a, b, c in f],
                        np.int64)
        allu = np.vstack([pu, u])
        allc = np.vstack([pc, c])
    else:
        allv, allf, allu, allc = v, f, u, c
    size = 780
    views = [("back", np.eye(3)),
             ("3/4 back", rm.rot_y(-28) @ rm.rot_x(-6)),
             ("side", rm.rot_y(-76)),
             ("back low", rm.rot_x(10))]
    sheet = Image.new("RGB", (size * 2, (size + 26) * 2), (28, 30, 38))
    d = ImageDraw.Draw(sheet)
    bg = np.zeros((size, size, 3), np.float64)
    yy = np.linspace(0, 1, size)[:, None, None]
    bg[:] = np.array([190, 194, 226]) * (1 - yy) + np.array([112, 116, 160]) * yy
    for i, (label, R) in enumerate(views):
        rgba = rm.render_view(allv, allf, allu, tex, R, size, alpha=True,
                              shade_lo=0.82, shade_hi=0.40, colors=allc)
        base = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
        base.alpha_composite(Image.fromarray(rgba, "RGBA"))
        img = np.asarray(base.convert("RGB"))
        x, y = (i % 2) * size, (i // 2) * (size + 26)
        sheet.paste(Image.fromarray(img), (x, y + 26))
        d.text((x + 10, y + 7), f"Dragon wing v1 - {label}", fill=(230, 226, 214))
    sheet.save(path)
    return sheet


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
                          shade_lo=0.82, shade_hi=0.40, colors=allc)
    bg = np.zeros((size, size, 3), np.float64)
    yy = np.linspace(0, 1, size)[:, None, None]
    bg[:] = np.array([190, 194, 226]) * (1 - yy) + np.array([112, 116, 160]) * yy
    base = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    base.alpha_composite(Image.fromarray(rgba, "RGBA"))
    return base.convert("RGB")


def render_compare(atlas, quads):
    ref = Image.open(OUT / "dragon_ref_f063_big.png").convert("RGB")
    new = render_single(atlas, quads, size=900, with_body=True)
    h = 760
    pad = 14
    ref_img = ref.resize((int(ref.width * h / ref.height), h), Image.LANCZOS)
    new_img = new.resize((int(new.width * h / new.height), h), Image.LANCZOS)
    sheet = Image.new("RGB", (ref_img.width + new_img.width + pad * 3, h + 70),
                      (24, 26, 33))
    sheet.paste(ref_img, (pad, 52))
    sheet.paste(new_img, (pad * 2 + ref_img.width, 52))
    d = ImageDraw.Draw(sheet)
    d.text((pad + 2, 22), "LUNAR REFERENCE - Dragon Wings (Black)", fill=(220, 214, 200))
    d.text((pad * 2 + ref_img.width + 2, 22), "NEW - skeletal dragon wing (back view)",
           fill=(220, 214, 200))
    sheet.save(OUT / "dragon_v1_compare.png")
    return sheet


def fold_quads(quads, fold):
    """Light idle flutter: small root lift + wrist swing, no deep fold."""
    s_z = Z_S + 0.10
    phi = math.radians(-4.5 * fold)
    c_phi, s_phi = math.cos(phi), math.sin(phi)
    th = math.radians(-1.5 * fold)
    c_th, s_th = math.cos(th), math.sin(th)
    fdx, fdy = TIPS[1][0] - W[0], TIPS[1][1] - W[1]
    flen = fdx * fdx + fdy * fdy
    wx0, wy0 = W[0] - S[0], W[1] - S[1]
    wpx = S[0] + wx0 * c_phi - wy0 * s_phi
    wpy = S[1] + wx0 * s_phi + wy0 * c_phi
    out = []
    for verts, uvs, tint, *rest in quads:
        nv = []
        for x, y, z in verts:
            side = 1.0 if x >= 0 else -1.0
            ax = abs(x)
            t = ((ax - W[0]) * fdx + (y - W[1]) * fdy) / flen
            t = min(1.0, max(0.0, t))
            dx, dy = ax - S[0], y - S[1]
            rx = S[0] + dx * c_phi - dy * s_phi
            ry = S[1] + dx * s_phi + dy * c_phi
            wphi = math.radians(-5.0 * fold * t)
            cw, sw = math.cos(wphi), math.sin(wphi)
            hx, hy = rx - wpx, ry - wpy
            hx2 = wpx + hx * cw - hy * sw
            hy2 = wpy + hx * sw + hy * cw
            dxr = hx2 - S[0]
            dz = z - s_z
            x3 = S[0] + dxr * c_th + dz * s_th
            z3 = s_z - dxr * s_th + dz * c_th
            nv.append((x3 * side, hy2, z3))
        out.append((nv, uvs, tint, *rest))
    return out


def render_anim(atlas, quads):
    phases = [math.sin(2 * math.pi * i / 8) for i in range(8)]
    size = 600
    sheet = Image.new("RGB", (size * 4, (size + 24) * 2), (28, 30, 38))
    d = ImageDraw.Draw(sheet)
    for i, fold in enumerate(phases):
        img = render_single(atlas, fold_quads(quads, fold), size=size, with_body=True)
        x, y = (i % 4) * size, (i // 4) * (size + 24)
        sheet.paste(img, (x, y + 24))
        d.text((x + 10, y + 6), f"idle flutter {fold:.2f}", fill=(230, 226, 214))
    sheet.save(OUT / "dragon_anim_fold.png")
    frames = []
    n = 30
    for i in range(n):
        fold = math.sin(2 * math.pi * i / n)
        frames.append(render_single(atlas, fold_quads(quads, fold), size=320,
                                    with_body=True))
    frames[0].save(OUT / "dragon_anim.gif", save_all=True,
                   append_images=frames[1:], duration=110, loop=0)
    print("saved", OUT / "dragon_anim_fold.png", OUT / "dragon_anim.gif")


def main():
    OUT.mkdir(exist_ok=True)
    atlas = build_atlas()
    quads = build_model()
    print("quads", len(quads))
    render_sheet(atlas, quads, OUT / "dragon_v1_preview.png", with_body=True)
    render_sheet(atlas, quads, OUT / "dragon_v1_clean.png", with_body=False)
    render_compare(atlas, quads)
    print("saved", OUT / "dragon_v1_preview.png")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "anim":
        OUT.mkdir(exist_ok=True)
        _atlas = build_atlas()
        _quads = build_model()
        render_anim(_atlas, _quads)
    else:
        main()
