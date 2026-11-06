package net.developer.finery.client.renderer;

import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;
import net.minecraft.world.item.ItemStack;
import top.theillusivec4.curios.api.SlotContext;
import top.theillusivec4.curios.api.client.ICurioRenderer;

/**
 * Bridges Curios' render signature to the signature Finery's renderers already use
 * (the Accessories one): Curios supplies the model parent, we hand the model itself
 * to the renderer.
 */
public abstract class CurioRendererAdapter implements ICurioRenderer {
    private static final java.util.Set<net.minecraft.world.item.Item> LOGGED =
            java.util.Collections.newSetFromMap(new java.util.concurrent.ConcurrentHashMap<>());

    @Override
    public <S extends LivingEntityRenderState, M extends EntityModel<? super S>> void render(
            ItemStack stack, SlotContext context, PoseStack poseStack, SubmitNodeCollector collector, int light,
            S state, RenderLayerParent<S, M> parent, EntityRendererProvider.Context rendererContext,
            float partialTicks, float ageInTicks) {
        logOnce(stack, context);
        SubmitGeometry geometry = new SubmitGeometry();
        renderCurio(stack, context, poseStack, parent.getModel(), geometry, light, partialTicks);
        geometry.submit(collector);
    }

    @Override
    public <S extends LivingEntityRenderState, M extends EntityModel<? super S>> void render(
            ItemStack stack, SlotContext context, PoseStack poseStack, MultiBufferSource buffer, int light,
            S state, RenderLayerParent<S, M> parent, EntityRendererProvider.Context rendererContext,
            float partialTicks, float ageInTicks) {
        logOnce(stack, context);
        renderCurio(stack, context, poseStack, parent.getModel(), buffer, light, partialTicks);
    }

    private static void logOnce(ItemStack stack, SlotContext context) {
        if (System.getProperty("finery.autotest") != null && LOGGED.add(stack.getItem())) {
            net.developer.finery.Finery.LOGGER.info("[Autotest] render call {} slot={} entity={}",
                    stack.getItem(), context.identifier(), context.entity());
        }
    }

    protected abstract void renderCurio(
            ItemStack stack, SlotContext context, PoseStack poseStack, EntityModel<?> model,
            MultiBufferSource buffer, int light, float tickDelta);
}
