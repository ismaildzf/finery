"""Restore the eyewrap's wrap width and thin its material.

Width: back to the authored x +-4.62 and z -4.833..4.539.
Thickness: the inner shell of every wall moves from 4.12 to 4.42, so each wall
is 0.2 px thick instead of 0.5.
"""

import json
import os

PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "src", "main", "resources", "assets", "finery", "headmodels", "eye_wrap.json")

CUR_LIMIT = 4.3
X0, X1 = -4.62, 4.62
Z0, Z1 = -4.833, 4.539
INNER = 4.12
OUTER_INNER = 4.42


def main():
    with open(PATH, encoding="utf-8") as fh:
        data = json.load(fh)
    for q in data["quads"]:
        for p in q["v"]:
            p[0] = X0 + (p[0] + CUR_LIMIT) / (2 * CUR_LIMIT) * (X1 - X0)
            p[2] = Z0 + (p[2] + CUR_LIMIT) / (2 * CUR_LIMIT) * (Z1 - Z0)
            if abs(abs(p[2]) - INNER) < 0.03:
                p[2] = OUTER_INNER if p[2] > 0 else -OUTER_INNER
            if abs(abs(p[0]) - INNER) < 0.03:
                p[0] = OUTER_INNER if p[0] > 0 else -OUTER_INNER
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
