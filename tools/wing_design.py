"""Blockbench-style wing designer (alpha planes + arm), high-res atlas art.

Model space: 1 unit = 1 pixel = 1/16 block, Y down, +X outboard, +Z backward.
Art is drawn at SCALE texels per unit so the feather linework stays crisp.

  _design/wing.json          model consumed by the Java renderer
  _design/wing_atlas.png     pixel-art atlas (alpha cutout, 3 shading layers)
  _design/wing_preview.png   offline renders (wing alone + on a player proxy)
"""
import json
import math
import pathlib
import sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import render_mesh as rm  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "_design"

SCALE = 4                  # texels per model unit
W, H = 30, 20              # wing cell (model units)
RW, RH = W * SCALE, H * SCALE
N_FEATHERS = 9

ATLAS_W, ATLAS_H = 512, 128
GAP = 6
CELL_POS = {"light": (0, 0), "mid": (RW + GAP, 0), "dark": (2 * (RW + GAP), 0)}

ARM_X = 3 * (RW + GAP)
ARM_UV = (ARM_X, 0, 20, 10)               # u, v, w, h (texels)
EDGE_UV = (ARM_X + 24, 0, 6, 6)
SKIN_UV = (ARM_X + 24, 10, 6, 6)

OUTLINE = (44, 32, 20)
SHADE = (128, 96, 58)
BASE = (196, 164, 116)
MID = (226, 202, 158)
LIGHT = (246, 234, 208)
WHITE = (255, 252, 244)

TINTS = {"dark": 0.80, "mid": 0.90, "light": 1.0}

PALETTES = {
    "seraph_wings": {"outline": (44, 32, 20), "shade": (128, 96, 58),
                     "base": (196, 164, 116), "mid": (226, 202, 158),
                     "light": (246, 234, 208), "white": (255, 252, 244)},
    "emberwing": {"outline": (42, 14, 8), "shade": (112, 34, 14),
                  "base": (170, 54, 20), "mid": (222, 96, 30),
                  "light": (255, 168, 70), "white": (255, 226, 150)},
    "voidwing": {"outline": (18, 12, 34), "shade": (52, 36, 88),
                 "base": (80, 58, 132), "mid": (122, 94, 184),
                 "light": (176, 154, 232), "white": (222, 214, 255)},
    "fae_wings": {"outline": (12, 34, 22), "shade": (26, 78, 46),
                  "base": (44, 112, 64), "mid": (86, 168, 104),
                  "light": (148, 214, 148), "white": (220, 255, 222)},
}


def shade(col, k):
    return tuple(max(0, min(255, int(c * k))) for c in col)


def _feather_poly(root, angle, length, width):
    dx, dy = math.cos(angle), math.sin(angle)
    px, py = -dy, dx
    x0, y0 = root

    def p(t, off):
        return (x0 + dx * length * t + px * off, y0 + dy * length * t + py * off)

    return [
        p(0.0, -width * 0.50),
        p(0.45, -width * 0.60),
        p(0.78, -width * 0.36),
        p(1.00, 0.0),
        p(0.78, width * 0.30),
        p(0.45, width * 0.56),
        p(0.0, width * 0.46),
    ]


def _arm_curve(t):
    x = 1.0 + 21.0 * t
    y = 4.2 - 1.2 * t - math.sin(t * 2.2) * 0.7
    return x, y


def _fan():
    """(root, angle, length, width, t) per primary, outer feathers first."""
    out = []
    for i in range(N_FEATHERS, -1, -1):
        t = i / N_FEATHERS
        ax, ay = _arm_curve(t)
        root = (ax, ay + 1.2)
        angle = math.radians(96 - t * 40)        # 96 deg inboard .. 56 deg at the tip
        length = 8.0 + t * 6.0
        width = 5.0 - t * 1.2
        out.append((root, angle, length, width, t))
    return out


def _covert_fan():
    """Shorter, lighter feather row layered over the primary roots."""
    out = []
    for i in range(4, -1, -1):
        t = i / 4
        ax, ay = _arm_curve(0.05 + t * 0.9)
        root = (ax, ay + 1.4)
        angle = math.radians(92 - t * 40)
        length = 4.2 + t * 3.4
        width = 3.6 - t * 0.8
        out.append((root, angle, length, width, t))
    return out


def wing_art(k, s=SCALE, pal=None):
    """Right wing: solid silhouette with feather linework inside (no gaps)."""
    pal = pal or PALETTES["seraph_wings"]
    OUTLINE = pal["outline"]
    SHADE = pal["shade"]
    BASE = pal["base"]
    MID = pal["mid"]
    LIGHT = pal["light"]
    WHITE = pal["white"]
    fan = _fan()
    size = (RW, RH)

    def S(pts):
        return [(x * s, y * s) for x, y in pts]

    # 1) silhouette = union of fattened feathers + arm band
    mask = Image.new("L", size, 0)
    md = ImageDraw.Draw(mask)
    for root, angle, length, width, t in fan:
        md.polygon(S(_feather_poly(root, angle, length * 1.04, width * 1.55)), fill=255)
    top = [_arm_curve(i / 16) for i in range(17)]
    band = [(x, y - 1.7) for x, y in top] + [(x, y + 2.0) for x, y in reversed(top)]
    md.polygon(S(band), fill=255)
    sx0, sy0 = _arm_curve(0.0)
    md.ellipse(S([(sx0 - 1.8, sy0 - 2.4), (sx0 + 3.4, sy0 + 3.0)]), fill=255)

    img = Image.new("RGBA", size, (0, 0, 0, 0))
    img.paste(Image.new("RGBA", size, shade(BASE, k) + (255,)), (0, 0), mask)
    d = ImageDraw.Draw(img)

    lw = max(2, s // 2 + 1)
    for root, angle, length, width, t in fan:
        dx, dy = math.cos(angle), math.sin(angle)
        px, py = -dy, dx
        x0, y0 = root
        d.polygon(S(_feather_poly(root, angle, length * 0.97, width)), fill=shade(OUTLINE, k))
        inner_root = (x0 + dx * length * 0.06, y0 + dy * length * 0.06)
        d.polygon(S(_feather_poly(inner_root, angle, length * 0.84, width * 0.70)),
                  fill=shade(MID, k))
        # lit edge (upper side) and midrib
        d.line(S([(x0 + px * width * 0.22, y0 + py * width * 0.22),
                  (x0 + dx * length * 0.72 + px * width * 0.10,
                   y0 + dy * length * 0.72 + py * width * 0.10)]),
               fill=shade(LIGHT, k), width=lw)
        d.line(S([(x0 + dx * 0.10 * length, y0 + dy * 0.10 * length),
                  (x0 + dx * length * 0.80, y0 + dy * length * 0.80)]),
               fill=shade(SHADE, k), width=max(1, lw // 2))

    # 2) covert row layered on top of the primaries
    for root, angle, length, width, t in _covert_fan():
        dx, dy = math.cos(angle), math.sin(angle)
        x0, y0 = root
        d.polygon(S(_feather_poly(root, angle, length, width)), fill=shade(OUTLINE, k))
        inner_root = (x0 + dx * length * 0.08, y0 + dy * length * 0.08)
        d.polygon(S(_feather_poly(inner_root, angle, length * 0.80, width * 0.66)),
                  fill=shade(BASE, k))
        d.line(S([(x0 + dx * 0.12 * length, y0 + dy * 0.12 * length),
                  (x0 + dx * length * 0.78, y0 + dy * length * 0.78)]),
               fill=shade(LIGHT, k), width=max(1, lw // 2))

    # 3) arm band on top of the feather roots
    d.polygon(S(band), fill=shade(SHADE, k * 0.95), outline=shade(OUTLINE, k))
    d.line(S([(x + 0.3, y - 0.9) for x, y in top]), fill=shade(WHITE, k), width=lw)

    # 4) shoulder pad
    sx, sy = _arm_curve(0.0)
    d.ellipse(S([(sx - 1.6, sy - 2.6), (sx + 3.8, sy + 2.6)]),
              fill=shade(MID, k), outline=shade(OUTLINE, k))
    d.ellipse(S([(sx - 0.8, sy - 1.8), (sx + 2.8, sy + 1.6)]),
              fill=shade(BASE, k))
    d.line(S([(sx - 0.4, sy - 1.2), (sx + 2.0, sy - 1.5)]), fill=shade(WHITE, k), width=max(1, lw // 2))

    img.putalpha(ImageChops.multiply(img.getchannel("A"), mask))
    return img


def box_uv_rects(frm, to, uv):
    dx, dy, dz = [b - a for a, b in zip(frm, to)]
    u, v = uv
    return {
        "north": (u + dz, v + dz, u + dz + dx, v + dz + dy),
        "east": (u, v + dz, u + dz, v + dz + dy),
        "south": (u + dz + dx, v + dz, u + 2 * dz + dx, v + dz + dy),
        "west": (u + 2 * dz + dx, v + dz, u + 2 * dz + 2 * dx, v + dz + dy),
        "up": (u + dz, v, u + dz + dx, v + dz),
        "down": (u + dz + dx, v, u + dz + 2 * dx, v + dz),
    }


def solid_box(name, bone, frm, to, uv):
    return {"name": name, "bone": bone, "from": frm, "to": to,
            "faces": {k: list(v) for k, v in box_uv_rects(frm, to, uv).items()}}


def plane(name, bone, frm, to, art):
    # planes are 0.4 units thick: hide the edge faces behind a transparent texel
    edge = [ATLAS_W - 3, ATLAS_H - 3, ATLAS_W - 2, ATLAS_H - 2]
    return {"name": name, "bone": bone, "from": frm, "to": to,
            "faces": {"north": list(art), "south": list(art),
                      "east": edge, "west": edge, "up": edge, "down": edge}}


def art_rect(name):
    u, v = CELL_POS[name]
    return [u, v, u + RW, v + RH]


PIVOT = (1.0, 3.0)


def build_model():
    bones = [
        {"name": "wing", "parent": None, "pivot": [PIVOT[0], PIVOT[1], 0.0], "rotation": [0, 0, -38]},
        {"name": "front_layer", "parent": "wing", "pivot": list(PIVOT) + [0.2], "rotation": [0, 0, -1.5]},
        {"name": "back_layer", "parent": "wing", "pivot": list(PIVOT) + [1.8], "rotation": [0, 0, 3.0]},
    ]
    cubes = [
        plane("plane_front", "front_layer", [0, 0, 0.0], [W, H, 0.4], art_rect("light")),
        plane("plane_back", "back_layer", [0, 0, 1.6], [W, H, 2.0], art_rect("dark")),
    ]
    return {"textureSize": [ATLAS_W, ATLAS_H], "bones": bones, "cubes": cubes}


FACES = [
    ("north", [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]),
    ("south", [(1, 0, 1), (0, 0, 1), (0, 1, 1), (1, 1, 1)]),
    ("west", [(0, 0, 1), (0, 0, 0), (0, 1, 0), (0, 1, 1)]),
    ("east", [(1, 0, 0), (1, 0, 1), (1, 1, 1), (1, 1, 0)]),
    ("up", [(0, 0, 1), (1, 0, 1), (1, 0, 0), (0, 0, 0)]),
    ("down", [(0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)]),
]


def rotz(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def bone_matrix(model, bone_name):
    by_name = {b["name"]: b for b in model["bones"]}
    chain, cur = [], by_name[bone_name]
    while cur is not None:
        chain.append(cur)
        cur = by_name.get(cur["parent"]) if cur["parent"] else None
    chain.reverse()

    Rm, t = np.eye(3), np.zeros(3)
    for b in chain:
        pivot = np.array(b["pivot"], float)
        r = rotz(b["rotation"][2])
        t = t + Rm @ (pivot - r @ pivot)
        Rm = Rm @ r
    return Rm, t


def to_mesh(model):
    verts, uvs, tris = [], [], []
    for cube in model["cubes"]:
        Rm, t = bone_matrix(model, cube["bone"])
        frm = np.array(cube["from"], float)
        to = np.array(cube["to"], float)
        for face, corners in FACES:
            r = cube["faces"][face]
            base = len(verts)
            for c in corners:
                p = frm + (to - frm) * np.array(c, float)
                p = Rm @ p + t
                verts.append([p[0], -p[1], p[2]])
                u = r[0] + (r[2] - r[0]) * c[0]
                v = r[1] + (r[3] - r[1]) * c[1]
                uvs.append((u / model["textureSize"][0], v / model["textureSize"][1]))
            tris += [(base, base + 1, base + 2), (base, base + 2, base + 3)]
    return np.array(verts), np.array(tris, np.int64), np.array(uvs)


def append_box(verts, faces, uvs, frm, to, rect, tex):
    frm = np.array(frm, float)
    to = np.array(to, float)
    for face, corners in FACES:
        base = len(verts)
        for c in corners:
            p = frm + (to - frm) * np.array(c, float)
            verts.append(list(p))
            u = rect[0] + (rect[2] - rect[0]) * c[0]
            v = rect[1] + (rect[3] - rect[1]) * c[1]
            uvs.append((u / tex[0], v / tex[1]))
        faces += [(base, base + 1, base + 2), (base, base + 2, base + 3)]


def build_scene(model):
    """Wing pair + player proxy (32 units tall, feet at y=0) in the preview frame."""
    v, f, u = to_mesh(model)
    verts, faces, uvs = [], [], []

    # lesson: pivot local (x, y) -> preview (x, -y); shoulder blades at y=21
    shift_r = np.array([2.0 - PIVOT[0], 21.0 + PIVOT[1], 2.0])
    shift_l = np.array([-2.0 + PIVOT[0], 21.0 + PIVOT[1], 2.0])
    right = v + shift_r
    left = v * np.array([-1.0, 1.0, 1.0]) + shift_l
    n = len(v)
    verts += [list(p) for p in right] + [list(p) for p in left]
    uvs += list(u) + list(u)
    faces += [(a, b, c) for a, b, c in f]
    faces += [(a + n, b + n, c + n) for a, b, c in f]

    tex = model["textureSize"]
    skin = (SKIN_UV[0], SKIN_UV[1], SKIN_UV[0] + 4, SKIN_UV[1] + 4)
    for frm, to in (
        ((-4, 24, -4), (4, 32, 4)),     # head
        ((-4, 12, -2), (4, 24, 2)),     # body
        ((-4, 0, -2), (0, 12, 2)),      # left leg
        ((0, 0, -2), (4, 12, 2)),       # right leg
        ((-8, 12, -2), (-4, 24, 2)),    # left arm
        ((4, 12, -2), (8, 24, 2)),      # right arm
    ):
        append_box(verts, faces, uvs, frm, to, skin, tex)

    return np.array(verts), np.array(faces, np.int64), np.array(uvs)


def make_atlas(pal):
    atlas = Image.new("RGBA", (ATLAS_W, ATLAS_H), (0, 0, 0, 0))
    for name, (u, v) in CELL_POS.items():
        atlas.alpha_composite(wing_art(TINTS[name], pal=pal), (u, v))
    d = ImageDraw.Draw(atlas)
    ax, ay, aw, ah = ARM_UV
    d.rectangle([ax, ay, ax + aw - 1, ay + ah - 1],
                fill=shade(pal["base"], 0.9), outline=pal["outline"])
    d.line([(ax + 1, ay + 1), (ax + aw - 2, ay + 1)], fill=pal["light"])
    ex, ey, ew, eh = EDGE_UV
    d.rectangle([ex, ey, ex + ew - 1, ey + eh - 1], fill=pal["shade"], outline=pal["outline"])
    sx, sy, sw, sh = SKIN_UV
    d.rectangle([sx, sy, sx + sw - 1, sy + sh - 1], fill=(120, 122, 130), outline=(72, 74, 82))
    return atlas


def item_icon(pal, size=16):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, (ang, ln, w) in enumerate(((-62, 11.5, 2.4), (-38, 10.5, 2.2), (-14, 8.5, 1.9))):
        a = math.radians(ang)
        x0, y0 = 2.5, 14.0
        x1, y1 = x0 + math.cos(a) * ln, y0 + math.sin(a) * ln
        nx, ny = -math.sin(a) * w, math.cos(a) * w
        d.polygon([(x0, y0), (x1 + nx, y1 + ny), (x1 + nx * 0.3, y1 + ny * 0.3),
                   (x1 - nx * 0.5, y1 - ny * 0.5), (x0, y0)],
                  fill=pal["mid"], outline=pal["outline"])
        d.line([(x0, y0), (x1, y1)], fill=pal["shade"])
    d.line([(2, 14), (6, 10)], fill=pal["light"])
    return img


RES = ROOT / "src" / "main" / "resources" / "assets" / "finery"


def main():
    OUT.mkdir(exist_ok=True)
    model = build_model()
    resources = RES / "wingmodels"
    textures = RES / "textures" / "wings"
    icons = RES / "textures" / "item"
    for folder in (resources, textures, icons):
        folder.mkdir(parents=True, exist_ok=True)
    (resources / "wing.json").write_text(json.dumps(model, indent=1), encoding="utf-8")
    (OUT / "wing.json").write_text(json.dumps(model, indent=1), encoding="utf-8")

    verts, faces, uv = to_mesh(model)
    sv, sf, su = build_scene(model)
    print("wing mesh:", verts.shape, faces.shape)

    size = 400
    sheet = Image.new("RGB", (size * 2, (size + 24) * 2), (16, 17, 20))
    dr = ImageDraw.Draw(sheet)
    for i, (variant, pal) in enumerate(PALETTES.items()):
        atlas = make_atlas(pal)
        atlas.save(textures / f"{variant}.png")
        item_icon(pal).save(icons / f"{variant}.png")
        if variant == "seraph_wings":
            atlas.save(OUT / "wing_atlas.png")
            (OUT / "item_icon.png").write_bytes((icons / f"{variant}.png").read_bytes())
        tex = np.asarray(atlas, float)
        img = rm.render_view(sv, sf, su, tex, rm.rot_y(-34) @ rm.rot_x(-6), size)
        x, y = (i % 2) * size, (i // 2) * (size + 24)
        sheet.paste(Image.fromarray(img), (x, y + 24))
        dr.text((x + 8, y + 6), variant, fill=(240, 235, 215))
    sheet.save(OUT / "wing_variants.png")

    # detail sheet for the gold/ivory variant
    tex = np.asarray(Image.open(textures / "seraph_wings.png").convert("RGBA"), float)
    views = [
        ("wing rot 0", np.eye(3), verts, faces, uv),
        ("wing rot 180", rm.rot_y(180), verts, faces, uv),
        ("back (player)", np.eye(3), sv, sf, su),
        ("3/4 back", rm.rot_y(-38) @ rm.rot_x(-6), sv, sf, su),
    ]
    sheet = Image.new("RGB", (size * 2, (size + 24) * 2), (16, 17, 20))
    dr = ImageDraw.Draw(sheet)
    for i, (label, Rm, vv, ff, uu) in enumerate(views):
        img = rm.render_view(vv, ff, uu, tex, Rm, size)
        x, y = (i % 2) * size, (i // 2) * (size + 24)
        sheet.paste(Image.fromarray(img), (x, y + 24))
        dr.text((x + 8, y + 6), label, fill=(240, 235, 215))
    sheet.save(OUT / "wing_preview.png")
    print("saved", OUT / "wing_preview.png", "and", OUT / "wing_variants.png")


if __name__ == "__main__":
    main()
