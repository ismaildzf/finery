package net.developer.finery.registry;

import net.developer.finery.Finery;
//? if >=1.21 {
import net.fabricmc.fabric.api.loot.v3.LootTableEvents;
//?} else {
/*import net.fabricmc.fabric.api.loot.v2.LootTableEvents;
*///?}
import net.minecraft.item.Item;
import net.minecraft.loot.LootPool;
import net.minecraft.loot.LootTable;
import net.minecraft.loot.LootTables;
import net.minecraft.loot.condition.RandomChanceLootCondition;
import net.minecraft.loot.entry.ItemEntry;
import net.minecraft.loot.provider.number.ConstantLootNumberProvider;

/**
 * Injects the loot-only capes into themed vanilla chests at low odds.
 * Uses the Fabric loot API so vanilla loot tables are extended, not replaced.
 */
public final class ModLoot {

    private ModLoot() {
    }

    public static void register() {
        //? if >=1.21 {
        LootTableEvents.MODIFY.register((key, tableBuilder, source, registries) -> {
            if (!source.isBuiltin()) {
                return;
            }
            addTo(tableBuilder, key);
        });
        //?} else {
        /*LootTableEvents.MODIFY.register((resourceManager, lootManager, id, tableBuilder, source) -> {
            if (!source.isBuiltin()) {
                return;
            }
            addTo(tableBuilder, id);
        });
        *///?}

        Finery.LOGGER.info("[Finery] Loot injection registered.");
    }

    /** The loot-table key is an Identifier on 1.20.1 and a RegistryKey on 1.21+. */
    private static void addTo(LootTable.Builder tableBuilder, Object key) {
            if (key == LootTables.ANCIENT_CITY_CHEST) {
                add(tableBuilder, ModItems.WARDEN_CAPE, 0.04F);
            } else if (key == LootTables.END_CITY_TREASURE_CHEST) {
                add(tableBuilder, ModItems.DRAGON_CAPE, 0.05F);
                add(tableBuilder, ModItems.DRAGON_HORNS, 0.04F);
                add(tableBuilder, ModItems.DRAGONBONE_TORC, 0.04F);
                add(tableBuilder, ModItems.ANGEL_WINGS, 0.005F);
                add(tableBuilder, ModItems.DRAGON_WINGS, 0.005F);
            } else if (key == LootTables.BURIED_TREASURE_CHEST) {
                add(tableBuilder, ModItems.CORAL_AMULET, 0.06F);
            } else if (key == LootTables.JUNGLE_TEMPLE_CHEST) {
                add(tableBuilder, ModItems.SERPENT_TORC, 0.07F);
            } else if (key == LootTables.IGLOO_CHEST_CHEST) {
                add(tableBuilder, ModItems.TUNDRA_TORC, 0.08F);
            } else if (key == LootTables.SHIPWRECK_TREASURE_CHEST) {
                add(tableBuilder, ModItems.PIRATE_CAPE, 0.08F);
            } else if (key == LootTables.DESERT_PYRAMID_CHEST) {
                add(tableBuilder, ModItems.PHARAOH_CAPE, 0.07F);
                add(tableBuilder, ModItems.PRAYER_BEADS, 0.05F);
            } else if (key == LootTables.WOODLAND_MANSION_CHEST) {
                add(tableBuilder, ModItems.TOTEM_CAPE, 0.07F);
                add(tableBuilder, ModItems.CROWN, 0.05F);
                add(tableBuilder, ModItems.HEART_LOCKET, 0.05F);
                add(tableBuilder, ModItems.BUTTERFLY_WINGS, 0.005F);
            } else if (key == LootTables.STRONGHOLD_LIBRARY_CHEST) {
                add(tableBuilder, ModItems.ENCHANTER_CAPE, 0.08F);
                add(tableBuilder, ModItems.MOON_LOCKET, 0.06F);
            //? if >=1.21 {
            } else if (key == LootTables.TRIAL_CHAMBERS_REWARD_OMINOUS_RARE_CHEST) {
                add(tableBuilder, ModItems.BREEZE_CAPE, 0.06F);
            //?}
            } else if (key == LootTables.NETHER_BRIDGE_CHEST) {
                add(tableBuilder, ModItems.WITHER_CAPE, 0.06F);
                add(tableBuilder, ModItems.DEMON_HORN, 0.05F);
                add(tableBuilder, ModItems.EMBER_PENDANT, 0.05F);
            } else if (key == LootTables.BASTION_TREASURE_CHEST) {
                add(tableBuilder, ModItems.RAM_HORNS, 0.05F);
                add(tableBuilder, ModItems.DEVIL_WINGS, 0.005F);
            } else if (key == LootTables.VILLAGE_PLAINS_CHEST
                    || key == LootTables.VILLAGE_DESERT_HOUSE_CHEST
                    || key == LootTables.VILLAGE_SAVANNA_HOUSE_CHEST
                    || key == LootTables.VILLAGE_SNOWY_HOUSE_CHEST
                    || key == LootTables.VILLAGE_TAIGA_HOUSE_CHEST) {
                add(tableBuilder, ModItems.EMERALD_CAPE, 0.04F);
            }
    }

    private static void add(LootTable.Builder table, Item item, float chance) {
        table.pool(LootPool.builder()
                .rolls(ConstantLootNumberProvider.create(1.0F))
                .conditionally(RandomChanceLootCondition.builder(chance))
                .with(ItemEntry.builder(item)));
    }
}
