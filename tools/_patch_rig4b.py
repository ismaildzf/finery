import pathlib
import math

p = pathlib.Path('tools/angelrig_v4.py')
s = p.read_text(encoding='utf-8')

# outer-edge bridging points for the primaries + more feathers
s = s.replace('''BOTTOM = [(22.3, -13.1), (21.4, -15.9), (20.45, -18.5), (17.5, -19.2),
          (14.62, -19.25), (12.4, -18.4), (10.51, -17.2), (9.0, -15.9),
          (7.85, -14.3), (6.6, -12.9), (5.46, -11.4), (4.7, -9.7), (4.02, -7.97)]''',
'''BOTTOM = [(23.2, -9.4), (22.28, -10.26), (22.51, -12.25), (22.3, -13.1),
          (21.4, -15.9), (20.45, -18.5), (17.5, -19.2),
          (14.62, -19.25), (12.4, -18.4), (10.51, -17.2), (9.0, -15.9),
          (7.85, -14.3), (6.6, -12.9), (5.46, -11.4), (4.7, -9.7), (4.02, -7.97)]''')
s = s.replace('''    roots = resample([(9.0, 0.5), (8.5, -0.2), (7.9, -1.0), (7.1, -1.9),
                      (6.2, -2.7), (5.3, -3.4), (4.6, -3.8)], 20)
    tips = resample(BOTTOM, 20)
    out = []
    for i, (r, t) in enumerate(zip(roots, tips)):
        k = i / 19.0''',
'''    roots = resample([(9.0, 0.5), (8.5, -0.2), (7.9, -1.0), (7.1, -1.9),
                      (6.2, -2.7), (5.3, -3.4), (4.6, -3.8)], 24)
    tips = resample(BOTTOM, 24)
    out = []
    for i, (r, t) in enumerate(zip(roots, tips)):
        k = i / 23.0''')

# polar covert cap around the shoulder
start = s.index('def covert_cap():')
end = s.index('def all_feathers():')
new_cap = '''def covert_cap():
    cx, cy = 1.9, 0.4
    rows = [
        (2.4, (26, 98), 6, 2.2, 1.16),
        (4.2, (20, 100), 7, 2.4, 1.08),
        (6.0, (16, 102), 7, 2.5, 1.00),
        (7.8, (14, 104), 7, 2.5, 0.92),
        (9.5, (18, 104), 6, 2.4, 0.84),
    ]
    out = []
    for ri, (r, (a0, a1), n, length, z) in enumerate(rows):
        for i in range(n):
            a = math.radians(a0 + (a1 - a0) * i / (n - 1) + 2.0 * math.sin(i * 2.7 + ri))
            root = (cx + math.cos(a) * r, cy + math.sin(a) * r)
            a2 = a + math.radians(4.0 * math.sin(i * 1.9 + ri * 1.3))
            ln = length * (0.94 + 0.07 * math.sin(i * 1.7 + ri))
            tip = (cx + math.cos(a2) * (r + ln), cy + math.sin(a2) * (r + ln))
            out.append(dict(root=root, tip=tip, width=1.55,
                            bow=0.05, z0=z + 0.008 * i, z1=z - 0.03 + 0.008 * i,
                            zbulge=0.04, thick=0.10, rounded=True, segs=4,
                            tag="radius", tint=0.995 - 0.010 * ri + 0.008 * (i % 2)))
    return out


'''
s = s[:start] + new_cap + s[end:]

# deeper blue on the feather backs, slightly bluer fronts
s = s.replace("BACK = (0.60, 0.67, 0.82)", "BACK = (0.52, 0.60, 0.78)")
s = s.replace("FRONT_SHADE = (0.93, 0.955, 1.00)", "FRONT_SHADE = (0.90, 0.94, 1.00)")
s = s.replace("EDGE = (0.85, 0.89, 0.97)", "EDGE = (0.80, 0.86, 0.96)")
p.write_text(s, encoding='utf-8')
print("patched v4b")
