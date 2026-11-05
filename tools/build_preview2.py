"""Clean 3-panel preview: joined vs split vs independent flap + texture inset."""
import pathlib
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import render_mesh as rm  # noqa: E402

SRC = pathlib.Path(r"C:\MinecraftModding\mods\finery\_ai3d\hy21_gen.glb")
OUT = SRC.with_name("hy21_split2.png")
TEX = SRC.with_name("hy21_gen_tex0.png")
SPAN = 2.6
GAP = 0.05
SIZE = 520


def submesh(verts, faces, uv, mask):
    f = faces[mask]
    used = np.unique(f)
    remap = -np.ones(len(verts), dtype=np.int64)
    remap[used] = np.arange(len(used))
    return verts[used], remap[f], (uv[used] if uv is not None else None)


def paste_rgba(base, rgba):
    img = Image.fromarray(rgba.astype(np.uint8), "RGBA")
    base.paste(img, (0, 0), img)


def main():
    verts, faces, uv, tex = rm.load_mesh(SRC)
    lo, hi = verts.min(0), verts.max(0)
    verts = verts * (SPAN / float(hi[0] - lo[0]))
    lo, hi = verts.min(0), verts.max(0)
    verts = verts - np.array([0.0, lo[1], (lo[2] + hi[2]) * 0.5])

    cent = verts[faces].mean(1)
    lm = cent[:, 0] < 0
    lv, lf, luv = submesh(verts, faces, uv, lm)
    rv, rf, ruv = submesh(verts, faces, uv, ~lm)

    panels = []

    panels.append(("1. AS GENERATED (wings joined)",
                   Image.fromarray(rm.render_view(verts, faces, uv, tex, np.eye(3), SIZE))))

    img = Image.new("RGB", (SIZE, SIZE), rm.BG)
    for v, f, u, off in ((lv, lf, luv, -GAP), (rv, rf, ruv, GAP)):
        vv = v.copy()
        vv[:, 0] += off
        paste_rgba(img, rm.render_view(vv, f, u, tex, np.eye(3), SIZE, alpha=True))
    panels.append(("2. SPLIT INTO TWO INDEPENDENT WINGS", img))

    img = Image.new("RGB", (SIZE, SIZE), rm.BG)
    for v, f, u, off, ang in ((lv, lf, luv, -GAP, 16), (rv, rf, ruv, GAP, -16)):
        vv = v.copy()
        vv[:, 0] += off
        paste_rgba(img, rm.render_view(vv, f, u, tex, rm.rot_z(ang), SIZE, alpha=True))
    panels.append(("3. INDEPENDENT FLAP (left up / right down)", img))

    img = Image.new("RGB", (SIZE, SIZE), rm.BG)
    for v, f, u, off in ((lv, lf, luv, -GAP), (rv, rf, ruv, GAP)):
        vv = v.copy()
        vv[:, 0] += off
        paste_rgba(img, rm.render_view(vv, f, u, tex, rm.rot_y(-40) @ rm.rot_x(-10), SIZE, alpha=True))
    panels.append(("4. SPLIT - 3/4 VIEW", img))

    cols, rows = 2, 2
    sheet = Image.new("RGB", (SIZE * cols, (SIZE + 30) * rows), (14, 15, 18))
    d = ImageDraw.Draw(sheet)
    for i, (label, p) in enumerate(panels):
        x, y = (i % cols) * SIZE, (i // cols) * (SIZE + 30)
        sheet.paste(p, (x, y + 30))
        d.text((x + 10, y + 9), label, fill=(240, 235, 215))

    # texture inset (bottom right corner of panel 4)
    if TEX.exists():
        t = Image.open(TEX).convert("RGB").resize((150, 150), Image.LANCZOS)
        sheet.paste(t, (SIZE * 2 - 160, SIZE + 30 + SIZE - 160))
        d.text((SIZE * 2 - 160, SIZE + 30 + SIZE - 180), "TEXTURE (ivory)", fill=(240, 235, 215))

    sheet.save(OUT)
    print("saved:", OUT, sheet.size)


if __name__ == "__main__":
    main()
