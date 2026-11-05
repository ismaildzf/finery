from pathlib import Path

p = Path(__file__).resolve().parents[1] / "src/client/java/net/developer/finery/client/renderer/head/HeadModels.java"
s = p.read_text(encoding="utf-8")


def sub(old, new):
    global s
    assert old in s, old[:80]
    s = s.replace(old, new)


# 1) demon horn: wider base ring, five thicker segments
sub(
    """        ModelPartData parent = root.addChild("demon_plate",
                ModelPartBuilder.create().uv(32, 48)
                        .cuboid(-0.8F, -0.5F, -0.35F, 1.6F, 0.5F, 0.9F),
                ModelTransform.of(1.7F, -7.0F, -3.7F, 0.22F, 0.0F, 0.0F));
        parent = parent.addChild("demon_1",
                ModelPartBuilder.create().uv(32, 48)
                        .cuboid(-0.6F, -1.6F, -0.6F, 1.2F, 1.6F, 1.2F),
                ModelTransform.of(0.0F, -0.5F, 0.0F, 0.42F, 0.0F, 0.0F));
        parent = parent.addChild("demon_2",
                ModelPartBuilder.create().uv(32, 48)
                        .cuboid(-0.5F, -1.4F, -0.5F, 1.0F, 1.4F, 1.0F),
                ModelTransform.of(0.0F, -1.6F, 0.0F, -0.32F, 0.0F, 0.0F));
        parent = parent.addChild("demon_3",
                ModelPartBuilder.create().uv(32, 48)
                        .cuboid(-0.42F, -1.2F, -0.42F, 0.84F, 1.2F, 0.84F),
                ModelTransform.of(0.0F, -1.4F, 0.0F, -0.28F, 0.0F, 0.0F));
        parent.addChild("demon_4",
                ModelPartBuilder.create().uv(32, 48)
                        .cuboid(-0.3F, -1.0F, -0.3F, 0.6F, 1.0F, 0.6F),
                ModelTransform.of(0.0F, -1.2F, 0.0F, -0.20F, 0.0F, 0.0F));""",
    """        ModelPartData parent = root.addChild("demon_plate",
                ModelPartBuilder.create().uv(32, 48)
                        .cuboid(-1.0F, -0.6F, -0.45F, 2.0F, 0.6F, 1.1F),
                ModelTransform.of(1.7F, -7.0F, -3.7F, 0.22F, 0.0F, 0.0F));
        parent = parent.addChild("demon_ring",
                ModelPartBuilder.create().uv(32, 48)
                        .cuboid(-0.85F, -0.55F, -0.85F, 1.7F, 0.55F, 1.7F),
                ModelTransform.of(0.0F, -0.6F, 0.0F, 0.30F, 0.0F, 0.0F));
        parent = parent.addChild("demon_1",
                ModelPartBuilder.create().uv(32, 48)
                        .cuboid(-0.75F, -1.7F, -0.75F, 1.5F, 1.7F, 1.5F),
                ModelTransform.of(0.0F, -0.5F, 0.0F, 0.40F, 0.0F, 0.0F));
        parent = parent.addChild("demon_2",
                ModelPartBuilder.create().uv(32, 48)
                        .cuboid(-0.65F, -1.6F, -0.65F, 1.3F, 1.6F, 1.3F),
                ModelTransform.of(0.0F, -1.7F, 0.0F, -0.30F, 0.0F, 0.0F));
        parent = parent.addChild("demon_3",
                ModelPartBuilder.create().uv(32, 48)
                        .cuboid(-0.55F, -1.4F, -0.55F, 1.1F, 1.4F, 1.1F),
                ModelTransform.of(0.0F, -1.6F, 0.0F, -0.26F, 0.0F, 0.0F));
        parent = parent.addChild("demon_4",
                ModelPartBuilder.create().uv(32, 48)
                        .cuboid(-0.42F, -1.2F, -0.42F, 0.84F, 1.2F, 0.84F),
                ModelTransform.of(0.0F, -1.4F, 0.0F, -0.22F, 0.0F, 0.0F));
        parent.addChild("demon_5",
                ModelPartBuilder.create().uv(32, 48)
                        .cuboid(-0.26F, -1.1F, -0.26F, 0.52F, 1.1F, 0.52F),
                ModelTransform.of(0.0F, -1.2F, 0.0F, -0.16F, 0.0F, 0.0F));""",
)

# 2) imp horns: thicker base, four segments plus a sharp tip
sub(
    """        ModelPartData parent = root.addChild(name + "_0",
                ModelPartBuilder.create().uv(32, 48)
                        .cuboid(-0.55F, -1.4F, -0.55F, 1.1F, 1.4F, 1.1F),
                ModelTransform.of(px, -7.0F, -3.7F, 0.42F, 0.0F, 0.28F * side));
        parent = parent.addChild(name + "_1",
                ModelPartBuilder.create().uv(32, 48)
                        .cuboid(-0.45F, -1.3F, -0.45F, 0.9F, 1.3F, 0.9F),
                ModelTransform.of(0.0F, -1.4F, 0.0F, -0.28F, 0.0F, 0.0F));
        parent = parent.addChild(name + "_2",
                ModelPartBuilder.create().uv(32, 48)
                        .cuboid(-0.34F, -1.1F, -0.34F, 0.68F, 1.1F, 0.68F),
                ModelTransform.of(0.0F, -1.3F, 0.0F, -0.24F, 0.0F, 0.0F));
        parent.addChild(name + "_3",
                ModelPartBuilder.create().uv(32, 48)
                        .cuboid(-0.2F, -0.8F, -0.2F, 0.4F, 0.8F, 0.4F),
                ModelTransform.of(0.0F, -1.1F, 0.0F, -0.15F, 0.0F, 0.0F));""",
    """        ModelPartData parent = root.addChild(name + "_0",
                ModelPartBuilder.create().uv(32, 48)
                        .cuboid(-0.68F, -1.5F, -0.68F, 1.36F, 1.5F, 1.36F),
                ModelTransform.of(px, -7.0F, -3.7F, 0.40F, 0.0F, 0.30F * side));
        parent = parent.addChild(name + "_1",
                ModelPartBuilder.create().uv(32, 48)
                        .cuboid(-0.56F, -1.4F, -0.56F, 1.12F, 1.4F, 1.12F),
                ModelTransform.of(0.0F, -1.5F, 0.0F, -0.26F, 0.0F, 0.0F));
        parent = parent.addChild(name + "_2",
                ModelPartBuilder.create().uv(32, 48)
                        .cuboid(-0.44F, -1.2F, -0.44F, 0.88F, 1.2F, 0.88F),
                ModelTransform.of(0.0F, -1.4F, 0.0F, -0.24F, 0.0F, 0.0F));
        parent = parent.addChild(name + "_3",
                ModelPartBuilder.create().uv(32, 48)
                        .cuboid(-0.3F, -1.0F, -0.3F, 0.6F, 1.0F, 0.6F),
                ModelTransform.of(0.0F, -1.2F, 0.0F, -0.20F, 0.0F, 0.0F));
        parent.addChild(name + "_4",
                ModelPartBuilder.create().uv(32, 48)
                        .cuboid(-0.16F, -0.9F, -0.16F, 0.32F, 0.9F, 0.32F),
                ModelTransform.of(0.0F, -1.0F, 0.0F, -0.14F, 0.0F, 0.0F));""",
)

# 3) crown: bevel under the band + gold frame around the centre gem
sub(
    """        // stepped spikes; front/back center ones taller""",
    """        // outer bevel under the band so the crown reads with depth, not as a flat ring
        root.addChild("bevel_front", ModelPartBuilder.create().uv(24, 36)
                .cuboid(-4.75F, -6.95F, -4.78F, 9.5F, 0.5F, 0.55F), ModelTransform.NONE);
        root.addChild("bevel_back", ModelPartBuilder.create().uv(24, 36)
                .cuboid(-4.75F, -6.95F, 4.23F, 9.5F, 0.5F, 0.55F), ModelTransform.NONE);
        root.addChild("bevel_left", ModelPartBuilder.create().uv(24, 36)
                .cuboid(-4.78F, -6.95F, -4.23F, 0.55F, 0.5F, 8.46F), ModelTransform.NONE);
        root.addChild("bevel_right", ModelPartBuilder.create().uv(24, 36)
                .cuboid(4.23F, -6.95F, -4.23F, 0.55F, 0.5F, 8.46F), ModelTransform.NONE);

        // stepped spikes; front/back center ones taller""",
)

sub(
    """        // gems on the front band
        root.addChild("gem_red", ModelPartBuilder.create().uv(48, 32)""",
    """        // gold frame around the centre gem, then the gems
        root.addChild("gem_frame", ModelPartBuilder.create().uv(24, 32)
                .cuboid(-1.35F, -8.55F, -4.98F, 2.7F, 2.7F, 0.4F), ModelTransform.NONE);
        root.addChild("gem_red", ModelPartBuilder.create().uv(48, 32)""",
)

sub(
    """        float baseH = tall ? 2.5F : 1.9F;
        float midY = tall ? -12.6F : -12.0F;
        float tipY = tall ? -13.5F : -12.8F;""",
    """        float baseH = tall ? 2.9F : 2.1F;
        float midY = tall ? -13.1F : -12.3F;
        float tipY = tall ? -14.1F : -13.1F;""",
)

# 4) wizard hat: under-brim lip, buckle, drooping tip
sub(
    """        root.addChild("brim", ModelPartBuilder.create().uv(0, 0)
                .cuboid(-5.0F, -8.7F, -5.0F, 10.0F, 0.8F, 10.0F), ModelTransform.NONE);""",
    """        root.addChild("brim", ModelPartBuilder.create().uv(0, 0)
                .cuboid(-5.0F, -8.7F, -5.0F, 10.0F, 0.8F, 10.0F), ModelTransform.NONE);
        // thin under-brim: gives the brim an edge instead of a flat slab
        root.addChild("brim_lip", ModelPartBuilder.create().uv(0, 0)
                .cuboid(-5.35F, -8.95F, -5.35F, 10.7F, 0.3F, 10.7F), ModelTransform.NONE);""",
)

sub(
    """        root.addChild("star", ModelPartBuilder.create().uv(0, 32)""",
    """        root.addChild("buckle", ModelPartBuilder.create().uv(0, 32)
                .cuboid(-1.1F, -12.1F, -4.9F, 2.2F, 1.5F, 0.45F), ModelTransform.NONE);
        root.addChild("star", ModelPartBuilder.create().uv(0, 32)""",
)

sub(
    """        root.addChild("tip", ModelPartBuilder.create().uv(0, 0)
                .cuboid(-0.9F, -20.6F, 0.1F, 1.8F, 1.6F, 1.8F), ModelTransform.NONE);""",
    """        root.addChild("tip", ModelPartBuilder.create().uv(0, 0)
                .cuboid(-0.9F, -20.6F, 0.1F, 1.8F, 1.6F, 1.8F),
                ModelTransform.of(0.0F, 0.0F, 0.0F, 0.16F, 0.0F, 0.10F));""",
)

# 5) headband: taller band, bigger knot with a lobe, extra crease
sub(
    """        root.addChild("band_front", ModelPartBuilder.create().uv(0, 0)
                .cuboid(-4.6F, -6.9F, -4.6F, 9.2F, 1.7F, 0.5F), ModelTransform.NONE);
        root.addChild("band_back", ModelPartBuilder.create().uv(0, 0)
                .cuboid(-4.6F, -6.9F, 4.1F, 9.2F, 1.7F, 0.5F), ModelTransform.NONE);
        root.addChild("band_left", ModelPartBuilder.create().uv(0, 0)
                .cuboid(-4.6F, -6.9F, -4.1F, 0.5F, 1.7F, 8.2F), ModelTransform.NONE);
        root.addChild("band_right", ModelPartBuilder.create().uv(0, 0)
                .cuboid(4.1F, -6.9F, -4.1F, 0.5F, 1.7F, 8.2F), ModelTransform.NONE);
        // raised centre pad so the band reads as fabric, not a flat strip
        root.addChild("band_pad", ModelPartBuilder.create().uv(0, 0)
                .cuboid(-3.6F, -6.7F, -4.75F, 7.2F, 1.3F, 0.35F), ModelTransform.NONE);
        // front-right knot + a short hanging fold
        root.addChild("knot", ModelPartBuilder.create().uv(20, 0)
                .cuboid(1.3F, -7.1F, -4.95F, 2.0F, 1.5F, 0.7F), ModelTransform.NONE);
        root.addChild("fold", ModelPartBuilder.create().uv(24, 4)
                .cuboid(1.7F, -5.7F, -4.9F, 1.3F, 0.9F, 0.6F), ModelTransform.NONE);""",
    """        root.addChild("band_front", ModelPartBuilder.create().uv(0, 0)
                .cuboid(-4.6F, -7.15F, -4.6F, 9.2F, 2.15F, 0.5F), ModelTransform.NONE);
        root.addChild("band_back", ModelPartBuilder.create().uv(0, 0)
                .cuboid(-4.6F, -7.15F, 4.1F, 9.2F, 2.15F, 0.5F), ModelTransform.NONE);
        root.addChild("band_left", ModelPartBuilder.create().uv(0, 0)
                .cuboid(-4.6F, -7.15F, -4.1F, 0.5F, 2.15F, 8.2F), ModelTransform.NONE);
        root.addChild("band_right", ModelPartBuilder.create().uv(0, 0)
                .cuboid(4.1F, -7.15F, -4.1F, 0.5F, 2.15F, 8.2F), ModelTransform.NONE);
        // raised centre pad so the band reads as fabric, not a flat strip
        root.addChild("band_pad", ModelPartBuilder.create().uv(0, 0)
                .cuboid(-3.6F, -6.95F, -4.75F, 7.2F, 1.7F, 0.4F), ModelTransform.NONE);
        // front-right knot + two hanging folds and a diagonal crease
        root.addChild("knot", ModelPartBuilder.create().uv(20, 0)
                .cuboid(1.1F, -7.35F, -5.0F, 2.4F, 1.8F, 0.75F), ModelTransform.NONE);
        root.addChild("knot_lobe", ModelPartBuilder.create().uv(20, 0)
                .cuboid(0.7F, -7.15F, -5.05F, 0.8F, 1.2F, 0.6F), ModelTransform.NONE);
        root.addChild("fold", ModelPartBuilder.create().uv(24, 4)
                .cuboid(1.7F, -5.7F, -4.95F, 1.5F, 1.0F, 0.65F), ModelTransform.NONE);
        root.addChild("crease", ModelPartBuilder.create().uv(24, 0)
                .cuboid(-2.6F, -6.55F, -4.8F, 1.9F, 1.1F, 0.3F), ModelTransform.NONE);""",
)

sub(
    """    public static final float[][] HEADBAND_TAIL_ORIGINS = {
            {2.3F, -5.4F, -4.8F},
            {2.9F, -5.4F, -4.8F},
    };""",
    """    public static final float[][] HEADBAND_TAIL_ORIGINS = {
            {2.2F, -5.35F, -4.8F},
            {2.9F, -5.35F, -4.8F},
    };""",
)

p.write_text(s, encoding="utf-8")
print("geometry patched")
