"""In-game QA for the four legendary wing kits (effects, fall immunity, slam, dodge)."""
import sys
import time

sys.path.insert(0, "tools")
import pc  # noqa: E402

OUT = "_design/ingame"


def chat(text, settle=0.9):
    pc.focus("Minecraft")
    pc.press("t")
    time.sleep(0.35)
    pc.paste_text(text)
    time.sleep(0.25)
    pc.press("enter")
    time.sleep(settle)


def shot(tag):
    pc.shot(f"{OUT}/abil_{tag}.png")


def main():
    pc.focus("Minecraft")
    time.sleep(0.6)
    chat("/effect clear @s")
    chat("/gamemode survival")
    chat("/time set midnight")
    chat("/gamerule doDaylightCycle false")
    chat("/kill @e[type=zombie]")

    # ── DRAGON: passive resistance + airborne strength + landing slam ──
    chat("/epiccosmetic dragon_wings")
    time.sleep(1.0)
    chat("/data get entity @s ActiveEffects")
    shot("dragon_effects")
    chat("/summon minecraft:zombie ~2 ~ ~2 {NoAI:1b,ArmorItems:[{id:\"minecraft:leather_helmet\",count:1},{},{},{}]}")
    time.sleep(0.6)
    chat("/data get entity @e[type=zombie,limit=1] Health")
    chat("/tp @s ~ ~6 ~")
    for i in range(12):
        time.sleep(0.7)
        shot(f"dragon_fall_{i:02d}")
    time.sleep(1.0)
    chat("/data get entity @e[type=zombie,limit=1] Health")
    chat("/data get entity @s Health")
    shot("dragon_landed")

    # ── ANGEL: regen + fall immunity + divine shield ──
    chat("/effect clear @s")
    chat("/epiccosmetic angel_wings")
    time.sleep(1.0)
    chat("/data get entity @s ActiveEffects")
    shot("angel_effects")
    chat("/data get entity @s Health")
    chat("/damage @s 10 minecraft:fall")
    chat("/data get entity @s Health")
    shot("angel_after_fall_damage")
    chat("/damage @s 15")
    time.sleep(0.5)
    shot("angel_shield")
    chat("/data get entity @s ActiveEffects")

    # ── BUTTERFLY: agility + dodge rolls ──
    chat("/effect clear @s")
    chat("/epiccosmetic butterfly_wings")
    time.sleep(1.0)
    chat("/kill @e[type=zombie]")
    chat("/summon minecraft:zombie ~2 ~ ~2 {NoAI:1b,ArmorItems:[{id:\"minecraft:leather_helmet\",count:1},{},{},{}]}")
    chat("/data get entity @s ActiveEffects")
    shot("butterfly_effects")
    for i in range(10):
        chat("/damage @s 1 minecraft:mob_attack by @e[type=zombie,limit=1]", settle=0.35)
    shot("butterfly_after_hits")
    chat("/data get entity @s ActiveEffects")

    print("ability QA finished")


if __name__ == "__main__":
    main()
