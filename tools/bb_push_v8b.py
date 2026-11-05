"""Push seraph_v8 into Blockbench through the plugin's mesh/texture tools."""
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
        verts += [[round(float(c), 3) for c in p] for p in verts4]
        faces.append([base, base + 1, base + 2, base + 3])
        uvs.append([[float(u) / 2.0, float(v) / 2.0] for u, v in uv4])
    xs = [p[0] for p in verts]
    ys = [p[1] for p in verts]
    zs = [p[2] for p in verts]
    off = [(min(xs) + max(xs)) * 0.5, (min(ys) + max(ys)) * 0.5, (min(zs) + max(zs)) * 0.5]
    verts = [[p[0] - off[0], p[1] - off[1], p[2] - off[2]] for p in verts]
    atlas.resize((512, 512)).save(ATLAS)
    print(f"mesh {len(verts)} verts, {len(faces)} quads, off {off}")
    return verts, faces, uvs


def main():
    SHOTS.mkdir(parents=True, exist_ok=True)
    verts, faces, uvs = build_payload()

    try:
        bbmcp.call("remove_element", {"id": "seraph_v8"})
    except Exception as exc:  # noqa: BLE001
        print("remove mesh:", exc)
    try:
        bbmcp.call("delete_texture", {"texture": "seraph_feathers"})
    except Exception as exc:  # noqa: BLE001
        print("remove tex:", exc)

    bbmcp.call("create_texture", {
        "name": "seraph_feathers", "width": 512, "height": 512,
        "uv_width": 512, "uv_height": 512, "data": str(ATLAS),
        "render_sides": "double"})
    print("texture created")
    bbmcp.call("place_mesh", {
        "elements": [{"name": "seraph_v8", "position": [0, 0, 0],
                      "vertices": verts, "faces": faces}],
        "texture": "seraph_feathers"})
    print("mesh placed")

    code = """
(() => {
  const mesh = Mesh.all.find(m => m.name === 'seraph_v8');
  const data = JSON.parse(%s);
  const ids = Object.keys(mesh.faces);
  let done = 0;
  ids.forEach((id, i) => {
    const face = mesh.faces[id];
    if (!data[i]) return;
    const keys = face.vertices;
    face.uv = {};
    keys.forEach((k, j) => { face.uv[k] = data[i][j]; });
    done++;
  });
  Canvas.updateAll();
  return JSON.stringify({faces: ids.length, updated: done, sample: mesh.faces[ids[0]].uv});
})()
""" % json.dumps(json.dumps(uvs))
    print("uv:", bbmcp.call("risky_eval", {"code": code}))

    views = {"back": ([0, 3, 150], 30), "threequarter": ([-105, 25, 115], 32),
             "side": ([150, 5, 0], 30), "top": ([0, 150, 2], 30)}
    for name, (pos, fov) in views.items():
        bbmcp.call("set_camera_angle", {"view": "v1", "position": pos,
                                        "target": [0, 0, 0], "fov": fov,
                                        "projection": "perspective"})
        bbmcp.shot(str(SHOTS / f"off2_{name}.png"), tool="capture_screenshot",
                   args={"view": "v1", "max_size": 1200})
        print("shot", name)


if __name__ == "__main__":
    main()
