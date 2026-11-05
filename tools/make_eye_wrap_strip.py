"""Port of the owner's Blockbench console script for the blindfold.

Generates the 320x64 band (the rect the model samples) as 16 vertical frames,
using the script's exact per-pixel formula, plus the static 512x512 sheet.
"""

import math
import os

import numpy as np
from PIL import Image

FRAMES = 16
W = 320
H = 64

# zones the script paints on the 512 sheet: (x, y, w, h)
SHEET_ZONES = [(10, 10, 320, 64), (340, 10, 150, 110), (10, 220, 320, 64), (340, 220, 150, 110)]


def render(canvas, rx, ry, rw, rh, t):
    ix = np.arange(rw, dtype=np.float32)[None, :]
    iy = np.arange(rh, dtype=np.float32)[:, None]
    wave_y = np.sin((ix / rw) * math.pi * 2.0) * 2.5
    v = iy / rh
    edge_round = np.sin(v * math.pi)
    shimmer = np.sin((ix * 0.035) - (iy * 0.05) + t * 2.5)
    secondary = np.cos((ix * 0.02) + (iy * 0.08) - t * 1.8)
    specular = np.power(np.maximum(0.0, shimmer), 4)
    base = 115.0 + 115.0 * edge_round
    fold = np.sin(ix * 0.07 + iy * 0.09 + wave_y * 0.2) * 22.0
    gloss = specular * 85.0 + np.maximum(0.0, secondary) * 25.0
    val = np.clip(np.floor(base + fold + gloss), 70, 255)
    rim = (iy < 4) | (iy > rh - 5)
    val = np.where(rim, np.floor(val * 0.42), val)
    canvas[ry:ry + rh, rx:rx + rw, :3] = val[:, :, None]
    canvas[ry:ry + rh, rx:rx + rw, 3] = 255.0


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pub = os.path.join(root, "publishing")
    os.makedirs(pub, exist_ok=True)

    strip = np.zeros((FRAMES * H, W, 4), dtype=np.float32)
    for f in range(FRAMES):
        t = (f / FRAMES) * math.pi * 2.0
        frame = np.zeros((512, 512, 4), dtype=np.float32)
        render(frame, 10, 220, W, H, t)
        strip[f * H:(f + 1) * H] = frame[220:220 + H, 10:10 + W]

    Image.fromarray(np.clip(strip, 0, 255).astype(np.uint8), "RGBA") \
        .save(os.path.join(pub, "eye_wrap_strip.png"))
    print("wrote eye_wrap_strip.png", (W, FRAMES * H))

    sheet = np.zeros((512, 512, 4), dtype=np.float32)
    for (x, y, w, h) in SHEET_ZONES:
        render(sheet, x, y, w, h, 0.4)
    Image.fromarray(np.clip(sheet, 0, 255).astype(np.uint8), "RGBA") \
        .save(os.path.join(pub, "blindfold_pure_clean_512.png"))
    print("wrote blindfold_pure_clean_512.png (512, 512)")


if __name__ == "__main__":
    main()
