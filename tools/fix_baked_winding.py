"""Make every baked quad face away from its element centroid.

Blockbench renders models double-sided, so a model exported face by face can
come out with inconsistent winding. Minecraft culls back faces, which made
most of the band walls disappear and left only the flat top/bottom rims.
"""

import json
import os


def comps(quads):
    parent = list(range(len(quads)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    seen = {}
    for i, q in enumerate(quads):
        for v in q["v"]:
            k = tuple(round(c, 2) for c in v)
            if k in seen:
                ra, rb = find(i), find(seen[k])
                if ra != rb:
                    parent[ra] = rb
            else:
                seen[k] = i
    groups = {}
    for i in range(len(quads)):
        groups.setdefault(find(i), []).append(i)
    return list(groups.values())


def normal(q):
    v = q["v"]
    ax, ay, az = v[1][0] - v[0][0], v[1][1] - v[0][1], v[1][2] - v[0][2]
    bx, by, bz = v[2][0] - v[0][0], v[2][1] - v[0][1], v[2][2] - v[0][2]
    return ay * bz - az * by, az * bx - ax * bz, ax * by - ay * bx


def fix(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    quads = data["quads"]
    flipped = 0
    for group in comps(quads):
        cx = sum(v[0] for i in group for v in quads[i]["v"]) / (4 * len(group))
        cy = sum(v[1] for i in group for v in quads[i]["v"]) / (4 * len(group))
        cz = sum(v[2] for i in group for v in quads[i]["v"]) / (4 * len(group))
        for i in group:
            q = quads[i]
            nx, ny, nz = normal(q)
            px = sum(v[0] for v in q["v"]) / 4 - cx
            py = sum(v[1] for v in q["v"]) / 4 - cy
            pz = sum(v[2] for v in q["v"]) / 4 - cz
            if nx * px + ny * py + nz * pz < 0:
                q["v"] = [q["v"][0], q["v"][3], q["v"][2], q["v"][1]]
                q["uv"] = [q["uv"][0], q["uv"][3], q["uv"][2], q["uv"][1]]
                flipped += 1
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, separators=(",", ":"))
    print(os.path.basename(path), "flipped", flipped, "of", len(quads), "components", len(comps(quads)))


if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for name in ("eye_wrap", "headband"):
        fix(os.path.join(root, "src", "main", "resources", "assets", "finery", "headmodels", name + ".json"))
