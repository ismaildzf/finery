"""Feathered wing designer v2 â€” real layered feather geometry (baked quads).

Model space: 1 unit = 1 pixel = 1/16 block, Y down, +X outboard, +Z backward.
Every feather is its own alpha quad with its own atlas sprite, so the wing has
true layered depth instead of one painted card.

Outputs
  _design/wing_v2.json          model for the Java renderer (baked quads)
  _design/v2_preview.png        offline multi-view render (wing pair + proxy)
  _design/v2_variants.png       all palettes
  _design/v2_atlas.png          seraph atlas
  _design/bb_payload.json       vertices/faces/uvs for the Blockbench push
  src/main/resources/...        wing.json, 4 atlases, 4 item icons
"""
import json
import math
import pathlib
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import render_mesh as rm  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "_design"
RES = ROOT / "src" / "main" / "resources" / "assets" / "finery"

SCALE = 8                      # texels per model unit
PAD = 2
ATLAS_W = 1024

# â”€â”€ palette â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
PALETTES = {
    # pearl-white flight feathers, lavender sheen, heavy gold filigree with gems
    "seraph_wings": dict(
        outline=(64, 52, 42), deep=(152, 154, 190), base=(226, 227, 238),
        light=(247, 248, 252), white=(255, 255, 255),
        sheen=(196, 200, 244), sheen2=(232, 216, 246),
        gold=(240, 202, 112), gold_dark=(158, 114, 44), gold_light=(255, 246, 198),
        gem1=(58, 96, 216), gem2=(126, 62, 190)),
    "emberwing": dict(
        outline=(58, 20, 10), deep=(150, 46, 16), base=(204, 82, 24),
        light=(250, 152, 56), white=(255, 226, 168),
        sheen=(255, 196, 96), sheen2=(255, 236, 170),
        gold=(236, 176, 62), gold_dark=(132, 56, 14), gold_light=(255, 234, 150),
        gem1=(236, 92, 32), gem2=(160, 32, 24)),
    "voidwing": dict(
        outline=(26, 18, 46), deep=(82, 62, 128), base=(112, 86, 176),
        light=(172, 146, 226), white=(232, 222, 255),
        sheen=(150, 176, 255), sheen2=(206, 172, 248),
        gold=(150, 206, 255), gold_dark=(64, 100, 164), gold_light=(224, 244, 255),
        gem1=(96, 168, 255), gem2=(168, 104, 236)),
    "fae_wings": dict(
        outline=(18, 44, 30), deep=(44, 108, 66), base=(66, 148, 88),
        light=(126, 210, 134), white=(214, 252, 218),
        sheen=(176, 240, 190), sheen2=(226, 250, 176),
        gold=(238, 226, 136), gold_dark=(128, 118, 46), gold_light=(252, 248, 198),
        gem1=(84, 176, 120), gem2=(196, 196, 64)),
}


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


# â”€â”€ arm curve â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
ARM_PTS = [(0.6, 0.9), (5.0, -2.4), (9.6, -6.7), (13.6, -10.4)]
_ARM_SEG = [math.dist(ARM_PTS[i], ARM_PTS[i + 1]) for i in range(len(ARM_PTS) - 1)]
_ARM_LEN = sum(_ARM_SEG)


def arm_at(t):
    """Point at arc-length fraction t in [0, 1]."""
    d = min(max(t, 0.0), 1.0) * _ARM_LEN
    for i, seg in enumerate(_ARM_SEG):
        if d <= seg or i == len(_ARM_SEG) - 1:
            f = d / seg
            a, b = ARM_PTS[i], ARM_PTS[i + 1]
            return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
        d -= seg
    return ARM_PTS[-1]


def arm_dir(t):
    e = 0.01
    a = arm_at(max(0.0, t - e))
    b = arm_at(min(1.0, t + e))
    dx, dy = b[0] - a[0], b[1] - a[1]
    ln = math.hypot(dx, dy) or 1.0
    return (dx / ln, dy / ln)


def arm_nrm(t):
    dx, dy = arm_dir(t)
    return (-dy, dx)


# â”€â”€ feather layout â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def ease(t):
    return t * t * (3.0 - 2.0 * t)


def primary_angle(t):
    """Degrees from +X toward +Y (down). Inner feathers hang, tip feathers point out."""
    return 82.0 - 62.0 * (t ** 1.05)


def primary_len(t):
    return 9.4 + 5.4 * math.sin(math.pi * (0.10 + 0.90 * t))


def layout():
    """Palette-independent feather list: kind, root, angle, length, width, z."""
    out = []

    # tertials fill the inner corner next to the spine
    for i, (t, ang, ln, wd) in enumerate(((0.02, 112.0, 7.4, 4.8),
                                          (0.08, 108.0, 8.0, 5.2))):
        p = arm_at(t)
        n = arm_nrm(t)
        out.append(dict(kind="tertial", root=(p[0] + n[0] * 0.7, p[1] + n[1] * 0.7),
                        angle=ang, length=ln, width=wd, z=0.14 + i * 0.10))

    # primaries (the trailing edge of the wing)
    N = 11
    for i in range(N):
        t = 0.12 + 0.88 * i / (N - 1)
        p = arm_at(t)
        n = arm_nrm(t)
        out.append(dict(kind="primary",
                        root=(p[0] + n[0] * 0.8, p[1] + n[1] * 0.8),
                        angle=primary_angle(t),
                        length=primary_len(t),
                        width=5.5 - 1.1 * t,
                        z=0.30 + 0.11 * i))

    # curled tip: a thin feather hooks up past the wrist
    out.append(dict(kind="tip", root=(19.2, -10.8), angle=-40.0,
                    length=4.0, width=2.4, z=0.22))

    # greater coverts
    M = 9
    for i in range(M):
        t = 0.06 + 0.90 * i / (M - 1)
        p = arm_at(t)
        n = arm_nrm(t)
        out.append(dict(kind="greater",
                        root=(p[0] + n[0] * 0.9, p[1] + n[1] * 0.9),
                        angle=primary_angle(t) - 7.0,
                        length=primary_len(t) * 0.46 + 1.4,
                        width=(5.5 - 1.1 * t) * 0.90,
                        z=1.15,
                        ornate=t < 0.68, gems=2 if t < 0.30 else 1))

    # lesser coverts
    K = 8
    for i in range(K):
        t = 0.04 + 0.78 * i / (K - 1)
        p = arm_at(t)
        n = arm_nrm(t)
        out.append(dict(kind="lesser",
                        root=(p[0] + n[0] * 1.0, p[1] + n[1] * 1.0),
                        angle=primary_angle(t) - 13.0,
                        length=primary_len(t) * 0.26 + 1.4,
                        width=(5.5 - 1.1 * t) * 0.80,
                        z=1.40,
                        ornate=t < 0.55, gems=1))

    # marginal coverts tucked under the leading edge
    J = 7
    for i in range(J):
        t = 0.03 + 0.74 * i / (J - 1)
        p = arm_at(t)
        n = arm_nrm(t)
        out.append(dict(kind="tuft",
                        root=(p[0] + n[0] * 1.0, p[1] + n[1] * 1.0),
                        angle=primary_angle(t) - 20.0,
                        length=primary_len(t) * 0.15 + 1.2,
                        width=(5.5 - 1.1 * t) * 0.64,
                        z=1.65,
                        ornate=t < 0.45, gems=1))

    # shoulder tuft hides the attachment point
    for i, (ang, ln, wd) in enumerate(((150.0, 4.6, 3.6), (136.0, 5.2, 3.8))):
        out.append(dict(kind="tuft", root=(2.0, 1.4), angle=ang,
                        length=ln, width=wd, z=1.85 + i * 0.08,
                        ornate=True, gems=1))
    return out


# â”€â”€ sprites â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
PROFILES = {
    #        u,   half-width factor
    "primary": [(0.00, 0.46), (0.06, 0.88), (0.16, 1.00), (0.68, 1.00),
                (0.86, 0.72), (0.96, 0.34), (1.00, 0.06)],
    "tertial": [(0.00, 0.48), (0.08, 0.90), (0.20, 1.00), (0.70, 0.98),
                (0.88, 0.74), (1.00, 0.18)],
    "greater": [(0.00, 0.52), (0.10, 0.92), (0.26, 1.00), (0.74, 0.96),
                (0.92, 0.66), (1.00, 0.20)],
    "lesser":  [(0.00, 0.56), (0.12, 0.94), (0.32, 1.00), (0.78, 0.92),
                (0.94, 0.62), (1.00, 0.22)],
    "tuft":    [(0.00, 0.58), (0.14, 0.96), (0.36, 1.00), (0.80, 0.90),
                (0.95, 0.56), (1.00, 0.20)],
    "tip":     [(0.00, 0.62), (0.14, 1.00), (0.50, 0.88), (0.82, 0.50),
                (1.00, 0.05)],
}

# colour ramp across the feather: -1 = leading (lit) edge, +1 = trailing (shadow) edge
RAMP = [(-1.00, "white"), (-0.45, "white"), (-0.08, "light"),
        (0.42, "base"), (0.78, "deep"), (1.00, "deep")]


def _interp(prof, u):
    for i in range(len(prof) - 1):
        u0, v0 = prof[i]
        u1, v1 = prof[i + 1]
        if u <= u1:
            f = (u - u0) / max(u1 - u0, 1e-6)
            return v0 + (v1 - v0) * f
    return prof[-1][1]


def sprite_size(f):
    w = max(8, int(round(f["length"] * SCALE)))
    h = max(6, int(round(f["width"] * SCALE)))
    return w, h


def feather_sprite(f, pal, seed=0):
    """One feather, base at u=0 (left), tip at u=1 (right). Hard alpha edges."""
    w, h = sprite_size(f)
    prof = PROFILES[f["kind"]]
    xs = np.arange(w)
    u = xs / max(w - 1, 1)

    half = np.array([_interp(prof, float(t)) * h * 0.5 for t in u])
    # asymmetric: leading (âˆ’perp) side is a touch flatter on long feathers
    lead = half * (0.94 if f["kind"] in ("primary", "tertial") else 1.0)
    trail = half * (1.06 if f["kind"] in ("primary", "tertial") else 1.0)

    # gentle bend of the shaft
    bend = (np.sin(u * math.pi) - 0.4) * (h * 0.06)
    cy = h * 0.5 + bend
    top = cy - lead
    bot = cy + trail

    ys = np.arange(h)[:, None]

    # signed position across the feather: -1 leading, +1 trailing
    d = np.zeros((h, w), float)
    rng = np.maximum(bot - top, 1e-6)
    d[:, :] = (ys - top[None, :]) / rng[None, :] * 2.0 - 1.0

    inside = (ys >= top[None, :] - 0.5) & (ys <= bot[None, :] + 0.5)

    # feather fringe: small splits along the trailing edge
    fringe = ((np.arange(w)[None, :] / 4.0) % 1.0) < 0.38
    inside = inside & ~(fringe & (d > 0.86))

    # bevel ramp across the feather (lit leading edge -> shadowed trailing edge)
    pos = np.array([r[0] for r in RAMP], float)
    cols = np.array([pal[r[1]] for r in RAMP], float)
    flat_d = d.ravel()
    col = np.stack([np.interp(flat_d, pos, cols[:, c]) for c in range(3)], axis=-1)
    col = col.reshape(h, w, 3)

    # lit ridge just inside the leading edge
    lead_hi = np.clip(1.0 - np.abs(d + 0.82) / 0.15, 0, 1)[:, :, None]
    col = col + (np.array(pal["white"], float) - col) * (0.70 * lead_hi)

    # length shading: roots sit under the covert layers, tips catch light
    len_k = (0.93 + 0.10 * np.clip((u - 0.12) / 0.88, 0, 1))[None, :, None]
    col = np.clip(col * len_k, 0, 255)

    # barb lines: shallow diagonals for feather texture
    barb = ((u[None, :] * w / 5.2 + np.abs(d) * 0.6) % 1.0) < 0.18
    barb &= (u[None, :] > 0.10) & (np.abs(d) < 0.92)
    col = col * np.where(barb, 0.93, 1.0)[:, :, None]

    # rachis
    rach = (np.abs(d) < 0.05) & (u[None, :] > 0.02) & (u[None, :] < 0.92)
    col = col + (np.array(pal["light"], float) - col) * 0.45 * rach[:, :, None]

    # iridescent sheen: cool pearl-lavender towards the tip and the trailing edge
    sh = np.array(pal["sheen"], float)
    sh2 = np.array(pal["sheen2"], float)
    tipk = np.clip((u[None, :] - 0.30) / 0.70, 0, 1) * np.clip((d + 0.25) / 1.25, 0, 1)
    col = col + (sh - col) * (0.40 * tipk)[:, :, None]
    edgek = np.clip((u[None, :] - 0.60) / 0.40, 0, 1) * np.clip((d - 0.62) / 0.38, 0, 1)
    col = col + (sh2 - col) * (0.26 * edgek)[:, :, None]

    # outline rim
    rim = inside & ~(_erode(inside, 1))
    col[rim] = pal["outline"]

    img = np.zeros((h, w, 4), np.uint8)
    img[:, :, :3] = np.clip(col, 0, 255).astype(np.uint8)
    img[:, :, 3] = np.where(inside, 255, 0).astype(np.uint8)
    img = Image.fromarray(img, "RGBA")
    if f.get("ornate"):
        img = _filigree(img, pal, f.get("gems", 1))
    return img


def _filigree(img, pal, gems=1):
    """Gold edge band + scrollwork + gem, drawn inside the feather's alpha."""
    w, h = img.size
    a = np.array(img)
    alpha = a[:, :, 3] > 0
    if not alpha.any():
        return img
    gold = pal["gold"]
    gold_l = pal["gold_light"]
    gold_d = pal["gold_dark"]
    top = np.argmax(alpha, axis=0)
    for x in range(w):
        y = int(top[x])
        if not alpha[y, x]:
            continue
        for k, colr in ((1, gold_l), (2, gold), (3, gold_d)):
            if y + k < h and alpha[y + k, x]:
                a[y + k, x, :3] = colr
    img = Image.fromarray(a, "RGBA")
    d = ImageDraw.Draw(img)

    # scroll curl in the body of the feather
    r = max(3, int(h * 0.20))
    cx = int(w * 0.42)
    cy = int(h * 0.52)
    d.arc([cx - r, cy - r, cx + r, cy + r], 200, 20, fill=gold_d + (255,), width=2)
    d.arc([cx - r + 1, cy - r + 1, cx + r - 1, cy + r - 1], 200, 20, fill=gold + (255,), width=1)
    d.arc([cx - r * 2, cy - r, cx + r * 2, cy + r], 200, 340, fill=gold_d + (255,), width=1)

    for i in range(gems):
        gx = int(w * (0.20 + 0.16 * i))
        gy = int(h * (0.46 + (0.10 if i % 2 else -0.06)))
        _gem(d, gx, gy, max(2, int(h * 0.14)), pal["gem1"] if i % 2 == 0 else pal["gem2"], pal)
    return img


def _gem(d, cx, cy, r, col, pal):
    r = max(2, r)
    d.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)],
              fill=col + (255,), outline=pal["outline"] + (255,))
    d.polygon([(cx, cy - r + 1), (cx + r - 2, cy), (cx, cy)], fill=pal["gold_light"] + (255,))



def _erode(mask, r):
    out = mask.copy()
    h, w = mask.shape
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx == 0 and dy == 0:
                continue
            if dx * dx + dy * dy > r * r:
                continue
            sh = np.zeros_like(mask)
            ys0, ys1 = max(0, dy), h + min(0, dy)
            xs0, xs1 = max(0, dx), w + min(0, dx)
            sh[ys0:ys1, xs0:xs1] = mask[max(0, -dy):h - max(0, dy),
                                        max(0, -dx):w - max(0, dx)]
            out &= sh
    return out


# â”€â”€ arm strip + clasp sprites â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
ARM_W = 5.0
ARM_PX_W = int(_ARM_LEN * SCALE)
ARM_PX_H = int(ARM_W * SCALE)


def arm_sprite(pal):
    """Ornate gold shoulder plate: tapered bar with filigree scrolls and gems."""
    w, h = ARM_PX_W, ARM_PX_H
    xs = np.arange(w)
    u = xs / max(w - 1, 1)
    taper = 1.0 - 0.62 * np.clip((u - 0.06) / 0.94, 0, 1)
    half = h * 0.5 * taper
    cy = h * 0.5 + np.sin(u * math.pi) * h * 0.06
    ys = np.arange(h)[:, None]
    inside = (ys >= cy - half[None, :]) & (ys <= cy + half[None, :])
    d = (ys - (cy - half)[None, :]) / np.maximum(2 * half[None, :], 1e-6) * 2 - 1

    gold = np.array(pal["gold"], float)
    gold_d = np.array(pal["gold_dark"], float)
    gold_l = np.array(pal["gold_light"], float)
    dark = np.array(pal["outline"], float)

    # metal bevel: bright polished gold with a soft ridge, dark only at the edges
    s = np.clip(1.0 - np.abs((d + 0.18) / 1.45) ** 2.2, 0, 1)
    col = gold[None, None, :] + (gold_l[None, None, :] - gold[None, None, :]) * (0.85 * s)[:, :, None]
    col = col + (gold_d - col) * np.clip((np.abs(d) - 0.55) / 0.45, 0, 1)[:, :, None] * 0.55
    # trailing shadow
    col = col * np.where(d > 0.35, 1.0 - 0.18 * np.clip((d - 0.35) / 0.65, 0, 1), 1.0)[:, :, None]
    # dark inner groove near the leading edge
    col[(np.abs(d + 0.80) < 0.05) & inside] = dark * 1.15

    rim = inside & ~(_erode(inside, 1))
    col[rim] = dark

    px = np.zeros((h, w, 4), np.uint8)
    px[:, :, :3] = np.clip(col, 0, 255).astype(np.uint8)
    px[:, :, 3] = np.where(inside, 255, 0).astype(np.uint8)
    img = Image.fromarray(px, "RGBA")

    draw = ImageDraw.Draw(img)
    # scrollwork: repeating curls along the plate
    step = max(10, int(2.6 * SCALE))
    i = 0
    for x in range(int(w * 0.10), int(w * 0.94), step):
        cyy = float(cy[min(x, w - 1)])
        r = step * 0.42
        up = i % 2 == 0
        box = [x - r, cyy - r * (0.9 if up else 0.5), x + r, cyy + r * (0.5 if up else 0.9)]
        draw.arc(box, 210 if up else 30, 330 if up else 150, fill=pal["outline"] + (255,), width=1)
        draw.arc([box[0] + 1, box[1] + 1, box[2] - 1, box[3] - 1],
                 210 if up else 30, 330 if up else 150, fill=pal["gold_light"] + (255,), width=1)
        i += 1

    # gems along the plate
    for k, frac in enumerate((0.16, 0.34, 0.56)):
        gx = int(w * frac)
        gy = int(cy[min(gx, w - 1)])
        _gem(draw, gx, gy, max(2, int(h * 0.11)),
             pal["gem1"] if k != 1 else pal["gem2"], pal)

    # rounded shoulder cap
    r = h * 0.5
    draw.ellipse([-r * 0.1, h * 0.5 - r, r * 1.2, h * 0.5 + r], fill=pal["gold_dark"] + (255,))
    draw.arc([-r * 0.1, h * 0.5 - r, r * 1.2, h * 0.5 + r], 90, 270, fill=pal["outline"] + (255,), width=1)
    return img



def clasp_sprite(pal, size_units=5.0):
    px = int(size_units * SCALE)
    img = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = px / 2
    # backing plate
    d.ellipse([1, 1, px - 2, px - 2], fill=pal["deep"] + (255,), outline=pal["outline"])
    d.ellipse([px * 0.12, px * 0.12, px * 0.88, px * 0.88], fill=pal["base"] + (255,))
    # diamond
    r = px * 0.34
    d.polygon([(c, c - r), (c + r, c), (c, c + r), (c - r, c)],
              fill=pal["gold"] + (255,), outline=pal["gold_dark"])
    r2 = r * 0.55
    d.polygon([(c, c - r2), (c + r2, c), (c, c + r2), (c - r2, c)],
              fill=pal["gold_light"] + (255,))
    d.point([(c, c - r2 * 0.4)], fill=(255, 255, 255, 255))
    return img


# â”€â”€ packing â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def pack(sizes, width=ATLAS_W):
    """Shelf packer -> list of (x, y) + atlas height."""
    pos = []
    x = y = PAD
    shelf = 0
    for w, h in sizes:
        if x + w + PAD > width:
            x = PAD
            y += shelf + PAD
            shelf = 0
        pos.append((x, y))
        x += w + PAD
        shelf = max(shelf, h)
    return pos, y + shelf + PAD


# â”€â”€ model â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def quad_from_feather(f, rect, atlas):
    a = math.radians(f["angle"])
    dx, dy = math.cos(a), math.sin(a)
    px, py = -dy, dx
    x0, y0 = f["root"]
    L, Wd = f["length"], f["width"]
    hw = Wd * 0.5
    z = f["z"]
    v = [
        (x0 - px * hw, y0 - py * hw, z),
        (x0 + dx * L - px * hw, y0 + dy * L - py * hw, z),
        (x0 + dx * L + px * hw, y0 + dy * L + py * hw, z),
        (x0 + px * hw, y0 + py * hw, z),
    ]
    u0, v0, u1, v1 = rect
    uv = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
    layer = "primaries" if f["kind"] in ("primary", "tertial") else "coverts"
    return dict(layer=layer, v=v, uv=uv)


def arm_quads(rect, atlas):
    quads = []
    u0, v0, u1, v1 = rect
    n_seg = len(ARM_PTS) - 1
    acc = 0.0
    for i in range(n_seg):
        ta = acc / _ARM_LEN
        acc += _ARM_SEG[i]
        tb = acc / _ARM_LEN
        a, b = ARM_PTS[i], ARM_PTS[i + 1]
        na, nb = arm_nrm(ta), arm_nrm(tb)
        wa = ARM_W * 0.5 * (1.0 - 0.62 * max(0.0, (ta - 0.06) / 0.94))
        wb = ARM_W * 0.5 * (1.0 - 0.62 * max(0.0, (tb - 0.06) / 0.94))
        z = 2.35
        v = [
            (a[0] - na[0] * wa, a[1] - na[1] * wa, z),
            (b[0] - nb[0] * wb, b[1] - nb[1] * wb, z),
            (b[0] + nb[0] * wb, b[1] + nb[1] * wb, z),
            (a[0] + na[0] * wa, a[1] + na[1] * wa, z),
        ]
        ua = u0 + (u1 - u0) * ta
        ub = u0 + (u1 - u0) * tb
        uv = [(ua, v0), (ub, v0), (ub, v1), (ua, v1)]
        quads.append(dict(layer="arm", v=v, uv=uv))
    return quads


def build(atlas_sizes):
    feats = layout()
    sizes = [sprite_size(f) for f in feats]
    sizes.append((ARM_PX_W, ARM_PX_H))
    sizes.append((int(5.0 * SCALE), int(5.0 * SCALE)))
    sizes.append((8, 8))                       # neutral patch for the preview proxy
    pos, height = pack(sizes)

    rects = []
    for (x, y), (w, h) in zip(pos, sizes):
        rects.append((x, y, x + w, y + h))

    quads = []
    for f, r in zip(feats, rects):
        quads.append(quad_from_feather(f, r, atlas_sizes))
    quads += arm_quads(rects[-2], atlas_sizes)

    # clasp at the shoulder, sits over the tuft
    cx, cy, cz = 2.2, 1.1, 2.52
    s = 2.6
    cr = rects[-3]
    quads.append(dict(layer="arm", v=[(cx - s, cy - s, cz), (cx + s, cy - s, cz),
                                      (cx + s, cy + s, cz), (cx - s, cy + s, cz)],
                      uv=[(cr[0], cr[1]), (cr[2], cr[1]),
                          (cr[2], cr[3]), (cr[0], cr[3])]))

    layers = [
        dict(name="primaries", pivot=[1.6, 0.4, 0.0], sway=1.1),
        dict(name="coverts", pivot=[1.6, 0.4, 1.6], sway=1.7),
        dict(name="arm", pivot=[1.6, 0.4, 2.8], sway=0.5),
    ]
    model = dict(textureSize=[ATLAS_W, height], layers=layers, quads=quads)
    gu = rects[-1]
    model["previewUv"] = [(gu[0] + 4) / ATLAS_W, (gu[1] + 4) / height]
    return feats, rects, model


def make_atlas(pal, feats, rects, height):
    atlas = Image.new("RGBA", (ATLAS_W, height), (0, 0, 0, 0))
    for f, r in zip(feats, rects):
        atlas.alpha_composite(feather_sprite(f, pal), (r[0], r[1]))
    atlas.alpha_composite(arm_sprite(pal), (rects[-2][0], rects[-2][1]))
    atlas.alpha_composite(clasp_sprite(pal), (rects[-3][0], rects[-3][1]))
    g = rects[-1]
    ImageDraw.Draw(atlas).rectangle([g[0], g[1], g[2] - 1, g[3] - 1], fill=(120, 122, 130, 255))
    return atlas


# â”€â”€ offline preview â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def to_tris(model, tex_w, tex_h):
    verts, uvs, faces = [], [], []
    for q in model["quads"]:
        base = len(verts)
        for (x, y, z), (u, vv) in zip(q["v"], q["uv"]):
            verts.append([x, -y, z])          # preview is Y-up
            uvs.append((u / tex_w, vv / tex_h))
        faces += [(base, base + 1, base + 2), (base, base + 2, base + 3)]
    return np.array(verts, float), np.array(faces, np.int64), np.array(uvs, float)


def proxy_scene(v, f, u, skin_uv):
    """Two wings on a blocky player (feet at y=0, shoulder z=+2.55)."""
    ROOT_X, ROOT_Y, ROOT_Z = 1.2, 13.6, 2.55
    raise_deg, sweep_deg = 16.0, 10.0

    def place(side):
        a = math.radians(raise_deg)
        c, s = math.cos(a), math.sin(a)
        out = []
        for p in v:
            x, y, z = p[0] * side, p[1], p[2]
            # rotate about Z around the root (raise the wing)
            xr = x * c - y * s
            yr = x * s + y * c
            # small Y sweep
            b = math.radians(sweep_deg * side)
            xr2 = xr * math.cos(b) + z * math.sin(b)
            zr2 = -xr * math.sin(b) + z * math.cos(b)
            out.append([xr2 + side * ROOT_X, yr + ROOT_Y, zr2 + ROOT_Z])
        return np.array(out)

    verts = [place(1), place(-1)]
    n = len(v)
    faces = [f, f + n]
    uvs = [u, u]
    allv = np.vstack(verts)
    allf = np.vstack(faces)
    allu = np.vstack(uvs)

    # player proxy
    skin_uv = skin_uv
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
                pv.append(corners[idx])
                pu.append(skin_uv)
            pf += [(base, base + 1, base + 2), (base, base + 2, base + 3)]
    allv = np.vstack([allv, np.array(pv, float)])
    allf = np.vstack([allf, np.array(pf, np.int64) + len(allv) - len(pv)])
    allu = np.vstack([allu, np.array(pu, float)])
    return allv, allf, allu


def item_icon(pal, size=16):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, (ang, ln, wd) in enumerate(((-58, 11.0, 2.6), (-30, 10.0, 2.4), (-4, 7.6, 2.0))):
        a = math.radians(ang)
        x0, y0 = 3.0, 13.0
        x1, y1 = x0 + math.cos(a) * ln, y0 + math.sin(a) * ln
        nx, ny = -math.sin(a) * wd, math.cos(a) * wd
        d.polygon([(x0, y0), (x1 + nx * 0.5, y1 + ny * 0.5), (x1, y1),
                   (x1 - nx * 0.5, y1 - ny * 0.5), (x0 - nx * 0.3, y0 - ny * 0.3)],
                  fill=pal["base"], outline=pal["outline"])
        d.line([(x0, y0), (x1, y1)], fill=pal["light"])
    d.line([(3, 13), (6, 10)], fill=pal["gold"], width=2)
    return img


def main():
    OUT.mkdir(exist_ok=True)
    feats, rects, model = build(None)
    tw, th = model["textureSize"]
    print(f"quads={len(model['quads'])} atlas={tw}x{th}")

    (OUT / "wing_v2.json").write_text(json.dumps(model), encoding="utf-8")
    (RES / "wingmodels").mkdir(parents=True, exist_ok=True)
    (RES / "wingmodels" / "wing.json").write_text(json.dumps(model), encoding="utf-8")

    for variant, pal in PALETTES.items():
        atlas = make_atlas(pal, feats, rects, th)
        (RES / "textures" / "wings").mkdir(parents=True, exist_ok=True)
        atlas.save(RES / "textures" / "wings" / f"{variant}.png")
        (RES / "textures" / "item").mkdir(parents=True, exist_ok=True)
        item_icon(pal).save(RES / "textures" / "item" / f"{variant}.png")
        if variant == "seraph_wings":
            atlas.save(OUT / "v2_atlas.png")

    # Blockbench payload (single mesh, per-face UV)
    v, f, u = to_tris(model, tw, th)
    bb = dict(atlas=[tw, th],
              vertices=[[float(p[0]), float(-p[1]), float(p[2])] for p in v],
              faces=[[int(a), int(b), int(c), int(d)] for a, b, c, d in
                     [tuple(range(i, i + 4)) for i in range(0, len(v), 4)]],
              uvs=[[[float(c[0]), float(c[1])] for c in qq["uv"]] for qq in model["quads"]])
    (OUT / "bb_payload.json").write_text(json.dumps(bb), encoding="utf-8")

    # sheet: wing pair on proxy, several angles
    sv, sf, su = proxy_scene(v, f, u, tuple(model["previewUv"]))
    tex = np.asarray(Image.open(RES / "textures" / "wings" / "seraph_wings.png").convert("RGBA"), float)
    size = 380
    views = [("back", np.eye(3)), ("3/4", rm.rot_y(-32) @ rm.rot_x(-6)),
             ("side", rm.rot_y(-72)), ("low 3/4", rm.rot_y(28) @ rm.rot_x(14))]
    sheet = Image.new("RGB", (size * 2, (size + 22) * 2), (16, 17, 20))
    dr = ImageDraw.Draw(sheet)
    for i, (label, R) in enumerate(views):
        img = rm.render_view(sv, sf, su, tex, R, size)
        x, y = (i % 2) * size, (i // 2) * (size + 22)
        sheet.paste(Image.fromarray(img), (x, y + 22))
        dr.text((x + 8, y + 5), label, fill=(240, 235, 215))
    sheet.save(OUT / "v2_preview.png")

    # variants sheet (wing alone, from behind)
    wv, wf, wu = to_tris(model, tw, th)
    sheet = Image.new("RGB", (size * 2, (size + 22) * 2), (16, 17, 20))
    dr = ImageDraw.Draw(sheet)
    for i, variant in enumerate(PALETTES):
        t2 = np.asarray(Image.open(RES / "textures" / "wings" / f"{variant}.png").convert("RGBA"), float)
        img = rm.render_view(wv, wf, wu, t2, np.eye(3), size)
        x, y = (i % 2) * size, (i // 2) * (size + 22)
        sheet.paste(Image.fromarray(img), (x, y + 22))
        dr.text((x + 8, y + 5), variant, fill=(240, 235, 215))
    sheet.save(OUT / "v2_variants.png")
    print("saved previews")


if __name__ == "__main__":
    main()
