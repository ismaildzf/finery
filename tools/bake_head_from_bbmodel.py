"""Bake the redesigned wizard hat and eye patch from Blockbench into head models.

Reads publishing/bb/{wizard_hat,eye_patch}.bbmodel (Generic Model, 64x64 texture),
applies the element transforms, mirrors X and Y for Minecraft's entity space
(x' = -x, y' = 24 - y) and writes a static baked model + texture per item.
"""

import base64
import json
import math
import os

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "publishing", "bb")
MODELS = os.path.join(ROOT, "src", "main", "resources", "assets", "finery", "headmodels")
TEX = os.path.join(ROOT, "src", "main", "resources", "assets", "finery", "textures", "head", "baked")

FACES = {
    "down": [0, 1, 2, 3], "up": [4, 7, 6, 5], "north": [4, 5, 1, 0],
    "south": [3, 2, 6, 7], "west": [0, 3, 7, 4], "east": [1, 5, 6, 2],
}


def rot_matrix(rot):
    rx, ry, rz = (math.radians(a) for a in rot)
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    mx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    my = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    mz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return mz @ my @ mx


def local_matrix(origin, rot):
    o = np.array(origin, dtype=float)
    t = np.eye(4)
    t[:3, 3] = o
    ti = np.eye(4)
    ti[:3, 3] = -o
    r = np.eye(4)
    r[:3, :3] = rot_matrix(rot)
    return t @ r @ ti


def bake(name):
    data = json.load(open(os.path.join(SRC, name + ".bbmodel"), encoding="utf-8"))
    quads = []
    for e in data["elements"]:
        m = local_matrix(e.get("origin", [0, 0, 0]), e.get("rotation", [0, 0, 0]))
        x0, y0, z0 = e["from"]
        x1, y1, z1 = e["to"]
        corners = [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1),
                   (x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)]
        pts = []
        for c in corners:
            w = m @ np.array([c[0], c[1], c[2], 1.0])
            pts.append([-w[0], 24.0 - w[1], w[2]])
        for face, idx in FACES.items():
            fd = e["faces"].get(face)
            if not fd or not fd.get("uv"):
                continue
            u = fd["uv"]
            uv = [[u[0], u[1]], [u[2], u[1]], [u[2], u[3]], [u[0], u[3]]]
            quads.append({"v": [pts[i] for i in idx], "uv": uv})
    os.makedirs(MODELS, exist_ok=True)
    os.makedirs(TEX, exist_ok=True)
    with open(os.path.join(MODELS, name + ".json"), "w", encoding="utf-8") as fh:
        json.dump({"textureSize": [64, 64], "frames": 1, "quads": quads}, fh,
                  separators=(",", ":"))
    src = data["textures"][0]["source"]
    raw = base64.b64decode(src.split(",", 1)[1])
    with open(os.path.join(TEX, name + ".png"), "wb") as fh:
        fh.write(raw)
    ys = [v[1] for q in quads for v in q["v"]]
    print(name, "quads", len(quads), "y", round(min(ys), 2), round(max(ys), 2))


if __name__ == "__main__":
    bake("wizard_hat")
    bake("eye_patch")
