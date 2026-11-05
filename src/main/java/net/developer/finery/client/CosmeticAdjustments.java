package net.developer.finery.client;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.reflect.TypeToken;

import java.io.Reader;
import java.io.Writer;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;

/**
 * Per-variant position offsets for head cosmetics, in model pixels (1px = 1
 * texel of the 64x64 model = 1/16 block). A player nudges a cosmetic in-game
 * (see {@link AdjustmentMode}) so it fits their own skin — eye positions vary
 * between skins, so the base placement can't fit everyone.
 *
 * Persisted client-side to config/finery/adjustments.json as
 * {"variant": [x, y, z]}. Offsets are clamped to ±6px to keep things sane.
 */
public final class CosmeticAdjustments {

    public static final float LIMIT = 6.0F;

    private static final Path FILE = net.minecraftforge.fml.loading.FMLPaths.CONFIGDIR.get().resolve("finery").resolve("adjustments.json");
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();

    private static final Map<String, float[]> OFFSETS = new HashMap<>();
    private static boolean loaded;

    private CosmeticAdjustments() {}

    /** Stored offset {x,y,z} or null when the variant was never adjusted. */
    public static float[] get(String variant) {
        ensureLoaded();
        return OFFSETS.get(variant);
    }

    public static void set(String variant, float x, float y, float z) {
        ensureLoaded();
        OFFSETS.put(variant, new float[]{clamp(x), clamp(y), clamp(z)});
        save();
    }

    private static float clamp(float v) {
        return Math.max(-LIMIT, Math.min(LIMIT, v));
    }

    private static void ensureLoaded() {
        if (loaded) {
            return;
        }
        loaded = true;
        if (!Files.isRegularFile(FILE)) {
            return;
        }
        try (Reader reader = Files.newBufferedReader(FILE)) {
            Map<String, float[]> data = GSON.fromJson(reader, new TypeToken<Map<String, float[]>>() {}.getType());
            if (data != null) {
                data.forEach((variant, offset) -> {
                    if (offset != null && offset.length == 3) {
                        OFFSETS.put(variant, offset);
                    }
                });
            }
        } catch (Exception ignored) {
            // broken file -> start from defaults
        }
    }

    private static void save() {
        try {
            Files.createDirectories(FILE.getParent());
            try (Writer writer = Files.newBufferedWriter(FILE)) {
                GSON.toJson(OFFSETS, writer);
            }
        } catch (Exception ignored) {
        }
    }
}
