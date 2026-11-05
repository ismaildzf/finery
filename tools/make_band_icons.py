"""Item icons for the two Blockbench head pieces, matching their new textures."""

import os

from PIL import Image

S = 32
OUT = {
    "headband": "src/main/resources/assets/finery/textures/item/headband.png",
    "eye_wrap": "src/main/resources/assets/finery/textures/item/eye_wrap.png",
}


def new():
    return Image.new("RGBA", (S, S), (0, 0, 0, 0))


def outline(img, color=(20, 6, 6, 255)):
    px = img.load()
    src = img.copy().load()
    for y in range(S):
        for x in range(S):
            if src[x, y][3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < S and 0 <= ny < S and src[nx, ny][3] > 0:
                        px[x, y] = color
                        break


def headband():
    img = new()
    px = img.load()
    dark = (58, 8, 10, 255)
    mid = (128, 16, 16, 255)
    hot = (214, 34, 26, 255)
    spark = (255, 156, 140, 255)
    rim = (255, 210, 200, 255)

    # band body, slight diagonal
    for x in range(3, 29):
        y0 = 13 - (x - 3) // 9
        for dy in range(6):
            px[x, y0 + dy] = (dark if dy in (0, 5) else mid)
        px[x, y0] = hot if x % 3 else rim
        if x % 4 == 1:
            px[x, y0] = spark
        # jagged lightning on the lower edge
        if (x * 7) % 5 == 0:
            px[x, y0 + 5] = spark
        if (x * 5) % 7 == 0:
            px[x, y0 + 1] = spark

    # knot
    for x in range(19, 26):
        for y in range(10, 17):
            px[x, y] = dark if (x in (19, 25) or y in (10, 16)) else mid
    for x in range(21, 24):
        px[x, 12] = hot
        px[x, 14] = hot

    # two tails
    for x0 in (20, 23):
        for y in range(17, 27):
            px[x0, y] = dark if y % 4 == 0 else mid
            px[x0 + 1, y] = hot if y % 3 == 0 else mid

    outline(img)
    return img


def eye_wrap():
    img = new()
    px = img.load()
    dark = (44, 44, 48, 255)
    shade = (150, 150, 156, 255)
    light = (206, 206, 212, 255)
    white = (245, 245, 248, 255)

    for x in range(3, 29):
        for dy in range(7):
            y = 12 + dy
            v = light if dy in (1, 2, 3, 4) else shade
            # chevrons pointing left, like the texture
            if (x + dy * 2) % 8 < 2:
                v = white
            if dy in (0, 6):
                v = dark
            px[x, y] = v
    # rounded ends
    for y in (12, 18):
        px[3, y] = (0, 0, 0, 0)
        px[28, y] = (0, 0, 0, 0)

    # small knot / strap on the right
    for x in range(24, 30):
        for y in range(15, 23):
            px[x, y] = dark if (x in (24, 29) or y in (15, 22)) else shade
    for y in range(23, 27):
        px[26, y] = dark
        px[27, y] = shade

    outline(img, (26, 26, 30, 255))
    return img


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    hb = headband()
    ew = eye_wrap()
    hb.save(os.path.join(root, OUT["headband"]))
    ew.save(os.path.join(root, OUT["eye_wrap"]))
    hb.resize((256, 256), Image.NEAREST).save(os.path.join(root, "publishing", "_debug_icon_new_headband.png"))
    ew.resize((256, 256), Image.NEAREST).save(os.path.join(root, "publishing", "_debug_icon_new_eye_wrap.png"))
    print("icons written")


if __name__ == "__main__":
    main()
