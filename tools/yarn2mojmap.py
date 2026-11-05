"""Convert Finery's Yarn source tree to Mojmap class names.

Classes and imports are renamed automatically; method/field renames are dumped
to JSON for review and applied later with compiler guidance. Comments and
string literals are never touched, so lang keys and registry ids stay intact.
"""

import argparse
import json
import os
import re


def parse_tiny(path):
    classes = {}
    methods = {}
    fields = {}
    owner = None
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            parts = line.lstrip("\t").rstrip("\n").split("\t")
            if not parts or parts[0] == "tiny":
                continue
            if parts[0] == "c" and len(parts) >= 3:
                owner = parts[1]
                classes[parts[1]] = parts[2]
            elif parts[0] == "m" and owner and len(parts) >= 4:
                methods[(owner, parts[2], parts[1])] = parts[3]
            elif parts[0] == "f" and owner and len(parts) >= 4:
                fields[(owner, parts[2], parts[1])] = parts[3]
    return classes, methods, fields


def remap_desc(desc, class_map):
    def replace(match):
        name = match.group(1)
        return "L" + class_map.get(name, name) + ";"

    return re.sub(r"L([^;]+);", replace, desc)


def token_rename(text, renames):
    """Rename identifiers outside comments and literals."""
    out = []
    i = 0
    n = len(text)
    identifiers = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*")
    while i < n:
        ch = text[i]
        if ch == "/" and i + 1 < n and text[i + 1] == "/":
            end = text.find("\n", i)
            end = n if end < 0 else end
            out.append(text[i:end])
            i = end
        elif ch == "/" and i + 1 < n and text[i + 1] == "*":
            end = text.find("*/", i + 2)
            end = n if end < 0 else end + 2
            out.append(text[i:end])
            i = end
        elif ch == '"' or ch == "'":
            quote = ch
            j = i + 1
            while j < n:
                if text[j] == "\\":
                    j += 2
                    continue
                if text[j] == quote:
                    j += 1
                    break
                j += 1
            out.append(text[i:j])
            i = j
        else:
            match = identifiers.match(text, i)
            if match:
                word = match.group(0)
                out.append(renames.get(word, word))
                i = match.end()
            else:
                out.append(ch)
                i += 1
    return "".join(out)


def parse_mojang(path):
    """official -> obf mapping from Mojang's client.txt."""
    classes = {}
    for line in open(path, encoding="utf-8"):
        if line.startswith("    ") or " -> " not in line:
            continue
        left, right = line.rstrip("\n").split(" -> ")
        if right.endswith(":"):
            classes[right[:-1]] = left.strip()
    return classes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--yarn", required=True)
    parser.add_argument("--intermediary", required=True)
    parser.add_argument("--mojang", required=True)
    parser.add_argument("--src", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()

    yarn_classes, yarn_methods, _ = parse_tiny(args.yarn)
    inter_classes, inter_methods, _ = parse_tiny(args.intermediary)
    obf_to_official = parse_mojang(args.mojang)

    inter_to_obf = {inter: obf for obf, inter in inter_classes.items()}
    named_to_official = {}
    for inter, named in yarn_classes.items():
        obf = inter_to_obf.get(inter)
        official = obf_to_official.get(obf) if obf else None
        if official and named != official:
            named_to_official[named] = official.replace(".", "/")

    # method/field map for later review: named name -> official name
    method_map = {}
    stats = {"classes": len(named_to_official), "methods": len(method_map), "files": 0, "imports": 0}
    for root, _, files in os.walk(args.src):
        for name in files:
            if not name.endswith(".java"):
                continue
            path = os.path.join(root, name)
            rel = os.path.relpath(path, args.src)
            text = open(path, encoding="utf-8").read()

            # Simple-name rewrites driven by the original imports.
            renames = {}
            for line in text.splitlines():
                match = re.match(r"import\s+(?:static\s+)?([\w.]+)\.([A-Za-z_$][\w$]*);", line)
                if match:
                    full = match.group(1) + "." + match.group(2)
                    simple = match.group(2)
                    official = named_to_official.get(full.replace(".", "/"))
                    if official:
                        stats["imports"] += 1
                        new_simple = official.rsplit("/", 1)[-1]
                        if new_simple != simple:
                            renames[simple] = new_simple

            # FQN rewrites (dotted) for any vanilla class we know.
            for named, official in named_to_official.items():
                dotted_named = named.replace("/", ".")
                dotted_official = official.replace("/", ".")
                if dotted_named in text:
                    text = text.replace(dotted_named, dotted_official)

            if renames:
                text = token_rename(text, renames)

            out_path = os.path.join(args.out, rel)
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            open(out_path, "w", encoding="utf-8").write(text)
            stats["files"] += 1

    os.makedirs(os.path.dirname(args.report), exist_ok=True)
    json.dump(
        {
            "stats": stats,
            "methods": {k: sorted(v) for k, v in sorted(method_map.items())},
            "classes": {k: v for k, v in sorted(named_to_official.items())},
        },
        open(args.report, "w", encoding="utf-8"),
        indent=1,
    )
    print(stats)


if __name__ == "__main__":
    main()
