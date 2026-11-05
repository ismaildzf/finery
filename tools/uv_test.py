"""UV sanity test: one box, atlas with letters, check face orientation."""
import pathlib
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import render_mesh as rm  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "_design"
OUT.mkdir(exist_ok=True)

# atlas: 64x64, every face region gets a letter in the top-left corner
img = Image.new("RGBA", (64, 64), (40, 40, 60, 255))
d = ImageDraw.Draw(img)
d.rectangle([0, 0, 63, 63], outline=(255, 255, 0, 255))
d.text((1, 1), "N", fill=(255, 0, 0, 255))
d.text((40, 1), "E", fill=(0, 255, 0, 255))
d.text((1, 40), "S", fill=(0, 128, 255, 255))
d.text((40, 40), "W", fill=(255, 0, 255, 255))
img.save(OUT / "_uvtest.png")

# cube 16 x 16 x 4, box uv at (0,0)
frm = np.array([0, 0, 0], float)
to = np.array([16, 16, 4], float)
uv = (0, 0)
dx, dy, dz = to - frm
rects = {
    "north": (uv[0] + dz, uv[1] + dz, uv[0] + dz + dx, uv[1] + dz + dy),
    "east": (uv[0], uv[1] + dz, uv[0] + dz, uv[1] + dz + dy),
    "south": (uv[0] + dz + dx, uv[1] + dz, uv[0] + 2 * dz + dx, uv[1] + dz + dy),
    "west": (uv[0] + 2 * dz + dx, uv[1] + dz, uv[0] + 2 * dz + 2 * dx, uv[1] + dz + dy),
    "up": (uv[0] + dz, uv[1], uv[0] + dz + dx, uv[1] + dz),
    "down": (uv[0] + dz + dx, uv[1], uv[0] + dz + 2 * dx, uv[1] + dz),
}
FACES = [
    ("north", [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]),
    ("south", [(1, 0, 1), (0, 0, 1), (0, 1, 1), (1, 1, 1)]),
    ("west", [(0, 0, 1), (0, 0, 0), (0, 1, 0), (0, 1, 1)]),
    ("east", [(1, 0, 0), (1, 0, 1), (1, 1, 1), (1, 1, 0)]),
    ("up", [(0, 0, 1), (1, 0, 1), (1, 0, 0), (0, 0, 0)]),
    ("down", [(0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)]),
]

verts, tris, uvs = [], [], []
for face, corners in FACES:
    r = rects[face]
    base = len(verts)
    for c in corners:
        p = frm + (to - frm) * np.array(c, float)
        verts.append(p)
        uu = r[0] + (r[2] - r[0]) * c[0]
        vv = r[1] + (r[3] - r[1]) * c[1]
        uvs.append((uu / 64.0, vv / 64.0))
    tris += [(base, base + 1, base + 2), (base, base + 2, base + 3)]

tex = np.asarray(Image.open(OUT / "_uvtest.png").convert("RGBA"), float)
sheet = Image.new("RGB", (420 * 3, 420), (16, 17, 20))
for i, R in enumerate((np.eye(3), rm.rot_y(-40) @ rm.rot_x(-20), rm.rot_y(35))):
    img2 = rm.render_view(np.array(verts), np.array(tris), np.array(uvs), tex, R, 420)
    sheet.paste(Image.fromarray(img2), (i * 420, 0))
sheet.save(OUT / "_uvtest_render.png")
print("done")
