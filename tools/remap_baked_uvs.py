"""Remap the baked UVs onto the compact animated strip layout.

headband: 320x56 per frame, art at the sheet's (10,10)-(330,66)
eye_wrap: 320x64 per frame, art at the sheet's (10,220)-(330,284)
"""

import json
import os

JOBS = {
    "headband": (320, 56, 10.0, 10.0, 2.0),
    "eye_wrap": (320, 64, 10.0, 220.0, 64.0 / 56.0),
}


def fix(path, tw, th, off_u, off_v, v_scale):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    data["textureSize"] = [tw, th]
    for q in data["quads"]:
        for p in q["uv"]:
            p[0] = p[0] * 2.0 - off_u
            p[1] = (p[1] * 2.0 - off_v) * v_scale
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, separators=(",", ":"))
    us = [p[0] for q in data["quads"] for p in q["uv"]]
    vs = [p[1] for q in data["quads"] for p in q["uv"]]
    print(os.path.basename(path), "u", round(min(us), 1), round(max(us), 1),
          "v", round(min(vs), 1), round(max(vs), 1), "size", tw, th)


if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for name, args in JOBS.items():
        fix(os.path.join(root, "src", "main", "resources", "assets", "finery", "headmodels", name + ".json"), *args)
