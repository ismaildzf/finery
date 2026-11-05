package net.developer.finery.client.renderer;

//? if <1.21 {
/*import com.mojang.blaze3d.systems.RenderSystem;
import net.minecraft.client.render.BufferBuilder;
import net.minecraft.client.render.VertexFormat;
import net.minecraft.client.render.VertexFormats;
*///?}
import net.minecraft.client.render.RenderLayer;
import net.minecraft.client.render.VertexConsumer;
import net.minecraft.client.render.VertexConsumerProvider;

/**
 * 1.20.1's {@code VertexConsumerProvider.Immediate} only keeps a shared
 * fallback buffer for custom-texture layers and leaves it in an unusable state
 * when the Accessories feature layer swaps layers, so accessory geometry is
 * never drawn. Build and draw the layer directly instead.
 */
public final class EntityLayerFlush {

    private EntityLayerFlush() {
    }

    //? if <1.21 {
    /*private static BufferBuilder direct;

    public static VertexConsumer begin(VertexConsumerProvider provider, RenderLayer layer) {
        if (direct == null) {
            direct = new BufferBuilder(32768);
        }
        direct.begin(VertexFormat.DrawMode.QUADS, VertexFormats.POSITION_COLOR_TEXTURE_OVERLAY_LIGHT_NORMAL);
        return direct;
    }

    public static void end(VertexConsumerProvider provider, RenderLayer layer) {
        if (direct != null && direct.isBuilding()) {
            layer.draw(direct, RenderSystem.getVertexSorting());
        }
    }
    *///?} else {
    public static VertexConsumer begin(VertexConsumerProvider provider, RenderLayer layer) {
        return provider.getBuffer(layer);
    }

    public static void end(VertexConsumerProvider provider, RenderLayer layer) {
    }
    //?}

    /**
     * 1.20.1 only counts a vertex once {@code next()} is called after its
     * elements are written; without it the buffer stays empty and nothing draws.
     */
    public static void finish(VertexConsumer buffer) {
        //? if <1.21 {
        /*buffer.next();
        *///?}
    }
}
