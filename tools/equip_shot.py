"""Equip a cosmetic in-game via chat (clipboard paste), then screenshot."""
import sys
import time

sys.path.insert(0, "tools")
import pc  # noqa: E402


def command(text):
    pc.focus("Minecraft")
    time.sleep(0.4)
    pc.press("t")
    time.sleep(0.8)
    ok = pc.paste_text(text)
    time.sleep(0.4)
    pc.press("enter")
    time.sleep(1.3)
    return ok


if __name__ == "__main__":
    variant = sys.argv[1] if len(sys.argv) > 1 else "seraph_wings"
    out = sys.argv[2] if len(sys.argv) > 2 else "_design/ingame/w_seraph.png"
    print("clipboard", command("/epiccosmetic " + variant))
    pc.focus("Minecraft")
    time.sleep(0.4)
    pc.shot(out)
    print(out)
