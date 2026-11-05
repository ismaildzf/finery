import json
import sys

sys.path.insert(0, "tools")
from bbmcp import connect, rpc  # noqa: E402

name = sys.argv[1]
connect()
tools = {t["name"]: t for t in rpc("tools/list").get("result", {}).get("tools", [])}
tool = tools[name]
print(json.dumps(tool.get("inputSchema", {}), ensure_ascii=False, indent=1)[:12000])
