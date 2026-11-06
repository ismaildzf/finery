package net.developer.finery.client.renderer;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.RenderType;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Captures the vertex writes of Finery's cosmetic renderers so they can be replayed into the
 * deferred submit queue. 1.21.9+ draws entities from recorded geometry: writing straight into
 * {@code renderBuffers().bufferSource()} lands the cape in a later frame, which makes it lag and
 * smear behind a moving player.
 */
final class SubmitGeometry implements MultiBufferSource {
    private static final class Vertex {
        float x, y, z;
        float u, v;
        int color = 0xFFFFFFFF;
        int overlay;
        int light;
        float nx, ny, nz = 1.0F;
    }

    private final Map<RenderType, List<Vertex>> batches = new LinkedHashMap<>();
    private List<Vertex> batch;
    private Vertex last;

    @Override
    public VertexConsumer getBuffer(RenderType layer) {
        batch = batches.computeIfAbsent(layer, key -> new ArrayList<>());
        last = null;
        return BUFFER;
    }

    private final VertexConsumer BUFFER = new VertexConsumer() {
        @Override
        public VertexConsumer addVertex(float x, float y, float z) {
            Vertex vertex = new Vertex();
            vertex.x = x;
            vertex.y = y;
            vertex.z = z;
            batch.add(vertex);
            last = vertex;
            return this;
        }

        @Override
        public VertexConsumer setColor(int red, int green, int blue, int alpha) {
            return setColor((alpha & 0xFF) << 24 | (red & 0xFF) << 16 | (green & 0xFF) << 8 | (blue & 0xFF));
        }

        @Override
        public VertexConsumer setColor(int argb) {
            last.color = argb;
            return this;
        }

        @Override
        public VertexConsumer setUv(float u, float v) {
            last.u = u;
            last.v = v;
            return this;
        }

        @Override
        public VertexConsumer setUv1(int u, int v) {
            last.overlay = (u & 0xFFFF) | (v & 0xFFFF) << 16;
            return this;
        }

        @Override
        public VertexConsumer setUv2(int u, int v) {
            last.light = (u & 0xFFFF) | (v & 0xFFFF) << 16;
            return this;
        }

        @Override
        public VertexConsumer setNormal(float x, float y, float z) {
            last.nx = x;
            last.ny = y;
            last.nz = z;
            return this;
        }
    };

    /**
     * Replays every captured batch into the deferred queue. The renderers baked the layer pose into
     * the vertices, so the submission uses an identity pose; re-applying the live stack would both
     * double the transform and read a stack the caller keeps mutating.
     */
    void submit(SubmitNodeCollector collector) {
        for (Map.Entry<RenderType, List<Vertex>> entry : batches.entrySet()) {
            List<Vertex> vertices = entry.getValue();
            collector.submitCustomGeometry(new PoseStack(), entry.getKey(), (pose, buffer) -> {
                for (Vertex vertex : vertices) {
                    buffer.addVertex(vertex.x, vertex.y, vertex.z)
                            .setColor(vertex.color)
                            .setUv(vertex.u, vertex.v)
                            .setUv1(vertex.overlay & 0xFFFF, vertex.overlay >> 16 & 0xFFFF)
                            .setUv2(vertex.light & 0xFFFF, vertex.light >> 16 & 0xFFFF)
                            .setNormal(vertex.nx, vertex.ny, vertex.nz);
                }
            });
        }
    }
}
