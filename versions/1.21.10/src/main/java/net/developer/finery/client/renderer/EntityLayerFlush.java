package net.developer.finery.client.renderer;

import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;

/** Layer acquisition helper; Curios does not need the 1.20.1 direct-buffer workaround. */
public final class EntityLayerFlush {
    private EntityLayerFlush() {
    }

    public static VertexConsumer begin(MultiBufferSource provider, RenderType layer) {
        return provider.getBuffer(layer);
    }

    public static void end(MultiBufferSource provider, RenderType layer) {
    }

    public static void finish(VertexConsumer buffer) {
    }

    public static void clearToast(MultiBufferSource provider, RenderType layer) {
        // Curios 13 batching mixes head/neck items when two are worn; flushing each layer as soon
        // as the item is drawn keeps every cosmetic on its own texture batch.
        if (provider instanceof MultiBufferSource.BufferSource source) {
            source.endBatch(layer);
        }
    }
}
