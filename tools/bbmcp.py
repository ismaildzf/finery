"""Minimal MCP client for the Blockbench MCP plugin (HTTP transport).

Importable helpers (avoid shell quoting):
    from bbmcp import call, shot
    res = call("place_cube", {...})

CLI:
    python tools/bbmcp.py list
    python tools/bbmcp.py call <tool> <args.json> [out.png]
    python tools/bbmcp.py shot <out.png> [tool-args.json]
"""
import base64
import json
import sys
import urllib.error
import urllib.request

URL = "http://127.0.0.1:3000/bb-mcp"
_session = {"id": None, "proto": "2024-11-05", "ready": False}


def _post(payload, session=None):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(URL, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json, text/event-stream")
    if session:
        req.add_header("Mcp-Session-Id", session)
        req.add_header("MCP-Protocol-Version", _session["proto"])
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            sid = r.headers.get("mcp-session-id")
            if sid:
                _session["id"] = sid
            return r.read().decode("utf-8", "replace"), r.headers.get("content-type", "")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')}") from None


def _parse(raw, ctype):
    if "text/event-stream" in ctype:
        out = []
        for line in raw.splitlines():
            if line.startswith("data:"):
                chunk = line[5:].strip()
                if chunk and chunk != "[DONE]":
                    out.append(json.loads(chunk))
        return out[-1] if out else {}
    return json.loads(raw) if raw.strip() else {}


def rpc(method, params=None, notify=False):
    payload = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        payload["params"] = params
    if not notify:
        payload["id"] = 1
    raw, ctype = _post(payload, _session["id"])
    return {} if notify else _parse(raw, ctype)


def connect():
    if _session["ready"]:
        return
    res = rpc("initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "finery-agent", "version": "1.0"},
    })
    _session["proto"] = res.get("result", {}).get("protocolVersion", _session["proto"])
    rpc("notifications/initialized", notify=True)
    _session["ready"] = True


def call(tool, args=None):
    """Call a tool and return its structured payload (falling back to parsed text)."""
    connect()
    res = rpc("tools/call", {"name": tool, "arguments": args or {}})
    if "error" in res:
        raise RuntimeError(json.dumps(res["error"], ensure_ascii=False))
    result = res.get("result", {})
    if result.get("isError"):
        text = " ".join(c.get("text", "") for c in result.get("content", []) if c.get("type") == "text")
        raise RuntimeError(text)
    if "structuredContent" in result:
        return result["structuredContent"]
    content = result.get("content", [])
    if len(content) == 1 and content[0].get("type") == "text":
        try:
            return json.loads(content[0].get("text", ""))
        except Exception:
            return content[0].get("text")
    return result


def images(result):
    """Base64 image payloads contained in a raw tool result."""
    out = []
    for item in result.get("content", []) if isinstance(result, dict) else []:
        if item.get("type") == "image":
            out.append(base64.b64decode(item.get("data", "")))
    return out


def shot(path, tool="capture_screenshot", args=None):
    connect()
    res = rpc("tools/call", {"name": tool, "arguments": args or {}})
    result = res.get("result", {})
    payloads = images(result)
    if not payloads:
        raise RuntimeError("no image in response: " + json.dumps(result)[:500])
    with open(path, "wb") as fh:
        fh.write(payloads[-1])
    return path


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd = sys.argv[1]
    if cmd == "list":
        connect()
        for tool in rpc("tools/list").get("result", {}).get("tools", []):
            print("-", tool["name"], "|", (tool.get("description") or "").split("\n")[0][:110])
    elif cmd == "call":
        args = json.load(open(sys.argv[3], encoding="utf-8")) if len(sys.argv) > 3 else {}
        print(json.dumps(call(sys.argv[2], args), ensure_ascii=False, indent=2)[:6000])
    elif cmd == "shot":
        print(shot(sys.argv[2], args=json.load(open(sys.argv[3], encoding="utf-8")) if len(sys.argv) > 3 else {}))
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
