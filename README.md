# Finery

Thirty-five wearables for **Fabric** — capes, wings, hats, horns and necklaces — built as real 3D geometry, each with a small perk attached.

[Modrinth](https://modrinth.com/mod/finery) · [CurseForge](https://www.curseforge.com/minecraft/mc-mods/finery) · [Issues](https://github.com/ismaildzf/finery/issues)

## What it is

Most cosmetic mods paint a texture on your back. Finery builds geometry: capes sway with a cloth simulation, wings fold and drift when you stand still, and every hat, horn and necklace can be nudged until it fits your own skin.

- **12 capes** — four crafts, the rest in village, shipwreck, pyramid, mansion, stronghold, trial chamber, nether fortress, Ancient City and End City loot.
- **9 headwear pieces** — Blockbench wizard hat and eye patch, crown, headband, bandanna, dragon/ram/demon/imp horns, and an animated dyeable eyewrap.
- **10 neckwear pieces** — a dyeable scarf and the black-and-gold Royal Scarf on a layered model, plus amulets, torcs and lockets.
- **4 legendary wings** — Devil, Dragon, Angel and Butterfly, with layered feathers and an idle flutter.

Every piece carries a small passive (fire resistance, night vision, extra hearts, luck, slow falling…) shown in a rarity-coloured tooltip with its drop location.

## Supported versions

| Minecraft | Jar |
| --- | --- |
| 1.20.1 | `finery-1.0.0+1.20.1.jar` |
| 1.21 | `finery-1.0.0+1.21.jar` |
| 1.21.1 | `finery-1.0.0+1.21.1.jar` |
| 1.21.3 | `finery-1.0.0+1.21.3.jar` |
| 1.21.4 | `finery-1.0.0+1.21.4.jar` |
| 1.21.10 | `finery-1.0.0+1.21.10.jar` |
| 1.21.11 | `finery-1.0.0+1.21.11.jar` |

GitHub release assets are the same jars; GitHub rewrites `+` to `.` in asset names (`finery-1.0.0.1.20.1.jar`).

Requires Fabric Loader, Fabric API and Accessories. owo-lib is also required on 1.21.3 and 1.21.4.

1.21.11 has no official Accessories build yet — use the community Fabric port of Accessories 1.4.3 with owo-lib 0.13.0.

## Building from source

The project uses [Stonecutter](https://stonecutter.kikugie.dev/) to target seven Minecraft versions from one source tree.

```bash
./gradlew "Set active project to 1.21.1" --console=plain -q
./gradlew :1.21.1:build
```

Replace `1.21.1` with any version from the table. The jar lands in `versions/<version>/build/libs/`.

## Using a cosmetic

- Wear pieces from the Accessories slots; capes and wings share the back slot.
- Press **K** (rebindable) for **Cosmetic Adjust** and nudge a worn piece until it fits your skin.
- Drop a dyeable piece in a crafting grid with any dye (any slot) to recolour it.

## Feedback

Bugs, clipping, missing textures and balance complaints go to [GitHub Issues](https://github.com/ismaildzf/finery/issues). Please include the game version, the mod version, your mod list, and a screenshot or log.

## License

MIT — see [LICENSE](LICENSE). Cloth behaviour takes cues from WaveyCapes by tr7zw (MIT). Accessories and owo-lib by WispForest.
