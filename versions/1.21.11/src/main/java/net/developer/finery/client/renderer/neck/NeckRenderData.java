package net.developer.finery.client.renderer.neck;

import java.util.HashMap;
import java.util.Map;

/**
 * Shared data for the neckwear renderer: which mesh style each variant uses
 * (soft scarf wrap, fine chain necklace, braided cord talisman) and the
 * pendant sprite dimensions sampled from the sheet's sprite zone
 * (u32..64 v32..64).
 */
public final class NeckRenderData {

    public enum Kind { SCARF, CHAIN, CORD }

    /** Pendant card width/height and how far below the loop it hangs (model px). */
    public record Data(Kind kind, float pendantW, float pendantH, float pendantDrop) {}

    private static final Map<String, Data> DATA = new HashMap<>();

    static {
        DATA.put("scarf", new Data(Kind.SCARF, 0.0F, 0.0F, 0.0F));
        DATA.put("royal_scarf", new Data(Kind.SCARF, 0.0F, 0.0F, 0.0F));

        DATA.put("coral_amulet", new Data(Kind.CHAIN, 3.0F, 4.0F, 0.1F));
        DATA.put("moon_locket", new Data(Kind.CHAIN, 3.1F, 3.1F, 0.1F));
        DATA.put("ember_pendant", new Data(Kind.CHAIN, 2.8F, 4.0F, 0.1F));
        DATA.put("prayer_beads", new Data(Kind.CHAIN, 3.1F, 3.4F, 0.1F));
        DATA.put("heart_locket", new Data(Kind.CHAIN, 3.3F, 3.8F, 0.1F));

        DATA.put("serpent_torc", new Data(Kind.CORD, 3.6F, 3.8F, 0.1F));
        DATA.put("tundra_torc", new Data(Kind.CORD, 3.0F, 4.2F, 0.1F));
        DATA.put("dragonbone_torc", new Data(Kind.CORD, 3.4F, 4.4F, 0.1F));
    }

    private NeckRenderData() {
    }

    public static Data get(String variant) {
        return DATA.get(variant);
    }
}
