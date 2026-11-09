package net.developer.finery;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonSyntaxException;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.item.ItemStack;
import net.minecraft.registry.Registries;

import java.io.IOException;
import java.io.Reader;
import java.io.Writer;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * Server-side configuration for Finery, stored in {@code config/finery.json}.
 *
 * <p>Pack authors need to switch behaviour off without editing the jar: loot
 * injection into vanilla chests, the small passive abilities, and the
 * cape/wing mutual exclusion are all configurable, and individual pieces can be
 * disabled by id. Everything defaults to the shipped behaviour, so an absent or
 * unreadable file changes nothing.
 */
public final class FineryConfig {

    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
    private static final String FILE_NAME = "finery.json";

    private static FineryConfig instance = new FineryConfig();
    private static Path path;

    // â”€â”€ Loot â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    /** Inject the loot-only pieces into vanilla structure chests. */
    public boolean lootEnabled = true;

    /** Multiply every injected loot chance (1.0 = shipped odds, 0 = none). */
    public double lootChanceMultiplier = 1.0D;

    // â”€â”€ Abilities â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    /** Master switch for every passive granted by a worn cosmetic. */
    public boolean abilitiesEnabled = true;

    public boolean capeAbilities = true;
    public boolean headAbilities = true;
    public boolean neckAbilities = true;
    public boolean wingAbilities = true;

    /** Damage-time wing passives (angel fall immunity + shield, butterfly dodge). */
    public boolean wingDamageEvents = true;

    // â”€â”€ Cosmetics â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    /** A cape and a pair of wings cannot be worn at the same time. */
    public boolean exclusiveCapeAndWings = true;


    // â”€â”€ Per-item overrides â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    /**
     * Piece ids whose ability is off, e.g. {@code ["finery:crimson_cape",
     * "angel_wings"]}. The cosmetic itself still works; only its perk stops.
     */
    public List<String> disabledAbilities = new ArrayList<>();

    // â”€â”€ Lifecycle â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    public enum Group {
        CAPE, HEAD, NECK, WING
    }

    public static FineryConfig get() {
        return instance;
    }

    public static Path path() {
        if (path == null) {
            path = FabricLoader.getInstance().getConfigDir().resolve(FILE_NAME);
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
                return;
            }
            try (Reader reader = Files.newBufferedReader(file)) {
                FineryConfig loaded = GSON.fromJson(reader, FineryConfig.class);
                instance = loaded != null ? loaded : new FineryConfig();
            }
            instance.normalise();
            Finery.LOGGER.info("[Finery] Config loaded from {}", file);
        } catch (IOException | JsonSyntaxException e) {
            Finery.LOGGER.warn("[Finery] Could not read {} ({}); using defaults", file, e.toString());
            instance = new FineryConfig();
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

    // â”€â”€ Queries â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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
            var id = Registries.ITEM.getId(stack.getItem());
            return id != null ? id.toString().toLowerCase(Locale.ROOT) : "";
        } catch (Throwable ignored) {
            return "";
        }
    }
}

