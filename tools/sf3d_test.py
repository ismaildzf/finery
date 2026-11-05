"""Test the Stable Fast 3D HF Space pipeline end-to-end (image -> GLB)."""
import pathlib
import shutil

from gradio_client import Client, handle_file

INPUT = r"C:\MinecraftModding\mods\finery\_refs\wings_pack_v1.jpg"
OUT_DIR = pathlib.Path(r"C:\MinecraftModding\mods\finery\_ai3d")
OUT_DIR.mkdir(exist_ok=True)


def as_path(x):
    """gradio_client may return str, dict or nested list for file outputs."""
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


client = Client("stabilityai/stable-fast-3d")
result = client.predict(
    input_image=handle_file(INPUT),
    foreground_ratio=0.85,
    remesh_option="Quad",
    vertex_count=2000,
    texture_size=1024,
    api_name="/run_button",
)
print("RAW RESULT:", result)

model_path = as_path(result[-1] if isinstance(result, (list, tuple)) else result)
preview_path = as_path(result[0]) if isinstance(result, (list, tuple)) and len(result) > 1 else None
print("MODEL PATH:", model_path)
print("PREVIEW PATH:", preview_path)

if model_path:
    dst = OUT_DIR / ("sf3d_test" + pathlib.Path(model_path).suffix)
    shutil.copyfile(model_path, dst)
    print("SAVED:", dst)
if preview_path:
    dst2 = OUT_DIR / ("sf3d_test_preview" + pathlib.Path(preview_path).suffix)
    shutil.copyfile(preview_path, dst2)
    print("SAVED PREVIEW:", dst2)
