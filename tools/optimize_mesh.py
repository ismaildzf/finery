"""Vertex-clustering decimation that keeps UVs (unlike quadric decimation).

Merges vertices that fall into the same grid cell, averages position/UV, drops
degenerate triangles. Output keeps the same JSON layout so the renderer needs
no change.

Usage: python optimize_mesh.py <in.mesh.json> [out.mesh.json] [--cell 0.012]
"""
import argparse
import json
import pathlib
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import render_mesh as rm  # noqa: E402


def cluster_part(part, cell):
    pos = np.asarray(part["positions"], dtype=np.float64).reshape(-1, 3)
    uvs = np.asarray(part.get("uvs") or [], dtype=np.float64).reshape(-1, 2)
    faces = np.asarray(part["faces"], dtype=np.int64).reshape(-1, 3)

    keys = np.floor(pos / cell).astype(np.int64)
    _, inverse, counts = np.unique(keys, axis=0, return_inverse=True, return_counts=True)
    n = counts.size

    # average position and uv per cluster
    new_pos = np.zeros((n, 3))
    np.add.at(new_pos, inverse, pos)
    new_pos /= counts[:, None]
    if uvs.size:
        new_uv = np.zeros((n, 2))
        np.add.at(new_uv, inverse, uvs)
        new_uv /= counts[:, None]
    else:
        new_uv = np.zeros((n, 2))

    new_faces = inverse[faces]
    good = (new_faces[:, 0] != new_faces[:, 1]) & (new_faces[:, 1] != new_faces[:, 2]) \
        & (new_faces[:, 0] != new_faces[:, 2])
    new_faces = new_faces[good]
    # drop duplicate triangles
    ordered = np.sort(new_faces, axis=1)
    _, uniq = np.unique(ordered, axis=0, return_index=True)
    new_faces = new_faces[np.sort(uniq)]

    return {
        "positions": [round(float(v), 5) for v in new_pos.reshape(-1)],
        "uvs": [round(float(v), 5) for v in new_uv.reshape(-1)],
        "faces": new_faces.reshape(-1).tolist(),
    }, len(faces), len(new_faces)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--cell", type=float, default=0.012, help="grid cell in blocks")
    ap.add_argument("--tex")
    ap.add_argument("--preview")
    args = ap.parse_args()

    src = pathlib.Path(args.src)
    out = pathlib.Path(args.out) if args.out else src.with_name(src.stem + "_opt.json")
    data = json.loads(src.read_text(encoding="utf-8"))

    new_parts = {}
    for name in ("left", "right"):
        part, before, after = cluster_part(data["parts"][name], args.cell)
        new_parts[name] = part
        print(f"{name}: {before} -> {after} triangles ({100.0 * after / before:.1f}%)")
    data["parts"] = new_parts
    out.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
    print("saved:", out, f"{out.stat().st_size / 1e6:.2f} MB")

    if args.preview and args.tex:
        tex = np.asarray(Image.open(args.tex).convert("RGBA"), dtype=np.float64)
        size = 512
        panels = []
        for name, rot in (("front", np.eye(3)), ("3/4", rm.rot_y(-35) @ rm.rot_x(-12))):
            verts = []
            faces = []
            uvs = []
            offset = 0
            for part_name, shift in (("left", -0.05), ("right", 0.05)):
                p = new_parts[part_name]
                v = np.asarray(p["positions"], dtype=np.float64).reshape(-1, 3).copy()
                v[:, 0] += shift
                f = np.asarray(p["faces"], dtype=np.int64).reshape(-1, 3) + offset
                u = np.asarray(p["uvs"], dtype=np.float64).reshape(-1, 2)
                verts.append(v)
                faces.append(f)
                uvs.append(u)
                offset += len(v)
            img = Image.new("RGB", (size, size), rm.BG)
            rgba = rm.render_view(np.vstack(verts), np.vstack(faces), np.vstack(uvs),
                                  tex, rot, size, alpha=True)
            pi = Image.fromarray(rgba.astype(np.uint8), "RGBA")
            img.paste(pi, (0, 0), pi)
            panels.append((name, img))

        sheet = Image.new("RGB", (size * 2, size + 26), (14, 15, 18))
        d = ImageDraw.Draw(sheet)
        for i, (label, img) in enumerate(panels):
            sheet.paste(img, (i * size, 26))
            d.text((i * size + 10, 8), label, fill=(240, 235, 215))
        sheet.save(args.preview)
        print("preview:", args.preview)


if __name__ == "__main__":
    main()
