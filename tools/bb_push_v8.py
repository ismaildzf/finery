"""Push the seraph_v8 feather mesh into the running Blockbench and capture views."""
import base64
import io
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import bbmcp  # noqa: E402
import seraph_v8 as v8  # noqa: E402

SHOTS = ROOT / "_design" / "bb_v8"
TEX = ROOT / "_design" / "seraph_atlas_bb.png"


def build_payload():
    atlas, rects = v8.build_atlas()
    feathers = v8.layout(rects)
    quads = v8.build_model(feathers, rects)
    verts, faces, uvs = [], [], []
    for verts4, uv4, _tint in quads:
        base = len(verts)
        verts += [[float(c) for c in p] for p in verts4]
        faces.append([base, base + 1, base + 2, base + 3])
        uvs.append([[float(u) / 2.0, 512.0 - float(v) / 2.0] for u, v in uv4])

    small = atlas.resize((512, 512))
    small.save(TEX)
    buf = io.BytesIO()
    small.save(buf, format="PNG")
    data_url = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")

    xs = [p[0] for p in verts]
    ys = [p[1] for p in verts]
    zs = [p[2] for p in verts]
    cx = (min(xs) + max(xs)) * 0.5
    cy = (min(ys) + max(ys)) * 0.5
    cz = (min(zs) + max(zs)) * 0.5
    verts = [[p[0] - cx, p[1] - cy, p[2] - cz] for p in verts]
    print(f"mesh {len(verts)} verts, {len(faces)} quads, span "
          f"{max(xs)-min(xs):.1f} x {max(ys)-min(ys):.1f} x {max(zs)-min(zs):.1f}, "
          f"tex {len(data_url)//1024} KB")
    return verts, faces, uvs, data_url


def push(verts, faces, uvs, data_url):
    payload = {"verts": verts, "faces": faces, "uvs": uvs}
    b64 = data_url.split(",", 1)[1].replace("/", "~")
    code = """
(async () => {
  const old = Mesh.all.filter(m => ['seraph_v8', 't1', 'mini', 'cube'].indexOf(m.name) !== -1);
  old.forEach(m => { if (m.remove) m.remove(); });
  Texture.all.filter(t => ['seraph_feathers', 'tt'].indexOf(t.name) !== -1).forEach(t => { if (t.remove) t.remove(); });
  const b64 = %s.split('~').join('/');
  const tex = new Texture({name: 'seraph_feathers', width: 512, height: 512,
                           uv_width: 512, uv_height: 512}).fromDataURL('data:image/png;base64,' + b64);
  tex.render_sides = 'double';
  await new Promise(r => setTimeout(r, 700));
  if (Texture.all.indexOf(tex) === -1) tex.add();
  tex.updateMaterial();
  const data = JSON.parse(%s);
  const mesh = new Mesh({name: 'seraph_v8', vertices: {}}).init();
  const keys = mesh.addVertices(...data.verts);
  const faceList = data.faces.map((f, i) => {
    const face = new MeshFace(mesh, {vertices: f.map(j => keys[j])});
    face.uv = {};
    face.texture = tex.uuid;
    f.forEach((j, k) => { face.uv[keys[j]] = data.uvs[i][k]; });
    return face;
  });
  mesh.addFaces(...faceList);
  Canvas.updateAll();
  return JSON.stringify({mesh: mesh.name, verts: Object.keys(mesh.vertices).length,
                         faces: Object.keys(mesh.faces).length, tex: tex.name,
                         loaded: tex.width + 'x' + tex.height, texCount: Texture.all.length});
})()
""" % (json.dumps(b64), json.dumps(json.dumps(payload)))
    print("push:", bbmcp.call("risky_eval", {"code": code}))


def camera(pos):
    code = """
(() => {
  const p = Preview.selected;
  p.camPers.position.set(%s);
  p.controls.target.set(0, 0, 0);
  p.camPers.fov = 30;
  p.camPers.updateProjectionMatrix();
  p.controls.update();
  p.render();
  Canvas.updateAll();
  return 'ok';
})()
""" % ", ".join(str(float(c)) for c in pos)
    bbmcp.call("risky_eval", {"code": code})


def main():
    SHOTS.mkdir(parents=True, exist_ok=True)
    verts, faces, uvs, data_url = build_payload()
    push(verts, faces, uvs, data_url)
    views = {"back": (0, 0, 150), "threequarter": (-95, 25, 115),
             "side": (150, 0, 0), "top": (0, 150, 1)}
    for name, pos in views.items():
        camera(pos)
        bbmcp.shot(str(SHOTS / f"{name}.png"), tool="capture_app_screenshot",
                   args={"max_size": 1400})
        print("shot", name)


if __name__ == "__main__":
    main()
