"""Equip every wing variant (with verification) and screenshot it."""
import pathlib
import sys
import time

sys.path.insert(0, "tools")
import pc  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOG = ROOT / "run" / "_client.log"


def tail(n=400):
    try:
        lines = LOG.read_text(encoding="utf-8", errors="ignore").splitlines()
        return "\n".join(lines[-n:])
    except OSError:
        return ""


def send(text):
    pc.focus("Minecraft")
    time.sleep(0.35)
    pc.press("t")
    time.sleep(0.75)
    pc.press_many("backspace", 48)     # drop stray characters typed by a held key
    pc.paste_text(text)
    time.sleep(0.25)
    pc.press("enter")
    time.sleep(1.1)


def equip(variant, tries=3):
    marker = "Equipped " + variant
    for attempt in range(tries):
        send("/epiccosmetic " + variant)
        if marker in tail():
            return True
        # recover from a stuck chat / menu
        pc.press("esc")
        time.sleep(0.4)
        pc.press("esc")
        time.sleep(0.6)
    return False


def main():
    variants = sys.argv[1:] or ["seraph_wings", "emberwing", "voidwing", "fae_wings"]
    pc.focus("Minecraft")
    time.sleep(0.4)
    pc.press("f5")
    time.sleep(1.2)
    for v in variants:
        ok = equip(v)
        pc.focus("Minecraft")
        time.sleep(0.9)
        out = ROOT / "_design" / "ingame" / f"n_{v}.png"
        pc.shot(str(out))
        print(("ok   " if ok else "FAIL ") + v)


if __name__ == "__main__":
    main()
