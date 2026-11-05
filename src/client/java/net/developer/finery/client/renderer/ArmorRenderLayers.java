package net.developer.finery.client.renderer;

import net.minecraft.client.render.RenderLayer;
import net.minecraft.util.Identifier;

/**
 * Armor-cutout render layer lookup.
 *
 * VERSION NOTE: 1.21.11 moved the armor layer helpers from RenderLayer to
 * RenderLayers; this helper keeps renderer code identical across versions.
 */
public final class ArmorRenderLayers {

    private ArmorRenderLayers() {}

    public static RenderLayer armorCutoutNoCull(Identifier texture) {
        //? if <1.21.11 {
        /*return RenderLayer.getArmorCutoutNoCull(texture);
        *///?} else {
        return net.minecraft.client.render.RenderLayers.armorCutoutNoCull(texture);
        //?}
    }
}
