"""Try Hunyuan3D-2.1 (best quality) with fallback to trellis-community one-shot."""
import os
import pathlib
import shutil
import sys
import time
import traceback

import httpx
from gradio_client import Client, handle_file

TOKEN = os.environ.get("HF_TOKEN", "")
assert TOKEN.startswith("hf_"), "set HF_TOKEN env var"

REF = r"C:\MinecraftModding\mods\finery\_refs\seraph_up.png"
OUT_DIR = pathlib.Path(r"C:\MinecraftModding\mods\finery\_ai3d")
OUT_DIR.mkdir(exist_ok=True)

TARGETS = {
    "hy21": "https://tencent-hunyuan3d-2.1.hf.space/config",
    "trellis_comm": "https://trellis-community-trellis.hf.space/config",
}


def reachable(url, tries=2):
    for i in range(tries):
        try:
            r = httpx.get(url, timeout=25, follow_redirects=True)
            print("reachable:", url, r.status_code)
            return r.status_code == 200
        except Exception as e:
            print(f"reach try {i+1} failed:", type(e).__name__)
            time.sleep(3)
    return False


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
                if not dst.exists():
                    shutil.copyfile(x, dst)
                saved.append(dst)
        elif isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, (list, tuple)):
            for v in x:
                walk(v)
    walk(result)
    print("saved files:", saved)
    return saved


def try_hy21():
    print("\n>>> Hunyuan3D-2.1 generation_all")
    c = Client("tencent/Hunyuan3D-2.1", token=TOKEN, verbose=False)
    gen = c.predict(
        caption=None,
        image=handle_file(REF),
        mv_image_front=None,
        mv_image_back=None,
        mv_image_left=None,
        mv_image_right=None,
        steps=30,
        guidance_scale=7.5,
        seed=42,
        octree_resolution=256,
        check_box_rembg=False,
        num_chunks=200000,
        randomize_seed=False,
        api_name="/generation_all",
    )
    print("gen result:", str(gen)[:400])
    saved = save_any(gen, "hy21_raw")
    glbs = [p for p in saved if p.suffix.lower() == ".glb"]
    if glbs:
        return True
    # try CPU export
    print(">>> CPU export via on_export_click")
    files = [as_path(x) for x in gen if as_path(x)]
    mesh_file = files[0] if files else None
    tex_file = files[1] if len(files) > 1 else None
    exp = c.predict(
        file_out=mesh_file,
        file_out2=tex_file,
        file_type="glb",
        reduce_face=True,
        export_texture=True,
        target_face_num=8000,
        api_name="/on_export_click",
    )
    print("export:", str(exp)[:300])
    save_any(exp, "hy21_glb")
    return True


def try_trellis_comm():
    print("\n>>> trellis-community one-shot")
    c = Client("trellis-community/TRELLIS", token=TOKEN, verbose=False)
    r = c.predict(
        image=handle_file(REF),
        multiimages=[],
        is_multiimage=False,
        seed=0,
        ss_guidance_strength=7.5,
        ss_sampling_steps=12,
        slat_guidance_strength=7.5,
        slat_sampling_steps=12,
        mesh_simplify=0.95,
        texture_size=1024,
        api_name="/generate_and_extract_glb",
    )
    print("result:", str(r)[:400])
    save_any(r, "trellis_comm")


if reachable(TARGETS["hy21"]):
    try:
        try_hy21()
    except Exception:
        traceback.print_exc()
        print("hy21 failed")
if reachable(TARGETS["trellis_comm"]):
    try:
        try_trellis_comm()
    except Exception:
        traceback.print_exc()
        print("trellis-community failed")
