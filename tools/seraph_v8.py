"""Seraph v8: individual-feather wing on an arched armature.

Model space (right wing, wing-local): X outboard, Y up, Z backward (toward the
camera in a back view). 1 unit = 1 texel = 1/16 block.

Rows follow real wing anatomy:
  secondaries  long inner feathers hanging under the arm
  primaries    long outer flight feathers fanning off wrist/hand
  coverts      short scalloped row covering the bases
  marginals    tiny feathers riding the leading edge
Each feather is a folded pair of quads (rachis ridge) with its own atlas sprite,
its own depth and a small twist, so the stack reads as volume from any angle.
"""
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
ART = ROOT / "art-wings" / "feathers"
OUT = ROOT / "_design"
sys.path.insert(0, str(ROOT / "tools"))
import render_mesh as rm  # noqa: E402

ATLAS_W = 1024
ATLAS_H = 1024
SWEEP_DEG = 15.0
SOLID = (900, 900, 932, 932)

# shoulder -> elbow -> wrist -> hand tip (wing-local, root at shoulder blade)
ARM = [(0.0, 0.0), (4.0, 2.8), (8.5, 5.8), (13.0, 7.4), (17.0, 7.8)]
ROOT_X = 1.5


# ── atlas ────────────────────────────────────────────────────────────────────
def key_black(img):
    rgb = np.asarray(img.convert("RGB")).astype(np.float32) / 255.0
    lum = rgb.max(axis=2)
    alpha = np.clip((lum - 0.035) / 0.13, 0.0, 1.0) ** 0.8
    fill = np.array([0.985, 0.975, 0.955], np.float32)
    out_rgb = rgb * alpha[..., None] + fill * (1.0 - alpha[..., None])
    arr = np.concatenate([np.clip(out_rgb * 255, 0, 255),
                          (alpha * 255)[..., None]], axis=2)
    return Image.fromarray(arr.astype(np.uint8), "RGBA")


def clean_sprite(img, max_dim=520):
    """Fill interior transparency, lift the dark barbs, soften to game scale."""
    img = key_black(img.convert("RGB"))
    a = np.asarray(img.getchannel("A"))
    # close the pinholes left by dark barbs so no background speckles survive
    sil = Image.fromarray(np.where(a > 60, 255, 0).astype(np.uint8), "L")
    sil = sil.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5))
    # opening removes stray 1-2px barb hairs that read as whiskers in 3D
    sil = sil.filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MaxFilter(5))
    solid = np.asarray(sil) > 127

    rgb = np.asarray(img.convert("RGB")).astype(np.float32)
    alpha = a.astype(np.float32) / 255.0
    fill = np.array([249.0, 245.0, 236.0], np.float32)
    w = np.clip(1.0 - alpha, 0.0, 1.0)[..., None]
    rgb = rgb * (1.0 - w) + fill * w
    rgb = 255.0 - (255.0 - rgb) * 0.55
    out = np.zeros((*solid.shape, 4), np.uint8)
    out[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    out[..., 3] = np.where(solid, 255, 0)
    pil = Image.fromarray(out, "RGBA").filter(ImageFilter.GaussianBlur(0.9))
    bbox = pil.getchannel("A").point(lambda v: 255 if v > 60 else 0).getbbox()
    if bbox:
        pil = pil.crop(bbox)
    # drop the bare quill and its downy hairs: the vane must start at the root
    mask = np.asarray(pil.getchannel("A")) > 60
    widths = mask.sum(axis=1)
    ref = np.percentile(widths, 95) if widths.size else 0
    cut = pil.height
    for y in range(pil.height - 1, int(pil.height * 0.6), -1):
        if widths[y] >= 0.7 * ref:
            cut = y + 2
            break
    pil = pil.crop((0, 0, pil.width, cut))
    if max(pil.size) > max_dim:
        s = max_dim / max(pil.size)
        pil = pil.resize((max(1, round(pil.width * s)), max(1, round(pil.height * s))),
                         Image.LANCZOS)
    return pil


def crop_sprite(img, pad=6):
    bbox = img.getchannel("A").point(lambda v: 255 if v > 60 else 0).getbbox()
    if not bbox:
        return img
    x0, y0, x1, y1 = bbox
    return img.crop((max(0, x0 - pad), max(0, y0 - pad),
                     min(img.width, x1 + pad), min(img.height, y1 + pad)))


def build_atlas():
    raw = {n: Image.open(ART / f"{n}_raw.png") for n in ("primary", "secondary", "covert")}
    sprites = {n: crop_sprite(clean_sprite(im)) for n, im in raw.items()}
    atlas = Image.new("RGBA", (ATLAS_W, ATLAS_H), (0, 0, 0, 0))
    cells = {
        "primary": (8, 8, 300, 1000),
        "secondary": (316, 8, 600, 800),
        "covert": (616, 8, 900, 520),
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
    ImageDraw.Draw(atlas).rectangle([SOLID[0], SOLID[1], SOLID[2] - 1, SOLID[3] - 1],
                                    fill=(96, 104, 120, 255))
    atlas.save(ART / "seraph_feather_atlas.png")
    atlas.resize((512, 512), Image.LANCZOS).save(ART / "seraph_feather_atlas_view.png")
    (ART / "seraph_atlas_rects.json").write_text(json.dumps(rects, indent=1))
    return atlas, rects


def sprite_aspect(rects, name):
    x0, y0, x1, y1 = rects[name]
    return (x1 - x0) / (y1 - y0)


# ── armature ─────────────────────────────────────────────────────────────────
_SEG = [math.dist(ARM[i], ARM[i + 1]) for i in range(len(ARM) - 1)]
_LEN = sum(_SEG)


def arm_point(t):
    d = min(max(t, 0.0), 1.0) * _LEN
    for i, seg in enumerate(_SEG):
        if d <= seg or i == len(_SEG) - 1:
            f = d / seg
            a, b = ARM[i], ARM[i + 1]
            return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
        d -= seg
    return ARM[-1]


def arm_angle(t):
    e = 0.01
    a, b = arm_point(max(0.0, t - e)), arm_point(min(1.0, t + e))
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))


def arm_normal(t):
    """Unit normal pointing to the trailing (lower) side."""
    a = math.radians(arm_angle(t))
    return (math.sin(a), -math.cos(a))


TINTS = {
    "secondary": (0.86, 0.87, 0.93),
    "primary": (0.93, 0.93, 0.97),
    "covert": (1.00, 0.99, 0.98),
    "marginal": (1.04, 1.03, 1.00),
    "tuft": (0.95, 0.95, 0.98),
    "tip": (1.00, 0.99, 1.01),
}


def tint_for(tag, i):
    j = 1.0 + 0.05 * (((i * 37) % 17) / 16.0 - 0.5)
    base = TINTS[tag]
    return tuple(min(1.25, c * j) for c in base)


# ── layout ───────────────────────────────────────────────────────────────────
def lerp(a, b, u):
    return a + (b - a) * u


def layout(rects):
    fe = []

    def add(t, depth, angle, length, width, z, cup, twist, sprite, name):
        px, py = arm_point(t)
        nx, ny = arm_normal(t)
        fe.append(dict(base=(px + nx * depth, py + ny * depth), angle=angle,
                       length=length, width=width, z=z, cup=cup, twist=twist,
                       sprite=sprite, tag=name, tint=tint_for(name, len(fe))))
    pa, sa = sprite_aspect(rects, "primary"), sprite_aspect(rects, "secondary")
    ca = sprite_aspect(rects, "covert")

    # secondaries: hang from the inner arm, steep at the body, flatter outward
    N = 15
    for i in range(N):
        u = i / (N - 1)
        t = lerp(0.0, 0.44, u)
        add(t, 0.75, lerp(-103, -66, u ** 0.9), lerp(9.0, 14.0, u ** 0.85),
            0.0, lerp(0.00, 0.20, u), 0.28, 0.10, "secondary", "secondary")

    # primaries: outer flight fan off wrist and hand
    N = 20
    for i in range(N):
        u = i / (N - 1)
        t = lerp(0.30, 1.0, u)
        ln = lerp(9.5, 16.5, u ** 0.72) * (1.0 - 0.06 * max(0.0, u - 0.86) / 0.14)
        add(t, 0.55, lerp(-56, 18, u ** 1.1), ln,
            ln * pa * 0.88, lerp(0.55, 0.92, u), 0.32, 0.14, "primary", "primary")

    # one curled tip flight feather rising off the hand
    add(1.0, 0.45, 14.0, 15.5, 15.5 * pa * 0.90, 0.94, 0.24, 0.08, "primary", "tip")

    # greater coverts: short scalloped row across the bases, grows outward
    N = 20
    for i in range(N):
        u = i / (N - 1)
        t = lerp(0.02, 0.68, u)
        ln = lerp(3.6, 5.0, u ** 1.1)
        add(t, 0.52, lerp(-92, -8, u ** 1.1), ln,
            ln * sa * 0.86, lerp(1.24, 1.50, u), 0.24, 0.12, "secondary", "covert")

    # marginals: tiny feathers riding the leading edge, form the smooth top arc
    N = 16
    for i in range(N):
        u = i / (N - 1)
        t = lerp(0.0, 0.62, u)
        ln = lerp(2.4, 3.6, u)
        add(t, 0.05, arm_angle(t) - 3.0 + 3.0 * u, ln,
            ln * ca * 0.92, lerp(1.72, 1.86, u), 0.16, 0.08, "covert", "marginal")

    # shoulder tuft hides the attachment point
    for i, (ang, ln) in enumerate(((58.0, 3.8), (36.0, 4.6), (14.0, 5.2),
                                   (-8.0, 5.0))):
        fe.append(dict(base=(0.1 + i * 0.4, 1.15 - i * 0.35), angle=ang, length=ln,
                       width=ln * ca * 0.95, z=1.10 + i * 0.04, cup=0.18, twist=0.06,
                       sprite="covert", tag="tuft", tint=tint_for("tuft", len(fe))))
    return fe


# ── mesh ─────────────────────────────────────────────────────────────────────
def quad(verts, uv, tint, quads):
    quads.append((verts, uv, tint))


def feather_quads(f, rects, side):
    a = math.radians(f["angle"])
    dx, dy = math.cos(a), math.sin(a)
    px, py = -dy, dx
    hw = f["width"] * 0.5
    bx, by = f["base"]
    z = f["z"]
    sweep = math.tan(math.radians(SWEEP_DEG))
    cup, tw = f["cup"], f["twist"]

    def P(along, across, dz):
        x = bx + dx * along + px * across
        y = by + dy * along + py * across
        return side * (x + ROOT_X), y, z + dz + x * sweep

    u0, v0, u1, v1 = rects[f["sprite"]]
    um = (u0 + u1) * 0.5
    tint = f["tint"]
    out = []
    # left half: outer edge -> spine ridge
    quad([P(0, hw, -tw), P(f["length"], hw, -tw + 0.04 * f["length"]),
          P(f["length"], 0, cup), P(0, 0, cup)],
         [(u0, v1), (u0, v0), (um, v0), (um, v1)], tint, out)
    # right half: spine ridge -> other edge
    quad([P(0, 0, cup), P(f["length"], 0, cup),
          P(f["length"], -hw, tw + 0.04 * f["length"]), P(0, -hw, tw)],
         [(um, v1), (um, v0), (u1, v0), (u1, v1)], tint, out)
    return out


def build_model(feathers, rects):
    quads = []
    for side in (1, -1):
        for f in feathers:
            quads += feather_quads(f, rects, side)
    return quads


# ── preview ──────────────────────────────────────────────────────────────────
def to_arrays(quads, tex_w, tex_h):
    verts, uvs, faces, cols = [], [], [], []
    for verts4, uv4, tint in quads:
        base = len(verts)
        for k, ((x, y, z), (u, v)) in enumerate(zip(verts4, uv4)):
            verts.append([x, y, z])
            uvs.append([u / tex_w, v / tex_h])
            f = 0.95 if k in (0, 3) else 1.03
            cols.append([min(1.25, c * f) for c in tint])
        faces.append((base, base + 1, base + 2))
        faces.append((base, base + 2, base + 3))
    return (np.array(verts, float), np.array(faces, np.int64),
            np.array(uvs, float), np.array(cols, float))


def proxy_boxes(shoulder_y=24.0, root_z=2.6):
    skin_uv = ((SOLID[0] + 8) / ATLAS_W, (SOLID[1] + 8) / ATLAS_H)
    boxes = [((-4, 24, -4), (4, 32, 4)), ((-4, 12, -2), (4, 24, 2)),
             ((-4, 0, -2), (0, 12, 2)), ((0, 0, -2), (4, 12, 2)),
             ((-8, 12, -2), (-4, 24, 2)), ((4, 12, -2), (8, 24, 2))]
    pv, pf, pu = [], [], []
    for frm, to in boxes:
        corners = [(frm[0], frm[1], frm[2]), (to[0], frm[1], frm[2]),
                   (to[0], to[1], frm[2]), (frm[0], to[1], frm[2]),
                   (frm[0], frm[1], to[2]), (to[0], frm[1], to[2]),
                   (to[0], to[1], to[2]), (frm[0], to[1], to[2])]
        quads = [(0, 1, 2, 3), (5, 4, 7, 6), (4, 5, 1, 0),
                 (2, 3, 7, 6), (4, 0, 3, 7), (1, 5, 6, 2)]
        for q in quads:
            base = len(pv)
            for idx in q:
                x, y, z = corners[idx]
                pv.append([x, y, z + root_z - 2.0])
                pu.append(skin_uv)
            pf += [(base, base + 1, base + 2), (base, base + 2, base + 3)]
    return np.array(pv, float), pf, np.array(pu, float)


def render_sheet(quads, atlas, path):
    tex = np.asarray(atlas.convert("RGBA"), float)
    v, f, u, c = to_arrays(quads, ATLAS_W, ATLAS_H)
    # place wing root at the shoulder: local (0,0) -> (±1.6, 24.4, 2.6)
    v = v + np.array([0.0, 22.2, 2.6])
    pv, pf, pu = proxy_boxes()
    allv = np.vstack([pv, v])
    allf = np.array(pf + [(a + len(pv), b + len(pv), c + len(pv)) for a, b, c in f],
                    np.int64)
    allu = np.vstack([pu, u])
    allc = np.vstack([np.ones((len(pv), 3)), c])

    size = 760
    views = [("back", np.eye(3), 0.9),
             ("3/4 back", rm.rot_y(-30) @ rm.rot_x(-8), 0.9),
             ("side", rm.rot_y(-76), 0.9),
             ("top", rm.rot_x(-78), 0.9)]
    sheet = Image.new("RGB", (size * 2, (size + 26) * 2), (17, 18, 22))
    d = ImageDraw.Draw(sheet)
    for i, (label, R, zoom) in enumerate(views):
        img = rm.render_view(allv, allf, allu, tex, R, size, shade_lo=0.55,
                             shade_hi=0.5, colors=allc)
        x, y = (i % 2) * size, (i // 2) * (size + 26)
        sheet.paste(Image.fromarray(img), (x, y + 26))
        d.text((x + 10, y + 7), f"Seraph v8 - {label}", fill=(240, 233, 208))
    sheet.save(path)
    return sheet


def main():
    OUT.mkdir(exist_ok=True)
    atlas, rects = build_atlas()
    feathers = layout(rects)
    quads = build_model(feathers, rects)
    print("feathers", len(feathers), "quads", len(quads), "rects", rects)
    render_sheet(quads, atlas, OUT / "seraph_v8_preview.png")
    print("saved", OUT / "seraph_v8_preview.png")


if __name__ == "__main__":
    main()
