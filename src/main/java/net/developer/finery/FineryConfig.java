package net.developer.finery;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonSyntaxException;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.fml.loading.FMLPaths;

import java.io.IOException;
import java.io.Reader;
import java.io.Writer;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * Server-side configuration for Finery on NeoForge, stored in {@code config/finery.json}.
 *
 * <p>Same file name and same keys as the Fabric build, so a pack can use one documented
 * file for both loaders. Loaded once from the mod constructor, before any content is
 * registered or any loot is touched. Every failure falls back to the shipped defaults.
 */
public final class FineryConfig {

    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
    private static final String FILE_NAME = "finery.json";

    private static FineryConfig instance = new FineryConfig();
    private static Path path;

    // ── Loot ────────────────────────────────────────────────────────────

    /** Inject the loot-only pieces into vanilla structure chests. */
    public boolean lootEnabled = true;

    /** Multiply every injected loot chance (1.0 = shipped odds, 0 = none). */
    public double lootChanceMultiplier = 1.0D;

    // ── Abilities ───────────────────────────────────────────────────────

    /** Master switch for every passive granted by a worn cosmetic. */
    public boolean abilitiesEnabled = true;

    public boolean capeAbilities = true;
    public boolean headAbilities = true;
    public boolean neckAbilities = true;
    public boolean wingAbilities = true;

    /** Damage-time wing passives (angel fall immunity + shield, butterfly dodge). */
    public boolean wingDamageEvents = true;

    // ── Cosmetics ───────────────────────────────────────────────────────

    /** A cape and a pair of wings cannot be worn at the same time. */
    public boolean exclusiveCapeAndWings = true;

    // ── Per-item overrides ──────────────────────────────────────────────

    /**
     * Piece ids whose ability is off, e.g. {@code ["finery:crimson_cape",
     * "angel_wings"]}. The cosmetic itself still works; only its perk stops.
     */
    public List<String> disabledAbilities = new ArrayList<>();

    // ── Lifecycle ───────────────────────────────────────────────────────

    public enum Group {
        CAPE, HEAD, NECK, WING
    }

    public static FineryConfig get() {
        return instance;
    }

    public static Path path() {
        if (path == null) {
            path = FMLPaths.CONFIGDIR.get().resolve(FILE_NAME);
        }
        return path;
    }

    /** Load (or create) the config file. Never throws. */
    public static void load() {
        Path file = path();
        try {
            if (!Files.exists(file)) {
                instance = new FineryConfig();
                save();
                Finery.LOGGER.info("[Finery] Wrote default config to {}", file);
                instance.logResolved(file);
                return;
            }
            try (Reader reader = Files.newBufferedReader(file)) {
                FineryConfig loaded = GSON.fromJson(reader, FineryConfig.class);
                instance = loaded != null ? loaded : new FineryConfig();
            }
            instance.normalise();
            instance.logResolved(file);
        } catch (IOException | JsonSyntaxException e) {
            Finery.LOGGER.warn("[Finery] Could not read {} ({}); using defaults", file, e.toString());
            instance = new FineryConfig();
            instance.normalise();
        }
    }

    /** Write the current config back to disk. Never throws. */
    public static void save() {
        Path file = path();
        try {
            Files.createDirectories(file.getParent());
            try (Writer writer = Files.newBufferedWriter(file)) {
                GSON.toJson(instance, writer);
            }
        } catch (IOException e) {
            Finery.LOGGER.warn("[Finery] Could not write {} ({})", file, e.toString());
        }
    }

    private void normalise() {
        if (disabledAbilities == null) {
            disabledAbilities = new ArrayList<>();
        }
        if (lootChanceMultiplier < 0.0D) {
            lootChanceMultiplier = 0.0D;
        }
        if (lootChanceMultiplier > 10.0D) {
            lootChanceMultiplier = 10.0D;
        }
    }

    /** One line in the log so a user can prove which file was read and with what values. */
    private void logResolved(Path file) {
        Finery.LOGGER.info(
                "[Finery] Config loaded from {} | loot={} x{} | abilities={} (cape={}, head={}, neck={}, wing={}, wingEvents={}) | exclusive={} | disabled={}",
                file, lootEnabled, lootChanceMultiplier,
                abilitiesEnabled, capeAbilities, headAbilities, neckAbilities, wingAbilities, wingDamageEvents,
                exclusiveCapeAndWings, disabledAbilities);
    }

    // ── Queries ─────────────────────────────────────────────────────────

    /** Loot chance after the multiplier, clamped to [0, 1]. */
    public float lootChance(float base) {
        double scaled = base * lootChanceMultiplier;
        if (scaled <= 0.0D) {
            return 0.0F;
        }
        return (float) Math.min(1.0D, scaled);
    }

    /** True when the perk of this stack is allowed to run. */
    public boolean abilityEnabled(ItemStack stack, Group group) {
        if (!abilitiesEnabled) {
            return false;
        }
        if (!groupEnabled(group)) {
            return false;
        }
        String id = idOf(stack);
        return !disabledAbilities.contains(id) && !disabledAbilities.contains(id.replace("finery:", ""));
    }

    public boolean groupEnabled(Group group) {
        return switch (group) {
            case CAPE -> capeAbilities;
            case HEAD -> headAbilities;
            case NECK -> neckAbilities;
            case WING -> wingAbilities;
        };
    }

    /** Wings keep their damage hooks only when abilities and those hooks are on. */
    public boolean wingDamageEventsEnabled() {
        return abilitiesEnabled && wingAbilities && wingDamageEvents;
    }

    public static String idOf(ItemStack stack) {
        if (stack == null || stack.isEmpty()) {
            return "";
        }
        try {
            ResourceLocation id = BuiltInRegistries.ITEM.getKey(stack.getItem());
            return id != null ? id.toString().toLowerCase(Locale.ROOT) : "";
        } catch (Throwable ignored) {
            return "";
        }
    }
}
