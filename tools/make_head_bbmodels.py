"""Build three improved head cosmetics as Blockbench projects for review.

Writes publishing/bb/{crown,wizard_hat,eye_patch}.bbmodel (Generic Model, 64x64
embedded texture) plus preview renders. Nothing is imported into the mod yet.
"""

import base64
import io
import json
import math
import os
import random

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "publishing", "bb")

CELLS = {
    "gold_l": (0, 0), "gold_m": (1, 0), "gold_d": (2, 0),
    "lea_d": (3, 0), "lea_m": (4, 0), "velvet": (5, 0),
    "blue": (6, 0), "silver": (7, 0), "red": (0, 1), "green": (1, 1),
}
BASE = {
    "gold_l": (248, 212, 118), "gold_m": (206, 156, 54), "gold_d": (146, 98, 28),
    "lea_d": (52, 38, 32), "lea_m": (88, 66, 52), "velvet": (112, 18, 32),
    "blue": (44, 74, 168), "silver": (206, 212, 222), "red": (176, 30, 40),
    "green": (40, 132, 72),
}


def texture():
    rng = random.Random(4)
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    px = img.load()
    for name, (cx, cy) in CELLS.items():
        r, g, b = BASE[name]
        for y in range(8):
            for x in range(8):
                n = rng.randint(-10, 10)
                px[cx * 8 + x, cy * 8 + y] = (
                    max(0, min(255, r + n)), max(0, min(255, g + n)),
                    max(0, min(255, b + n)), 255)
    return img


def uv(name):
    cx, cy = CELLS[name]
    return [cx * 8, cy * 8, cx * 8 + 8, cy * 8 + 8]


def cube(name, frm, to, mat, origin=(0, 28, 0), rot=None):
    top = "gold_l" if mat == "gold_m" else mat
    bottom = "gold_d" if mat == "gold_m" else mat
    return {
        "name": name, "box_uv": False, "render_order": "default", "locked": False,
        "export": True, "scope": 0, "allow_mirror_modeling": True,
        "from": list(frm), "to": list(to), "autouv": 0, "color": 0,
        "origin": list(origin), "rotation": list(rot or (0, 0, 0)),
        "faces": {f: {"uv": uv(top if f == "up" else bottom if f == "down" else mat),
                      "texture": 0}
                  for f in ("north", "east", "south", "west", "up", "down")},
        "uuid": name,
    }


def project(name, elements, view):
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
    render_preview(name, elements, tex, view)
    print("wrote", name)


def render_preview(name, elements, tex, view):
    scale = 15
    W = H = 460
    img = np.zeros((H, W, 3), dtype=np.float32)
    depth = np.full((H, W), 1e9, dtype=np.float32)
    light = np.array([-0.45, -0.6, -0.66])
    light /= np.linalg.norm(light)
    T = np.asarray(tex).astype(np.float32)
    ang = math.radians(35)
    ca, sa = math.cos(ang), math.sin(ang)

    def proj(p):
        return p[0] * ca - p[2] * sa, p[1], p[0] * sa + p[2] * ca

    xs = [v for e in elements for v in (e["from"][0], e["to"][0], -4.0, 4.0)]
    ys = [v for e in elements for v in (e["from"][1], e["to"][1], 24.0, 32.0)]
    zs = [v for e in elements for v in (e["from"][2], e["to"][2], -4.0, 4.0)]
    cx = (min(xs) + max(xs)) / 2.0
    cy = (min(ys) + max(ys)) / 2.0
    cz = (min(zs) + max(zs)) / 2.0

    faces = {"down": [3, 2, 1, 0], "up": [7, 6, 5, 4], "north": [4, 5, 1, 0],
             "south": [7, 6, 2, 3], "west": [4, 7, 3, 0], "east": [5, 6, 2, 1]}
    head = {"from": [-4.0, 24.0, -4.0], "to": [4.0, 32.0, 4.0],
            "faces": {f: {"uv": [0, 0, 0, 0]} for f in faces}}

    for e in list(elements) + [head]:
        a0 = [e["from"][i] - (cx, cy, cz)[i] for i in range(3)]
        a1 = [e["to"][i] - (cx, cy, cz)[i] for i in range(3)]
        x0, y0, z0 = a0
        x1, y1, z1 = a1
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
            vp = [proj(p) for p in pts]
            vn = proj((n[0], n[1], n[2]))
            if vn[2] > -0.02:
                continue
            shade = 0.55 + 0.45 * max(0.0, -float(np.dot(n, light)))
            u = e["faces"][fname]["uv"]
            if u[2] > u[0]:
                col = T[u[1] + 4, u[0] + 4, :3] * shade
            else:
                col = np.array([150, 128, 110], dtype=np.float32) * shade
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
                        if z > depth[py, px]:
                            continue
                        depth[py, px] = z
                        img[py, px] = col
    panel = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")
    panel.save(os.path.join(OUT, name + "_" + view + ".png"))


def crown():
    els = []
    outer, inner = 4.28, 3.78
    walls = (("front", (-outer, 29.6, -outer), (outer, 32.1, -inner)),
             ("back", (-outer, 29.6, inner), (outer, 32.1, outer)),
             ("left", (inner, 29.6, -outer), (outer, 32.1, outer)),
             ("right", (-outer, 29.6, -outer), (-inner, 32.1, outer)))
    for side, a, b in walls:
        els.append(cube("band_" + side, a, b, "gold_m", (0, 29.6, 0)))
    rims = (("front", (-4.42, 32.0, -4.42), (4.42, 32.35, -3.72)),
            ("back", (-4.42, 32.0, 3.72), (4.42, 32.35, 4.42)),
            ("left", (3.72, 32.0, -4.42), (4.42, 32.35, 4.42)),
            ("right", (-4.42, 32.0, -4.42), (-3.72, 32.35, 4.42)))
    for side, a, b in rims:
        els.append(cube("rim_" + side, a, b, "gold_l", (0, 32, 0)))
    for (px, pz, tag) in ((0, -3.9, "front"), (-2.9, -3.9, "fl"), (2.9, -3.9, "fr"),
                          (-3.0, 3.9, "bl"), (3.0, 3.9, "br")):
        w = 1.05 if tag == "front" else 0.85
        h = 3.4 if tag == "front" else 2.7
        els.append(cube("point_" + tag, (px - w, 32.3, pz - 0.42),
                        (px + w, 32.3 + h * 0.55, pz + 0.42), "gold_m"))
        els.append(cube("point_tip_" + tag, (px - w * 0.55, 32.3 + h * 0.55, pz - 0.34),
                        (px + w * 0.55, 32.3 + h, pz + 0.34), "gold_l"))
        els.append(cube("pearl_" + tag, (px - 0.32, 32.3 + h, pz - 0.32),
                        (px + 0.32, 32.3 + h + 0.55, pz + 0.32), "silver"))
    els.append(cube("jewel_red", (-0.45, 30.4, -4.36), (0.45, 31.3, -4.26), "red"))
    els.append(cube("jewel_blue_l", (-2.4, 30.5, -4.36), (-1.7, 31.2, -4.26), "blue"))
    els.append(cube("jewel_blue_r", (1.7, 30.5, -4.36), (2.4, 31.2, -4.26), "blue"))
    inlays = (("front", (-3.72, 30.0, -3.72), (3.72, 31.9, -3.55)),
              ("back", (-3.72, 30.0, 3.55), (3.72, 31.9, 3.72)),
              ("left", (3.55, 30.0, -3.72), (3.72, 31.9, 3.72)),
              ("right", (-3.72, 30.0, -3.72), (-3.55, 31.9, 3.72)))
    for side, a, b in inlays:
        els.append(cube("inlay_" + side, a, b, "velvet"))
    project("crown", els, "threequarter")


def wizard_hat():
    els = [
        cube("brim", (-5.0, 31.5, -5.0), (5.0, 32.45, 5.0), "lea_m", (0, 32, 0)),
        cube("brim_lip", (-5.35, 31.2, -5.35), (5.35, 31.5, 5.35), "lea_d", (0, 32, 0)),
        cube("cone1", (-4.0, 32.45, -4.0), (4.0, 35.3, 4.0), "lea_m", (0, 32, 0)),
        cube("cone2", (-3.2, 35.3, -3.4), (3.2, 37.9, 3.0), "lea_m", (0, 32, 0)),
        cube("cone3", (-2.4, 37.9, -2.9), (2.4, 40.1, 2.0), "lea_m", (0, 32, 0)),
        cube("cone4", (-1.7, 40.1, -2.5), (1.7, 42.1, 0.9), "lea_m", (0, 32, 0)),
        cube("tip", (-0.85, 42.1, -2.3), (0.85, 43.5, -0.3), "lea_d", (0, 42.1, 0), (0.16, 0, 0.1)),
    ]
    bands = (("front", (-4.06, 32.45, -4.06), (4.06, 33.4, -3.62)),
             ("back", (-4.06, 32.45, 3.62), (4.06, 33.4, 4.06)),
             ("left", (3.62, 32.45, -4.06), (4.06, 33.4, 4.06)),
             ("right", (-4.06, 32.45, -4.06), (-3.62, 33.4, 4.06)))
    for side, a, b in bands:
        els.append(cube("band_" + side, a, b, "gold_m"))
    els.append(cube("buckle", (-1.1, 32.55, -4.34), (1.1, 33.45, -3.95), "gold_l"))
    els.append(cube("buckle_gem", (-0.35, 32.8, -4.38), (0.35, 33.2, -4.3), "red"))
    els.append(cube("star", (-0.55, 33.6, -4.12), (0.55, 34.7, -3.95), "gold_l"))
    project("wizard_hat", els, "threequarter")


def eye_patch():
    els = [
        cube("patch_base", (-4.42, 27.05, -4.5), (-0.8, 30.15, -4.18), "lea_d"),
        cube("patch_face", (-4.3, 27.2, -4.54), (-0.92, 30.0, -4.2), "lea_m"),
        cube("strap_front", (-4.2, 28.15, -4.22), (-1.0, 29.25, -3.94), "lea_d"),
        cube("strap_left", (3.95, 28.15, -4.22), (4.25, 29.25, 4.22), "lea_d"),
        cube("strap_right", (-4.25, 28.15, -4.22), (-3.95, 29.25, 4.22), "lea_d"),
        cube("strap_back", (-4.2, 28.15, 3.94), (4.2, 29.25, 4.22), "lea_d"),
        cube("knot", (2.0, 27.85, 4.0), (2.85, 29.5, 4.55), "lea_m"),
        cube("knot_tail", (2.2, 26.2, 4.12), (2.62, 28.0, 4.45), "lea_m"),
    ]
    project("eye_patch", els, "threequarter")


if __name__ == "__main__":
    crown()
    wizard_hat()
    eye_patch()
