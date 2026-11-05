package net.developer.finery.client.mixin;

import net.minecraft.client.render.entity.LivingEntityRenderer;
import net.minecraft.client.render.entity.feature.CapeFeatureRenderer;
import net.minecraft.client.render.entity.feature.FeatureRenderer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Suppresses the vanilla CapeFeatureRenderer from being registered.
 * 
 * WHY: We handle cape rendering entirely through the Accessories API's
 * AccessoryRenderer system. If vanilla's CapeFeatureRenderer is also active,
 * players with both a Mojang cape AND our accessory cape would see double
 * rendering (two capes overlapping).
 * 
 * HOW: Intercepts LivingEntityRenderer.addFeature() at HEAD. If the feature
 * being added is the vanilla CapeFeatureRenderer, we cancel the registration.
 * 
 * SAFETY: This only blocks CapeFeatureRenderer specifically. All other
 * FeatureRenderers (armor, held items, elytra, etc.) pass through normally.
 *
 * VERSION NOTE: In Yarn, CapeFeatureRenderer keeps its name through 1.21.10+
 * (Mojang's CapeLayer rename doesn't affect Yarn mappings), and
 * LivingEntityRenderer.addFeature(FeatureRenderer) keeps the same erased
 * signature in every supported version, so this mixin needs no branching.
 */
@Mixin(LivingEntityRenderer.class)
public class VanillaCapeSuppressionMixin {

    @Inject(
            method = "addFeature",
            at = @At("HEAD"),
            cancellable = true
    )
    private void finery$suppressVanillaCape(FeatureRenderer<?, ?> feature, CallbackInfoReturnable<Boolean> cir) {
        if (feature instanceof CapeFeatureRenderer) {
            // Block vanilla cape renderer — our AccessoryRenderer handles it
            cir.setReturnValue(false);
        }
    }
}
