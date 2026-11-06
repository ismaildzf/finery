package net.developer.finery;

import net.developer.finery.item.CosmeticDye;
import net.developer.finery.registry.ModItems;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.fml.common.Mod;
import top.theillusivec4.curios.api.CuriosApi;

/**
 * Visual test helper, opt-in with -Dfinery.autotest=true.
 * Cycles one representative item from every cosmetic family so the client can
 * screenshot the roster.
 */
@EventBusSubscriber(modid = Finery.MOD_ID, bus = EventBusSubscriber.Bus.GAME)
public final class AutoTestEquip {
    private static final int PHASE_TICKS = 140;

    private static final boolean ENABLED = System.getProperty("finery.autotest") != null;
    private static int ticks;
    private static int phase = -1;
    private static int healthCheckAt = -1;

    private AutoTestEquip() {
    }

    @SubscribeEvent
    public static void loggedIn(PlayerEvent.PlayerLoggedInEvent event) {
        if (!ENABLED || !(event.getEntity() instanceof ServerPlayer player)) {
            return;
        }
        ticks = 0;
        phase = -1;
        player.setGameMode(net.minecraft.world.level.GameType.CREATIVE);
        player.setHealth(player.getMaxHealth());
        player.getFoodData().setFoodLevel(20);
        player.serverLevel().setDayTime(1000L);
        Finery.LOGGER.info("[Autotest] curio handler: {}", CuriosApi.getCuriosInventory(player)
                .map(handler -> handler.getCurios().keySet().toString())
                .orElse("absent"));
    }

    @SubscribeEvent
    public static void serverTick(ServerTickEvent.Post event) {
        if (!ENABLED) {
            return;
        }
        ticks++;
        int next = ticks / PHASE_TICKS;
        if (next > phase && next < PHASE_COUNT) {
            phase = next;
            Item[] kit = phaseKit(phase);
            if (kit[0] == null || kit[1] == null || kit[2] == null || kit[3] == null) {
                Finery.LOGGER.warn("[Autotest] phase {} has unbound items", phase);
                return;
            }
            for (ServerPlayer player : event.getServer().getPlayerList().getPlayers()) {
                wear(player, kit, phase);
                Finery.LOGGER.info("[Autotest] phase {} = {} + {} + {} + {} | maxHealth={}",
                        phase, kit[0].getDescriptionId(), kit[1].getDescriptionId(),
                        kit[2].getDescriptionId(), kit[3].getDescriptionId(),
                        player.getAttributeValue(net.minecraft.world.entity.ai.attributes.Attributes.MAX_HEALTH));
            }
            healthCheckAt = ticks + 10;
        }
        if (ticks == healthCheckAt + 5 && (phase == 1 || phase == 6)) {
            for (ServerPlayer player : event.getServer().getPlayerList().getPlayers()) {
                net.minecraft.world.level.GameType previous = player.gameMode.getGameModeForPlayer();
                player.setGameMode(net.minecraft.world.level.GameType.SURVIVAL);
                float before = player.getHealth();
                player.hurt(player.damageSources().fall(), 6.0F);
                float after = player.getHealth();
                player.setGameMode(previous);
                Finery.LOGGER.info("[Autotest] phase {} fall damage: {} -> {} ({})",
                        phase, before, after, phase == 1 ? "angel expected: unchanged" : "control expected: reduced");
            }
        }
        if (ticks == healthCheckAt) {
            for (ServerPlayer player : event.getServer().getPlayerList().getPlayers()) {
                Finery.LOGGER.info("[Autotest] phase {} settled maxHealth={}", phase,
                        player.getAttributeValue(net.minecraft.world.entity.ai.attributes.Attributes.MAX_HEALTH));
            }
        }
    }

    private static final int PHASE_COUNT = 8;

    private static Item[] phaseKit(int index) {
        return switch (index) {
            case 0 -> new Item[]{ModItems.AZURE_CAPE, ModItems.CROWN, ModItems.HEART_LOCKET, ModItems.EYE_WRAP};
            case 1 -> new Item[]{ModItems.ANGEL_WINGS, ModItems.CROWN, ModItems.HEART_LOCKET, ModItems.EYE_WRAP};
            case 2 -> new Item[]{ModItems.DEVIL_WINGS, ModItems.CROWN, ModItems.HEART_LOCKET, ModItems.EYE_WRAP};
            case 3 -> new Item[]{ModItems.DRAGON_WINGS, ModItems.CROWN, ModItems.HEART_LOCKET, ModItems.EYE_WRAP};
            case 4 -> new Item[]{ModItems.BUTTERFLY_WINGS, ModItems.CROWN, ModItems.HEART_LOCKET, ModItems.EYE_WRAP};
            case 5 -> new Item[]{ModItems.AZURE_CAPE, ModItems.WIZARD_HAT, ModItems.SCARF, ModItems.EYE_WRAP};
            case 6 -> new Item[]{ModItems.AZURE_CAPE, ModItems.DRAGON_HORNS, ModItems.DRAGONBONE_TORC, ModItems.EYE_PATCH};
            default -> new Item[]{ModItems.VOID_CAPE, ModItems.CROWN, ModItems.SCARF, ModItems.EYE_WRAP};
        };
    }

    private static void wear(ServerPlayer player, Item[] kit, int phase) {
        CuriosApi.getCuriosInventory(player).ifPresent(handler -> {
            ItemStack neck = new ItemStack(kit[2]);
            ItemStack face = new ItemStack(kit[3]);
            if (phase == 7) {
                CosmeticDye.set(neck, 1);
                CosmeticDye.set(face, 11);
            }
            handler.setEquippedCurio("back", 0, new ItemStack(kit[0]));
            handler.setEquippedCurio("head", 0, new ItemStack(kit[1]));
            handler.setEquippedCurio("necklace", 0, neck);
            handler.setEquippedCurio("charm", 0, face);
        });
    }
}
