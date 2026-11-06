package net.developer.finery;

import net.developer.finery.registry.ModItems;
import net.developer.finery.registry.ModLoot;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.server.MinecraftServer;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.storage.loot.BuiltInLootTables;
import net.minecraft.world.level.storage.loot.LootTable;
import net.minecraft.world.level.storage.loot.entries.LootItem;
import java.lang.reflect.Field;
import net.neoforged.neoforge.event.server.ServerStartedEvent;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.fml.common.Mod;

/** Optional boot check: -Dfinery.selftest=true prints PASS/FAIL evidence to the log. */
@EventBusSubscriber(modid = Finery.MOD_ID)
public final class SelfTest {
    private SelfTest() {
    }

    @SubscribeEvent
    public static void serverStarted(ServerStartedEvent event) {
        if (System.getProperty("finery.selftest") == null) {
            return;
        }
        MinecraftServer server = event.getServer();
        Registry<Item> items = server.registryAccess().lookupOrThrow(Registries.ITEM);

        int registered = (int) items.keySet().stream()
                .filter(id -> id.getNamespace().equals(Finery.MOD_ID))
                .count();
        Finery.LOGGER.info("[Selftest] items registered: {} {}", registered, registered == 35 ? "PASS" : "FAIL");

        int recipes = (int) server.getRecipeManager().getRecipes().stream()
                .filter(holder -> holder.id().identifier().getNamespace().equals(Finery.MOD_ID))
                .count();
        boolean dyeRecipe = server.getRecipeManager().byKey(
                        net.minecraft.resources.ResourceKey.create(Registries.RECIPE,
                                Identifier.fromNamespaceAndPath(Finery.MOD_ID, "cosmetic_dyeing")))
                .isPresent();
        Finery.LOGGER.info("[Selftest] recipes: {} total, dye serializer present: {} {}",
                recipes, dyeRecipe, (recipes >= 15 && dyeRecipe) ? "PASS" : "FAIL");

        for (String slot : new String[]{"back", "head", "charm", "necklace"}) {
            TagKey<Item> tag = TagKey.create(Registries.ITEM, Identifier.fromNamespaceAndPath("curios", slot));
            int count = items.get(tag)
                    .map(holders -> (int) holders.stream()
                            .filter(holder -> items.getKey(holder.value()) != null
                                    && items.getKey(holder.value()).getNamespace().equals(Finery.MOD_ID))
                            .count())
                    .orElse(-1);
            Finery.LOGGER.info("[Selftest] curios:{} tag: {} {}", slot, count, count > 0 ? "PASS" : "FAIL");
        }

        Finery.LOGGER.info("[Selftest] loot pools injected at table load: {} {}", ModLoot.injections,
                ModLoot.injections >= 20 ? "PASS" : "FAIL");

        checkLoot(server, BuiltInLootTables.ANCIENT_CITY, ModItems.WARDEN_CAPE);
        checkLoot(server, BuiltInLootTables.WOODLAND_MANSION, ModItems.CROWN);
        checkLoot(server, BuiltInLootTables.END_CITY_TREASURE, ModItems.DRAGON_CAPE);
    }

    private static void checkLoot(MinecraftServer server, net.minecraft.resources.ResourceKey<LootTable> tableId, Item expected) {
        LootTable table = server.reloadableRegistries().getLootTable(tableId);
        boolean found = false;
        try {
            java.util.List<?> pools = (java.util.List<?>) fieldByType(LootTable.class, java.util.List.class).get(table);
            for (Object pool : pools) {
                java.util.List<?> entries = (java.util.List<?>) fieldByType(pool.getClass(), java.util.List.class).get(pool);
                for (Object entry : entries) {
                    if (entry instanceof LootItem) {
                        Object held = fieldByType(LootItem.class, net.minecraft.core.Holder.class).get(entry);
                        if (held instanceof net.minecraft.core.Holder<?> holder && holder.value() == expected) {
                            found = true;
                        }
                    }
                }
            }
        } catch (ReflectiveOperationException error) {
            Finery.LOGGER.warn("[Selftest] loot reflection failed for {}: {}", tableId, error.toString());
        }
        Finery.LOGGER.info("[Selftest] loot {} contains {}: {} {}", tableId,
                itemsName(expected), found, found ? "PASS" : "FAIL");
    }

    private static Field fieldByType(Class<?> owner, Class<?> type) throws NoSuchFieldException {
        for (Class<?> current = owner; current != null; current = current.getSuperclass()) {
            for (Field field : current.getDeclaredFields()) {
                if (type.isAssignableFrom(field.getType())) {
                    field.setAccessible(true);
                    return field;
                }
            }
        }
        throw new NoSuchFieldException(owner.getName() + " field of type " + type.getName());
    }

    private static String itemsName(Item item) {
        return net.minecraft.core.registries.BuiltInRegistries.ITEM.getKey(item).toString();
    }
}
