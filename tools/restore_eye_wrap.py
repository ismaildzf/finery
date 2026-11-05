"""Restore the eyewrap to its authored Blockbench dimensions.

x +-4.62, y -4.664..-2.493, z -4.833..4.539 (undoes the thinning and flattening).
"""

import json
import os

PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "src", "main", "resources", "assets", "finery", "headmodels", "eye_wrap.json")

TARGET = {
    0: (-4.62, 4.62),
    1: (-4.664, -2.493),
    2: (-4.833, 4.539),
}


def main():
    with open(PATH, encoding="utf-8") as fh:
        data = json.load(fh)
    for axis, (a, b) in TARGET.items():
        vals = [p[axis] for q in data["quads"] for p in q["v"]]
        c, d = min(vals), max(vals)
        if abs(d - c) < 1e-6:
            continue
        for q in data["quads"]:
            for p in q["v"]:
                p[axis] = a + (p[axis] - c) / (d - c) * (b - a)
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
