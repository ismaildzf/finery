"""Inspect a GLB mesh: stats + optional viewer copy + files.json refresh.

Usage: python mesh_stats.py [mesh_dir]
"""
import json
import pathlib
import sys

import trimesh
from PIL import Image

MESH_DIR = pathlib.Path(sys.argv[1] if len(sys.argv) > 1
                        else r"C:\MinecraftModding\mods\finery\_ai3d")

for glb in sorted(MESH_DIR.glob("*.glb")):
    print("\n" + "=" * 64)
    print("FILE:", glb.name, f"({glb.stat().st_size/1024:.0f} KB)")
    try:
        loaded = trimesh.load(str(glb), process=False)
        if isinstance(loaded, trimesh.Scene):
            print("scene nodes:", list(loaded.geometry.keys()))
            mesh = loaded.dump(concatenate=True)
        else:
            mesh = loaded
        print("verts:", len(mesh.vertices), "| faces:", len(mesh.faces))
        print("bounds min:", [round(v, 3) for v in mesh.bounds[0]])
        print("bounds max:", [round(v, 3) for v in mesh.bounds[1]])
        size = mesh.bounds[1] - mesh.bounds[0]
        print("size (x,y,z):", [round(float(v), 3) for v in size])
        uv = getattr(mesh.visual, "uv", None)
        print("uvs:", None if uv is None else uv.shape)
        mat = getattr(mesh.visual, "material", None)
        img = getattr(mat, "image", None) if mat is not None else None
        if img is not None:
            print("texture:", img.size)
            # save texture next to it for quick look
            tex_out = MESH_DIR / (glb.stem + "_tex.png")
            img.convert("RGBA").save(tex_out)
            print("texture saved:", tex_out.name)
        else:
            print("texture: none")
    except Exception as e:  # noqa: BLE001
        print("FAILED to load:", type(e).__name__, str(e)[:200])

files = [{"name": p.name} for p in sorted(MESH_DIR.glob("*.glb"))]
(MESH_DIR / "files.json").write_text(json.dumps(files, indent=1), encoding="utf-8")
print("\nfiles.json ->", [f["name"] for f in files])
