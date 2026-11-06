"""Download the 1.20.1 asset objects that are still missing, in parallel."""

import hashlib
import json
import os
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = os.path.join(os.environ["APPDATA"], ".minecraft", "assets")
INDEX = os.path.join(ROOT, "indexes", "5.json")
WORKERS = 24


def fetch_object(name, entry):
    digest = entry["hash"]
    target = os.path.join(ROOT, "objects", digest[:2], digest)
    if os.path.exists(target):
        return 0
    url = f"https://resources.download.minecraft.net/{digest[:2]}/{digest}"
    os.makedirs(os.path.dirname(target), exist_ok=True)
    for attempt in range(4):
        try:
            data = urllib.request.urlopen(url, timeout=60).read()
            if hashlib.sha1(data).hexdigest() != digest:
                continue
            tmp = target + ".part"
            open(tmp, "wb").write(data)
            os.replace(tmp, target)
            return len(data)
        except Exception:
            continue
    print("FAILED", name, digest, flush=True)
    return 0


def main():
    index = json.load(open(INDEX, encoding="utf-8"))
    pending = [(n, o) for n, o in index["objects"].items()
               if not os.path.exists(os.path.join(ROOT, "objects", o["hash"][:2], o["hash"]))]
    total = sum(o["size"] for _, o in pending)
    print("pending", len(pending), "bytes", total, flush=True)
    done = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = [pool.submit(fetch_object, n, o) for n, o in pending]
        for future in as_completed(futures):
            done += future.result()
    print("downloaded", done, "of", total, flush=True)


if __name__ == "__main__":
    main()
