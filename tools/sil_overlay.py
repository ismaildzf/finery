"""Silhouette overlay: my void wing vs the Lunar dragon-wing reference.

Normalises both images by the character's shoulder width and overlays the
wing masks (mine = red, Lunar = green, overlap = yellow) so the shape
difference is measurable instead of guessed.
"""
from PIL import Image

MINE = r"C:\MinecraftModding\mods\finery\wing_v6_voidwing.png"
REF = r"C:\Users\Administrator\AppData\Local\Temp\opencode\lunar_refs\dragonblack_04.png"
OUT = r"C:\MinecraftModding\mods\finery\_sil_overlay.png"


def mask_mine():
    im = Image.open(MINE).convert("RGB")
    px = im.load()
    # pose 0 cell: x 0..860, character centre 430, torso top y=300, 13 px/texel
    mask = set()
    for x in range(0, 860):
        for y in range(0, 560):
            r, g, b = px[x, y]
            if r < 90 and b > r + 10 and b < 160 and g < 90:      # dark violet wing
                mask.add(((x - 430) / 13.0, (y - 300) / 13.0))     # texels, y down
    return mask


def mask_ref():
    im = Image.open(REF).convert("RGB")
    px = im.load()
    w, h = im.size
    # find teal shirt to normalise: teal = strong green+blue, low red
    tx = []
    ty = []
    for x in range(0, w, 2):
        for y in range(0, h, 2):
            r, g, b = px[x, y]
            if r < 130 and g > 150 and b > 140 and abs(g - b) < 60:
                tx.append(x)
                ty.append(y)
    if not tx:
        raise SystemExit("teal not found in ref")
    cx = (min(tx) + max(tx)) / 2.0
    top = min(ty)
    shoulder = 8 * ((max(tx) - min(tx)) / 8.0)                 # px per 8 texels = shirt width
    s = shoulder / 8.0
    mask = set()
    for x in range(0, w):
        for y in range(0, h):
            r, g, b = px[x, y]
            if max(r, g, b) < 75 and (r - b) < 18 and r < 70:   # near-black wing
                mask.add(((x - cx) / s, (y - top) / s))
    return mask, s, cx, top


def main():
    m = mask_mine()
    ref, rs, rcx, rtop = mask_ref()
    W, H = 900, 900
    SC = 14.0
    img = Image.new("RGB", (W, H), (18, 18, 22))
    px = img.load()
    for (u, v) in ref:
        x = int(W / 2 + u * SC)
        y = int(H / 2 + (v - 4) * SC)
        if 0 <= x < W and 0 <= y < H:
            px[x, y] = (60, 200, 80)
    for (u, v) in m:
        x = int(W / 2 + u * SC)
        y = int(H / 2 + (v - 4) * SC)
        if 0 <= x < W and 0 <= y < H:
            old = px[x, y]
            px[x, y] = (235, 210, 60) if old == (60, 200, 80) else (230, 60, 60)
    # shoulder reference line + body box
    for x in range(int(W / 2 - 4 * SC), int(W / 2 + 4 * SC)):
        for y in range(int(H / 2 + (0 - 4) * SC), int(H / 2 + (1 - 4) * SC)):
            if px[x, y] == (18, 18, 22):
                px[x, y] = (70, 70, 90)
    img.save(OUT)
    print("mine px:", len(m), " ref px:", len(ref))
    print("ref scale: %.1f px/texel, shoulder top y=%d" % (rs, rtop))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
