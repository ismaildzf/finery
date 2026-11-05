"""Per-face UV sanity test: map an 'F' onto one face and check orientation."""
import pathlib
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import render_mesh as rm  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "_design"
OUT.mkdir(exist_ok=True)

img = Image.new("RGBA", (32, 32), (255, 0, 255, 255))
d = ImageDraw.Draw(img)
d.rectangle([0, 0, 15, 15], fill=(20, 20, 20, 255))
# 'F' shape, 16x16
d.rectangle([2, 2, 3, 13], fill=(255, 255, 255, 255))      # vertical stem
d.rectangle([2, 2, 12, 3], fill=(255, 255, 255, 255))      # top bar
d.rectangle([2, 7, 9, 8], fill=(255, 255, 255, 255))       # middle bar
img.save(OUT / "_uvtest2.png")

# single quad at z=0 facing -z (north), 16x16 px, uv rect (0,0)-(16,16)
verts = [(0, 0, 0), (16, 0, 0), (16, 16, 0), (0, 16, 0)]
uvs = [(0, 0), (1, 0), (1, 1), (0, 1)]          # u right, v down
uvs = [(u * 0.5, v * 0.5) for u, v in uvs]      # 16/32 of the atlas
tris = [(0, 1, 2), (0, 2, 3)]

tex = np.asarray(Image.open(OUT / "_uvtest2.png").convert("RGBA"), float)
# render from -z looking toward +z (front of the quad): camera_front False flips painter order
for cam in (True, False):
    im = rm.render_view(np.array(verts, float), np.array(tris), np.array(uvs), tex,
                        np.eye(3), 256, camera_front=cam)
    Image.fromarray(im).save(OUT / f"_uvtest2_cam{cam}.png")
print("ok")
