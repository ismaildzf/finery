"""Download Lunar Client store preview stills (visual reference only — never shipped).

Product pages host MP4 previews plus a few PNG stills on the webstore CDN.
Cloudflare's media transform can extract a frame from the MP4 as an image,
which gives us a usable reference screenshot.

Saves files into %TEMP%/opencode/lunar_refs.
"""
import os
import re
import urllib.parse
import urllib.request

OUTDIR = r"C:\Users\Administrator\AppData\Local\Temp\opencode\lunar_refs"
PAGES = {
    "angel2025w": "https://store.lunarclient.com/products/7009727/angel-wings-2025-white",
    "angelwhite": "https://store.lunarclient.com/products/6792802/angel-wings-white",
    "demonblack": "https://store.lunarclient.com/products/7009731/demon-wings-black",
    "demonred": "https://store.lunarclient.com/products/7009732/demon-wings-red",
    "dragonblack": "https://store.lunarclient.com/products/7009700/dragon-wings-black",
    "devilwings": "https://store.lunarclient.com/products/7713883/devil-wings",
    "crystal": "https://store.lunarclient.com/products/7009746/crystal-wings",
}
UA = {"User-Agent": "Mozilla/5.0"}
PKG_RE = re.compile(r"//webstoreassets\.lunarclientprod\.com/packages/([0-9a-f]{32})\.(png|mp4)")


def download(url: str, path: str) -> int:
    req = urllib.request.Request(url, headers=UA)
    data = urllib.request.urlopen(req, timeout=90).read()
    with open(path, "wb") as fh:
        fh.write(data)
    return len(data)


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    for key, url in PAGES.items():
        try:
            req = urllib.request.Request(url, headers=UA)
            html = urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "ignore")
        except Exception as exc:                    # noqa: BLE001
            print(key, "FETCH ERR", exc)
            continue
        hits = []
        seen = set()
        for m in PKG_RE.finditer(html):
            h, ext = m.group(1), m.group(2)
            if (h, ext) in seen:
                continue
            seen.add((h, ext))
            hits.append((h, ext))
        print(key, "assets:", len(hits))
        idx = 0
        for h, ext in hits:
            if ext == "png":
                base = f"https://webstoreassets.lunarclientprod.com/packages/{h}.png"
            else:
                base = ("https://webstoreassets.lunarclientprod.com/cdn-cgi/media/"
                        f"mode=frame,width=1024,height=1024,fit=contain/packages/{h}.mp4")
            name = f"{key}_{idx:02d}.png"
            try:
                size = download(base, os.path.join(OUTDIR, name))
                print("   saved", name, size // 1024, "KB")
                idx += 1
            except Exception as exc:                # noqa: BLE001
                print("   err", name, exc)


if __name__ == "__main__":
    main()
