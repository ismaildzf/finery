"""Push the Angel v10 feather mesh + armature into Blockbench and capture views."""
import json
import pathlib
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import bbmcp  # noqa: E402
import angelv10 as av  # noqa: E402

SHOTS = ROOT / "_design" / "bb_angel"
ATLAS = ROOT / "_design" / "angel_feather_atlas_bb.png"
MESH = "angel_v10_mesh"
TEX = "angel_feather_atlas"
PROJECT = "AngelWings_v10"


def build_payload():
    atlas = Image.open(av.ART / "seraph_feather_atlas.png").convert("RGBA")
    atlas.save(ATLAS)
    rects = json.loads((av.ART / "seraph_atlas_rects.json").read_text())
    feathers = av.layout(rects)
    quads = []
    for side in (1, -1):
        for f in feathers:
            quads += av.s8.feather_quads(f, rects, side)
    verts, faces, uvs = [], [], []
    for verts4, uv4, _tint in quads:
        base = len(verts)
        verts += [[round(float(c), 4) for c in p] for p in verts4]
        faces.append([base, base + 1, base + 2, base + 3])
        uvs.append([[float(u), float(v)] for u, v in uv4])
    centers = []
    for f in faces:
        pts = [verts[i] for i in f]
        centers.append([round(sum(p[k] for p in pts) / len(pts), 4) for k in range(3)])
    print(f"mesh {len(verts)} verts, {len(faces)} quads")
    return verts, faces, uvs, centers


def assign_uvs(uvs, centers):
    data = [{"c": c, "uv": u} for c, u in zip(centers, uvs)]
    code = """
(() => {
  const mesh = Mesh.all.find(m => m.name === '%s');
  const refs = JSON.parse(%s);
  let done = 0, missed = 0, maxDist = 0;
  for (const key in mesh.faces) {
    const face = mesh.faces[key];
    const pts = face.vertices.map(k => mesh.vertices[k]);
    const c = [0, 1, 2].map(axis => pts.reduce((a, p) => a + p[axis], 0) / pts.length);
    let best = -1, bd = 1e9;
    for (let i = 0; i < refs.length; i++) {
      const r = refs[i].c;
      const d = (r[0]-c[0])**2 + (r[1]-c[1])**2 + (r[2]-c[2])**2;
      if (d < bd) { bd = d; best = i; }
    }
    if (best < 0 || bd > 0.05) { missed++; continue; }
    maxDist = Math.max(maxDist, Math.sqrt(bd));
    const uv = refs[best].uv;
    face.uv = {};
    face.vertices.forEach((k, j) => { face.uv[k] = uv[j]; });
    done++;
  }
  Canvas.updateAll();
  return JSON.stringify({faces: Object.keys(mesh.faces).length, updated: done,
                         missed: missed, maxDist: maxDist});
})()
""" % (MESH, json.dumps(json.dumps(data)))
    print("uv:", bbmcp.call("risky_eval", {"code": code}))


def add_rig():
    try:
        bbmcp.call("remove_armature", {"id": "WingRig"})
    except Exception as exc:  # noqa: BLE001
        print("remove rig:", exc)
    print("armature:", bbmcp.call("add_armature", {
        "name": "WingRig", "visibility": True, "add_initial_bone": False}))
    bones = [
        # name, parent, origin(relative), rotation xyz, length, color
        ("root", "WingRig", [0, -3.0, 0.6], [0, 0, 0], 3.0, 0),
        ("humerus_R", "root", [0, 3.0, 0], [0, 0, -45], 4.25, 1),
        ("radius_R", "humerus_R", [0, 4.25, 0], [0, 0, -3], 4.75, 1),
        ("hand_R", "radius_R", [0, 4.75, 0], [0, 0, 1], 4.1, 1),
        ("finger_a_R", "hand_R", [0, 4.1, 0], [0, 0, 28], 6.0, 2),
        ("finger_b_R", "hand_R", [0, 4.1, 0], [0, 0, -7], 7.0, 2),
        ("finger_c_R", "hand_R", [0, 4.1, 0], [0, 0, -42], 6.0, 2),
        ("root_L", "WingRig", [0, -3.0, 0.6], [0, 0, 0], 3.0, 0),
        ("humerus_L", "root_L", [0, 3.0, 0], [0, 0, 45], 4.25, 4),
        ("radius_L", "humerus_L", [0, 4.25, 0], [0, 0, 3], 4.75, 4),
        ("hand_L", "radius_L", [0, 4.75, 0], [0, 0, -1], 4.1, 4),
        ("finger_a_L", "hand_L", [0, 4.1, 0], [0, 0, -28], 6.0, 5),
        ("finger_b_L", "hand_L", [0, 4.1, 0], [0, 0, 7], 7.0, 5),
        ("finger_c_L", "hand_L", [0, 4.1, 0], [0, 0, 42], 6.0, 5),
    ]
    for name, parent, origin, rot, length, color in bones:
        try:
            bbmcp.call("add_armature_bone", {
                "parent_id": parent, "name": name, "origin": origin,
                "rotation": rot, "length": length, "width": 1.2,
                "connected": False, "color": color})
        except Exception as exc:  # noqa: BLE001
            print("bone", name, "failed:", exc)
    print("bones:", bbmcp.call("list_armature_bones", {"armature_id": "WingRig"}))


def composite(src, dst):
    im = Image.open(src).convert("RGBA")
    bg = Image.new("RGBA", im.size, (20, 21, 25, 255))
    bg.alpha_composite(im)
    bg.convert("RGB").save(dst)


def main():
    SHOTS.mkdir(parents=True, exist_ok=True)
    print("current project:", bbmcp.call("get_project_info"))
    try:
        print("checkpoint:", bbmcp.call("save_checkpoint", {"name": "before angel v10"}))
    except Exception as exc:  # noqa: BLE001
        print("checkpoint failed:", exc)
    print("project:", bbmcp.call("create_project", {"name": PROJECT, "format": "free"}))
    verts, faces, uvs, centers = build_payload()
    try:
        bbmcp.call("remove_element", {"id": MESH})
    except Exception as exc:  # noqa: BLE001
        print("remove mesh:", exc)
    bbmcp.call("create_texture", {
        "name": TEX, "width": 1024, "height": 1024,
        "uv_width": 1024, "uv_height": 1024, "data": str(ATLAS),
        "render_sides": "double"})
    bbmcp.call("place_mesh", {
        "elements": [{"name": MESH, "position": [0, 0, 0],
                      "vertices": verts, "faces": faces}],
        "texture": TEX})
    assign_uvs(uvs, centers)
    add_rig()
    try:
        bbmcp.call("create_offscreen_view", {"id": "angel", "width": 1200,
                                             "height": 1200, "antialias": True,
                                             "copy_view": "none"})
    except Exception as exc:  # noqa: BLE001
        print("offscreen:", exc)
    views = {"back": ([0, -6, 105], 32), "threequarter": ([-68, 4, 80], 32),
             "side": ([100, -6, 4], 32), "close": ([-26, 2, 52], 26)}
    for name, (pos, fov) in views.items():
        bbmcp.call("set_camera_angle", {"view": "angel", "position": pos,
                                        "target": [0, -3, 0], "fov": fov,
                                        "projection": "perspective"})
        raw = SHOTS / f"raw_{name}.png"
        bbmcp.shot(str(raw), tool="capture_screenshot",
                   args={"view": "angel", "max_size": 1200})
        composite(raw, SHOTS / f"{name}.png")
        print("shot", name)


if __name__ == "__main__":
    main()
