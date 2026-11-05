package net.developer.finery;

import net.developer.finery.registry.ModItems;
import net.developer.finery.registry.ModLoot;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.storage.loot.BuiltInLootTables;
import net.minecraft.world.level.storage.loot.LootTable;
import net.minecraft.world.level.storage.loot.entries.LootItem;
import java.lang.reflect.Field;
import net.minecraftforge.event.server.ServerStartedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Optional boot check: -Dfinery.selftest=true prints PASS/FAIL evidence to the log. */
@Mod.EventBusSubscriber(modid = Finery.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class SelfTest {
    private SelfTest() {
    }

    @SubscribeEvent
    public static void serverStarted(ServerStartedEvent event) {
        if (System.getProperty("finery.selftest") == null) {
            return;
        }
        MinecraftServer server = event.getServer();
        Registry<Item> items = server.registryAccess().registryOrThrow(Registries.ITEM);

        int registered = (int) items.keySet().stream()
                .filter(id -> id.getNamespace().equals(Finery.MOD_ID))
                .count();
        Finery.LOGGER.info("[Selftest] items registered: {} {}", registered, registered == 35 ? "PASS" : "FAIL");

        int recipes = (int) server.getRecipeManager().getRecipes().stream()
                .filter(recipe -> recipe.getId().getNamespace().equals(Finery.MOD_ID))
                .count();
        boolean dyeRecipe = server.getRecipeManager().byKey(new ResourceLocation(Finery.MOD_ID, "cosmetic_dyeing"))
                .isPresent();
        Finery.LOGGER.info("[Selftest] recipes: {} total, dye serializer present: {} {}",
                recipes, dyeRecipe, (recipes >= 15 && dyeRecipe) ? "PASS" : "FAIL");

        for (String slot : new String[]{"back", "head", "charm", "necklace"}) {
            TagKey<Item> tag = TagKey.create(Registries.ITEM, new ResourceLocation("curios", slot));
            int count = items.getTag(tag)
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

    private static void checkLoot(MinecraftServer server, ResourceLocation tableId, Item expected) {
        LootTable table = server.getLootData().getLootTable(tableId);
        boolean found = false;
        try {
            java.util.List<?> pools = (java.util.List<?>) fieldByType(LootTable.class, java.util.List.class).get(table);
            for (Object pool : pools) {
                Object[] entries = (Object[]) fieldByType(pool.getClass(), net.minecraft.world.level.storage.loot.entries.LootPoolEntryContainer[].class).get(pool);
                for (Object entry : entries) {
                    if (entry instanceof LootItem) {
                        if (fieldByType(LootItem.class, Item.class).get(entry) == expected) {
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
