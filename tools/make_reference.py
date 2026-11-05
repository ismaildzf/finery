"""Render a clean reference image of a wing style (wings only, transparent
background, no player) for AI image->3D pipelines.

Usage: python make_reference.py [wing_name] [tag]
Outputs: _refs/<tag>_<pose>.png
"""
import math
import os
import sys

from PIL import Image

MOD = r"C:\MinecraftModding\mods\finery"
sys.path.insert(0, MOD)

import wing_v6_preview as W  # noqa: E402


def render(name, pose, out_path, scale=2):
    # higher-res canvas, same framing as the preview sheets
    W.S = 13 * scale
    W.PW, W.PH = 860 * scale, 560 * scale
    W.OY = 300 * scale
    raise_, sweep, phase, _yaw, airborne = pose
    tex = Image.open(os.path.join(W.TEX, name + ".png")).convert("RGBA")
    scene = W.Scene(tex, (0, 0, 0, 0))
    W.build_wing(scene, name, raise_, sweep, phase, airborne)
    img = scene.img
    bbox = img.getchannel("A").getbbox()
    if not bbox:
        raise SystemExit("empty render for " + name)
    pad = 16
    l, t, r, b = bbox
    l = max(0, l - pad)
    t = max(0, t - pad)
    r = min(img.width, r + pad)
    b = min(img.height, b + pad)
    img = img.crop((l, t, r, b))
    side = max(img.width, img.height)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.alpha_composite(img, ((side - img.width) // 2, (side - img.height) // 2))
    if side != 1024:
        canvas = canvas.resize((1024, 1024), Image.LANCZOS)
    canvas.save(out_path)
    print("wrote", out_path, canvas.size)


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "seraph_wings"
    tag = sys.argv[2] if len(sys.argv) > 2 else "ref"
    out_dir = os.path.join(MOD, "_refs")
    os.makedirs(out_dir, exist_ok=True)
    poses = {
        "idle": (0.34, 0.30, 0.60, 0.0, False),
        "up": (0.56, 0.31, math.pi / 2, 0.0, True),
    }
    for label, pose in poses.items():
        render(name, pose, os.path.join(out_dir, f"{tag}_{label}.png"))
