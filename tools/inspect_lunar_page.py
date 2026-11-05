"""Dump image URLs found in a Lunar store product page (diagnostic)."""
import re
import urllib.request

URL = "https://store.lunarclient.com/products/7009727/angel-wings-2025-white"
req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
print("html len", len(html))

urls = re.findall(r"https?://[^\s\"'<>\\]+?\.(?:png|jpg|jpeg|webp)", html)
uniq = sorted(set(urls))
print("image urls:", len(uniq))
for u in uniq[:40]:
    print("  ", u[:180])

# also look for any packages/ or webstoreassets mentions
for m in sorted(set(re.findall(r"[A-Za-z0-9_./:-]*(?:packages|webstoreassets)[A-Za-z0-9_./:-]*", html)))[:30]:
    print("M:", m[:180])
