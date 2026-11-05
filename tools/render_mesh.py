"""Offline software renderer for wing meshes -> multi-view PNG sheet.

No GPU / no display needed (pure numpy painter's algorithm).

Usage:
  python render_mesh.py <mesh.glb> [out.png] [--size 512]
"""
import argparse
import pathlib
import sys

import numpy as np
import trimesh
from PIL import Image, ImageDraw

BG = (24, 26, 30)
LIGHT = np.array([0.35, 0.55, 0.75])


def rot_x(deg):
    a = np.radians(deg)
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def rot_y(deg):
    a = np.radians(deg)
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def rot_z(deg):
    a = np.radians(deg)
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def load_mesh(glb):
    loaded = trimesh.load(str(glb), process=False)
    mesh = loaded.to_geometry() if isinstance(loaded, trimesh.Scene) else loaded
    verts = np.asarray(mesh.vertices, dtype=np.float64)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    uv = getattr(mesh.visual, "uv", None)
    uv = np.asarray(uv, dtype=np.float64) if uv is not None else None
    tex = None
    mat = getattr(mesh.visual, "material", None)
    if mat is not None:
        img = getattr(mat, "image", None)
        if img is not None:
            tex = np.asarray(img.convert("RGBA"), dtype=np.float64)
    if tex is None:
        base = pathlib.Path(str(glb)).with_name(pathlib.Path(glb).stem)
        for suffix in ("_tex0.png", "_tex0.jpg", "_tex.png"):
            p = pathlib.Path(str(base) + suffix)
            if p.exists():
                tex = np.asarray(Image.open(p).convert("RGBA"), dtype=np.float64)
                break
    return verts, faces, uv, tex


def render_view(verts, faces, uv, tex, R, size, camera_front=True, alpha=False,
                shade_lo=0.62, shade_hi=0.38, colors=None):
    v = verts @ R.T
    lo, hi = v.min(0), v.max(0)
    span = max(float(hi[0] - lo[0]), float(hi[1] - lo[1]))
    span = span if span > 1e-9 else 1.0
    scale = size * 0.88 / span
    cx, cy = (lo[0] + hi[0]) * 0.5, (lo[1] + hi[1]) * 0.5
    X = (v[:, 0] - cx) * scale + size * 0.5
    Y = size * 0.5 - (v[:, 1] - cy) * scale
    Z = v[:, 2]

    if alpha:
        img = np.zeros((size, size, 4), dtype=np.float64)
    else:
        img = np.empty((size, size, 3), dtype=np.float64)
        img[:] = BG

    tv = v[faces]
    n = np.cross(tv[:, 1] - tv[:, 0], tv[:, 2] - tv[:, 0])
    ln = np.linalg.norm(n, axis=1)
    ln[ln == 0] = 1.0
    n = n / ln[:, None]
    l = LIGHT / np.linalg.norm(LIGHT)
    shade = shade_lo + shade_hi * np.abs(n @ l)

    fz = Z[faces].mean(axis=1)
    order = np.argsort(fz) if camera_front else np.argsort(-fz)
    fcol = None
    if colors is not None:
        fcol = np.asarray(colors, float)[faces].mean(axis=1)

    for i in order:
        f = faces[i]
        x, y = X[f], Y[f]
        minx = max(int(np.floor(x.min())), 0)
        maxx = min(int(np.ceil(x.max())), size - 1)
        miny = max(int(np.floor(y.min())), 0)
        maxy = min(int(np.ceil(y.max())), size - 1)
        if minx > maxx or miny > maxy:
            continue
        d = (y[1] - y[2]) * (x[0] - x[2]) + (x[2] - x[1]) * (y[0] - y[2])
        if abs(d) < 1e-9:
            continue
        gx, gy = np.meshgrid(np.arange(minx, maxx + 1) + 0.5,
                             np.arange(miny, maxy + 1) + 0.5)
        w0 = ((y[1] - y[2]) * (gx - x[2]) + (x[2] - x[1]) * (gy - y[2])) / d
        w1 = ((y[2] - y[0]) * (gx - x[2]) + (x[0] - x[2]) * (gy - y[2])) / d
        w2 = 1.0 - w0 - w1
        m = (w0 >= -1e-9) & (w1 >= -1e-9) & (w2 >= -1e-9)
        if not m.any():
            continue
        if uv is not None:
            u = (w0 * uv[f[0], 0] + w1 * uv[f[1], 0] + w2 * uv[f[2], 0]) % 1.0
            vv = (w0 * uv[f[0], 1] + w1 * uv[f[1], 1] + w2 * uv[f[2], 1]) % 1.0
            ti = np.clip((u * (tex.shape[1] - 1)).astype(np.int32), 0, tex.shape[1] - 1)
            tj = np.clip((vv * (tex.shape[0] - 1)).astype(np.int32), 0, tex.shape[0] - 1)
            col = tex[tj, ti, :3]
            if tex.shape[2] == 4:
                keep = tex[tj, ti, 3] >= 128.0
                if not keep.any():
                    continue
                m = m & keep
        else:
            col = np.full((gx.shape[0], gx.shape[1], 3), 200.0)
        if fcol is not None:
            col = col * fcol[i]
        sub = img[miny:maxy + 1, minx:maxx + 1]
        if alpha:
            rgb = col[m] * shade[i]
            a = np.full((rgb.shape[0], 1), 255.0)
            sub[m] = np.concatenate([rgb, a], axis=1)
        else:
            sub[m] = col[m] * shade[i]
    return np.clip(img, 0, 255).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("glb")
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--size", type=int, default=512)
    args = ap.parse_args()

    glb = pathlib.Path(args.glb)
    out = pathlib.Path(args.out) if args.out else glb.with_name(glb.stem + "_views.png")
    size = args.size

    verts, faces, uv, tex = load_mesh(glb)
    print(f"mesh: {len(verts)} verts, {len(faces)} faces, uv={'yes' if uv is not None else 'no'}, "
          f"tex={None if tex is None else tex.shape}")

    views = [
        ("back (x,y)", np.eye(3), True),
        ("front (mirrored)", rot_y(180) @ np.eye(3), True),
        ("side", rot_y(90), True),
        ("top", rot_x(-90), True),
        ("3/4", rot_y(-35) @ rot_x(-12), True),
        ("3/4 low", rot_y(40) @ rot_x(18), True),
    ]
    cols = 3
    rows = (len(views) + cols - 1) // cols
    sheet = Image.new("RGB", (size * cols, size * rows + 28 * rows), (18, 19, 22))
    d = ImageDraw.Draw(sheet)
    for idx, (name, R, cam) in enumerate(views):
        img = render_view(verts, faces, uv, tex, R, size, cam)
        cx = (idx % cols) * size
        cy = (idx // cols) * (size + 28)
        sheet.paste(Image.fromarray(img), (cx, cy + 28))
        d.text((cx + 10, cy + 8), name, fill=(235, 230, 210))
        print("rendered", name)

    sheet.save(out)
    print("saved:", out)


if __name__ == "__main__":
    main()
