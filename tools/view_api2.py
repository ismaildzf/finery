"""Show exact API signatures of the two candidate spaces (post marshal)."""
import os

from gradio_client import Client

TOKEN = os.environ.get("HF_TOKEN", "")
assert TOKEN.startswith("hf_"), "set HF_TOKEN"

for sid in ["tencent/Hunyuan3D-2.1", "trellis-community/TRELLIS"]:
    print("\n" + "=" * 70)
    try:
        c = Client(sid, token=TOKEN, verbose=False)
        print("== connected:", sid, "->", c.src)
        info = c.view_api(return_format="dict")
        for name, ep in (info.get("named_endpoints") or {}).items():
            if "glb" in name.lower() or "generation" in name.lower() or "export" in name.lower() or "shape" in name.lower():
                print(f"\n--- {name} ---")
                for p in ep.get("parameters", []):
                    print(f"    {p.get('parameter_name')}: default={p.get('parameter_default')!r} type={p.get('python_type', {}).get('type', '?')} required={p.get('parameter_has_default') is False}")
    except Exception as e:  # noqa: BLE001
        print(sid, "FAIL:", type(e).__name__, str(e)[:250])
