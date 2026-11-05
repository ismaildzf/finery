"""Push seraph_v8 into Blockbench and assign UVs by matching face centers."""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import bbmcp  # noqa: E402
import seraph_v8 as v8  # noqa: E402

SHOTS = ROOT / "_design" / "bb_v8"
ATLAS = ROOT / "_design" / "seraph_atlas_bb.png"


def build_payload():
    atlas, rects = v8.build_atlas()
    feathers = v8.layout(rects)
    quads = v8.build_model(feathers, rects)
    verts, faces, uvs = [], [], []
    for verts4, uv4, _tint in quads:
        base = len(verts)
        verts += [[round(float(c), 4) for c in p] for p in verts4]
        faces.append([base, base + 1, base + 2, base + 3])
        uvs.append([[float(u) / 2.0, float(v) / 2.0] for u, v in uv4])
    xs = [p[0] for p in verts]
    ys = [p[1] for p in verts]
    zs = [p[2] for p in verts]
    off = [(min(xs) + max(xs)) * 0.5, (min(ys) + max(ys)) * 0.5, (min(zs) + max(zs)) * 0.5]
    verts = [[p[0] - off[0], p[1] - off[1], p[2] - off[2]] for p in verts]
    centers = []
    for f in faces:
        pts = [verts[i] for i in f]
        centers.append([round(sum(p[k] for p in pts) / len(pts), 4) for k in range(3)])
    atlas.resize((512, 512)).save(ATLAS)
    print(f"mesh {len(verts)} verts, {len(faces)} quads")
    return verts, faces, uvs, centers


def assign_uvs(uvs, centers):
    data = [{"c": c, "uv": u} for c, u in zip(centers, uvs)]
    code = """
(() => {
  const mesh = Mesh.all.find(m => m.name === 'seraph_v8');
  const refs = JSON.parse(%s);
  let done = 0, maxDist = 0, missed = 0;
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
""" % json.dumps(json.dumps(data))
    print("uv:", bbmcp.call("risky_eval", {"code": code}))


def main():
    SHOTS.mkdir(parents=True, exist_ok=True)
    verts, faces, uvs, centers = build_payload()

    try:
        bbmcp.call("remove_element", {"id": "seraph_v8"})
    except Exception as exc:  # noqa: BLE001
        print("remove mesh:", exc)
    try:
        bbmcp.call("delete_texture", {"texture": "seraph_feathers"})
    except Exception as exc:  # noqa: BLE001
        print("remove tex:", exc)
    try:
        bbmcp.call("create_texture", {
            "name": "seraph_feathers", "width": 512, "height": 512,
            "uv_width": 512, "uv_height": 512, "data": str(ATLAS),
            "render_sides": "double"})
        print("texture created")
    except Exception as exc:  # noqa: BLE001
        print("texture:", exc)
    bbmcp.call("place_mesh", {
        "elements": [{"name": "seraph_v8", "position": [0, 0, 0],
                      "vertices": verts, "faces": faces}],
        "texture": "seraph_feathers"})
    print("mesh placed")

    assign_uvs(uvs, centers)

    views = {"back": ([0, 3, 130], 28), "threequarter": ([-90, 22, 100], 30),
             "side": ([130, 5, 0], 28), "top": ([0, 130, 2], 28)}
    for name, (pos, fov) in views.items():
        bbmcp.call("set_camera_angle", {"view": "v1", "position": pos,
                                        "target": [0, 0, 0], "fov": fov,
                                        "projection": "perspective"})
        bbmcp.shot(str(SHOTS / f"off5_{name}.png"), tool="capture_screenshot",
                   args={"view": "v1", "max_size": 1200})
        print("shot", name)


if __name__ == "__main__":
    main()
