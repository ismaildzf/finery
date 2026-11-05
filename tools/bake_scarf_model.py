"""Bake the owner's pro scarf cubes into neck-local quads.

Coordinates: Blockbench player space (y 24 = neck) -> neck space y' = 24 - y,
which is the body part space the neck renderer uses (origin on the neck line,
+y downward). Group rotations are baked; face UVs follow the script (each face
uses the cube's whole rect, tail fringe caps use the transparent 1x1 corner,
and left/right caps are rotated 90 degrees).
"""

import json
import math
import os

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "src", "main", "resources", "assets", "finery", "neckmodels", "scarf.json")

# name, from, to, uv(u,v,w,h), group chain, fringe, rotate_caps
CUBES = [
    ("collar_low_front", (-4.65, 22.3, -3.15), (4.65, 24.25, -2.05), (10, 10, 160, 56), ["lowerRoll"], False, False),
    ("collar_low_back", (-4.65, 22.5, 2.05), (4.65, 24.35, 3.05), (170, 10, 160, 56), ["lowerRoll"], False, False),
    ("collar_low_left", (3.65, 22.4, -3.10), (4.70, 24.30, 3.00), (50, 10, 140, 56), ["lowerRoll"], False, True),
    ("collar_low_right", (-4.70, 22.4, -3.10), (-3.65, 24.30, 3.00), (50, 10, 140, 56), ["lowerRoll"], False, True),
    ("collar_up_front", (-4.45, 23.55, -2.95), (4.45, 25.25, -1.95), (10, 80, 160, 48), ["upperRoll"], False, False),
    ("collar_up_back", (-4.45, 23.65, 1.95), (4.45, 25.30, 2.85), (170, 80, 160, 48), ["upperRoll"], False, False),
    ("collar_up_left", (3.55, 23.60, -2.90), (4.50, 25.28, 2.80), (50, 80, 140, 48), ["upperRoll"], False, True),
    ("collar_up_right", (-4.50, 23.60, -2.90), (-3.55, 25.28, 2.80), (50, 80, 140, 48), ["upperRoll"], False, True),
    ("knot_main_fold", (-3.1, 21.8, -3.55), (-0.1, 24.4, -2.45), (10, 145, 120, 64), ["frontKnot"], False, False),
    ("knot_side_tuck", (-2.8, 22.1, -3.45), (0.2, 23.9, -2.55), (10, 145, 120, 64), ["frontKnot"], False, False),
    ("tl_seg1", (-3.15, 18.6, -3.42), (-0.55, 22.4, -2.85), (160, 145, 96, 75), ["tailLong1"], False, False),
    ("tl_seg2", (-3.20, 15.0, -3.40), (-0.50, 18.7, -2.88), (160, 220, 96, 75), ["tailLong1", "tailLong2"], False, False),
    ("tl_seg3_tassels", (-3.22, 11.5, -3.38), (-0.48, 15.1, -2.92), (160, 295, 96, 70), ["tailLong1", "tailLong2", "tailLong3"], True, False),
    ("ts_seg1", (-1.75, 18.5, -3.02), (0.65, 22.3, -2.50), (280, 145, 88, 90), ["tailShort1"], False, False),
    ("ts_seg2_tassels", (-1.78, 14.8, -2.98), (0.68, 18.6, -2.54), (280, 235, 88, 90), ["tailShort1", "tailShort2"], True, False),
]

GROUPS = {
    "lowerRoll": ((0, 23.3, 0), (4.5, 0, -1.5)),
    "upperRoll": ((0, 24.4, 0), (2.0, 0, 2.0)),
    "frontKnot": ((-1.6, 23.0, -3.1), (3, 6, -4)),
    "tailLong1": ((-1.85, 22.2, -3.25), (-3.5, 4, 2.5)),
    "tailLong2": ((-1.85, 18.6, -3.15), (2.5, -2, -2.0)),
    "tailLong3": ((-1.85, 15.0, -3.15), (2.0, 0, -1.5)),
    "tailShort1": ((-0.55, 22.2, -2.85), (-2.0, -6, -7.5)),
    "tailShort2": ((-0.55, 18.5, -2.75), (2.0, 2, 3.5)),
}


def rot_matrix(rx, ry, rz):
    rx, ry, rz = (math.radians(a) for a in (rx, ry, rz))
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    mx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    my = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    mz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return mz @ my @ mx


def group_matrix(path):
    m = np.eye(4)
    for name in path:
        (ox, oy, oz), (rx, ry, rz) = GROUPS[name]
        t = np.eye(4)
        t[:3, 3] = (ox, oy, oz)
        ti = np.eye(4)
        ti[:3, 3] = (-ox, -oy, -oz)
        r = np.eye(4)
        r[:3, :3] = rot_matrix(rx, ry, rz)
        m = m @ t @ r @ ti
    return m


def conv(p):
    return [p[0], 24.0 - p[1], p[2]]


FACES = {
    "down": [0, 1, 2, 3],
    "up": [4, 5, 6, 7],
    "north": [0, 1, 5, 4],
    "south": [3, 2, 6, 7],
    "west": [0, 3, 7, 4],
    "east": [1, 2, 6, 5],
}


def main():
    quads = []
    for (name, frm, to, uv, path, fringe, rotate_caps) in CUBES:
        m = group_matrix(path)
        x0, y0, z0 = frm
        x1, y1, z1 = to
        corners = [
            (x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1),
            (x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1),
        ]
        pts = []
        for c in corners:
            v = np.array([c[0], c[1], c[2], 1.0])
            w = m @ v
            pts.append(conv((w[0], w[1], w[2])))

        u, v0, uw, uh = uv
        u1, v1 = u + uw, v0 + uh
        rect = [(u, v0), (u1, v0), (u1, v1), (u, v1)]
        rect_rot = [(u, v1), (u, v0), (u1, v0), (u1, v1)]

        for face, idx in FACES.items():
            if fringe and face in ("up", "down"):
                face_uv = [(0, 0), (1, 0), (1, 1), (0, 1)]
            elif rotate_caps and face in ("up", "down"):
                face_uv = rect_rot
            else:
                face_uv = rect
            quads.append({
                "v": [pts[i] for i in idx],
                "uv": [list(p) for p in face_uv],
            })

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump({"textureSize": [512, 512], "quads": quads}, fh, separators=(",", ":"))
    ys = [v[1] for q in quads for v in q["v"]]
    zs = [v[2] for q in quads for v in q["v"]]
    print("quads", len(quads), "y", round(min(ys), 2), round(max(ys), 2), "z", round(min(zs), 2), round(max(zs), 2))


if __name__ == "__main__":
    main()
