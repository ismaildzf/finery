package net.developer.finery.client.renderer;

import com.mojang.blaze3d.vertex.PoseStack;
import net.developer.finery.item.CapeItem;
import net.minecraft.client.model.player.PlayerModel;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.entity.state.AvatarRenderState;
import net.minecraft.world.item.ItemStack;
import top.theillusivec4.curios.api.SlotContext;
import top.theillusivec4.curios.api.SlotResult;

import java.util.List;

/**
 * Draws worn capes from Finery's own player layer instead of Curios' renderer hook. A real
 * RenderLayer receives the same pose and submit queue as the vanilla cape, which is what the
 * deferred 1.21.9+ pipeline expects; drawing from the accessory hook put the ribbon outside that
 * ordering. Curios still publishes which slots are worn on the render state.
 */
public final class CapeRenderLayer extends RenderLayer<AvatarRenderState, PlayerModel> {
    private final CapeAccessoryRenderer drawer = new CapeAccessoryRenderer();

    public CapeRenderLayer(RenderLayerParent<AvatarRenderState, PlayerModel> parent) {
        super(parent);
    }

    @Override
    public void submit(PoseStack poseStack, SubmitNodeCollector collector, int light,
                       AvatarRenderState state, float yRot, float xRot) {
        List<SlotResult> results = state.getRenderDataOrDefault(
                top.theillusivec4.curios.client.CuriosClientMod.CUSTOM_RENDER, List.of());
        for (SlotResult result : results) {
            ItemStack stack = result.stack();
            SlotContext context = result.slotContext();
            if (!(stack.getItem() instanceof CapeItem) || context.entity() == null) {
                continue;
            }
            SubmitGeometry geometry = new SubmitGeometry();
            drawer.renderCloak(stack, context, new PoseStack(), getParentModel(), geometry, light, state.partialTick);
            geometry.submit(collector, poseStack);
        }
    }
}
