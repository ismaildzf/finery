package net.developer.finery.client.renderer.head;

//? if <1.21.10 {
import top.theillusivec4.curios.api.client.ICurioRenderer;
import top.theillusivec4.curios.api.SlotContext;
//?} else {

/*import io.wispforest.accessories.api.AccessoriesStorageLookup;
import io.wispforest.accessories.api.client.AccessoriesRenderStateKeys;
import io.wispforest.accessories.api.client.AccessoryRenderState;
import io.wispforest.accessories.api.client.renderers.AccessoryRenderer;
import io.wispforest.accessories.api.slot.SlotPath;
import net.minecraft.client.render.command.OrderedRenderCommandQueue;
import net.minecraft.client.render.entity.state.LivingEntityRenderState;

*///?}
import net.developer.finery.client.CosmeticAdjustments;
import net.developer.finery.client.renderer.ArmorRenderLayers;
import net.developer.finery.client.renderer.EntityLayerFlush;
import net.developer.finery.item.HeadItem;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.client.renderer.rendertype.RenderType;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.player.PlayerModel;
//? if >=1.21.3 {
/*import net.minecraft.client.render.entity.state.LivingEntityRenderState;
*///?}
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import com.mojang.math.Axis;
import org.joml.Matrix4f;
import org.joml.Vector3f;
import org.joml.Vector4f;

/**
 * Renders the head cosmetics: a baked 3D model (see {@link HeadModels})
 * anchored to the player's head part, plus the animated fluttering tails
 * of the headband (a small time-driven sine chain, no physics needed at
 * this scale).
 */
//? if <1.21.5 {
public class HeadAccessoryRenderer extends net.developer.finery.client.renderer.CurioRendererAdapter {

    private static final float TEXEL = 1.0F / 64.0F;
    private static final int TAIL_SLICES = 7;
    private static final float TAIL_SLICE_H = 1.35F / 16.0F;
    private static final float TAIL_WIDTH = 1.7F / 16.0F;

    private final Vector3f normalScratch = new Vector3f();

    @Override
    public void renderCurio(
            ItemStack stack,
            SlotContext reference,
            PoseStack matrices,
            EntityModel<?> model,
            MultiBufferSource vertexConsumers,
            int light,
            float tickDelta
    ) {
        renderHead(stack, reference, matrices, model, vertexConsumers, light, tickDelta);
    }

    private void renderHead(
            ItemStack stack,
            SlotContext reference,
            PoseStack matrices,
            EntityModel<?> model,
            MultiBufferSource vertexConsumers,
            int light,
            float tickDelta
    ) {
        LivingEntity entity = reference.entity();
        if (!(entity instanceof AbstractClientPlayer player)) {
            return;
        }
        if (player.isScoping()) {
            return;
        }
        if (!(stack.getItem() instanceof HeadItem headItem)) {
            return;
        }
        if (!(model instanceof PlayerModel playerModel)) {
            return;
        }

        matrices.pushPose();
        playerModel.head.translateAndRotate(matrices);

        // per-variant nudge set by the player (AdjustmentMode) to fit their skin
        float[] offset = CosmeticAdjustments.get(headItem.get());
        if (offset != null) {
            matrices.translate(offset[0] / 16.0F, offset[1] / 16.0F, offset[2] / 16.0F);
        }

        BakedHeadModel.Model baked = BakedHeadModel.get(headItem.get());
        RenderType headLayer = net.minecraft.client.renderer.rendertype.RenderTypes.entityCutoutNoCull(baked != null
                ? BakedHeadModel.texture(headItem.get())
                : headItem.getHeadTexture(stack));
        VertexConsumer buffer = EntityLayerFlush.begin(vertexConsumers, headLayer);

        if (baked != null) {
            BakedHeadRenderer.render(baked, matrices, buffer, light,
                    BakedHeadRenderer.tintOf(headItem.get(), stack), entity.tickCount + tickDelta);
        } else {
            HeadModels.get(headItem.get()).render(matrices, buffer, light, OverlayTexture.NO_OVERLAY);
            if ("headband".equals(headItem.get())) {
                renderTails(matrices, buffer, player, tickDelta, light);
            }
        }

        EntityLayerFlush.clearToast(vertexConsumers, headLayer);
        matrices.popPose();
    }

    // Two headband tails: chained slices with a traveling flutter wave
    private void renderTails(PoseStack matrices, VertexConsumer buffer,
                             AbstractClientPlayer player, float tickDelta, int light) {
        float time = player.tickCount + tickDelta;
        for (int tail = 0; tail < HeadModels.HEADBAND_TAIL_ORIGINS.length; tail++) {
            float[] origin = HeadModels.HEADBAND_TAIL_ORIGINS[tail];
            matrices.pushPose();
            matrices.translate(origin[0] / 16.0F, origin[1] / 16.0F, origin[2] / 16.0F);

            for (int i = 0; i < TAIL_SLICES; i++) {
                // gentle forward droop away from the face + traveling flutter
                float flutter = (float) Math.sin(Math.toRadians(time * 9.0F + i * 60.0F + tail * 180.0F))
                        * (2.5F + i * 0.7F);
                matrices.mulPose(Axis.XP.rotationDegrees(-6.0F + flutter));

                float u0 = 28 * TEXEL;
                float u1 = 36 * TEXEL;
                float v0 = (24 + i) * TEXEL;
                float v1 = (25 + i) * TEXEL;
                emitQuad(matrices, buffer, TAIL_WIDTH, TAIL_SLICE_H, u0, u1, v0, v1, light);
                matrices.translate(0.0D, TAIL_SLICE_H, 0.0D);
            }
            matrices.popPose();
        }
    }

    private void emitQuad(PoseStack matrices, VertexConsumer buffer,
                          float width, float height,
                          float u0, float u1, float v0, float v1, int light) {
        Matrix4f matrix = matrices.last().pose();
        matrix.transformDirection(normalScratch.set(0.0F, 0.0F, 1.0F)).normalize();

        vertex(buffer, matrix, 0.0F, 0.0F, 0.0F, u0, v0, light);
        vertex(buffer, matrix, width, 0.0F, 0.0F, u1, v0, light);
        vertex(buffer, matrix, width, height, 0.0F, u1, v1, light);
        vertex(buffer, matrix, 0.0F, height, 0.0F, u0, v1, light);
    }

    private void vertex(VertexConsumer buffer, Matrix4f matrix,
                        float x, float y, float z, float u, float v, int light) {
        EntityLayerFlush.finish(buffer.addVertex(matrix, x, y, z)
                .setColor(255, 255, 255, 255)
                .setUv(u, v)
                .setOverlay(OverlayTexture.NO_OVERLAY)
                .setLight(light)
                .setNormal(normalScratch.x, normalScratch.y, normalScratch.z));
    }
}
//?} else {

/*public class HeadAccessoryRenderer extends net.developer.finery.client.renderer.CurioRendererAdapter {

    private static final float TEXEL = 1.0F / 64.0F;
    private static final int TAIL_SLICES = 7;
    private static final float TAIL_SLICE_H = 1.35F / 16.0F;
    private static final float TAIL_WIDTH = 1.7F / 16.0F;

    private final Vector3f normalScratch = new Vector3f();
    private final Vector4f vertexScratch = new Vector4f();

    // Carries the living entity and worn stack through the render-state pipeline.
    private static final class HeadRenderState extends AccessoryRenderState {
        final LivingEntity entity;
        final ItemStack stack;

        HeadRenderState(LivingEntity entity, ItemStack stack) {
            this.entity = entity;
            this.stack = stack;
        }
    }

    @Override
    public AccessoryRenderState createRenderState(ItemStack stack, SlotPath path,
                                                  AccessoriesStorageLookup storageLookup,
                                                  LivingEntity entity, LivingEntityRenderState entityState) {
        // keep the default first-person-arm filter, then attach the entity
        if (AccessoryRenderer.super.createRenderState(stack, path, storageLookup, entity, entityState) == null) {
            return null;
        }
        HeadRenderState state = new HeadRenderState(entity, stack);
        state.setStateData(AccessoriesRenderStateKeys.ITEM_STACK, stack);
        state.setStateData(AccessoriesRenderStateKeys.SLOT_PATH, path);
        state.setStateData(AccessoriesRenderStateKeys.ENTITY_STATE, entityState);
        return state;
    }

    @Override
    public <S extends LivingEntityRenderState> void render(
            AccessoryRenderState accessoryState,
            S entityState,
            EntityModel<S> model,
            MatrixStack matrices,
            OrderedRenderCommandQueue collector
    ) {
        HeadRenderState state = (HeadRenderState) accessoryState;
        LivingEntity entity = state.entity;
        ItemStack stack = state.stack;
        if (!(entity instanceof AbstractClientPlayerEntity player)) {
            return;
        }
        if (player.isInvisible()) {
            return;
        }
        if (!(stack.getItem() instanceof HeadItem headItem)) {
            return;
        }
        if (!(model instanceof PlayerEntityModel playerModel)) {
            return;
        }

        int light = entityState.light;

        matrices.pushPose();
        playerModel.head.applyTransform(matrices);

        // per-variant nudge set by the player (AdjustmentMode) to fit their skin
        float[] offset = CosmeticAdjustments.get(headItem.getVariant());
        if (offset != null) {
            matrices.translate(offset[0] / 16.0F, offset[1] / 16.0F, offset[2] / 16.0F);
        }

        BakedHeadModel.Model baked = BakedHeadModel.get(headItem.getVariant());
        int tint = BakedHeadRenderer.tintOf(headItem.getVariant(), stack);
        collector.submitCustom(matrices, ArmorRenderLayers.armorCutoutNoCull(baked != null
                        ? BakedHeadModel.texture(headItem.getVariant())
                        : headItem.getHeadTexture(stack)),
                (entry, buffer) -> {
                    // Deferred callback: the live MatrixStack is popped by the time this
                    // runs, so rebuild the pose from the matrix captured at submit time.
                    MatrixStack local = new MatrixStack();
                    local.peek().copy(entry);
                    if (baked != null) {
                        BakedHeadRenderer.render(baked, local, buffer, light, tint, entityState.tickCount);
                    } else {
                        HeadModels.get(headItem.getVariant()).render(local, buffer, light, OverlayTexture.NO_OVERLAY);
                        if ("headband".equals(headItem.getVariant())) {
                            renderTails(local, buffer, entityState.tickCount, light);
                        }
                    }
                });

        matrices.pop();
    }

    // Two headband tails: chained slices with a traveling flutter wave.
    private void renderTails(MatrixStack matrices, VertexConsumer buffer,
                             float time, int light) {
        for (int tail = 0; tail < HeadModels.HEADBAND_TAIL_ORIGINS.length; tail++) {
            float[] origin = HeadModels.HEADBAND_TAIL_ORIGINS[tail];
            matrices.pushPose();
            matrices.translate(origin[0] / 16.0F, origin[1] / 16.0F, origin[2] / 16.0F);

            for (int i = 0; i < TAIL_SLICES; i++) {
                // gentle forward droop away from the face + traveling flutter
                float flutter = (float) Math.sin(Math.toRadians(time * 9.0F + i * 60.0F + tail * 180.0F))
                        * (2.5F + i * 0.7F);
                matrices.multiply(RotationAxis.XP.rotationDegrees(-6.0F + flutter));

                float u0 = 28 * TEXEL;
                float u1 = 36 * TEXEL;
                float v0 = (24 + i) * TEXEL;
                float v1 = (25 + i) * TEXEL;
                emitQuad(matrices, buffer, TAIL_WIDTH, TAIL_SLICE_H, u0, u1, v0, v1, light);
                matrices.translate(0.0D, TAIL_SLICE_H, 0.0D);
            }
            matrices.pop();
        }
    }

    private void emitQuad(MatrixStack matrices, VertexConsumer buffer,
                          float width, float height,
                          float u0, float u1, float v0, float v1, int light) {
        Matrix4f matrix = matrices.peek().pose();
        matrix.transformDirection(normalScratch.set(0.0F, 0.0F, 1.0F)).normalize();

        vertex(buffer, matrix, 0.0F, 0.0F, 0.0F, u0, v0, light);
        vertex(buffer, matrix, width, 0.0F, 0.0F, u1, v0, light);
        vertex(buffer, matrix, width, height, 0.0F, u1, v1, light);
        vertex(buffer, matrix, 0.0F, height, 0.0F, u0, v1, light);
    }

    private void vertex(VertexConsumer buffer, Matrix4f matrix,
                        float x, float y, float z, float u, float v, int light) {
        vertexScratch.set(x, y, z, 1.0F);
        matrix.transform(vertexScratch);
        buffer.addVertex(vertexScratch.x, vertexScratch.y, vertexScratch.z)
                .setColor(255, 255, 255, 255)
                .setUv(u, v)
                .setOverlay(OverlayTexture.NO_OVERLAY)
                .setLight(light)
                .setNormal(normalScratch.x, normalScratch.y, normalScratch.z);
    }
}

*///?}
