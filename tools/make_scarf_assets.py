"""Port of the owner's pro scarf script: texture sheets + gold mask.

Royal sheet keeps the real gold; the mask carries the same gold pixels as
opaque white so a second pass can tint only the embroidery with the dye.
The white sheet is fully dyeable (grayscale).
"""

import math
import os

import numpy as np
from PIL import Image

S = 512
STRIPS = [(10, 10, 340, 56), (10, 80, 340, 48), (10, 145, 120, 64)]
TAILS = [(160, 145, 96, 220), (280, 145, 88, 180)]


def fabric(img, mask, rx, ry, rw, rh, side_borders):
    for ix in range(rw):
        u = ix / rw
        for iy in range(rh):
            v = iy / rh
            lum = 0.25 + 0.65 * math.sin(v * math.pi) \
                + math.sin(u * math.pi * 6 + v * 1.5) * 0.12 \
                + math.sin((ix + iy) * 0.45) * 0.035
            if iy < 4 or iy > rh - 5:
                lum *= 0.45
            if side_borders and (ix < 5 or ix > rw - 6):
                lum *= 0.55

            base = min(255, max(12, round(lum * 68)))
            r, g, b = base, base, min(255, round(base * 1.08))

            gold = (8 <= iy <= 11) or (rh - 12 <= iy <= rh - 9)
            diamond = abs((ix % 24) - 12) + abs(iy - rh / 2)
            if 18 <= diamond <= 20.5 and 13 < iy < rh - 14:
                gold = True
            if gold:
                shine = 0.75 + 0.25 * math.sin(ix * 0.08 + iy * 0.05)
                r, g, b = min(255, round(235 * shine)), min(255, round(185 * shine)), min(255, round(65 * shine))
                mask[ry + iy, rx + ix] = (255, 255, 255, 255)

            img[ry + iy, rx + ix] = (r, g, b, 255)


def tail(img, mask, tx, ty, tw, th):
    fringe = 28
    body = th - fringe
    for iy in range(body):
        v = iy / body
        shadow = (0.28 + (iy / 26) * 0.72) if iy < 26 else 1.0
        for ix in range(tw):
            u = ix / tw
            lum = (0.28 + 0.64 * math.sin(u * math.pi)
                   + math.sin(u * math.pi * 3 + v * 4) * 0.1
                   + math.sin((ix - iy) * 0.4) * 0.03) * shadow
            if ix < 4 or ix > tw - 5:
                lum *= 0.5
            base = min(255, max(10, round(lum * 70)))
            r, g, b = base, base, min(255, round(base * 1.08))

            side_gold = (8 <= ix <= 11) or (tw - 12 <= ix <= tw - 9)
            bottom = (body - 16 <= iy <= body - 11) or (body - 6 <= iy <= body - 4)
            chevron = abs(iy - (body - 38 + abs(ix - tw / 2) * 0.55)) <= 2.2 and 11 < ix < tw - 12
            if side_gold or bottom or chevron:
                shine = (0.7 + 0.3 * math.sin(u * math.pi)) * shadow
                r, g, b = round(240 * shine), round(190 * shine), round(70 * shine)
                mask[ty + iy, tx + ix] = (255, 255, 255, 255)

            img[ty + iy, tx + ix] = (r, g, b, 255)

    slots = 9
    slot_w = tw / slots
    for t in range(slots):
        cx = tx + (t + 0.5) * slot_w
        half = slot_w * 0.28
        for fy in range(fringe):
            fv = fy / fringe
            sway = math.sin(fv * math.pi + t) * 1.2
            cur = half * (1 - fv * 0.35)
            for fx in range(int(-half - 2), int(half + 3)):
                dist = abs(fx - sway)
                if dist <= cur:
                    shade = math.cos((dist / cur) * math.pi * 0.45)
                    if fy >= fringe - 7:
                        r, g, b = round(235 * shade), round(180 * shade), round(60 * shade)
                        mask[ty + body + fy, int(round(cx + fx))] = (255, 255, 255, 255)
                    else:
                        tv = round(45 * shade)
                        r, g, b = tv, tv, tv
                    img[ty + body + fy, int(round(cx + fx))] = (r, g, b, 255)


def white_page():
    img = np.zeros((S, S, 4), dtype=np.uint8)
    for (rx, ry, rw, rh) in STRIPS:
        for ix in range(rw):
            u = ix / rw
            for iy in range(rh):
                v = iy / rh
                lum = 0.25 + 0.65 * math.sin(v * math.pi) \
                    + math.sin(u * math.pi * 6 + v * 1.5) * 0.12 \
                    + math.sin((ix + iy) * 0.45) * 0.035
                if iy < 4 or iy > rh - 5:
                    lum *= 0.45
                val = min(255, max(65, round(lum * 245)))
                img[ry + iy, rx + ix] = (val, val, val, 255)
    for (tx, ty, tw, th) in TAILS:
        fringe = 28
        body = th - fringe
        for iy in range(body):
            v = iy / body
            shadow = (0.28 + (iy / 26) * 0.72) if iy < 26 else 1.0
            for ix in range(tw):
                u = ix / tw
                lum = (0.28 + 0.64 * math.sin(u * math.pi)
                       + math.sin(u * math.pi * 3 + v * 4) * 0.1
                       + math.sin((ix - iy) * 0.4) * 0.03) * shadow
                if ix < 4 or ix > tw - 5:
                    lum *= 0.5
                emboss = (8 <= ix <= 11) or (tw - 12 <= ix <= tw - 9) or (body - 15 <= iy <= body - 11)
                if emboss:
                    lum = min(1.0, lum * 1.25)
                val = min(255, max(55, round(lum * 245)))
                img[ty + iy, tx + ix] = (val, val, val, 255)
        slots = 9
        slot_w = tw / slots
        for t in range(slots):
            cx = tx + (t + 0.5) * slot_w
            half = slot_w * 0.28
            for fy in range(fringe):
                fv = fy / fringe
                sway = math.sin(fv * math.pi + t) * 1.2
                cur = half * (1 - fv * 0.35)
                for fx in range(int(-half - 2), int(half + 3)):
                    dist = abs(fx - sway)
                    if dist <= cur:
                        shade = math.cos((dist / cur) * math.pi * 0.45)
                        tv = round((245 if fy >= fringe - 7 else 195) * shade)
                        img[ty + body + fy, int(round(cx + fx))] = (tv, tv, tv, 255)
    return img


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pub = os.path.join(root, "publishing")
    royal = np.zeros((S, S, 4), dtype=np.uint8)
    mask = np.zeros((S, S, 4), dtype=np.uint8)
    for (rx, ry, rw, rh) in STRIPS:
        fabric(royal, mask, rx, ry, rw, rh, rw < 200)
    for (tx, ty, tw, th) in TAILS:
        tail(royal, mask, tx, ty, tw, th)

    Image.fromarray(royal, "RGBA").save(os.path.join(pub, "scarf_royal_black_gold_512.png"))
    Image.fromarray(mask, "RGBA").save(os.path.join(pub, "scarf_royal_mask_512.png"))
    Image.fromarray(white_page(), "RGBA").save(os.path.join(pub, "scarf_dyeable_white_512.png"))
    print("scarf textures written")


if __name__ == "__main__":
    main()
