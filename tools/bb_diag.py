import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import bbmcp  # noqa: E402

code = """
const t = Texture.all[0];
const mesh = Mesh.all[0];
mesh.preview_controller.updateUV(mesh);
const f = Object.values(mesh.faces)[0];
JSON.stringify({
  tex: {name: t.name, w: t.width, h: t.height, uw: t.uv_width, uh: t.uv_height,
        canvas: !!t.canvas, px: t.ctx.getImageData(10, 10, 1, 1).data.join(',')},
  mesh: {name: mesh.name, verts: mesh.vertices.length, faces: Object.keys(mesh.faces).length,
         uv_size: mesh.uv_size, first_uv: f.uv, first_verts: f.vertices},
  camera: (() => { const c = Project.active; return 'ok'; })(),
  visible: mesh.visibility
});
"""
print(json.dumps(bbmcp.call("risky_eval", {"code": code}), indent=1)[:3000])
