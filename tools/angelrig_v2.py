"""Angel wing v5 - 3D armature + volumetric feathers, matched to the approved
2D silhouette (art-wings/angel/angel_v3_wing.png).

Local wing space (right wing): x outboard, y up, z toward the viewer (back).
The approved art maps to local x 0..23.35 (outboard from the body) and
y +11.6..-19.6. Feather tips are taken from the art's alpha boundary so the
silhouette matches exactly; depth comes from 5 z-layers plus curved vanes.
"""
import json
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

WING_ART = ART / "angel_v3_wing.png"
X_OUT = 23.35
Y_TOP, Y_BOT = 11.6, -19.6

# ── skeleton (right wing, local) ─────────────────────────────────────────
SHOULDER = (0.5, -4.4, 0.20)
ELBOW = (3.4, -1.0, 0.30)
WRIST = (6.6, 3.2, 0.40)
HAND = (9.2, 6.4, 0.45)
JOINTS = [("shoulder", SHOULDER, 0.34), ("elbow", ELBOW, 0.25),
          ("wrist", WRIST, 0.19), ("hand", HAND, 0.13)]

# ── palette ──────────────────────────────────────────────────────────────
FRONT = (0.975, 0.985, 1.00)
FRONT_SHADE = (0.93, 0.955, 1.00)
BACK = (0.60, 0.67, 0.82)
EDGE = (0.85, 0.89, 0.97)
SHAFT = (0.83, 0.87, 0.96)
BONE = (0.93, 0.90, 0.82)
GOLD = (0.94, 0.74, 0.34)
UNDER = (0.33, 0.39, 0.55)


def mirror(p):
    return (-p[0], p[1], p[2])


# ── primitives ───────────────────────────────────────────────────────────
def tube(a, b, r0, r1, sides=6, segs=3, tint=BONE):
    quads = []
    dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length < 1e-6:
        return quads
    ux, uy, uz = dx / length, dy / length, dz / length
    rx, ry, rz = (1.0, 0.0, 0.0) if abs(uz) > 0.9 else (0.0, 0.0, 1.0)
    tx, ty, tz = uy * rz - uz * ry, uz * rx - ux * rz, ux * ry - uy * rx
    tl = math.sqrt(tx * tx + ty * ty + tz * tz) or 1.0
    tx, ty, tz = tx / tl, ty / tl, tz / tl
    nx, ny, nz = ty * uz - tz * uy, tz * ux - tx * uz, tx * uy - ty * ux
    rings = []
    for j in range(segs + 1):
        t = j / segs
        px, py, pz = a[0] + dx * t, a[1] + dy * t, a[2] + dz * t
        bulge = 1.0 + 0.10 * math.sin(math.pi * t)
        r = (r0 + (r1 - r0) * t) * bulge
        ring = []
        for i in range(sides):
            ang = 2 * math.pi * i / sides
            ca, sa = math.cos(ang), math.sin(ang)
            ring.append((px + r * (nx * ca + tx * sa),
                         py + r * (ny * ca + ty * sa),
                         pz + r * (nz * ca + tz * sa)))
        rings.append(ring)
    for j in range(segs):
        for i in range(sides):
            i2 = (i + 1) % sides
            quads.append(([rings[j][i], rings[j][i2], rings[j + 1][i2], rings[j + 1][i]],
                          None, tint))
    return quads


def ball(c, r, tint=GOLD, sides=7, rings=4):
    quads = []
    for j in range(rings):
        v0, v1 = math.pi * j / rings, math.pi * (j + 1) / rings
        for i in range(sides):
            a0, a1 = 2 * math.pi * i / sides, 2 * math.pi * (i + 1) / sides
            pts = [(c[0] + r * math.sin(v) * math.cos(aa),
                    c[1] + r * math.cos(v),
                    c[2] + r * math.sin(v) * math.sin(aa))
                   for v, aa in ((v0, a0), (v0, a1), (v1, a1), (v1, a0))]
            quads.append((pts, None, tint))
    return quads


def feather(root, tip, width, bow=0.0, z0=0.4, z1=0.1, zbulge=0.06,
            thick=0.09, rounded=False, segs=4, front=FRONT, back=BACK,
            edge=EDGE, shaft=SHAFT, tint=1.0):
    """Curved volumetric feather from root to tip.

    bow: perpendicular offset of the bezier control point (+ lifts the feather
    toward its left side, i.e. counter-clockwise of the root->tip direction).
    """
    rx, ry = root[0], root[1]
    tx, ty = tip[0], tip[1]
    dxs, dys = tx - rx, ty - ry
    length = math.hypot(dxs, dys)
    if length < 1e-6:
        return []
    ux, uy = dxs / length, dys / length
    nx, ny = -uy, ux
    cx = (rx + tx) * 0.5 + nx * bow
    cy = (ry + ty) * 0.5 + ny * bow

    ts = [i / segs for i in range(segs + 1)]
    widths = [(t ** 0.38) * ((1.0 - t) ** 0.48) for t in ts]
    peak = max(widths) or 1.0
    widths = [w / peak * width for w in widths]
    if rounded:
        widths[-1] = max(widths[-1], 0.55 * width)
    else:
        widths[-1] = 0.05

    spine, left, right, ridge, backl = [], [], [], [], []
    for k, t in enumerate(ts):
        u = 1.0 - t
        px = u * u * rx + 2 * u * t * cx + t * t * tx
        py = u * u * ry + 2 * u * t * cy + t * t * ty
        # tangent of the quadratic bezier
        mx = 2 * u * (cx - rx) + 2 * t * (tx - cx)
        my = 2 * u * (cy - ry) + 2 * t * (ty - cy)
        ml = math.hypot(mx, my) or 1.0
        sx, sy = -my / ml, mx / ml
        zc = z0 + (z1 - z0) * t + zbulge * math.sin(math.pi * t)
        w = widths[k]
        spine.append((px, py, zc))
        left.append((px + sx * w, py + sy * w, zc - 0.055 * w))
        right.append((px - sx * w, py - sy * w, zc - 0.055 * w))
        ridge.append((px, py, zc + (0.07 if rounded else 0.15) * w))
        backl.append((px, py, zc - thick))
    quads = []
    f = tuple(c * tint for c in front)
    f2 = tuple(c * tint * 0.97 for c in FRONT_SHADE)
    b = tuple(c * tint for c in back)
    e = tuple(c * tint for c in edge)
    sh = tuple(c * tint for c in shaft)
    for k in range(len(ts) - 1):
        quads.append(([left[k], left[k + 1], ridge[k + 1], ridge[k]], None, f))
        quads.append(([ridge[k], ridge[k + 1], right[k + 1], right[k]], None, f2))
        quads.append(([left[k], backl[k], backl[k + 1], left[k + 1]], None, b))
        quads.append(([backl[k], right[k], right[k + 1], backl[k + 1]], None, b))
        quads.append(([left[k], left[k + 1], backl[k + 1], backl[k]], None, e))
        quads.append(([right[k], backl[k], backl[k + 1], right[k + 1]], None, e))
    # quill ridge, a hair darker
    for k in range(len(ts) - 1):
        p0, p1 = spine[k], spine[k + 1]

        def mix(kk, a, b):
            return (a[kk][0] + (b[kk][0] - a[kk][0]) * 0.45,
                    a[kk][1] + (b[kk][1] - a[kk][1]) * 0.45)
        m0 = mix(k, left, right)
        m1 = mix(k + 1, left, right)
        n0 = (m0[0] * 0.1 + spine[k][0] * 0.9, m0[1] * 0.1 + spine[k][1] * 0.9)
        n1 = (m1[0] * 0.1 + spine[k + 1][0] * 0.9, m1[1] * 0.1 + spine[k + 1][1] * 0.9)
        h0 = (0.08 if rounded else 0.165) * widths[k]
        h1 = (0.08 if rounded else 0.165) * widths[k + 1]
        quads.append(([(m0[0], m0[1], p0[2] + h0),
                       (n0[0], n0[1], p0[2] + h0),
                       (n1[0], n1[1], p1[2] + h1),
                       (m1[0], m1[1], p1[2] + h1)], None, sh))
    if rounded:
        # rounded cap over the last ring
        p = spine[-1]
        mxx = 2 * (tx - cx)
        myy = 2 * (ty - cy)
        ml = math.hypot(mxx, myy) or 1.0
        tipx = p[0] + mxx / ml * widths[-1] * 0.55
        tipy = p[1] + myy / ml * widths[-1] * 0.55
        tq = (tipx, tipy, p[2] - 0.02)
        quads.append(([left[-1], right[-1], tq, tq], None, f))
        quads.append(([right[-1], backl[-1], tq, tq], None, e))
        quads.append(([backl[-1], left[-1], tq, tq], None, e))
    return quads


# ── feather layout (right wing) ──────────────────────────────────────────
def leading_fan():
    """Long feathers from the covert cap out along the top/outer edge."""
    tips = [(7.0, 11.6), (8.6, 10.2), (10.8, 9.6), (13.5, 7.6), (16.3, 5.6),
            (18.3, 3.7), (20.1, 1.7), (20.9, -0.3), (22.0, -2.3), (22.8, -4.3),
            (23.35, -6.3), (23.35, -8.3)]
    roots = [(6.2, 6.8), (6.6, 6.4), (6.9, 5.9), (7.2, 5.4), (7.5, 4.9),
             (7.8, 4.4), (8.0, 3.9), (8.2, 3.4), (8.4, 2.9), (8.5, 2.4),
             (8.6, 1.9), (8.6, 1.4)]
    widths = [1.25, 1.2, 1.3, 1.45, 1.6, 1.7, 1.8, 1.85, 1.9, 1.9, 1.85, 1.8]
    out = []
    for i, (r, t, w) in enumerate(zip(roots, tips, widths)):
        out.append(dict(root=r, tip=t, width=w, bow=0.18 + 0.04 * i,
                        z0=0.50 + 0.012 * i, z1=0.28 + 0.010 * i,
                        zbulge=0.05, thick=0.10, rounded=False,
                        tag="finger", tint=0.985 - 0.004 * i))
    return out


def primary_fan():
    tips = [(22.3, -13.1), (21.4, -15.9), (20.45, -18.5), (17.5, -19.2),
            (14.62, -19.25), (12.4, -18.4), (10.51, -17.2), (9.0, -15.9),
            (7.85, -14.3), (6.6, -12.9), (5.46, -11.4), (4.7, -9.7),
            (4.02, -7.97)]
    roots = [(9.2, 0.7), (8.9, 0.2), (8.6, -0.3), (8.2, -0.9), (7.8, -1.5),
             (7.3, -2.0), (6.8, -2.5), (6.3, -2.9), (5.8, -3.2), (5.3, -3.4),
             (4.9, -3.5), (4.6, -3.6), (4.4, -3.7)]
    widths = [1.75, 1.9, 2.0, 2.0, 1.95, 1.85, 1.75, 1.65, 1.55, 1.45, 1.35, 1.25, 1.15]
    out = []
    for i, (r, t, w) in enumerate(zip(roots, tips, widths)):
        out.append(dict(root=r, tip=t, width=w, bow=-0.5 - 0.25 * math.sin(math.pi * i / 12),
                        z0=0.44 - 0.006 * i, z1=0.10, zbulge=0.05, thick=0.11,
                        rounded=False, tag="hand", tint=0.945 - 0.008 * i))
    return out


def inner_tertials():
    data = [((4.9, 3.0), (2.8, 0.7), 1.1, 0.55),
            ((5.2, 1.2), (3.1, -2.3), 1.2, 0.53),
            ((5.4, -0.3), (4.6, -4.3), 1.2, 0.51),
            ((5.2, -1.8), (4.1, -6.3), 1.1, 0.48),
            ((5.0, -3.0), (4.0, -8.0), 1.0, 0.45)]
    out = []
    for i, (r, t, w, z) in enumerate(data):
        out.append(dict(root=r, tip=t, width=w, bow=0.15, z0=z, z1=z - 0.06,
                        zbulge=0.02, thick=0.09, rounded=(i < 2),
                        tag="radius", tint=0.92))
    return out


def covert_cap():
    """Five shingled rows of short rounded coverts over the inner-top cap."""
    rows = [
        ([(0.9, 8.0), (2.2, 8.5), (3.5, 8.4), (4.7, 7.8), (5.7, 6.9)],
         [(1.3, 10.3), (2.8, 10.9), (4.4, 10.7), (5.8, 9.9), (6.8, 8.6)],
         1.12),
        ([(0.4, 6.2), (1.7, 6.8), (3.1, 6.9), (4.5, 6.3), (5.7, 5.4), (6.6, 4.3)],
         [(0.5, 8.5), (2.0, 9.2), (3.7, 9.1), (5.3, 8.3), (6.6, 7.2), (7.5, 5.8)],
         1.04),
        ([(0.2, 4.4), (1.4, 5.0), (2.8, 5.1), (4.2, 4.5), (5.4, 3.7),
          (6.5, 2.7), (7.4, 1.5)],
         [(0.3, 6.7), (1.8, 7.4), (3.4, 7.3), (5.0, 6.5), (6.4, 5.3),
          (7.4, 3.9), (8.1, 2.3)],
         0.96),
        ([(0.5, 2.6), (1.7, 3.2), (3.1, 3.3), (4.5, 2.7), (5.7, 1.9),
          (6.8, 0.9), (7.6, -0.4)],
         [(0.7, 4.9), (2.2, 5.6), (3.8, 5.5), (5.4, 4.7), (6.8, 3.5),
          (7.8, 2.1), (8.4, 0.6)],
         0.88),
        ([(0.9, 0.9), (2.1, 1.5), (3.5, 1.6), (4.9, 1.0), (6.1, 0.2), (7.2, -0.9)],
         [(1.2, 3.2), (2.7, 3.9), (4.3, 3.8), (5.9, 3.0), (7.3, 1.8), (8.3, 0.3)],
         0.80),
    ]
    out = []
    for ri, (roots, tips, z) in enumerate(rows):
        for i, (r, t) in enumerate(zip(roots, tips)):
            out.append(dict(root=r, tip=t, width=0.92 + 0.06 * (ri == 0),
                            bow=0.12, z0=z, z1=z - 0.05, zbulge=0.05,
                            thick=0.10, rounded=True, tag="radius",
                            tint=1.0 - 0.012 * ri + 0.01 * (i % 2)))
    return out


def median_coverts():
    data = [((1.5, -0.2), (1.9, 1.8)), ((2.9, 0.0), (3.4, 2.1)),
            ((4.3, -0.4), (4.9, 1.8)), ((5.6, -1.0), (6.2, 1.0)),
            ((6.7, -1.9), (7.1, 0.1))]
    out = []
    for i, (r, t) in enumerate(data):
        out.append(dict(root=r, tip=t, width=0.95, bow=0.10, z0=0.72,
                        z1=0.66, zbulge=0.04, thick=0.09, rounded=True,
                        tag="radius", tint=0.95))
    return out


def all_feathers():
    return leading_fan() + primary_fan() + inner_tertials() + median_coverts() + covert_cap()


def feather_quads(side):
    quads = []
    for f in all_feathers():
        r, t = f["root"], f["tip"]
        if side < 0:
            r, t = (-r[0], r[1]), (-t[0], t[1])
        q = feather(r, t, f["width"], bow=f["bow"] * (1 if side > 0 else -1),
                    z0=f["z0"], z1=f["z1"], zbulge=f["zbulge"], thick=f["thick"],
                    rounded=f["rounded"], tint=f["tint"])
        for verts, _uv, tint in q:
            quads.append((verts, None, tint, f["tag"]))
    return quads


def bone_quads(side):
    def m(p):
        return p if side > 0 else mirror(p)

    out = []
    segs = [(SHOULDER, ELBOW, 0.32, 0.24, "humerus"),
            (ELBOW, WRIST, 0.24, 0.17, "radius"),
            (WRIST, HAND, 0.16, 0.09, "hand")]
    for a, b, r0, r1, tag in segs:
        out += [(v, None, t, tag) for v, _u, t in tube(m(a), m(b), r0, r1, segs=3)]
    for name, c, r in JOINTS:
        tag = "root" if name == "shoulder" else (
            "humerus" if name == "elbow" else ("radius" if name == "wrist" else "hand"))
        out += [(v, None, t, tag) for v, _u, t in ball(m(c), r)]
    return out


# ── underwing backing ────────────────────────────────────────────────────
def backing_quads(side):
    a = np.asarray(Image.open(WING_ART).convert("RGBA"))[:, :, 3]
    cell = 10
    quads = []
    for v0 in range(0, a.shape[0], cell):
        for u0 in range(0, a.shape[1], cell):
            u1, v1 = min(u0 + cell, a.shape[1]), min(v0 + cell, a.shape[0])
            block = a[v0:v1, u0:u1]
            if block.min() < 250:
                continue
            p = []
            for (u, v) in ((u0, v0), (u1, v0), (u1, v1), (u0, v1)):
                x = (500 - u) / 500 * X_OUT
                y = Y_TOP - v / a.shape[0] * (Y_TOP - Y_BOT)
                z = -0.12 + 0.10 * math.exp(-((x - 9.0) ** 2 / 80.0 + (y + 1.0) ** 2 / 120.0))
                if side < 0:
                    x = -x
                p.append((x + 0.0, y, z))
            shade = 0.92 + 0.05 * math.sin(v0 * 0.13)
            col = tuple(c * shade for c in UNDER)
            quads.append((p, None, col, "root"))
    return quads


# ── preview frame ────────────────────────────────────────────────────────
def world_quads(quads):
    out = []
    for verts4, uv, tint, *rest in quads:
        side = 1 if float(np.mean([p[0] for p in verts4])) >= 0 else -1
        w4 = [(p[0] + side * 1.55, p[1] + 27.0, p[2] + 2.6) for p in verts4]
        out.append((w4, uv, tint, *rest))
    return out


def to_arrays(quads):
    verts, faces, cols = [], [], []
    for q in quads:
        base = len(verts)
        for p in q[0]:
            verts.append([p[0], p[1], p[2]])
            cols.append(q[2])
        faces.append((base, base + 1, base + 2))
        faces.append((base, base + 2, base + 3))
    return (np.array(verts, float), np.array(faces, np.int64), np.array(cols, float))


WHITE = Image.new("RGBA", (16, 16), (255, 255, 255, 255))


def proxy_boxes():
    boxes = [((-4, 24, -4), (4, 32, 4), (0.34, 0.24, 0.16)),
             ((-4, 12, -2), (4, 24, 2), (0.16, 0.62, 0.66)),
             ((-4, 0, -2), (0, 12, 2), (0.20, 0.22, 0.72)),
             ((0, 0, -2), (4, 12, 2), (0.20, 0.22, 0.72)),
             ((-8, 12, -2), (-4, 24, 2), (0.74, 0.54, 0.40)),
             ((4, 12, -2), (8, 24, 2), (0.74, 0.54, 0.40))]
    pv, pf, pc = [], [], []
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
                pc.append(col)
            pf += [(base, base + 1, base + 2), (base, base + 2, base + 3)]
    return np.array(pv, float), pf, np.array(pc, float)


def setup(quads, body=True):
    quads = world_quads(quads)
    verts, faces, cols = to_arrays(quads)
    tex = np.asarray(WHITE, float)
    uv = np.full((len(verts), 2), (0.5, 0.5))
    if body:
        pv, pf, pc = proxy_boxes()
        allv = np.vstack([pv, verts])
        allf = np.array(pf + [(a + len(pv), b + len(pv), c + len(pv)) for a, b, c in faces],
                        np.int64)
        allu = np.vstack([np.full((len(pv), 2), (0.5, 0.5)), uv])
        allc = np.vstack([pc, cols])
    else:
        allv, allf, allu, allc = verts, faces, uv, cols
    return allv, allf, allu, allc, tex


def render(quads, body=True, out=1000):
    allv, allf, allu, allc, tex = setup(quads, body)
    rgba = rm.render_view(allv, allf, allu, tex, np.eye(3), 2200, alpha=True,
                          shade_lo=0.68, shade_hi=0.38, colors=allc)
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


def view_sheet(quads, size=620, out=None):
    allv, allf, allu, allc, tex = setup(quads, True)
    views = [("back", np.eye(3)),
             ("3/4", rm.rot_y(-38) @ rm.rot_x(-8)),
             ("side", rm.rot_y(90)),
             ("44 low", rm.rot_y(30) @ rm.rot_x(14))]
    sheet = Image.new("RGB", (size * 4, size + 30), (24, 26, 33))
    d = ImageDraw.Draw(sheet)
    for i, (name, R) in enumerate(views):
        img = rm.render_view(allv, allf, allu, tex, R, size, alpha=True,
                             shade_lo=0.68, shade_hi=0.38, colors=allc)
        tile = Image.new("RGB", (size, size), (24, 26, 33))
        a = Image.fromarray(img, "RGBA")
        tile.paste(a, (0, 0), a)
        sheet.paste(tile, (i * size, 30))
        d.text((i * size + 10, 10), name, fill=(220, 214, 200))
    if out is not None:
        sheet.save(out)
    return sheet


def main():
    quads = (feather_quads(1) + feather_quads(-1)
             + bone_quads(1) + bone_quads(-1))
    print("quads", len(quads))
    back = render(quads, body=True)
    back.save(OUT / "angel_v5_back.png")
    render(quads, body=False).save(OUT / "angel_v5_clean.png")
    view_sheet(quads, out=OUT / "angel_v5_views.png")
    arm = bone_quads(1) + bone_quads(-1)
    view_sheet(arm, out=OUT / "angel_v5_armature.png")
    ref = Image.open(OUT / "angel_ref_big.png").convert("RGB").resize((800, 800), Image.LANCZOS)
    new_img = back.resize((800, 800), Image.LANCZOS)
    sheet = Image.new("RGB", (1620, 860), (24, 26, 33))
    sheet.paste(ref, (10, 50))
    sheet.paste(new_img, (810, 50))
    d = ImageDraw.Draw(sheet)
    d.text((12, 22), "LUNAR REFERENCE", fill=(220, 214, 200))
    d.text((812, 22), "ANGEL v5 - 3D armature + volumetric feathers", fill=(220, 214, 200))
    sheet.save(OUT / "angel_v5_compare.png")
    print("saved")


if __name__ == "__main__":
    main()
