"""Generate a wing mesh (shape+texture) via tencent/Hunyuan3D-2 with HF token.

Quota: generation_all ~90s of the free 5 min/day; CPU export is free.
Usage: python hunyuan_try.py <input_image> <tag>
"""
import os
import pathlib
import shutil
import sys
import traceback

from gradio_client import Client, handle_file

TOKEN = os.environ.get("HF_TOKEN", "")
assert TOKEN.startswith("hf_"), "set HF_TOKEN env var"

INPUT = sys.argv[1] if len(sys.argv) > 1 else r"C:\MinecraftModding\mods\finery\_refs\seraph_up.png"
TAG = sys.argv[2] if len(sys.argv) > 2 else "seraph"
OUT_DIR = pathlib.Path(r"C:\MinecraftModding\mods\finery\_ai3d")
OUT_DIR.mkdir(exist_ok=True)


def as_path(x):
    if isinstance(x, str):
        return x
    if isinstance(x, dict):
        for key in ("path", "value", "model", "url"):
            if key in x:
                return as_path(x[key])
        return None
    if isinstance(x, (list, tuple)) and x:
        return as_path(x[0])
    return None


client = Client("tencent/Hunyuan3D-2", token=TOKEN)
print(">>> generation_all (shape + texture) ...")
try:
    gen = client.predict(
        caption=None,
        image=handle_file(INPUT),
        mv_image_front=None,
        mv_image_back=None,
        mv_image_left=None,
        mv_image_right=None,
        steps=30,
        guidance_scale=7.5,
        seed=1234,
        octree_resolution=256,
        check_box_rembg=False,
        num_chunks=200000,
        randomize_seed=False,
        api_name="/generation_all",
    )
except Exception:
    traceback.print_exc()
    sys.exit(1)

print("generation ok:", str(gen)[:300])
mesh_file = as_path(gen[0]) if isinstance(gen, (list, tuple)) else None
tex_file = None
for item in (gen if isinstance(gen, (list, tuple)) else []):
    p = as_path(item)
    if p and p != mesh_file and pathlib.Path(p).suffix.lower() in (".glb", ".obj", ".ply", ".fbx"):
        tex_file = p
        break
print("mesh_file:", mesh_file)
print("tex_file:", tex_file)

# CPU export (free)
print(">>> export GLB ...")
exp = client.predict(
    file_out=mesh_file,
    file_out2=tex_file,
    file_type="glb",
    reduce_face=True,
    export_texture=True,
    target_face_num=8000,
    api_name="/on_export_click",
)
print("export raw:", str(exp)[:300])
glb = None
for item in (exp if isinstance(exp, (list, tuple)) else [exp]):
    p = as_path(item)
    if p and pathlib.Path(p).suffix.lower() in (".glb", ".obj"):
        glb = p
if glb:
    dst = OUT_DIR / f"hunyuan_{TAG}.glb"
    shutil.copyfile(glb, dst)
    print("SAVED:", dst)
else:
    print("no glb in export result")
