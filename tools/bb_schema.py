import json
import sys

sys.path.insert(0, "tools")
from bbmcp import connect, rpc  # noqa: E402

wanted = sys.argv[1:] or [
    "risky_eval", "create_project", "create_texture", "place_cube", "add_group",
    "modify_cube", "set_cube_uv", "capture_screenshot", "export_model", "list_outline",
]
connect()
tools = {t["name"]: t for t in rpc("tools/list").get("result", {}).get("tools", [])}
for name in wanted:
    tool = tools.get(name)
    if not tool:
        print(f"### {name}: MISSING")
        continue
    print(f"### {name}: {(tool.get('description') or '').strip()[:300]}")
    schema = tool.get("inputSchema", {})
    props = schema.get("properties", {})
    for key, spec in props.items():
        typ = spec.get("type", "?")
        desc = (spec.get("description") or "").replace("\n", " ")[:90]
        default = spec.get("default")
        print(f"    {key}: {typ} default={default!r} :: {desc}")
    print("    required:", schema.get("required"))
    print()
