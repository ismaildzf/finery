"""Find package asset paths inside a Lunar store product page (diagnostic)."""
import re
import urllib.request

URL = "https://store.lunarclient.com/products/7009727/angel-wings-2025-white"
req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")

pats = sorted(set(re.findall(r"[A-Za-z0-9_\-./]*packages/[A-Za-z0-9_\-./]+", html)))
print("packages paths:", len(pats))
for p in pats[:60]:
    print("  ", p[:180])

# Look at __NEXT_DATA__ style keys around images
for key in ("image", "gallery", "asset", "thumbnail", "media"):
    idxs = [m.start() for m in re.finditer(key, html)][:4]
    for i in idxs:
        snippet = html[max(0, i - 60): i + 160].replace("\n", " ")
        print("KEY", key, "::", snippet[:200])
        break
