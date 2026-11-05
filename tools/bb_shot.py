import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import bbmcp  # noqa: E402

SHOTS = ROOT / "_design" / "bb"
SHOTS.mkdir(exist_ok=True)

VIEWS = [
    ("back", [0, 0, 70], [0, 0, 1], 0.27),
    ("threequarter", [-40, -16, 55], [0, 0, 1], 0.24),
    ("side", [70, 0, 0], [0, 0, 1], 0.28),
    ("tip", [-16, -22, 26], [8, -4, 1], 0.55),
]

for name, pos, target, zoom in VIEWS:
    try:
        bbmcp.shot(str(SHOTS / f"{name}.png"), tool="set_camera_angle", args={
            "position": pos, "target": target, "projection": "orthographic",
            "zoom": zoom, "max_size": 1100,
        })
        print("shot", name)
    except Exception as exc:  # noqa: BLE001
        print("fail", name, exc)
