package net.developer.finery.client.renderer;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.rendertype.RenderType;
import org.joml.Matrix4f;
import org.joml.Vector3f;
import org.joml.Vector4f;

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
        public VertexConsumer setLineWidth(float width) {
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
     * Replays the captured batches. Vertices are in the layer's local space; the collector hands the
     * callback a pose (a copy taken at submit time) and expects the callback to transform with it,
     * exactly like vanilla's model feature does.
     */
    void submit(SubmitNodeCollector collector, PoseStack poseStack) {
        for (Map.Entry<RenderType, List<Vertex>> entry : batches.entrySet()) {
            List<Vertex> vertices = entry.getValue();
            collector.submitCustomGeometry(poseStack, entry.getKey(), (pose, buffer) -> {
                Matrix4f matrix = pose.pose();
                Vector3f normal = new Vector3f();
                Vector4f position = new Vector4f();
                for (Vertex vertex : vertices) {
                    position.set(vertex.x, vertex.y, vertex.z, 1.0F);
                    matrix.transform(position);
                    normal.set(vertex.nx, vertex.ny, vertex.nz);
                    pose.transformNormal(normal, normal);
                    buffer.addVertex(position.x, position.y, position.z)
                            .setColor(vertex.color)
                            .setUv(vertex.u, vertex.v)
                            .setUv1(vertex.overlay & 0xFFFF, vertex.overlay >> 16 & 0xFFFF)
                            .setUv2(vertex.light & 0xFFFF, vertex.light >> 16 & 0xFFFF)
                            .setNormal(normal.x, normal.y, normal.z);
                }
            });
        }
    }
}
