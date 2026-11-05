"""Correct the Blockbench -> Minecraft Y axis for baked models.

Blockbench's player head spans y 24 (chin) .. 32 (crown); Minecraft's head part
spans y -8 (crown) .. 0 (chin). The bake originally used y-32, which is a
translation and leaves the model upside down. The right mapping is 24 - y,
i.e. y' = -y - 8. Run fix_baked_winding.py afterwards to restore outward faces.
"""

import json
import os


def fix(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    for q in data["quads"]:
        for v in q["v"]:
            v[1] = -v[1] - 8.0
    ys = [v[1] for q in data["quads"] for v in q["v"]]
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, separators=(",", ":"))
    print(os.path.basename(path), "new y range", round(min(ys), 2), round(max(ys), 2))


if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for name in ("eye_wrap", "headband"):
        fix(os.path.join(root, "src", "main", "resources", "assets", "finery", "headmodels", name + ".json"))
