"""Push the generated wing mesh into Blockbench, apply per-face UVs, screenshot."""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import bbmcp  # noqa: E402

PAYLOAD = ROOT / "_design" / "bb_payload.json"
ATLAS = ROOT / "src" / "main" / "resources" / "assets" / "finery" / "textures" / "wings" / "seraph_wings.png"
SHOTS = ROOT / "_design" / "bb"
SHOTS.mkdir(exist_ok=True)


def main():
    data = json.loads(PAYLOAD.read_text(encoding="utf-8"))
    verts = data["vertices"]
    faces = data["faces"]
    uvs = data["uvs"]

    n = len(verts)
    all_verts = verts + [[-x, y, z] for x, y, z in verts]
    all_faces = faces + [[a + n, d + n, c + n, b + n] for a, b, c, d in faces]
    all_uvs = uvs + uvs

    print("project:", bbmcp.call("create_project", {"name": "EpicWings", "format": "free"}))
    bbmcp.call("create_texture", {
        "name": "wings", "width": data["atlas"][0], "height": data["atlas"][1],
        "uv_width": data["atlas"][0], "uv_height": data["atlas"][1],
        "data": str(ATLAS), "render_sides": "double",
    })
    bbmcp.call("place_mesh", {
        "elements": [{"name": "wing", "position": [0, 0, 0],
                      "vertices": all_verts, "faces": all_faces}],
        "texture": "wings",
    })

    script = """
    const mesh = Mesh.all.find(m => m.name === 'wing') || Mesh.all[Mesh.all.length - 1];
    const uvs = %s;
    const faces = Object.values(mesh.faces);
    let done = 0;
    faces.forEach((f, i) => {
        const keys = Object.keys(f.uv || {});
        const vk = keys.length ? keys : f.vertices.slice();
        if (!uvs[i]) return;
        f.uv = {};
        vk.forEach((k, j) => { f.uv[k] = uvs[i][j]; });
        done++;
    });
    mesh.preview_controller.updateUV(mesh);
    Canvas.updateAll();
    JSON.stringify({faces: faces.length, updated: done, sample: Object.entries(mesh.faces)[0][1].uv});
    """ % json.dumps(all_uvs)
    print("uv:", bbmcp.call("risky_eval", {"code": script}))

    for name, pos, zoom in (("back", [0, 0, 70], 1.35),
                            ("threequarter", [-45, -18, 55], 1.1),
                            ("side", [70, 0, 0], 1.35)):
        try:
            bbmcp.shot(str(SHOTS / f"{name}.png"), tool="set_camera_angle", args={
                "position": pos, "target": [0, 0, 1.0],
                "projection": "orthographic", "zoom": zoom, "max_size": 1100,
            })
            print("shot", name)
        except Exception as exc:  # noqa: BLE001
            print("shot failed", name, exc)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
