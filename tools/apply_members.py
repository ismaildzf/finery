"""Apply unique Yarn->Mojmap method renames to a converted source tree."""

import argparse
import json
import os
import re

IDENT = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*")


def scan_rename(text, renames):
    out = []
    i = 0
    n = len(text)
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
        elif ch in "\"'":
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
            match = IDENT.match(text, i)
            if match:
                word = match.group(0)
                j = match.end()
                # rename only call sites and method references
                k = j
                while k < n and text[k] in " \t\r\n":
                    k += 1
                is_call = k < n and text[k] == "("
                is_ref = i >= 2 and text[i - 2:i] == "::"
                if word in renames and (is_call or is_ref):
                    out.append(renames[word])
                else:
                    out.append(word)
                i = j
            else:
                out.append(ch)
                i += 1
    return "".join(out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True)
    parser.add_argument("--map", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    data = json.load(open(args.map, encoding="utf-8"))
    renames = {}
    for name, targets in data["methods"].items():
        targets = set(targets)
        if len(targets) == 1:
            target = next(iter(targets))
            if target != name:
                renames[name] = target

    changed = 0
    calls = 0
    for root, _, files in os.walk(args.src):
        for name in files:
            if not name.endswith(".java"):
                continue
            path = os.path.join(root, name)
            rel = os.path.relpath(path, args.src)
            text = open(path, encoding="utf-8").read()
            new = scan_rename(text, renames)
            if new != text:
                changed += 1
                calls += sum(1 for key in renames if key + "(" in text)
            out_path = os.path.join(args.out, rel)
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            open(out_path, "w", encoding="utf-8").write(new)
    print("rename entries", len(renames), "files changed", changed)


if __name__ == "__main__":
    main()
