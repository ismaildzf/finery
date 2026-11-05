"""Download and inspect the 'spaces' package + gradio_client for ZeroGPU auth."""
import glob
import pathlib
import re
import subprocess
import sys

tmp = pathlib.Path(r"C:\MinecraftModding\tmp_pkgs")
tmp.mkdir(exist_ok=True)

subprocess.run([sys.executable, "-m", "pip", "download", "spaces", "--no-deps", "-d", str(tmp)],
               check=False)

files = glob.glob(str(tmp / "spaces-*"))
print("downloaded:", files)
if not files:
    sys.exit(1)

import zipfile

src_files = {}
p = pathlib.Path(files[0])
if p.suffix == ".whl":
    z = zipfile.ZipFile(p)
    for n in z.namelist():
        if n.endswith(".py"):
            src_files[n] = z.read(n).decode("utf8", "replace")
else:
    import tarfile
    t = tarfile.open(p)
    for m in t.getmembers():
        if m.name.endswith(".py"):
            src_files[m.name] = t.extractfile(m).read().decode("utf8", "replace")

kws = ("authorization", "x-hf", "quota", "get_current_user", "oauth", "user_token", "hf_token")
for n, src in src_files.items():
    hits = []
    for i, line in enumerate(src.splitlines(), 1):
        low = line.lower()
        if any(k in low for k in kws):
            hits.append(f"  {i}: {line.strip()[:170]}")
    if hits:
        print(f"\n=== {n} ===")
        print("\n".join(hits[:40]))

# gradio_client: how is the token attached?
import gradio_client

root = pathlib.Path(gradio_client.__file__).parent
print("\n\n### gradio_client headers usage in", root)
for f in root.rglob("*.py"):
    try:
        src = f.read_text(encoding="utf8", errors="replace")
    except Exception:
        continue
    for i, line in enumerate(src.splitlines(), 1):
        low = line.lower()
        if "hf-authorization" in low or "x-hf" in low or ("authorization" in low and "header" in low):
            print(f"{f.relative_to(root)}:{i}: {line.strip()[:170]}")
