"""Build a Yarn-name -> Mojmap-name dictionary for methods and fields (1.20.1)."""

import json
import re

PRIMITIVES = {
    "void": "V", "boolean": "Z", "byte": "B", "char": "C", "short": "S",
    "int": "I", "long": "J", "float": "F", "double": "D",
}


def type_desc(name):
    if name in PRIMITIVES:
        return PRIMITIVES[name]
    if name.endswith("[]"):
        return "[" + type_desc(name[:-2])
    return "L" + name + ";"


def parse_tiny(path):
    classes, methods, fields = {}, {}, {}
    owner = None
    for line in open(path, encoding="utf-8"):
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


def parse_mojang(path):
    classes, methods, fields = {}, {}, {}
    owner = None
    method_re = re.compile(r"^\s+\d+:\d+:(\S+) ([A-Za-z_$][\w$]*)\((.*)\) -> (\S+)$")
    field_re = re.compile(r"^\s+(\S+) ([A-Za-z_$][\w$]*) -> (\S+)$")
    for line in open(path, encoding="utf-8"):
        if line.startswith(" ") and " -> " in line:
            m = method_re.match(line.rstrip("\n"))
            if m:
                ret, name, args, obf = m.groups()
                arg_desc = "".join(type_desc(a.strip()) for a in args.split(",") if a.strip())
                desc = "(" + arg_desc + ")" + type_desc(ret.strip())
                methods[(owner, obf, desc)] = name
                continue
            f = field_re.match(line.rstrip("\n"))
            if f:
                ftype, name, obf = f.groups()
                fields[(owner, obf, type_desc(ftype.strip()))] = name
                continue
            continue
        if " -> " in line:
            left, right = line.rstrip("\n").split(" -> ")
            right = right[:-1] if right.endswith(":") else right
            classes[right] = left.strip()
            owner = right
    return classes, methods, fields


def remap_desc(desc, class_map):
    return re.sub(r"L([^;]+);", lambda m: "L" + class_map.get(m.group(1), m.group(1)) + ";", desc)


def main():
    yarn_c, yarn_m, yarn_f = parse_tiny(r"C:\MinecraftModding\mods\finery-neoforge\_port\mappings\yarn.tiny")
    inter_c, inter_m, inter_f = parse_tiny(r"C:\MinecraftModding\mods\finery-neoforge\_port\mappings\intermediary.tiny")
    moj_c, moj_m, moj_f = parse_mojang(r"C:\MinecraftModding\mods\finery-neoforge\_port\mappings\mojang.txt")

    inter_to_obf = {inter: obf for obf, inter in inter_c.items()}
    obf_by_inter_method = {(owner, inter_name, desc): obf_name
                           for (owner, obf_name, desc), inter_name in inter_m.items()}
    obf_by_inter_field = {(owner, inter_name, desc): obf_name
                          for (owner, obf_name, desc), inter_name in inter_f.items()}

    method_map, field_map = {}, {}
    for (owner, inter_name, inter_desc), named in yarn_m.items():
        obf_owner = inter_to_obf.get(owner)
        if not obf_owner:
            continue
        obf_desc = remap_desc(inter_desc, inter_to_obf)
        obf_name = obf_by_inter_method.get((obf_owner, inter_name, obf_desc))
        if not obf_name:
            continue
        off_desc = remap_desc(obf_desc, moj_c)
        official = moj_m.get((obf_owner, obf_name, off_desc))
        if official and official != named:
            method_map.setdefault(named, set()).add(official)

    for (owner, inter_name, inter_desc), named in yarn_f.items():
        obf_owner = inter_to_obf.get(owner)
        if not obf_owner:
            continue
        obf_desc = remap_desc(inter_desc, inter_to_obf)
        obf_name = obf_by_inter_field.get((obf_owner, inter_name, obf_desc))
        if not obf_name:
            continue
        off_desc = remap_desc(obf_desc, moj_c)
        official = moj_f.get((obf_owner, obf_name, off_desc))
        if official and official != named:
            field_map.setdefault(named, set()).add(official)

    ambiguous_m = {k: sorted(v) for k, v in method_map.items() if len(v) > 1}
    json.dump({"methods": {k: sorted(v) for k, v in sorted(method_map.items())},
               "fields": {k: sorted(v) for k, v in sorted(field_map.items())}},
              open(r"C:\MinecraftModding\mods\finery-neoforge\_port\member_map.json", "w", encoding="utf-8"), indent=1)
    print("method names", len(method_map), "ambiguous", len(ambiguous_m), "unique", len(method_map) - len(ambiguous_m))
    print("field names", len(field_map))
    print("examples", {k: sorted(v)[:2] for k, v in list(method_map.items())[:5]})


if __name__ == "__main__":
    main()
