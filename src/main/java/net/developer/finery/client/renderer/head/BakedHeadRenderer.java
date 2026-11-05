package net.developer.finery.client.renderer.head;

import net.developer.finery.client.renderer.EntityLayerFlush;
import net.developer.finery.item.CosmeticDye;
import net.developer.finery.item.DyeableHeadItem;
import net.minecraft.client.renderer.texture.OverlayTexture;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.world.item.ItemStack;
import org.joml.Matrix4f;
import org.joml.Vector3f;
import org.joml.Vector4f;

/**
 * Draws a {@link BakedHeadModel} in the current head pose, with an optional dye tint.
 *
 * The texture is a vertical strip of {@link #FRAMES} frames; the game binds that
 * strip as one image, so the quad UVs (authored against a single frame) get the
 * current frame's row added here.
 */
public final class BakedHeadRenderer {

    private static final int FRAMES = 16;
    private static final int FRAME_TICKS = 3;

    private static final Vector3f NORMAL = new Vector3f();
    private static final Vector4f POS = new Vector4f();

    private BakedHeadRenderer() {
    }

    public static void render(BakedHeadModel.Model model, PoseStack matrices,
                              VertexConsumer buffer, int light, int tint, float animTicks) {
        if (model == null || model.quads == null) {
            return;
        }
        Matrix4f matrix = matrices.last().pose();
        int cr = (tint >> 16) & 0xFF;
        int cg = (tint >> 8) & 0xFF;
        int cb = tint & 0xFF;
        float tw = model.textureSize[0];
        float frameH = model.textureSize[1];
        int frames = model.frames > 0 ? model.frames : 1;
        float stripH = frameH * frames;
        float vBase = (int) (animTicks / FRAME_TICKS) % frames * frameH;

        for (BakedHeadModel.Quad quad : model.quads) {
            float[][] v = quad.v;
            float[][] uv = quad.uv;
            float ax = v[1][0] - v[0][0], ay = v[1][1] - v[0][1], az = v[1][2] - v[0][2];
            float bx = v[2][0] - v[0][0], by = v[2][1] - v[0][1], bz = v[2][2] - v[0][2];
            NORMAL.set(ay * bz - az * by, az * bx - ax * bz, ax * by - ay * bx);
            if (NORMAL.lengthSquared() < 1.0E-6F) {
                NORMAL.set(0.0F, 1.0F, 0.0F);
            } else {
                NORMAL.normalize();
            }
            for (int i = 0; i < 4; i++) {
                POS.set(v[i][0] / 16.0F, v[i][1] / 16.0F, v[i][2] / 16.0F, 1.0F);
                matrix.transform(POS);
                EntityLayerFlush.finish(buffer.vertex(POS.x, POS.y, POS.z)
                        .color(cr, cg, cb, 255)
                        .uv(uv[i][0] / tw, (uv[i][1] + vBase) / stripH)
                        .overlayCoords(OverlayTexture.NO_OVERLAY)
                        .uv2(light)
                        .normal(NORMAL.x, NORMAL.y, NORMAL.z));
            }
        }
    }

    /** The eyewrap takes the dye colour; everything else stays untinted. */
    public static int tintOf(String variant, ItemStack stack) {
        if ("eye_wrap".equals(variant) && stack.getItem() instanceof DyeableHeadItem dyable) {
            return CosmeticDye.rgb(CosmeticDye.get(stack, dyable.defaultDye()));
        }
        return 0xFFFFFF;
    }
}
