import pathlib

p = pathlib.Path('tools/angelshell_v2.py')
s = p.read_text(encoding='utf-8')

s = s.replace("from PIL import Image, ImageDraw", "from PIL import Image, ImageDraw, ImageFilter")
s = s.replace("    mask = rgba[:, :, 3] > 40\n    sil = fill_holes(mask)",
"""    mask = rgba[:, :, 3] > 40
    mi = Image.fromarray((mask * 255).astype(np.uint8))
    mi = mi.filter(ImageFilter.MaxFilter(25)).filter(ImageFilter.MinFilter(25))
    closed = np.asarray(mi) > 128
    sil = fill_holes(closed)""")

# lighter, smaller relief set
s = s.replace('''    for i, (x, y) in enumerate(bottom):
        u = 500 - x / X_OUT * 500
        v = (Y_TOP - y) / (Y_TOP - Y_BOT) * 628
        drop = 0.9 + 0.5 * math.sin(i * 1.1)
        tip_v = min(627, v + drop / (Y_TOP - Y_BOT) * 628)
        root_v = max(0, v - (3.0 + 0.5 * math.sin(i * 0.7)) / (Y_TOP - Y_BOT) * 628)
        add_feather((min(499, u + 12), root_v), (min(499, u - 6), tip_v),
                    1.6 + 0.35 * math.sin(i * 0.9), 0.22 + 0.01 * i,
                    0.99 - 0.005 * i, rounded=False, bow=-0.22)''',
'''    for i, (x, y) in enumerate(bottom):
        u = 500 - x / X_OUT * 500
        v = (Y_TOP - y) / (Y_TOP - Y_BOT) * 628
        drop = 0.7 + 0.4 * math.sin(i * 1.1)
        tip_v = min(627, v + drop / (Y_TOP - Y_BOT) * 628)
        root_v = max(0, v - (2.6 + 0.4 * math.sin(i * 0.7)) / (Y_TOP - Y_BOT) * 628)
        add_feather((min(499, u + 10), root_v), (min(499, u - 4), tip_v),
                    1.35 + 0.25 * math.sin(i * 0.9), 0.16 + 0.008 * i,
                    0.985 - 0.005 * i, rounded=False, bow=-0.18)''')
s = s.replace('''    for i, (x, y) in enumerate(outer):
        u = 500 - x / X_OUT * 500
        v = (Y_TOP - y) / (Y_TOP - Y_BOT) * 628
        root_v = min(627, v + 70)
        add_feather((min(499, u + 8), root_v), (max(0, u - 18), max(0, v - 22)),
                    1.45, 0.22 + 0.012 * i, 0.97 - 0.005 * i,
                    rounded=False, bow=0.22)''',
'''    for i, (x, y) in enumerate(outer):
        u = 500 - x / X_OUT * 500
        v = (Y_TOP - y) / (Y_TOP - Y_BOT) * 628
        root_v = min(627, v + 60)
        add_feather((min(499, u + 6), root_v), (max(0, u - 12), max(0, v - 16)),
                    1.30, 0.16 + 0.010 * i, 0.975 - 0.005 * i,
                    rounded=False, bow=0.18)''')
s = s.replace('''            add_feather((u, v + 60), (u - 26, v - 48), 1.9,
                        0.20 + 0.010 * i, 0.985 - 0.012 * ri + 0.007 * (i % 2),
                        rounded=True, bow=0.10)''',
'''            add_feather((u, v + 55), (u - 22, v - 42), 1.55,
                        0.14 + 0.008 * i, 0.985 - 0.012 * ri + 0.007 * (i % 2),
                        rounded=True, bow=0.08)''')
s = s.replace('thick=0.14, rounded=rounded, segs=3, tint=tint)', 'thick=0.09, rounded=rounded, segs=3, tint=tint)')
s = s.replace('def shell_quads(side, mask, cell=12):', 'def shell_quads(side, mask, cell=10):')
p.write_text(s, encoding='utf-8')
print("patched v3")
