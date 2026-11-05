"""Debug: log local coordinate bounds of every moth quad (fore vs hind)."""
import sys

sys.path.insert(0, r"C:\MinecraftModding\mods\finery")
from PIL import Image                                     # noqa: E402

import wing_v6_preview as w                                # noqa: E402

orig_quad = w.Scene.quad
DBG = {"u": [], "v": [], "w": [], "n": 0}


def spy(self, side, a, b, c, d, ua, ub, uc, ud, cols, angle,
        root_x, root_z, raise_, sweep, full_bright=False, bias=None):
    DBG["n"] += 1
    for p in (a, b, c, d):
        DBG["u"].append(abs(p.u))
        DBG["v"].append(p.v)
        DBG["w"].append(p.w)
    return orig_quad(self, side, a, b, c, d, ua, ub, uc, ud, cols, angle,
                     root_x, root_z, raise_, sweep, full_bright, bias)


w.Scene.quad = spy
tex = Image.new("RGBA", (256, 256))
scene = w.Scene(tex)
w.build_moth(scene, "fae_wings", 0.0, 0.20, 0.30, 0.20, side_only=1)
print("quads:", DBG["n"])
print("|u| range: %.2f .. %.2f" % (min(DBG["u"]), max(DBG["u"])))
print(" v  range: %.2f .. %.2f" % (min(DBG["v"]), max(DBG["v"])))
print(" w  range: %.2f .. %.2f" % (min(DBG["w"]), max(DBG["w"])))

# Now check the same for a fresh spy that separates the fore/hind by their UV zone.
