"""Push devil_v1 into Blockbench and assign UVs by nearest face center."""
import json
import pathlib
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import bbmcp  # noqa: E402
import devil_v1 as dv  # noqa: E402

SHOTS = ROOT / "_design" / "bb_devil"
ATLAS = ROOT / "_design" / "devil_atlas_bb_v5.png"
MESH = "devil_v1"
TEX = "devil_membrane_v5"


def build_payload():
    atlas = dv.build_atlas()
    quads = dv.build_model()
    verts, faces, uvs = [], [], []
    for verts4, uv4 in quads:
        base = len(verts)
        verts += [[round(float(c), 4) for c in p] for p in verts4]
        faces.append([base, base + 1, base + 2, base + 3])
        # Blockbench mesh UVs are in texture pixels, not 0..1
        uvs.append([[float(u) * 512.0, float(v) * 512.0] for u, v in uv4])
    xs = [p[0] for p in verts]
    ys = [p[1] for p in verts]
    zs = [p[2] for p in verts]
    off = [(min(xs) + max(xs)) * 0.5, (min(ys) + max(ys)) * 0.5,
           (min(zs) + max(zs)) * 0.5]
    verts = [[p[0] - off[0], p[1] - off[1], p[2] - off[2]] for p in verts]
    centers = []
    for f in faces:
        pts = [verts[i] for i in f]
        centers.append([round(sum(p[k] for p in pts) / len(pts), 4) for k in range(3)])
    atlas.save(ATLAS)
    print(f"mesh {len(verts)} verts, {len(faces)} quads, bbox off {off}")
    return verts, faces, uvs, centers


def assign_uvs(uvs, centers):
    data = [{"c": c, "uv": u} for c, u in zip(centers, uvs)]
    code = """
(() => {
  const mesh = Mesh.all.find(m => m.name === '%s');
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
""" % (MESH, json.dumps(json.dumps(data)))
    print("uv:", bbmcp.call("risky_eval", {"code": code}))


def composite(src, dst, label):
    im = Image.open(src).convert("RGBA")
    bg = Image.new("RGBA", im.size, (20, 21, 25, 255))
    bg.alpha_composite(im)
    bg.convert("RGB").save(dst)


def main():
    SHOTS.mkdir(parents=True, exist_ok=True)
    verts, faces, uvs, centers = build_payload()

    try:
        bbmcp.call("remove_element", {"id": MESH})
    except Exception as exc:  # noqa: BLE001
        print("remove mesh:", exc)
    names = [t.get("name") for t in (bbmcp.call("list_textures") or [])]
    if TEX in names:
        print("reusing texture", TEX)
    else:
        bbmcp.call("create_texture", {
            "name": TEX, "width": 512, "height": 512,
            "uv_width": 512, "uv_height": 512, "data": str(ATLAS),
            "render_sides": "double"})
        print("texture created")
    bbmcp.call("place_mesh", {
        "elements": [{"name": MESH, "position": [0, 0, 0],
                      "vertices": verts, "faces": faces}],
        "texture": TEX})
    print("mesh placed")
    assign_uvs(uvs, centers)

    try:
        bbmcp.call("create_offscreen_view", {"id": "devil", "width": 1200,
                                             "height": 1200, "antialias": True,
                                             "copy_view": "none"})
    except Exception as exc:  # noqa: BLE001
        print("offscreen:", exc)
    views = {"back": ([0, 2, 120], 28), "threequarter": ([-78, 18, 95], 28),
             "side": ([120, 4, 0], 28), "close": ([0, 12, 62], 24)}
    for name, (pos, fov) in views.items():
        bbmcp.call("set_camera_angle", {"view": "devil", "position": pos,
                                        "target": [0, 3, 0], "fov": fov,
                                        "projection": "perspective"})
        raw = SHOTS / f"raw_{name}.png"
        bbmcp.shot(str(raw), tool="capture_screenshot",
                   args={"view": "devil", "max_size": 1200})
        composite(raw, SHOTS / f"{name}.png", name)
        print("shot", name)


if __name__ == "__main__":
    main()
