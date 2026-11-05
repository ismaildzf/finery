package net.developer.finery.client.mixin;

import net.developer.finery.client.LocalSkinProvider;
import net.minecraft.client.network.AbstractClientPlayerEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Makes the local player render with the offline skin file loaded by
 * {@link LocalSkinProvider} instead of the session-less default.
 *
 * HOW: Intercepts the skin getter at HEAD. When a custom skin applies (local
 * player + config/finery/skin.png present) the returned value is replaced;
 * every other call falls through to vanilla.
 *
 * VERSION NOTE: 1.20.1 has no SkinTextures API at all (this mixin is a no-op
 * there); 1.21.1 uses getSkinTextures(); 1.21.10+ renamed the getter to
 * getSkin() and moved SkinTextures to net.minecraft.entity.player.
 */
@Mixin(AbstractClientPlayerEntity.class)
public class LocalSkinMixin {

    //? if =1.21.1 {
    /*@Inject(
            method = "getSkinTextures",
            at = @At("HEAD"),
            cancellable = true
    )
    private void finery$useLocalSkin(CallbackInfoReturnable<net.minecraft.client.util.SkinTextures> cir) {
        net.minecraft.client.util.SkinTextures local =
                LocalSkinProvider.getLocalSkin((AbstractClientPlayerEntity) (Object) this);
        if (local != null) {
            cir.setReturnValue(local);
        }
    }
    *///?} elif >=1.21.10 {
    @Inject(
            method = "getSkin",
            at = @At("HEAD"),
            cancellable = true
    )
    private void finery$useLocalSkin(CallbackInfoReturnable<net.minecraft.entity.player.SkinTextures> cir) {
        net.minecraft.entity.player.SkinTextures local =
                LocalSkinProvider.getLocalSkin((AbstractClientPlayerEntity) (Object) this);
        if (local != null) {
            cir.setReturnValue(local);
        }
    }
    //?}
}
