"""Generate the dyed scarf sheets and the single 'dyeable' scarf icon."""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
NECK = ROOT / "src/main/resources/assets/finery/textures/neck"
ITEM = ROOT / "src/main/resources/assets/finery/textures/item"

DYES = {
    "white": (249, 255, 254),
    "orange": (249, 128, 29),
    "magenta": (199, 78, 189),
    "light_blue": (58, 179, 218),
    "yellow": (254, 216, 61),
    "lime": (128, 199, 31),
    "pink": (243, 139, 170),
    "gray": (71, 79, 82),
    "light_gray": (157, 157, 151),
    "cyan": (22, 156, 156),
    "purple": (137, 50, 184),
    "blue": (60, 68, 170),
    "brown": (131, 84, 50),
    "green": (94, 124, 22),
    "red": (176, 46, 38),
    "black": (29, 29, 33),
}


LUMA = np.array([0.299, 0.587, 0.114])
GOLD = np.array([222.0, 178.0, 84.0])


def tint(base: Image.Image, rgb, pattern: str) -> Image.Image:
    src = np.array(base.convert("RGBA")).astype(np.float32)
    alpha = src[:, :, 3]
    lum = src[:, :, :3] @ LUMA
    opaque = alpha > 0
    lo, hi = np.percentile(lum[opaque], 2), np.percentile(lum[opaque], 98)
    span = max(hi - lo, 1e-3)
    t = np.clip((lum - lo) / span, 0.0, 1.0)

    shade = 0.30 + 0.85 * t
    out = np.stack([rgb[c] * shade for c in range(3)], axis=-1)

    sheen = np.clip((t - 0.75) / 0.25, 0, 1) * 0.28
    out = out * (1 - sheen[..., None]) + 255.0 * sheen[..., None]

    h, w = lum.shape
    yy, xx = np.mgrid[0:h, 0:w]
    if pattern == "knit":
        out *= np.where(yy % 3 == 0, 0.94, 1.0)[..., None]
        out *= np.where(xx % 4 == 0, 1.05, 1.0)[..., None]
    else:
        weave_a = (xx + yy) % 4 == 0
        weave_b = (xx - yy) % 4 == 0
        out *= np.where(weave_a, 1.06, 1.0)[..., None]
        out *= np.where(weave_b, 0.95, 1.0)[..., None]

    pale = opaque & (lum > hi * 0.985)
    out[pale] = out[pale] * 0.5 + 235.0 * 0.5

    for x in range(w):
        col = np.where(opaque[:, x])[0]
        if col.size == 0:
            continue
        breaks = np.where(np.diff(col) > 1)[0]
        starts = np.concatenate(([0], breaks + 1))
        ends = np.concatenate((breaks, [col.size - 1]))
        for s, e in zip(starts, ends):
            for y in (col[s], col[e]):
                out[y, x] = out[y, x] * 0.62 + GOLD * 0.38
            length = col[e] - col[s]
            if length >= 7:
                for frac in (0.30, 0.66):
                    y = col[s] + int(round(length * frac))
                    out[y, x] = out[y, x] * 0.55 + GOLD * 0.45

    # sparse stitch marks so the cloth reads as decorated at a distance
    for x in range(4, w, 12):
        for y in range(4, h, 12):
            if opaque[y, x]:
                out[y, x] = out[y, x] * 0.30 + GOLD * 0.70

    out = np.clip(out, 0, 255)
    result = src.copy()
    result[:, :, :3][opaque] = out[opaque]
    return Image.fromarray(result.astype(np.uint8), "RGBA")


def shade(c, target, amount):
    return tuple(round(a + (b - a) * amount) for a, b in zip(c, target))


def dyeable_icon():
    """Neutral scarf whose two crossing bands carry the four dye colours."""
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cloth = (226, 221, 213)
    outl = (32, 30, 36)
    dark = (176, 170, 162)
    d.arc([6, 2, 26, 16], 200, 340, fill=outl, width=8)
    d.arc([6, 2, 26, 16], 200, 340, fill=cloth, width=5)
    d.line([(7, 7), (12.5, 16.5)], fill=outl, width=8)
    d.line([(25, 7), (16.5, 16.5)], fill=outl, width=8)
    d.line([(7, 7), (12.5, 16.5)], fill=cloth, width=5)
    d.line([(25, 7), (16.5, 16.5)], fill=cloth, width=5)
    # dyed segments along the crossing bands
    d.line([(7.2, 7.2), (9.9, 11.9)], fill=(176, 46, 38, 255), width=4)
    d.line([(9.9, 11.9), (12.3, 16.1)], fill=(254, 216, 61, 255), width=4)
    d.line([(24.8, 7.2), (20.6, 11.9)], fill=(60, 68, 170, 255), width=4)
    d.line([(20.6, 11.9), (16.8, 16.1)], fill=(94, 124, 22, 255), width=4)
    # knot + tails
    d.ellipse([9, 14, 17, 22], fill=outl)
    d.ellipse([10, 15, 16, 21], fill=cloth)
    d.line([(10, 18), (15, 17)], fill=dark)
    d.polygon([(9, 19), (13, 20), (14, 26), (11, 31), (8, 30)], fill=cloth, outline=outl)
    d.polygon([(13, 20), (17, 21), (21, 28), (17, 30), (15, 26)], fill=dark, outline=outl)
    d.line([(11, 22), (10, 27)], fill=dark)
    for x, y, ex in ((8, 30, -1), (10, 31, 0), (16, 30, 1), (18, 28, 2)):
        d.line([(x, y), (x + ex, y + 2)], fill=cloth, width=1)
    return img


base = Image.open(ROOT / "publishing/scarf-base.png").convert("RGBA")
for name, rgb in DYES.items():
    tint(base, rgb, "knit").save(NECK / f"scarf_{name}.png", optimize=True)

dyeable_icon().save(ITEM / "scarf.png", optimize=True)

sheet = Image.new("RGB", (4 * 136 + 8, 136), "#14101f")
for i, name in enumerate(["black", "red", "blue", "white"]):
    im = Image.open(NECK / f"scarf_{name}.png").convert("RGBA").resize((128, 128), Image.LANCZOS)
    bg = Image.new("RGBA", im.size, "#2a2338")
    bg.alpha_composite(im)
    sheet.paste(bg.convert("RGB"), (8 + i * 136, 4))
sheet.save(ROOT / "publishing/scarf-dyes.png")
print("wrote 16 neck sheets, icon, preview")
