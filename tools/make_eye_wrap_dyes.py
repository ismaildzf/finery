"""Generate the dyed eyewrap sheets and the single "dyeable" item icon.

The tint keeps a wide luminance range (so the weave and folds survive), adds a
procedural weave, a lighter hem along every cloth edge, and keeps the brightest
source pixels pale so stitched trim stays visible on dark dyes.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
HEAD = ROOT / "src/main/resources/assets/finery/textures/head"
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

    # keep stitched trim / fringe pale instead of dyeing it flat
    pale = opaque & (lum > hi * 0.985)
    out[pale] = out[pale] * 0.5 + 235.0 * 0.5

    # lighter hem on the first/last opaque pixel of each column run
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


def dyeable_icon():
    """Neutral wrap with four dye stripes so one icon reads as 'recolorable'."""
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    band = [(3, 12), (29, 10), (30, 20), (4, 22)]
    d.polygon(band, fill=(52, 50, 58, 255))
    inner = [(4, 13), (28, 11.4), (29, 19), (5, 20.6)]
    d.polygon(inner, fill=(214, 210, 202, 255))
    stripes = [(176, 46, 38), (254, 216, 61), (60, 68, 170), (94, 124, 22)]
    for i, x in enumerate((6, 10, 14, 18)):
        d.line([(x, 15.4 - i * 0.15), (x + 3, 15.0 - i * 0.15)], fill=stripes[i] + (255,), width=2)
    d.rounded_rectangle([22, 12, 29, 19], radius=2, fill=(38, 36, 44, 255))
    d.polygon([(23, 17), (26, 17), (25, 26), (22, 26)], fill=(70, 66, 76, 255))
    return img


base = Image.open(HEAD / "eye_wrap_white.png").convert("RGBA")
for name, rgb in DYES.items():
    tint(base, rgb, "weave").save(HEAD / f"eye_wrap_{name}.png", optimize=True)

dyeable_icon().save(ITEM / "eye_wrap.png", optimize=True)

sheet = Image.new("RGB", (4 * 136 + 8, 136), "#14101f")
for i, name in enumerate(["black", "red", "blue", "white"]):
    im = Image.open(HEAD / f"eye_wrap_{name}.png").convert("RGBA").crop((0, 192, 128, 256))
    im = im.resize((128, 64), Image.NEAREST)
    bg = Image.new("RGBA", im.size, "#2a2338")
    bg.alpha_composite(im)
    sheet.paste(bg.convert("RGB"), (8 + i * 136, 8))
sheet.save(ROOT / "publishing/eye-wrap-dyes.png")
print("wrote 16 head sheets, icon, preview")
