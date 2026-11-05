"""Pull the eyewrap toward the face (depth only).

The band keeps its horizontal width (x +-4.62) but its depth shrinks from
-4.833..4.539 to -4.35..4.30, i.e. it protrudes ~0.3 px instead of ~0.8.
"""

import json
import os

PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "src", "main", "resources", "assets", "finery", "headmodels", "eye_wrap.json")

NEW_Z0, NEW_Z1 = -4.35, 4.30


def main():
    with open(PATH, encoding="utf-8") as fh:
        data = json.load(fh)
    zs = [p[2] for q in data["quads"] for p in q["v"]]
    z0, z1 = min(zs), max(zs)
    for q in data["quads"]:
        for p in q["v"]:
            p[2] = NEW_Z0 + (p[2] - z0) / (z1 - z0) * (NEW_Z1 - NEW_Z0)
    with open(PATH, "w", encoding="utf-8") as fh:
        json.dump(data, fh, separators=(",", ":"))
    xs = [p[0] for q in data["quads"] for p in q["v"]]
    ys = [p[1] for q in data["quads"] for p in q["v"]]
    zs = [p[2] for q in data["quads"] for p in q["v"]]
    print("x", round(min(xs), 2), round(max(xs), 2),
          "y", round(min(ys), 2), round(max(ys), 2),
          "z", round(min(zs), 2), round(max(zs), 2))


if __name__ == "__main__":
    main()
