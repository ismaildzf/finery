"""Build the animated strips from the textures embedded in the owner's bbmodels.

The art is the owner's own 512x512 sheet (one band per item); it is cropped to
the band rectangle, kept at native resolution (320xH), and animated by sweeping
a soft specular sheen across it. 16 frames, seamless loop.
"""

import os

import numpy as np
from PIL import Image

FRAMES = 16

# (source png, band rect (x0, y0, x1, y1), output width, output height)
# the eyewrap strip is produced by tools/make_eye_wrap_strip.py
JOBS = {
    "headband": ("publishing/headband_crimson_lightning_512.png", (10, 10, 330, 66), 320, 56),
}


def build(src, rect, w, h, out_path):
    sheet = Image.open(src).convert("RGBA")
    band = sheet.crop(rect).resize((w, h), Image.LANCZOS)
    base = np.asarray(band).astype(np.float32)
    frames = np.zeros((FRAMES * h, w, 4), dtype=np.float32)

    xs = np.arange(w, dtype=np.float32)[None, :] / w
    ys = np.arange(h, dtype=np.float32)[:, None] / max(1, h - 1)
    for f in range(FRAMES):
        phase = f / FRAMES
        center = phase - 0.15 + (ys - 0.5) * 0.22
        d = (xs - center) / 0.075
        sheen = np.exp(-d * d)
        gain = 1.0 + 2.4 * sheen
        frame = base.copy()
        frame[:, :, :3] = np.clip(base[:, :, :3] * gain[:, :, None], 0.0, 255.0)
        frames[f * h:(f + 1) * h] = frame

    img = Image.fromarray(np.clip(frames, 0, 255).astype(np.uint8), "RGBA")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path)
    print("wrote", out_path, img.size)


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for name, (src, rect, w, h) in JOBS.items():
        build(os.path.join(root, src), rect, w, h,
              os.path.join(root, "publishing", name + "_strip.png"))


if __name__ == "__main__":
    main()
