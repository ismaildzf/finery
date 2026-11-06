package net.developer.finery.client.renderer;

import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.world.entity.LivingEntity;
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
    public <T extends LivingEntity, M extends EntityModel<T>> void render(
            ItemStack stack, SlotContext context, PoseStack poseStack, RenderLayerParent<T, M> parent,
            MultiBufferSource buffer, int light, float limbSwing, float limbSwingAmount,
            float partialTicks, float ageInTicks, float netHeadYaw, float headPitch) {
        if (System.getProperty("finery.autotest") != null && LOGGED.add(stack.getItem())) {
            net.developer.finery.Finery.LOGGER.info("[Autotest] render call {} slot={} entity={} buffer={}",
                    stack.getItem(), context.identifier(), context.entity(), buffer.getClass().getName());
        }
        renderCurio(stack, context, poseStack, parent.getModel(), buffer, light,
                limbSwing, limbSwingAmount, partialTicks, ageInTicks, netHeadYaw, headPitch);
    }

    protected abstract <M extends LivingEntity> void renderCurio(
            ItemStack stack, SlotContext context, PoseStack poseStack, EntityModel<M> model,
            MultiBufferSource buffer, int light, float limbSwing, float limbSwingAmount,
            float partialTicks, float ageInTicks, float netHeadYaw, float headPitch);
}
