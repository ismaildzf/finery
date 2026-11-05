package net.developer.finery;

import net.developer.finery.ability.WingEvents;
import net.developer.finery.registry.ModItems;
import net.developer.finery.recipe.DyeCosmeticRecipe;
import net.developer.finery.registry.ModLoot;
import net.fabricmc.api.ModInitializer;
//? if <1.21 {
/*import io.wispforest.accessories.api.AccessoriesCapability;
import io.wispforest.accessories.impl.AccessoriesEventHandler;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents;
import net.minecraft.server.network.ServerPlayerEntity;
import java.util.HashMap;
import java.util.Map;
*///?}
import net.minecraft.recipe.RecipeSerializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Main mod initializer for Finery.
 * Runs on both client and server to register items, slots, and data.
 * 
 * Architecture Note: This mod is designed to be version-portable.
 * All version-specific logic is isolated in clearly marked utility classes
 * so future updates (1.22+, etc.) only require updating those boundaries.
 */
public class Finery implements ModInitializer {
    public static final String MOD_ID = "finery";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

    //? if <1.21 {
    /*private static final Map<ServerPlayerEntity, int[]> PENDING_ACCESSORY_RESYNC = new HashMap<>();
    *///?}

    @Override
    public void onInitialize() {
        LOGGER.info("[Finery] Initializing Finery mod...");

        // Register all custom items (capes)
        ModItems.register();

        // One dye + one dyable cosmetic, in any crafting slots
        RecipeSerializer.register("finery:cosmetic_dyeing", DyeCosmeticRecipe.SERIALIZER);

        // Add the loot-only capes to their themed vanilla chests
        ModLoot.register();

        // Damage-time wing passives (angel fall immunity/shield, butterfly dodge)
        WingEvents.register();

        // Dev helper: /epiccosmetic <variant>
        DevCommands.register();
        Showcase.register();

        // Stats granted by worn cosmetics are re-applied by their tick; clear stale
        // modifiers on login so an item removed while offline cannot leave a bonus.
        net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents.JOIN.register(
                (handler, sender, server) ->
                        net.developer.finery.ability.CosmeticStats.clearWornBonuses(handler.getPlayer()));

        //? if <1.21 {
        /*// Accessories 1.0.0-beta.47 syncs containers too early during login (before the
        // client has spawned the player entity) and the packet is dropped, leaving the
        // client's accessory containers empty so nothing renders. Re-send the sync a few
        // times after join and nudge occupied slots so the client receives them.
        ServerPlayConnectionEvents.JOIN.register((handler, sender, server) ->
                PENDING_ACCESSORY_RESYNC.put(handler.getPlayer(), new int[]{40, 3}));

        ServerTickEvents.END_SERVER_TICK.register(server -> {
            if (PENDING_ACCESSORY_RESYNC.isEmpty()) {
                return;
            }
            var iterator = PENDING_ACCESSORY_RESYNC.entrySet().iterator();
            while (iterator.hasNext()) {
                var entry = iterator.next();
                int[] state = entry.getValue();
                if (state[0] > 1) {
                    state[0]--;
                    continue;
                }
                var player = entry.getKey();
                if (!player.isRemoved()) {
                    resyncAccessories(player);
                }
                state[1]--;
                if (state[1] <= 0) {
                    iterator.remove();
                } else {
                    state[0] = 80;
                }
            }
        });
        *///?}

        LOGGER.info("[Finery] Mod initialized successfully!");
    }

    //? if <1.21 {
    /*private static void resyncAccessories(ServerPlayerEntity player) {
        AccessoriesEventHandler.dataSync(null, player);
        var capability = AccessoriesCapability.getOptionally(player).orElse(null);
        if (capability == null) {
            return;
        }
        for (var container : capability.getContainers().values()) {
            var accessories = container.getAccessories();
            for (int i = 0; i < container.getSize(); i++) {
                var stack = accessories.getStack(i);
                if (!stack.isEmpty()) {
                    accessories.setStack(i, stack.copy());
                }
            }
        }
    }
    *///?}
}
