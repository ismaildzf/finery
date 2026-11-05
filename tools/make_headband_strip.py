"""Port of the owner's animated crimson-lightning headband script.

renderCrimsonLightningFrame -> 16 frames of the 320x56 band the model samples.
"""

import math
import os

import numpy as np
from PIL import Image

FRAMES = 16
W = 320
H = 56


def wave(ix, width, freq, phase):
    return np.sin((ix / width) * math.pi * 2.0 * freq + phase)


def frame(t):
    ix = np.arange(W, dtype=np.float32)[None, :]
    iy = np.arange(H, dtype=np.float32)[:, None]
    half = (H - 1) / 2.0

    smooth = (wave(ix, W, 6, t * 2.0) + wave(ix, W, 12, -t * 3.0) * 0.4 + 1.4) / 2.8
    flame_reach = 4.5 + smooth * 6.5

    bolt = wave(ix, W, 10, -t * 7.5) + wave(ix, W, 27, t * 11.0) * 0.45 \
        + wave(ix, W, 55, -t * 16.0) * 0.22
    bolt_pos = 3.5 + np.abs(bolt) * 4.2
    bolt_pulse = 0.65 + 0.35 * np.sin(t * 9.0 + (ix / W) * math.pi * 6.0)

    dist_edge = np.minimum(iy, (H - 1) - iy)
    center_ratio = dist_edge / half

    heat = np.where(dist_edge < flame_reach,
                    np.power(np.maximum(0.0, 1.0 - dist_edge / flame_reach), 1.5), 0.0)

    dist_bolt = np.abs(dist_edge - bolt_pos)
    core = np.where(dist_bolt < 1.1, (1.0 - dist_bolt / 1.1) * bolt_pulse, 0.0)
    aura = np.where(dist_bolt < 3.8, np.power(np.maximum(0.0, 1.0 - dist_bolt / 3.8), 2) * bolt_pulse, 0.0)

    dark = (wave(ix, W, 3, t) + 1.0) * 0.5
    void_red = 8.0 + (1.0 - center_ratio) * 14.0 + dark * 8.0

    combined_red = np.maximum(heat * 235.0, aura * 250.0)
    r = np.minimum(255, np.round(void_red + combined_red + core * 255.0))
    g = np.minimum(255, np.round(2.0 + heat * 28.0 + aura * 35.0 + core * 210.0))
    b = np.minimum(255, np.round(5.0 + heat * 18.0 + aura * 55.0 + core * 225.0))

    rim = dist_edge < 1.6
    r = np.where(rim, 255.0, r)
    g = np.where(rim, 210.0, g)
    b = np.where(rim, 200.0, b)

    out = np.zeros((H, W, 4), dtype=np.float32)
    out[:, :, 0] = r
    out[:, :, 1] = g
    out[:, :, 2] = b
    out[:, :, 3] = 255.0
    return out


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    strip = np.zeros((FRAMES * H, W, 4), dtype=np.float32)
    for f in range(FRAMES):
        strip[f * H:(f + 1) * H] = frame((f / FRAMES) * math.pi * 2.0)
    path = os.path.join(root, "publishing", "headband_strip.png")
    Image.fromarray(np.clip(strip, 0, 255).astype(np.uint8), "RGBA").save(path)
    print("wrote", path, (W, FRAMES * H))


if __name__ == "__main__":
    main()
