import pathlib

p = pathlib.Path('tools/angelrig_v4.py')
s = p.read_text(encoding='utf-8')

# 1. fuller feather profile + low ridge
s = s.replace('''    ts = [i / segs for i in range(segs + 1)]
    widths = [(t ** 0.38) * ((1.0 - t) ** 0.48) for t in ts]
    peak = max(widths) or 1.0
    widths = [w / peak * width for w in widths]
    if rounded:
        widths[-1] = max(widths[-1], 0.55 * width)
    else:
        widths[-1] = 0.05''',
'''    ts = [i / segs for i in range(segs + 1)]
    if rounded:
        widths = [width * (0.72 + 0.28 * math.sin(math.pi * t)) for t in ts]
        widths[-1] = 0.62 * width
    else:
        raw = [((1.0 - t ** 2.6) ** 0.45) * (0.5 + 0.5 * min(1.0, t * 4.0))
               for t in ts]
        peak = max(raw) or 1.0
        widths = [w / peak * width for w in raw]
        widths[-1] = 0.08 * width''')
s = s.replace('ridge.append((px, py, zc + (0.07 if rounded else 0.15) * w))',
              'ridge.append((px, py, zc + (0.05 if rounded else 0.085) * w))')
s = s.replace('h0 = (0.08 if rounded else 0.165) * widths[k]', 'h0 = (0.06 if rounded else 0.10) * widths[k]')
s = s.replace('h1 = (0.08 if rounded else 0.165) * widths[k + 1]', 'h1 = (0.06 if rounded else 0.10) * widths[k + 1]')

# 2. larger, softer covert cap
old_start = s.index('def covert_cap():')
old_end = s.index('def all_feathers():')
new_cap = '''def covert_cap():
    rows = [
        (8.6, [1.0, 2.2, 3.4, 4.6, 5.8], 2.8, 1.18),
        (6.6, [0.5, 1.7, 2.9, 4.1, 5.3, 6.5], 3.0, 1.10),
        (4.4, [0.4, 1.6, 2.8, 4.0, 5.2, 6.4, 7.4], 3.2, 1.02),
        (2.2, [0.7, 1.9, 3.1, 4.3, 5.5, 6.7, 7.8], 3.2, 0.94),
        (0.0, [1.2, 2.4, 3.6, 4.8, 6.0, 7.2, 8.0], 3.0, 0.86),
    ]
    out = []
    for ri, (y, xs, length, z) in enumerate(rows):
        for i, x in enumerate(xs):
            ang = math.radians(62 - 5.0 * i + 2.0 * math.sin(i * 2.3 + ri))
            ln = length * (1.0 - 0.035 * i) * (0.97 + 0.05 * math.sin(i * 1.7 + ri * 0.9))
            tip = (x + math.cos(ang) * ln * 0.8, y + math.sin(ang) * ln)
            out.append(dict(root=(x, y - 0.2), tip=tip, width=1.75,
                            bow=0.06, z0=z + 0.008 * i, z1=z - 0.03 + 0.008 * i,
                            zbulge=0.04, thick=0.10, rounded=True, segs=4,
                            tag="radius", tint=0.995 - 0.010 * ri + 0.008 * (i % 2)))
    return out


'''
s = s[:old_start] + new_cap + s[old_end:]

# 3. drop the under-fan from the feather set
s = s.replace('''    return (leading_fan() + primary_fan() + under_fan() + inner_tertials()
            + median_coverts() + covert_cap())''',
'''    return (leading_fan() + primary_fan() + inner_tertials()
            + median_coverts() + covert_cap())''')

# 4. shadow backing shell behind the feathers
marker = '# ── preview frame ────────────────────────────────────────────────────────'
backing = '''# ── shadow backing (fills the gaps between feathers) ────────────────────
OUTLINE = ([(7.0, 11.6), (7.6, 11.2), (10.8, 9.61), (13.54, 7.63),
            (16.34, 5.64), (18.26, 3.65), (20.13, 1.66), (20.87, -0.32),
            (22.0, -2.31), (22.84, -4.3), (23.35, -6.29), (23.35, -8.27),
            (22.3, -13.1), (21.4, -15.9), (20.45, -18.5), (17.5, -19.2),
            (14.62, -19.25), (12.4, -18.4), (10.51, -17.2), (9.0, -15.9),
            (7.85, -14.3), (6.6, -12.9), (5.46, -11.4), (4.7, -9.7),
            (4.02, -7.97), (4.1, -6.3), (4.4, -5.3), (4.1, -3.3),
            (3.1, -2.3), (2.8, 0.7), (1.7, 1.7), (1.4, 2.7), (1.1, 3.6),
            (0.2, 4.6), (0.4, 5.6), (1.7, 6.6), (3.6, 7.6), (4.4, 8.6),
            (4.7, 9.6), (5.0, 10.6), (6.3, 11.6)])


def backing_quads(side):
    gw, gh = 70, 100
    x0, x1 = 2.0, 23.9
    y0, y1 = -20.0, 12.0
    img = Image.new("L", (gw, gh), 0)
    d = ImageDraw.Draw(img)
    poly = [((warp_x(x) - x0) / (x1 - x0) * (gw - 1),
             (y1 - y) / (y1 - y0) * (gh - 1)) for x, y in OUTLINE]
    d.polygon(poly, fill=255)
    m = np.asarray(img) > 127
    cell = 4
    quads = []
    for j in range(0, gh - cell, cell):
        for i in range(0, gw - cell, cell):
            if not (m[j, i] and m[j, i + cell] and m[j + cell, i] and m[j + cell, i + cell]):
                continue
            pts = []
            for (px, py) in ((i, j), (i + cell, j), (i + cell, j + cell), (i, j + cell)):
                x = x0 + px / (gw - 1) * (x1 - x0)
                y = y1 - py / (gh - 1) * (y1 - y0)
                z = -0.30 + 0.10 * math.sin(math.pi * (x - x0) / (x1 - x0))
                if side < 0:
                    x = -x
                pts.append((x, y, z))
            shade = 0.70 + 0.16 * (0.5 + 0.5 * math.sin((i * 0.7 + j * 1.3)))
            tint = (0.80 * shade, 0.85 * shade, 0.95 * shade)
            quads.append((pts, None, tint, "root"))
    return quads


'''
s = s.replace(marker, backing + marker)

# 5. main: no bones in the feathered render
s = s.replace('''    quads = (feather_quads(1) + feather_quads(-1)
             + bone_quads(1) + bone_quads(-1))''',
'''    quads = (feather_quads(1) + feather_quads(-1)
             + backing_quads(1) + backing_quads(-1))''')
for a, b in (("angel_v6_back.png", "angel_v9_back.png"),
             ("angel_v6_clean.png", "angel_v9_clean.png"),
             ("angel_v6_views.png", "angel_v9_views.png"),
             ("angel_v6_armature.png", "angel_v9_armature.png"),
             ("angel_v6_compare.png", "angel_v9_compare.png")):
    s = s.replace(a, b)
s = s.replace("ANGEL v6 - volumetric feather fan + 3D underwing",
              "ANGEL v9 - full feathered fan + 3D armature")
p.write_text(s, encoding='utf-8')
print("patched v4")
