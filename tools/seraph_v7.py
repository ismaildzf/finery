"""Seraph v7: individual-feather wing prototype.

Loads the three AI-painted feather sprites, keys them to alpha, packs an atlas,
lays out four feather rows along a wing armature, and renders a 2D proof sheet.
Use --push to send the generated quad mesh into the running Blockbench.
"""
from PIL import Image, ImageDraw
import numpy as np
import json
import math
import os
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
ART = ROOT / "art-wings" / "feathers"
OUT = ROOT / "_design"
RES = ROOT / "src" / "main" / "resources" / "assets" / "finery"
sys.path.insert(0, str(ROOT / "tools"))

GLOBAL_DEG = -20.0
ATLAS_W = 1024
ATLAS_H = 1024


def key_black(img):
    rgb = np.asarray(img.convert("RGB")).astype(np.float32) / 255.0
    lum = rgb.max(axis=2)
    alpha = np.clip((lum - 0.012) / 0.085, 0.0, 1.0)
    alpha = alpha ** 0.85
    fill = np.array([0.985, 0.975, 0.955], np.float32)
    out_rgb = rgb * alpha[..., None] + fill * (1.0 - alpha[..., None])
    arr = np.concatenate([np.clip(out_rgb * 255, 0, 255),
                          (alpha * 255)[..., None]], axis=2)
    return Image.fromarray(arr.astype(np.uint8), "RGBA")


def crop_sprite(img, pad=8):
    bbox = img.getchannel("A").point(lambda v: 255 if v > 60 else 0).getbbox()
    if not bbox:
        return img
    x0, y0, x1, y1 = bbox
    return img.crop((max(0, x0 - pad), max(0, y0 - pad),
                     min(img.width, x1 + pad), min(img.height, y1 + pad)))


def build_atlas():
    raw = {n: Image.open(ART / f"{n}_raw.png") for n in ("primary", "secondary", "covert")}
    sprites = {n: crop_sprite(key_black(im)) for n, im in raw.items()}
    atlas = Image.new("RGBA", (ATLAS_W, ATLAS_H), (0, 0, 0, 0))
    cells = {
        "primary": (8, 8, 270, 820),
        "secondary": (286, 8, 540, 660),
        "covert": (560, 8, 830, 420),
    }
    rects = {}
    for name, (x0, y0, x1, y1) in cells.items():
        s = sprites[name]
        scale = min((x1 - x0) / s.width, (y1 - y0) / s.height)
        w, h = max(1, round(s.width * scale)), max(1, round(s.height * scale))
        fitted = s.resize((w, h), Image.LANCZOS)
        px = x0 + (x1 - x0 - w) // 2
        py = y1 - h
        atlas.alpha_composite(fitted, (px, py))
        rects[name] = (px, py, px + w, py + h)
    atlas.save(ART / "seraph_feather_atlas.png")
    atlas.resize((512, 512), Image.LANCZOS).save(ART / "seraph_feather_atlas_view.png")
    return atlas, rects


def bezier(p0, p1, p2, t):
    mt = 1.0 - t
    return (mt * mt * p0[0] + 2 * mt * t * p1[0] + t * t * p2[0],
            mt * mt * p0[1] + 2 * mt * t * p1[1] + t * t * p2[1])


def bezier_tan(p0, p1, p2, t):
    x = 2 * (1 - t) * (p1[0] - p0[0]) + 2 * t * (p2[0] - p1[0])
    y = 2 * (1 - t) * (p1[1] - p0[1]) + 2 * t * (p2[1] - p1[1])
    ln = math.hypot(x, y) or 1.0
    return x / ln, y / ln


ARM = ((1.5, 2.0), (9.0, 3.5), (22.0, -5.0))   # drooping leading edge: shoulder -> wrist -> tip


def arm_point(t):
    return bezier(*ARM, t)


def row(side_t0, side_t1, count, angle0, angle1, len0, len1,
        width0, width1, z0, z1, tilt0, tilt1, sprite):
    """One feather row; angles in degrees from +X (Y up)."""
    out = []
    for i in range(count):
        u = i / max(1, count - 1)
        t = side_t0 + (side_t1 - side_t0) * u
        bx, by = arm_point(t)
        ang = math.radians(angle0 + (angle1 - angle0) * u)
        length = len0 + (len1 - len0) * (u ** 0.85)
        width = width0 + (width1 - width0) * u
        z = z0 + (z1 - z0) * u
        tilt = tilt0 + (tilt1 - tilt0) * u
        out.append(dict(base=(bx, by), angle=ang, length=length, width=width,
                        z=z, tilt=tilt, sprite=sprite, row=side_t0))
    return out


def root_offset(t, depth):
    """Base point slightly inside the leading edge."""
    x, y = arm_point(t)
    tx, ty = bezier_tan(*ARM, t)
    nx, ny = ty, -tx
    ln = math.hypot(nx, ny) or 1.0
    return x + nx / ln * depth, y + ny / ln * depth


def row_bases(t0, t1, count, depth, angle0, angle1, len0, len1,
              width0, width1, z0, z1, tilt0, tilt1, sprite):
    out = []
    for i in range(count):
        u = i / max(1, count - 1)
        t = t0 + (t1 - t0) * u
        bx, by = root_offset(t, depth)
        ang = math.radians(angle0 + (angle1 - angle0) * u)
        # longest around 60-70% out, tapered at the very tip
        bulge = 1.0 - 0.18 * max(0.0, u - 0.72) / 0.28
        length = (len0 + (len1 - len0) * (u ** 0.9)) * bulge
        width = width0 + (width1 - width0) * u
        z = z0 + (z1 - z0) * u
        tilt = tilt0 + (tilt1 - tilt0) * u
        out.append(dict(base=(bx, by), angle=ang, length=length, width=width,
                        z=z, tilt=tilt, sprite=sprite, row=t0))
    return out


def layout():
    feathers = []
    # primaries: long outer flight feathers, wide fan
    feathers += row_bases(0.28, 1.0, 13, 0.55, -94, -20, 14.0, 22.0,
                          3.4, 4.0, 0.0, 0.12, 13.0, 8.0, "primary")
    # secondaries: inner flight feathers hanging close to the body
    feathers += row_bases(0.03, 0.56, 11, 0.55, -128, -98, 9.0, 15.5,
                          3.1, 3.7, 0.12, 0.26, 11.0, 7.0, "secondary")
    # greater coverts: short scalloped row over the bases
    feathers += row_bases(0.02, 0.92, 16, 0.35, -112, -42, 3.8, 6.8,
                          2.4, 2.9, 0.90, 1.10, 6.0, 4.0, "secondary")
    # marginal coverts near the shoulder / leading edge
    feathers += row_bases(0.0, 0.34, 8, 0.25, -138, -112, 2.4, 4.0,
                          2.2, 2.6, 1.40, 1.50, 3.0, 1.0, "covert")
    return feathers


def load_sprite(name):
    atlas = Image.open(ART / "seraph_feather_atlas.png").convert("RGBA")
    rects = json.loads((ART / "seraph_atlas_rects.json").read_text())
    r = rects[name]
    return atlas.crop(r)


def render_2d(feathers, path):
    W, H = 1800, 1250
    S = 23  # screen px per model unit
    SCALE = 0.72
    SHOULDER = 24.0
    cx, cy = W * 0.5, H - 90
    img = Image.new("RGBA", (W, H), (28, 29, 36, 255))
    # player silhouette
    d = ImageDraw.Draw(img)
    d.rectangle([cx - 4 * S / 4, cy - 24 * S, cx + 4 * S / 4, cy], fill=(58, 68, 96, 255))
    d.rectangle([cx - 4 * S / 4, cy - 32 * S, cx + 4 * S / 4, cy - 24 * S], fill=(198, 158, 122, 255))

    sprites = {n: load_sprite(n) for n in ("primary", "secondary", "covert")}
    for side in (1, -1):
        g = math.radians(GLOBAL_DEG)
        cg, sg = math.cos(g), math.sin(g)
        for f in feathers:
            sp = sprites[f["sprite"]]
            L = max(2, int(round(f["length"] * SCALE * S)))
            w = max(1, int(round(sp.width * L / sp.height)))
            sp = sp.resize((w, L), Image.LANCZOS)
            if side < 0:
                sp = sp.transpose(Image.FLIP_LEFT_RIGHT)
            ang = f["angle"] + g
            angle_img = math.degrees(ang) - 90.0
            rot = sp.rotate(angle_img, resample=Image.BICUBIC, expand=True)
            bxs = f["base"][0] * cg - f["base"][1] * sg
            bys = f["base"][0] * sg + f["base"][1] * cg
            bx = cx + side * bxs * SCALE * S
            by = cy - (SHOULDER + bys * SCALE) * S
            dx = side * math.cos(ang) * f["length"] * SCALE * S * 0.5
            dy = -math.sin(ang) * f["length"] * SCALE * S * 0.5
            px = bx + dx - rot.width / 2
            py = by + dy - rot.height / 2
            img.alpha_composite(rot, (int(px), int(py)))
    d = ImageDraw.Draw(img)
    d.text((16, 12), "Seraph v7 - individual feathers, shoulder-rooted (2D proof)", fill=(240, 230, 200, 255))
    img.save(path)


def write_rects(rects):
    (ART / "seraph_atlas_rects.json").write_text(json.dumps(rects, indent=1))


def main():
    OUT.mkdir(exist_ok=True)
    atlas, rects = build_atlas()
    write_rects(rects)
    feathers = layout()
    render_2d(feathers, OUT / "seraph_v7_layout.png")
    print("atlas", atlas.size, "feathers", len(feathers))
    print("rects", rects)


if __name__ == "__main__":
    main()
