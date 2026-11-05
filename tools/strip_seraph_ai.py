import pathlib

base = pathlib.Path(__file__).resolve().parents[1] / "src" / "main" / "resources" / "assets" / "finery" / "lang"
for name in ("en_us.json", "ar_sa.json"):
    p = base / name
    lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
    kept = [ln for ln in lines if "seraph_ai" not in ln]
    p.write_text("".join(kept), encoding="utf-8")
    print(name, len(lines), "->", len(kept))
