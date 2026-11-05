"""Generate the four wing styles: model + atlas + preview per variant.

Everything is parametric: one feather layout routine drives the angel, demon
and void wings (different angles, lengths, palettes and trims), while the fae
wing gets its own butterfly layout. Outputs land directly in the mod resources.
"""
import json
import math
import pathlib
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import wing_design2 as W  # noqa: E402

RES = ROOT / "src" / "main" / "resources" / "assets" / "finery"
OUT = ROOT / "_design"
SCALE = W.SCALE


# ── palettes ────────────────────────────────────────────────────────────────
PAL = {
    "seraph_wings": dict(
        outline=(58, 46, 36), deep=(150, 152, 188), base=(226, 227, 238),
        light=(247, 248, 252), white=(255, 255, 255),
        sheen=(196, 200, 244), sheen2=(232, 216, 246),
        gold=(240, 202, 112), gold_dark=(158, 114, 44), gold_light=(255, 246, 198),
        gem1=(58, 96, 216), gem2=(126, 62, 190)),
    "emberwing": dict(
        outline=(34, 12, 8), deep=(84, 26, 16), base=(138, 46, 22),
        light=(216, 92, 32), white=(255, 190, 104),
        sheen=(255, 112, 36), sheen2=(255, 206, 120),
        gold=(250, 148, 52), gold_dark=(112, 30, 10), gold_light=(255, 226, 150),
        gem1=(255, 96, 24), gem2=(178, 26, 18)),
    "voidwing": dict(
        outline=(10, 8, 22), deep=(38, 28, 76), base=(60, 44, 114),
        light=(112, 92, 190), white=(200, 190, 255),
        sheen=(104, 214, 255), sheen2=(178, 140, 255),
        gold=(148, 226, 255), gold_dark=(48, 82, 142), gold_light=(226, 250, 255),
        gem1=(96, 220, 255), gem2=(160, 120, 255)),
    "fae_wings": dict(
        outline=(16, 44, 30), deep=(38, 104, 66), base=(62, 150, 92),
        light=(126, 216, 148), white=(220, 255, 226),
        sheen=(184, 248, 196), sheen2=(232, 252, 172),
        gold=(240, 228, 140), gold_dark=(120, 110, 44), gold_light=(254, 250, 202),
        gem1=(96, 200, 130), gem2=(206, 208, 72)),
}

# ── per-style shape parameters ──────────────────────────────────────────────
STYLE = {
    "seraph_wings": dict(n=11, ang=(82, -62), ln=(9.4, 5.4), wd=(5.5, 1.0),
                         ornate=0.68, arm="gold", spikes=0, glow=False, stars=False),
    "emberwing": dict(n=10, ang=(88, -48), ln=(8.2, 6.6), wd=(5.2, 1.0),
                      ornate=0.34, arm="bone", spikes=3, glow=True, stars=False),
    "voidwing": dict(n=13, ang=(86, -68), ln=(9.6, 6.2), wd=(4.4, 0.9),
                     ornate=0.22, arm="void", spikes=2, glow=True, stars=True),
}


def arm_point(t):
    return W.arm_at(t)


# ── layout ──────────────────────────────────────────────────────────────────
def feather_layout(st):
    out = []
    for i, (t, ang, ln, wd) in enumerate(((0.02, 112.0, 7.4, 4.8),
                                          (0.08, 108.0, 8.0, 5.2))):
        p, n = arm_point(t), W.arm_nrm(t)
        out.append(dict(kind="tertial", root=(p[0] + n[0] * 0.7, p[1] + n[1] * 0.7),
                        angle=ang, length=ln, width=wd, z=0.14 + i * 0.10))

    n = st["n"]
    for i in range(n):
        t = 0.10 + 0.90 * i / (n - 1)
        p, nv = arm_point(t), W.arm_nrm(t)
        ang = st["ang"][0] + (st["ang"][1] - st["ang"][0]) * (t ** 1.05)
        ln = st["ln"][0] + st["ln"][1] * math.sin(math.pi * (0.10 + 0.90 * t))
        wd = st["wd"][0] - st["wd"][1] * t
        out.append(dict(kind="primary", root=(p[0] + nv[0] * 0.8, p[1] + nv[1] * 0.8),
                        angle=ang, length=ln, width=wd, z=0.30 + 0.11 * i))

    M = 9
    for i in range(M):
        t = 0.06 + 0.90 * i / (M - 1)
        p, nv = arm_point(t), W.arm_nrm(t)
        ang = st["ang"][0] + (st["ang"][1] - st["ang"][0]) * (t ** 1.05) - 7.0
        ln = (st["ln"][0] + st["ln"][1] * math.sin(math.pi * (0.10 + 0.90 * t))) * 0.46 + 1.4
        out.append(dict(kind="greater", root=(p[0] + nv[0] * 0.9, p[1] + nv[1] * 0.9),
                        angle=ang, length=ln, width=(st["wd"][0] - st["wd"][1] * t) * 0.90,
                        z=1.15, ornate=t < st["ornate"], gems=2 if t < 0.30 else 1))

    K = 8
    for i in range(K):
        t = 0.04 + 0.78 * i / (K - 1)
        p, nv = arm_point(t), W.arm_nrm(t)
        ang = st["ang"][0] + (st["ang"][1] - st["ang"][0]) * (t ** 1.05) - 13.0
        ln = (st["ln"][0] + st["ln"][1] * math.sin(math.pi * (0.10 + 0.90 * t))) * 0.26 + 1.4
        out.append(dict(kind="lesser", root=(p[0] + nv[0] * 1.0, p[1] + nv[1] * 1.0),
                        angle=ang, length=ln, width=(st["wd"][0] - st["wd"][1] * t) * 0.80,
                        z=1.40, ornate=t < st["ornate"] * 0.8, gems=1))

    J = 7
    for i in range(J):
        t = 0.03 + 0.74 * i / (J - 1)
        p, nv = arm_point(t), W.arm_nrm(t)
        ang = st["ang"][0] + (st["ang"][1] - st["ang"][0]) * (t ** 1.05) - 20.0
        ln = (st["ln"][0] + st["ln"][1] * math.sin(math.pi * (0.10 + 0.90 * t))) * 0.15 + 1.2
        out.append(dict(kind="tuft", root=(p[0] + nv[0] * 1.0, p[1] + nv[1] * 1.0),
                        angle=ang, length=ln, width=(st["wd"][0] - st["wd"][1] * t) * 0.64,
                        z=1.65, ornate=t < st["ornate"] * 0.7, gems=1))

    for i, (ang, ln, wd) in enumerate(((150.0, 4.6, 3.6), (136.0, 5.2, 3.8))):
        out.append(dict(kind="tuft", root=(0.9, 1.2), angle=ang, length=ln, width=wd,
                        z=1.85 + i * 0.08, ornate=True, gems=1))

    # claw / spike feathers along the leading edge
    for i in range(st["spikes"]):
        t = 0.62 + 0.14 * i
        p = arm_point(t)
        out.append(dict(kind="tip", root=(p[0] - 0.8, p[1] - 1.0), angle=-72.0 + 12 * i,
                        length=5.4 - 0.6 * i, width=2.2, z=2.10 + 0.04 * i))

    # curled tip
    out.append(dict(kind="tip", root=(19.2, -10.8), angle=-40.0,
                    length=4.0, width=2.4, z=0.22))
    return out


# ── sprites ─────────────────────────────────────────────────────────────────
def tint_sprite(img, pal, st, f):
    """Style post-pass: ember glow at the tips, void starfield."""
    a = np.array(img).astype(float)
    h, w = a.shape[:2]
    if st["glow"]:
        u = np.arange(w)[None, :] / max(w - 1, 1)
        k = np.clip((u - 0.55) / 0.45, 0, 1) ** 1.6
        a[:, :, :3] = a[:, :, :3] + (np.array(pal["white"], float) - a[:, :, :3]) * (0.55 * k)[:, :, None]
    if st["stars"]:
        rng = np.random.default_rng(abs(hash(f.get("kind", "x"))) % 9999)
        n = max(2, int(w * h / 900))
        for _ in range(n):
            x, y = int(rng.integers(1, max(2, w - 1))), int(rng.integers(1, max(2, h - 1)))
            if a[y, x, 3] > 0:
                a[y, x, :3] = np.array(pal["white"], float)
                if 0 < x + 1 < w and a[y, x + 1, 3] > 0:
                    a[y, x + 1, :3] = (a[y, x + 1, :3] + np.array(pal["sheen"], float)) * 0.5
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")


def feather_sprite(f, pal, st):
    return tint_sprite(W.feather_sprite(f, pal), pal, st, f)


def arm_quads(rect, width, z, n_seg=3):
    quads = []
    u0, v0, u1, v1 = rect
    acc = 0.0
    for i in range(len(W.ARM_PTS) - 1):
        ta = acc / W._ARM_LEN
        acc += W._ARM_SEG[i]
        tb = acc / W._ARM_LEN
        a, b = W.ARM_PTS[i], W.ARM_PTS[i + 1]
        na, nb = W.arm_nrm(ta), W.arm_nrm(tb)
        wa = width * 0.5 * (1.0 - 0.62 * max(0.0, (ta - 0.06) / 0.94))
        wb = width * 0.5 * (1.0 - 0.62 * max(0.0, (tb - 0.06) / 0.94))
        v = [(a[0] - na[0] * wa, a[1] - na[1] * wa, z),
             (b[0] - nb[0] * wb, b[1] - nb[1] * wb, z),
             (b[0] + nb[0] * wb, b[1] + nb[1] * wb, z),
             (a[0] + na[0] * wa, a[1] + na[1] * wa, z)]
        ua = u0 + (u1 - u0) * ta
        ub = u0 + (u1 - u0) * tb
        quads.append(dict(layer="arm", v=v, uv=[(ua, v0), (ub, v0), (ub, v1), (ua, v1)]))
    return quads


def arm_sprite(pal, kind):
    w, h = W.ARM_PX_W, W.ARM_PX_H
    xs = np.arange(w)
    u = xs / max(w - 1, 1)
    taper = 1.0 - 0.62 * np.clip((u - 0.06) / 0.94, 0, 1)
    half = h * 0.5 * taper
    cy = h * 0.5 + np.sin(u * math.pi) * h * 0.06
    ys = np.arange(h)[:, None]
    inside = (ys >= cy - half[None, :]) & (ys <= cy + half[None, :])
    d = (ys - (cy - half)[None, :]) / np.maximum(2 * half[None, :], 1e-6) * 2 - 1

    if kind == "bone":
        core = np.array(pal["deep"], float)
        edge = np.array(pal["outline"], float)
        hot = np.array(pal["light"], float)
        col = core[None, None, :] + (edge[None, None, :] - core[None, None, :]) * np.clip(np.abs(d), 0, 1)[:, :, None]
        crack = (np.abs(((u[None, :] * w / 7.0) % 1.0) - 0.5) < 0.06) & (np.abs(d) < 0.55)
        col = np.where(crack[:, :, None], hot, col)
    else:  # void spine
        core = np.array(pal["deep"], float)
        glow = np.array(pal["gold"], float)
        col = core[None, None, :] * (1.0 - 0.35 * np.abs(d)[:, :, None])
        col = col + (glow - col) * np.clip(1.0 - np.abs(d) / 0.22, 0, 1)[:, :, None]

    rim = inside & ~W._erode(inside, 1)
    col[rim] = pal["outline"]
    px = np.zeros((h, w, 4), np.uint8)
    px[:, :, :3] = np.clip(col, 0, 255).astype(np.uint8)
    px[:, :, 3] = np.where(inside, 255, 0).astype(np.uint8)
    return Image.fromarray(px, "RGBA")


# ── fae (butterfly) ─────────────────────────────────────────────────────────
def _bez(p0, p1, p2, n=26):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])
            for t in (i / (n - 1) for i in range(n))]


def fae_sprites(pal, w=240, h=150):
    """Fore and hind butterfly wing drawn in quad space: root left, tip right."""

    def lobe(fore=True):
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        root = (1, h * 0.60 if fore else h * 0.46)
        if fore:
            tip, c_up, c_low = (w * 0.98, h * 0.26), (w * 0.34, -0.04 * h), (w * 0.56, h * 1.02)
        else:
            tip, c_up, c_low = (w * 0.92, h * 0.56), (w * 0.36, h * 0.06), (w * 0.52, h * 1.00)
        pts = _bez(root, c_up, tip) + _bez(tip, c_low, root)[1:]
        d.polygon(pts, fill=pal["base"] + (255,))
        d.line(pts + [pts[0]], fill=pal["outline"] + (255,), width=3, joint="curve")

        inner = [(root[0] + (x - root[0]) * 0.62, root[1] + (y - root[1]) * 0.62) for x, y in pts]
        d.polygon(inner, fill=W.mix(pal["base"], pal["light"], 0.55) + (255,))
        core = [(root[0] + (x - root[0]) * 0.26, root[1] + (y - root[1]) * 0.26) for x, y in pts]
        d.polygon(core, fill=pal["light"] + (255,))

        vein = W.mix(pal["deep"], pal["outline"], 0.30)
        for k in range(6):
            idx = int((k + 1) / 7 * (len(pts) - 1))
            d.line([root, pts[idx]], fill=vein + (255,), width=2)
        d.line([root, tip], fill=pal["gold"] + (255,), width=4)

        for fx, fy, rr in ((0.40, 0.30, 11), (0.62, 0.22, 9), (0.54, 0.55, 8), (0.76, 0.40, 7)):
            sx, sy = w * fx, h * (fy if fore else fy + 0.18)
            d.ellipse([sx - rr, sy - rr * 0.8, sx + rr, sy + rr * 0.8],
                      fill=pal["white"] + (255,), outline=pal["deep"] + (255,))
            d.ellipse([sx - rr * 0.45, sy - rr * 0.36, sx + rr * 0.45, sy + rr * 0.36],
                      fill=pal["sheen2"] + (255,))
        return img

    return lobe(True), lobe(False)


def build_fae(pal):
    fore, hind = fae_sprites(pal)
    sizes = [fore.size, hind.size, (int(4.2 * SCALE), int(4.2 * SCALE)), (8, 8)]
    pos, height = W.pack(sizes)
    rects = [(x, y, x + w, y + h) for (x, y), (w, h) in zip(pos, sizes)]

    quads = []
    specs = [(rects[0], (0.6, -0.6), -46.0, 15.5, 11.0, 1.30),
             (rects[1], (0.6, 0.4), 34.0, 12.4, 9.0, 1.10)]
    for (rect, root, ang, ln, wd, z) in specs:
        a = math.radians(ang)
        dx, dy = math.cos(a), math.sin(a)
        px, py = -dy, dx
        hw = wd * 0.5
        v = [(root[0] - px * hw, root[1] - py * hw, z),
             (root[0] + dx * ln - px * hw, root[1] + dy * ln - py * hw, z),
             (root[0] + dx * ln + px * hw, root[1] + dy * ln + py * hw, z),
             (root[0] + px * hw, root[1] + py * hw, z)]
        quads.append(dict(layer="coverts",
                          v=v, uv=[(rect[0], rect[1]), (rect[2], rect[1]),
                                   (rect[2], rect[3]), (rect[0], rect[3])]))

    # small body ornament between the wings
    cr = rects[2]
    s = 2.0
    quads.append(dict(layer="arm", v=[(-s, -s - 0.4, 2.2), (s, -s - 0.4, 2.2),
                                      (s, s + 0.4, 2.2), (-s, s + 0.4, 2.2)],
                      uv=[(cr[0], cr[1]), (cr[2], cr[1]), (cr[2], cr[3]), (cr[0], cr[3])]))

    layers = [dict(name="coverts", pivot=[0.8, 0.0, 1.4], sway=2.4),
              dict(name="arm", pivot=[0.8, 0.0, 2.4], sway=0.6)]
    model = dict(textureSize=[W.ATLAS_W, height], layers=layers, quads=quads)
    gu = rects[-1]
    model["previewUv"] = [(gu[0] + 4) / W.ATLAS_W, (gu[1] + 4) / height]

    atlas = Image.new("RGBA", (W.ATLAS_W, height), (0, 0, 0, 0))
    atlas.alpha_composite(fore, (rects[0][0], rects[0][1]))
    atlas.alpha_composite(hind, (rects[1][0], rects[1][1]))
    atlas.alpha_composite(W.clasp_sprite(pal, 2.0), (rects[2][0], rects[2][1]))
    ImageDraw.Draw(atlas).rectangle([gu[0], gu[1], gu[2] - 1, gu[3] - 1], fill=(120, 122, 130, 255))
    return model, atlas


# ── build a feathered style ─────────────────────────────────────────────────
def build_feathered(variant, st):
    pal = PAL[variant]
    feats = feather_layout(st)
    sizes = [W.sprite_size(f) for f in feats]
    sizes += [(W.ARM_PX_W, W.ARM_PX_H), (int(5.0 * SCALE), int(5.0 * SCALE)), (8, 8)]
    pos, height = W.pack(sizes)
    rects = [(x, y, x + w, y + h) for (x, y), (w, h) in zip(pos, sizes)]

    quads = []
    for f, r in zip(feats, rects):
        quads.append(W.quad_from_feather(f, r, None))
    quads += arm_quads(rects[-3], 5.0, 2.35)

    cr = rects[-2]
    s = 2.0
    quads.append(dict(layer="arm", v=[(1.6 - s, 0.4 - s, 2.55), (1.6 + s, 0.4 - s, 2.55),
                                      (1.6 + s, 0.4 + s, 2.55), (1.6 - s, 0.4 + s, 2.55)],
                      uv=[(cr[0], cr[1]), (cr[2], cr[1]), (cr[2], cr[3]), (cr[0], cr[3])]))

    layers = [dict(name="primaries", pivot=[1.6, 0.4, 0.0], sway=1.1),
              dict(name="coverts", pivot=[1.6, 0.4, 1.6], sway=1.7),
              dict(name="arm", pivot=[1.6, 0.4, 2.8], sway=0.5)]
    model = dict(textureSize=[W.ATLAS_W, height], layers=layers, quads=quads)
    gu = rects[-1]
    model["previewUv"] = [(gu[0] + 4) / W.ATLAS_W, (gu[1] + 4) / height]

    atlas = Image.new("RGBA", (W.ATLAS_W, height), (0, 0, 0, 0))
    for f, r in zip(feats, rects):
        atlas.alpha_composite(feather_sprite(f, pal, st), (r[0], r[1]))
    atlas.alpha_composite(W.arm_sprite(pal) if st["arm"] == "gold" else arm_sprite(pal, st["arm"]),
                          (rects[-3][0], rects[-3][1]))
    atlas.alpha_composite(W.clasp_sprite(pal, 2.0), (rects[-2][0], rects[-2][1]))
    ImageDraw.Draw(atlas).rectangle([gu[0], gu[1], gu[2] - 1, gu[3] - 1], fill=(120, 122, 130, 255))
    return model, atlas


def main():
    OUT.mkdir(exist_ok=True)
    (RES / "wingmodels").mkdir(parents=True, exist_ok=True)
    (RES / "textures" / "wings").mkdir(parents=True, exist_ok=True)
    (RES / "textures" / "item").mkdir(parents=True, exist_ok=True)

    previews = {}
    for variant, st in STYLE.items():
        model, atlas = build_feathered(variant, st)
        write(variant, model, atlas)
        previews[variant] = (model, atlas)

    model, atlas = build_fae(PAL["fae_wings"])
    write("fae_wings", model, atlas)
    previews["fae_wings"] = (model, atlas)

    # contact sheet
    tiles = []
    for variant, (model, atlas) in previews.items():
        tw, th = model["textureSize"]
        v, f, u = W.to_tris(model, tw, th)
        sv, sf, su = W.proxy_scene(v, f, u, tuple(model["previewUv"]))
        tex = np.asarray(atlas, float)
        img = W.rm.render_view(sv, sf, su, tex, np.eye(3), 420)
        tile = Image.fromarray(img)
        dr = ImageDraw.Draw(tile)
        dr.text((10, 8), variant, fill=(240, 235, 215))
        tiles.append(tile)
    sheet = Image.new("RGB", (840, 440 * 2), (16, 17, 20))
    for i, tile in enumerate(tiles):
        sheet.paste(tile, ((i % 2) * 420, (i // 2) * 440))
    sheet.save(OUT / "wings4_preview.png")
    print("wrote 4 wings", [p for p in previews])


def write(variant, model, atlas):
    (RES / "wingmodels" / f"{variant}.json").write_text(json.dumps(model), encoding="utf-8")
    atlas.save(RES / "textures" / "wings" / f"{variant}.png")
    W.item_icon(PAL[variant]).save(RES / "textures" / "item" / f"{variant}.png")
    print(f"  {variant}: quads={len(model['quads'])} atlas={atlas.size}")


if __name__ == "__main__":
    main()
