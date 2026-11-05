package net.developer.finery.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import org.joml.Matrix4f;
import top.theillusivec4.curios.api.SlotContext;
import top.theillusivec4.curios.api.client.ICurioRenderer;

public final class TestCurioRenderer implements ICurioRenderer {
    private static final ResourceLocation TEXTURE =
            new ResourceLocation("finery", "textures/item/azure_cape.png");

    @Override
    public <T extends LivingEntity, M extends EntityModel<T>> void render(
            ItemStack stack, SlotContext slotContext, PoseStack poseStack,
            RenderLayerParent<T, M> renderLayerParent, MultiBufferSource buffer,
            int light, float limbSwing, float limbSwingAmount, float partialTicks,
            float ageInTicks, float netHeadYaw, float headPitch) {
        ICurioRenderer.translateIfSneaking(poseStack, slotContext.entity());
        ICurioRenderer.rotateIfSneaking(poseStack, slotContext.entity());
        poseStack.pushPose();
        poseStack.translate(0.0D, 1.1D, 0.18D);
        Matrix4f pose = poseStack.last().pose();
        VertexConsumer vertices = buffer.getBuffer(RenderType.entityCutoutNoCull(TEXTURE));
        vertices.vertex(pose, -0.25F, 0.0F, 0.0F).color(255, 255, 255, 255).uv(0.0F, 1.0F)
                .overlayCoords(OverlayTexture.NO_OVERLAY).uv2(light).normal(0.0F, 0.0F, 1.0F).endVertex();
        vertices.vertex(pose, 0.25F, 0.0F, 0.0F).color(255, 255, 255, 255).uv(1.0F, 1.0F)
                .overlayCoords(OverlayTexture.NO_OVERLAY).uv2(light).normal(0.0F, 0.0F, 1.0F).endVertex();
        vertices.vertex(pose, 0.25F, 0.7F, 0.0F).color(255, 255, 255, 255).uv(1.0F, 0.0F)
                .overlayCoords(OverlayTexture.NO_OVERLAY).uv2(light).normal(0.0F, 0.0F, 1.0F).endVertex();
        vertices.vertex(pose, -0.25F, 0.7F, 0.0F).color(255, 255, 255, 255).uv(0.0F, 0.0F)
                .overlayCoords(OverlayTexture.NO_OVERLAY).uv2(light).normal(0.0F, 0.0F, 1.0F).endVertex();
        poseStack.popPose();
    }
}
