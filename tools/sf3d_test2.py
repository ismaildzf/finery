"""Diagnostic: try SF3D with default settings on a tiny generated test image."""
import pathlib

from PIL import Image, ImageDraw
from gradio_client import Client, handle_file

out_dir = pathlib.Path(r"C:\MinecraftModding\mods\finery\_ai3d")
out_dir.mkdir(exist_ok=True)
img_path = out_dir / "test_shape.png"

im = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
d.ellipse([40, 40, 216, 216], fill=(220, 60, 60, 255), outline=(90, 20, 20, 255), width=8)
im.save(img_path)
print("TEST IMAGE:", img_path)

c = Client("stabilityai/stable-fast-3d")
try:
    r = c.predict(
        input_image=handle_file(str(img_path)),
        foreground_ratio=0.85,
        remesh_option="None",
        vertex_count=-1,
        texture_size=1024,
        api_name="/run_button",
    )
    print("SUCCESS:", r)
except Exception as e:  # noqa: BLE001
    print("FAILED:", type(e).__name__, "|", str(e)[:500])
