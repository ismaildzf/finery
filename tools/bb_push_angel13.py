"""Push the restored v3-shape mesh (v13) + armature to Blockbench and export."""
import json
import math
import pathlib
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import bbmcp  # noqa: E402
import angelv13 as av  # noqa: E402

SHOTS = ROOT / "_design" / "bb_angel_v13"
ATLAS = av.ATLAS
MESH = "angel_v13_mesh"
TEX = "angel_v3_atlas"
PROJECT = "AngelWings_v13"
CELL = 14


def build_quads():
    base = Image.open(av.BASE_PNG).convert("RGBA")
    covert = Image.open(av.COVERT_PNG).convert("RGBA")
    sil = av.solid_mask()
    quads = []
    for side in (1, -1):
        quads += av.grid_quads(base, av.BASE_U0, side, CELL, 0.0, back_off=1.0, rim=False, mask=sil)
        quads += av.grid_quads(covert, av.COVERT_U0, side, CELL, 0.72, back_off=0.0,
                               rim=False, tint=(0.985, 0.99, 1.0))
        quads += av.rod_quads(side)
    return quads


def build_payload():
    quads = build_quads()
    verts, faces, uvs = [], [], []
    for verts4, uv4, tint, _tag in quads:
        base = len(verts)
        verts += [[round(float(c), 4) for c in p] for p in verts4]
        faces.append([base, base + 1, base + 2, base + 3])
        if uv4 is None:
            uvs.append([[972.0, 672.0]] * 4)
        else:
            uvs.append([[u * 1024.0, v * 1024.0] for u, v in uv4])
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
  let done = 0, missed = 0;
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
    const uv = refs[best].uv;
    face.uv = {};
    face.vertices.forEach((k, j) => { face.uv[k] = uv[j]; });
    done++;
  }
  Canvas.updateAll();
  return JSON.stringify({faces: Object.keys(mesh.faces).length, updated: done, missed: missed});
})()
""" % (MESH, json.dumps(json.dumps(data)))
    print("uv:", bbmcp.call("risky_eval", {"code": code}))


def add_rig():
    try:
        bbmcp.call("remove_armature", {"id": "WingRigV3"})
    except Exception:
        pass
    bbmcp.call("add_armature", {"name": "WingRigV3", "visibility": True,
                                "add_initial_bone": False})
    bones = [
        ("root", "WingRigV3", [0, -4.4, 0.6], 0, 2.5, 0),
        ("humerus_R", "root", [0, 2.5, 0], -38.7, 4.5, 1),
        ("radius_R", "humerus_R", [0, 4.5, 0], -11.3, 4.4, 1),
        ("hand_R", "radius_R", [0, 4.4, 0], -5.0, 3.6, 1),
        ("finger_a_R", "hand_R", [0, 3.6, 0], 10.0, 3.5, 2),
        ("finger_b_R", "hand_R", [0, 3.6, 0], 35.0, 4.0, 2),
        ("finger_c_R", "hand_R", [0, 3.6, 0], 60.0, 3.5, 2),
    ]
    for name, parent, origin, rot, length, color in bones:
        bbmcp.call("add_armature_bone", {
            "parent_id": parent, "name": name, "origin": origin,
            "rotation": [0, 0, rot], "length": length, "width": 1.2,
            "connected": False, "color": color})
    # mirror by hand (names + rotation sign)
    for name, parent, origin, rot, length, color in bones:
        if name == "root":
            parent_l = "WingRigV3"
        else:
            parent_l = parent.replace("_R", "_L") if parent.endswith("_R") else parent
        bbmcp.call("add_armature_bone", {
            "parent_id": parent_l, "name": name.replace("_R", "_L") if name.endswith("_R") else name + "_L",
            "origin": origin, "rotation": [0, 0, -rot], "length": length,
            "width": 1.2, "connected": False, "color": 4 + color % 4})
    print("bones:", sum(1 for b in bbmcp.call("list_armature_bones",
                                             {"armature_id": "WingRigV3"})["bones"]))


def composite(src, dst):
    im = Image.open(src).convert("RGBA")
    bg = Image.new("RGBA", im.size, (20, 21, 25, 255))
    bg.alpha_composite(im)
    bg.convert("RGB").save(dst)


def main():
    SHOTS.mkdir(parents=True, exist_ok=True)
    print("project:", bbmcp.call("create_project", {"name": PROJECT, "format": "free"}))
    verts, faces, uvs, centers = build_payload()
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
        bbmcp.call("create_offscreen_view", {"id": "angel13", "width": 1200,
                                             "height": 1200, "antialias": True,
                                             "copy_view": "none"})
    except Exception as exc:
        print("offscreen:", exc)
    views = {"back": ([0, -6, 105], 32), "threequarter": ([-68, 4, 80], 32),
             "side": ([100, -6, 4], 32), "close": ([-26, 2, 52], 26)}
    for name, (pos, fov) in views.items():
        bbmcp.call("set_camera_angle", {"view": "angel13", "position": pos,
                                        "target": [0, -3, 0], "fov": fov,
                                        "projection": "perspective"})
        raw = SHOTS / f"raw_{name}.png"
        bbmcp.shot(str(raw), tool="capture_screenshot",
                   args={"view": "angel13", "max_size": 1200})
        composite(raw, SHOTS / f"{name}.png")
        print("shot", name)
    out = (ROOT / "_design" / "AngelWings_v13.bbmodel").resolve()
    try:
        print("export:", json.dumps(bbmcp.call("export_model", {
            "codec_id": "project", "path": str(out), "overwrite": True}))[:200])
    except Exception as exc:
        print("export failed:", exc)
    if out.exists():
        data = json.loads(out.read_text(encoding="utf-8"))
        els = [(e.get("type"), e.get("name")) for e in data.get("elements", [])]
        print("file", out.stat().st_size, "armature", any(t == "armature" for t, _ in els),
              "bones", sum(1 for t, _ in els if t == "armature_bone"))


if __name__ == "__main__":
    main()
