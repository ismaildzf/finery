"""Emit a Blockbench (Bedrock) file that mirrors our in-game head geometry.

Every part is flattened into an element with its full transform, so the file
can be reviewed in Blockbench without the mod running. Coordinates are
head-local; the viewer adds the player head at 24..32 as a reference.
"""
import base64
import io
import json
import math
import uuid
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "publishing" / "headband_eyewrap.bbmodel"


def rot_x(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def rot_y(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def rot_z(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def euler_deg(r):
    y = math.degrees(math.asin(max(-1.0, min(1.0, -r[2, 0]))))
    x = math.degrees(math.atan2(r[2, 1], r[2, 2]))
    z = math.degrees(math.atan2(r[1, 0], r[0, 0]))
    return [round(x, 3), round(y, 3), round(z, 3)]


def part(name, cuboids, pivot=(0, 0, 0), rot=None, parent=None):
    return {
        "name": name,
        "cuboids": cuboids,          # list of (from, size)
        "pivot": np.array(pivot, float),
        "rot": rot if rot is not None else np.eye(3),
        "parent": parent,
    }


# ── headband ────────────────────────────────────────────────────────────
HEADBAND = [
    part("band_front", [((-4.6, -7.15, -4.6), (9.2, 2.05, 0.3))]),
    part("band_back", [((-4.6, -7.15, 4.3), (9.2, 2.05, 0.3))]),
    part("band_left", [((-4.6, -7.15, -4.3), (0.3, 2.05, 8.6))]),
    part("band_right", [((4.3, -7.15, -4.3), (0.3, 2.05, 8.6))]),
    part("lip_front", [((-4.66, -5.3, -4.66), (9.32, 0.35, 0.34))]),
    part("lip_back", [((-4.66, -5.3, 4.32), (9.32, 0.35, 0.34))]),
    part("lip_left", [((-4.66, -5.3, -4.32), (0.34, 0.35, 8.64))]),
    part("lip_right", [((4.32, -5.3, -4.32), (0.34, 0.35, 8.64))]),
    part("band_pad", [((-3.6, -6.95, -4.75), (7.2, 1.6, 0.3))]),
    part("wrap_diagonal", [((-4.3, -0.52, -0.16), (8.6, 1.05, 0.32))],
         pivot=(0, -6.15, -4.83), rot=rot_z(0.16)),
    part("knot_base", [((-0.85, -0.8, 0.0), (1.7, 1.6, 0.55))],
         pivot=(3.25, -6.1, 3.25), rot=rot_y(0.785)),
]

KNOT = part("knot_loops", [
    ((-1.35, -0.55, 0.3), (1.15, 1.1, 0.3)),
    ((0.2, -0.55, 0.3), (1.15, 1.1, 0.3)),
    ((-1.05, -0.28, 0.55), (2.1, 0.56, 0.3)),
], pivot=(3.25, -6.1, 3.25), rot=rot_y(0.785))
KNOT["loops"] = [
    ((-1.35, -0.55, 0.3), (1.15, 1.1, 0.3), (-0.5, 0.0, 0.4), rot_z(0.55)),
    ((0.2, -0.55, 0.3), (1.15, 1.1, 0.3), (0.5, 0.0, 0.4), rot_z(-0.55)),
    ((-1.05, -0.28, 0.55), (2.1, 0.56, 0.3), (0.0, 0.0, 0.55), rot_z(0.24)),
]

# ── eyewrap ─────────────────────────────────────────────────────────────
EYEWRAP = [
    part("blind_front_top", [((-4.6, -5.0, -4.55), (9.2, 0.8, 0.5))]),
    part("blind_front_mid", [((-4.6, -4.2, -4.72), (9.2, 1.0, 0.62))]),
    part("blind_front_bot", [((-4.6, -3.2, -4.55), (9.2, 0.6, 0.5))]),
    part("blind_back", [((-4.6, -5.0, 4.1), (9.2, 2.4, 0.5))]),
    part("blind_left", [((-4.6, -5.0, -4.1), (0.5, 2.4, 8.2))]),
    part("blind_right", [((4.1, -5.0, -4.1), (0.5, 2.4, 8.2))]),
    part("bevel_fl", [((-0.5, -5.0, -0.5), (1.0, 2.4, 1.0))], pivot=(-4.06, 0, -4.06), rot=rot_y(0.785)),
    part("bevel_fr", [((-0.5, -5.0, -0.5), (1.0, 2.4, 1.0))], pivot=(4.06, 0, -4.06), rot=rot_y(-0.785)),
    part("bevel_bl", [((-0.5, -5.0, -0.5), (1.0, 2.4, 1.0))], pivot=(-4.06, 0, 4.06), rot=rot_y(-0.785)),
    part("bevel_br", [((-0.5, -5.0, -0.5), (1.0, 2.4, 1.0))], pivot=(4.06, 0, 4.06), rot=rot_y(0.785)),
    part("back_overlap_a", [((-1.5, -4.75, 4.42), (3.2, 1.8, 0.26))], pivot=(0, 0, 4.5), rot=rot_z(0.10)),
    part("back_overlap_b", [((-1.1, -4.55, 4.55), (2.7, 1.4, 0.24))], pivot=(0, 0, 4.6), rot=rot_z(-0.12)),
    part("cheek_l", [((1.8, -3.45, -4.78), (2.4, 0.55, 0.6))], pivot=(3.0, 0, -4.4), rot=rot_z(-0.10)),
    part("cheek_r", [((-4.2, -3.45, -4.78), (2.4, 0.55, 0.6))], pivot=(-3.0, 0, -4.4), rot=rot_z(0.10)),
]


def make_texture():
    img = Image.new("RGBA", (64, 64), (236, 228, 216, 255))
    d = ImageDraw.Draw(img)
    for y in range(0, 32, 2):
        d.line([(0, y), (32, y)], fill=(214, 204, 190, 255))
    for x in range(0, 32, 4):
        d.line([(x, 0), (x, 32)], fill=(222, 213, 199, 255))
    d.rectangle([32, 0, 63, 63], fill=(96, 100, 108, 255))
    for y in range(32, 64, 4):
        d.line([(32, y), (63, y)], fill=(78, 82, 90, 255))
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def element(part_def, from_v, size, uv_rect=(0, 0, 32, 32)):
    f = np.array(from_v, float)
    t = f + np.array(size, float)
    world_from = part_def["origin"] + f
    world_to = part_def["origin"] + t
    faces = {face: {"uv": list(uv_rect), "texture": 0}
             for face in ("north", "east", "south", "west", "up", "down")}
    return {
        "name": part_def["name"] + "_" + uuid.uuid4().hex[:4],
        "box_uv": False,
        "render_order": "default",
        "locked": False,
        "export": True,
        "scope": 0,
        "allow_mirror_modeling": True,
        "from": [round(v, 3) for v in world_from],
        "to": [round(v, 3) for v in world_to],
        "autouv": 0,
        "color": 0,
        "origin": [round(v, 3) for v in part_def["origin"]],
        "rotation": part_def["rotation"],
        "faces": faces,
        "type": "cube",
        "uuid": str(uuid.uuid4()),
    }


def group(name, origin, rotation=(0, 0, 0)):
    uid = str(uuid.uuid4())
    meta = {
        "name": name, "uuid": uid, "export": True, "locked": False, "scope": 0,
        "selected": False, "visibility": True,
        "_static": {"properties": {}, "temp_data": {}},
        "origin": list(origin), "rotation": list(rotation),
        "bedrock_binding": "", "color": 0, "children": [], "reset": False,
        "shade": True, "mirror_uv": False, "autouv": 0, "isOpen": True,
        "primary_selected": False,
    }
    return meta, {"uuid": uid, "isOpen": True, "children": []}


def build():
    elements, group_meta, outliner = [], [], []

    def emit(parts, group_name):
        meta, node = group(group_name, (0, 0, 0))
        group_meta.append(meta)
        for p in parts:
            p["origin"] = np.array(p["pivot"], float)
            p["rotation"] = euler_deg(p["rot"])
            for from_v, size in p["cuboids"]:
                e = element(p, from_v, size)
                elements.append(e)
                node["children"].append(e["uuid"])
            if p["name"] == "knot_base":
                for from_v, size, pivot, rot in KNOT["loops"]:
                    sub = dict(p)
                    sub["name"] = "knot_loop"
                    sub["origin"] = p["origin"] + p["rot"] @ np.array(pivot, float)
                    sub["rotation"] = euler_deg(p["rot"] @ rot)
                    e = element(sub, from_v, size)
                    elements.append(e)
                    node["children"].append(e["uuid"])
        outliner.append(node)

    emit(HEADBAND, "headband")
    emit(EYEWRAP, "eyewrap")

    head_meta, head_node = group("HEAD_REFERENCE (hide me)", (0, -8, 0))
    head = {
        "name": "HEAD_REFERENCE", "box_uv": False, "render_order": "default",
        "locked": False, "export": True, "scope": 0, "allow_mirror_modeling": True,
        "from": [-4, -8, -4], "to": [4, 0, 4], "autouv": 0, "color": 0,
        "origin": [0, -8, 0], "rotation": [0, 0, 0],
        "faces": {f: {"uv": [34, 34, 62, 62], "texture": 0}
                  for f in ("north", "east", "south", "west", "up", "down")},
        "type": "cube", "uuid": str(uuid.uuid4()),
    }
    elements.append(head)
    head_node["children"].append(head["uuid"])
    group_meta.append(head_meta)
    outliner.append(head_node)

    for e in elements:
        for key in ("from", "to", "origin"):
            e[key][1] += 32.0
    for m in group_meta:
        m["origin"][1] += 32.0

    data = {
        "meta": {"format_version": "5.0", "model_format": "bedrock", "box_uv": False},
        "name": "Finery headband + eyewrap (in-game shape)",
        "model_identifier": "",
        "resolution": {"width": 64, "height": 64},
        "elements": elements,
        "groups": group_meta,
        "outliner": outliner,
        "textures": [{"name": "preview_cloth.png", "path": "", "source": make_texture(),
                      "width": 64, "height": 64, "uv_width": 64, "uv_height": 64}],
    }
    OUT.write_text(json.dumps(data), encoding="utf-8")
    print("wrote", OUT, "elements", len(elements))


if __name__ == "__main__":
    build()
