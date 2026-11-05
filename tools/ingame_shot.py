"""Chat command + third-person screenshot helper for in-game wing checks."""
import sys
import time

import pc


def cmd(text):
    pc.focus("Minecraft")
    pc.press("t")
    time.sleep(0.30)
    pc.type_raw(text)
    time.sleep(0.25)
    pc.press("enter")
    time.sleep(0.8)


def main():
    variant = sys.argv[1] if len(sys.argv) > 1 else "seraph_wings"
    out = sys.argv[2] if len(sys.argv) > 2 else "_design/ingame/w1.png"
    cmd("/epiccosmetic " + variant)
    pc.focus("Minecraft")
    pc.press("f5")
    time.sleep(1.2)
    pc.shot(out)
    print(out)


if __name__ == "__main__":
    main()
