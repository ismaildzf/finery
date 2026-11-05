"""Radical redesign of the crown, wizard hat and eye patch (v2).

Follows publishing/bb/DESIGN_PROMPT.md. Writes publishing/bb/*.bbmodel plus
three-quarter previews rendered with a painter's algorithm.
"""

import base64
import io
import json
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "publishing", "bb")

CELLS = {
    "gold_l": (0, 0), "gold_m": (1, 0), "gold_d": (2, 0), "ruby": (3, 0),
    "pearl": (4, 0), "velvet": (5, 0), "purple_l": (6, 0), "purple_m": (7, 0),
    "purple_d": (0, 1), "lea_l": (1, 1), "lea_m": (2, 1), "lea_d": (3, 1),
    "stitch": (4, 1), "silver": (5, 1),
}
BASE = {
    "gold_l": (248, 212, 118), "gold_m": (206, 156, 54), "gold_d": (146, 98, 28),
    "ruby": (176, 30, 40), "pearl": (220, 227, 234), "velvet": (110, 18, 32),
    "purple_l": (95, 68, 120), "purple_m": (74, 53, 96), "purple_d": (55, 39, 69),
    "lea_l": (122, 91, 70), "lea_m": (94, 68, 54), "lea_d": (58, 42, 34),
    "stitch": (201, 168, 106), "silver": (185, 192, 200),
}
FAMILY = {
    "gold": ("gold_l", "gold_m", "gold_d"),
    "purple": ("purple_l", "purple_m", "purple_d"),
    "leather": ("lea_l", "lea_m", "lea_d"),
}


def texture():
    rng = random.Random(11)
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    px = img.load()
    for name, (cx, cy) in CELLS.items():
        r, g, b = BASE[name]
        for y in range(8):
            for x in range(8):
                n = rng.randint(-7, 7)
                px[cx * 8 + x, cy * 8 + y] = (
                    max(0, min(255, r + n)), max(0, min(255, g + n)),
                    max(0, min(255, b + n)), 255)
    return img


def uv(name):
    cx, cy = CELLS[name]
    return [cx * 8, cy * 8, cx * 8 + 8, cy * 8 + 8]


def cube(name, frm, to, mat, origin=(0, 28, 0), rot=None):
    if mat in FAMILY:
        top, side, bottom = FAMILY[mat]
    else:
        top = side = bottom = mat
    return {
        "name": name, "box_uv": False, "render_order": "default", "locked": False,
        "export": True, "scope": 0, "allow_mirror_modeling": True,
        "from": list(frm), "to": list(to), "autouv": 0, "color": 0,
        "origin": list(origin), "rotation": list(rot or (0, 0, 0)),
        "faces": {f: {"uv": uv(top if f == "up" else bottom if f == "down" else side),
                      "texture": 0}
                  for f in ("north", "east", "south", "west", "up", "down")},
        "uuid": name,
    }


def write_project(name, elements):
    tex = texture()
    buf = io.BytesIO()
    tex.save(buf, format="PNG")
    data = {
        "meta": {"format_version": "4.0", "model_format": "free", "box_uv": False},
        "name": name, "model_identifier": "", "visible_box": [1, 1, 0],
        "variable_placeholders": "", "multi_file_ruleset": False,
        "variable_placeholder_buttons": [], "bedrock_animation_mode": "entity",
        "timeline_setups": [], "unhandled_root_fields": {},
        "resolution": {"width": 64, "height": 64},
        "textures": [{"path": "", "name": name + ".png", "folder": "blockbench",
                      "namespace": "", "id": "0", "particle": False,
                      "width": 64, "height": 64,
                      "source": "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()}],
        "elements": elements, "groups": [],
        "outliner": [{"uuid": e["uuid"], "isOpen": True} for e in elements],
    }
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name + ".bbmodel"), "w", encoding="utf-8") as fh:
        json.dump(data, fh, separators=(",", ":"))
    render_preview(name, elements, tex, 32, '_preview')
    render_preview(name, elements, tex, 0, '_front')
    print("wrote", name, len(elements), "cubes")


def rot_y(p, ang):
    ca, sa = math.cos(ang), math.sin(ang)
    return (p[0] * ca - p[2] * sa, p[1], p[0] * sa + p[2] * ca)


def render_preview(name, elements, tex, ang_deg=32, suffix='_preview'):
    scale = 15
    W = H = 460
    ang = math.radians(ang_deg)
    ca, sa = math.cos(ang), math.sin(ang)
    img = np.zeros((H, W, 3), dtype=np.float32)
    zbuf = np.full((H, W), 1e9, dtype=np.float32)
    T = np.asarray(tex).astype(np.float32)
    light = np.array([-0.4, -0.62, -0.67])
    light /= np.linalg.norm(light)

    xs = [v for e in elements for v in (e["from"][0], e["to"][0])] + [-4.0, 4.0]
    ys = [v for e in elements for v in (e["from"][1], e["to"][1])] + [24.0, 32.0]
    zs = [v for e in elements for v in (e["from"][2], e["to"][2])] + [-4.0, 4.0]
    cx = (min(xs) + max(xs)) / 2.0
    cy = (min(ys) + max(ys)) / 2.0
    cz = (min(zs) + max(zs)) / 2.0

    faces = {"down": [0, 1, 2, 3], "up": [4, 7, 6, 5], "north": [4, 5, 1, 0],
             "south": [3, 2, 6, 7], "west": [0, 3, 7, 4], "east": [1, 5, 6, 2]}
    head = {"from": [-4.0, 24.0, -4.0], "to": [4.0, 32.0, 4.0],
            "faces": {f: {"uv": [0, 0, 0, 0]} for f in faces}}

    def ry(p):
        return (p[0] * ca - p[2] * sa, p[1], p[0] * sa + p[2] * ca)

    for e in [head] + list(elements):
        x0, y0, z0 = [e["from"][i] - (cx, cy, cz)[i] for i in range(3)]
        x1, y1, z1 = [e["to"][i] - (cx, cy, cz)[i] for i in range(3)]
        c = [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1),
             (x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)]
        for fname, idx in faces.items():
            pts = [c[i] for i in idx]
            ax, ay, az = pts[1][0] - pts[0][0], pts[1][1] - pts[0][1], pts[1][2] - pts[0][2]
            bx, by, bz = pts[2][0] - pts[0][0], pts[2][1] - pts[0][1], pts[2][2] - pts[0][2]
            n = np.array([ay * bz - az * by, az * bx - ax * bz, ax * by - ay * bx], dtype=float)
            ln = np.linalg.norm(n)
            if ln < 1e-9:
                continue
            n /= ln
            if ry((n[0], n[1], n[2]))[2] > -0.02:
                continue
            shade = 0.55 + 0.45 * max(0.0, -float(np.dot(n, light)))
            u = e["faces"][fname]["uv"]
            col = (T[u[1] + 4, u[0] + 4, :3] if u[2] > u[0]
                   else np.array([150, 128, 110], dtype=np.float32)) * shade
            vp = [ry(p) for p in pts]
            sp = [(W / 2 + q[0] * scale, H / 2 - q[1] * scale) for q in vp]
            for tri in ((0, 1, 2), (0, 2, 3)):
                s3 = [sp[i] for i in tri]
                z3 = [vp[i][2] for i in tri]
                minx = max(0, int(min(q[0] for q in s3)))
                maxx = min(W - 1, int(max(q[0] for q in s3)) + 1)
                miny = max(0, int(min(q[1] for q in s3)))
                maxy = min(H - 1, int(max(q[1] for q in s3)) + 1)
                if minx > maxx or miny > maxy:
                    continue
                ex = [s3[1][0] - s3[0][0], s3[2][0] - s3[0][0]]
                ey = [s3[1][1] - s3[0][1], s3[2][1] - s3[0][1]]
                den = ex[0] * ey[1] - ex[1] * ey[0]
                if abs(den) < 1e-9:
                    continue
                for py in range(miny, maxy + 1):
                    for px in range(minx, maxx + 1):
                        wx, wy = px + 0.5 - s3[0][0], py + 0.5 - s3[0][1]
                        b1 = (wx * ey[1] - wy * ex[1]) / den
                        b2 = (ex[0] * wy - ey[0] * wx) / den
                        b0 = 1 - b1 - b2
                        if b0 < -0.01 or b1 < -0.01 or b2 < -0.01:
                            continue
                        z = b0 * z3[0] + b1 * z3[1] + b2 * z3[2]
                        if z > zbuf[py, px]:
                            continue
                        zbuf[py, px] = z
                        img[py, px] = col
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB").save(
        os.path.join(OUT, name + suffix + ".png"))


def crown():
    e = []
    outer, inner = 4.32, 3.98
    for tag, a, b in (("front", (-outer, 30.55, -outer), (outer, 31.75, -inner)),
                      ("back", (-outer, 30.55, inner), (outer, 31.75, outer)),
                      ("left", (inner, 30.55, -outer), (outer, 31.75, outer)),
                      ("right", (-outer, 30.55, -outer), (-inner, 31.75, outer))):
        e.append(cube("band_" + tag, a, b, "gold", (0, 30.55, 0)))
    for tag, a, b in (("front", (-4.4, 31.7, -4.4), (4.4, 31.9, -3.9)),
                      ("back", (-4.4, 31.7, 3.9), (4.4, 31.9, 4.4)),
                      ("left", (3.9, 31.7, -4.4), (4.4, 31.9, 4.4)),
                      ("right", (-4.4, 31.7, -4.4), (-3.9, 31.9, 4.4))):
        e.append(cube("rim_" + tag, a, b, "gold_l", (0, 31.75, 0)))
    # central ruby, set into the band
    e.append(cube("gem", (-0.55, 30.65, -4.37), (0.55, 31.62, -4.3), "ruby"))
    e.append(cube("gem_frame_l", (-0.78, 30.55, -4.35), (-0.55, 31.72, -4.3), "gold_l"))
    e.append(cube("gem_frame_r", (0.55, 30.55, -4.35), (0.78, 31.72, -4.3), "gold_l"))
    # five slender spikes around the front half
    spikes = ((0.0, -4.05, 3.1, 0.55), (-2.05, -3.95, 2.4, 0.45), (2.05, -3.95, 2.4, 0.45),
              (-3.45, -1.1, 1.7, 0.4), (3.45, -1.1, 1.7, 0.4))
    for i, (px, pz, h, w) in enumerate(spikes):
        e.append(cube("base_%d" % i, (px - w, 31.85, pz - 0.26), (px + w, 32.15, pz + 0.26), "gold_l"))
        e.append(cube("spike_%d" % i, (px - w * 0.72, 32.15, pz - 0.2), (px + w * 0.72, 32.15 + h * 0.72, pz + 0.2), "gold"))
        e.append(cube("tip_%d" % i, (px - w * 0.38, 32.15 + h * 0.72, pz - 0.16), (px + w * 0.38, 32.15 + h, pz + 0.16), "gold_l"))
        e.append(cube("orb_%d" % i, (px - 0.24, 32.15 + h, pz - 0.24), (px + 0.24, 32.15 + h + 0.42, pz + 0.24), "pearl"))
    write_project("crown", e)


def wizard_hat():
    tilt = (4, 0, 0)
    e = [
        cube("brim", (-5.4, 31.5, -5.4), (5.4, 32.05, 5.4), "purple", (0, 32, 0), tilt),
        cube("brim_lip", (-5.85, 31.2, -5.85), (5.85, 31.55, 5.85), "purple", (0, 32, 0), tilt),
    ]
    segs = ((4.0, 32.05, 34.4, 0.0), (3.35, 34.4, 36.5, 0.3), (2.7, 36.5, 38.4, 0.65),
            (2.05, 38.4, 40.1, 1.0), (1.45, 40.1, 41.6, 1.35), (1.0, 41.6, 42.8, 1.7))
    for i, (w, y0, y1, dz) in enumerate(segs):
        e.append(cube("cone_%d" % i, (-w, y0, -w + dz), (w, y1, w + dz), "purple", (0, 32, 0)))
    e.append(cube("tip", (-0.4, 42.8, 1.2), (0.4, 43.9, 2.2), "purple_d", (0, 42.8, 1.6), (12, 0, 0)))
    for tag, a, b in (("front", (-4.06, 32.1, -4.06), (4.06, 33.05, -3.78)),
                      ("back", (-4.06, 32.1, 3.78), (4.06, 33.05, 4.06)),
                      ("left", (3.78, 32.1, -4.06), (4.06, 33.05, 4.06)),
                      ("right", (-4.06, 32.1, -4.06), (-3.78, 33.05, 4.06))):
        e.append(cube("band_" + tag, a, b, "gold"))
    e.append(cube("buckle", (-1.1, 32.15, -4.3), (1.1, 33.0, -4.0), "gold_l"))
    e.append(cube("gem", (-0.3, 32.4, -4.34), (0.3, 32.8, -4.28), "ruby"))
    e.append(cube("star", (-0.6, 33.35, -4.1), (0.6, 34.55, -3.96), "gold_l"))
    write_project("wizard_hat", e)


def eye_patch():
    pv = (-2.6, 27.1, -4.2)
    sv = (0, 27.1, 0)
    e = [
        cube("patch_rim", (-4.45, 25.45, -4.38), (-0.7, 28.55, -4.12), "lea_d", pv, (0, 0, 4)),
        cube("patch_face", (-4.24, 25.7, -4.52), (-0.92, 28.3, -4.34), "leather", pv, (0, 0, 4)),
        cube("patch_stitch_l", (-4.33, 25.75, -4.49), (-4.13, 28.25, -4.42), "stitch", pv, (0, 0, 4)),
        cube("patch_stitch_r", (-1.03, 25.75, -4.49), (-0.83, 28.25, -4.42), "stitch", pv, (0, 0, 4)),
        cube("patch_stitch_t", (-4.13, 28.05, -4.49), (-1.03, 28.25, -4.42), "stitch", pv, (0, 0, 4)),
        cube("patch_stitch_b", (-4.13, 25.75, -4.49), (-1.03, 25.95, -4.42), "stitch", pv, (0, 0, 4)),
        cube("strap_front", (-4.22, 26.5, -4.26), (-0.95, 27.7, -3.92), "lea_d", sv, (0, 0, 3)),
        cube("strap_left", (3.92, 26.5, -4.26), (4.24, 27.7, 4.24), "lea_d", sv, (0, 0, 3)),
        cube("strap_right", (-4.24, 26.5, -4.26), (-3.92, 27.7, 4.24), "lea_d", sv, (0, 0, 3)),
        cube("strap_back", (-4.22, 26.5, 3.92), (4.22, 27.7, 4.24), "lea_d", sv, (0, 0, 3)),
        cube("buckle", (2.25, 26.3, 4.0), (3.25, 27.45, 4.34), "silver"),
        cube("knot", (1.95, 26.2, 3.98), (2.85, 27.75, 4.5), "leather"),
        cube("tail_a", (2.05, 24.6, 4.1), (2.45, 26.4, 4.42), "lea_m"),
        cube("tail_b", (2.5, 25.0, 4.1), (2.9, 26.4, 4.42), "leather"),
    ]
    write_project("eye_patch", e)


if __name__ == "__main__":
    crown()
    wizard_hat()
    eye_patch()
