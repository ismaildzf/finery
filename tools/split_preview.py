"""Split the AI wing mesh into two independent wings and render a preview.

Outputs:
  _ai3d/hy21_split_preview.png   (panels: joined, split front, split 3/4, split flap)
  _ai3d/hy21_split.mesh.json     (two-part mesh in blocks, roots at wing base)

Usage: python split_preview.py [mesh.glb]
"""
import json
import pathlib
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import render_mesh as rm  # noqa: E402

SRC = pathlib.Path(sys.argv[1] if len(sys.argv) > 1
                   else r"C:\MinecraftModding\mods\finery\_ai3d\hy21_gen.glb")
OUT_DIR = SRC.parent
SPAN = 2.6          # blocks, total width of both wings
GAP = 0.06          # blocks between the wing roots when displayed split


def submesh(verts, faces, uv, mask):
    f = faces[mask]
    used = np.unique(f)
    remap = -np.ones(len(verts), dtype=np.int64)
    remap[used] = np.arange(len(used))
    v = verts[used]
    u = uv[used] if uv is not None else None
    return v, remap[f], u


def main():
    verts, faces, uv, tex = rm.load_mesh(SRC)
    print("loaded:", verts.shape, faces.shape)

    lo, hi = verts.min(0), verts.max(0)
    scale = SPAN / float(hi[0] - lo[0])
    verts = verts * scale
    lo, hi = verts.min(0), verts.max(0)
    pivot = np.array([0.0, lo[1], (lo[2] + hi[2]) * 0.5])
    verts = verts - pivot
    print("scaled size:", np.round(hi - lo, 3), "blocks")

    cent = verts[faces].mean(axis=1)
    left_mask = cent[:, 0] < 0
    right_mask = ~left_mask
    lv, lf, luv = submesh(verts, faces, uv, left_mask)
    rv, rf, ruv = submesh(verts, faces, uv, right_mask)
    print("left:", len(lv), "verts", len(lf), "faces | right:", len(rv), "verts", len(rf), "faces")

    size = 460
    panels = []

    # 1) joined (as generated)
    panels.append(("as generated (joined)",
                   Image.fromarray(rm.render_view(verts, faces, uv, tex, np.eye(3), size))))

    # 2) split, straight back view, slight gap
    img = Image.new("RGB", (size, size), rm.BG)
    for part, off in ((lv, -GAP), (rv, GAP)):
        vv = part.copy()
        vv[:, 0] += off
        rgba = rm.render_view(vv, lf if part is lv else rf, luv if part is lv else ruv,
                              tex, np.eye(3), size, alpha=True)
        img.paste(Image.fromarray(rgba.astype(np.uint8)), (0, 0), Image.fromarray(rgba.astype(np.uint8)))
    panels.append(("split (two wings)", img))

    # 3) split 3/4 view
    R34 = rm.rot_y(-35) @ rm.rot_x(-12)
    img = Image.new("RGB", (size, size), rm.BG)
    for part, off in ((lv, -GAP), (rv, GAP)):
        vv = part.copy()
        vv[:, 0] += off
        rgba = rm.render_view(vv, lf if part is lv else rf, luv if part is lv else ruv,
                              tex, R34, size, alpha=True)
        img.paste(Image.fromarray(rgba.astype(np.uint8)), (0, 0), Image.fromarray(rgba.astype(np.uint8)))
    panels.append(("split - 3/4 view", img))

    # 4) split with independent flap (left raised, right lowered) — proves independent motion
    img = Image.new("RGB", (size, size), rm.BG)
    for part, f, u, off, ang in ((lv, lf, luv, -GAP, 18), (rv, rf, ruv, GAP, -18)):
        vv = part.copy()
        vv[:, 0] += off
        R = rm.rot_z(ang)
        rgba = rm.render_view(vv, f, u, tex, R, size, alpha=True)
        img.paste(Image.fromarray(rgba.astype(np.uint8)), (0, 0), Image.fromarray(rgba.astype(np.uint8)))
    panels.append(("independent flap test", img))

    cols = 2
    rows = (len(panels) + cols - 1) // cols
    sheet = Image.new("RGB", (size * cols, (size + 26) * rows), (16, 17, 20))
    d = ImageDraw.Draw(sheet)
    for i, (label, img) in enumerate(panels):
        x = (i % cols) * size
        y = (i // cols) * (size + 26)
        sheet.paste(img, (x, y + 26))
        d.text((x + 10, y + 7), label, fill=(235, 230, 210))
    out = OUT_DIR / "hy21_split_preview.png"
    sheet.save(out)
    print("preview saved:", out)

    # save two-part mesh json for the game
    data = {
        "units": "blocks",
        "texture": None,
        "parts": {
            "left": {
                "positions": [round(float(v), 5) for v in lv.reshape(-1)],
                "uvs": [round(float(v), 5) for v in luv.reshape(-1)] if luv is not None else [],
                "faces": lf.reshape(-1).tolist(),
            },
            "right": {
                "positions": [round(float(v), 5) for v in rv.reshape(-1)],
                "uvs": [round(float(v), 5) for v in ruv.reshape(-1)] if ruv is not None else [],
                "faces": rf.reshape(-1).tolist(),
            },
        },
    }
    js = OUT_DIR / "hy21_split.mesh.json"
    js.write_text(json.dumps(data), encoding="utf-8")
    print("mesh json saved:", js)


if __name__ == "__main__":
    main()
