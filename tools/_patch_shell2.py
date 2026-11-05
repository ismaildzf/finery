import pathlib

p = pathlib.Path('tools/angelshell_v2.py')
s = p.read_text(encoding='utf-8')

# ── texture prep + flood fill ────────────────────────────────────────────
s = s.replace('''def mirror(p):
    return (-p[0], p[1], p[2])''',
'''def mirror(p):
    return (-p[0], p[1], p[2])


def fill_holes(mask):
    """True outside the silhouette, then invert; fills interior transparent gaps."""
    from collections import deque
    h, w = mask.shape
    outside = np.zeros((h, w), bool)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if not mask[y, x] and not outside[y, x]:
                outside[y, x] = True
                q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if not mask[y, x] and not outside[y, x]:
                outside[y, x] = True
                q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and not mask[ny, nx] and not outside[ny, nx]:
                outside[ny, nx] = True
                q.append((ny, nx))
    return ~outside


def prepare_texture():
    art = Image.open(WING_ART).convert("RGBA")
    rgba = np.asarray(art, float)
    alpha = rgba[:, :, 3] / 255.0
    mask = rgba[:, :, 3] > 40
    sil = fill_holes(mask)
    base = np.array([214.0, 228.0, 246.0])
    rgb = rgba[:, :, :3] * alpha[:, :, None] + base * (1 - alpha[:, :, None])
    out = np.zeros((rgba.shape[0], rgba.shape[1], 4), np.uint8)
    out[:, :, :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    out[:, :, 3] = np.where(sil, 255, 0).astype(np.uint8)
    atlas = Image.open(ATLAS).convert("RGBA")
    atlas.paste(Image.fromarray(out, "RGBA"), (int(WING_U0), int(WING_V0)))
    patch = Image.new("RGBA", (24, 24), (255, 255, 255, 255))
    atlas.paste(patch, (960, 660))
    return atlas, sil''')

# shell uses the filled silhouette
s = s.replace('''def shell_quads(side, cell=16):
    art = np.asarray(Image.open(WING_ART).convert("RGBA"))[:, :, 3]
    H, W = art.shape
    mask = art > 250''',
'''def shell_quads(side, mask, cell=12):
    H, W = mask.shape''')
s = s.replace('            ok = (mask[v0, u0] and mask[v0, u0 + cell - 1]\n                  and mask[v0 + cell - 1, u0] and mask[v0 + cell - 1, u0 + cell - 1])',
              '            ok = bool(mask[v0, u0] and mask[v0, u0 + cell - 1]\n                      and mask[v0 + cell - 1, u0] and mask[v0 + cell - 1, u0 + cell - 1])')

# relief feather geometry: z follows the shell, cap moved inboard, gentler tips
s = s.replace('''def relief_feathers(side):
    art = np.asarray(Image.open(WING_ART).convert("RGBA"))[:, :, 3]
    H, W = art.shape
    quads = []

    def add_feather(root_uv, tip_uv, width, z0, z1, tint, rounded=False, bow=0.2):
        r = shell_pos(root_uv[0], root_uv[1], side)
        t = shell_pos(tip_uv[0], tip_uv[1], side)
        r = (r[0], r[1], z0)
        t = (t[0], t[1], z1)
        if side < 0:
            bow = -bow
        q = rig.feather(r, t, width, bow=bow, z0=z0, z1=z1, zbulge=0.05,
                        thick=0.12, rounded=rounded, segs=3, tint=tint)
        for verts, _uv, tnt in q:
            quads.append((verts, None, tnt, "feather"))
''',
'''def relief_feathers(side):
    quads = []

    def add_feather(root_uv, tip_uv, width, lift, tint, rounded=False, bow=0.2):
        r = shell_pos(root_uv[0], root_uv[1], side)
        t = shell_pos(tip_uv[0], tip_uv[1], side)
        z0 = r[2] + lift
        z1 = t[2] + lift * 0.55
        r = (r[0], r[1], z0)
        t = (t[0], t[1], z1)
        if side < 0:
            bow = -bow
        q = rig.feather(r, t, width, bow=bow, z0=z0, z1=z1, zbulge=0.10,
                        thick=0.14, rounded=rounded, segs=3, tint=tint)
        for verts, _uv, tnt in q:
            quads.append((verts, None, tnt, "feather"))
''')
s = s.replace('''        drop = 1.4 + 0.7 * math.sin(i * 1.1)
        tip_v = min(627, v + drop / (Y_TOP - Y_BOT) * 628)
        root_v = max(0, v - (3.4 + 0.6 * math.sin(i * 0.7)) / (Y_TOP - Y_BOT) * 628)
        add_feather((min(499, u + 14), root_v), (min(499, u - 8), tip_v),
                    1.7 + 0.4 * math.sin(i * 0.9), 1.12 + 0.012 * i, 0.92,
                    0.98 - 0.006 * i, rounded=False, bow=-0.25)''',
'''        drop = 0.9 + 0.5 * math.sin(i * 1.1)
        tip_v = min(627, v + drop / (Y_TOP - Y_BOT) * 628)
        root_v = max(0, v - (3.0 + 0.5 * math.sin(i * 0.7)) / (Y_TOP - Y_BOT) * 628)
        add_feather((min(499, u + 12), root_v), (min(499, u - 6), tip_v),
                    1.6 + 0.35 * math.sin(i * 0.9), 0.22 + 0.01 * i,
                    0.99 - 0.005 * i, rounded=False, bow=-0.22)''')
s = s.replace('''        root_v = min(627, v + 90)
        add_feather((min(499, u + 8), root_v), (max(0, u - 26), max(0, v - 34)),
                    1.5, 1.10 + 0.015 * i, 0.96, 0.97 - 0.006 * i,
                    rounded=False, bow=0.25)''',
'''        root_v = min(627, v + 70)
        add_feather((min(499, u + 8), root_v), (max(0, u - 18), max(0, v - 22)),
                    1.45, 0.22 + 0.012 * i, 0.97 - 0.005 * i,
                    rounded=False, bow=0.22)''')
s = s.replace('''    cap = [
        ((150, 120), (110, 40), (60, 130), (25, 80), (-10, 130)),
        ((210, 210), (170, 135), (125, 225), (85, 175), (45, 235), (10, 205)),
        ((270, 300), (230, 230), (190, 320), (150, 270), (110, 330), (75, 300)),
    ]
    for ri, row in enumerate(cap):
        for i, (u, v) in enumerate(row):
            add_feather((u, v + 70), (u - 34, v - 55), 2.1,
                        1.16 + 0.008 * i, 1.04 + 0.008 * i,
                        0.99 - 0.01 * ri + 0.007 * (i % 2), rounded=True, bow=0.12)
    return quads''',
'''    cap = [
        ((470, 100), (435, 70), (400, 135), (365, 105), (330, 150)),
        ((480, 190), (445, 155), (410, 215), (375, 180), (340, 230), (305, 200)),
        ((485, 280), (450, 245), (415, 300), (380, 265), (345, 315), (310, 290)),
    ]
    for ri, row in enumerate(cap):
        for i, (u, v) in enumerate(row):
            add_feather((u, v + 60), (u - 26, v - 48), 1.9,
                        0.20 + 0.010 * i, 0.985 - 0.012 * ri + 0.007 * (i % 2),
                        rounded=True, bow=0.10)
    return quads''')

# render with prepared texture
s = s.replace('''def setup(quads, body=True):
    quads = world_quads(quads)
    verts, faces, uv, cols = to_arrays(quads)
    tex = np.asarray(Image.open(ATLAS).convert("RGBA"), float)''',
'''def setup(quads, body=True, atlas=None):
    quads = world_quads(quads)
    verts, faces, uv, cols = to_arrays(quads)
    if atlas is None:
        atlas, _ = prepare_texture()
    tex = np.asarray(atlas.convert("RGBA"), float)''')
s = s.replace('''def render(quads, body=True, out=1000):
    allv, allf, allu, allc, tex = setup(quads, body)''',
'''def render(quads, body=True, out=1000, atlas=None):
    allv, allf, allu, allc, tex = setup(quads, body, atlas)''')
s = s.replace('''def view_sheet(quads, size=620, out=None):
    allv, allf, allu, allc, tex = setup(quads, True)''',
'''def view_sheet(quads, size=620, out=None, atlas=None):
    allv, allf, allu, allc, tex = setup(quads, True, atlas)''')

# main
s = s.replace('''def main():
    shell = shell_quads(1) + shell_quads(-1)
    relief = relief_feathers(1) + relief_feathers(-1)
    bones = bone_quads(1) + bone_quads(-1)
    quads = shell + relief + bones
    print("quads", len(quads), "shell", len(shell), "relief", len(relief), "bones", len(bones))
    back = render(quads, body=True)
    back.save(OUT / "angel_v7_back.png")
    render(quads, body=False).save(OUT / "angel_v7_clean.png")
    view_sheet(quads, out=OUT / "angel_v7_views.png")
    view_sheet(bones + shell_quads(1, 26) + shell_quads(-1, 26),
               out=OUT / "angel_v7_armature.png")''',
'''def main():
    atlas, sil = prepare_texture()
    shell = shell_quads(1, sil) + shell_quads(-1, sil)
    relief = relief_feathers(1) + relief_feathers(-1)
    bones = bone_quads(1) + bone_quads(-1)
    quads = shell + relief + bones
    print("quads", len(quads), "shell", len(shell), "relief", len(relief))
    back = render(quads, body=True, atlas=atlas)
    back.save(OUT / "angel_v8_back.png")
    render(quads, body=False, atlas=atlas).save(OUT / "angel_v8_clean.png")
    view_sheet(quads, out=OUT / "angel_v8_views.png", atlas=atlas)
    view_sheet(bones + shell_quads(1, sil, 24) + shell_quads(-1, sil, 24),
               out=OUT / "angel_v8_armature.png", atlas=atlas)''')
s = s.replace('''    sheet.save(OUT / "angel_v7_compare.png")''', '''    sheet.save(OUT / "angel_v8_compare.png")''')
s = s.replace("ANGEL v7 - curved shell + relief feathers + armature",
              "ANGEL v8 - solid 3D shell + relief feathers + armature")
p.write_text(s, encoding='utf-8')
print("patched shell v2")
