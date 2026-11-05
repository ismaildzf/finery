"""Try real image->3D via HF Spaces: TRELLIS.2 first, Hunyuan3D-2 as fallback."""
import pathlib
import shutil
import traceback

from gradio_client import Client, handle_file

INPUT = r"C:\MinecraftModding\mods\finery\_refs\wings_pack_v1.jpg"
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


def try_trellis():
    print("=== TRELLIS.2 ===")
    c = Client("microsoft/TRELLIS.2")
    c.predict(api_name="/start_session")
    print("session ok")
    pre = c.predict(input=handle_file(INPUT), api_name="/preprocess_image")
    print("preprocess ok:", as_path(pre))
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
    print("generation ok:", str(gen)[:150])
    glb = c.predict(decimation_target=6000, texture_size=1024, api_name="/extract_glb")
    print("extract:", glb)
    path = as_path(glb)
    if path:
        dst = OUT_DIR / ("trellis2_test" + pathlib.Path(path).suffix)
        shutil.copyfile(path, dst)
        print("SAVED:", dst)
        return True
    return False


def try_hunyuan():
    print("=== Hunyuan3D-2 ===")
    c = Client("tencent/Hunyuan3D-2")
    gen = c.predict(
        caption=None,
        image=handle_file(INPUT),
        mv_image_front=None,
        mv_image_back=None,
        mv_image_left=None,
        mv_image_right=None,
        steps=20,
        guidance_scale=5.0,
        seed=1234,
        octree_resolution=256,
        check_box_rembg=True,
        num_chunks=8000,
        randomize_seed=False,
        api_name="/generation_all",
    )
    print("generation ok:", str(gen)[:200])
    mesh_file = as_path(gen[0])
    tex_file = as_path(gen[1]) if isinstance(gen, (list, tuple)) and len(gen) > 1 else None
    print("mesh:", mesh_file, "| tex:", tex_file)
    exp = c.predict(
        file_out=mesh_file,
        file_out2=tex_file,
        file_type="glb",
        reduce_face=True,
        export_texture=True,
        target_face_num=8000,
        api_name="/on_export_click",
    )
    print("export:", str(exp)[:200])
    path = as_path(exp[-1] if isinstance(exp, (list, tuple)) else exp)
    if path:
        dst = OUT_DIR / ("hunyuan_test" + pathlib.Path(path).suffix)
        shutil.copyfile(path, dst)
        print("SAVED:", dst)
        return True
    return False


try:
    ok = try_trellis()
    if not ok:
        print("TRELLIS failed, trying Hunyuan...")
        try_hunyuan()
except Exception:
    traceback.print_exc()
    print("TRELLIS raised, trying Hunyuan...")
    try:
        try_hunyuan()
    except Exception:
        traceback.print_exc()
