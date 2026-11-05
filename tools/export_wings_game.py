"""Bake Devil v1 and Dragon v1 into in-game wingmodels, textures and icons.

The designs are authored in player pixels with feet at y=0 and +z toward the
back camera. The renderer roots every wing at (1.55, 27, 2.55), the same frame
the approved angel used, so each design is shifted onto that root here.
"""
import json
import pathlib
import sys

import numpy as np
from PIL import Image, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parents[1]
ASSETS = ROOT / "src/main/resources/assets/finery"
OUT = ROOT / "_design"
sys.path.insert(0, str(ROOT / "tools"))
import devil_v1 as dv  # noqa: E402
import dragonwing_v1 as dw  # noqa: E402
import render_mesh as rm  # noqa: E402

ROOT_X = 1.55
ROOT_Y = 27.0
ROOT_Z = 2.55
DEVIL_ROOT = (dv.ROOT_X, 22.4, ROOT_Z)
DRAGON_MEMBRANE = (32, 8)


def pad_quad(verts, uvs):
    if len(verts) == 3:
        verts = list(verts) + [verts[2]]
        uvs = list(uvs) + [uvs[2]]
    return verts, uvs


def flat_quad(verts, uvs, color, tex_w, tex_h):
    verts, uvs = pad_quad(verts, uvs)
    vflat = [round(float(c), 4) for p in verts for c in p]
    uvflat = []
    for u, v in uvs:
        if u <= 1.5 and v <= 1.5:
            uvflat += [round(float(u) * tex_w, 2), round(float(v) * tex_h, 2)]
        else:
            uvflat += [round(float(u), 2), round(float(v), 2)]
    c = [int(round(min(1.0, max(0.0, float(x))) * 255.0)) for x in color]
    return {"v": vflat, "uv": uvflat, "c": c}


def write_model(name, tex_size, quads):
    data = {"textureSize": list(tex_size), "quads": quads}
    path = ASSETS / "wingmodels" / f"{name}.json"
    path.write_text(json.dumps(data, separators=(",", ":")))
    lo = np.array([q["v"][i:i + 3] for q in quads for i in range(0, 12, 3)], float)
    print(f"{name}: {len(quads)} quads, {path.stat().st_size / 1024:.0f} KiB, "
          f"bbox x {lo[:,0].min():.1f}..{lo[:,0].max():.1f} "
          f"y {lo[:,1].min():.1f}..{lo[:,1].max():.1f} "
          f"z {lo[:,2].min():.1f}..{lo[:,2].max():.1f}")
    return path


def build_devil():
    atlas = dv.build_atlas()
    atlas.save(ASSETS / "textures/wings/devil_wings.png")
    quads = []
    for verts, uvs in dv.membrane_quads() + dv.bone_quads():
        vv = [(x + DEVIL_ROOT[0] - ROOT_X,
               y + DEVIL_ROOT[1] - ROOT_Y,
               z + DEVIL_ROOT[2] - ROOT_Z) for x, y, z in verts]
        quads.append(flat_quad(vv, uvs, (1.0, 1.0, 1.0), 512, 512))
    write_model("devil_wings", (512, 512), quads)
    return atlas, 512


def build_dragon():
    atlas = dw.build_atlas()
    # entity lighting is much darker than the preview: lift the atlas shadows
    arr = np.asarray(atlas.convert("RGBA"), np.float32)
    arr[..., :3] = np.clip(((arr[..., :3] / 255.0) ** 0.72) * 255.0, 0, 255)
    atlas = Image.fromarray(arr.astype(np.uint8), "RGBA")
    atlas.save(ASSETS / "textures/wings/dragon_wings.png")
    dw.GAME_LOD = 0.25
    parts = (dw.membrane_quads(*DRAGON_MEMBRANE) + dw.crease_quads()
             + dw.bone_quads() + dw.scale_plates() + dw.leading_bands())
    dw.GAME_LOD = 1.0
    quads = []
    for verts, uvs, tint, *_rest in parts:
        vv = [(x - ROOT_X, y - ROOT_Y, z - ROOT_Z) for x, y, z in verts]
        # entity lighting is darker than the offline preview: lift the dark
        # bone/claw tints so the skeleton stays readable in game
        lifted = [min(1.0, float(c) ** 0.45) for c in tint]
        quads.append(flat_quad(vv, uvs, lifted, 1024, 1024))
    write_model("dragon_wings", (1024, 1024), quads)
    return atlas, 1024


def mesh_arrays(quads, tex_size):
    verts, uvs, faces, cols = [], [], [], []
    for q in quads:
        v, uv, c = q["v"], q["uv"], q["c"]
        base = len(verts)
        for k in range(4):
            verts.append(v[k * 3:k * 3 + 3])
            uvs.append([uv[k * 2] / tex_size, uv[k * 2 + 1] / tex_size])
            cols.append([x / 255.0 for x in c])
        faces.append((base, base + 1, base + 2))
        faces.append((base, base + 2, base + 3))
    return (np.array(verts, float), np.array(faces, np.int64),
            np.array(uvs, float), np.array(cols, float))


def mirror_quad(q, gap):
    v, uv, c = q["v"], q["uv"], q["c"]
    right = [v[i] + gap for i in range(0, 12, 3)]
    verts = []
    for k in range(4):
        verts += [-(v[k * 3] + gap), v[k * 3 + 1], v[k * 3 + 2]]
    left = {"v": verts, "uv": uv, "c": c}
    right = {"v": list(v), "uv": uv, "c": c}
    return left, right


def make_icon(atlas, quads, tex_size, path):
    tex = np.asarray(atlas.convert("RGBA"), float)
    pair = []
    for q in quads:
        left, right = mirror_quad(q, 1.15)
        pair += [right, left]
    v, f, u, c = mesh_arrays(pair, tex_size)
    rgba = rm.render_view(v, f, u, tex, np.eye(3), 320, alpha=True,
                          shade_lo=0.90, shade_hi=0.24, colors=c)
    img = Image.fromarray(rgba, "RGBA")
    a = np.asarray(img)[..., 3]
    ys, xs = np.where(a > 12)
    crop = img.crop((int(xs.min()), int(ys.min()),
                     int(xs.max()) + 1, int(ys.max()) + 1))
    crop.thumbnail((28, 28), Image.LANCZOS)
    out = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    ox, oy = (32 - crop.width) // 2, (32 - crop.height) // 2
    alpha = crop.getchannel("A").point(lambda x: 255 if x > 88 else 0)
    outline = Image.new("L", (32, 32), 0)
    outline.paste(alpha.filter(ImageFilter.MaxFilter(3)), (ox, oy))
    rim = Image.new("RGBA", (32, 32), (62, 65, 82, 255))
    out.paste(rim, (0, 0), outline)
    out.alpha_composite(crop, (ox, oy))
    out.save(path)
    return crop


def main():
    (ASSETS / "textures/wings").mkdir(parents=True, exist_ok=True)
    (ASSETS / "wingmodels").mkdir(parents=True, exist_ok=True)
    (ASSETS / "textures/item").mkdir(parents=True, exist_ok=True)
    OUT.mkdir(exist_ok=True)

    devil_atlas, devil_tex = build_devil()
    dragon_atlas, dragon_tex = build_dragon()
    devil_model = json.loads((ASSETS / "wingmodels/devil_wings.json").read_text())
    dragon_model = json.loads((ASSETS / "wingmodels/dragon_wings.json").read_text())

    icons = Image.new("RGBA", (128, 64), (0, 0, 0, 0))
    for i, (atlas, quads, tex, name) in enumerate((
            (devil_atlas, devil_model["quads"], devil_tex, "devil_wings"),
            (dragon_atlas, dragon_model["quads"], dragon_tex, "dragon_wings"))):
        icon = make_icon(atlas, quads, tex, ASSETS / f"textures/item/{name}.png")
        big = icon.resize((56, 56), Image.NEAREST)
        icons.alpha_composite(big, (i * 64 + 4, 4))
    icons.save(OUT / "game_wing_icons.png")
    print("saved", OUT / "game_wing_icons.png")


if __name__ == "__main__":
    main()
