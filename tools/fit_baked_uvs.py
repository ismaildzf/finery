"""Fit the baked models' V range to the band zone the texture actually draws.

The Blockbench UVs cover 32 texels (v 5..37 / 110..142) while the owner's script
paints a 28-texel band (5..33 / 110..138). Squeezing V into the painted zone
stops the band sampling the empty strip under the flames.
"""

import json
import os

FITS = {
    "headband": ((5.0, 37.0), (5.0, 33.0)),
    "eye_wrap": ((110.0, 142.0), (110.0, 138.0)),
}


def fix(path, src, dst):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    s0, s1 = src
    d0, d1 = dst
    for q in data["quads"]:
        for p in q["uv"]:
            p[1] = d0 + (p[1] - s0) * (d1 - d0) / (s1 - s0)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, separators=(",", ":"))
    vs = [p[1] for q in data["quads"] for p in q["uv"]]
    print(os.path.basename(path), "v", round(min(vs), 2), round(max(vs), 2))


if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for name, (src, dst) in FITS.items():
        fix(os.path.join(root, "src", "main", "resources", "assets", "finery", "headmodels", name + ".json"), src, dst)
