package net.developer.finery.client.renderer.head;

import com.google.gson.Gson;
import net.developer.finery.Finery;
import net.minecraft.resources.ResourceLocation;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Head cosmetics authored in Blockbench and baked to quads.
 * Channels: v = four vertex positions in head-local pixels (y 0 at the head top),
 * uv = texture pixels against {@link Model#textureSize} (one animation frame).
 */
public final class BakedHeadModel {

    public static final class Quad {
        public float[][] v;
        public float[][] uv;
    }

    public static final class Model {
        public int[] textureSize;
        /** Animation frames in the strip; static textures use 1. */
        public int frames = 16;
        public List<Quad> quads;
    }

    private static final Map<String, Model> CACHE = new HashMap<>();

    private BakedHeadModel() {
    }

    public static Model get(String variant) {
        if (CACHE.containsKey(variant)) {
            return CACHE.get(variant);
        }
        Model parsed = null;
        try (InputStream in = BakedHeadModel.class.getResourceAsStream(
                "/assets/finery/headmodels/" + variant + ".json")) {
            if (in != null) {
                parsed = new Gson().fromJson(new InputStreamReader(in, StandardCharsets.UTF_8), Model.class);
            }
        } catch (Exception ignored) {
            parsed = null;
        }
        CACHE.put(variant, parsed);
        return parsed;
    }

    public static ResourceLocation texture(String variant) {
        return new ResourceLocation(Finery.MOD_ID, "textures/head/baked/" + variant + ".png");
    }
}
