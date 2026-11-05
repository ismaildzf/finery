package net.developer.finery.registry;

import net.developer.finery.Finery;
import net.developer.finery.item.CosmeticDye;
import net.developer.finery.ability.CapeAbility;
import net.developer.finery.ability.HeadAbility;
import net.developer.finery.ability.NeckAbility;
import net.developer.finery.ability.WingAbility;
import net.developer.finery.item.CapeItem;
import net.developer.finery.item.CapeRarity;
import net.developer.finery.item.DyeableHeadItem;
import net.developer.finery.item.DyeableNeckItem;
import net.developer.finery.item.HeadItem;
import net.developer.finery.item.NeckItem;
import net.developer.finery.item.WingItem;
import net.fabricmc.fabric.api.itemgroup.v1.FabricItemGroup;
import net.minecraft.item.Item;
import net.minecraft.item.ItemGroup;
import net.minecraft.item.ItemStack;
import net.minecraft.registry.Registries;
import net.minecraft.registry.Registry;
import net.minecraft.registry.RegistryKey;
import net.minecraft.registry.RegistryKeys;
import net.minecraft.text.Text;
import net.minecraft.util.Identifier;

import java.util.List;

/**
 * Central item registry for Finery.
 *
 * Two families of capes:
 *  - Craftable (crimson/azure/emerald/void): shaped recipes under data/finery/recipe
 *  - Loot-only (warden/dragon/pirate/pharaoh/totem/enchanter/breeze/wither):
 *    injected into themed vanilla chests by {@link ModLoot}
 */
public class ModItems {

    // ── Craftable capes (RPG "uncommon" starter tier) ───────────────────
    public static final CapeItem CRIMSON_CAPE = register("crimson_cape", "crimson",
            CapeAbility.FLAME_WARD, CapeRarity.UNCOMMON, "item.finery.hint.craft");
    public static final CapeItem AZURE_CAPE = register("azure_cape", "azure",
            CapeAbility.TIDES_GRACE, CapeRarity.UNCOMMON, "item.finery.hint.craft");
    public static final CapeItem EMERALD_CAPE = register("emerald_cape", "emerald",
            CapeAbility.MERCHANT_CHARM, CapeRarity.EPIC, "item.finery.hint.loot_village");
    public static final CapeItem VOID_CAPE = register("void_cape", "void",
            CapeAbility.VOIDSTEP, CapeRarity.UNCOMMON, "item.finery.hint.craft");

    // ── Loot-only capes (themed to structures) ──────────────────────────
    public static final CapeItem WARDEN_CAPE = register("warden_cape", "warden",
            CapeAbility.SCULK_VEIL, CapeRarity.LEGENDARY, "item.finery.hint.loot_ancient_city");
    public static final CapeItem DRAGON_CAPE = register("dragon_cape", "dragon",
            CapeAbility.DRACONIC_GRACE, CapeRarity.LEGENDARY, "item.finery.hint.loot_end_city");
    public static final CapeItem PIRATE_CAPE = register("pirate_cape", "pirate",
            CapeAbility.SEA_LEGS, CapeRarity.EPIC, "item.finery.hint.loot_shipwreck");
    public static final CapeItem PHARAOH_CAPE = register("pharaoh_cape", "pharaoh",
            CapeAbility.DESERT_STRIDE, CapeRarity.EPIC, "item.finery.hint.loot_desert_pyramid");
    public static final CapeItem TOTEM_CAPE = register("totem_cape", "totem",
            CapeAbility.LAST_STAND, CapeRarity.EPIC, "item.finery.hint.loot_woodland_mansion");
    public static final CapeItem ENCHANTER_CAPE = register("enchanter_cape", "enchanter",
            CapeAbility.ARCANE_INSIGHT, CapeRarity.EPIC, "item.finery.hint.loot_stronghold");
    public static final CapeItem BREEZE_CAPE = register("breeze_cape", "breeze",
            CapeAbility.WINDBORNE, CapeRarity.EPIC, "item.finery.hint.loot_trial_chambers");
    public static final CapeItem WITHER_CAPE = register("wither_cape", "wither",
            CapeAbility.UNDYING_EMBER, CapeRarity.EPIC, "item.finery.hint.loot_nether_fortress");

    /** All capes, in creative-tab order. */
    public static final List<CapeItem> ALL = List.of(
            CRIMSON_CAPE, AZURE_CAPE, EMERALD_CAPE, VOID_CAPE,
            WARDEN_CAPE, DRAGON_CAPE, PIRATE_CAPE, PHARAOH_CAPE,
            TOTEM_CAPE, ENCHANTER_CAPE, BREEZE_CAPE, WITHER_CAPE);

    // ── Head cosmetics: hats, crown, horns, headband, eye patch ─────────
    public static final HeadItem WIZARD_HAT = registerHead("wizard_hat", "wizard_hat", "hat",
            HeadAbility.FORTUNE, CapeRarity.UNCOMMON, "item.finery.hint.craft");
    public static final HeadItem HEADBAND = registerHead("headband", "headband", "hat",
            HeadAbility.REFLEX, CapeRarity.UNCOMMON, "item.finery.hint.craft");
    public static final HeadItem EYE_PATCH = registerHead("eye_patch", "eye_patch", "face",
            HeadAbility.STEADY_GAZE, CapeRarity.UNCOMMON, "item.finery.hint.craft");
    public static final HeadItem CROWN = registerHead("crown", "crown", "hat",
            HeadAbility.VITALITY, CapeRarity.EPIC, "item.finery.hint.loot_woodland_mansion");
    public static final HeadItem DRAGON_HORNS = registerHead("dragon_horns", "dragon_horns", "hat",
            HeadAbility.DIVE_FURY, CapeRarity.LEGENDARY, "item.finery.hint.loot_end_city");
    public static final HeadItem RAM_HORNS = registerHead("ram_horns", "ram_horns", "hat",
            HeadAbility.GORE_CHARGE, CapeRarity.LEGENDARY, "item.finery.hint.loot_bastion");
    public static final HeadItem DEMON_HORN = registerHead("demon_horn", "demon_horn", "hat",
            HeadAbility.HELLFIRE, CapeRarity.EPIC, "item.finery.hint.loot_nether_fortress");
    public static final HeadItem IMP_HORNS = registerHead("imp_horns", "imp_horns", "hat",
            HeadAbility.IMP_VIGOR, CapeRarity.UNCOMMON, "item.finery.hint.craft");
    public static final HeadItem EYE_WRAP = registerDyeableHead("eye_wrap", "eye_wrap", "face",
            HeadAbility.SHADOW_SIGHT, CapeRarity.UNCOMMON, "item.finery.hint.craft", 0);

    /** All head cosmetics, in creative-tab order. */
    public static final List<HeadItem> HEADS = List.of(
            WIZARD_HAT, HEADBAND, EYE_PATCH, CROWN, DRAGON_HORNS, RAM_HORNS,
            DEMON_HORN, IMP_HORNS, EYE_WRAP);

    // ── Neckwear: scarves, amulets, torcs (chapter 3) ────────────────────
    public static final NeckItem SCARF = registerDyeableNeck("scarf", "scarf",
            NeckAbility.WARMTH, CapeRarity.UNCOMMON, "item.finery.hint.craft", 0);
    public static final NeckItem ROYAL_SCARF = registerNeck("royal_scarf", "royal_scarf",
            NeckAbility.WARMTH, CapeRarity.EPIC, "item.finery.hint.craft");
    public static final NeckItem CORAL_AMULET = registerNeck("coral_amulet", "coral_amulet",
            NeckAbility.CORAL_CONDUIT, CapeRarity.EPIC, "item.finery.hint.loot_buried_treasure");
    public static final NeckItem MOON_LOCKET = registerNeck("moon_locket", "moon_locket",
            NeckAbility.MOONLIGHT, CapeRarity.EPIC, "item.finery.hint.loot_stronghold");
    public static final NeckItem SERPENT_TORC = registerNeck("serpent_torc", "serpent_torc",
            NeckAbility.ANTIVENOM, CapeRarity.EPIC, "item.finery.hint.loot_jungle_temple");
    public static final NeckItem TUNDRA_TORC = registerNeck("tundra_torc", "tundra_torc",
            NeckAbility.FROSTSTRIDE, CapeRarity.EPIC, "item.finery.hint.loot_igloo");
    public static final NeckItem EMBER_PENDANT = registerNeck("ember_pendant", "ember_pendant",
            NeckAbility.EMBERHEART, CapeRarity.LEGENDARY, "item.finery.hint.loot_nether_fortress");
    public static final NeckItem PRAYER_BEADS = registerNeck("prayer_beads", "prayer_beads",
            NeckAbility.BLESSING, CapeRarity.LEGENDARY, "item.finery.hint.loot_desert_pyramid");
    public static final NeckItem HEART_LOCKET = registerNeck("heart_locket", "heart_locket",
            NeckAbility.VITALITY, CapeRarity.LEGENDARY, "item.finery.hint.loot_woodland_mansion");
    public static final NeckItem DRAGONBONE_TORC = registerNeck("dragonbone_torc", "dragonbone_torc",
            NeckAbility.DRAGON_MIGHT, CapeRarity.LEGENDARY, "item.finery.hint.loot_end_city");

    /** All neckwear, in creative-tab order. */
    public static final List<NeckItem> NECKS = List.of(
            SCARF, ROYAL_SCARF,
            CORAL_AMULET, MOON_LOCKET, SERPENT_TORC, TUNDRA_TORC,
            EMBER_PENDANT, PRAYER_BEADS, HEART_LOCKET, DRAGONBONE_TORC);

    // ── Legendary wings, back slot (chapter 4) ───────────────────────────
    public static final WingItem DEVIL_WINGS = registerWing("devil_wings", "devil_wings",
            WingAbility.DEVIL, "item.finery.hint.wing_devil");
    public static final WingItem DRAGON_WINGS = registerWing("dragon_wings", "dragon_wings",
            WingAbility.DRAGON, "item.finery.hint.wing_dragon");
    public static final WingItem ANGEL_WINGS = registerWing("angel_wings", "angel_wings",
            WingAbility.ANGEL, "item.finery.hint.wing_angel");
    public static final WingItem BUTTERFLY_WINGS = registerWing("butterfly_wings", "butterfly_wings",
            WingAbility.BUTTERFLY, "item.finery.hint.wing_butterfly");

    /** All wings. Wings and capes cannot be worn together. */
    public static final List<WingItem> WINGS = List.of(
            DEVIL_WINGS, DRAGON_WINGS, ANGEL_WINGS, BUTTERFLY_WINGS);

    /** Dedicated creative tab so the 12 capes don't flood vanilla tabs. */
    public static final ItemGroup GROUP = Registry.register(Registries.ITEM_GROUP,
            Identifier.of(Finery.MOD_ID, "main"),
            FabricItemGroup.builder()
                    .displayName(Text.translatable("itemGroup.finery.main"))
                    .icon(() -> new ItemStack(DRAGON_CAPE))
                    .entries((context, entries) -> {
                        ALL.forEach(entries::add);
                        HEADS.forEach(entries::add);
                        NECKS.forEach(entries::add);
                        WINGS.forEach(entries::add);
                    })
                    .build());

    // 1.21.10 resolves the item translation key inside the Item constructor, so the
    // registry key must already be present in the settings before registration.
    private static Item.Settings settings(String name) {
        //? if <1.21.2 {
        /*return new Item.Settings().maxCount(1);
        *///?} else {
        return new Item.Settings().maxCount(1)
                .registryKey(RegistryKey.of(RegistryKeys.ITEM, Identifier.of(Finery.MOD_ID, name)));
        //?}
    }

    private static CapeItem register(String name, String variant, CapeAbility ability,
                                     CapeRarity rarity, String hintKey) {
        return Registry.register(Registries.ITEM, Identifier.of(Finery.MOD_ID, name),
                new CapeItem(settings(name), variant, ability, rarity, hintKey));
    }

    private static HeadItem registerHead(String name, String variant, String slot,
                                         HeadAbility ability, CapeRarity rarity, String hintKey) {
        return Registry.register(Registries.ITEM, Identifier.of(Finery.MOD_ID, name),
                new HeadItem(settings(name), variant, slot, ability, rarity, hintKey));
    }

    private static HeadItem registerDyeableHead(String name, String variant, String slot,
                                                HeadAbility ability, CapeRarity rarity, String hintKey,
                                                int defaultDye) {
        return Registry.register(Registries.ITEM, Identifier.of(Finery.MOD_ID, name),
                new DyeableHeadItem(settings(name), variant, slot, ability, rarity, hintKey, defaultDye));
    }

    private static NeckItem registerNeck(String name, String variant, NeckAbility ability,
                                         CapeRarity rarity, String hintKey) {
        return Registry.register(Registries.ITEM, Identifier.of(Finery.MOD_ID, name),
                new NeckItem(settings(name), variant, ability, rarity, hintKey));
    }

    private static NeckItem registerDyeableNeck(String name, String variant, NeckAbility ability,
                                                CapeRarity rarity, String hintKey, int defaultDye) {
        return Registry.register(Registries.ITEM, Identifier.of(Finery.MOD_ID, name),
                new DyeableNeckItem(settings(name), variant, ability, rarity, hintKey, defaultDye));
    }

    private static WingItem registerWing(String name, String variant, WingAbility ability,
                                         String hintKey) {
        return Registry.register(Registries.ITEM, Identifier.of(Finery.MOD_ID, name),
                new WingItem(settings(name).fireproof(), variant, ability,
                        CapeRarity.LEGENDARY, hintKey));
    }

    /** Triggered from ModInitializer; class-load runs the static registration above. */
    public static void register() {
        Finery.LOGGER.info("[Finery] Registered {} capes, {} head cosmetics, {} neckwear and {} wings.",
                ALL.size(), HEADS.size(), NECKS.size(), WINGS.size());
    }
}
