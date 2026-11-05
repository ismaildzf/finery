"""Drive the dev showcase file and capture every wing variant."""
import pathlib
import sys
import time

sys.path.insert(0, "tools")
import pc  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
FILE = ROOT / "epic_showcase.txt"
VARIANTS = ["seraph_wings", "emberwing", "voidwing", "fae_wings"]


def show(variant, wait=1.6):
    FILE.write_text(variant, encoding="utf-8")
    time.sleep(wait)


def main():
    pc.focus("Minecraft")
    time.sleep(0.5)
    pc.press("f5")
    time.sleep(1.2)
    for v in VARIANTS:
        show(v)
        pc.focus("Minecraft")
        time.sleep(0.6)
        pc.shot(str(ROOT / "_design" / "ingame" / f"n_{v}.png"))
        print("shot", v)


if __name__ == "__main__":
    main()
