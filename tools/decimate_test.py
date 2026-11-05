"""Test quadric decimation — does it keep UVs/texture?"""
import pathlib

import trimesh

SRC = pathlib.Path(r"C:\MinecraftModding\mods\finery\_ai3d\hy21_gen.glb")
OUT = SRC.with_name("hy21_dec.glb")

m = trimesh.load(str(SRC), process=False)
m = m.to_geometry() if isinstance(m, trimesh.Scene) else m
uv = getattr(m.visual, "uv", None)
print("orig:", len(m.vertices), "verts,", len(m.faces), "faces, uv:",
      None if uv is None else uv.shape)

try:
    d = m.simplify_quadric_decimation(face_count=8000)
    duv = getattr(d.visual, "uv", None)
    print("decimated:", len(d.vertices), "verts,", len(d.faces), "faces, uv:",
          None if duv is None else duv.shape)
    d.export(str(OUT))
    print("saved:", OUT)
except Exception as e:  # noqa: BLE001
    print("FAILED:", type(e).__name__, str(e)[:300])
