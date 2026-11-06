package net.developer.finery.client.renderer.neck;

import com.google.gson.Gson;
import net.developer.finery.Finery;
import net.minecraft.resources.Identifier;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Neckwear authored in Blockbench and baked to quads, in body space
 * (origin on the neck line, +y downward, positions divided by 16 at draw time).
 */
public final class BakedNeckModel {

    public static final class Quad {
        public float[][] v;
        public float[][] uv;
    }

    public static final class Model {
        public int[] textureSize;
        public List<Quad> quads;
    }

    private static final Map<String, Model> CACHE = new HashMap<>();

    private BakedNeckModel() {
    }

    public static Model get(String variant) {
        if (CACHE.containsKey(variant)) {
            return CACHE.get(variant);
        }
        Model parsed = null;
        try (InputStream in = BakedNeckModel.class.getResourceAsStream(
                "/assets/finery/neckmodels/" + variant + ".json")) {
            if (in != null) {
                parsed = new Gson().fromJson(new InputStreamReader(in, StandardCharsets.UTF_8), Model.class);
            }
        } catch (Exception ignored) {
            parsed = null;
        }
        CACHE.put(variant, parsed);
        return parsed;
    }

    public static Identifier texture(String variant) {
        return Identifier.fromNamespaceAndPath(Finery.MOD_ID, "textures/neck/baked/" + variant + ".png");
    }

    public static Identifier mask(String variant) {
        return Identifier.fromNamespaceAndPath(Finery.MOD_ID, "textures/neck/baked/" + variant + "_mask.png");
    }
}
