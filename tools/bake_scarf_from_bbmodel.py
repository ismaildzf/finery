"""Bake the owner's saved scarf project (Documents/1.bbmodel) to neck quads.

Reads the real outliner so nested group rotations, element rotations and face
UV rects/rotations match Blockbench exactly. Y is mirrored to Minecraft's body
space (y' = 24 - y). Reference body cubes are skipped.
"""

import json
import math
import os

import numpy as np

SRC = r"C:\Users\Administrator\Documents\1.bbmodel"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "src", "main", "resources", "assets", "finery", "neckmodels")


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


FACES = {
    "down": [0, 1, 2, 3],
    "up": [4, 5, 6, 7],
    "north": [0, 1, 5, 4],
    "south": [3, 2, 6, 7],
    "west": [0, 3, 7, 4],
    "east": [1, 2, 6, 5],
}


def uv_corners(rect, rotation):
    u0, v0, u1, v1 = rect
    corners = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
    steps = int(round((rotation or 0) / 90)) % 4
    for _ in range(steps):
        corners = [corners[3], corners[0], corners[1], corners[2]]
    return corners


def main():
    data = json.load(open(SRC, encoding="utf-8"))
    elements = {e["uuid"]: e for e in data["elements"]}
    groups = {g["uuid"]: g for g in data["groups"]}

    chains = {}

    def walk(node, chain):
        uuid = node["uuid"]
        if uuid in groups:
            g = groups[uuid]
            next_chain = chain + [(g.get("origin", [0, 0, 0]), g.get("rotation", [0, 0, 0]), g.get("name", ""))]
            for child in node.get("children", []):
                if isinstance(child, dict):
                    walk(child, next_chain)
                elif child in elements:
                    chains[child] = next_chain
                elif child in groups:
                    walk({"uuid": child, "children": groups[child].get("children", [])}, next_chain)
        else:
            for child in node.get("children", []):
                if isinstance(child, dict):
                    walk(child, chain)
                elif child in elements:
                    chains[child] = chain

    for node in data["outliner"]:
        walk(node, [])

    quads = []
    for uuid, element in elements.items():
        chain = chains.get(uuid, [])
        if any("reference" in name for _, _, name in chain):
            continue
        m = np.eye(4)
        for origin, rot, _ in chain:
            m = m @ local_matrix(origin, rot)
        m = m @ local_matrix(element.get("origin", [0, 0, 0]), element.get("rotation", [0, 0, 0]))

        x0, y0, z0 = element["from"]
        x1, y1, z1 = element["to"]
        corners = [
            (x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1),
            (x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1),
        ]
        pts = []
        for c in corners:
            w = m @ np.array([c[0], c[1], c[2], 1.0])
            # the entity renderer mirrors X and Y, so both axes are negated here
            pts.append([-w[0], 24.0 - w[1], w[2]])

        for face, idx in FACES.items():
            fd = element.get("faces", {}).get(face)
            if not fd:
                continue
            uv = fd.get("uv")
            if uv is None:
                continue
            rect = [uv[0], uv[1], uv[2], uv[3]]
            face_uv = uv_corners(rect, fd.get("rotation"))
            quads.append({"v": [pts[i] for i in idx], "uv": [list(p) for p in face_uv]})

    os.makedirs(OUT_DIR, exist_ok=True)
    payload = {"textureSize": [512, 512], "quads": quads}
    for name in ("scarf", "royal_scarf"):
        with open(os.path.join(OUT_DIR, name + ".json"), "w", encoding="utf-8") as fh:
            json.dump(payload, fh, separators=(",", ":"))
    xs = [v[0] for q in quads for v in q["v"]]
    ys = [v[1] for q in quads for v in q["v"]]
    zs = [v[2] for q in quads for v in q["v"]]
    print("quads", len(quads), "x", round(min(xs), 2), round(max(xs), 2),
          "y", round(min(ys), 2), round(max(ys), 2), "z", round(min(zs), 2), round(max(zs), 2))


if __name__ == "__main__":
    main()
