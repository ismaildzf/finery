package net.developer.finery.registry;

import net.developer.finery.Finery;
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
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.registries.DeferredRegister;
import net.minecraft.core.registries.BuiltInRegistries;
import net.neoforged.neoforge.registries.DeferredHolder;

import java.util.ArrayList;
import java.util.List;

/** NeoForge item registry. Static fields are bound after registration in common setup. */
public final class ModItems {
    public static final DeferredRegister<Item> ITEMS = DeferredRegister.create(BuiltInRegistries.ITEM, Finery.MOD_ID);
    public static final DeferredRegister<CreativeModeTab> TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, Finery.MOD_ID);

    public static CapeItem CRIMSON_CAPE;
    private static final DeferredHolder<Item, CapeItem> CRIMSON_CAPE_H = register("crimson_cape", "crimson", CapeAbility.FLAME_WARD, CapeRarity.UNCOMMON, "item.finery.hint.craft");
    public static CapeItem AZURE_CAPE;
    private static final DeferredHolder<Item, CapeItem> AZURE_CAPE_H = register("azure_cape", "azure", CapeAbility.TIDES_GRACE, CapeRarity.UNCOMMON, "item.finery.hint.craft");
    public static CapeItem EMERALD_CAPE;
    private static final DeferredHolder<Item, CapeItem> EMERALD_CAPE_H = register("emerald_cape", "emerald", CapeAbility.MERCHANT_CHARM, CapeRarity.EPIC, "item.finery.hint.loot_village");
    public static CapeItem VOID_CAPE;
    private static final DeferredHolder<Item, CapeItem> VOID_CAPE_H = register("void_cape", "void", CapeAbility.VOIDSTEP, CapeRarity.UNCOMMON, "item.finery.hint.craft");
    public static CapeItem WARDEN_CAPE;
    private static final DeferredHolder<Item, CapeItem> WARDEN_CAPE_H = register("warden_cape", "warden", CapeAbility.SCULK_VEIL, CapeRarity.LEGENDARY, "item.finery.hint.loot_ancient_city");
    public static CapeItem DRAGON_CAPE;
    private static final DeferredHolder<Item, CapeItem> DRAGON_CAPE_H = register("dragon_cape", "dragon", CapeAbility.DRACONIC_GRACE, CapeRarity.LEGENDARY, "item.finery.hint.loot_end_city");
    public static CapeItem PIRATE_CAPE;
    private static final DeferredHolder<Item, CapeItem> PIRATE_CAPE_H = register("pirate_cape", "pirate", CapeAbility.SEA_LEGS, CapeRarity.EPIC, "item.finery.hint.loot_shipwreck");
    public static CapeItem PHARAOH_CAPE;
    private static final DeferredHolder<Item, CapeItem> PHARAOH_CAPE_H = register("pharaoh_cape", "pharaoh", CapeAbility.DESERT_STRIDE, CapeRarity.EPIC, "item.finery.hint.loot_desert_pyramid");
    public static CapeItem TOTEM_CAPE;
    private static final DeferredHolder<Item, CapeItem> TOTEM_CAPE_H = register("totem_cape", "totem", CapeAbility.LAST_STAND, CapeRarity.EPIC, "item.finery.hint.loot_woodland_mansion");
    public static CapeItem ENCHANTER_CAPE;
    private static final DeferredHolder<Item, CapeItem> ENCHANTER_CAPE_H = register("enchanter_cape", "enchanter", CapeAbility.ARCANE_INSIGHT, CapeRarity.EPIC, "item.finery.hint.loot_stronghold");
    public static CapeItem BREEZE_CAPE;
    private static final DeferredHolder<Item, CapeItem> BREEZE_CAPE_H = register("breeze_cape", "breeze", CapeAbility.WINDBORNE, CapeRarity.EPIC, "item.finery.hint.loot_trial_chambers");
    public static CapeItem WITHER_CAPE;
    private static final DeferredHolder<Item, CapeItem> WITHER_CAPE_H = register("wither_cape", "wither", CapeAbility.UNDYING_EMBER, CapeRarity.EPIC, "item.finery.hint.loot_nether_fortress");
    public static HeadItem WIZARD_HAT;
    private static final DeferredHolder<Item, HeadItem> WIZARD_HAT_H = registerHead("wizard_hat", "wizard_hat", "hat", HeadAbility.FORTUNE, CapeRarity.UNCOMMON, "item.finery.hint.craft");
    public static HeadItem HEADBAND;
    private static final DeferredHolder<Item, HeadItem> HEADBAND_H = registerHead("headband", "headband", "hat", HeadAbility.REFLEX, CapeRarity.UNCOMMON, "item.finery.hint.craft");
    public static HeadItem EYE_PATCH;
    private static final DeferredHolder<Item, HeadItem> EYE_PATCH_H = registerHead("eye_patch", "eye_patch", "face", HeadAbility.STEADY_GAZE, CapeRarity.UNCOMMON, "item.finery.hint.craft");
    public static HeadItem CROWN;
    private static final DeferredHolder<Item, HeadItem> CROWN_H = registerHead("crown", "crown", "hat", HeadAbility.VITALITY, CapeRarity.EPIC, "item.finery.hint.loot_woodland_mansion");
    public static HeadItem DRAGON_HORNS;
    private static final DeferredHolder<Item, HeadItem> DRAGON_HORNS_H = registerHead("dragon_horns", "dragon_horns", "hat", HeadAbility.DIVE_FURY, CapeRarity.LEGENDARY, "item.finery.hint.loot_end_city");
    public static HeadItem RAM_HORNS;
    private static final DeferredHolder<Item, HeadItem> RAM_HORNS_H = registerHead("ram_horns", "ram_horns", "hat", HeadAbility.GORE_CHARGE, CapeRarity.LEGENDARY, "item.finery.hint.loot_bastion");
    public static HeadItem DEMON_HORN;
    private static final DeferredHolder<Item, HeadItem> DEMON_HORN_H = registerHead("demon_horn", "demon_horn", "hat", HeadAbility.HELLFIRE, CapeRarity.EPIC, "item.finery.hint.loot_nether_fortress");
    public static HeadItem IMP_HORNS;
    private static final DeferredHolder<Item, HeadItem> IMP_HORNS_H = registerHead("imp_horns", "imp_horns", "hat", HeadAbility.IMP_VIGOR, CapeRarity.UNCOMMON, "item.finery.hint.craft");
    public static HeadItem EYE_WRAP;
    private static final DeferredHolder<Item, HeadItem> EYE_WRAP_H = registerDyeableHead("eye_wrap", "eye_wrap", "face", HeadAbility.SHADOW_SIGHT, CapeRarity.UNCOMMON, "item.finery.hint.craft", 0);
    public static NeckItem SCARF;
    private static final DeferredHolder<Item, NeckItem> SCARF_H = registerDyeableNeck("scarf", "scarf", NeckAbility.WARMTH, CapeRarity.UNCOMMON, "item.finery.hint.craft", 0);
    public static NeckItem ROYAL_SCARF;
    private static final DeferredHolder<Item, NeckItem> ROYAL_SCARF_H = registerNeck("royal_scarf", "royal_scarf", NeckAbility.WARMTH, CapeRarity.EPIC, "item.finery.hint.craft");
    public static NeckItem CORAL_AMULET;
    private static final DeferredHolder<Item, NeckItem> CORAL_AMULET_H = registerNeck("coral_amulet", "coral_amulet", NeckAbility.CORAL_CONDUIT, CapeRarity.EPIC, "item.finery.hint.loot_buried_treasure");
    public static NeckItem MOON_LOCKET;
    private static final DeferredHolder<Item, NeckItem> MOON_LOCKET_H = registerNeck("moon_locket", "moon_locket", NeckAbility.MOONLIGHT, CapeRarity.EPIC, "item.finery.hint.loot_stronghold");
    public static NeckItem SERPENT_TORC;
    private static final DeferredHolder<Item, NeckItem> SERPENT_TORC_H = registerNeck("serpent_torc", "serpent_torc", NeckAbility.ANTIVENOM, CapeRarity.EPIC, "item.finery.hint.loot_jungle_temple");
    public static NeckItem TUNDRA_TORC;
    private static final DeferredHolder<Item, NeckItem> TUNDRA_TORC_H = registerNeck("tundra_torc", "tundra_torc", NeckAbility.FROSTSTRIDE, CapeRarity.EPIC, "item.finery.hint.loot_igloo");
    public static NeckItem EMBER_PENDANT;
    private static final DeferredHolder<Item, NeckItem> EMBER_PENDANT_H = registerNeck("ember_pendant", "ember_pendant", NeckAbility.EMBERHEART, CapeRarity.LEGENDARY, "item.finery.hint.loot_nether_fortress");
    public static NeckItem PRAYER_BEADS;
    private static final DeferredHolder<Item, NeckItem> PRAYER_BEADS_H = registerNeck("prayer_beads", "prayer_beads", NeckAbility.BLESSING, CapeRarity.LEGENDARY, "item.finery.hint.loot_desert_pyramid");
    public static NeckItem HEART_LOCKET;
    private static final DeferredHolder<Item, NeckItem> HEART_LOCKET_H = registerNeck("heart_locket", "heart_locket", NeckAbility.VITALITY, CapeRarity.LEGENDARY, "item.finery.hint.loot_woodland_mansion");
    public static NeckItem DRAGONBONE_TORC;
    private static final DeferredHolder<Item, NeckItem> DRAGONBONE_TORC_H = registerNeck("dragonbone_torc", "dragonbone_torc", NeckAbility.DRAGON_MIGHT, CapeRarity.LEGENDARY, "item.finery.hint.loot_end_city");
    public static WingItem DEVIL_WINGS;
    private static final DeferredHolder<Item, WingItem> DEVIL_WINGS_H = registerWing("devil_wings", "devil_wings", WingAbility.DEVIL, "item.finery.hint.wing_devil");
    public static WingItem DRAGON_WINGS;
    private static final DeferredHolder<Item, WingItem> DRAGON_WINGS_H = registerWing("dragon_wings", "dragon_wings", WingAbility.DRAGON, "item.finery.hint.wing_dragon");
    public static WingItem ANGEL_WINGS;
    private static final DeferredHolder<Item, WingItem> ANGEL_WINGS_H = registerWing("angel_wings", "angel_wings", WingAbility.ANGEL, "item.finery.hint.wing_angel");
    public static WingItem BUTTERFLY_WINGS;
    private static final DeferredHolder<Item, WingItem> BUTTERFLY_WINGS_H = registerWing("butterfly_wings", "butterfly_wings", WingAbility.BUTTERFLY, "item.finery.hint.wing_butterfly");

    private static final List<DeferredHolder<Item, CapeItem>> ALL_HOLDERS = List.of(CRIMSON_CAPE_H, AZURE_CAPE_H, EMERALD_CAPE_H, VOID_CAPE_H, WARDEN_CAPE_H, DRAGON_CAPE_H, PIRATE_CAPE_H, PHARAOH_CAPE_H, TOTEM_CAPE_H, ENCHANTER_CAPE_H, BREEZE_CAPE_H, WITHER_CAPE_H);
    public static List<CapeItem> ALL;
    private static final List<DeferredHolder<Item, HeadItem>> HEADS_HOLDERS = List.of(WIZARD_HAT_H, HEADBAND_H, EYE_PATCH_H, CROWN_H, DRAGON_HORNS_H, RAM_HORNS_H, DEMON_HORN_H, IMP_HORNS_H, EYE_WRAP_H);
    public static List<HeadItem> HEADS;
    private static final List<DeferredHolder<Item, NeckItem>> NECKS_HOLDERS = List.of(SCARF_H, ROYAL_SCARF_H, CORAL_AMULET_H, MOON_LOCKET_H, SERPENT_TORC_H, TUNDRA_TORC_H, EMBER_PENDANT_H, PRAYER_BEADS_H, HEART_LOCKET_H, DRAGONBONE_TORC_H);
    public static List<NeckItem> NECKS;
    private static final List<DeferredHolder<Item, WingItem>> WINGS_HOLDERS = List.of(DEVIL_WINGS_H, DRAGON_WINGS_H, ANGEL_WINGS_H, BUTTERFLY_WINGS_H);
    public static List<WingItem> WINGS;

    public static final DeferredHolder<CreativeModeTab, CreativeModeTab> TAB = TABS.register("finery", () -> CreativeModeTab.builder()
            .title(Component.translatable("itemGroup.finery"))
            .icon(() -> new ItemStack(CRIMSON_CAPE_H.get()))
            .displayItems((params, output) -> {
                for (DeferredHolder<Item, ? extends Item> holder : ALL_HOLDERS) output.accept(holder.get());
                for (DeferredHolder<Item, ? extends Item> holder : HEADS_HOLDERS) output.accept(holder.get());
                for (DeferredHolder<Item, ? extends Item> holder : NECKS_HOLDERS) output.accept(holder.get());
                for (DeferredHolder<Item, ? extends Item> holder : WINGS_HOLDERS) output.accept(holder.get());
            })
            .build());

    private ModItems() {
    }

    public static void register(net.neoforged.bus.api.IEventBus bus) {
        ITEMS.register(bus);
        TABS.register(bus);
    }

    /** Runs after registries are frozen. */
    public static void bind() {
        CRIMSON_CAPE = CRIMSON_CAPE_H.get();
        AZURE_CAPE = AZURE_CAPE_H.get();
        EMERALD_CAPE = EMERALD_CAPE_H.get();
        VOID_CAPE = VOID_CAPE_H.get();
        WARDEN_CAPE = WARDEN_CAPE_H.get();
        DRAGON_CAPE = DRAGON_CAPE_H.get();
        PIRATE_CAPE = PIRATE_CAPE_H.get();
        PHARAOH_CAPE = PHARAOH_CAPE_H.get();
        TOTEM_CAPE = TOTEM_CAPE_H.get();
        ENCHANTER_CAPE = ENCHANTER_CAPE_H.get();
        BREEZE_CAPE = BREEZE_CAPE_H.get();
        WITHER_CAPE = WITHER_CAPE_H.get();
        WIZARD_HAT = WIZARD_HAT_H.get();
        HEADBAND = HEADBAND_H.get();
        EYE_PATCH = EYE_PATCH_H.get();
        CROWN = CROWN_H.get();
        DRAGON_HORNS = DRAGON_HORNS_H.get();
        RAM_HORNS = RAM_HORNS_H.get();
        DEMON_HORN = DEMON_HORN_H.get();
        IMP_HORNS = IMP_HORNS_H.get();
        EYE_WRAP = EYE_WRAP_H.get();
        SCARF = SCARF_H.get();
        ROYAL_SCARF = ROYAL_SCARF_H.get();
        CORAL_AMULET = CORAL_AMULET_H.get();
        MOON_LOCKET = MOON_LOCKET_H.get();
        SERPENT_TORC = SERPENT_TORC_H.get();
        TUNDRA_TORC = TUNDRA_TORC_H.get();
        EMBER_PENDANT = EMBER_PENDANT_H.get();
        PRAYER_BEADS = PRAYER_BEADS_H.get();
        HEART_LOCKET = HEART_LOCKET_H.get();
        DRAGONBONE_TORC = DRAGONBONE_TORC_H.get();
        DEVIL_WINGS = DEVIL_WINGS_H.get();
        DRAGON_WINGS = DRAGON_WINGS_H.get();
        ANGEL_WINGS = ANGEL_WINGS_H.get();
        BUTTERFLY_WINGS = BUTTERFLY_WINGS_H.get();

        ALL = List.copyOf(ALL_HOLDERS.stream().map(DeferredHolder::get).toList());
        HEADS = List.copyOf(HEADS_HOLDERS.stream().map(DeferredHolder::get).toList());
        NECKS = List.copyOf(NECKS_HOLDERS.stream().map(DeferredHolder::get).toList());
        WINGS = List.copyOf(WINGS_HOLDERS.stream().map(DeferredHolder::get).toList());
        Finery.LOGGER.info("[Finery] Registered {} capes, {} head cosmetics, {} neckwear and {} wings.",
                ALL.size(), HEADS.size(), NECKS.size(), WINGS.size());
    }

    private static Item.Properties settings(String name) {
        return new Item.Properties().stacksTo(1).setId(
                net.minecraft.resources.ResourceKey.create(Registries.ITEM,
                        net.minecraft.resources.ResourceLocation.fromNamespaceAndPath(Finery.MOD_ID, name)));
    }

    private static DeferredHolder<Item, CapeItem> register(String name, String variant, CapeAbility ability,
                                                    CapeRarity rarity, String hintKey) {
        return ITEMS.register(name, () -> new CapeItem(settings(name), variant, ability, rarity, hintKey));
    }

    private static DeferredHolder<Item, HeadItem> registerHead(String name, String variant, String slot,
                                                         HeadAbility ability, CapeRarity rarity, String hintKey) {
        return ITEMS.register(name, () -> new HeadItem(settings(name), variant, slot, ability, rarity, hintKey));
    }

    private static DeferredHolder<Item, HeadItem> registerDyeableHead(String name, String variant, String slot,
                                                                HeadAbility ability, CapeRarity rarity,
                                                                String hintKey, int defaultDye) {
        return ITEMS.register(name, () -> new DyeableHeadItem(settings(name), variant, slot, ability, rarity, hintKey, defaultDye));
    }

    private static DeferredHolder<Item, NeckItem> registerNeck(String name, String variant, NeckAbility ability,
                                                         CapeRarity rarity, String hintKey) {
        return ITEMS.register(name, () -> new NeckItem(settings(name), variant, ability, rarity, hintKey));
    }

    private static DeferredHolder<Item, NeckItem> registerDyeableNeck(String name, String variant, NeckAbility ability,
                                                                CapeRarity rarity, String hintKey, int defaultDye) {
        return ITEMS.register(name, () -> new DyeableNeckItem(settings(name), variant, ability, rarity, hintKey, defaultDye));
    }

    private static DeferredHolder<Item, WingItem> registerWing(String name, String variant, WingAbility ability,
                                                         String hintKey) {
        return ITEMS.register(name, () -> new WingItem(settings(name).fireResistant(), variant, ability,
                CapeRarity.LEGENDARY, hintKey));
    }
}
