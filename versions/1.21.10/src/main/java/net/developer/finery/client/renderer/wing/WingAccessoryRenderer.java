package net.developer.finery.client.renderer.wing;

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
import net.developer.finery.item.WingItem;
import net.developer.finery.item.WingStyle;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.client.renderer.RenderType;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.PlayerModel;
//? if >=1.21.3 {
/*import net.minecraft.client.render.entity.state.LivingEntityRenderState;
*///?}
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import com.mojang.math.Axis;
import org.joml.Matrix4f;
import org.joml.Vector3f;
import org.joml.Vector4f;

/**
 * Legendary wing renderer.
 *
 * Angel and butterfly wings are sculpted from procedural sheets; devil and
 * dragon wings are baked meshes (bone fingers, membranes, claws) exported by
 * {@code tools/export_wings_game.py}. Every style shares a slow fore/aft pitch
 * around the shoulder plus a symmetric sweep, so the wings rock backward and
 * forward instead of only lifting.
 *
 * Local wing frame: u = outward, v = up, w = backward from the torso.
 */
//? if <1.21.5 {
public class WingAccessoryRenderer extends net.developer.finery.client.renderer.CurioRendererAdapter {

    private static final float PX = 1.0F / 16.0F;
    private static final float TEXEL = 1.0F / 64.0F;
    private static final int FULL_BRIGHT = 15728880;

    private static final float ROOT_Y = 3.00F;
    private static final float ROOT_Z = 2.55F;
    private static final float ROOT_Z_ARMOR = 3.35F;
    private static final float ROOT_X = 1.55F;
    private static final float ROOT_X_BUTTERFLY = 1.20F;

    // butterfly sheet zones
    private static final float F_U0 = 0, F_U1 = 30, F_V0 = 0, F_V1 = 30;
    private static final float H_U0 = 30, H_U1 = 50, H_V0 = 0, H_V1 = 22;
    private static final float BODY_U0 = 50, BODY_U1 = 54, BODY_V0 = 0, BODY_V1 = 14;
    private static final float MOTHGEM_U0 = 56, MOTHGEM_U1 = 58, MOTHGEM_V0 = 0, MOTHGEM_V1 = 2;

    private final Vector4f pA = new Vector4f();
    private final Vector4f pB = new Vector4f();
    private final Vector4f pC = new Vector4f();
    private final Vector3f edge1 = new Vector3f();
    private final Vector3f edge2 = new Vector3f();
    private final Vector3f normal = new Vector3f();
    private boolean liftNormals;

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
        renderWings(stack, reference, matrices, model, vertexConsumers, light, tickDelta);
    }

    private void renderWings(
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
        if (!(stack.getItem() instanceof WingItem wingItem)) {
            return;
        }
        if (!(model instanceof PlayerModel playerModel)) {
            return;
        }
        ItemStack chest = player.getItemBySlot(EquipmentSlot.CHEST);
        if (chest.is(Items.ELYTRA)) {
            return;
        }

        WingStyle style = wingItem.getOverlay();
        float rootZ = chest.isEmpty() ? ROOT_Z : ROOT_Z_ARMOR;
        float rootX = style == WingStyle.BUTTERFLY ? ROOT_X_BUTTERFLY : ROOT_X;

        float t = player.tickCount + tickDelta;
        float[] pose = pose(t, style, player);
        float raise = pose[0];
        float sweep = pose[1];
        float flap = pose[2];
        float pitch = pose[3];
        boolean airborne = isAirborne(player);

        RenderType wingLayer = net.minecraft.client.renderer.RenderType.armorCutoutNoCull(wingItem.getWingTexture());
        VertexConsumer buffer = EntityLayerFlush.begin(vertexConsumers, wingLayer);

        WingModelData.Model baked = null;
        if (style == WingStyle.DEVIL || style == WingStyle.DRAGON) {
            baked = WingModelData.get(wingItem.getWingModelPath());
        }

        matrices.pushPose();
        playerModel.body.translateAndRotate(matrices);

        float[] adjust = CosmeticAdjustments.get(wingItem.get());
        if (adjust != null) {
            matrices.translate(adjust[0] * PX, adjust[1] * PX, adjust[2] * PX);
        }

        if (style == WingStyle.BUTTERFLY) {
            renderButterflyBody(matrices, buffer, rootZ, light);
        }

        for (int side = -1; side <= 1; side += 2) {
            matrices.pushPose();
            matrices.translate(side * rootX * PX, ROOT_Y * PX, rootZ * PX);
            matrices.mulPose(Axis.YN.rotation(side * sweep));
            matrices.mulPose(Axis.ZN.rotation(side * raise));
            // shared fore/aft pitch: both wings rock back and forward together
            matrices.mulPose(Axis.XP.rotation(pitch));
            Matrix4f matrix = matrices.last().pose();
            Vector3f back = new Vector3f(0.0F, 0.0F, 1.0F);
            matrix.transformDirection(back);

            switch (style) {
                case ANGEL -> {
                    liftNormals = true;
                    renderAngel(buffer, matrix, side, light, back, t, airborne,
                            player.isSprinting());
                    liftNormals = false;
                }
                case BUTTERFLY -> renderButterflyWing(buffer, matrix, side, light, back, flap);
                case DEVIL, DRAGON -> {
                    if (baked != null) {
                        liftNormals = true;
                        int bakedLight = style == WingStyle.DRAGON ? FULL_BRIGHT : light;
                        renderBaked(buffer, matrix, side, bakedLight, back, baked);
                        liftNormals = false;
                    }
                }
            }

            matrices.popPose();
        }

        EntityLayerFlush.clearToast(vertexConsumers, wingLayer);
        matrices.popPose();
    }

    private static boolean isAirborne(AbstractClientPlayer player) {
        return !player.onGround() && !player.isInWater();
    }

    // Returns {raise, sweep, flap, pitch}. Flap is -1..1 for sheet sway
    private static float[] pose(float t, WingStyle style, AbstractClientPlayer player) {
        boolean airborne = isAirborne(player);
        boolean sneaking = player.isShiftKeyDown();

        if (style == WingStyle.ANGEL) {
            // the reference idles with a barely-there flutter, never a drop
            if (airborne) {
                float speed = player.isSprinting() ? 0.55F : 0.42F;
                float raise = 0.10F + (float) Math.sin(t * speed) * 0.13F;
                float sweep = 0.16F + (float) Math.sin(t * speed * 0.5F) * 0.07F;
                float pitch = 0.045F + (float) Math.sin(t * speed * 0.5F + 1.1F) * 0.11F;
                return new float[]{raise, sweep, (float) Math.sin(t * speed), pitch};
            }
            float raise = 0.045F + (float) Math.sin(t * 0.055F) * 0.05F;
            float sweep = (sneaking ? 0.30F : 0.16F)
                    + (float) Math.sin(t * 0.045F + 1.2F) * 0.075F;
            float pitch = 0.025F + (float) Math.sin(t * 0.045F + 0.6F) * 0.075F;
            return new float[]{raise, sweep, (float) Math.sin(t * 0.09F), pitch};
        }

        if (style == WingStyle.BUTTERFLY) {
            if (airborne) {
                float speed = 1.15F;
                float raise = 0.24F + (float) Math.sin(t * speed) * 0.55F;
                float sweep = 0.34F + (float) Math.sin(t * speed * 0.5F + 0.9F) * 0.11F;
                float pitch = 0.04F + (float) Math.sin(t * speed * 0.5F + 1.4F) * 0.16F;
                return new float[]{raise, sweep, (float) Math.sin(t * speed), pitch};
            }
            float raise = 0.38F + (float) Math.sin(t * 0.058F) * 0.05F;
            float sweep = (sneaking ? 0.72F : 0.42F)
                    + (float) Math.sin(t * 0.042F + 1.2F) * 0.085F;
            float pitch = 0.04F + (float) Math.sin(t * 0.040F + 0.4F) * 0.10F;
            return new float[]{raise, sweep, (float) Math.sin(t * 0.08F), pitch};
        }

        boolean dragon = style == WingStyle.DRAGON;
        if (airborne) {
            float speed = dragon ? 0.55F : 0.62F;
            float raise = (dragon ? 0.04F : 0.06F) + (float) Math.sin(t * speed) * (dragon ? 0.26F : 0.30F);
            float sweep = (dragon ? 0.22F : 0.26F)
                    + (float) Math.sin(t * speed * 0.5F + 0.9F) * (dragon ? 0.11F : 0.10F);
            float pitch = (dragon ? 0.07F : 0.08F)
                    + (float) Math.sin(t * speed * 0.5F + 1.4F) * (dragon ? 0.15F : 0.16F);
            return new float[]{raise, sweep, (float) Math.sin(t * speed), pitch};
        }
        float raise = (dragon ? 0.08F : 0.06F) + (float) Math.sin(t * 0.052F) * 0.045F;
        float sweep = (sneaking ? (dragon ? 0.60F : 0.55F) : (dragon ? 0.20F : 0.16F))
                + (float) Math.sin(t * 0.042F + 1.2F) * 0.08F;
        float pitch = (dragon ? 0.055F : 0.05F)
                + (float) Math.sin(t * 0.040F + 0.5F) * (dragon ? 0.10F : 0.095F);
        return new float[]{raise, sweep, (float) Math.sin(t * 0.08F), pitch};
    }

    // ── baked devil / dragon wing ────────────────────────────────────────

    private void renderBaked(VertexConsumer buffer, Matrix4f m, float side, int light,
                             Vector3f back, WingModelData.Model model) {
        int texW = 1024;
        int texH = 1024;
        if (model.textureSize != null && model.textureSize.length >= 2) {
            texW = Math.max(1, model.textureSize[0]);
            texH = Math.max(1, model.textureSize[1]);
        }
        float su = 64.0F / texW;
        float sv = 64.0F / texH;
        for (WingModelData.Quad q : model.quads) {
            if (q == null || q.v == null || q.uv == null || q.v.length < 12 || q.uv.length < 8) {
                continue;
            }
            int cr = 255;
            int cg = 255;
            int cb = 255;
            if (q.c != null && q.c.length >= 3) {
                cr = channel(q.c[0]);
                cg = channel(q.c[1]);
                cb = channel(q.c[2]);
            }
            bakedQuad(buffer, m, side, q.v, q.uv, su, sv, cr, cg, cb, light, back);
        }
    }

    private static int channel(float value) {
        return Math.max(0, Math.min(255, Math.round(value)));
    }

    private void bakedQuad(VertexConsumer buffer, Matrix4f m, float side,
                           float[] v, float[] uv, float su, float sv,
                           int cr, int cg, int cb, int light, Vector3f back) {
        calculateRelativePosition(m, side, v[0], v[1], v[2], pA);
        calculateRelativePosition(m, side, v[3], v[4], v[5], pB);
        calculateRelativePosition(m, side, v[6], v[7], v[8], pC);
        edge1.set(pB.x - pA.x, pB.y - pA.y, pB.z - pA.z);
        edge2.set(pC.x - pA.x, pC.y - pA.y, pC.z - pA.z);
        normal.set(edge1).cross(edge2);
        if (normal.lengthSquared() < 1.0E-8F) {
            normal.set(back);
        } else {
            normal.normalize();
            if (normal.dot(back) < 0.0F) {
                normal.negate();
            }
        }
        if (liftNormals) {
            normal.add(0.0F, 1.8F, 0.0F).normalize();
        }

        vertex(buffer, pA, uv[0] * su, uv[1] * sv, normal, cr, cg, cb, 255, light);
        vertex(buffer, pB, uv[2] * su, uv[3] * sv, normal, cr, cg, cb, 255, light);
        vertex(buffer, pC, uv[4] * su, uv[5] * sv, normal, cr, cg, cb, 255, light);
        calculateRelativePosition(m, side, v[9], v[10], v[11], pA);
        vertex(buffer, pA, uv[6] * su, uv[7] * sv, normal, cr, cg, cb, 255, light);
    }

    // ── angel wing (v3) ─────────────────────────────────────────────────

    // Baked in player-model pixels from tools/angelwing_v3.py: the approved
    // reference box is 23.35 px outboard and 31.2 px tall, rooted on the
    // shoulder blade. Two sheets: long pointed primaries behind, fluffy
    // coverts 0.30 px in front, each on its own slow flutter phase.
    private static final float ANGEL_U = 23.35F;
    private static final float ANGEL_V_TOP = 11.6F;
    private static final float ANGEL_V_BOT = -19.6F;
    private static final float ANGEL_BEND = 0.50F;
    private static final float ANGEL_COVERT_LIFT = 0.30F;
    private static final float ANGEL_COVERT_VMAX = 0.57F;
    private static final float ANGEL_TEX = 1024.0F;
    private static final float ANGEL_UV64 = 64.0F / ANGEL_TEX;
    private static final float ANGEL_WING_U0 = 8.0F;
    private static final float ANGEL_COVERT_U0 = 516.0F;
    private static final float ANGEL_TEX_V0 = 8.0F;
    private static final float ANGEL_TEX_W = 500.0F;
    private static final float ANGEL_TEX_H = 628.0F;

    private void renderAngel(VertexConsumer buffer, Matrix4f m, float side, int light,
                             Vector3f back, float t, boolean airborne, boolean sprinting) {
        float phase = t * (airborne ? (sprinting ? 0.50F : 0.40F) : 0.055F);
        float amp = airborne ? (sprinting ? 0.42F : 0.30F) : 0.075F;
        angelSheet(buffer, m, side, light, back, phase, amp, false);
        angelSheet(buffer, m, side, light, back, phase + 1.15F, amp * 0.7F, true);
    }

    private void angelSheet(VertexConsumer buffer, Matrix4f m, float side, int light,
                            Vector3f back, float phase, float amp, boolean covert) {
        final int nu = 12;
        final int nv = covert ? 8 : 14;
        final float vmax = covert ? ANGEL_COVERT_VMAX : 1.0F;
        P[][] grid = new P[nu + 1][nv + 1];
        for (int i = 0; i <= nu; i++) {
            float tu = i / (float) nu;
            for (int j = 0; j <= nv; j++) {
                float tv = j / (float) nv * vmax;
                float u = ANGEL_U * (1.0F - tu);
                float v = ANGEL_V_TOP - tv * (ANGEL_V_TOP - ANGEL_V_BOT);
                float w = 0.07F + ANGEL_BEND * (float) Math.pow(1.0F - tu, 1.35F)
                        + 0.10F * (float) Math.sin(Math.PI * tv)
                        + (covert ? ANGEL_COVERT_LIFT : 0.0F);
                float hinge = (covert ? 0.010F : 0.018F) * (float) Math.sin(phase);
                float c = (float) Math.cos(hinge);
                float s = (float) Math.sin(hinge);
                float ru = u * c - v * s;
                float rv = u * s + v * c;
                float tip = (float) Math.pow(1.0F - tv, 1.5F);
                rv += amp * tip * (float) Math.sin(phase * 1.35F + u * 0.45F
                        + (covert ? 1.2F : 0.0F));
                w += 0.35F * amp * tip * (float) Math.sin(phase * 1.1F + u * 0.35F + 0.7F);
                grid[i][j] = new P(ru, rv, w);
            }
        }
        float texU0 = covert ? ANGEL_COVERT_U0 : ANGEL_WING_U0;
        for (int i = 0; i < nu; i++) {
            for (int j = 0; j < nv; j++) {
                float tu0 = i / (float) nu;
                float tu1 = (i + 1) / (float) nu;
                float tv0 = j / (float) nv * vmax;
                float tv1 = (j + 1) / (float) nv * vmax;
                putBulkData(buffer, m, side,
                        grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1],
                        angelUV(texU0 + tu0 * ANGEL_TEX_W, ANGEL_TEX_V0 + tv0 * ANGEL_TEX_H),
                        angelUV(texU0 + tu1 * ANGEL_TEX_W, ANGEL_TEX_V0 + tv0 * ANGEL_TEX_H),
                        angelUV(texU0 + tu1 * ANGEL_TEX_W, ANGEL_TEX_V0 + tv1 * ANGEL_TEX_H),
                        angelUV(texU0 + tu0 * ANGEL_TEX_W, ANGEL_TEX_V0 + tv1 * ANGEL_TEX_H),
                        light, back);
            }
        }
    }

    private static UV angelUV(float px, float py) {
        return new UV(px * ANGEL_UV64, py * ANGEL_UV64);
    }

    // ── butterfly wing ───────────────────────────────────────────────────

    private void renderButterflyWing(VertexConsumer buffer, Matrix4f m, float side, int light,
                                     Vector3f back, float flap) {
        float flex = flap * 4.0F;

        mothCard(buffer, m, side,
                0.1F, -10.6F, 10.2F, -10.2F, 10.2F, 0.4F, 0.1F, 0.6F,
                0.0F,
                -0.36F, -0.30F, -0.18F, 0.06F,
                H_U0, H_V0, H_U1, H_V1, light, back);

        mothCard(buffer, m, side,
                0.2F, -0.4F, 13.0F, -0.2F, 13.3F, 12.4F, 0.2F, 11.6F,
                -14.0F + flex * 0.7F,
                0.0F, 0.15F, 0.10F, 0.0F,
                F_U0, F_V0, F_U1, F_V1, light, back);

        gemCross(buffer, m, side, 0.5F, 0.3F, 0.42F, 1.0F,
                MOTHGEM_U0, MOTHGEM_U1, MOTHGEM_V0, MOTHGEM_V1, light, back);
    }

    // A 2x2 curved wing card. Corners are given in order inner-low, outer-low,
    // outer-high, inner-high. UVs follow the same order. rot rotates the
    // card around its inner-low corner.
    private void mothCard(VertexConsumer buffer, Matrix4f m, float side,
                          float x0, float y0, float x1, float y1, float x2, float y2,
                          float x3, float y3, float rotDeg,
                          float w00, float w10, float w11, float w01,
                          float u0, float v0, float u1, float v1, int light, Vector3f back) {
        double ra = Math.toRadians(rotDeg);
        float ca = (float) Math.cos(ra);
        float sa = (float) Math.sin(ra);

        float[] xs = {x0, x1, x2, x3};
        float[] ys = {y0, y1, y2, y3};
        float[] ws = {w00, w10, w11, w01};
        for (int i = 0; i < 4; i++) {
            float dx = xs[i] - x0;
            float dy = ys[i] - y0;
            xs[i] = x0 + dx * ca - dy * sa;
            ys[i] = y0 + dx * sa + dy * ca;
        }

        P[] p = {new P(xs[0], ys[0], ws[0]), new P(xs[1], ys[1], ws[1]),
                new P(xs[2], ys[2], ws[2]), new P(xs[3], ys[3], ws[3])};
        P p01 = mid(p[0], p[1], 0.0F);
        P p12 = mid(p[1], p[2], 0.0F);
        P p23 = mid(p[2], p[3], 0.0F);
        P p30 = mid(p[3], p[0], 0.0F);
        P center = mid(mid(p[0], p[2], 0.0F), mid(p[1], p[3], 0.0F), 0.0F);
        center = new P(center.u, center.v, center.w + 0.24F);

        UV uv0 = new UV(u0, v1);
        UV uv1 = new UV(u1, v1);
        UV uv2 = new UV(u1, v0);
        UV uv3 = new UV(u0, v0);
        UV uv01 = uvMid(uv0, uv1);
        UV uv12 = uvMid(uv1, uv2);
        UV uv23 = uvMid(uv2, uv3);
        UV uv30 = uvMid(uv3, uv0);
        UV uvc = uvMid(uvMid(uv0, uv2), uvMid(uv1, uv3));

        putBulkData(buffer, m, side, p[0], p01, center, p30, uv0, uv01, uvc, uv30, light, back);
        putBulkData(buffer, m, side, p01, p[1], p12, center, uv01, uv1, uv12, uvc, light, back);
        putBulkData(buffer, m, side, center, p12, p[2], p23, uvc, uv12, uv2, uv23, light, back);
        putBulkData(buffer, m, side, p30, center, p23, p[3], uv30, uvc, uv23, uv3, light, back);
    }

    private void renderButterflyBody(PoseStack matrices, VertexConsumer buffer, float rootZ, int light) {
        matrices.pushPose();
        matrices.translate(0.0F, ROOT_Y * PX, rootZ * PX);
        Matrix4f m = matrices.last().pose();
        Vector3f back = new Vector3f(0.0F, 0.0F, 1.0F);
        m.transformDirection(back);

        putBulkData(buffer, m, 1.0F,
                new P(-0.72F, 1.8F, 0.12F), new P(0.72F, 1.8F, 0.12F),
                new P(0.72F, -3.9F, 0.12F), new P(-0.72F, -3.9F, 0.12F),
                new UV(BODY_U0, BODY_V1), new UV(BODY_U1, BODY_V1),
                new UV(BODY_U1, BODY_V0), new UV(BODY_U0, BODY_V0), light, back);
        putBulkData(buffer, m, 1.0F,
                new P(0.0F, 1.8F, -0.58F), new P(0.0F, 1.8F, 0.58F),
                new P(0.0F, -3.9F, 0.58F), new P(0.0F, -3.9F, -0.58F),
                new UV(BODY_U0, BODY_V1), new UV(BODY_U1, BODY_V1),
                new UV(BODY_U1, BODY_V0), new UV(BODY_U0, BODY_V0), light, back);

        matrices.popPose();
    }

    // ── shared primitives ────────────────────────────────────────────────

    private void gemCross(VertexConsumer buffer, Matrix4f m, float side,
                          float centerU, float centerV, float centerW, float size,
                          float u0, float u1, float v0, float v1, int light, Vector3f back) {
        crossCard(buffer, m, side, centerU, centerV, centerW, size, u0, u1, v0, v1,
                FULL_BRIGHT, back);
    }

    private void crossCard(VertexConsumer buffer, Matrix4f m, float side,
                           float centerU, float centerV, float centerW, float size,
                           float u0, float u1, float v0, float v1, int light, Vector3f back) {
        putBulkData(buffer, m, side,
                new P(centerU - size, centerV - size, centerW),
                new P(centerU - size, centerV + size, centerW),
                new P(centerU + size, centerV + size, centerW),
                new P(centerU + size, centerV - size, centerW),
                new UV(u0, v1), new UV(u0, v0), new UV(u1, v0), new UV(u1, v1),
                light, back);
        putBulkData(buffer, m, side,
                new P(centerU, centerV - size, centerW - size),
                new P(centerU, centerV + size, centerW - size),
                new P(centerU, centerV + size, centerW + size),
                new P(centerU, centerV - size, centerW + size),
                new UV(u0, v1), new UV(u0, v0), new UV(u1, v0), new UV(u1, v1),
                light, back);
    }

    private void putBulkData(VertexConsumer buffer, Matrix4f m, float side,
                      P a, P b, P c, P d,
                      UV ua, UV ub, UV uc, UV ud,
                      int light, Vector3f back) {
        quadTint(buffer, m, side, a, b, c, d, ua, ub, uc, ud,
                255, 255, 255, 255, light, back);
    }

    private void quadTint(VertexConsumer buffer, Matrix4f m, float side,
                          P a, P b, P c, P d,
                          UV ua, UV ub, UV uc, UV ud,
                          int cr, int cg, int cb, int ca, int light, Vector3f back) {
        calculateRelativePosition(m, side, a, pA);
        calculateRelativePosition(m, side, b, pB);
        calculateRelativePosition(m, side, c, pC);
        edge1.set(pB.x - pA.x, pB.y - pA.y, pB.z - pA.z);
        edge2.set(pC.x - pA.x, pC.y - pA.y, pC.z - pA.z);
        normal.set(edge1).cross(edge2);
        if (normal.lengthSquared() < 1.0E-8F) {
            normal.set(back);
        } else {
            normal.normalize();
            if (normal.dot(back) < 0.0F) {
                normal.negate();
            }
        }
        if (liftNormals) {
            // painted sheets carry their own shading; bias toward the sky light
            normal.add(0.0F, 1.8F, 0.0F).normalize();
        }

        vertex(buffer, pA, ua.u, ua.v, normal, cr, cg, cb, ca, light);
        vertex(buffer, pB, ub.u, ub.v, normal, cr, cg, cb, ca, light);
        vertex(buffer, pC, uc.u, uc.v, normal, cr, cg, cb, ca, light);
        calculateRelativePosition(m, side, d, pA);
        vertex(buffer, pA, ud.u, ud.v, normal, cr, cg, cb, ca, light);
    }

    private static void calculateRelativePosition(Matrix4f matrix, float side, P p, Vector4f dest) {
        calculateRelativePosition(matrix, side, p.u, p.v, p.w, dest);
    }

    private static void calculateRelativePosition(Matrix4f matrix, float side,
                                  float u, float v, float w, Vector4f dest) {
        dest.set(side * u * PX, -v * PX, w * PX, 1.0F);
        matrix.transform(dest);
    }

    private static void vertex(VertexConsumer buffer, Vector4f p, float u, float v,
                               Vector3f normal, int cr, int cg, int cb, int ca, int light) {
        EntityLayerFlush.finish(buffer.addVertex(p.x, p.y, p.z)
                .setColor(cr, cg, cb, ca)
                .setUv(u * TEXEL, v * TEXEL)
                .setOverlay(OverlayTexture.NO_OVERLAY)
                .setLight(light)
                .setNormal(normal.x, normal.y, normal.z));
    }

    private static P mid(P a, P b, float wPush) {
        return new P((a.u + b.u) * 0.5F, (a.v + b.v) * 0.5F,
                (a.w + b.w) * 0.5F + wPush);
    }

    private static UV uvMid(UV a, UV b) {
        return new UV((a.u + b.u) * 0.5F, (a.v + b.v) * 0.5F);
    }

    private record P(float u, float v, float w) {
    }

    private record UV(float u, float v) {
    }
}
//?} else {

/*public class WingAccessoryRenderer extends net.developer.finery.client.renderer.CurioRendererAdapter {

    private static final float PX = 1.0F / 16.0F;
    private static final float TEXEL = 1.0F / 64.0F;
    private static final int FULL_BRIGHT = 15728880;

    private static final float ROOT_Y = 3.00F;
    private static final float ROOT_Z = 2.55F;
    private static final float ROOT_Z_ARMOR = 3.35F;
    private static final float ROOT_X = 1.55F;
    private static final float ROOT_X_BUTTERFLY = 1.20F;

    // butterfly sheet zones
    private static final float F_U0 = 0, F_U1 = 30, F_V0 = 0, F_V1 = 30;
    private static final float H_U0 = 30, H_U1 = 50, H_V0 = 0, H_V1 = 22;
    private static final float BODY_U0 = 50, BODY_U1 = 54, BODY_V0 = 0, BODY_V1 = 14;
    private static final float MOTHGEM_U0 = 56, MOTHGEM_U1 = 58, MOTHGEM_V0 = 0, MOTHGEM_V1 = 2;

    private final Vector4f pA = new Vector4f();
    private final Vector4f pB = new Vector4f();
    private final Vector4f pC = new Vector4f();
    private final Vector3f edge1 = new Vector3f();
    private final Vector3f edge2 = new Vector3f();
    private final Vector3f normal = new Vector3f();
    private boolean liftNormals;

    // Carries the living entity and worn stack through the render-state pipeline.
    private static final class WingRenderState extends AccessoryRenderState {
        final LivingEntity entity;
        final ItemStack stack;

        WingRenderState(LivingEntity entity, ItemStack stack) {
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
        WingRenderState state = new WingRenderState(entity, stack);
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
        WingRenderState state = (WingRenderState) accessoryState;
        LivingEntity entity = state.entity;
        ItemStack stack = state.stack;
        if (!(entity instanceof AbstractClientPlayerEntity player)) {
            return;
        }
        if (player.isInvisible()) {
            return;
        }
        if (!(stack.getItem() instanceof WingItem wingItem)) {
            return;
        }
        if (!(model instanceof PlayerEntityModel playerModel)) {
            return;
        }
        ItemStack chest = player.getItemBySlot(EquipmentSlot.CHEST);
        if (chest.is(Items.ELYTRA)) {
            return;
        }

        int light = entityState.light;
        WingStyle style = wingItem.getStyle();
        float rootZ = chest.isEmpty() ? ROOT_Z : ROOT_Z_ARMOR;
        float rootX = style == WingStyle.BUTTERFLY ? ROOT_X_BUTTERFLY : ROOT_X;

        float t = entityState.tickCount;
        float[] pose = pose(t, style, player);
        float raise = pose[0];
        float sweep = pose[1];
        float flap = pose[2];
        float pitch = pose[3];
        boolean airborne = isAirborne(player);
        boolean sprinting = player.isSprinting();

        WingModelData.Model baked = (style == WingStyle.DEVIL || style == WingStyle.DRAGON)
                ? WingModelData.get(wingItem.getWingModelPath()) : null;

        matrices.pushPose();
        playerModel.body.applyTransform(matrices);

        float[] adjust = CosmeticAdjustments.get(wingItem.getVariant());
        if (adjust != null) {
            matrices.translate(adjust[0] * PX, adjust[1] * PX, adjust[2] * PX);
        }

        if (style == WingStyle.BUTTERFLY) {
            matrices.pushPose();
            matrices.translate(0.0F, ROOT_Y * PX, rootZ * PX);
            collector.submitCustom(matrices, ArmorRenderLayers.armorCutoutNoCull(wingItem.getWingTexture()),
                    (entry, buffer) -> {
                        Matrix4f m = entry.pose();
                        emitButterflyBody(buffer, m, light);
                    });
            matrices.pop();
        }

        for (int side = -1; side <= 1; side += 2) {
            float fSide = side;
            matrices.pushPose();
            matrices.translate(side * rootX * PX, ROOT_Y * PX, rootZ * PX);
            matrices.multiply(RotationAxis.YN.rotation(side * sweep));
            matrices.multiply(RotationAxis.ZN.rotation(side * raise));
            // shared fore/aft pitch: both wings rock back and forward together
            matrices.multiply(RotationAxis.XP.rotation(pitch));
            collector.submitCustom(matrices, ArmorRenderLayers.armorCutoutNoCull(wingItem.getWingTexture()),
                    (entry, buffer) -> {
                        Matrix4f matrix = entry.pose();
                        Vector3f back = new Vector3f(0.0F, 0.0F, 1.0F);
                        matrix.transformDirection(back);

                        switch (style) {
                            case ANGEL -> {
                                liftNormals = true;
                                renderAngel(buffer, matrix, fSide, light, back, t, airborne, sprinting);
                                liftNormals = false;
                            }
                            case BUTTERFLY -> renderButterflyWing(buffer, matrix, fSide, light, back, flap);
                            case DEVIL, DRAGON -> {
                                if (baked != null) {
                                    liftNormals = true;
                                    int bakedLight = style == WingStyle.DRAGON ? FULL_BRIGHT : light;
                                    renderBaked(buffer, matrix, fSide, bakedLight, back, baked);
                                    liftNormals = false;
                                }
                            }
                        }
                    });
            matrices.pop();
        }

        matrices.pop();
    }

    private static boolean isAirborne(AbstractClientPlayerEntity player) {
        return !player.isOnGround() && !player.isTouchingWater();
    }

    // Returns {raise, sweep, flap, pitch}. Flap is -1..1 for sheet sway
    private static float[] pose(float t, WingStyle style, AbstractClientPlayerEntity player) {
        boolean airborne = isAirborne(player);
        boolean sneaking = player.isSneaking();

        if (style == WingStyle.ANGEL) {
            // the reference idles with a barely-there flutter, never a drop
            if (airborne) {
                float speed = player.isSprinting() ? 0.55F : 0.42F;
                float raise = 0.10F + (float) Math.sin(t * speed) * 0.13F;
                float sweep = 0.16F + (float) Math.sin(t * speed * 0.5F) * 0.07F;
                float pitch = 0.045F + (float) Math.sin(t * speed * 0.5F + 1.1F) * 0.11F;
                return new float[]{raise, sweep, (float) Math.sin(t * speed), pitch};
            }
            float raise = 0.045F + (float) Math.sin(t * 0.055F) * 0.05F;
            float sweep = (sneaking ? 0.30F : 0.16F)
                    + (float) Math.sin(t * 0.045F + 1.2F) * 0.075F;
            float pitch = 0.025F + (float) Math.sin(t * 0.045F + 0.6F) * 0.075F;
            return new float[]{raise, sweep, (float) Math.sin(t * 0.09F), pitch};
        }

        if (style == WingStyle.BUTTERFLY) {
            if (airborne) {
                float speed = 1.15F;
                float raise = 0.24F + (float) Math.sin(t * speed) * 0.55F;
                float sweep = 0.34F + (float) Math.sin(t * speed * 0.5F + 0.9F) * 0.11F;
                float pitch = 0.04F + (float) Math.sin(t * speed * 0.5F + 1.4F) * 0.16F;
                return new float[]{raise, sweep, (float) Math.sin(t * speed), pitch};
            }
            float raise = 0.38F + (float) Math.sin(t * 0.058F) * 0.05F;
            float sweep = (sneaking ? 0.72F : 0.42F)
                    + (float) Math.sin(t * 0.042F + 1.2F) * 0.085F;
            float pitch = 0.04F + (float) Math.sin(t * 0.040F + 0.4F) * 0.10F;
            return new float[]{raise, sweep, (float) Math.sin(t * 0.08F), pitch};
        }

        boolean dragon = style == WingStyle.DRAGON;
        if (airborne) {
            float speed = dragon ? 0.55F : 0.62F;
            float raise = (dragon ? 0.04F : 0.06F) + (float) Math.sin(t * speed) * (dragon ? 0.26F : 0.30F);
            float sweep = (dragon ? 0.22F : 0.26F)
                    + (float) Math.sin(t * speed * 0.5F + 0.9F) * (dragon ? 0.11F : 0.10F);
            float pitch = (dragon ? 0.07F : 0.08F)
                    + (float) Math.sin(t * speed * 0.5F + 1.4F) * (dragon ? 0.15F : 0.16F);
            return new float[]{raise, sweep, (float) Math.sin(t * speed), pitch};
        }
        float raise = (dragon ? 0.08F : 0.06F) + (float) Math.sin(t * 0.052F) * 0.045F;
        float sweep = (sneaking ? (dragon ? 0.60F : 0.55F) : (dragon ? 0.20F : 0.16F))
                + (float) Math.sin(t * 0.042F + 1.2F) * 0.08F;
        float pitch = (dragon ? 0.055F : 0.05F)
                + (float) Math.sin(t * 0.040F + 0.5F) * (dragon ? 0.10F : 0.095F);
        return new float[]{raise, sweep, (float) Math.sin(t * 0.08F), pitch};
    }

    // ── baked devil / dragon wing ────────────────────────────────────────

    private void renderBaked(VertexConsumer buffer, Matrix4f m, float side, int light,
                             Vector3f back, WingModelData.Model model) {
        int texW = 1024;
        int texH = 1024;
        if (model.textureSize != null && model.textureSize.length >= 2) {
            texW = Math.max(1, model.textureSize[0]);
            texH = Math.max(1, model.textureSize[1]);
        }
        float su = 64.0F / texW;
        float sv = 64.0F / texH;
        for (WingModelData.Quad q : model.quads) {
            if (q == null || q.v == null || q.uv == null || q.v.length < 12 || q.uv.length < 8) {
                continue;
            }
            int cr = 255;
            int cg = 255;
            int cb = 255;
            if (q.c != null && q.c.length >= 3) {
                cr = channel(q.c[0]);
                cg = channel(q.c[1]);
                cb = channel(q.c[2]);
            }
            bakedQuad(buffer, m, side, q.v, q.uv, su, sv, cr, cg, cb, light, back);
        }
    }

    private static int channel(float value) {
        return Math.max(0, Math.min(255, Math.round(value)));
    }

    private void bakedQuad(VertexConsumer buffer, Matrix4f m, float side,
                           float[] v, float[] uv, float su, float sv,
                           int cr, int cg, int cb, int light, Vector3f back) {
        transform(m, side, v[0], v[1], v[2], pA);
        transform(m, side, v[3], v[4], v[5], pB);
        transform(m, side, v[6], v[7], v[8], pC);
        edge1.set(pB.x - pA.x, pB.y - pA.y, pB.z - pA.z);
        edge2.set(pC.x - pA.x, pC.y - pA.y, pC.z - pA.z);
        normal.set(edge1).cross(edge2);
        if (normal.lengthSquared() < 1.0E-8F) {
            normal.set(back);
        } else {
            normal.normalize();
            if (normal.dot(back) < 0.0F) {
                normal.negate();
            }
        }
        if (liftNormals) {
            normal.add(0.0F, 1.8F, 0.0F).normalize();
        }

        vertex(buffer, pA, uv[0] * su, uv[1] * sv, normal, cr, cg, cb, 255, light);
        vertex(buffer, pB, uv[2] * su, uv[3] * sv, normal, cr, cg, cb, 255, light);
        vertex(buffer, pC, uv[4] * su, uv[5] * sv, normal, cr, cg, cb, 255, light);
        transform(m, side, v[9], v[10], v[11], pA);
        vertex(buffer, pA, uv[6] * su, uv[7] * sv, normal, cr, cg, cb, 255, light);
    }

    // ── angel wing (v3) ─────────────────────────────────────────────────

    // Baked in player-model pixels from tools/angelwing_v3.py: the approved
    // reference box is 23.35 px outboard and 31.2 px tall, rooted on the
    // shoulder blade. Two sheets: long pointed primaries behind, fluffy
    // coverts 0.30 px in front, each on its own slow flutter phase.
    private static final float ANGEL_U = 23.35F;
    private static final float ANGEL_V_TOP = 11.6F;
    private static final float ANGEL_V_BOT = -19.6F;
    private static final float ANGEL_BEND = 0.50F;
    private static final float ANGEL_COVERT_LIFT = 0.30F;
    private static final float ANGEL_COVERT_VMAX = 0.57F;
    private static final float ANGEL_TEX = 1024.0F;
    private static final float ANGEL_UV64 = 64.0F / ANGEL_TEX;
    private static final float ANGEL_WING_U0 = 8.0F;
    private static final float ANGEL_COVERT_U0 = 516.0F;
    private static final float ANGEL_TEX_V0 = 8.0F;
    private static final float ANGEL_TEX_W = 500.0F;
    private static final float ANGEL_TEX_H = 628.0F;

    private void renderAngel(VertexConsumer buffer, Matrix4f m, float side, int light,
                             Vector3f back, float t, boolean airborne, boolean sprinting) {
        float phase = t * (airborne ? (sprinting ? 0.50F : 0.40F) : 0.055F);
        float amp = airborne ? (sprinting ? 0.42F : 0.30F) : 0.075F;
        angelSheet(buffer, m, side, light, back, phase, amp, false);
        angelSheet(buffer, m, side, light, back, phase + 1.15F, amp * 0.7F, true);
    }

    private void angelSheet(VertexConsumer buffer, Matrix4f m, float side, int light,
                            Vector3f back, float phase, float amp, boolean covert) {
        final int nu = 12;
        final int nv = covert ? 8 : 14;
        final float vmax = covert ? ANGEL_COVERT_VMAX : 1.0F;
        P[][] grid = new P[nu + 1][nv + 1];
        for (int i = 0; i <= nu; i++) {
            float tu = i / (float) nu;
            for (int j = 0; j <= nv; j++) {
                float tv = j / (float) nv * vmax;
                float u = ANGEL_U * (1.0F - tu);
                float v = ANGEL_V_TOP - tv * (ANGEL_V_TOP - ANGEL_V_BOT);
                float w = 0.07F + ANGEL_BEND * (float) Math.pow(1.0F - tu, 1.35F)
                        + 0.10F * (float) Math.sin(Math.PI * tv)
                        + (covert ? ANGEL_COVERT_LIFT : 0.0F);
                float hinge = (covert ? 0.010F : 0.018F) * (float) Math.sin(phase);
                float c = (float) Math.cos(hinge);
                float s = (float) Math.sin(hinge);
                float ru = u * c - v * s;
                float rv = u * s + v * c;
                float tip = (float) Math.pow(1.0F - tv, 1.5F);
                rv += amp * tip * (float) Math.sin(phase * 1.35F + u * 0.45F
                        + (covert ? 1.2F : 0.0F));
                w += 0.35F * amp * tip * (float) Math.sin(phase * 1.1F + u * 0.35F + 0.7F);
                grid[i][j] = new P(ru, rv, w);
            }
        }
        float texU0 = covert ? ANGEL_COVERT_U0 : ANGEL_WING_U0;
        for (int i = 0; i < nu; i++) {
            for (int j = 0; j < nv; j++) {
                float tu0 = i / (float) nu;
                float tu1 = (i + 1) / (float) nu;
                float tv0 = j / (float) nv * vmax;
                float tv1 = (j + 1) / (float) nv * vmax;
                quad(buffer, m, side,
                        grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1],
                        angelUV(texU0 + tu0 * ANGEL_TEX_W, ANGEL_TEX_V0 + tv0 * ANGEL_TEX_H),
                        angelUV(texU0 + tu1 * ANGEL_TEX_W, ANGEL_TEX_V0 + tv0 * ANGEL_TEX_H),
                        angelUV(texU0 + tu1 * ANGEL_TEX_W, ANGEL_TEX_V0 + tv1 * ANGEL_TEX_H),
                        angelUV(texU0 + tu0 * ANGEL_TEX_W, ANGEL_TEX_V0 + tv1 * ANGEL_TEX_H),
                        light, back);
            }
        }
    }

    private static UV angelUV(float px, float py) {
        return new UV(px * ANGEL_UV64, py * ANGEL_UV64);
    }

    // ── butterfly wing ───────────────────────────────────────────────────

    private void renderButterflyWing(VertexConsumer buffer, Matrix4f m, float side, int light,
                                     Vector3f back, float flap) {
        float flex = flap * 4.0F;

        mothCard(buffer, m, side,
                0.1F, -10.6F, 10.2F, -10.2F, 10.2F, 0.4F, 0.1F, 0.6F,
                0.0F,
                -0.36F, -0.30F, -0.18F, 0.06F,
                H_U0, H_V0, H_U1, H_V1, light, back);

        mothCard(buffer, m, side,
                0.2F, -0.4F, 13.0F, -0.2F, 13.3F, 12.4F, 0.2F, 11.6F,
                -14.0F + flex * 0.7F,
                0.0F, 0.15F, 0.10F, 0.0F,
                F_U0, F_V0, F_U1, F_V1, light, back);

        gemCross(buffer, m, side, 0.5F, 0.3F, 0.42F, 1.0F,
                MOTHGEM_U0, MOTHGEM_U1, MOTHGEM_V0, MOTHGEM_V1, light, back);
    }

    private void emitButterflyBody(VertexConsumer buffer, Matrix4f m, int light) {
        Vector3f back = new Vector3f(0.0F, 0.0F, 1.0F);
        m.transformDirection(back);

        quad(buffer, m, 1.0F,
                new P(-0.72F, 1.8F, 0.12F), new P(0.72F, 1.8F, 0.12F),
                new P(0.72F, -3.9F, 0.12F), new P(-0.72F, -3.9F, 0.12F),
                new UV(BODY_U0, BODY_V1), new UV(BODY_U1, BODY_V1),
                new UV(BODY_U1, BODY_V0), new UV(BODY_U0, BODY_V0), light, back);
        quad(buffer, m, 1.0F,
                new P(0.0F, 1.8F, -0.58F), new P(0.0F, 1.8F, 0.58F),
                new P(0.0F, -3.9F, 0.58F), new P(0.0F, -3.9F, -0.58F),
                new UV(BODY_U0, BODY_V1), new UV(BODY_U1, BODY_V1),
                new UV(BODY_U1, BODY_V0), new UV(BODY_U0, BODY_V0), light, back);
    }

    // A 2x2 curved wing card. Corners are given in order inner-low, outer-low,
    // outer-high, inner-high. UVs follow the same order. rot rotates the
    // card around its inner-low corner.
    private void mothCard(VertexConsumer buffer, Matrix4f m, float side,
                          float x0, float y0, float x1, float y1, float x2, float y2,
                          float x3, float y3, float rotDeg,
                          float w00, float w10, float w11, float w01,
                          float u0, float v0, float u1, float v1, int light, Vector3f back) {
        double ra = Math.toRadians(rotDeg);
        float ca = (float) Math.cos(ra);
        float sa = (float) Math.sin(ra);

        float[] xs = {x0, x1, x2, x3};
        float[] ys = {y0, y1, y2, y3};
        float[] ws = {w00, w10, w11, w01};
        for (int i = 0; i < 4; i++) {
            float dx = xs[i] - x0;
            float dy = ys[i] - y0;
            xs[i] = x0 + dx * ca - dy * sa;
            ys[i] = y0 + dx * sa + dy * ca;
        }

        P[] p = {new P(xs[0], ys[0], ws[0]), new P(xs[1], ys[1], ws[1]),
                new P(xs[2], ys[2], ws[2]), new P(xs[3], ys[3], ws[3])};
        P p01 = mid(p[0], p[1], 0.0F);
        P p12 = mid(p[1], p[2], 0.0F);
        P p23 = mid(p[2], p[3], 0.0F);
        P p30 = mid(p[3], p[0], 0.0F);
        P center = mid(mid(p[0], p[2], 0.0F), mid(p[1], p[3], 0.0F), 0.0F);
        center = new P(center.u, center.v, center.w + 0.24F);

        UV uv0 = new UV(u0, v1);
        UV uv1 = new UV(u1, v1);
        UV uv2 = new UV(u1, v0);
        UV uv3 = new UV(u0, v0);
        UV uv01 = uvMid(uv0, uv1);
        UV uv12 = uvMid(uv1, uv2);
        UV uv23 = uvMid(uv2, uv3);
        UV uv30 = uvMid(uv3, uv0);
        UV uvc = uvMid(uvMid(uv0, uv2), uvMid(uv1, uv3));

        quad(buffer, m, side, p[0], p01, center, p30, uv0, uv01, uvc, uv30, light, back);
        quad(buffer, m, side, p01, p[1], p12, center, uv01, uv1, uv12, uvc, light, back);
        quad(buffer, m, side, center, p12, p[2], p23, uvc, uv12, uv2, uv23, light, back);
        quad(buffer, m, side, p30, center, p23, p[3], uv30, uvc, uv23, uv3, light, back);
    }

    // ── shared primitives ────────────────────────────────────────────────

    private void gemCross(VertexConsumer buffer, Matrix4f m, float side,
                          float centerU, float centerV, float centerW, float size,
                          float u0, float u1, float v0, float v1, int light, Vector3f back) {
        crossCard(buffer, m, side, centerU, centerV, centerW, size, u0, u1, v0, v1,
                FULL_BRIGHT, back);
    }

    private void crossCard(VertexConsumer buffer, Matrix4f m, float side,
                           float centerU, float centerV, float centerW, float size,
                           float u0, float u1, float v0, float v1, int light, Vector3f back) {
        quad(buffer, m, side,
                new P(centerU - size, centerV - size, centerW),
                new P(centerU - size, centerV + size, centerW),
                new P(centerU + size, centerV + size, centerW),
                new P(centerU + size, centerV - size, centerW),
                new UV(u0, v1), new UV(u0, v0), new UV(u1, v0), new UV(u1, v1),
                light, back);
        quad(buffer, m, side,
                new P(centerU, centerV - size, centerW - size),
                new P(centerU, centerV + size, centerW - size),
                new P(centerU, centerV + size, centerW + size),
                new P(centerU, centerV - size, centerW + size),
                new UV(u0, v1), new UV(u0, v0), new UV(u1, v0), new UV(u1, v1),
                light, back);
    }

    private void quad(VertexConsumer buffer, Matrix4f m, float side,
                      P a, P b, P c, P d,
                      UV ua, UV ub, UV uc, UV ud,
                      int light, Vector3f back) {
        quadTint(buffer, m, side, a, b, c, d, ua, ub, uc, ud,
                255, 255, 255, 255, light, back);
    }

    private void quadTint(VertexConsumer buffer, Matrix4f m, float side,
                          P a, P b, P c, P d,
                          UV ua, UV ub, UV uc, UV ud,
                          int cr, int cg, int cb, int ca, int light, Vector3f back) {
        transform(m, side, a, pA);
        transform(m, side, b, pB);
        transform(m, side, c, pC);
        edge1.set(pB.x - pA.x, pB.y - pA.y, pB.z - pA.z);
        edge2.set(pC.x - pA.x, pC.y - pA.y, pC.z - pA.z);
        normal.set(edge1).cross(edge2);
        if (normal.lengthSquared() < 1.0E-8F) {
            normal.set(back);
        } else {
            normal.normalize();
            if (normal.dot(back) < 0.0F) {
                normal.negate();
            }
        }
        if (liftNormals) {
            // painted sheets carry their own shading; bias toward the sky light
            normal.add(0.0F, 1.8F, 0.0F).normalize();
        }

        vertex(buffer, pA, ua.u, ua.v, normal, cr, cg, cb, ca, light);
        vertex(buffer, pB, ub.u, ub.v, normal, cr, cg, cb, ca, light);
        vertex(buffer, pC, uc.u, uc.v, normal, cr, cg, cb, ca, light);
        transform(m, side, d, pA);
        vertex(buffer, pA, ud.u, ud.v, normal, cr, cg, cb, ca, light);
    }

    private static void transform(Matrix4f matrix, float side, P p, Vector4f dest) {
        transform(matrix, side, p.u, p.v, p.w, dest);
    }

    private static void transform(Matrix4f matrix, float side,
                                  float u, float v, float w, Vector4f dest) {
        dest.set(side * u * PX, -v * PX, w * PX, 1.0F);
        matrix.transform(dest);
    }

    private static void vertex(VertexConsumer buffer, Vector4f p, float u, float v,
                               Vector3f normal, int cr, int cg, int cb, int ca, int light) {
        EntityLayerFlush.finish(buffer.addVertex(p.x, p.y, p.z)
                .setColor(cr, cg, cb, ca)
                .setUv(u * TEXEL, v * TEXEL)
                .setOverlay(OverlayTexture.NO_OVERLAY)
                .setLight(light)
                .setNormal(normal.x, normal.y, normal.z));
    }

    private static P mid(P a, P b, float wPush) {
        return new P((a.u + b.u) * 0.5F, (a.v + b.v) * 0.5F,
                (a.w + b.w) * 0.5F + wPush);
    }

    private static UV uvMid(UV a, UV b) {
        return new UV((a.u + b.u) * 0.5F, (a.v + b.v) * 0.5F);
    }

    private record P(float u, float v, float w) {
    }

    private record UV(float u, float v) {
    }
}

*///?}
