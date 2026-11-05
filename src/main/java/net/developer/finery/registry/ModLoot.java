package net.developer.finery.registry;

import net.developer.finery.Finery;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.storage.loot.BuiltInLootTables;
import net.minecraft.world.level.storage.loot.LootPool;
import net.minecraft.world.level.storage.loot.entries.LootItem;
import net.minecraft.world.level.storage.loot.predicates.LootItemRandomChanceCondition;
import net.minecraft.world.level.storage.loot.providers.number.ConstantValue;
import net.minecraftforge.event.LootTableLoadEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Injects the loot-only cosmetics into themed vanilla chests at low odds. */
@Mod.EventBusSubscriber(modid = Finery.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class ModLoot {
    private ModLoot() {
    }

    public static int injections;

    @SubscribeEvent
    public static void onLootTableLoad(LootTableLoadEvent event) {
        ResourceLocation id = event.getName();
        if (id.equals(BuiltInLootTables.ANCIENT_CITY)) {
            add(event, ModItems.WARDEN_CAPE, 0.04F);
        } else if (id.equals(BuiltInLootTables.END_CITY_TREASURE)) {
            add(event, ModItems.DRAGON_CAPE, 0.05F);
            add(event, ModItems.DRAGON_HORNS, 0.04F);
            add(event, ModItems.DRAGONBONE_TORC, 0.04F);
            add(event, ModItems.ANGEL_WINGS, 0.005F);
            add(event, ModItems.DRAGON_WINGS, 0.005F);
        } else if (id.equals(BuiltInLootTables.BURIED_TREASURE)) {
            add(event, ModItems.CORAL_AMULET, 0.06F);
        } else if (id.equals(BuiltInLootTables.JUNGLE_TEMPLE)) {
            add(event, ModItems.SERPENT_TORC, 0.07F);
        } else if (id.equals(BuiltInLootTables.IGLOO_CHEST)) {
            add(event, ModItems.TUNDRA_TORC, 0.08F);
        } else if (id.equals(BuiltInLootTables.SHIPWRECK_TREASURE)) {
            add(event, ModItems.PIRATE_CAPE, 0.08F);
        } else if (id.equals(BuiltInLootTables.DESERT_PYRAMID)) {
            add(event, ModItems.PHARAOH_CAPE, 0.07F);
            add(event, ModItems.PRAYER_BEADS, 0.05F);
        } else if (id.equals(BuiltInLootTables.WOODLAND_MANSION)) {
            add(event, ModItems.TOTEM_CAPE, 0.07F);
            add(event, ModItems.CROWN, 0.05F);
            add(event, ModItems.HEART_LOCKET, 0.05F);
            add(event, ModItems.BUTTERFLY_WINGS, 0.005F);
        } else if (id.equals(BuiltInLootTables.STRONGHOLD_LIBRARY)) {
            add(event, ModItems.ENCHANTER_CAPE, 0.08F);
            add(event, ModItems.MOON_LOCKET, 0.06F);
        } else if (id.equals(BuiltInLootTables.NETHER_BRIDGE)) {
            add(event, ModItems.WITHER_CAPE, 0.06F);
            add(event, ModItems.DEMON_HORN, 0.05F);
            add(event, ModItems.EMBER_PENDANT, 0.05F);
        } else if (id.equals(BuiltInLootTables.BASTION_TREASURE)) {
            add(event, ModItems.RAM_HORNS, 0.05F);
            add(event, ModItems.DEVIL_WINGS, 0.005F);
        } else if (id.equals(BuiltInLootTables.VILLAGE_PLAINS_HOUSE)
                || id.equals(BuiltInLootTables.VILLAGE_DESERT_HOUSE)
                || id.equals(BuiltInLootTables.VILLAGE_SAVANNA_HOUSE)
                || id.equals(BuiltInLootTables.VILLAGE_SNOWY_HOUSE)
                || id.equals(BuiltInLootTables.VILLAGE_TAIGA_HOUSE)) {
            add(event, ModItems.EMERALD_CAPE, 0.04F);
        }
    }

    private static void add(LootTableLoadEvent event, Item item, float chance) {
        if (item == null) {
            return;
        }
        LootPool pool = LootPool.lootPool()
                .setRolls(ConstantValue.exactly(1.0F))
                .when(LootItemRandomChanceCondition.randomChance(chance))
                .add(LootItem.lootTableItem(item))
                .build();
        event.getTable().addPool(pool);
        injections++;
    }
}
