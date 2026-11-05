import json
import sys

sys.path.insert(0, "tools")
from bbmcp import call  # noqa: E402

script = (
    "JSON.stringify({"
    "require: typeof require,"
    "process: typeof process,"
    "fs: (typeof require === 'function' ? (function(){ try { return typeof require('fs').readFileSync; } "
    "catch (e) { return 'ERR ' + e.message; } })() : 'none'),"
    "Blockbench: typeof Blockbench,"
    "Texture: typeof Texture,"
    "canvas: (typeof Texture !== 'undefined' && Texture.all.length) ? Texture.all[0].width : null"
    "})"
)
print(call("risky_eval", {"script": script}))
