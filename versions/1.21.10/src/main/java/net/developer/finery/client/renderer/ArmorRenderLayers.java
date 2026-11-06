package net.developer.finery.client.renderer;

import net.minecraft.client.renderer.RenderType;
import net.minecraft.resources.ResourceLocation;

/**
 * Armor-cutout render layer lookup.
 *
 * VERSION NOTE: 1.21.11 moved the armor layer helpers from RenderLayer to
 * RenderLayers; this helper keeps renderer code identical across versions.
 */
public final class ArmorRenderLayers {

    private ArmorRenderLayers() {}

    public static RenderType armorCutoutNoCull(ResourceLocation texture) {
        //? if <1.21.11 {
        return net.minecraft.client.renderer.RenderType.armorCutoutNoCull(texture);
        //?} else {
        /*return net.minecraft.client.renderer.RenderType.armorCutoutNoCull(texture);
        *///?}
    }
}
