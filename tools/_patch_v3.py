import pathlib

p = pathlib.Path('tools/angelrig_v3.py')
s = p.read_text(encoding='utf-8')
start = s.index('# ── feather layout (right wing)')
end = s.index('# ── preview frame')
new = '''# ── silhouette targets (measured from the approved art) ─────────────────
X_WARP_IN = 2.0
X_SCALE = (X_OUT - X_WARP_IN) / X_OUT

OUTER = [(7.0, 11.6), (7.6, 11.2), (10.8, 9.61), (13.54, 7.63),
         (16.34, 5.64), (18.26, 3.65), (20.13, 1.66), (20.87, -0.32),
         (22.0, -2.31), (22.84, -4.3), (23.35, -6.29), (23.35, -8.27)]
BOTTOM = [(22.3, -13.1), (21.4, -15.9), (20.45, -18.5), (17.5, -19.2),
          (14.62, -19.25), (12.4, -18.4), (10.51, -17.2), (9.0, -15.9),
          (7.85, -14.3), (6.6, -12.9), (5.46, -11.4), (4.7, -9.7), (4.02, -7.97)]


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


def pull(points, center, amount):
    out = []
    for p in points:
        dx, dy = center[0] - p[0], center[1] - p[1]
        d = math.hypot(dx, dy) or 1.0
        out.append((p[0] + dx / d * amount, p[1] + dy / d * amount))
    return out


def warp_x(x):
    return X_WARP_IN + x * X_SCALE


def leading_fan():
    roots = resample([(6.0, 7.2), (6.6, 6.5), (7.1, 5.7), (7.6, 4.8),
                      (8.0, 3.9), (8.35, 3.0), (8.6, 2.1), (8.75, 1.3), (8.8, 0.7)], 22)
    tips = resample(OUTER, 22)
    out = []
    for i, (r, t) in enumerate(zip(roots, tips)):
        k = i / 21.0
        out.append(dict(root=r, tip=t, width=1.10 + 0.55 * k, bow=0.14,
                        z0=0.50 + 0.007 * i, z1=0.34 + 0.006 * i,
                        zbulge=0.04, thick=0.10, rounded=False, segs=4,
                        tag="finger", tint=0.99 - 0.004 * i))
    return out


def primary_fan():
    roots = resample([(9.0, 0.5), (8.5, -0.2), (7.9, -1.0), (7.1, -1.9),
                      (6.2, -2.7), (5.3, -3.4), (4.6, -3.8)], 20)
    tips = resample(BOTTOM, 20)
    out = []
    for i, (r, t) in enumerate(zip(roots, tips)):
        k = i / 19.0
        out.append(dict(root=r, tip=t, width=1.15 + 0.55 * math.sin(math.pi * k ** 0.8),
                        bow=-0.30, z0=0.40 - 0.005 * i, z1=0.07,
                        zbulge=0.05, thick=0.11, rounded=False, segs=4,
                        tag="hand", tint=0.965 - 0.006 * i))
    return out


def under_fan():
    roots = resample([(9.0, 0.5), (8.5, -0.2), (7.9, -1.0), (7.1, -1.9),
                      (6.2, -2.7), (5.3, -3.4), (4.6, -3.8)], 16)
    tips = pull(resample(BOTTOM, 16), (7.0, -1.0), 1.4)
    out = []
    for i, (r, t) in enumerate(zip(roots, tips)):
        out.append(dict(root=r, tip=t, width=2.5, bow=-0.25, z0=-0.02,
                        z1=-0.12, zbulge=0.03, thick=0.06, rounded=False,
                        segs=3, simple=True, tag="hand",
                        tint=0.72 + 0.006 * i))
    return out


def inner_tertials():
    data = [((5.0, 3.0), (2.8, 0.7), 1.15), ((5.3, 1.2), (3.1, -2.3), 1.2),
            ((5.5, -0.4), (4.6, -4.3), 1.15), ((5.2, -1.9), (4.1, -6.3), 1.05)]
    out = []
    for i, (r, t, w) in enumerate(data):
        out.append(dict(root=r, tip=t, width=w, bow=0.15, z0=0.60 - 0.03 * i,
                        z1=0.50 - 0.03 * i, zbulge=0.02, thick=0.09,
                        rounded=(i < 2), segs=3, tag="radius", tint=0.94))
    return out


def median_coverts():
    data = [((1.7, -0.2), (2.1, 1.8)), ((3.1, 0.0), (3.6, 2.1)),
            ((4.5, -0.4), (5.1, 1.8)), ((5.8, -1.0), (6.4, 1.0)),
            ((6.9, -1.9), (7.3, 0.1))]
    out = []
    for i, (r, t) in enumerate(data):
        out.append(dict(root=r, tip=t, width=1.05, bow=0.10, z0=0.70,
                        z1=0.64, zbulge=0.03, thick=0.09, rounded=True,
                        segs=3, tag="radius", tint=0.95))
    return out


def covert_cap():
    rows = [
        (8.6, [1.2, 2.3, 3.4, 4.5, 5.6], 2.05, 1.16),
        (7.0, [0.7, 1.8, 2.9, 4.0, 5.1, 6.2], 2.15, 1.08),
        (5.4, [0.5, 1.55, 2.6, 3.65, 4.7, 5.75, 6.8], 2.25, 1.00),
        (3.8, [0.7, 1.8, 2.9, 4.0, 5.1, 6.2, 7.3], 2.35, 0.92),
        (2.2, [0.9, 2.0, 3.1, 4.2, 5.3, 6.4, 7.5], 2.35, 0.84),
        (0.6, [1.2, 2.3, 3.4, 4.5, 5.6, 6.7, 7.8], 2.25, 0.76),
    ]
    out = []
    for ri, (y, xs, length, z) in enumerate(rows):
        for i, x in enumerate(xs):
            ang = math.radians(64 - 4.6 * i + 1.5 * math.sin(i * 2.1 + ri))
            ln = length * (1.0 - 0.04 * i) * (0.96 + 0.05 * math.sin(i * 1.3 + ri))
            tip = (x + math.cos(ang) * ln * 0.85, y + math.sin(ang) * ln)
            out.append(dict(root=(x, y - 0.25), tip=tip, width=1.24,
                            bow=0.08, z0=z + 0.008 * i, z1=z - 0.04 + 0.008 * i,
                            zbulge=0.03, thick=0.11, rounded=True, segs=3,
                            tag="radius", tint=1.0 - 0.012 * ri + 0.008 * (i % 2)))
    return out


def all_feathers():
    return (leading_fan() + primary_fan() + under_fan() + inner_tertials()
            + median_coverts() + covert_cap())


def feather_quads(side):
    quads = []
    for f in all_feathers():
        r, t = f["root"], f["tip"]
        rx = warp_x(r[0])
        tx = warp_x(t[0])
        if side < 0:
            r, t = (-rx, r[1]), (-tx, t[1])
        else:
            r, t = (rx, r[1]), (tx, t[1])
        q = feather(r, t, f["width"], bow=f["bow"] * (1 if side > 0 else -1),
                    z0=f["z0"], z1=f["z1"], zbulge=f["zbulge"], thick=f["thick"],
                    rounded=f["rounded"], segs=f["segs"], simple=f.get("simple", False),
                    tint=f["tint"])
        for verts, _uv, tint in q:
            quads.append((verts, None, tint, f["tag"]))
    return quads


def bone_quads(side):
    def m(p):
        q = (warp_x(p[0]), p[1], p[2])
        return q if side > 0 else mirror(q)

    out = []
    segs = [(SHOULDER, ELBOW, 0.30, 0.22, "humerus"),
            (ELBOW, WRIST, 0.22, 0.16, "radius"),
            (WRIST, HAND, 0.15, 0.08, "hand")]
    for a, b, r0, r1, tag in segs:
        out += [(v, None, t, tag) for v, _u, t in tube(m(a), m(b), r0, r1, segs=3)]
    for name, c, r in JOINTS:
        tag = "root" if name == "shoulder" else (
            "humerus" if name == "elbow" else ("radius" if name == "wrist" else "hand"))
        out += [(v, None, t, tag) for v, _u, t in ball(m(c), r)]
    return out


'''
s = s[:start] + new + s[end:]
s = s.replace('SHOULDER = (0.5, -4.4, 0.20)\nELBOW = (3.4, -1.0, 0.30)\nWRIST = (6.6, 3.2, 0.40)\nHAND = (9.2, 6.4, 0.45)\nJOINTS = [("shoulder", SHOULDER, 0.34), ("elbow", ELBOW, 0.25),\n          ("wrist", WRIST, 0.19), ("hand", HAND, 0.13)]',
              'SHOULDER = (0.8, -4.0, 0.10)\nELBOW = (3.2, -0.8, 0.14)\nWRIST = (5.6, 2.2, 0.18)\nHAND = (7.8, 4.2, 0.22)\nJOINTS = [("shoulder", SHOULDER, 0.32), ("elbow", ELBOW, 0.24),\n          ("wrist", WRIST, 0.18), ("hand", HAND, 0.12)]')
s = s.replace('''    quads = (feather_quads(1) + feather_quads(-1)
             + bone_quads(1) + bone_quads(-1)
             + backing_quads(1) + backing_quads(-1))''',
'''    quads = (feather_quads(1) + feather_quads(-1))''')
for old, new_name in (("angel_v5_back.png", "angel_v6_back.png"),
                      ("angel_v5_clean.png", "angel_v6_clean.png"),
                      ("angel_v5_views.png", "angel_v6_views.png"),
                      ("angel_v5_armature.png", "angel_v6_armature.png"),
                      ("angel_v5_compare.png", "angel_v6_compare.png")):
    s = s.replace(old, new_name)
s = s.replace('ANGEL v5 - 3D armature + volumetric feathers',
              'ANGEL v6 - volumetric feather fan + 3D underwing')
p.write_text(s, encoding='utf-8')
print('layout rewritten')
