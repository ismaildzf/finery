package net.developer.finery.client.renderer.neck;

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
import org.joml.Vector4f;

//?}
import net.developer.finery.client.CosmeticAdjustments;
import net.developer.finery.client.renderer.ArmorRenderLayers;
import net.developer.finery.client.renderer.EntityLayerFlush;
import net.developer.finery.item.CosmeticDye;
import net.developer.finery.item.NeckItem;
import net.fabricmc.api.EnvType;
import net.fabricmc.api.Environment;
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
import net.minecraft.util.math.RotationAxis;
import org.joml.Matrix4f;
import org.joml.Vector3f;

/**
 * Renders the neckwear as smooth custom meshes anchored to the body:
 *  - scarves: two soft wraps around the neck base, a compact side knot and two
 *    long fringed tails that hang down the chest and sway gently
 *  - necklaces: a closed chain loop that hugs the neck and dips to a pendant
 *  - cords (the old torcs): the same loop in a thicker braided cord
 *
 * The player model's body pivot sits exactly at the neck line (y=0 in body
 * space, +y downwards), so fabric placed around y 0..1.8 really is collar
 * height. Armor inflates the body by 1px, so every piece moves outward when a
 * chestplate is worn.
 */
//? if <1.21.5 {
/*@Environment(EnvType.CLIENT)
public class NeckAccessoryRenderer implements AccessoryRenderer {


    private static final float PX = 1.0F / 16.0F;
    private static final float TEXEL = 1.0F / 64.0F;
    private static final float TAU = (float) (Math.PI * 2.0);
    // Superellipse exponent: pulls the ring towards the square torso, like cloth
    private static final float SHAPE = 0.55F;

    private static final float TAIL_A_X = -2.45F;
    private static final float TAIL_A_Y = 1.92F;
    private static final float TAIL_A_Z = -3.06F;
    private static final float TAIL_B_X = -0.62F;
    private static final float TAIL_B_Y = 1.82F;
    private static final float TAIL_B_Z = -2.97F;

    // Keeps the scarf right under the chin instead of on the upper chest
    private static final float SCARF_LIFT = -0.62F;

    private final Vector3f normalScratch = new Vector3f();

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
        renderNeck(stack, reference, matrices, model, vertexConsumers, light, tickDelta);
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
        renderNeck(stack, reference, matrices, model, vertexConsumers, light, tickDelta);
    }
    //?}

    private void renderNeck(
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
        if (!(stack.getItem() instanceof NeckItem neckItem)) {
            return;
        }
        if (!(model instanceof PlayerEntityModel playerModel)) {
            return;
        }
        NeckRenderData.Data data = NeckRenderData.get(neckItem.getVariant());
        if (data == null) {
            return;
        }

        boolean armored = !player.getEquippedStack(EquipmentSlot.CHEST).isEmpty();

        matrices.push();
        playerModel.body.rotate(matrices);

        // per-variant nudge set by the player in the adjust screen (K)
        float[] offset = CosmeticAdjustments.get(neckItem.getVariant());
        if (offset != null) {
            matrices.translate(offset[0] / 16.0F, offset[1] / 16.0F, offset[2] / 16.0F);
        }

        BakedNeckModel.Model baked = BakedNeckModel.get(neckItem.getVariant());
        if (baked != null) {
            int dye = stack.getItem() instanceof net.developer.finery.item.DyeableNeckItem dyable
                    ? CosmeticDye.get(stack, dyable.defaultDye()) : -1;
            RenderLayer baseLayer = RenderLayer.getArmorCutoutNoCull(BakedNeckModel.texture(neckItem.getVariant()));
            VertexConsumer baseBuffer = EntityLayerFlush.begin(vertexConsumers, baseLayer);
            BakedNeckRenderer.render(baked, matrices, baseBuffer, light,
                    dye < 0 ? 0xFFFFFF : CosmeticDye.rgb(dye));
            EntityLayerFlush.end(vertexConsumers, baseLayer);
            matrices.pop();
            return;
        }

        RenderLayer neckLayer = RenderLayer.getArmorCutoutNoCull(neckItem.getNeckTexture(stack));
        VertexConsumer buffer = EntityLayerFlush.begin(vertexConsumers, neckLayer);

        switch (data.kind()) {
            case SCARF -> renderScarf(matrices, buffer, player, tickDelta, light, armored);
            case CHAIN -> renderNecklace(matrices, buffer, light, armored, data, 0.34F, 1.94F, 18.0F);
            case CORD -> renderNecklace(matrices, buffer, light, armored, data, 0.44F, 2.04F, 24.0F);
        }

        EntityLayerFlush.end(vertexConsumers, neckLayer);
        matrices.pop();
    }

    // ── scarves ─────────────────────────────────────────────────────────

    private void renderScarf(MatrixStack matrices, VertexConsumer buffer, AbstractClientPlayerEntity player,
                             float tickDelta, int light, boolean armored) {
        matrices.push();
        matrices.translate(0.0F, SCARF_LIFT * PX, 0.0F);

        float rx = armored ? 5.80F : 4.78F;
        float rz = armored ? 3.55F : 2.78F;
        float front = -rz;

        // upper wrap, right at the collar line under the chin
        band(matrices, buffer, light, rx, rz, 0.02F, 1.34F, 0.34F, 28,
                0.0F, TAU, 0.07F, 0.05F, 0.22F, 255);
        // lower wrap, slightly wider and lower: the second loop of a real scarf
        band(matrices, buffer, light, rx + 0.16F, rz + 0.12F, 0.72F, 1.78F, 0.30F, 28,
                0.18F, TAU - 0.18F, 0.09F, 0.04F, 0.10F, 238);

        // compact knot, tied a little off-centre on the player's right
        fabricBox(matrices, buffer, light, -1.72F, 1.50F, front - 0.44F,
                0.32F, 0.18F, 2.30F, 1.42F, 0.96F, 255);
        fabricBox(matrices, buffer, light, -1.48F, 1.30F, front - 0.58F,
                -0.52F, -0.30F, 1.55F, 1.82F, 0.76F, 240);

        float zShift = armored ? -0.80F : 0.0F;
        renderTail(matrices, buffer, player, tickDelta, light,
                TAIL_A_X, TAIL_A_Y, TAIL_A_Z + zShift, 9, 0.86F, 2.60F, 1.90F,
                1.35F, 1.0F, 0.0F, 16.0F, 22.0F);
        renderTail(matrices, buffer, player, tickDelta, light,
                TAIL_B_X, TAIL_B_Y, TAIL_B_Z + zShift, 7, 0.80F, 2.10F, 1.60F,
                -1.45F, -0.8F, 2.1F, 24.0F, 30.0F);

        matrices.pop();
    }

    // One long scarf tail: a thin 3D ribbon with taper, twist, fringe and sway
    private void renderTail(MatrixStack matrices, VertexConsumer buffer, AbstractClientPlayerEntity player,
                            float tickDelta, int light,
                            float originX, float originY, float originZ,
                            int slices, float sliceH, float topWidth, float endWidth,
                            float curl, float twist, float phase, float u0, float u1) {
        float time = player.age + tickDelta;
        matrices.push();
        matrices.translate(originX * PX, originY * PX, originZ * PX);

        for (int i = 0; i < slices; i++) {
            float t0 = (float) i / slices;
            float t1 = (float) (i + 1) / slices;
            float w0 = topWidth + (endWidth - topWidth) * t0;
            float w1 = topWidth + (endWidth - topWidth) * t1;
            float h = sliceH * (i == slices - 1 ? 1.35F : 1.0F);

            float sway = (float) Math.sin(Math.toRadians(time * 2.6F + phase * 60.0F + i * 24.0F));
            matrices.multiply(RotationAxis.POSITIVE_X.rotationDegrees(-1.0F + sway * 0.9F));
            matrices.multiply(RotationAxis.POSITIVE_Z.rotationDegrees(curl + sway * 0.55F));
            matrices.multiply(RotationAxis.POSITIVE_Y.rotationDegrees(twist));

            float v0 = 16.0F + 10.0F * t0;
            float v1 = 16.0F + 10.0F * t1;
            ribbonSlice(matrices, buffer, light, w0, w1, h, u0, u1, v0, v1);
            matrices.translate(0.0D, h * PX, 0.0D);
        }
        matrices.pop();
    }

    // A slice of the tail: front, back and two thin side faces
    private void ribbonSlice(MatrixStack matrices, VertexConsumer buffer, int light,
                             float w0, float w1, float h, float u0, float u1, float v0, float v1) {
        Matrix4f m = matrices.peek().getPositionMatrix();
        float hw0 = w0 / 2.0F * PX;
        float hw1 = w1 / 2.0F * PX;
        float y1 = h * PX;
        float zBack = 0.14F * PX;

        // front face
        quad(m, buffer,
                -hw0, 0.0F, 0.0F,
                hw0, 0.0F, 0.0F,
                hw1, y1, 0.0F,
                -hw1, y1, 0.0F,
                u0, v0, u1, v0, u1, v1, u0, v1, light, 255);
        // back face, UVs mirrored in x so the fringe holes line up with the front
        quad(m, buffer,
                hw0, 0.0F, zBack,
                -hw0, 0.0F, zBack,
                -hw1, y1, zBack,
                hw1, y1, zBack,
                u1, v0, u0, v0, u0, v1, u1, v1, light, 198);
        // side hems
        quad(m, buffer,
                -hw0, 0.0F, 0.0F,
                -hw0, 0.0F, zBack,
                -hw1, y1, zBack,
                -hw1, y1, 0.0F,
                u0, v0, u0 + 0.7F, v0, u0 + 0.7F, v1, u0, v1, light, 222);
        quad(m, buffer,
                hw0, 0.0F, zBack,
                hw0, 0.0F, 0.0F,
                hw1, y1, 0.0F,
                hw1, y1, zBack,
                u1 - 0.7F, v0, u1, v0, u1, v1, u1 - 0.7F, v1, light, 214);
    }

    // Cloth band around the neck: outer face plus rolled top and bottom rims
    private void band(MatrixStack matrices, VertexConsumer buffer, int light,
                      float rx, float rz, float yTop, float yBot, float thick, int segments,
                      float aStart, float aEnd, float hemWave, float ripple, float frontDip, int shade) {
        Matrix4f m = matrices.peek().getPositionMatrix();
        for (int i = 0; i < segments; i++) {
            float a0 = aStart + (aEnd - aStart) * i / segments;
            float a1 = aStart + (aEnd - aStart) * (i + 1) / segments;
            float t0 = yTop + frontDip * Math.max(0.0F, (float) Math.cos(a0));
            float t1 = yTop + frontDip * Math.max(0.0F, (float) Math.cos(a1));
            float b0 = yBot + frontDip * Math.max(0.0F, (float) Math.cos(a0))
                    + (float) Math.sin(a0 * 3.0F + 0.7F) * hemWave;
            float b1 = yBot + frontDip * Math.max(0.0F, (float) Math.cos(a1))
                    + (float) Math.sin(a1 * 3.0F + 0.7F) * hemWave;
            float r0 = ripple * (float) Math.sin(a0 * 2.0F + 1.1F);
            float r1 = ripple * (float) Math.sin(a1 * 2.0F + 1.1F);

            float sin0 = (float) Math.sin(a0);
            float cos0 = (float) Math.cos(a0);
            float sin1 = (float) Math.sin(a1);
            float cos1 = (float) Math.cos(a1);

            float o0x = (rx + r0 + thick / 2.0F) * powShape(sin0);
            float o0z = -(rz + r0 + thick / 2.0F) * powShape(cos0);
            float o1x = (rx + r1 + thick / 2.0F) * powShape(sin1);
            float o1z = -(rz + r1 + thick / 2.0F) * powShape(cos1);
            float i0x = (rx + r0 - thick / 2.0F) * powShape(sin0);
            float i0z = -(rz + r0 - thick / 2.0F) * powShape(cos0);
            float i1x = (rx + r1 - thick / 2.0F) * powShape(sin1);
            float i1z = -(rz + r1 - thick / 2.0F) * powShape(cos1);

            float u0 = 0.5F + 47.0F * i / segments;
            float u1 = 0.5F + 47.0F * (i + 1) / segments;

            quad(m, buffer,
                    o0x * PX, t0 * PX, o0z * PX,
                    o1x * PX, t1 * PX, o1z * PX,
                    o1x * PX, b1 * PX, o1z * PX,
                    o0x * PX, b0 * PX, o0z * PX,
                    u0, 0.15F, u1, 0.15F, u1, 1.85F, u0, 1.85F, light, shade);

            quad(m, buffer,
                    o0x * PX, t0 * PX, o0z * PX,
                    i0x * PX, t0 * PX, i0z * PX,
                    i1x * PX, t1 * PX, i1z * PX,
                    o1x * PX, t1 * PX, o1z * PX,
                    u0, 2.2F, u1, 2.2F, u1, 3.1F, u0, 3.1F, light, Math.max(0, shade - 14));

            quad(m, buffer,
                    i0x * PX, b0 * PX, i0z * PX,
                    o0x * PX, b0 * PX, o0z * PX,
                    o1x * PX, b1 * PX, o1z * PX,
                    i1x * PX, b1 * PX, i1z * PX,
                    u0, 3.3F, u1, 3.3F, u1, 4.2F, u0, 4.2F, light, Math.max(0, shade - 34));
        }
    }

    // Small fabric box used for the knot; each face gets its own shade
    private void fabricBox(MatrixStack matrices, VertexConsumer buffer, int light,
                           float x, float y, float z, float yaw, float roll,
                           float w, float h, float d, int shade) {
        matrices.push();
        matrices.translate(x * PX, y * PX, z * PX);
        matrices.multiply(RotationAxis.POSITIVE_Y.rotation(yaw));
        matrices.multiply(RotationAxis.POSITIVE_Z.rotation(roll));
        Matrix4f m = matrices.peek().getPositionMatrix();
        float hw = w / 2.0F * PX;
        float hh = h / 2.0F * PX;
        float hd = d / 2.0F * PX;

        // front / back
        quad(m, buffer, -hw, -hh, -hd, hw, -hh, -hd, hw, hh, -hd, -hw, hh, -hd,
                2.0F, 16.6F, 7.5F, 16.6F, 7.5F, 22.0F, 2.0F, 22.0F, light, shade);
        quad(m, buffer, hw, -hh, hd, -hw, -hh, hd, -hw, hh, hd, hw, hh, hd,
                2.0F, 16.6F, 7.5F, 16.6F, 7.5F, 22.0F, 2.0F, 22.0F, light, Math.max(0, shade - 52));
        // top / bottom
        quad(m, buffer, -hw, -hh, -hd, -hw, -hh, hd, hw, -hh, hd, hw, -hh, -hd,
                2.0F, 16.6F, 2.8F, 16.6F, 2.8F, 18.4F, 2.0F, 18.4F, light, Math.max(0, shade - 18));
        quad(m, buffer, -hw, hh, hd, -hw, hh, -hd, hw, hh, -hd, hw, hh, hd,
                2.0F, 16.6F, 2.8F, 16.6F, 2.8F, 18.4F, 2.0F, 18.4F, light, Math.max(0, shade - 72));
        // sides
        quad(m, buffer, -hw, -hh, hd, -hw, -hh, -hd, -hw, hh, -hd, -hw, hh, hd,
                2.0F, 16.6F, 2.8F, 16.6F, 2.8F, 22.0F, 2.0F, 22.0F, light, Math.max(0, shade - 35));
        quad(m, buffer, hw, -hh, -hd, hw, -hh, hd, hw, hh, hd, hw, hh, -hd,
                2.0F, 16.6F, 2.8F, 16.6F, 2.8F, 22.0F, 2.0F, 22.0F, light, Math.max(0, shade - 28));
        matrices.pop();
    }

    // ── necklaces and cord talismans ────────────────────────────────────

    private void renderNecklace(MatrixStack matrices, VertexConsumer buffer, int light,
                                boolean armored, NeckRenderData.Data data,
                                float halfWidth, float drop, float uSpan) {
        // Open U on the front of the neck: the ends rise under the chin, so the
        // loop reads as neck-sized instead of running out to the shoulders.
        float yTop = -0.28F;
        float rx = 3.15F;
        float zBase = armored ? -3.12F : -2.36F;
        int n = 16;

        float prevX = 0.0F;
        float prevY = 0.0F;
        float prevZ = 0.0F;
        for (int i = 0; i <= n; i++) {
            float t = -1.0F + 2.0F * i / n;
            float x = rx * t;
            float y = yTop + drop * (1.0F - t * t);
            float z = zBase - 0.10F * (1.0F - t * t);
            if (i > 0) {
                float u0 = 1.0F + uSpan * (i - 1) / n;
                float u1 = 1.0F + uSpan * i / n;
                Matrix4f m = matrices.peek().getPositionMatrix();
                quad(m, buffer,
                        prevX * PX, (prevY - halfWidth) * PX, prevZ * PX,
                        x * PX, (y - halfWidth) * PX, z * PX,
                        x * PX, (y + halfWidth) * PX, z * PX,
                        prevX * PX, (prevY + halfWidth) * PX, prevZ * PX,
                        u0, 0.6F, u1, 0.6F, u1, 7.4F, u0, 7.4F, light, 255);
            }
            prevX = x;
            prevY = y;
            prevZ = z;
        }

        // pendant hangs from the lowest point of the U, on the upper chest
        float top = yTop + drop + halfWidth - 0.02F + data.pendantDrop();
        float cy = top + data.pendantH() / 2.0F;
        pendantCard(matrices, buffer, 0.0F, cy, zBase - 0.26F, data, light);
    }

    // ── mesh helpers ────────────────────────────────────────────────────

    // Signed |v|^SHAPE: turns the ellipse into a soft rounded rectangle
    private static float powShape(float v) {
        if (v == 0.0F) {
            return 0.0F;
        }
        return Math.copySign((float) Math.pow(Math.abs(v), SHAPE), v);
    }

    private void pendantCard(MatrixStack matrices, VertexConsumer buffer, float x, float y, float z,
                             NeckRenderData.Data data, int light) {
        card(matrices, buffer, x, y, z, data.pendantW(), data.pendantH(),
                0.0F, 0.0F, 32.0F, 32.0F, 63.5F, 63.5F, light, 255);
        card(matrices, buffer, x, y, z + 0.12F, data.pendantW(), data.pendantH(),
                0.0F, 0.0F, 32.0F, 32.0F, 63.5F, 63.5F, light, 150);
    }

    private void card(MatrixStack matrices, VertexConsumer buffer,
                      float x, float y, float z, float w, float h, float yaw, float roll,
                      float u0, float v0, float u1, float v1, int light, int shade) {
        matrices.push();
        matrices.translate(x * PX, y * PX, z * PX);
        if (yaw != 0.0F) {
            matrices.multiply(RotationAxis.POSITIVE_Y.rotation(yaw));
        }
        if (roll != 0.0F) {
            matrices.multiply(RotationAxis.POSITIVE_Z.rotation(roll));
        }
        Matrix4f m = matrices.peek().getPositionMatrix();
        float hw = w / 2.0F * PX;
        float hh = h / 2.0F * PX;
        quad(m, buffer,
                -hw, -hh, 0.0F,
                hw, -hh, 0.0F,
                hw, hh, 0.0F,
                -hw, hh, 0.0F,
                u0, v0, u1, v0, u1, v1, u0, v1, light, shade);
        matrices.pop();
    }

    // Quad with per-corner UVs (in texels) and a computed normal
    private void quad(Matrix4f matrix, VertexConsumer buffer,
                      float x0, float y0, float z0,
                      float x1, float y1, float z1,
                      float x2, float y2, float z2,
                      float x3, float y3, float z3,
                      float u0, float v0, float u1, float v1,
                      float u2, float v2, float u3, float v3,
                      int light, int shade) {
        normalScratch.set(x1 - x0, y1 - y0, z1 - z0);
        normalScratch.cross(x3 - x0, y3 - y0, z3 - z0);
        if (normalScratch.lengthSquared() > 1.0E-8F) {
            normalScratch.normalize();
        } else {
            normalScratch.set(0.0F, 0.0F, 1.0F);
        }
        float nx = normalScratch.x();
        float ny = normalScratch.y();
        float nz = normalScratch.z();

        vertex(buffer, matrix, x0, y0, z0, u0, v0, nx, ny, nz, light, shade);
        vertex(buffer, matrix, x1, y1, z1, u1, v1, nx, ny, nz, light, shade);
        vertex(buffer, matrix, x2, y2, z2, u2, v2, nx, ny, nz, light, shade);
        vertex(buffer, matrix, x3, y3, z3, u3, v3, nx, ny, nz, light, shade);
    }

    private void vertex(VertexConsumer buffer, Matrix4f matrix, float x, float y, float z,
                        float u, float v, float nx, float ny, float nz, int light, int shade) {
        EntityLayerFlush.finish(buffer.vertex(matrix, x, y, z)
                .color(shade, shade, shade, 255)
                .texture(u * TEXEL, v * TEXEL)
                .overlay(OverlayTexture.DEFAULT_UV)
                .light(light)
                .normal(nx, ny, nz));
    }
}
*///?} else {

@Environment(EnvType.CLIENT)
public class NeckAccessoryRenderer implements AccessoryRenderer {


    private static final float PX = 1.0F / 16.0F;
    private static final float TEXEL = 1.0F / 64.0F;
    private static final float TAU = (float) (Math.PI * 2.0);
    // Superellipse exponent: pulls the ring towards the square torso, like cloth
    private static final float SHAPE = 0.55F;

    private static final float TAIL_A_X = -2.45F;
    private static final float TAIL_A_Y = 1.92F;
    private static final float TAIL_A_Z = -3.06F;
    private static final float TAIL_B_X = -0.62F;
    private static final float TAIL_B_Y = 1.82F;
    private static final float TAIL_B_Z = -2.97F;

    // Keeps the scarf right under the chin instead of on the upper chest
    private static final float SCARF_LIFT = -0.62F;

    private final Vector3f normalScratch = new Vector3f();
    private final Vector4f vertexScratch = new Vector4f();

    // Carries the living entity and worn stack through the render-state pipeline.
    private static final class NeckRenderState extends AccessoryRenderState {
        final LivingEntity entity;
        final ItemStack stack;

        NeckRenderState(LivingEntity entity, ItemStack stack) {
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
        NeckRenderState state = new NeckRenderState(entity, stack);
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
        NeckRenderState state = (NeckRenderState) accessoryState;
        LivingEntity entity = state.entity;
        ItemStack stack = state.stack;
        if (!(entity instanceof AbstractClientPlayerEntity player)) {
            return;
        }
        if (player.isInvisible()) {
            return;
        }
        if (!(stack.getItem() instanceof NeckItem neckItem)) {
            return;
        }
        if (!(model instanceof PlayerEntityModel playerModel)) {
            return;
        }
        NeckRenderData.Data data = NeckRenderData.get(neckItem.getVariant());
        if (data == null) {
            return;
        }

        int light = entityState.light;
        float time = entityState.age;
        boolean armored = !player.getEquippedStack(EquipmentSlot.CHEST).isEmpty();

        matrices.push();
        playerModel.body.applyTransform(matrices);

        // per-variant nudge set by the player in the adjust screen (K)
        float[] offset = CosmeticAdjustments.get(neckItem.getVariant());
        if (offset != null) {
            matrices.translate(offset[0] / 16.0F, offset[1] / 16.0F, offset[2] / 16.0F);
        }

        BakedNeckModel.Model baked = BakedNeckModel.get(neckItem.getVariant());
        if (baked != null) {
            int dye = stack.getItem() instanceof net.developer.finery.item.DyeableNeckItem dyable
                    ? CosmeticDye.get(stack, dyable.defaultDye()) : -1;
            int tint = dye < 0 ? 0xFFFFFF : CosmeticDye.rgb(dye);
            collector.submitCustom(matrices, ArmorRenderLayers.armorCutoutNoCull(BakedNeckModel.texture(neckItem.getVariant())),
                    (entry, buffer) -> {
                        MatrixStack local = new MatrixStack();
                        local.peek().copy(entry);
                        BakedNeckRenderer.render(baked, local, buffer, light, tint);
                    });
            matrices.pop();
            return;
        }

        collector.submitCustom(matrices, ArmorRenderLayers.armorCutoutNoCull(neckItem.getNeckTexture(stack)),
                (entry, buffer) -> {
                    Matrix4f base = entry.getPositionMatrix();
                    switch (data.kind()) {
                        case SCARF -> renderScarf(base, buffer, time, light, armored);
                        case CHAIN -> renderNecklace(base, buffer, light, armored, data, 0.34F, 1.94F, 18.0F);
                        case CORD -> renderNecklace(base, buffer, light, armored, data, 0.44F, 2.04F, 24.0F);
                    }
                });

        matrices.pop();
    }

    // ── scarves ─────────────────────────────────────────────────────────

    private void renderScarf(Matrix4f base, VertexConsumer buffer, float time, int light, boolean armored) {
        Matrix4f m = new Matrix4f(base);
        m.translate(0.0F, SCARF_LIFT * PX, 0.0F);

        float rx = armored ? 5.80F : 4.78F;
        float rz = armored ? 3.55F : 2.78F;
        float front = -rz;

        // upper wrap, right at the collar line under the chin
        band(m, buffer, light, rx, rz, 0.02F, 1.34F, 0.34F, 28,
                0.0F, TAU, 0.07F, 0.05F, 0.22F, 255);
        // lower wrap, slightly wider and lower: the second loop of a real scarf
        band(m, buffer, light, rx + 0.16F, rz + 0.12F, 0.72F, 1.78F, 0.30F, 28,
                0.18F, TAU - 0.18F, 0.09F, 0.04F, 0.10F, 238);

        // compact knot, tied a little off-centre on the player's right
        fabricBox(m, buffer, light, -1.72F, 1.50F, front - 0.44F,
                0.32F, 0.18F, 2.30F, 1.42F, 0.96F, 255);
        fabricBox(m, buffer, light, -1.48F, 1.30F, front - 0.58F,
                -0.52F, -0.30F, 1.55F, 1.82F, 0.76F, 240);

        float zShift = armored ? -0.80F : 0.0F;
        renderTail(m, buffer, time, light,
                TAIL_A_X, TAIL_A_Y, TAIL_A_Z + zShift, 9, 0.86F, 2.60F, 1.90F,
                1.35F, 1.0F, 0.0F, 16.0F, 22.0F);
        renderTail(m, buffer, time, light,
                TAIL_B_X, TAIL_B_Y, TAIL_B_Z + zShift, 7, 0.80F, 2.10F, 1.60F,
                -1.45F, -0.8F, 2.1F, 24.0F, 30.0F);
    }

    // One long scarf tail: a thin 3D ribbon with taper, twist, fringe and sway
    private void renderTail(Matrix4f base, VertexConsumer buffer, float time, int light,
                            float originX, float originY, float originZ,
                            int slices, float sliceH, float topWidth, float endWidth,
                            float curl, float twist, float phase, float u0, float u1) {
        Matrix4f m = new Matrix4f(base);
        m.translate(originX * PX, originY * PX, originZ * PX);

        for (int i = 0; i < slices; i++) {
            float t0 = (float) i / slices;
            float t1 = (float) (i + 1) / slices;
            float w0 = topWidth + (endWidth - topWidth) * t0;
            float w1 = topWidth + (endWidth - topWidth) * t1;
            float h = sliceH * (i == slices - 1 ? 1.35F : 1.0F);

            float sway = (float) Math.sin(Math.toRadians(time * 2.6F + phase * 60.0F + i * 24.0F));
            m.rotate(RotationAxis.POSITIVE_X.rotationDegrees(-1.0F + sway * 0.9F));
            m.rotate(RotationAxis.POSITIVE_Z.rotationDegrees(curl + sway * 0.55F));
            m.rotate(RotationAxis.POSITIVE_Y.rotationDegrees(twist));

            float v0 = 16.0F + 10.0F * t0;
            float v1 = 16.0F + 10.0F * t1;
            ribbonSlice(m, buffer, light, w0, w1, h, u0, u1, v0, v1);
            m.translate(0.0F, h * PX, 0.0F);
        }
    }

    // A slice of the tail: front, back and two thin side faces
    private void ribbonSlice(Matrix4f m, VertexConsumer buffer, int light,
                             float w0, float w1, float h, float u0, float u1, float v0, float v1) {
        float hw0 = w0 / 2.0F * PX;
        float hw1 = w1 / 2.0F * PX;
        float y1 = h * PX;
        float zBack = 0.14F * PX;

        // front face
        quad(m, buffer,
                -hw0, 0.0F, 0.0F,
                hw0, 0.0F, 0.0F,
                hw1, y1, 0.0F,
                -hw1, y1, 0.0F,
                u0, v0, u1, v0, u1, v1, u0, v1, light, 255);
        // back face, UVs mirrored in x so the fringe holes line up with the front
        quad(m, buffer,
                hw0, 0.0F, zBack,
                -hw0, 0.0F, zBack,
                -hw1, y1, zBack,
                hw1, y1, zBack,
                u1, v0, u0, v0, u0, v1, u1, v1, light, 198);
        // side hems
        quad(m, buffer,
                -hw0, 0.0F, 0.0F,
                -hw0, 0.0F, zBack,
                -hw1, y1, zBack,
                -hw1, y1, 0.0F,
                u0, v0, u0 + 0.7F, v0, u0 + 0.7F, v1, u0, v1, light, 222);
        quad(m, buffer,
                hw0, 0.0F, zBack,
                hw0, 0.0F, 0.0F,
                hw1, y1, 0.0F,
                hw1, y1, zBack,
                u1 - 0.7F, v0, u1, v0, u1, v1, u1 - 0.7F, v1, light, 214);
    }

    // Cloth band around the neck: outer face plus rolled top and bottom rims
    private void band(Matrix4f m, VertexConsumer buffer, int light,
                      float rx, float rz, float yTop, float yBot, float thick, int segments,
                      float aStart, float aEnd, float hemWave, float ripple, float frontDip, int shade) {
        for (int i = 0; i < segments; i++) {
            float a0 = aStart + (aEnd - aStart) * i / segments;
            float a1 = aStart + (aEnd - aStart) * (i + 1) / segments;
            float t0 = yTop + frontDip * Math.max(0.0F, (float) Math.cos(a0));
            float t1 = yTop + frontDip * Math.max(0.0F, (float) Math.cos(a1));
            float b0 = yBot + frontDip * Math.max(0.0F, (float) Math.cos(a0))
                    + (float) Math.sin(a0 * 3.0F + 0.7F) * hemWave;
            float b1 = yBot + frontDip * Math.max(0.0F, (float) Math.cos(a1))
                    + (float) Math.sin(a1 * 3.0F + 0.7F) * hemWave;
            float r0 = ripple * (float) Math.sin(a0 * 2.0F + 1.1F);
            float r1 = ripple * (float) Math.sin(a1 * 2.0F + 1.1F);

            float sin0 = (float) Math.sin(a0);
            float cos0 = (float) Math.cos(a0);
            float sin1 = (float) Math.sin(a1);
            float cos1 = (float) Math.cos(a1);

            float o0x = (rx + r0 + thick / 2.0F) * powShape(sin0);
            float o0z = -(rz + r0 + thick / 2.0F) * powShape(cos0);
            float o1x = (rx + r1 + thick / 2.0F) * powShape(sin1);
            float o1z = -(rz + r1 + thick / 2.0F) * powShape(cos1);
            float i0x = (rx + r0 - thick / 2.0F) * powShape(sin0);
            float i0z = -(rz + r0 - thick / 2.0F) * powShape(cos0);
            float i1x = (rx + r1 - thick / 2.0F) * powShape(sin1);
            float i1z = -(rz + r1 - thick / 2.0F) * powShape(cos1);

            float u0 = 0.5F + 47.0F * i / segments;
            float u1 = 0.5F + 47.0F * (i + 1) / segments;

            quad(m, buffer,
                    o0x * PX, t0 * PX, o0z * PX,
                    o1x * PX, t1 * PX, o1z * PX,
                    o1x * PX, b1 * PX, o1z * PX,
                    o0x * PX, b0 * PX, o0z * PX,
                    u0, 0.15F, u1, 0.15F, u1, 1.85F, u0, 1.85F, light, shade);

            quad(m, buffer,
                    o0x * PX, t0 * PX, o0z * PX,
                    i0x * PX, t0 * PX, i0z * PX,
                    i1x * PX, t1 * PX, i1z * PX,
                    o1x * PX, t1 * PX, o1z * PX,
                    u0, 2.2F, u1, 2.2F, u1, 3.1F, u0, 3.1F, light, Math.max(0, shade - 14));

            quad(m, buffer,
                    i0x * PX, b0 * PX, i0z * PX,
                    o0x * PX, b0 * PX, o0z * PX,
                    o1x * PX, b1 * PX, o1z * PX,
                    i1x * PX, b1 * PX, i1z * PX,
                    u0, 3.3F, u1, 3.3F, u1, 4.2F, u0, 4.2F, light, Math.max(0, shade - 34));
        }
    }

    // Small fabric box used for the knot; each face gets its own shade
    private void fabricBox(Matrix4f base, VertexConsumer buffer, int light,
                           float x, float y, float z, float yaw, float roll,
                           float w, float h, float d, int shade) {
        Matrix4f m = new Matrix4f(base);
        m.translate(x * PX, y * PX, z * PX);
        m.rotate(RotationAxis.POSITIVE_Y.rotation(yaw));
        m.rotate(RotationAxis.POSITIVE_Z.rotation(roll));
        float hw = w / 2.0F * PX;
        float hh = h / 2.0F * PX;
        float hd = d / 2.0F * PX;

        // front / back
        quad(m, buffer, -hw, -hh, -hd, hw, -hh, -hd, hw, hh, -hd, -hw, hh, -hd,
                2.0F, 16.6F, 7.5F, 16.6F, 7.5F, 22.0F, 2.0F, 22.0F, light, shade);
        quad(m, buffer, hw, -hh, hd, -hw, -hh, hd, -hw, hh, hd, hw, hh, hd,
                2.0F, 16.6F, 7.5F, 16.6F, 7.5F, 22.0F, 2.0F, 22.0F, light, Math.max(0, shade - 52));
        // top / bottom
        quad(m, buffer, -hw, -hh, -hd, -hw, -hh, hd, hw, -hh, hd, hw, -hh, -hd,
                2.0F, 16.6F, 2.8F, 16.6F, 2.8F, 18.4F, 2.0F, 18.4F, light, Math.max(0, shade - 18));
        quad(m, buffer, -hw, hh, hd, -hw, hh, -hd, hw, hh, -hd, hw, hh, hd,
                2.0F, 16.6F, 2.8F, 16.6F, 2.8F, 18.4F, 2.0F, 18.4F, light, Math.max(0, shade - 72));
        // sides
        quad(m, buffer, -hw, -hh, hd, -hw, -hh, -hd, -hw, hh, -hd, -hw, hh, hd,
                2.0F, 16.6F, 2.8F, 16.6F, 2.8F, 22.0F, 2.0F, 22.0F, light, Math.max(0, shade - 35));
        quad(m, buffer, hw, -hh, -hd, hw, -hh, hd, hw, hh, hd, hw, hh, -hd,
                2.0F, 16.6F, 2.8F, 16.6F, 2.8F, 22.0F, 2.0F, 22.0F, light, Math.max(0, shade - 28));
    }

    // ── necklaces and cord talismans ────────────────────────────────────

    private void renderNecklace(Matrix4f base, VertexConsumer buffer, int light,
                                boolean armored, NeckRenderData.Data data,
                                float halfWidth, float drop, float uSpan) {
        // Open U on the front of the neck: the ends rise under the chin, so the
        // loop reads as neck-sized instead of running out to the shoulders.
        float yTop = -0.28F;
        float rx = 3.15F;
        float zBase = armored ? -3.12F : -2.36F;
        int n = 16;

        float prevX = 0.0F;
        float prevY = 0.0F;
        float prevZ = 0.0F;
        for (int i = 0; i <= n; i++) {
            float t = -1.0F + 2.0F * i / n;
            float x = rx * t;
            float y = yTop + drop * (1.0F - t * t);
            float z = zBase - 0.10F * (1.0F - t * t);
            if (i > 0) {
                float u0 = 1.0F + uSpan * (i - 1) / n;
                float u1 = 1.0F + uSpan * i / n;
                quad(base, buffer,
                        prevX * PX, (prevY - halfWidth) * PX, prevZ * PX,
                        x * PX, (y - halfWidth) * PX, z * PX,
                        x * PX, (y + halfWidth) * PX, z * PX,
                        prevX * PX, (prevY + halfWidth) * PX, prevZ * PX,
                        u0, 0.6F, u1, 0.6F, u1, 7.4F, u0, 7.4F, light, 255);
            }
            prevX = x;
            prevY = y;
            prevZ = z;
        }

        // pendant hangs from the lowest point of the U, on the upper chest
        float top = yTop + drop + halfWidth - 0.02F + data.pendantDrop();
        float cy = top + data.pendantH() / 2.0F;
        pendantCard(base, buffer, 0.0F, cy, zBase - 0.26F, data, light);
    }

    // ── mesh helpers ────────────────────────────────────────────────────

    // Signed |v|^SHAPE: turns the ellipse into a soft rounded rectangle
    private static float powShape(float v) {
        if (v == 0.0F) {
            return 0.0F;
        }
        return Math.copySign((float) Math.pow(Math.abs(v), SHAPE), v);
    }

    private void pendantCard(Matrix4f base, VertexConsumer buffer, float x, float y, float z,
                             NeckRenderData.Data data, int light) {
        card(base, buffer, x, y, z, data.pendantW(), data.pendantH(),
                0.0F, 0.0F, 32.0F, 32.0F, 63.5F, 63.5F, light, 255);
        card(base, buffer, x, y, z + 0.12F, data.pendantW(), data.pendantH(),
                0.0F, 0.0F, 32.0F, 32.0F, 63.5F, 63.5F, light, 150);
    }

    private void card(Matrix4f base, VertexConsumer buffer,
                      float x, float y, float z, float w, float h, float yaw, float roll,
                      float u0, float v0, float u1, float v1, int light, int shade) {
        Matrix4f m = new Matrix4f(base);
        m.translate(x * PX, y * PX, z * PX);
        if (yaw != 0.0F) {
            m.rotate(RotationAxis.POSITIVE_Y.rotation(yaw));
        }
        if (roll != 0.0F) {
            m.rotate(RotationAxis.POSITIVE_Z.rotation(roll));
        }
        float hw = w / 2.0F * PX;
        float hh = h / 2.0F * PX;
        quad(m, buffer,
                -hw, -hh, 0.0F,
                hw, -hh, 0.0F,
                hw, hh, 0.0F,
                -hw, hh, 0.0F,
                u0, v0, u1, v0, u1, v1, u0, v1, light, shade);
    }

    // Quad with per-corner UVs (in texels) and a computed normal
    private void quad(Matrix4f matrix, VertexConsumer buffer,
                      float x0, float y0, float z0,
                      float x1, float y1, float z1,
                      float x2, float y2, float z2,
                      float x3, float y3, float z3,
                      float u0, float v0, float u1, float v1,
                      float u2, float v2, float u3, float v3,
                      int light, int shade) {
        normalScratch.set(x1 - x0, y1 - y0, z1 - z0);
        normalScratch.cross(x3 - x0, y3 - y0, z3 - z0);
        if (normalScratch.lengthSquared() > 1.0E-8F) {
            normalScratch.normalize();
        } else {
            normalScratch.set(0.0F, 0.0F, 1.0F);
        }
        float nx = normalScratch.x();
        float ny = normalScratch.y();
        float nz = normalScratch.z();

        vertex(buffer, matrix, x0, y0, z0, u0, v0, nx, ny, nz, light, shade);
        vertex(buffer, matrix, x1, y1, z1, u1, v1, nx, ny, nz, light, shade);
        vertex(buffer, matrix, x2, y2, z2, u2, v2, nx, ny, nz, light, shade);
        vertex(buffer, matrix, x3, y3, z3, u3, v3, nx, ny, nz, light, shade);
    }

    private void vertex(VertexConsumer buffer, Matrix4f matrix, float x, float y, float z,
                        float u, float v, float nx, float ny, float nz, int light, int shade) {
        vertexScratch.set(x, y, z, 1.0F);
        matrix.transform(vertexScratch);
        buffer.vertex(vertexScratch.x, vertexScratch.y, vertexScratch.z)
                .color(shade, shade, shade, 255)
                .texture(u * TEXEL, v * TEXEL)
                .overlay(OverlayTexture.DEFAULT_UV)
                .light(light)
                .normal(nx, ny, nz);
    }
}

//?}
