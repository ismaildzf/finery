import pathlib

p = pathlib.Path('tools/angelshell_v2.py')
s = p.read_text(encoding='utf-8')

s = s.replace('''def prepare_texture():
    art = Image.open(WING_ART).convert("RGBA")
    rgba = np.asarray(art, float)
    alpha = rgba[:, :, 3] / 255.0
    mask = rgba[:, :, 3] > 40
    mi = Image.fromarray((mask * 255).astype(np.uint8))
    mi = mi.filter(ImageFilter.MaxFilter(25)).filter(ImageFilter.MinFilter(25))
    closed = np.asarray(mi) > 128
    sil = fill_holes(closed)''',
'''OUTLINE_OUTER = [(7.0, 11.6), (7.6, 11.2), (10.8, 9.61), (13.54, 7.63),
                 (16.34, 5.64), (18.26, 3.65), (20.13, 1.66), (20.87, -0.32),
                 (22.0, -2.31), (22.84, -4.3), (23.35, -6.29), (23.35, -8.27),
                 (22.9, -10.6)]
OUTLINE_BOTTOM = [(22.3, -13.1), (21.4, -15.9), (20.45, -18.5), (17.5, -19.2),
                  (14.62, -19.25), (12.4, -18.4), (10.51, -17.2), (9.0, -15.9),
                  (7.85, -14.3), (6.6, -12.9), (5.46, -11.4), (4.7, -9.7),
                  (4.02, -7.97)]
OUTLINE_INNER = [(4.1, -6.3), (4.4, -5.3), (4.1, -3.3), (3.1, -2.3),
                 (2.8, 0.7), (1.7, 1.7), (1.4, 2.7), (1.1, 3.6),
                 (0.2, 4.6), (0.4, 5.6), (1.7, 6.6), (3.6, 7.6),
                 (4.4, 8.6), (4.7, 9.6), (5.0, 10.6), (6.3, 11.6)]


def art_uv(x, y):
    return (500.0 - x / X_OUT * 500.0, (Y_TOP - y) / (Y_TOP - Y_BOT) * 628.0)


def outline_mask():
    pts = OUTLINE_OUTER + OUTLINE_BOTTOM + OUTLINE_INNER
    img = Image.new("L", (500, 628), 0)
    d = ImageDraw.Draw(img)
    poly = [art_uv(x, y) for x, y in pts]
    d.polygon(poly, fill=255)
    return np.asarray(img) > 127


def prepare_texture():
    art = Image.open(WING_ART).convert("RGBA")
    rgba = np.asarray(art, float)
    alpha = rgba[:, :, 3] / 255.0
    sil = outline_mask()''')

# feather relief: trim the outer mane
s = s.replace('''    outer = [(23.35, -6.3), (23.35, -8.3), (22.8, -4.3), (22.0, -2.3),
             (20.9, -0.3), (20.1, 1.7), (18.3, 3.7), (16.3, 5.6),
             (13.5, 7.6), (10.8, 9.6)]''',
'''    outer = [(23.35, -8.3), (22.0, -2.3), (20.1, 1.7), (18.3, 3.7),
             (16.3, 5.6), (13.5, 7.6), (10.8, 9.6)]''')
p.write_text(s, encoding='utf-8')
print("patched outline shell")
