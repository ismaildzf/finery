"""Build the v6 presentation sheets: overview, zoomed detail, and Lunar comparisons.

Run from the mod folder after re-rendering the four wing sheets with
wing_v6_preview.py.  Pose 0 (idle-back) = x 0..860, pose 1 (flap-up) = 860..1720,
character centre x=430, shoulder line y=300, 13 px per texel.
"""
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
REF = r"C:\Users\Administrator\AppData\Local\Temp\opencode\lunar_refs"

WINGS = ["seraph_wings", "emberwing", "voidwing", "fae_wings"]
CELL = (30, 20, 830, 540)          # pose-0 crop around the character


def pose_img(name, pose=0, box=CELL):
    im = Image.open(os.path.join(MOD, "wing_v6_%s.png" % name)).convert("RGB")
    x0, y0, x1, y1 = box
    return im.crop((pose * 860 + x0, y0, pose * 860 + x1, y1))


def overview():
    cw, ch = 400, 260
    img = Image.new("RGB", (4 * (cw + 8) + 8, 2 * (ch + 8) + 8), (44, 48, 58))
    for i, name in enumerate(WINGS):
        for j, pose in enumerate((0, 1)):
            cell = pose_img(name, pose).resize((cw, ch), Image.LANCZOS)
            img.paste(cell, (8 + i * (cw + 8), 8 + j * (ch + 8)))
    img.save(os.path.join(MOD, "wing_v6_overview.png"))
    print("wrote wing_v6_overview.png")


def detail():
    cw, ch = 520, 400
    box = (170, 50, 690, 450)      # tighter on the upper body
    img = Image.new("RGB", (2 * (cw + 8) + 8, 2 * (ch + 8) + 8), (44, 48, 58))
    for i, name in enumerate(WINGS):
        cell = pose_img(name, 0, box).resize((cw, ch), Image.LANCZOS)
        x = 8 + (i % 2) * (cw + 8)
        y = 8 + (i // 2) * (ch + 8)
        img.paste(cell, (x, y))
    img.save(os.path.join(MOD, "wing_v6_detail.png"))
    print("wrote wing_v6_detail.png")


def compare(ref_file, wing, out):
    ref = Image.open(os.path.join(REF, ref_file)).convert("RGB")
    ref.thumbnail((480, 480), Image.LANCZOS)
    mine0 = pose_img(wing, 0)
    mine1 = pose_img(wing, 1)
    mine0.thumbnail((480, 480), Image.LANCZOS)
    mine1.thumbnail((480, 480), Image.LANCZOS)
    pad = 10
    H = 500
    img = Image.new("RGB", (3 * 490 + 4 * pad, H + 2 * pad), (44, 48, 58))
    for k, im in enumerate((ref, mine0, mine1)):
        x = pad + k * (490 + pad)
        y = pad + (H - im.height) // 2
        img.paste(im, (x + (490 - im.width) // 2, y))
    img.save(os.path.join(MOD, out))
    print("wrote", out)


if __name__ == "__main__":
    overview()
    detail()
    compare("angel2025w_06.png", "seraph_wings", "_lunar_cmp_seraph.png")
    compare("dragonblack_04.png", "voidwing", "_lunar_cmp_void.png")
    compare("demonred_09.png", "emberwing", "_lunar_cmp_ember.png")
