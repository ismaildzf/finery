"""Angel wing v4 - real 3D armature and volumetric feathers.

Structure (right wing, player pixels, x outboard, y up, z back):
  shoulder -> humerus -> elbow -> radius -> wrist -> hand -> 3 finger bones,
  visible ivory bones with gold joints, and individual feathers with a raised
  shaft, curved vane, thin rim and underside. Rows: leading, primaries,
  secondaries, two covert rows, shoulder fluff.

The approved reference box is preserved: wing top ~11.6 above the shoulder
root, bottom ~-19.6, outboard reach ~23.4.
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

AW = AH = 1024
CELLS = {
    "vane": (8, 8, 264, 520),
    "bone": (272, 8, 336, 520),
    "fluff": (344, 8, 424, 280),
    "gold": (432, 8, 472, 72),
    "shaft": (480, 8, 512, 520),
    "solid": (480, 528, 496, 544),
}

# ── armature (local wing space) ──────────────────────────────────────────
SHOULDER = (0.0, -5.7, 0.00)
ELBOW = (5.9, -0.2, 0.26)
WRIST = (12.9, 4.4, 0.48)
T1 = (20.4, 6.2, 0.60)
T2 = (21.0, 1.6, 0.58)
T3 = (19.2, -3.6, 0.52)
KNUCKLE2 = (16.6, 3.1, 0.56)

BONE_R = 0.34
FINGER_R = 0.13


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t,
            a[1] + (b[1] - a[1]) * t,
            a[2] + (b[2] - a[2]) * t)


def bezier(a, b, c, t):
    u = 1.0 - t
    return (u * u * a[0] + 2 * u * t * b[0] + t * t * c[0],
            u * u * a[1] + 2 * u * t * b[1] + t * t * c[1],
            u * u * a[2] + 2 * u * t * b[2] + t * t * c[2])


def mirror(p):
    return (-p[0], p[1], p[2])


# ── primitives ───────────────────────────────────────────────────────────
def bone_tube(a, b, r0, r1, sides=6, segs=3, tint=(0.88, 0.86, 0.79)):
    quads = []
    ax, ay, az = a
    bx, by, bz = b
    dx, dy, dz = bx - ax, by - ay, bz - az
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length < 1e-6:
        return quads
    ux, uy, uz = dx / length, dy / length, dz / length
    # stable frame
    rx, ry, rz = 0.0, 0.0, 1.0
    if abs(uz) > 0.9:
        rx, ry, rz = 1.0, 0.0, 0.0
    tx = uy * rz - uz * ry
    ty = uz * rx - ux * rz
    tz = ux * ry - uy * rx
    tl = math.sqrt(tx * tx + ty * ty + tz * tz) or 1.0
    tx, ty, tz = tx / tl, ty / tl, tz / tl
    nx = ty * uz - tz * uy
    ny = tz * ux - tx * uz
    nz = tx * uy - ty * ux
    rings = []
    for j in range(segs + 1):
        t = j / segs
        px, py, pz = ax + dx * t, ay + dy * t, az + dz * t
        bulge = 1.0 + 0.12 * math.sin(math.pi * t) + 0.06 * math.sin(3 * math.pi * t)
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


def joint_ball(c, r, tint=(0.95, 0.76, 0.36), sides=6, rings=3):
    quads = []
    cx, cy, cz = c
    for j in range(rings):
        v0 = math.pi * j / rings
        v1 = math.pi * (j + 1) / rings
        for i in range(sides):
            a0 = 2 * math.pi * i / sides
            a1 = 2 * math.pi * (i + 1) / sides
            pts = []
            for v, aa in ((v0, a0), (v0, a1), (v1, a1), (v1, a0)):
                pts.append((cx + r * math.sin(v) * math.cos(aa),
                            cy + r * math.cos(v),
                            cz + r * math.sin(v) * math.sin(aa)))
            quads.append((pts, None, tint))
    return quads


def feather(root, angle, length, width, z, curl=0.12, thick=0.07,
            front=(0.97, 0.98, 1.0), back=(0.66, 0.71, 0.84),
            edge=(0.83, 0.87, 0.95), shaft_col=(0.50, 0.52, 0.58),
            segs=4, mat="vane"):
    a = math.radians(angle)
    dx, dy = math.cos(a), math.sin(a)
    px, py = -dy, dx
    ts = [0.05, 0.28, 0.58, 0.85, 1.0] if segs == 4 else [i / segs for i in range(segs + 1)]
    widths = []
    for t in ts:
        w = width * (t ** 0.40) * ((1.0 - t) ** 0.50)
        widths.append(w)
    peak = max(widths) or 1.0
    widths = [w / peak * width for w in widths]
    spine, left, right, backp, ridge = [], [], [], [], []
    for k, t in enumerate(ts):
        bend = curl * length * t * t
        x = root[0] + dx * length * t + px * bend
        y = root[1] + dy * length * t + py * bend
        zc = z + 0.10 * math.sin(math.pi * t) + 0.16 * t * t
        w = widths[k]
        spine.append((x, y, zc))
        left.append((x + px * w, y + py * w, zc - 0.035 * w))
        right.append((x - px * w, y - py * w, zc - 0.035 * w))
        ridge.append((x, y, zc + 0.11 * max(0.5, w))) 
        backp.append((x, y, zc - thick))
    quads = []
    for k in range(len(ts) - 1):
        quads.append(([left[k], left[k + 1], ridge[k + 1], ridge[k]], None, front))
        quads.append(([ridge[k], ridge[k + 1], right[k + 1], right[k]], None, front))
        quads.append(([left[k], backp[k], backp[k + 1], left[k + 1]], None, back))
        quads.append(([backp[k], right[k], right[k + 1], backp[k + 1]], None, back))
        quads.append(([left[k], left[k + 1], backp[k + 1], backp[k]], None, edge))
        quads.append(([right[k], backp[k], backp[k + 1], right[k + 1]], None, edge))
    # raised quill / shaft
    for k in range(len(ts) - 1):
        w0 = max(0.045, widths[k] * 0.05)
        w1 = max(0.045, widths[k + 1] * 0.05)
        p0 = spine[k]
        p1 = spine[k + 1]
        q0 = ridge[k]
        q1 = ridge[k + 1]
        quads.append(([(p0[0] - px * w0, p0[1] - py * w0, p0[2] + 0.03),
                       (p0[0] + px * w0, p0[1] + py * w0, p0[2] + 0.03),
                       (p1[0] + px * w1, p1[1] + py * w1, p1[2] + 0.03),
                       (p1[0] - px * w1, p1[1] - py * w1, p1[2] + 0.03)], None, shaft_col))
        _ = q0, q1
    return quads


# ── layout ───────────────────────────────────────────────────────────────
def arm_point(t):
    """0..0.55 shoulder->elbow, 0.55..1 elbow->wrist."""
    if t <= 0.55:
        return lerp(SHOULDER, ELBOW, t / 0.55)
    return lerp(ELBOW, WRIST, (t - 0.55) / 0.45)


def build_feathers():
    fe = []

    # leading edge feathers, rising above the arm
    for i in range(12):
        t = 0.08 + 0.92 * i / 11
        p = arm_point(t)
        ang = 46 + 38 * (i / 11)
        ln = 3.4 + 3.6 * math.sin(math.pi * (i / 11.0) ** 0.75)
        wd = 1.15 + 0.55 * math.sin(math.pi * i / 11)
        fe.append((p, ang, ln, wd, 0.58 + 0.14 * (i / 11), 0.10, "radius"))

    # primaries hang from the hand's trailing edge
    prim_lens = [13.0, 16.0, 18.5, 20.5, 22.0, 23.0, 23.2, 22.4, 21.0, 19.5, 18.0]
    prim_w = [1.5, 1.6, 1.8, 1.9, 2.0, 2.0, 2.0, 1.9, 1.8, 1.7, 1.6]
    for i, (ln, wd) in enumerate(zip(prim_lens, prim_w)):
        t = i / (len(prim_lens) - 1)
        p = bezier(WRIST, (16.8, 6.2, 0.55), T2, t)
        ang = -58 - 42 * t
        # keep the fan inside the reference box
        ln = min(ln, 24.0 - 6.0 * t * t)
        fe.append((p, ang, ln, wd, 0.34 + 0.12 * t, 0.14, "hand"))

    # secondaries along the forearm, drooping inward
    for i in range(9):
        t = i / 8.0
        p = lerp(ELBOW, WRIST, 0.10 + 0.85 * t)
        ang = -78 - 26 * t
        ln = 7.0 + 7.5 * math.sin(math.pi * (0.25 + 0.7 * t))
        wd = 1.35 + 0.5 * math.sin(math.pi * t)
        fe.append((p, ang, ln, wd, 0.30 + 0.10 * t, 0.16, "radius"))

    # greater coverts
    for i in range(11):
        t = 0.06 + 0.90 * i / 10
        p = arm_point(t)
        ang = 38 + 45 * t
        ln = 2.8 + 2.4 * math.sin(math.pi * t ** 0.8)
        wd = 1.5 + 0.5 * math.sin(math.pi * t)
        fe.append((p, ang, ln, wd, 0.62 + 0.12 * t, 0.10, "humerus"))

    # median coverts
    for i in range(9):
        t = 0.10 + 0.84 * i / 8
        p = arm_point(t)
        ang = 30 + 50 * t
        ln = 1.9 + 1.4 * math.sin(math.pi * t)
        wd = 1.2 + 0.4 * math.sin(math.pi * t)
        fe.append((p, ang, ln, wd, 0.72 + 0.10 * t, 0.12, "humerus"))

    # shoulder fluff: short round feathers around the root
    for i in range(12):
        a = math.radians(-30 + 200 * i / 11)
        r = 1.5 + 1.4 * (i % 3) / 2
        p = (SHOULDER[0] + math.cos(a) * r, SHOULDER[1] + math.sin(a) * r * 0.8,
             0.44 + 0.18 * (i % 4) / 3)
        ang = 20 + 140 * i / 11
        ln = 2.2 + 2.0 * math.sin(math.pi * i / 11)
        wd = 1.1 + 0.5 * math.sin(math.pi * i / 11)
        fe.append((p, ang, ln, wd, 0.40, 0.08, "root"))
    return fe


def feather_tint(k, col):
    b = 0.97 + 0.04 * math.sin(k * 1.7)
    return (min(1.0, col[0] * b), min(1.0, col[1] * b), min(1.0, col[2] * b))


def quads_for(side=1):
    quads = []
    fe = build_feathers()
    for k, (p, ang, ln, wd, z, curl, bone) in enumerate(fe):
        if side > 0:
            root_p = p
            a = ang
        else:
            root_p = mirror(p)
            a = 180 - ang
        q = feather(root_p, a, ln, wd, z, curl=curl * (1 if side > 0 else -1))
        for verts, _uv, tint in q:
            quads.append((verts, None, feather_tint(k, tint), bone))
    return quads


def bone_quads(side=1):
    def m(p):
        return p if side > 0 else mirror(p)
    out = []
    arm_segs = [
        (m(SHOULDER), m(ELBOW), 0.38, 0.30),
        (m(ELBOW), m(WRIST), 0.30, 0.23),
        (m(WRIST), m(T1), 0.19, 0.09),
    ]
    for a, b, r0, r1 in arm_segs:
        out += [(v, None, t, "humerus" if a == m(SHOULDER) else
                 ("radius" if b == m(WRIST) else "hand")) for v, _u, t in
                bone_tube(a, b, r0, r1, segs=3)]
    for tip, bone in ((T2, "finger2"), (T3, "finger3")):
        out += [(v, None, (0.90, 0.88, 0.81), bone) for v, _u, t in
                bone_tube(m(WRIST), m(tip), 0.13, 0.05, sides=5, segs=3)]
    for c, r in ((SHOULDER, 0.42), (ELBOW, 0.34), (WRIST, 0.28),
                 (KNUCKLE2, 0.16), (T1, 0.12)):
        out += [(v, None, t, "root" if c == SHOULDER else "hand") for v, _u, t in
                joint_ball(m(c), r)]
    return out


def to_arrays(quads):
    verts, faces, cols, tags = [], [], [], []
    for q in quads:
        verts4, tint = q[0], q[2]
        tag = q[3] if len(q) > 3 else "root"
        base = len(verts)
        for p in verts4:
            verts.append([p[0], p[1], p[2]])
            cols.append(tint)
            tags.append(tag)
        faces.append((base, base + 1, base + 2))
        faces.append((base, base + 2, base + 3))
    return (np.array(verts, float), np.array(faces, np.int64),
            np.array(cols, float), tags)


# white 8x8 texture so per-vertex colours drive the preview
WHITE = Image.new("RGBA", (16, 16), (255, 255, 255, 255))


def proxy_boxes():
    boxes = [((-4, 24, -4), (4, 32, 4), (0.34, 0.24, 0.16)),
             ((-4, 12, -2), (4, 24, 2), (0.16, 0.62, 0.66)),
             ((-4, 0, -2), (0, 12, 2), (0.20, 0.22, 0.72)),
             ((0, 0, -2), (4, 12, 2), (0.20, 0.22, 0.72)),
             ((-8, 12, -2), (-4, 24, 2), (0.74, 0.54, 0.40)),
             ((4, 12, -2), (8, 24, 2), (0.74, 0.54, 0.40))]
    uv = ((CELLS["solid"][0] + 8) / AW, (CELLS["solid"][1] + 8) / AH)
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
                pu.append(uv)
                pc.append(col)
            pf += [(base, base + 1, base + 2), (base, base + 2, base + 3)]
    return np.array(pv, float), pf, np.array(pu, float), np.array(pc, float)


def world_quads(quads):
    """Local wing space -> preview world space (same frame as the body proxy)."""
    out = []
    for verts4, uv, tint, *rest in quads:
        side = 1 if float(np.mean([p[0] for p in verts4])) >= 0 else -1
        w4 = [(p[0] + side * 1.55, p[1] + 27.0, p[2] + 2.6) for p in verts4]
        out.append((w4, uv, tint, *rest))
    return out


def render(quads, size=1000, body=True, out=1000):
    quads = world_quads(quads)
    verts, faces, cols, tags = to_arrays(quads)
    tex = np.asarray(WHITE, float)
    uv = np.full((len(verts), 2), (8.0 / 16.0, 8.0 / 16.0))
    if body:
        pv, pf, pu, pc = proxy_boxes()
        allv = np.vstack([pv, verts])
        allf = np.array(pf + [(a + len(pv), b + len(pv), c + len(pv)) for a, b, c in faces],
                        np.int64)
        allu = np.vstack([pu, uv])
        allc = np.vstack([pc, cols])
        bv = pv
    else:
        allv, allf, allu, allc = verts, faces, uv, cols
        bv = verts
    rgba = rm.render_view(allv, allf, allu, tex, np.eye(3), 2200, alpha=True,
                          shade_lo=0.72, shade_hi=0.34, colors=allc)
    # the renderer auto-fits; reuse the reference camera math
    lo, hi = np.vstack([bv, verts]).min(0), np.vstack([bv, verts]).max(0)
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
    quads = world_quads(quads)
    verts, faces, cols, tags = to_arrays(quads)
    pv, pf, pu, pc = proxy_boxes()
    allv = np.vstack([pv, verts])
    allf = np.array(pf + [(a + len(pv), b + len(pv), c + len(pv)) for a, b, c in faces],
                    np.int64)
    allu = np.vstack([pu, np.full((len(verts), 2), (0.5, 0.5))])
    allc = np.vstack([pc, cols])
    tex = np.asarray(WHITE, float)
    views = [("back", np.eye(3)),
             ("3/4", rm.rot_y(-38) @ rm.rot_x(-8)),
             ("side", rm.rot_y(90)),
             ("top 3/4", rm.rot_x(-32) @ rm.rot_y(-16))]
    sheet = Image.new("RGB", (size * 4, size + 30), (24, 26, 33))
    d = ImageDraw.Draw(sheet)
    for i, (name, R) in enumerate(views):
        img = rm.render_view(allv, allf, allu, tex, R, size, alpha=True,
                             shade_lo=0.72, shade_hi=0.34, colors=allc)
        tile = Image.new("RGB", (size, size), (24, 26, 33))
        tile.paste(Image.fromarray(img, "RGBA"), (0, 0), Image.fromarray(img, "RGBA"))
        sheet.paste(tile, (i * size, 30))
        d.text((i * size + 10, 10), name, fill=(220, 214, 200))
    if out is not None:
        sheet.save(out)
    return sheet


def main():
    quads = quads_for(1) + quads_for(-1) + bone_quads(1) + bone_quads(-1)
    print("quads", len(quads))
    back = render(quads, body=True)
    back.save(OUT / "angel_v4_back.png")
    render(quads, body=False).save(OUT / "angel_v4_clean.png")
    view_sheet(quads, out=OUT / "angel_v4_views.png")
    ref = Image.open(OUT / "angel_ref_big.png").convert("RGB")
    ref_img = ref.resize((800, 800), Image.LANCZOS)
    new_img = back.resize((800, 800), Image.LANCZOS)
    sheet = Image.new("RGB", (1620, 860), (24, 26, 33))
    sheet.paste(ref_img, (10, 50))
    sheet.paste(new_img, (810, 50))
    d = ImageDraw.Draw(sheet)
    d.text((12, 22), "LUNAR REFERENCE", fill=(220, 214, 200))
    d.text((812, 22), "NEW - 3D armature + individual feathers", fill=(220, 214, 200))
    sheet.save(OUT / "angel_v4_compare.png")
    print("saved")


if __name__ == "__main__":
    main()
