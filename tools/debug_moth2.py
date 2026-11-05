"""Debug 2: separate the moth's fore/hind quads by UV zone, print bounds and alpha."""
import sys

sys.path.insert(0, r"C:\MinecraftModding\mods\finery")
from PIL import Image                                     # noqa: E402

import wing_v6_preview as w                                # noqa: E402

orig_quad = w.Scene.quad
REC = []


def spy(self, side, a, b, c, d, ua, ub, uc, ud, cols, angle,
        root_x, root_z, raise_, sweep, full_bright=False, bias=None):
    umid = (ua.u + ub.u + uc.u + ud.u) / 4.0
    vmid = (ua.v + ub.v + uc.v + ud.v) / 4.0
    REC.append((umid, vmid,
                min(abs(p.u) for p in (a, b, c, d)), max(abs(p.u) for p in (a, b, c, d)),
                min(p.v for p in (a, b, c, d)), max(p.v for p in (a, b, c, d)),
                min(p.w for p in (a, b, c, d)), max(p.w for p in (a, b, c, d))))
    return orig_quad(self, side, a, b, c, d, ua, ub, uc, ud, cols, angle,
                     root_x, root_z, raise_, sweep, full_bright, bias)


w.Scene.quad = spy
tex = Image.open(r"C:\MinecraftModding\mods\finery\src\main\resources\assets\finery\textures\wings\fae_wings.png").convert("RGBA")
scene = w.Scene(tex)
w.build_moth(scene, "fae_wings", 0.0, 0.20, 0.30, 0.20, side_only=1)
print("fore zone:", w.ZONES_FAE["FORE"], " hind zone:", w.ZONES_FAE["HIND"])
groups = {"FORE": [], "HIND": [], "OTHER": []}
for rec in REC:
    umid, vmid = rec[0], rec[1]
    if 0 <= vmid < 12:
        groups["FORE"].append(rec)
    elif 13 <= vmid < 25:
        groups["HIND"].append(rec)
    else:
        groups["OTHER"].append(rec)
for name, recs in groups.items():
    if not recs:
        print(name, "none")
        continue
    print(name, "quads:", len(recs),
          "|u| %.2f..%.2f" % (min(r[2] for r in recs), max(r[3] for r in recs)),
          "v %.2f..%.2f" % (min(r[4] for r in recs), max(r[5] for r in recs)),
          "w %.2f..%.2f" % (min(r[6] for r in recs), max(r[7] for r in recs)))

# alpha coverage of each zone in the texture
px = tex.load()
tw, th = tex.size
for name, zone in w.ZONES_FAE.items():
    if name not in ("FORE", "HIND"):
        continue
    x0, y0, x1, y1 = zone
    n = 0
    tot = 0
    for xx in range(int(x0 * tw / 64.0), int(x1 * tw / 64.0)):
        for yy in range(int(y0 * th / 64.0), int(y1 * th / 64.0)):
            tot += 1
            if px[xx, yy][3] > 24:
                n += 1
    print("zone", name, "opaque %d/%d" % (n, tot))
