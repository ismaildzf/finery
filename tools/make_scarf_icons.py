"""32x32 item icons for the two scarves (white dyeable / royal black-gold)."""

import os

from PIL import Image

S = 32


def draw(royal):
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    px = img.load()
    if royal:
        dark, mid, light, accent = (18, 18, 20, 255), (44, 44, 48, 255), (72, 72, 78, 255), (235, 185, 65, 255)
    else:
        dark, mid, light, accent = (120, 122, 128, 255), (186, 188, 194, 255), (226, 228, 232, 255), (250, 250, 252, 255)

    # neck loop (arc)
    for x in range(6, 27):
        t = (x - 6) / 20.0
        y = 7 + int(round(4 * abs(t - 0.5) * 2))
        for dy in range(4):
            px[x, y + dy] = light if dy == 0 else mid
        if x % 6 == 0:
            px[x, y + 3] = accent if royal else dark

    # knot
    for x in range(9, 17):
        for y in range(10, 17):
            edge = x in (9, 16) or y in (10, 16)
            px[x, y] = dark if edge else mid
    for x in range(11, 15):
        px[x, 12] = accent
        px[x, 14] = accent

    # two tails with fringe
    for x0, y1 in ((9, 26), (15, 28)):
        for y in range(17, y1):
            px[x0, y] = dark
            px[x0 + 1, y] = mid
            px[x0 + 2, y] = light
            if royal and y % 5 == 0:
                px[x0, y] = accent
                px[x0 + 2, y] = accent
        for y in range(y1, min(S, y1 + 3)):
            px[x0 + 1, y] = accent if royal else dark

    # outline
    src = img.copy().load()
    out = (12, 12, 14, 255) if royal else (92, 94, 100, 255)
    for y in range(S):
        for x in range(S):
            if src[x, y][3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < S and 0 <= ny < S and src[nx, ny][3] > 0:
                        px[x, y] = out
                        break
    return img


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for name, royal in (("scarf", False), ("royal_scarf", True)):
        img = draw(royal)
        img.save(os.path.join(root, "src", "main", "resources", "assets", "finery", "textures", "item", name + ".png"))
        img.resize((192, 192), Image.NEAREST).save(os.path.join(root, "publishing", "_debug_icon_" + name + "_v2.png"))
    print("icons written")


if __name__ == "__main__":
    main()
