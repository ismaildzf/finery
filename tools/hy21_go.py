"""Generate wings via tencent/Hunyuan3D-2.1 (shape+texture), CPU-export GLB.

Fallback: trellis-community/TRELLIS one-shot (image -> GLB).

Usage: python hy21_go.py
"""
import json
import os
import pathlib
import shutil
import sys
import traceback

from gradio_client import Client, handle_file

TOKEN = os.environ.get("HF_TOKEN", "")
assert TOKEN.startswith("hf_"), "set HF_TOKEN env var"

REF = sys.argv[1] if len(sys.argv) > 1 else r"C:\MinecraftModding\mods\finery\_refs\seraph_up.png"
TAG = sys.argv[2] if len(sys.argv) > 2 else "hy21"
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


def save_any(result, tag):
    saved = []

    def walk(x):
        if isinstance(x, str):
            if pathlib.Path(x).is_file():
                dst = OUT_DIR / f"{tag}{pathlib.Path(x).suffix}"
                shutil.copyfile(x, dst)
                saved.append(dst)
        elif isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, (list, tuple)):
            for v in x:
                walk(v)

    walk(result)
    print("saved:", saved)
    return saved


def try_hy21():
    print(">>> Hunyuan3D-2.1 /generation_all")
    c = Client("tencent/Hunyuan3D-2.1", token=TOKEN, verbose=False,
               httpx_kwargs={"timeout": 900})
    gen = c.predict(
        image=handle_file(REF),
        mv_image_front=None,
        mv_image_back=None,
        mv_image_left=None,
        mv_image_right=None,
        steps=30,
        guidance_scale=5.0,
        seed=1234,
        octree_resolution=256,
        check_box_rembg=False,
        num_chunks=8000,
        randomize_seed=False,
        api_name="/generation_all",
    )
    print("gen result:", str(gen)[:400])
    files = save_any(gen, f"{TAG}_gen")
    if any(p.suffix.lower() == ".glb" for p in files):
        print("GLB already returned by generation_all")
        return True

    print(">>> CPU export /on_export_click")
    mesh_file = as_path(gen[0])
    tex_file = as_path(gen[1])
    exp = c.predict(
        file_out=mesh_file,
        file_out2=tex_file,
        file_type="glb",
        reduce_face=True,
        export_texture=True,
        target_face_num=8000,
        api_name="/on_export_click",
    )
    print("export result:", str(exp)[:400])
    files = save_any(exp, f"{TAG}_glb")
    return any(p.suffix.lower() == ".glb" for p in files)


def try_trellis_comm():
    print(">>> trellis-community one-shot")
    c = Client("trellis-community/TRELLIS", token=TOKEN, verbose=False,
               httpx_kwargs={"timeout": 900})
    try:
        c.predict(api_name="/start_session")
    except Exception:
        print("start_session skipped")
    r = c.predict(
        image=handle_file(REF),
        multiimages=[],
        seed=0,
        ss_guidance_strength=7.5,
        ss_sampling_steps=12,
        slat_guidance_strength=3.0,
        slat_sampling_steps=12,
        multiimage_algo="stochastic",
        mesh_simplify=0.95,
        texture_size=1024,
        api_name="/generate_and_extract_glb",
    )
    print("result:", str(r)[:400])
    files = save_any(r, f"{TAG}_trellis")
    return any(p.suffix.lower() == ".glb" for p in files)


ok = False
try:
    ok = try_hy21()
    print("HY21 OK:", ok)
except Exception:
    traceback.print_exc()
    print("HY21 FAILED")

if not ok:
    try:
        ok = try_trellis_comm()
        print("TRELLIS-COMM OK:", ok)
    except Exception:
        traceback.print_exc()
        print("TRELLIS-COMM FAILED")

print("DONE. GLB in _ai3d:", [str(p.name) for p in OUT_DIR.glob('*.glb')])
