package net.developer.finery.client.renderer.wing;

import com.google.gson.Gson;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.Reader;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Baked wing mesh: quads already positioned in the wing-local frame
 * (x outboard, y up, z backward) and UVs in texture pixels.
 * Produced by {@code tools/export_wings_game.py}.
 */
public final class WingModelData {

    public static final class Quad {
        /** x,y,z for four corners. */
        public float[] v;
        /** u,v for four corners, in texture pixels. */
        public float[] uv;
        /** Optional RGB tint 0..255. */
        public float[] c;
    }

    public static final class Model {
        public int[] textureSize;
        public List<Quad> quads;
    }

    private static final Map<String, Model> CACHE = new HashMap<>();

    private WingModelData() {
    }

    /** Loads (and caches) one wing mesh; {@code null} if the resource is missing. */
    public static Model get(String path) {
        if (CACHE.containsKey(path)) {
            return CACHE.get(path);
        }
        Model parsed = null;
        try (InputStream in = WingModelData.class.getResourceAsStream(path)) {
            if (in != null) {
                try (Reader reader = new InputStreamReader(in, StandardCharsets.UTF_8)) {
                    parsed = new Gson().fromJson(reader, Model.class);
                }
            }
        } catch (Exception ignored) {
            parsed = null;
        }
        CACHE.put(path, parsed);
        return parsed;
    }
}
