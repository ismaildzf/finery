"""In-game wing QA: straight-back screenshots + animation frames."""
import sys
import time

sys.path.insert(0, "tools")
import pc  # noqa: E402


def chat(text):
    pc.focus("Minecraft")
    pc.press("t")
    time.sleep(0.4)
    pc.paste_text(text)
    time.sleep(0.3)
    pc.press("enter")
    time.sleep(1.2)


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "wing"
    out = sys.argv[2] if len(sys.argv) > 2 else "_design/ingame"
    variant = sys.argv[3] if len(sys.argv) > 3 else None
    if variant:
        chat("/epiccosmetic " + variant)
    pc.focus("Minecraft")
    time.sleep(0.4)
    # align the body with the camera and get out of any grass
    pc.press("w", hold=0.35)
    time.sleep(0.7)
    pc.shot(f"{out}/{tag}_back.png")
    for i in range(8):
        time.sleep(0.32)
        pc.shot(f"{out}/{tag}_f{i}.png")
    print("saved", out, tag)


if __name__ == "__main__":
    main()
