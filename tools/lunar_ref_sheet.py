"""Contact sheet of downloaded Lunar reference stills (visual inspection helper)."""
import glob
import os
import sys

from PIL import Image, ImageDraw

REF = r"C:\Users\Administrator\AppData\Local\Temp\opencode\lunar_refs"


def sheet(prefix: str, out: str, cols: int = 5, cell: int = 260):
    files = sorted(glob.glob(os.path.join(REF, prefix + "_*.png")))
    if not files:
        print("no files for", prefix)
        return
    rows = (len(files) + cols - 1) // cols
    img = Image.new("RGB", (cols * (cell + 8) + 8, rows * (cell + 34) + 8), (30, 30, 34))
    d = ImageDraw.Draw(img)
    for k, f in enumerate(files):
        try:
            im = Image.open(f).convert("RGB")
        except Exception as exc:                    # noqa: BLE001
            print("skip", f, exc)
            continue
        im.thumbnail((cell, cell), Image.LANCZOS)
        cx = (k % cols) * (cell + 8) + 8
        cy = (k // cols) * (cell + 34) + 30
        img.paste(im, (cx + (cell - im.width) // 2, cy + (cell - im.height) // 2))
        idx = os.path.basename(f).rsplit("_", 1)[1].split(".")[0]
        d.text((cx + 4, cy - 24), idx, fill=(240, 235, 220))
        d.rectangle([cx - 2, cy - 2, cx + cell + 1, cy + cell + 1], outline=(70, 70, 78))
    img.save(out)
    print("wrote", out, len(files), "cells")


if __name__ == "__main__":
    prefix = sys.argv[1] if len(sys.argv) > 1 else "angel2025w"
    out = sys.argv[2] if len(sys.argv) > 2 else f"_ref_sheet_{prefix}.png"
    sheet(prefix, out)
