"""Overlay generator-zone (red, x0,y0,w,h) and preview-zone (blue, x0,y0,x1,y1)
rectangles on the feather atlas so the real layout is visible."""
from PIL import Image, ImageDraw

ATLAS = r"C:\MinecraftModding\mods\finery\src\main\resources\assets\finery\textures\wings\seraph_wings.png"
OUT = r"C:\MinecraftModding\mods\finery\_atlas_zones.png"

ZONES = {
    "P":  (1.0, 1.0, 4.0, 15.0),
    "S":  (7.0, 1.0, 4.5, 14.0),
    "C1": (1.0, 18.0, 5.0, 11.0),
    "C0": (8.0, 18.0, 5.0, 9.0),
    "SC": (1.0, 31.0, 5.0, 8.0),
}
PXU = 4  # 256/64

im = Image.open(ATLAS).convert("RGBA")
# darken the checker so shapes pop
bg = Image.new("RGBA", im.size, (40, 40, 48, 255))
bg.alpha_composite(im)
im = bg.convert("RGB")
d = ImageDraw.Draw(im)
for name, (x0, y0, a, b) in ZONES.items():
    # red: generator reading (w,h)
    d.rectangle([x0 * PXU, y0 * PXU, (x0 + a) * PXU - 1, (y0 + b) * PXU - 1],
                outline=(255, 60, 60), width=2)
    d.text((x0 * PXU + 4, y0 * PXU + 4), name + " gen", fill=(255, 120, 120))
    # blue: preview reading (x1,y1)
    d.rectangle([min(x0 * PXU, a * PXU), min(y0 * PXU, b * PXU),
                 max(x0 * PXU, a * PXU), max(y0 * PXU, b * PXU)],
                outline=(80, 140, 255), width=2)
    d.text((x0 * PXU + 4, y0 * PXU + 20), name + " prv", fill=(140, 180, 255))

im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
im.save(OUT)
print("wrote", OUT)
