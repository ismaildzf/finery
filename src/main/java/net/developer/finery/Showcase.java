package net.developer.finery;

import io.wispforest.accessories.api.AccessoriesCapability;
import net.developer.finery.registry.ModItems;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.minecraft.item.ItemStack;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.network.ServerPlayerEntity;

import java.nio.file.Files;
import java.nio.file.Path;

/**
 * Development showcase hook: while a file named {@code epic_showcase.txt} exists
 * in the run directory, its content (a wing variant id) is equipped on the first
 * player whenever it changes. Lets screenshots be driven without touching the
 * keyboard, which is unreliable with non-Latin layouts. Dev-only.
 */
public final class Showcase {

    private static final Path FILE = Path.of("epic_showcase.txt");
    private static String last = "";
    private static long lastModified;

    private Showcase() {
    }

    public static void register() {
        ServerTickEvents.END_SERVER_TICK.register(Showcase::tick);
    }

    private static void tick(MinecraftServer server) {
        if (server.getTicks() % 5 != 0) {
            return;
        }
        try {
            if (!Files.exists(FILE)) {
                return;
            }
            long stamp = Files.getLastModifiedTime(FILE).toMillis();
            if (stamp == lastModified) {
                return;
            }
            lastModified = stamp;
            String variant = Files.readString(FILE).trim();
            if (variant.isEmpty() || variant.equals(last)) {
                return;
            }
            last = variant;
            if (server.getPlayerManager().getPlayerList().isEmpty()) {
                return;
            }
            ServerPlayerEntity player = server.getPlayerManager().getPlayerList().get(0);
            boolean ok = DevCommands.equip(player, variant);
            Finery.LOGGER.info("[showcase] {} -> {}", variant, ok ? "equipped" : "unknown");
        } catch (Exception ignored) {
            // dev helper: never let the file watcher break the game
        }
    }
}
