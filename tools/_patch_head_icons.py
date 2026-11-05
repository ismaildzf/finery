from pathlib import Path

p = Path(__file__).resolve().parents[1] / "generate_head_textures.py"
s = p.read_text(encoding="utf-8")


def sub(old, new):
    global s
    assert old in s, old[:60]
    s = s.replace(old, new)


sub(
    '''def icon_wizard_hat(img, d):
    d.ellipse([2, 19, 30, 27], fill=(74, 42, 122, 255), outline=(46, 26, 78, 255), width=1)
    d.ellipse([5, 19, 27, 24], fill=(88, 52, 140, 255))
    cone = [(8, 22), (13, 10), (18, 4), (22, 7), (24, 22)]
    d.polygon(cone, fill=(94, 56, 150, 255), outline=(50, 28, 84, 255))
    d.line([(15, 9), (20, 6)], fill=(120, 76, 186, 255), width=1)
    d.rectangle([7, 18, 25, 21], fill=(212, 160, 23, 255), outline=(140, 100, 12, 255))
    for sx, sy in [(23, 9), (12, 14), (20, 13)]:
        d.line([(sx - 2, sy), (sx + 2, sy)], fill=(255, 226, 130, 255))
        d.line([(sx, sy - 2), (sx, sy + 2)], fill=(255, 226, 130, 255))''',
    '''def icon_wizard_hat(img, d):
    # under-brim shadow, then a wavy brim with an upturned right edge
    d.ellipse([1, 21, 31, 27], fill=(58, 32, 96, 255), outline=(40, 22, 66, 255), width=1)
    d.ellipse([2, 18, 30, 25], fill=(84, 49, 134, 255), outline=(46, 26, 78, 255), width=1)
    d.ellipse([5, 19, 27, 23], fill=(104, 62, 162, 255))
    d.polygon([(27, 18), (31, 15), (30, 22), (27, 23)], fill=(94, 56, 150, 255), outline=(46, 26, 78, 255))
    # cone: tall, leaning left at the base and bending right at the tip
    cone = [(10, 21), (12, 12), (16, 3), (20, 6), (23, 21)]
    d.polygon(cone, fill=(96, 58, 154, 255), outline=(50, 28, 84, 255))
    d.polygon([(13, 12), (16, 4), (18, 6), (16, 13)], fill=(126, 82, 194, 255))
    d.line([(18, 6), (20, 10)], fill=(72, 42, 118, 255))
    # gold band + square buckle
    d.rectangle([8, 17, 25, 21], fill=(206, 154, 22, 255), outline=(140, 100, 12, 255))
    d.line([(9, 18), (24, 18)], fill=(248, 216, 118, 255))
    d.rectangle([15, 16, 20, 22], fill=(222, 172, 34, 255), outline=(120, 84, 10, 255))
    d.rectangle([16.5, 18, 18.5, 20], fill=(70, 44, 14, 255))
    # little stars
    for sx, sy in [(11, 10), (21, 12)]:
        d.line([(sx - 2, sy), (sx + 2, sy)], fill=(255, 232, 150, 255))
        d.line([(sx, sy - 2), (sx, sy + 2)], fill=(255, 232, 150, 255))''',
)

sub(
    '''def icon_headband(img, d):
    red, dark, light = (170, 34, 34, 255), (108, 18, 18, 255), (208, 58, 58, 255)
    d.rounded_rectangle([2, 10, 30, 18], radius=2, fill=red, outline=dark)
    d.line([(3, 12), (29, 12)], fill=light)
    d.line([(3, 16), (29, 16)], fill=(240, 234, 226, 255))
    d.rounded_rectangle([19, 8, 27, 17], radius=2, fill=(132, 24, 24, 255), outline=dark)
    d.polygon([(20, 15), (23, 15), (22, 26), (18, 26)], fill=(146, 28, 28, 255), outline=dark)
    d.polygon([(23, 15), (26, 15), (27, 24), (24, 24)], fill=(122, 20, 20, 255), outline=dark)''',
    '''def icon_headband(img, d):
    red, dark, light = (168, 32, 32, 255), (96, 14, 14, 255), (206, 62, 62, 255)
    # two-tone cloth band: darker underside, lighter top fold
    d.rounded_rectangle([2, 11, 30, 20], radius=2, fill=red, outline=dark)
    d.rounded_rectangle([3, 11, 29, 15], radius=2, fill=light, outline=None)
    d.line([(3, 18), (29, 18)], fill=(238, 230, 220, 255))
    d.line([(5, 13), (9, 17)], fill=(140, 22, 22, 255))
    d.line([(12, 12), (14, 17)], fill=(146, 24, 24, 255))
    # side knot with two lobes
    d.ellipse([18, 9, 27, 19], fill=(126, 20, 20, 255), outline=dark)
    d.ellipse([19, 10, 24, 16], fill=(150, 28, 28, 255))
    d.ellipse([23, 12, 27, 18], fill=(136, 22, 22, 255))
    d.line([(20, 12), (25, 14)], fill=(196, 54, 54, 255))
    # long tails, one light one dark so the silhouette reads
    d.polygon([(19, 17), (23, 18), (22, 29), (18, 28)], fill=(154, 30, 30, 255), outline=dark)
    d.polygon([(23, 17), (27, 18), (28, 26), (24, 27)], fill=(118, 16, 16, 255), outline=dark)
    d.line([(20, 20), (20, 26)], fill=(190, 52, 52, 255))
    d.line([(25, 20), (26, 25)], fill=(88, 10, 10, 255))''',
)

sub(
    '''def icon_crown(img, d):
    d.rectangle([5, 16, 27, 26], fill=(212, 160, 23, 255), outline=(140, 100, 12, 255))
    d.line([(6, 18), (26, 18)], fill=(250, 222, 130, 255))
    d.line([(6, 24), (26, 24)], fill=(250, 222, 130, 255))
    for cx, ch in [(6, 7), (11, 9), (16, 11), (21, 9), (26, 7)]:
        d.polygon([(cx - 2, 17), (cx + 2, 17), (cx, 17 - ch)],
                  fill=(232, 182, 40, 255), outline=(140, 100, 12, 255))
    d.ellipse([13, 19, 18, 24], fill=(216, 40, 66, 255), outline=(120, 12, 28, 255))
    d.ellipse([19, 20, 23, 24], fill=(52, 94, 228, 255), outline=(22, 42, 130, 255))
    d.point([(15, 20)], fill=(255, 200, 200, 255))
    d.point([(20, 21)], fill=(220, 235, 255, 255))''',
    '''def icon_crown(img, d):
    gold, gold_lite, gold_dark = (214, 162, 24, 255), (252, 224, 132, 255), (132, 92, 10, 255)
    # band with a bevel: darker base strip and a bright top edge
    d.rectangle([4, 15, 28, 26], fill=gold, outline=gold_dark)
    d.line([(5, 16), (27, 16)], fill=gold_lite)
    d.rectangle([4, 24, 28, 27], fill=(186, 134, 14, 255), outline=gold_dark)
    d.line([(5, 23), (27, 23)], fill=gold_lite)
    d.line([(6, 18), (6, 22)], fill=gold_dark)
    d.line([(26, 18), (26, 22)], fill=gold_dark)
    # five spikes, centre one taller with a collar
    for cx, top, half in [(5, 7, 1.6), (10, 4, 2.0), (16, 2, 2.4), (22, 4, 2.0), (27, 7, 1.6)]:
        d.polygon([(cx - half, 16), (cx + half, 16), (cx, top)],
                  fill=(236, 188, 46, 255), outline=gold_dark)
        d.line([(cx, top + 1), (cx, 14)], fill=gold_lite)
    d.rectangle([14, 13, 18, 16], fill=(230, 178, 34, 255), outline=gold_dark)
    # gems: gold setting + jewel + highlight
    d.ellipse([12, 17, 20, 25], fill=(232, 180, 36, 255), outline=gold_dark)
    d.ellipse([13, 18, 19, 24], fill=(206, 36, 62, 255), outline=(110, 10, 24, 255))
    d.point([(15, 20)], fill=(255, 196, 196, 255))
    d.ellipse([21, 19, 26, 24], fill=(232, 180, 36, 255), outline=gold_dark)
    d.ellipse([21.5, 19.5, 25.5, 23.5], fill=(54, 98, 226, 255), outline=(22, 42, 130, 255))
    d.point([(22, 21)], fill=(214, 232, 255, 255))
    d.ellipse([7, 20, 11, 24], fill=(232, 180, 36, 255), outline=gold_dark)
    d.ellipse([7.5, 20.5, 10.5, 23.5], fill=(44, 168, 120, 255), outline=(16, 88, 60, 255))''',
)

p.write_text(s, encoding="utf-8")
print("icons patched")
