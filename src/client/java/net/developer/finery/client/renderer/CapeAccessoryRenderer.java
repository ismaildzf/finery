package net.developer.finery.client.renderer;

//? if <1.21.10 {
/*import io.wispforest.accessories.api.client.AccessoryRenderer;
import io.wispforest.accessories.api.slot.SlotReference;
*///?} else {

import io.wispforest.accessories.api.AccessoriesStorageLookup;
import io.wispforest.accessories.api.client.AccessoriesRenderStateKeys;
import io.wispforest.accessories.api.client.AccessoryRenderState;
import io.wispforest.accessories.api.client.renderers.AccessoryRenderer;
import io.wispforest.accessories.api.slot.SlotPath;
import net.minecraft.client.render.command.OrderedRenderCommandQueue;
import net.minecraft.client.render.entity.state.LivingEntityRenderState;

//?}
import net.developer.finery.client.renderer.wave.CapeSimulation;
import net.developer.finery.client.renderer.wave.CapeWaveManager;
import net.developer.finery.item.CapeItem;
import net.fabricmc.api.EnvType;
import net.fabricmc.api.Environment;
import net.minecraft.client.model.ModelPart;
import net.minecraft.client.network.AbstractClientPlayerEntity;
import net.minecraft.client.render.OverlayTexture;
import net.minecraft.client.render.RenderLayer;
import net.minecraft.client.render.VertexConsumer;
import net.minecraft.client.render.VertexConsumerProvider;
import net.minecraft.client.render.entity.model.EntityModel;
import net.minecraft.client.render.entity.model.PlayerEntityModel;
//? if >=1.21.3 {
import net.minecraft.client.render.entity.state.LivingEntityRenderState;
//?}
import net.minecraft.client.util.math.MatrixStack;
import net.minecraft.entity.EquipmentSlot;
import net.minecraft.entity.LivingEntity;
import net.minecraft.item.ItemStack;
import net.minecraft.item.Items;
import net.minecraft.util.Identifier;
import net.minecraft.util.math.RotationAxis;
import org.joml.Matrix4f;
import org.joml.Vector3f;
import org.joml.Vector4f;

/**
 * Renders wavy, cloth-like capes on the player's back when equipped via the
 * Accessories API's "cape" slot.
 *
 * Geometry: the cape is a ribbon of {@link CapeSimulation#PART_COUNT} horizontal
 * slices (10px wide, 1px tall). A rope simulation produces the per-slice offset
 * and angle each frame; adjacent slices share edge matrices so the ribbon bends
 * without gaps.
 *
 * The transform pipeline (slice stacking, rotation pivots, wind flutter) is a
 * port of the SMOOTH render path of tr7zw's WaveyCapes (MIT), which itself
 * matches vanilla cape UV layout - our HD textures use the same 64x32-normalized
 * layout, so u1..11 = outside face, u12..22 = inside, u0/u11 = edges, v0 = rims.
 */
//? if <1.21.5 {
/*@Environment(EnvType.CLIENT)
public class CapeAccessoryRenderer implements AccessoryRenderer {

    private static final int PARTS = CapeSimulation.PART_COUNT;
    private static final float HALF_W = 5.0F / 16.0F;        // half of the 10px width
    private static final float HEIGHT = 1.0F;                // 16px in blocks
    private static final float DEPTH = 1.0F / 16.0F;         // 1px cloth thickness
    private static final float PART_H = 1.0F / PARTS;        // 1px per slice
    private static final float TEXEL_U = 1.0F / 64.0F;
    private static final float TEXEL_V = 1.0F / 32.0F;
    private static final int FULL_BRIGHT = 15728880;

    // per-slice render matrices + smoothed normals (render thread only)
    private final Matrix4f[] partMatrices = newMatrixArray();
    private final Vector3f[] frontNormals = newVectorArray();
    private final Vector3f[] backNormals = newVectorArray();
    private final Vector4f transformScratch = new Vector4f();
    private final Vector3f normalScratch = new Vector3f();
    private final Vector3f originScratch = new Vector3f();
    private final Vector3f edgeScratch = new Vector3f();
    private final Vector3f topScratch = new Vector3f();
    private final Vector3f bottomScratch = new Vector3f();

    private static Matrix4f[] newMatrixArray() {
        Matrix4f[] array = new Matrix4f[PARTS];
        for (int i = 0; i < PARTS; i++) {
            array[i] = new Matrix4f();
        }
        return array;
    }

    private static Vector3f[] newVectorArray() {
        Vector3f[] array = new Vector3f[PARTS];
        for (int i = 0; i < PARTS; i++) {
            array[i] = new Vector3f();
        }
        return array;
    }

    //? if <1.21.3 {
    /^@Override
    public <M extends LivingEntity> void render(
            ItemStack stack,
            SlotReference reference,
            MatrixStack matrices,
            EntityModel<M> model,
            VertexConsumerProvider vertexConsumers,
            int light,
            float limbAngle,
            float limbDistance,
            float tickDelta,
            float animationProgress,
            float headYaw,
            float headPitch
    ) {
        renderCape(stack, reference, matrices, model, vertexConsumers, light, tickDelta);
    }
    ^///?} else {
    @Override
    public <S extends LivingEntityRenderState> void render(
            ItemStack stack,
            SlotReference reference,
            MatrixStack matrices,
            EntityModel<S> model,
            S entityState,
            VertexConsumerProvider vertexConsumers,
            int light,
            float tickDelta
    ) {
        renderCape(stack, reference, matrices, model, vertexConsumers, light, tickDelta);
    }
    //?}

    private void renderCape(
            ItemStack stack,
            SlotReference reference,
            MatrixStack matrices,
            EntityModel<?> model,
            VertexConsumerProvider vertexConsumers,
            int light,
            float tickDelta
    ) {
        LivingEntity entity = reference.entity();
        if (!(entity instanceof AbstractClientPlayerEntity player)) {
            return;
        }
        if (player.isInvisible()) {
            return;
        }
        ItemStack chestItem = player.getEquippedStack(EquipmentSlot.CHEST);
        if (chestItem.isOf(Items.ELYTRA)) {
            return;
        }
        if (!(stack.getItem() instanceof CapeItem capeItem)) {
            return;
        }
        if (!(model instanceof PlayerEntityModel playerModel)) {
            return;
        }

        CapeSimulation sim = CapeWaveManager.obtain(player);
        Identifier capeTexture = capeItem.getCapeTexture();
        RenderLayer capeLayer = RenderLayer.getArmorCutoutNoCull(capeTexture);

        matrices.push();

        // attach to the torso (follows body yaw)
        ModelPart body = playerModel.body;
        body.rotate(matrices);

        // chestplate offset compensation (same as before)
        if (!chestItem.isEmpty()) {
            matrices.translate(0.0D, -0.053125D, 0.06875D);
        }

        // pass 1: capture one matrix per slice from the rope simulation
        for (int part = 0; part < PARTS; part++) {
            poseSlice(matrices, sim, tickDelta, part);
            partMatrices[part].set(matrices.peek().getPositionMatrix());
            matrices.pop();
        }

        // per-slice face normals for smooth lighting across bends
        boolean inverse = light == FULL_BRIGHT;
        for (int part = 0; part < PARTS; part++) {
            float bottom = (part + 1) * PART_H;
            float top = part * PART_H;
            Matrix4f prev = partMatrices[Math.max(part - 1, 0)];
            getNormal(prev, prev, partMatrices[part],
                    HALF_W, top, -DEPTH,
                    -HALF_W, top, -DEPTH,
                    HALF_W, bottom, -DEPTH,
                    inverse, frontNormals[part]);
            getNormal(prev, prev, partMatrices[part],
                    HALF_W, bottom, 0.0F,
                    -HALF_W, bottom, 0.0F,
                    HALF_W, top, 0.0F,
                    inverse, backNormals[part]);
        }

        VertexConsumer buffer = EntityLayerFlush.begin(vertexConsumers, capeLayer);
        emitRibbon(buffer, light);
        EntityLayerFlush.end(vertexConsumers, capeLayer);

        matrices.pop();
    }

    // ── per-slice pose (port of WaveyCapes modifyPoseStackSimulation) ───

    private void poseSlice(MatrixStack matrices, CapeSimulation sim, float delta, int part) {
        matrices.push();
        matrices.translate(0.0D, 0.0D, 0.125D);

        float x = sim.lerpX(part, delta) - sim.lerpX(0, delta);
        if (x > 0.0F) {
            x = 0.0F;
        }
        float y = sim.lerpY(0, delta) - part - sim.lerpY(part, delta);

        float wind = naturalWind(part);
        float partRotation = getRotation(sim, delta, part);

        matrices.multiply(RotationAxis.POSITIVE_X.rotationDegrees(6.0F + wind));
        matrices.multiply(RotationAxis.POSITIVE_Y.rotationDegrees(180.0F));
        matrices.translate(0.0D, y / 16.0D, x / 16.0D);     // rope displacement
        matrices.translate(0.0D, 0.48D / 16.0D, -0.48D / 16.0D);
        matrices.translate(0.0D, part * PART_H, 0.0D);     // pivot at this slice's top
        matrices.multiply(RotationAxis.POSITIVE_X.rotationDegrees(-partRotation));
        matrices.translate(0.0D, -part * PART_H, 0.0D);
        matrices.translate(0.0D, -0.48D / 16.0D, 0.48D / 16.0D);
    }

    private static float getRotation(CapeSimulation sim, float delta, int part) {
        if (part == PARTS - 1) {
            part = PARTS - 2;
        }
        float ax = sim.lerpX(part, delta);
        float ay = sim.lerpY(part, delta);
        float bx = sim.lerpX(part + 1, delta);
        float by = sim.lerpY(part + 1, delta);
        return (float) Math.toDegrees(Math.atan2(bx - ax, by - ay)) + 180.0F;
    }

    // Traveling wind wave across the slices (idle flutter)
    private static float naturalWind(int part) {
        long highlightedPart = (System.currentTimeMillis() / 3L) % 360L;
        float relativePart = (part + 1) / (float) PARTS;
        return (float) (Math.sin(Math.toRadians(relativePart * 360.0F - highlightedPart)) * 4.0F);
    }

    // ── ribbon emission (port of WaveyCapes renderSmoothCape) ───────────

    private void emitRibbon(VertexConsumer buffer, int light) {
        for (int part = 0; part < PARTS; part++) {
            float minV = TEXEL_V * (part + 1);
            float maxV = minV + TEXEL_V;
            Matrix4f current = partMatrices[part];
            Matrix4f prev = partMatrices[Math.max(part - 1, 0)];
            float top = part * PART_H;
            float bottom = (part + 1) * PART_H;

            // top cap (samples the collar rim row)
            if (part == 0) {
                getNormal(current, current, current,
                        HALF_W, 0.0F, 0.0F,
                        -HALF_W, 0.0F, 0.0F,
                        HALF_W, 0.0F, DEPTH,
                        light == FULL_BRIGHT, normalScratch);
                vertex(buffer, current, HALF_W, 0.0F, 0.0F, 11 * TEXEL_U, TEXEL_V, normalScratch, light);
                vertex(buffer, current, -HALF_W, 0.0F, 0.0F, 1 * TEXEL_U, TEXEL_V, normalScratch, light);
                vertex(buffer, current, -HALF_W, 0.0F, -DEPTH, 1 * TEXEL_U, 0.0F, normalScratch, light);
                vertex(buffer, current, HALF_W, 0.0F, -DEPTH, 11 * TEXEL_U, 0.0F, normalScratch, light);
            }

            // bottom cap (samples the hem rim row)
            if (part == PARTS - 1) {
                getNormal(current, current, current,
                        HALF_W, HEIGHT, -DEPTH,
                        -HALF_W, HEIGHT, -DEPTH,
                        HALF_W, HEIGHT, 0.0F,
                        light == FULL_BRIGHT, normalScratch);
                vertex(buffer, current, HALF_W, HEIGHT, -DEPTH, 21 * TEXEL_U, 0.0F, normalScratch, light);
                vertex(buffer, current, -HALF_W, HEIGHT, -DEPTH, 11 * TEXEL_U, 0.0F, normalScratch, light);
                vertex(buffer, current, -HALF_W, HEIGHT, 0.0F, 11 * TEXEL_U, TEXEL_V, normalScratch, light);
                vertex(buffer, current, HALF_W, HEIGHT, 0.0F, 21 * TEXEL_U, TEXEL_V, normalScratch, light);
            }

            // left edge (u0 strip)
            getNormal(current, current, prev,
                    -HALF_W, bottom, 0.0F,
                    -HALF_W, bottom, -DEPTH,
                    -HALF_W, top, 0.0F,
                    light == FULL_BRIGHT, normalScratch);
            vertex(buffer, current, -HALF_W, bottom, 0.0F, 0.0F, maxV, normalScratch, light);
            vertex(buffer, current, -HALF_W, bottom, -DEPTH, TEXEL_U, maxV, normalScratch, light);
            vertex(buffer, prev, -HALF_W, top, -DEPTH, TEXEL_U, minV, normalScratch, light);
            vertex(buffer, prev, -HALF_W, top, 0.0F, 0.0F, minV, normalScratch, light);

            // right edge (u11 strip)
            getNormal(current, current, prev,
                    HALF_W, bottom, -DEPTH,
                    HALF_W, bottom, 0.0F,
                    HALF_W, top, -DEPTH,
                    light == FULL_BRIGHT, normalScratch);
            vertex(buffer, current, HALF_W, bottom, -DEPTH, 11 * TEXEL_U, maxV, normalScratch, light);
            vertex(buffer, current, HALF_W, bottom, 0.0F, 12 * TEXEL_U, maxV, normalScratch, light);
            vertex(buffer, prev, HALF_W, top, 0.0F, 12 * TEXEL_U, minV, normalScratch, light);
            vertex(buffer, prev, HALF_W, top, -DEPTH, 11 * TEXEL_U, minV, normalScratch, light);

            // front (outside) face - u1..11, smoothed normals between slices
            average(frontNormals[part], frontNormals[Math.max(part - 1, 0)], topScratch);
            average(frontNormals[part], frontNormals[Math.min(part + 1, PARTS - 1)], bottomScratch);
            vertex(buffer, prev, HALF_W, top, -DEPTH, 11 * TEXEL_U, minV, topScratch, light);
            vertex(buffer, prev, -HALF_W, top, -DEPTH, 1 * TEXEL_U, minV, topScratch, light);
            vertex(buffer, current, -HALF_W, bottom, -DEPTH, 1 * TEXEL_U, maxV, bottomScratch, light);
            vertex(buffer, current, HALF_W, bottom, -DEPTH, 11 * TEXEL_U, maxV, bottomScratch, light);

            // back (inside) face - u12..22, mirrored
            average(backNormals[part], backNormals[Math.max(part - 1, 0)], topScratch);
            average(backNormals[part], backNormals[Math.min(part + 1, PARTS - 1)], bottomScratch);
            vertex(buffer, prev, HALF_W, top, 0.0F, 12 * TEXEL_U, minV, topScratch, light);
            vertex(buffer, prev, -HALF_W, top, 0.0F, 22 * TEXEL_U, minV, topScratch, light);
            vertex(buffer, current, -HALF_W, bottom, 0.0F, 22 * TEXEL_U, maxV, bottomScratch, light);
            vertex(buffer, current, HALF_W, bottom, 0.0F, 12 * TEXEL_U, maxV, bottomScratch, light);
        }
    }

    private static void vertex(VertexConsumer buffer, Matrix4f matrix,
                               float x, float y, float z,
                               float u, float v, Vector3f normal, int light) {
        EntityLayerFlush.finish(buffer.vertex(matrix, x, y, z)
                .color(255, 255, 255, 255)
                .texture(u, v)
                .overlay(OverlayTexture.DEFAULT_UV)
                .light(light)
                .normal(normal.x, normal.y, normal.z));
    }

    // ── helpers ─────────────────────────────────────────────────────────

    private static void average(Vector3f a, Vector3f b, Vector3f dest) {
        dest.set((a.x + b.x) / 2.0F, (a.y + b.y) / 2.0F, (a.z + b.z) / 2.0F);
    }

    private void getNormal(Matrix4f m1, Matrix4f m2, Matrix4f m3,
                           float x1, float y1, float z1,
                           float x2, float y2, float z2,
                           float x3, float y3, float z3,
                           boolean inverse, Vector3f dest) {
        transform(m1, x1, y1, z1, originScratch);
        transform(m2, x2, y2, z2, normalScratch);
        normalScratch.sub(originScratch);
        transform(m3, x3, y3, z3, edgeScratch);
        edgeScratch.sub(originScratch);
        normalScratch.cross(edgeScratch);
        normalScratch.normalize();
        if (inverse) {
            normalScratch.negate();
        }
        dest.set(normalScratch.x, normalScratch.y, normalScratch.z);
    }

    private void transform(Matrix4f matrix, float x, float y, float z, Vector3f dest) {
        transformScratch.set(x, y, z, 1.0F);
        matrix.transform(transformScratch);
        dest.set(transformScratch.x, transformScratch.y, transformScratch.z);
    }
}
*///?} else {

@Environment(EnvType.CLIENT)
public class CapeAccessoryRenderer implements AccessoryRenderer {

    private static final int PARTS = CapeSimulation.PART_COUNT;
    private static final float HALF_W = 5.0F / 16.0F;        // half of the 10px width
    private static final float HEIGHT = 1.0F;                // 16px in blocks
    private static final float DEPTH = 1.0F / 16.0F;         // 1px cloth thickness
    private static final float PART_H = 1.0F / PARTS;        // 1px per slice
    private static final float TEXEL_U = 1.0F / 64.0F;
    private static final float TEXEL_V = 1.0F / 32.0F;
    private static final int FULL_BRIGHT = 15728880;

    // per-slice render matrices + smoothed normals (render thread only)
    private final Matrix4f[] partMatrices = newMatrixArray();
    private final Vector3f[] frontNormals = newVectorArray();
    private final Vector3f[] backNormals = newVectorArray();
    private final Vector4f transformScratch = new Vector4f();
    private final Vector3f vertexScratch = new Vector3f();
    private final Vector3f normalScratch = new Vector3f();
    private final Vector3f originScratch = new Vector3f();
    private final Vector3f edgeScratch = new Vector3f();
    private final Vector3f topScratch = new Vector3f();
    private final Vector3f bottomScratch = new Vector3f();

    // Carries the living entity and worn stack through the render-state pipeline.
    private static final class CapeRenderState extends AccessoryRenderState {
        final LivingEntity entity;
        final ItemStack stack;

        CapeRenderState(LivingEntity entity, ItemStack stack) {
            this.entity = entity;
            this.stack = stack;
        }
    }

    private static Matrix4f[] newMatrixArray() {
        Matrix4f[] array = new Matrix4f[PARTS];
        for (int i = 0; i < PARTS; i++) {
            array[i] = new Matrix4f();
        }
        return array;
    }

    private static Vector3f[] newVectorArray() {
        Vector3f[] array = new Vector3f[PARTS];
        for (int i = 0; i < PARTS; i++) {
            array[i] = new Vector3f();
        }
        return array;
    }

    @Override
    public AccessoryRenderState createRenderState(ItemStack stack, SlotPath path,
                                                  AccessoriesStorageLookup storageLookup,
                                                  LivingEntity entity, LivingEntityRenderState entityState) {
        // keep the default first-person-arm filter, then attach the entity
        if (AccessoryRenderer.super.createRenderState(stack, path, storageLookup, entity, entityState) == null) {
            return null;
        }
        CapeRenderState state = new CapeRenderState(entity, stack);
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
        CapeRenderState state = (CapeRenderState) accessoryState;
        LivingEntity entity = state.entity;
        ItemStack stack = state.stack;
        if (!(entity instanceof AbstractClientPlayerEntity player)) {
            return;
        }
        if (player.isInvisible()) {
            return;
        }
        ItemStack chestItem = player.getEquippedStack(EquipmentSlot.CHEST);
        if (chestItem.isOf(Items.ELYTRA)) {
            return;
        }
        if (!(stack.getItem() instanceof CapeItem capeItem)) {
            return;
        }
        if (!(model instanceof PlayerEntityModel playerModel)) {
            return;
        }

        int light = entityState.light;
        float delta = entityState.age - (float) Math.floor(entityState.age);
        CapeSimulation sim = CapeWaveManager.obtain(player);
        Identifier capeTexture = capeItem.getCapeTexture();

        matrices.push();

        // attach to the torso (follows body yaw)
        ModelPart body = playerModel.body;
        body.applyTransform(matrices);

        // chestplate offset compensation (same as before)
        if (!chestItem.isEmpty()) {
            matrices.translate(0.0D, -0.053125D, 0.06875D);
        }

        // pass 1: capture one matrix per slice from the rope simulation
        for (int part = 0; part < PARTS; part++) {
            poseSlice(matrices, sim, delta, part);
            partMatrices[part].set(matrices.peek().getPositionMatrix());
            matrices.pop();
        }

        // per-slice face normals for smooth lighting across bends
        boolean inverse = light == FULL_BRIGHT;
        for (int part = 0; part < PARTS; part++) {
            float bottom = (part + 1) * PART_H;
            float top = part * PART_H;
            Matrix4f prev = partMatrices[Math.max(part - 1, 0)];
            getNormal(prev, prev, partMatrices[part],
                    HALF_W, top, -DEPTH,
                    -HALF_W, top, -DEPTH,
                    HALF_W, bottom, -DEPTH,
                    inverse, frontNormals[part]);
            getNormal(prev, prev, partMatrices[part],
                    HALF_W, bottom, 0.0F,
                    -HALF_W, bottom, 0.0F,
                    HALF_W, top, 0.0F,
                    inverse, backNormals[part]);
        }

        collector.submitCustom(matrices, ArmorRenderLayers.armorCutoutNoCull(capeTexture),
                (entry, buffer) -> emitRibbon(buffer, light));

        matrices.pop();
    }

    // ── per-slice pose (port of WaveyCapes modifyPoseStackSimulation) ───

    private void poseSlice(MatrixStack matrices, CapeSimulation sim, float delta, int part) {
        matrices.push();
        matrices.translate(0.0D, 0.0D, 0.125D);

        float x = sim.lerpX(part, delta) - sim.lerpX(0, delta);
        if (x > 0.0F) {
            x = 0.0F;
        }
        float y = sim.lerpY(0, delta) - part - sim.lerpY(part, delta);

        float wind = naturalWind(part);
        float partRotation = getRotation(sim, delta, part);

        matrices.multiply(RotationAxis.POSITIVE_X.rotationDegrees(6.0F + wind));
        matrices.multiply(RotationAxis.POSITIVE_Y.rotationDegrees(180.0F));
        matrices.translate(0.0D, y / 16.0D, x / 16.0D);     // rope displacement
        matrices.translate(0.0D, 0.48D / 16.0D, -0.48D / 16.0D);
        matrices.translate(0.0D, part * PART_H, 0.0D);     // pivot at this slice's top
        matrices.multiply(RotationAxis.POSITIVE_X.rotationDegrees(-partRotation));
        matrices.translate(0.0D, -part * PART_H, 0.0D);
        matrices.translate(0.0D, -0.48D / 16.0D, 0.48D / 16.0D);
    }

    private static float getRotation(CapeSimulation sim, float delta, int part) {
        if (part == PARTS - 1) {
            part = PARTS - 2;
        }
        float ax = sim.lerpX(part, delta);
        float ay = sim.lerpY(part, delta);
        float bx = sim.lerpX(part + 1, delta);
        float by = sim.lerpY(part + 1, delta);
        return (float) Math.toDegrees(Math.atan2(bx - ax, by - ay)) + 180.0F;
    }

    // Traveling wind wave across the slices (idle flutter)
    private static float naturalWind(int part) {
        long highlightedPart = (System.currentTimeMillis() / 3L) % 360L;
        float relativePart = (part + 1) / (float) PARTS;
        return (float) (Math.sin(Math.toRadians(relativePart * 360.0F - highlightedPart)) * 4.0F);
    }

    // ── ribbon emission (port of WaveyCapes renderSmoothCape) ───────────

    private void emitRibbon(VertexConsumer buffer, int light) {
        for (int part = 0; part < PARTS; part++) {
            float minV = TEXEL_V * (part + 1);
            float maxV = minV + TEXEL_V;
            Matrix4f current = partMatrices[part];
            Matrix4f prev = partMatrices[Math.max(part - 1, 0)];
            float top = part * PART_H;
            float bottom = (part + 1) * PART_H;

            // top cap (samples the collar rim row)
            if (part == 0) {
                getNormal(current, current, current,
                        HALF_W, 0.0F, 0.0F,
                        -HALF_W, 0.0F, 0.0F,
                        HALF_W, 0.0F, DEPTH,
                        light == FULL_BRIGHT, normalScratch);
                vertex(buffer, current, HALF_W, 0.0F, 0.0F, 11 * TEXEL_U, TEXEL_V, normalScratch, light);
                vertex(buffer, current, -HALF_W, 0.0F, 0.0F, 1 * TEXEL_U, TEXEL_V, normalScratch, light);
                vertex(buffer, current, -HALF_W, 0.0F, -DEPTH, 1 * TEXEL_U, 0.0F, normalScratch, light);
                vertex(buffer, current, HALF_W, 0.0F, -DEPTH, 11 * TEXEL_U, 0.0F, normalScratch, light);
            }

            // bottom cap (samples the hem rim row)
            if (part == PARTS - 1) {
                getNormal(current, current, current,
                        HALF_W, HEIGHT, -DEPTH,
                        -HALF_W, HEIGHT, -DEPTH,
                        HALF_W, HEIGHT, 0.0F,
                        light == FULL_BRIGHT, normalScratch);
                vertex(buffer, current, HALF_W, HEIGHT, -DEPTH, 21 * TEXEL_U, 0.0F, normalScratch, light);
                vertex(buffer, current, -HALF_W, HEIGHT, -DEPTH, 11 * TEXEL_U, 0.0F, normalScratch, light);
                vertex(buffer, current, -HALF_W, HEIGHT, 0.0F, 11 * TEXEL_U, TEXEL_V, normalScratch, light);
                vertex(buffer, current, HALF_W, HEIGHT, 0.0F, 21 * TEXEL_U, TEXEL_V, normalScratch, light);
            }

            // left edge (u0 strip)
            getNormal(current, current, prev,
                    -HALF_W, bottom, 0.0F,
                    -HALF_W, bottom, -DEPTH,
                    -HALF_W, top, 0.0F,
                    light == FULL_BRIGHT, normalScratch);
            vertex(buffer, current, -HALF_W, bottom, 0.0F, 0.0F, maxV, normalScratch, light);
            vertex(buffer, current, -HALF_W, bottom, -DEPTH, TEXEL_U, maxV, normalScratch, light);
            vertex(buffer, prev, -HALF_W, top, -DEPTH, TEXEL_U, minV, normalScratch, light);
            vertex(buffer, prev, -HALF_W, top, 0.0F, 0.0F, minV, normalScratch, light);

            // right edge (u11 strip)
            getNormal(current, current, prev,
                    HALF_W, bottom, -DEPTH,
                    HALF_W, bottom, 0.0F,
                    HALF_W, top, -DEPTH,
                    light == FULL_BRIGHT, normalScratch);
            vertex(buffer, current, HALF_W, bottom, -DEPTH, 11 * TEXEL_U, maxV, normalScratch, light);
            vertex(buffer, current, HALF_W, bottom, 0.0F, 12 * TEXEL_U, maxV, normalScratch, light);
            vertex(buffer, prev, HALF_W, top, 0.0F, 12 * TEXEL_U, minV, normalScratch, light);
            vertex(buffer, prev, HALF_W, top, -DEPTH, 11 * TEXEL_U, minV, normalScratch, light);

            // front (outside) face - u1..11, smoothed normals between slices
            average(frontNormals[part], frontNormals[Math.max(part - 1, 0)], topScratch);
            average(frontNormals[part], frontNormals[Math.min(part + 1, PARTS - 1)], bottomScratch);
            vertex(buffer, prev, HALF_W, top, -DEPTH, 11 * TEXEL_U, minV, topScratch, light);
            vertex(buffer, prev, -HALF_W, top, -DEPTH, 1 * TEXEL_U, minV, topScratch, light);
            vertex(buffer, current, -HALF_W, bottom, -DEPTH, 1 * TEXEL_U, maxV, bottomScratch, light);
            vertex(buffer, current, HALF_W, bottom, -DEPTH, 11 * TEXEL_U, maxV, bottomScratch, light);

            // back (inside) face - u12..22, mirrored
            average(backNormals[part], backNormals[Math.max(part - 1, 0)], topScratch);
            average(backNormals[part], backNormals[Math.min(part + 1, PARTS - 1)], bottomScratch);
            vertex(buffer, prev, HALF_W, top, 0.0F, 12 * TEXEL_U, minV, topScratch, light);
            vertex(buffer, prev, -HALF_W, top, 0.0F, 22 * TEXEL_U, minV, topScratch, light);
            vertex(buffer, current, -HALF_W, bottom, 0.0F, 22 * TEXEL_U, maxV, bottomScratch, light);
            vertex(buffer, current, HALF_W, bottom, 0.0F, 12 * TEXEL_U, maxV, bottomScratch, light);
        }
    }

    private void vertex(VertexConsumer buffer, Matrix4f matrix,
                        float x, float y, float z,
                        float u, float v, Vector3f normal, int light) {
        transform(matrix, x, y, z, vertexScratch);
        buffer.vertex(vertexScratch.x, vertexScratch.y, vertexScratch.z)
                .color(255, 255, 255, 255)
                .texture(u, v)
                .overlay(OverlayTexture.DEFAULT_UV)
                .light(light)
                .normal(normal.x, normal.y, normal.z);
    }

    // ── helpers ─────────────────────────────────────────────────────────

    private static void average(Vector3f a, Vector3f b, Vector3f dest) {
        dest.set((a.x + b.x) / 2.0F, (a.y + b.y) / 2.0F, (a.z + b.z) / 2.0F);
    }

    private void getNormal(Matrix4f m1, Matrix4f m2, Matrix4f m3,
                           float x1, float y1, float z1,
                           float x2, float y2, float z2,
                           float x3, float y3, float z3,
                           boolean inverse, Vector3f dest) {
        transform(m1, x1, y1, z1, originScratch);
        transform(m2, x2, y2, z2, normalScratch);
        normalScratch.sub(originScratch);
        transform(m3, x3, y3, z3, edgeScratch);
        edgeScratch.sub(originScratch);
        normalScratch.cross(edgeScratch);
        normalScratch.normalize();
        if (inverse) {
            normalScratch.negate();
        }
        dest.set(normalScratch.x, normalScratch.y, normalScratch.z);
    }

    private void transform(Matrix4f matrix, float x, float y, float z, Vector3f dest) {
        transformScratch.set(x, y, z, 1.0F);
        matrix.transform(transformScratch);
        dest.set(transformScratch.x, transformScratch.y, transformScratch.z);
    }
}

//?}
