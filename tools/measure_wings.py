"""Measure wing extents (in texels) for my render vs the Lunar reference."""
from PIL import Image

MINE = r"C:\MinecraftModding\mods\finery\wing_v6_voidwing.png"
REF = r"C:\Users\Administrator\AppData\Local\Temp\opencode\lunar_refs\dragonblack_04.png"


def bbox(points):
    if not points:
        return None
    us = [p[0] for p in points]
    vs = [p[1] for p in points]
    return min(us), max(us), min(vs), max(vs)


def measure_mine():
    im = Image.open(MINE).convert("RGB")
    px = im.load()
    pts = []
    for x in range(0, 860):
        for y in range(0, 560):
            r, g, b = px[x, y]
            if r >= g and b > g + 6 and r < 115 and (max(r, g, b) - min(r, g, b)) > 12:
                pts.append(((x - 430) / 13.0, (300 - y) / 13.0))   # u, v (v up)
    print("mine wing bbox (texels) u0,u1,v0,v1:", ["%.2f" % v for v in bbox(pts)], "n=", len(pts))
    left = [p for p in pts if p[0] < 0]
    right = [p for p in pts if p[0] > 0]
    print("  left :", ["%.2f" % v for v in bbox(left)])
    print("  right:", ["%.2f" % v for v in bbox(right)])


def measure_ref():
    im = Image.open(REF).convert("RGB")
    px = im.load()
    w, h = im.size
    tx, ty = [], []
    for x in range(0, w, 2):
        for y in range(0, h, 2):
            r, g, b = px[x, y]
            if r < 130 and g > 150 and b > 140 and abs(g - b) < 60:
                tx.append(x)
                ty.append(y)
    cx = (min(tx) + max(tx)) / 2.0
    top = min(ty)
    s = (max(tx) - min(tx)) / 8.0
    pts = []
    for x in range(int(cx - 400), int(cx + 400)):
        for y in range(int(top - 420), int(top + 480)):
            if 0 <= x < w and 0 <= y < h:
                r, g, b = px[x, y]
                if max(r, g, b) < 78 and (r - b) < 20 and (max(r, g, b) - min(r, g, b)) < 40:
                    pts.append(((x - cx) / s, (top - y) / s))
    print("ref  wing bbox (texels) u0,u1,v0,v1:", ["%.2f" % v for v in bbox(pts)], "n=", len(pts), "scale=%.1f" % s)
    left = [p for p in pts if p[0] < 0]
    right = [p for p in pts if p[0] > 0]
    print("  left :", ["%.2f" % v for v in bbox(left)])
    print("  right:", ["%.2f" % v for v in bbox(right)])


measure_mine()
measure_ref()
