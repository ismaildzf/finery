"""Launch the installed NeoForge 1.20.1 client with a dedicated game dir.

Usage: python tools/launch_client.py <version_id> <game_dir> [extra game args...]
"""

import json
import os
import shutil
import subprocess
import sys
import zipfile

MC = os.path.join(os.environ["APPDATA"], ".minecraft")
JAVA = os.environ.get(
    "FINERY_JAVA", r"C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe")


def allowed(rules):
    if not rules:
        return True
    allow = False
    for rule in rules:
        os_rule = rule.get("os", {})
        applies = True
        if "name" in os_rule and os_rule["name"] != "windows":
            applies = False
        if applies:
            allow = rule["action"] == "allow"
    return allow


def load(version_id, seen=None):
    seen = seen or set()
    if version_id in seen:
        raise RuntimeError("inheritance loop " + version_id)
    seen.add(version_id)
    path = os.path.join(MC, "versions", version_id, version_id + ".json")
    data = json.load(open(path, encoding="utf-8"))
    if "inheritsFrom" not in data:
        return data
    parent = load(data["inheritsFrom"], seen)
    merged = dict(parent)
    merged.update({k: v for k, v in data.items() if k != "inheritsFrom"})
    merged["inheritsFrom"] = data["inheritsFrom"]
    merged["libraries"] = parent.get("libraries", []) + data.get("libraries", [])
    merged["arguments"] = {
        "jvm": parent.get("arguments", {}).get("jvm", []) + data.get("arguments", {}).get("jvm", []),
        "game": parent.get("arguments", {}).get("game", []) + data.get("arguments", {}).get("game", []),
    }
    return merged


def main():
    version_id = sys.argv[1] if len(sys.argv) > 1 else "1.20.1-forge-47.1.106"
    game_dir = sys.argv[2] if len(sys.argv) > 2 else r"C:\MinecraftModding\mods\neoforge-client-test"
    extra = sys.argv[3:]
    os.makedirs(game_dir, exist_ok=True)
    natives = os.path.join(game_dir, "natives")
    os.makedirs(natives, exist_ok=True)

    version = load(version_id)
    libs_dir = os.path.join(MC, "libraries")
    classpath = []
    for lib in version.get("libraries", []):
        if not allowed(lib.get("rules")):
            continue
        artifact = lib.get("downloads", {}).get("artifact")
        if artifact:
            classpath.append(os.path.join(libs_dir, artifact["path"]))
        native = lib.get("downloads", {}).get("classifiers", {}).get("natives-windows")
        if native and allowed(lib.get("rules")):
            jar = os.path.join(libs_dir, native["path"])
            if os.path.exists(jar):
                with zipfile.ZipFile(jar) as archive:
                    for entry in archive.namelist():
                        if entry.startswith("META-INF") or entry.endswith("/"):
                            continue
                        archive.extract(entry, natives)
    # NeoForge's patched client jar is already a library; the vanilla jar would duplicate packages.
    classpath = list(dict.fromkeys(classpath))

    asset_index = version["assetIndex"]["id"]
    assets = os.path.join(MC, "assets")
    replacements = {
        "${auth_player_name}": "Test",
        "${version_name}": version_id,
        "${game_directory}": game_dir,
        "${assets_root}": assets,
        "${assets_index_name}": asset_index,
        "${auth_uuid}": "00000000000000000000000000000001",
        "${auth_access_token}": "0",
        "${user_type}": "legacy",
        "${version_type}": version.get("type", "release"),
        "${user_properties}": "{}",
        "${clientid}": "",
        "${auth_xuid}": "",
        "${natives_directory}": natives,
        "${launcher_name}": "finery-test",
        "${launcher_version}": "1",
        "${classpath}": os.pathsep.join(classpath),
        "${classpath_separator}": os.pathsep,
        "${library_directory}": libs_dir,
        "${resolution_width}": "1280",
        "${resolution_height}": "720",
    }

    def render(value):
        if isinstance(value, dict):
            return None
        for key, replacement in replacements.items():
            value = value.replace(key, replacement)
        return value

    jvm = []
    for item in version["arguments"]["jvm"]:
        if isinstance(item, dict):
            if allowed(item.get("rules")):
                value = item.get("value", "")
                rendered = [render(v) for v in value] if isinstance(value, list) else [render(value)]
                jvm.extend(v for v in rendered if v)
        else:
            jvm.append(render(item))
    if not any("java.library.path" in arg for arg in jvm):
        jvm.append("-Djava.library.path=" + natives)
    if os.environ.get("FINERY_EXTRA_JVM"):
        jvm.extend(os.environ["FINERY_EXTRA_JVM"].split())
    if os.environ.get("FINERY_CAPEDEBUG"):
        jvm.append("-Dfinery.capedebug=true")
    jvm.append("-Xmx2G")
    if not os.environ.get("FINERY_NO_AUTOTEST"):
        jvm.append("-Dfinery.autotest=true")
    jvm.append("-Dfile.encoding=UTF-8")

    game = []
    for item in version["arguments"]["game"]:
        if isinstance(item, dict):
            if allowed(item.get("rules")):
                value = item.get("value", "")
                rendered = [render(v) for v in value] if isinstance(value, list) else [render(value)]
                game.extend(v for v in rendered if v)
        else:
            game.append(render(item))
    # The version json carries unresolved quickPlay placeholders; leaving --quickPlaySingleplayer
    # in place makes vanilla pick the singleplayer branch and ignore our multiplayer target.
    skip_flags = {"--quickPlayMultiplayer", "--quickPlaySingleplayer", "--quickPlayRealms", "--quickPlayPath"}
    cleaned = []
    index = 0
    while index < len(game):
        if game[index] in skip_flags:
            index += 2
            continue
        cleaned.append(game[index])
        index += 1
    game = cleaned
    game.extend(extra)

    command = [JAVA] + jvm + [version["mainClass"]] + game
    log = open(os.path.join(game_dir, "client.log"), "w", encoding="utf-8", errors="replace")
    process = subprocess.Popen(command, cwd=game_dir, stdout=log, stderr=subprocess.STDOUT,
                               creationflags=subprocess.CREATE_NO_WINDOW)
    if os.environ.get("FINERY_DEBUG_ARGS"):
        print("CMDLINE", "\n".join(command))
    print("pid", process.pid, "gameDir", game_dir)
    print(" ".join(command)[:400])


if __name__ == "__main__":
    main()
