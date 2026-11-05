"""Angel wings v3 - AI artwork mapped to the Lunar reference silhouette.

Source art: ImageGen white pixel-art angel wings on magenta (own asset).
Reference: Lunar Client white angel wings (reference only, no asset copying).
Build: long pointed primaries (art H) on a curved double-sided plane, plus a
raised fluffy covert layer (art G) cut along a scalloped feather line. Box and
pose measured from the reference; all textures are original AI-generated art.
Coordinates: player units, feet y=0, head top y=32, +z toward the back camera.
"""
import math
import pathlib
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parents[1]
ART = ROOT / "art-wings" / "angel"
OUT = ROOT / "_design"
AI_SRC = pathlib.Path(r"C:\Users\Administrator\Downloads\first mod\vibe_images"
                      r"\angel_wings_pixel_h_1792577880802_c14b0e0b.png")
OVERLAY_SRC = pathlib.Path(r"C:\Users\Administrator\Downloads\first mod\vibe_images"
                           r"\angel_wings_pixel_g_1792577290650_f4d670d0.png")
sys.path.insert(0, str(ROOT / "tools"))
import render_mesh as rm  # noqa: E402
from dragonwing_v1 import to_arrays  # noqa: E402

AW = AH = 1024
WING_RECT = (8, 8, 8 + 500, 8 + 628)
SOLID = (960, 660, 984, 684)
OVERLAY_RECT = (516, 8, 516 + 500, 8 + 628)

# reference measured box (player units, left wing)
X_OUT, X_IN = -24.9, -1.55
Y_TOP, Y_BOT = 38.6, 7.4
Z_ROOT = 2.62
Z_OUT = 3.12

TEX_WHITE = (1.0, 1.0, 1.0)
TEX_BACK = (0.80, 0.84, 0.94)


# ------------------------------------------------------------------ texture
def load_wing_art(src_path, outline=None):
    ai = np.array(Image.open(src_path).convert("RGB")).astype(float)
    r, g, b = ai[:, :, 0], ai[:, :, 1], ai[:, :, 2]
    pink = (r - g > 18) & (b - g > 18)
    alpha = (~pink).astype(float)
    alpha[:, 512:] = 0
    ys, xs = np.where(alpha > 0)
    crop = ai[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    pcrop = pink[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    crop[pcrop] = (250, 252, 255)
    a = (alpha[ys.min():ys.max() + 1, xs.min():xs.max() + 1] * 255).astype(np.uint8)
    src = Image.fromarray(np.dstack([crop, a]).astype(np.uint8), "RGBA")
    w, h = WING_RECT[2] - WING_RECT[0], WING_RECT[3] - WING_RECT[1]
    wing = src.resize((w, h), Image.LANCZOS)
    wa = np.array(wing)[:, :, 3]
    wa[wa < 96] = 0
    arr = np.array(wing)
    arr[:, :, 3] = wa
    rgb = arr[:, :, :3].astype(float)
    rgb = np.clip((rgb - 12.0) * 1.10, 0, 255)
    if outline is not None:
        lum = rgb.mean(2)
        edge = (lum < 185) & (wa > 0)
        rgb[edge] = outline
    arr[:, :, :3] = rgb.astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


def scallop_bottom(img, base=0.47, amp=0.04):
    arr = np.array(img)
    h, w = arr.shape[:2]
    v = np.linspace(0.0, 1.0, h)[:, None]
    u = np.linspace(0.0, 1.0, w)[None, :]
    cut = (base + amp * np.cos(2 * np.pi * u * 5.0)
           + 0.02 * np.cos(2 * np.pi * u * 11.0 + 1.3))
    arr[:, :, 3] = (arr[:, :, 3] * (v < cut)).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


def build_wing_texture(src_path=None, outline=None, tag="angel_v3"):
    wing = load_wing_art(src_path or AI_SRC, outline)
    overlay = scallop_bottom(load_wing_art(OVERLAY_SRC))
    ART.mkdir(parents=True, exist_ok=True)
    wing.save(ART / f"{tag}_wing.png")
    overlay.save(ART / f"{tag}_covert.png")
    atlas = Image.new("RGBA", (AW, AH), (0, 0, 0, 0))
    atlas.alpha_composite(wing, (WING_RECT[0], WING_RECT[1]))
    atlas.alpha_composite(overlay, (OVERLAY_RECT[0], OVERLAY_RECT[1]))
    ImageDraw.Draw(atlas).rectangle([SOLID[0], SOLID[1], SOLID[2] - 1, SOLID[3] - 1],
                                    fill=(120, 124, 132, 255))
    atlas.save(ART / f"{tag}_atlas.png")
    return wing, overlay, atlas


def wuv(u, v, rect=None):
    x0, y0, x1, y1 = rect or WING_RECT
    return (x0 + 1 + u * (x1 - x0 - 2), y0 + 1 + v * (y1 - y0 - 2))


def set_box(x_out, x_in, y_top, y_bot):
    global X_OUT, X_IN, Y_TOP, Y_BOT
    X_OUT, X_IN, Y_TOP, Y_BOT = x_out, x_in, y_top, y_bot


# ------------------------------------------------------------------ geometry
def wing_z(u, v):
    return Z_ROOT + (Z_OUT - Z_ROOT) * (1.0 - u) ** 1.35 + 0.10 * math.sin(math.pi * v)


def wing_point(u, v, side):
    x = X_OUT + u * (X_IN - X_OUT)
    y = Y_TOP + v * (Y_BOT - Y_TOP)
    if side > 0:
        x = -x
    return (x, y, wing_z(u, v))


def wing_quads(wing_img, side, vlo=0.0, vhi=1.0, lift=0.0, rect=None, tint=None):
    alpha = np.array(wing_img)[:, :, 3].astype(float)
    nx, ny = 44, 54
    j0, j1 = int(vlo * ny), int(vhi * ny)
    quads = []
    for j in range(j0, j1):
        for i in range(nx):
            u0, u1 = i / nx, (i + 1) / nx
            va, vb = j / ny, (j + 1) / ny
            x0 = int(u0 * (alpha.shape[1] - 1))
            x1 = int(u1 * (alpha.shape[1] - 1))
            y0 = int(va * (alpha.shape[0] - 1))
            y1 = int(vb * (alpha.shape[0] - 1))
            cell = alpha[y0:y1 + 1, x0:x1 + 1]
            if cell.size == 0 or cell.max() < 128:
                continue
            p00 = wing_point(u0, va, side)
            p10 = wing_point(u1, va, side)
            p11 = wing_point(u1, vb, side)
            p01 = wing_point(u0, vb, side)
            front = [(p[0], p[1], p[2] + lift) for p in (p00, p10, p11, p01)]
            uvs = [wuv(u0, va, rect), wuv(u1, va, rect),
                   wuv(u1, vb, rect), wuv(u0, vb, rect)]
            back = [(p[0], p[1], p[2] - 0.09) for p in front]
            quads.append((front, uvs, tint or TEX_WHITE))
            quads.append((back, uvs, TEX_BACK))
    return quads


def all_quads(wing_img, overlay_img=None):
    quads = []
    for side in (-1, 1):
        quads += wing_quads(wing_img, side)
        if overlay_img is not None:
            quads += wing_quads(overlay_img, side, vhi=0.57, lift=0.30,
                                rect=OVERLAY_RECT)
    return quads


# ------------------------------------------------------------------ body proxy
def body_proxy():
    boxes = [((-4, 24, -4), (4, 32, 4), (0.34, 0.24, 0.16)),
             ((-4, 12, -2), (4, 24, 2), (0.16, 0.62, 0.66)),
             ((-4, 0, -2), (0, 12, 2), (0.20, 0.22, 0.72)),
             ((0, 0, -2), (4, 12, 2), (0.20, 0.22, 0.72)),
             ((-8, 12, -2), (-4, 24, 2), (0.74, 0.54, 0.40)),
             ((4, 12, -2), (8, 24, 2), (0.74, 0.54, 0.40))]
    skin_uv = ((SOLID[0] + 8) / AW, (SOLID[1] + 8) / AH)
    pv, pf, pu, pc = [], [], [], []
    for frm, to, col in boxes:
        corners = [(frm[0], frm[1], frm[2]), (to[0], frm[1], frm[2]),
                   (to[0], to[1], frm[2]), (frm[0], to[1], frm[2]),
                   (frm[0], frm[1], to[2]), (to[0], frm[1], to[2]),
                   (to[0], to[1], to[2]), (frm[0], to[1], to[2])]
        for q in ((0, 1, 2, 3), (5, 4, 7, 6), (4, 5, 1, 0),
                  (2, 3, 7, 6), (4, 0, 3, 7), (1, 5, 6, 2)):
            base = len(pv)
            for idx in q:
                pv.append(list(corners[idx]))
                pu.append(skin_uv)
                pc.append(col)
            pf += [(base, base + 1, base + 2), (base, base + 2, base + 3)]
    return np.array(pv, float), pf, np.array(pu, float), np.array(pc, float)


# ------------------------------------------------------------------ render
BG_TOP = np.array([196, 200, 232])
BG_BOT = np.array([108, 112, 158])


def render_sheet(atlas, quads, path):
    tex = np.asarray(atlas.convert("RGBA"), float)
    v, f, u, c = to_arrays(quads)
    pv, pf, pu, pc = body_proxy()
    allv = np.vstack([pv, v])
    allf = np.array(pf + [(a + len(pv), b + len(pv), c2 + len(pv)) for a, b, c2 in f],
                    np.int64)
    allu = np.vstack([pu, u])
    allc = np.vstack([pc, c])
    size = 760
    views = [("back", np.eye(3)),
             ("3/4 back", rm.rot_y(-28) @ rm.rot_x(-6)),
             ("side", rm.rot_y(-76)),
             ("back low", rm.rot_x(10))]
    sheet = Image.new("RGB", (size * 2, (size + 26) * 2), (28, 30, 38))
    d = ImageDraw.Draw(sheet)
    bg = np.zeros((size, size, 3), np.float64)
    yy = np.linspace(0, 1, size)[:, None, None]
    bg[:] = BG_TOP * (1 - yy) + BG_BOT * yy
    for i, (label, R) in enumerate(views):
        rgba = rm.render_view(allv, allf, allu, tex, R, size, alpha=True,
                              shade_lo=0.95, shade_hi=0.06, colors=allc)
        base = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
        base.alpha_composite(Image.fromarray(rgba, "RGBA"))
        x, y = (i % 2) * size, (i // 2) * (size + 26)
        sheet.paste(base.convert("RGB"), (x, y + 26))
        d.text((x + 10, y + 7), f"Angel wing v3 - {label}", fill=(230, 226, 214))
    sheet.save(path)
    return sheet


def fixed_render(atlas, quads, out=1000, S=2600, unit_px=19.0, cy0=17.63, body=True):
    """Back view framed exactly like the reference screenshot."""
    tex = np.asarray(atlas.convert("RGBA"), float)
    v, f, u, c = to_arrays(quads)
    pv, pf, pu, pc = body_proxy()
    if body:
        allv = np.vstack([pv, v])
        allf = np.array(pf + [(a + len(pv), b + len(pv), c2 + len(pv)) for a, b, c2 in f],
                        np.int64)
        allu = np.vstack([pu, u])
        allc = np.vstack([pc, c])
    else:
        allv, allf, allu, allc = v, f, u, c
    rgba = rm.render_view(allv, allf, allu, tex, np.eye(3), S, alpha=True,
                          shade_lo=0.95, shade_hi=0.06, colors=allc)
    lo, hi = np.vstack([pv, v]).min(0), np.vstack([pv, v]).max(0)
    span = max(hi[0] - lo[0], hi[1] - lo[1])
    k = S * 0.88 / span
    cx, cy = (lo[0] + hi[0]) * 0.5, (lo[1] + hi[1]) * 0.5
    rx = (0 - cx) * k + S * 0.5
    ry = S * 0.5 - (cy0 - cy) * k
    half = (out / unit_px) * k * 0.5
    x0, x1 = int(round(rx - half)), int(round(rx + half))
    y0, y1 = int(round(ry - half)), int(round(ry + half))
    pl, pt = max(0, -x0), max(0, -y0)
    pr, pb = max(0, x1 - S), max(0, y1 - S)
    canvas = np.zeros((S + pt + pb, S + pl + pr, 4), np.float64)
    canvas[pt:pt + S, pl:pl + S] = rgba
    crop = canvas[y0 + pt:y1 + pt, x0 + pl:x1 + pl]
    im = Image.fromarray(crop.astype(np.uint8), "RGBA").resize((out, out), Image.LANCZOS)
    bg = np.zeros((out, out, 3), np.float64)
    yy = np.linspace(0, 1, out)[:, None, None]
    bg[:] = BG_TOP * (1 - yy) + BG_BOT * yy
    base = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    base.alpha_composite(im)
    return base.convert("RGB")


def render_compare(atlas, quads):
    ref = Image.open(OUT / "angel_ref_big.png").convert("RGB")
    new = fixed_render(atlas, quads, out=1000)
    h = 800
    pad = 14
    ref_img = ref.resize((h, h), Image.LANCZOS)
    new_img = new.resize((h, h), Image.LANCZOS)
    sheet = Image.new("RGB", (ref_img.width + new_img.width + pad * 3, h + 70),
                      (24, 26, 33))
    sheet.paste(ref_img, (pad, 52))
    sheet.paste(new_img, (pad * 2 + ref_img.width, 52))
    d = ImageDraw.Draw(sheet)
    d.text((pad + 2, 22), "LUNAR REFERENCE - white angel wings", fill=(220, 214, 200))
    d.text((pad * 2 + ref_img.width + 2, 22), "NEW - angel v3 (own AI art, same pose)",
           fill=(220, 214, 200))
    sheet.save(OUT / "angel_v3_compare.png")
    return sheet


def main():
    wing, overlay, atlas = build_wing_texture(outline=(202, 219, 240))
    quads = all_quads(wing, overlay)
    print("quads", len(quads))
    back = fixed_render(atlas, quads)
    back.save(OUT / "angel_v3_back.png")
    fixed_render(atlas, quads, body=False).save(OUT / "angel_v3_clean.png")
    render_sheet(atlas, quads, OUT / "angel_v3_preview.png")
    render_compare(atlas, quads)
    print("saved")


if __name__ == "__main__":
    main()
