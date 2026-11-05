"""Make the eyewrap thinner and hug the head more closely.

Vertical: keep the lower edge over the eyes and cut the band down to ~1.2 px.
Horizontal: pull both x and z in to +-4.3 px (0.3 px outside the 8 px head).
"""

import json
import os

PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "src", "main", "resources", "assets", "finery", "headmodels", "eye_wrap.json")

NEW_H = 1.2
LIMIT = 4.3


def main():
    with open(PATH, encoding="utf-8") as fh:
        data = json.load(fh)
    xs = [p[0] for q in data["quads"] for p in q["v"]]
    ys = [p[1] for q in data["quads"] for p in q["v"]]
    zs = [p[2] for q in data["quads"] for p in q["v"]]
    x0, x1 = min(xs), max(xs)
    z0, z1 = min(zs), max(zs)
    y0, y1 = min(ys), max(ys)
    for q in data["quads"]:
        for p in q["v"]:
            p[0] = (p[0] - x0) / (x1 - x0) * (2 * LIMIT) - LIMIT
            p[2] = (p[2] - z0) / (z1 - z0) * (2 * LIMIT) - LIMIT
            p[1] = y1 - (y1 - p[1]) / (y1 - y0) * NEW_H
    with open(PATH, "w", encoding="utf-8") as fh:
        json.dump(data, fh, separators=(",", ":"))
    ys = [p[1] for q in data["quads"] for p in q["v"]]
    print("y", round(min(ys), 2), round(max(ys), 2), "x/z +-", LIMIT)


if __name__ == "__main__":
    main()
