"""Lift the four near-black capes out of the mud and tame Zephyr's blown highlights.

Applies the same curve to the in-world sheet and the 32px inventory icon so both stay in sync.
Run from the mod root; originals are copied to dev-backups/capes-pre-contrast/ first.
"""
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "src/main/resources/assets/finery/textures/cape"
ICON = ROOT / "src/main/resources/assets/finery/textures/item"
BACKUP = ROOT / "dev-backups/capes-pre-contrast"

# gamma, contrast around mid grey, saturation
DARK = (0.62, 1.15, 1.18)
CAPES = {
    "void": DARK,
    "warden": DARK,
    "wither": DARK,
    "dragon": (0.60, 1.18, 1.20),
    "enchanter": (0.78, 1.12, 1.12),
}


def curve(rgb: np.ndarray, gamma: float, contrast: float, saturation: float) -> np.ndarray:
    x = rgb.astype(np.float32) / 255.0
    x = np.power(x, gamma)
    x = (x - 0.5) * contrast + 0.5
    x = np.clip(x, 0.0, 1.0) * 255.0
    out = Image.fromarray(x.astype(np.uint8), "RGB")
    out = ImageEnhance.Color(out).enhance(saturation)
    return np.array(out)


def tame_highlights(rgb: np.ndarray) -> np.ndarray:
    x = rgb.astype(np.float32) / 255.0
    knee = 0.80
    x = np.where(x > knee, knee + (x - knee) * 0.45, x)
    x = np.clip((x - 0.5) * 1.06 + 0.5, 0.0, 1.0) * 255.0
    out = Image.fromarray(x.astype(np.uint8), "RGB")
    out = ImageEnhance.Color(out).enhance(1.10)
    return np.array(out)


def punch(name: str, tex: bool) -> None:
    folder = TEX if tex else ICON
    path = folder / (f"{name}.png" if tex else f"{name}_cape.png")
    img = Image.open(path).convert("RGBA")
    arr = np.array(img)
    mask = arr[:, :, 3] > 0
    if name == "breeze":
        changed = tame_highlights(arr[:, :, :3])
    else:
        changed = curve(arr[:, :, :3], *CAPES[name])
    arr[:, :, :3][mask] = changed[mask]
    Image.fromarray(arr, "RGBA").save(path, optimize=True)

    stats = arr[mask][:, :3].astype(float)
    print(f"{'cape' if tex else 'icon'} {name:10s} lum={stats.mean():5.1f} sd={stats.std():5.1f}")


if __name__ == "__main__":
    BACKUP.mkdir(parents=True, exist_ok=True)
    for name in list(CAPES) + ["breeze"]:
        shutil.copy2(TEX / f"{name}.png", BACKUP / f"cape_{name}.png")
        shutil.copy2(ICON / f"{name}_cape.png", BACKUP / f"icon_{name}_cape.png")
        punch(name, tex=True)
        punch(name, tex=False)
