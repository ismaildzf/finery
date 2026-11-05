"""Retry HF Spaces image->3D with an authenticated HF token (ZeroGPU quota).

Usage: python hf3d_token_test.py [input_image] [tag]
"""
import os
import pathlib
import shutil
import sys

from gradio_client import Client, handle_file

TOKEN = os.environ.get("HF_TOKEN", "")
assert TOKEN.startswith("hf_"), "Set HF_TOKEN env var first"

INPUT = sys.argv[1] if len(sys.argv) > 1 else r"C:\MinecraftModding\mods\finery\_refs\wings_pack_v1.jpg"
TAG = sys.argv[2] if len(sys.argv) > 2 else "test"
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


def save(x, name):
    p = as_path(x)
    if not p:
        return None
    dst = OUT_DIR / (name + pathlib.Path(p).suffix)
    shutil.copyfile(p, dst)
    return dst


def run_sf3d():
    print(">>> SF3D with token")
    c = Client("stabilityai/stable-fast-3d", token=TOKEN)
    r = c.predict(
        input_image=handle_file(INPUT),
        foreground_ratio=0.85,
        remesh_option="None",
        vertex_count=-1,
        texture_size=1024,
        api_name="/run_button",
    )
    print("result:", str(r)[:250])
    print("SAVED:", save(r[-1], f"sf3d_{TAG}"))


def run_trellis():
    print(">>> TRELLIS.2 with token")
    c = Client("microsoft/TRELLIS.2", token=TOKEN)
    c.predict(api_name="/start_session")
    pre = c.predict(input=handle_file(INPUT), api_name="/preprocess_image")
    print("preprocessed:", as_path(pre))
    gen = c.predict(
        image=pre,
        seed=0,
        resolution="512",
        ss_guidance_strength=7.5,
        ss_guidance_rescale=0.7,
        ss_sampling_steps=12,
        ss_rescale_t=5.0,
        shape_slat_guidance_strength=7.5,
        shape_slat_guidance_rescale=0.5,
        shape_slat_sampling_steps=12,
        shape_slat_rescale_t=3.0,
        tex_slat_guidance_strength=1.0,
        tex_slat_guidance_rescale=0.0,
        tex_slat_sampling_steps=12,
        tex_slat_rescale_t=3.0,
        api_name="/image_to_3d",
    )
    print("generated:", str(gen)[:150])
    glb = c.predict(decimation_target=6000, texture_size=1024, api_name="/extract_glb")
    print("glb:", str(glb)[:250])
    print("SAVED:", save(glb, f"trellis2_{TAG}"))


for name, fn in (("SF3D", run_sf3d), ("TRELLIS.2", run_trellis)):
    try:
        fn()
        print(f"[{name}] OK")
    except Exception as e:  # noqa: BLE001
        print(f"[{name}] FAILED: {type(e).__name__}: {str(e)[:300]}")
