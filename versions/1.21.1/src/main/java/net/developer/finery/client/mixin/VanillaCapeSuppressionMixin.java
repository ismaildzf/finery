package net.developer.finery.client.mixin;

import net.minecraft.client.renderer.entity.LivingEntityRenderer;
import net.minecraft.client.renderer.entity.layers.CapeLayer;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Keeps the vanilla Mojang cape from drawing under our Curios cape. */
@Mixin(LivingEntityRenderer.class)
public class VanillaCapeSuppressionMixin {
    @Inject(method = "addLayer", at = @At("HEAD"), cancellable = true)
    private void finery$suppressVanillaCape(RenderLayer<?, ?> layer, CallbackInfoReturnable<Boolean> cir) {
        if (layer instanceof CapeLayer) {
            cir.setReturnValue(false);
        }
    }
}
