"""Silhouette overlay: reference wing vs rendered wing, aligned by head width.

Usage: python tools/silhouette_compare.py <reference.png> <render.png> <out.png>
"""
import sys

import cv2
import numpy as np
from PIL import Image


def head_box(img):
    r, g, b = img[..., 0].astype(int), img[..., 1].astype(int), img[..., 2].astype(int)
    m = ((r - b) > 9) & ((r - b) < 40) & (r > 20) & (r < 100) & \
        (g > 15) & (g < 80) & (b < 60)
    h, w = img.shape[:2]
    m[:int(h * 0.08)] = False
    m[:, :int(w * 0.28)] = False
    m[:, int(w * 0.72):] = False
    m[int(h * 0.55):] = False
    m = (m.astype(np.uint8) * 255)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    n, labels, stats, cents = cv2.connectedComponentsWithStats(m, 8)
    if n < 2:
        raise SystemExit("no head found")
    i = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    x, y, bw, bh, area = stats[i]
    return x, y, bw, bh


def wing_mask(img, cx, top, unit):
    r, g, b = img[..., 0].astype(int), img[..., 1].astype(int), img[..., 2].astype(int)
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    m = ((mx - mn) <= 14) & (mx < 150)
    h, w = img.shape[:2]
    x0 = max(0, int(cx - 21 * unit))
    x1 = min(w, int(cx + 21 * unit))
    y0 = max(0, int(top - 7 * unit))
    y1 = min(h, int(top + 30 * unit))
    out = np.zeros((h, w), np.uint8)
    out[y0:y1, x0:x1] = m[y0:y1, x0:x1]
    n, labels, stats, _ = cv2.connectedComponentsWithStats(out, 8)
    keep = np.zeros_like(out)
    if n > 1:
        big = stats[1:, cv2.CC_STAT_AREA].max()
        for i in range(1, n):
            if stats[i, cv2.CC_STAT_AREA] >= max(200, big * 0.015):
                keep[labels == i] = 1
    return keep


def main(ref_path, render_path, out_path):
    ref = np.asarray(Image.open(ref_path).convert("RGB"))
    new = np.asarray(Image.open(render_path).convert("RGB"))
    rx, ry, rw, rh = head_box(ref)
    nx, ny, nw, nh = head_box(new)
    print("ref head", rx, ry, rw, rh, "new head", nx, ny, nw, nh)

    ref_unit = rw / 8.0
    new_unit = nw / 8.0
    scale = new_unit / ref_unit
    unit = new_unit
    W = H = 1500
    cx_dst, top_dst = 750, 220

    def place(img, factor, hcx, htop):
        im = Image.fromarray(img)
        if factor != 1.0:
            im = im.resize((int(im.width * factor), int(im.height * factor)),
                           Image.LANCZOS)
        canvas = Image.new("RGB", (W, H), (90, 140, 100))
        canvas.paste(im, (int(cx_dst - hcx * factor), int(top_dst - htop * factor)))
        return np.asarray(canvas)

    ref2 = place(ref, scale, rx + rw / 2, ry)
    new2 = place(new, 1.0, nx + nw / 2, ny)
    mref = wing_mask(ref2, cx_dst, top_dst, unit)
    mnew = wing_mask(new2, cx_dst, top_dst, unit)
    ncx, ntop = cx_dst, top_dst

    ys, xs = np.where((mref | mnew) > 0)
    pad = 24
    x0, y0 = max(0, xs.min() - pad), max(0, ys.min() - pad)
    x1, y1 = min(W, xs.max() + pad), min(H, ys.max() + pad)
    mref, mnew = mref[y0:y1, x0:x1], mnew[y0:y1, x0:x1]

    out = np.zeros((*mref.shape, 3), np.uint8)
    out[...] = (90, 140, 100)
    out[mref > 0] = (220, 60, 60)
    out[mnew > 0] = (60, 120, 230)
    both = (mref > 0) & (mnew > 0)
    out[both] = (235, 235, 235)
    Image.fromarray(out).save(out_path)

    inter = int(both.sum())
    union = int(((mref > 0) | (mnew > 0)).sum())
    print("IoU", round(inter / union, 3))
    for name, m in (("ref", mref), ("new", mnew)):
        ys2, xs2 = np.where(m > 0)
        # coordinates in head units, origin = head center x / head top y
        print(name,
              "span", round((xs2.max() - xs2.min()) / new_unit, 1),
              "xL", round((xs2.min() + x0 - ncx) / new_unit, 1),
              "xR", round((xs2.max() + x0 - ncx) / new_unit, 1),
              "top", round((ys2.min() + y0 - ntop) / new_unit, 1),
              "bot", round((ys2.max() + y0 - ntop) / new_unit, 1),
              "area", int(m.sum()))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
