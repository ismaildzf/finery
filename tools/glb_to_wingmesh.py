"""Convert an AI-generated GLB wing mesh into the mod's compact mesh format.

Usage:
  python glb_to_wingmesh.py <input.glb> [out_dir] [--span 2.6] [--rot x,y,z]

Outputs (in out_dir, default = same folder as input):
  <name>.mesh.json   positions (blocks, Y-up, pivot at wing centre) + uvs + faces
  <name>.png         texture atlas extracted from the GLB

Prints mesh stats (triangles, bounds, uvs) so orientation can be checked.
"""
import argparse
import json
import pathlib
import sys

import numpy as np
import trimesh
from PIL import Image


def rotx(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], dtype=np.float64)


def roty(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], dtype=np.float64)


def rotz(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=np.float64)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("glb")
    ap.add_argument("out_dir", nargs="?", default=None)
    ap.add_argument("--span", type=float, default=2.6,
                    help="final size (blocks) of the largest dimension")
    ap.add_argument("--rot", default="0,0,0",
                    help="extra rotation degrees x,y,z applied before export")
    ap.add_argument("--tex", type=int, default=1024, help="max texture size")
    args = ap.parse_args()

    src = pathlib.Path(args.glb)
    out_dir = pathlib.Path(args.out_dir) if args.out_dir else src.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    name = src.stem

    loaded = trimesh.load(str(src), process=False)
    if isinstance(loaded, trimesh.Scene):
        mesh = loaded.dump(concatenate=True)
    else:
        mesh = loaded

    verts = np.asarray(mesh.vertices, dtype=np.float64)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    uvs = getattr(mesh.visual, "uv", None)
    print("vertices:", len(verts), "faces:", len(faces))
    if uvs is not None:
        uvs = np.asarray(uvs, dtype=np.float64)
        print("uvs:", uvs.shape)
        if len(uvs) != len(verts):
            print("WARNING: uv count != vertex count; dropping uvs")
            uvs = None

    rx, ry, rz = [float(v) for v in args.rot.split(",")]
    extra = rotz(np.radians(rz)) @ roty(np.radians(ry)) @ rotx(np.radians(rx))
    verts = verts @ extra.T

    lo = verts.min(axis=0)
    hi = verts.max(axis=0)
    size = hi - lo
    print("raw bounds min:", np.round(lo, 4), "max:", np.round(hi, 4))
    print("raw size (x,y,z):", np.round(size, 4))

    # scale so the largest dimension becomes --span blocks
    scale = args.span / float(size.max())
    verts = verts * scale
    lo = verts.min(axis=0)
    hi = verts.max(axis=0)

    # pivot: centre on X (symmetry axis) and Z, top on Y (attachment area)
    pivot = np.array([(lo[0] + hi[0]) * 0.5, hi[1], (lo[2] + hi[2]) * 0.5])
    rel = verts - pivot
    print("scaled size (blocks):", np.round(hi - lo, 4))

    left = right = None
    if faces.size:
        # split wings by x centroid sign (relative to pivot)
        cent = rel[faces].mean(axis=1)
        left_idx = np.where(cent[:, 0] < 0)[0]
        right_idx = np.where(cent[:, 0] >= 0)[0]
        left = left_idx.tolist()
        right = right_idx.tolist()

    tex_path = None
    img = None
    mat = getattr(mesh.visual, "material", None)
    if mat is not None:
        img = getattr(mat, "image", None)
        if img is None:
            base = getattr(mat, "baseColorTexture", None)
            img = getattr(base, "image", None) if base is not None else None
    if img is not None:
        img = img.convert("RGBA")
        if max(img.size) > args.tex:
            img = img.resize((args.tex, args.tex), Image.LANCZOS)
        tex_path = out_dir / (name + ".png")
        img.save(tex_path)
        print("texture:", tex_path, img.size)
    else:
        # fall back to a texture extracted from the GLB next to it
        for cand in ("_tex0.png", "_tex0.jpg", "_tex.png"):
            c = src.with_name(src.stem + cand)
            if c.exists():
                img = Image.open(c).convert("RGBA")
                if max(img.size) > args.tex:
                    img = img.resize((args.tex, args.tex), Image.LANCZOS)
                tex_path = out_dir / (name + ".png")
                img.save(tex_path)
                print("texture (sidecar):", tex_path, img.size)
                break
        if tex_path is None:
            print("WARNING: no embedded texture found")

    out = {
        "name": name,
        "units": "blocks",
        "pivot": [0.0, 0.0, 0.0],
        "positions": [round(float(v), 5) for v in rel.reshape(-1)],
        "uvs": [round(float(v), 5) for v in uvs.reshape(-1)] if uvs is not None else [],
        "faces": faces.reshape(-1).tolist(),
        "parts": {"left": left, "right": right},
        "texture": tex_path.name if tex_path else None,
    }
    json_path = out_dir / (name + ".mesh.json")
    json_path.write_text(json.dumps(out), encoding="utf-8")
    print("wrote", json_path)


if __name__ == "__main__":
    main()
