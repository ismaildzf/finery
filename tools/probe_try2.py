"""Focused retry: SF3D (JPEG, no alpha) then Hunyuan3D-2 shape-only fallback."""
import os
import pathlib
import shutil
import sys
import traceback

from PIL import Image
from gradio_client import Client, handle_file

TOKEN = os.environ.get("HF_TOKEN", "")
assert TOKEN.startswith("hf_"), "set HF_TOKEN env var"

REF = r"C:\MinecraftModding\mods\finery\_refs\seraph_up.png"
OUT_DIR = pathlib.Path(r"C:\MinecraftModding\mods\finery\_ai3d")
OUT_DIR.mkdir(exist_ok=True)

# JPEG on white background (some spaces mishandle alpha)
white = Image.new("RGB", (1024, 1024), (255, 255, 255))
rgba = Image.open(REF).convert("RGBA")
white.paste(rgba, (0, 0), rgba)
jpg_path = OUT_DIR / "seraph_up_white.jpg"
white.save(jpg_path, quality=95)
print("jpeg ref:", jpg_path)


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


def sf3d():
    print(">>> SF3D (jpeg, token)")
    c = Client("stabilityai/stable-fast-3d", token=TOKEN, verbose=False)
    r = c.predict(
        input_image=handle_file(str(jpg_path)),
        foreground_ratio=0.85,
        remesh_option="None",
        vertex_count=-1,
        texture_size=1024,
        api_name="/run_button",
    )
    p = as_path(r[-1] if isinstance(r, (list, tuple)) else r)
    print("sf3d ok:", str(r)[:200])
    if p:
        dst = OUT_DIR / ("sf3d_seraph" + pathlib.Path(p).suffix)
        shutil.copyfile(p, dst)
        print("SAVED:", dst)
        return True
    return False


def hunyuan_shape():
    print(">>> Hunyuan3D-2 shape_generation (token)")
    c = Client("tencent/Hunyuan3D-2", token=TOKEN, verbose=False)
    r = c.predict(
        caption=None,
        image=handle_file(str(jpg_path)),
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
        randomize_seed=True,
        api_name="/shape_generation",
    )
    print("hy shape ok:", str(r)[:400])
    return r


try:
    sf3d()
except Exception:
    traceback.print_exc()
    print("SF3D failed -> trying Hunyuan shape-only")
    try:
        hunyuan_shape()
    except Exception:
        traceback.print_exc()
