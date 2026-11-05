"""Extract texture + JSON info from a GLB by parsing its container directly."""
import json
import pathlib
import struct
import sys

p = pathlib.Path(sys.argv[1] if len(sys.argv) > 1
                 else r"C:\MinecraftModding\mods\finery\_ai3d\hy21_gen.glb")
data = p.read_bytes()
magic, version, length = struct.unpack_from("<III", data, 0)
print("magic ok:", magic == 0x46546C67, "version:", version, "length:", length, "file:", len(data))

chunks = []
off = 12
while off < length:
    clen, ctype = struct.unpack_from("<II", data, off)
    chunks.append((ctype, off + 8, clen))
    off += 8 + clen
print("chunks:", [(hex(c[0]), c[2]) for c in chunks])

j = json.loads(data[[c for c in chunks if c[0] == 0x4E4F534A][0][1]:][: [c for c in chunks if c[0] == 0x4E4F534A][0][2]])
print("meshes:", len(j.get("meshes", [])))
print("materials:", json.dumps(j.get("materials"), indent=1)[:600])
print("images:", json.dumps(j.get("images"), indent=1)[:400])
print("textures:", json.dumps(j.get("textures"), indent=1)[:400])
print("nodes:", json.dumps(j.get("nodes"), indent=1)[:400])

bin_chunks = [c for c in chunks if c[0] == 0x004E4942]
if j.get("images"):
    import base64
    for idx, img in enumerate(j["images"]):
        uri = img.get("uri") or ""
        if uri.startswith("data:") and "base64," in uri:
            blob = base64.b64decode(uri.split("base64,", 1)[1])
            ext = ".jpg" if "jpeg" in uri.split(";")[0] else ".png"
            out = p.with_name(p.stem + f"_tex{idx}{ext}")
            out.write_bytes(blob)
            print("texture saved (data-uri):", out.name, len(blob), "bytes")
        elif "bufferView" in img and bin_chunks:
            bstart = bin_chunks[0][1]
            bv = j["bufferViews"][img["bufferView"]]
            start = bstart + bv.get("byteOffset", 0)
            blob = data[start:start + bv["byteLength"]]
            ext = ".jpg" if "jpeg" in (img.get("mimeType") or "") else ".png"
            out = p.with_name(p.stem + f"_tex{idx}{ext}")
            out.write_bytes(blob)
            print("texture saved (bufferView):", out.name, len(blob), "bytes")
else:
    print("no embedded image found")
