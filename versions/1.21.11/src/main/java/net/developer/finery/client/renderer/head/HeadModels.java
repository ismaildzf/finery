package net.developer.finery.client.renderer.head;

import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.PartDefinition;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.LayerDefinition;

import java.util.HashMap;
import java.util.Map;

/**
 * Static 3D models for the head cosmetics (baked against a 64x64 sheet, so a
 * 4x-resolution 256x256 texture lines up). All coordinates are in head-local
 * space: the player head box spans x/z -4..4 with the top at y=-8, the face
 * at -z, hanging directions at +y. The face texture rows map ~1:1 to y.
 *
 * HAIR LAYER: the skin's second (overlay) layer is inflated +0.5px around the
 * head cube, so every head-hugging band keeps its outer surface at |4.55| or
 * farther from the centre — otherwise the player's overlay texture (hair,
 * hats) renders on top of the cosmetic.
 *
 * EYE ZONE (verified from steve.png/alex.png): the vanilla eye row is faceRow
 * 4 = model y -4..-3, but skin artists draw eyes anywhere in rows 3..5
 * (y -5..-2) — e.g. 2px-tall eyes span rows 4-5. No fixed placement fits
 * every skin, so positions below are the neutral defaults; players nudge
 * them in-game (K key / pause-menu screen) to fit their own skin.
 *
 * Curved horns are nested rotated segment chains; per-sheet texture UV zones
 * are documented in generate_head_textures.py.
 */
public final class HeadModels {

    private static final Map<String, ModelPart> CACHE = new HashMap<>();

    private HeadModels() {
    }

    public static ModelPart get(String variant) {
        return CACHE.computeIfAbsent(variant, HeadModels::build);
    }

    private static ModelPart build(String variant) {
        MeshDefinition data = new MeshDefinition();
        PartDefinition root = data.getRoot();
        switch (variant) {
            case "wizard_hat" -> buildWizardHat(root);
            case "crown" -> buildCrown(root);
            case "headband" -> buildHeadband(root);
            case "eye_patch" -> buildEyePatch(root);
            case "dragon_horns" -> {
                buildDragonHorn(root, "horn_l", 3.1F, -6.6F, -3.5F, 1.0F);
                buildDragonHorn(root, "horn_r", -3.1F, -6.6F, -3.5F, -1.0F);
            }
            case "ram_horns" -> {
                buildRamCurl(root, "ram_l", 3.3F, -6.5F, -3.3F, 1.0F);
                buildRamCurl(root, "ram_r", -3.3F, -6.5F, -3.3F, -1.0F);
            }
            case "demon_horn" -> buildDemonHorn(root);
            case "imp_horns" -> {
                buildImpHorn(root, "imp_l", 1.7F, 1.0F);
                buildImpHorn(root, "imp_r", -1.7F, -1.0F);
            }
            case "eye_wrap" -> buildEyeWrap(root);
            default -> throw new IllegalArgumentException("Unknown head model: " + variant);
        }
        return LayerDefinition.create(data, 64, 64).bakeRoot();
    }

    // ── wizard hat (compact: brim 10x10, ~12px tall) ────────────────────

    private static void buildWizardHat(PartDefinition root) {
        root.addOrReplaceChild("brim", CubeListBuilder.create().texOffs(0, 0)
                .addBox(-5.0F, -8.7F, -5.0F, 10.0F, 0.8F, 10.0F), PartPose.ZERO);
        // thin under-brim: gives the brim an edge instead of a flat slab
        root.addOrReplaceChild("brim_lip", CubeListBuilder.create().texOffs(0, 0)
                .addBox(-5.35F, -8.95F, -5.35F, 10.7F, 0.3F, 10.7F), PartPose.ZERO);
        root.addOrReplaceChild("cone1", CubeListBuilder.create().texOffs(0, 0)
                .addBox(-4.0F, -12.0F, -4.0F, 8.0F, 3.3F, 8.0F), PartPose.ZERO);
        root.addOrReplaceChild("cone2", CubeListBuilder.create().texOffs(0, 0)
                .addBox(-3.2F, -14.8F, -3.2F, 6.4F, 2.8F, 6.4F), PartPose.ZERO);
        root.addOrReplaceChild("cone3", CubeListBuilder.create().texOffs(0, 0)
                .addBox(-2.4F, -17.2F, -2.4F, 4.8F, 2.4F, 4.8F), PartPose.ZERO);
        // tip bends backwards
        root.addOrReplaceChild("cone4", CubeListBuilder.create().texOffs(0, 0)
                .addBox(-1.7F, -19.2F, -1.3F, 3.4F, 2.2F, 3.4F), PartPose.ZERO);
        root.addOrReplaceChild("tip", CubeListBuilder.create().texOffs(0, 0)
                .addBox(-0.9F, -20.6F, 0.1F, 1.8F, 1.6F, 1.8F),
                PartPose.offsetAndRotation(0.0F, 0.0F, 0.0F, 0.16F, 0.0F, 0.10F));
        // gold band strips at the cone base + front star
        root.addOrReplaceChild("band_front", CubeListBuilder.create().texOffs(0, 32)
                .addBox(-4.3F, -12.35F, -4.3F, 8.6F, 1.0F, 0.5F), PartPose.ZERO);
        root.addOrReplaceChild("band_back", CubeListBuilder.create().texOffs(0, 32)
                .addBox(-4.3F, -12.35F, 3.8F, 8.6F, 1.0F, 0.5F), PartPose.ZERO);
        root.addOrReplaceChild("band_left", CubeListBuilder.create().texOffs(0, 32)
                .addBox(-4.3F, -12.35F, -3.8F, 0.5F, 1.0F, 7.6F), PartPose.ZERO);
        root.addOrReplaceChild("band_right", CubeListBuilder.create().texOffs(0, 32)
                .addBox(3.8F, -12.35F, -3.8F, 0.5F, 1.0F, 7.6F), PartPose.ZERO);
        root.addOrReplaceChild("buckle", CubeListBuilder.create().texOffs(0, 32)
                .addBox(-1.1F, -12.1F, -4.9F, 2.2F, 1.5F, 0.45F), PartPose.ZERO);
        root.addOrReplaceChild("star", CubeListBuilder.create().texOffs(0, 32)
                .addBox(-0.9F, -13.0F, -4.75F, 1.8F, 1.8F, 0.55F), PartPose.ZERO);
    }

    // ── royal crown (hugs the upper head, proper band + rims + spikes) ──

    private static void buildCrown(PartDefinition root) {
        CubeListBuilder band = CubeListBuilder.create().texOffs(0, 32);
        root.addOrReplaceChild("band_front", band.addBox(-4.6F, -8.7F, -4.6F, 9.2F, 2.0F, 0.6F), PartPose.ZERO);
        root.addOrReplaceChild("band_back", CubeListBuilder.create().texOffs(0, 32)
                .addBox(-4.6F, -8.7F, 4.0F, 9.2F, 2.0F, 0.6F), PartPose.ZERO);
        root.addOrReplaceChild("band_left", CubeListBuilder.create().texOffs(0, 32)
                .addBox(-4.6F, -8.7F, -4.0F, 0.6F, 2.0F, 8.0F), PartPose.ZERO);
        root.addOrReplaceChild("band_right", CubeListBuilder.create().texOffs(0, 32)
                .addBox(4.0F, -8.7F, -4.0F, 0.6F, 2.0F, 8.0F), PartPose.ZERO);

        // thin rims top and bottom of the band
        root.addOrReplaceChild("rim_top_front", CubeListBuilder.create().texOffs(24, 32)
                .addBox(-4.7F, -9.1F, -4.7F, 9.4F, 0.4F, 0.5F), PartPose.ZERO);
        root.addOrReplaceChild("rim_top_back", CubeListBuilder.create().texOffs(24, 32)
                .addBox(-4.7F, -9.1F, 4.2F, 9.4F, 0.4F, 0.5F), PartPose.ZERO);
        root.addOrReplaceChild("rim_top_left", CubeListBuilder.create().texOffs(24, 32)
                .addBox(-4.7F, -9.1F, -4.2F, 0.5F, 0.4F, 8.4F), PartPose.ZERO);
        root.addOrReplaceChild("rim_top_right", CubeListBuilder.create().texOffs(24, 32)
                .addBox(4.2F, -9.1F, -4.2F, 0.5F, 0.4F, 8.4F), PartPose.ZERO);
        root.addOrReplaceChild("rim_bottom_front", CubeListBuilder.create().texOffs(24, 36)
                .addBox(-4.7F, -6.7F, -4.7F, 9.4F, 0.35F, 0.5F), PartPose.ZERO);
        root.addOrReplaceChild("rim_bottom_back", CubeListBuilder.create().texOffs(24, 36)
                .addBox(-4.7F, -6.7F, 4.2F, 9.4F, 0.35F, 0.5F), PartPose.ZERO);
        root.addOrReplaceChild("rim_bottom_left", CubeListBuilder.create().texOffs(24, 36)
                .addBox(-4.7F, -6.7F, -4.2F, 0.5F, 0.35F, 8.4F), PartPose.ZERO);
        root.addOrReplaceChild("rim_bottom_right", CubeListBuilder.create().texOffs(24, 36)
                .addBox(4.2F, -6.7F, -4.2F, 0.5F, 0.35F, 8.4F), PartPose.ZERO);

        // outer bevel under the band so the crown reads with depth, not as a flat ring
        root.addOrReplaceChild("bevel_front", CubeListBuilder.create().texOffs(24, 36)
                .addBox(-4.75F, -6.95F, -4.78F, 9.5F, 0.5F, 0.55F), PartPose.ZERO);
        root.addOrReplaceChild("bevel_back", CubeListBuilder.create().texOffs(24, 36)
                .addBox(-4.75F, -6.95F, 4.23F, 9.5F, 0.5F, 0.55F), PartPose.ZERO);
        root.addOrReplaceChild("bevel_left", CubeListBuilder.create().texOffs(24, 36)
                .addBox(-4.78F, -6.95F, -4.23F, 0.55F, 0.5F, 8.46F), PartPose.ZERO);
        root.addOrReplaceChild("bevel_right", CubeListBuilder.create().texOffs(24, 36)
                .addBox(4.23F, -6.95F, -4.23F, 0.55F, 0.5F, 8.46F), PartPose.ZERO);

        // stepped spikes; front/back center ones taller
        addSpike(root, "spike_fc", 0.0F, -4.35F, true);
        addSpike(root, "spike_fr", 3.1F, -3.1F, false);
        addSpike(root, "spike_fl", -3.1F, -3.1F, false);
        addSpike(root, "spike_r", 4.3F, 0.0F, false);
        addSpike(root, "spike_l", -4.3F, 0.0F, false);
        addSpike(root, "spike_br", 3.1F, 3.1F, false);
        addSpike(root, "spike_bl", -3.1F, 3.1F, false);
        addSpike(root, "spike_bc", 0.0F, 4.3F, true);

        // gold frame around the centre gem, then the gems
        root.addOrReplaceChild("gem_frame", CubeListBuilder.create().texOffs(24, 32)
                .addBox(-1.35F, -8.55F, -4.98F, 2.7F, 2.7F, 0.4F), PartPose.ZERO);
        root.addOrReplaceChild("gem_red", CubeListBuilder.create().texOffs(48, 32)
                .addBox(-1.0F, -8.2F, -5.0F, 2.0F, 2.0F, 0.55F), PartPose.ZERO);
        root.addOrReplaceChild("gem_blue_r", CubeListBuilder.create().texOffs(48, 40)
                .addBox(1.5F, -8.0F, -4.95F, 0.9F, 0.9F, 0.5F), PartPose.ZERO);
        root.addOrReplaceChild("gem_blue_l", CubeListBuilder.create().texOffs(48, 40)
                .addBox(-2.4F, -8.0F, -4.95F, 0.9F, 0.9F, 0.5F), PartPose.ZERO);
    }

    private static void addSpike(PartDefinition root, String name, float sx, float sz, boolean tall) {
        float baseH = tall ? 2.9F : 2.1F;
        float midY = tall ? -13.1F : -12.3F;
        float tipY = tall ? -14.1F : -13.1F;
        root.addOrReplaceChild(name + "_base", CubeListBuilder.create().texOffs(0, 40)
                .addBox(sx - 0.75F, -8.7F - baseH, sz - 0.75F, 1.5F, baseH, 1.5F), PartPose.ZERO);
        root.addOrReplaceChild(name + "_mid", CubeListBuilder.create().texOffs(8, 40)
                .addBox(sx - 0.5F, midY, sz - 0.5F, 1.0F, 1.3F, 1.0F), PartPose.ZERO);
        root.addOrReplaceChild(name + "_tip", CubeListBuilder.create().texOffs(14, 40)
                .addBox(sx - 0.25F, tipY, sz - 0.25F, 0.5F, 0.9F, 0.5F), PartPose.ZERO);
    }

    // ── headband (wide cloth band around the forehead + knot + tails) ───
    // Outer surfaces at 4.6 so the band sits above the skin's hair layer.

    private static void buildHeadband(PartDefinition root) {
        // main band, outer shell at 4.6 so it clears the skin's hair layer
        root.addOrReplaceChild("band_front", CubeListBuilder.create().texOffs(0, 0)
                .addBox(-4.6F, -7.15F, -4.6F, 9.2F, 2.05F, 0.3F), PartPose.ZERO);
        root.addOrReplaceChild("band_back", CubeListBuilder.create().texOffs(0, 0)
                .addBox(-4.6F, -7.15F, 4.3F, 9.2F, 2.05F, 0.3F), PartPose.ZERO);
        root.addOrReplaceChild("band_left", CubeListBuilder.create().texOffs(0, 0)
                .addBox(-4.6F, -7.15F, -4.3F, 0.3F, 2.05F, 8.6F), PartPose.ZERO);
        root.addOrReplaceChild("band_right", CubeListBuilder.create().texOffs(0, 0)
                .addBox(4.3F, -7.15F, -4.3F, 0.3F, 2.05F, 8.6F), PartPose.ZERO);
        // second, slightly larger lip at the bottom: layered cloth edge
        root.addOrReplaceChild("lip_front", CubeListBuilder.create().texOffs(0, 0)
                .addBox(-4.66F, -5.3F, -4.66F, 9.32F, 0.35F, 0.34F), PartPose.ZERO);
        root.addOrReplaceChild("lip_back", CubeListBuilder.create().texOffs(0, 0)
                .addBox(-4.66F, -5.3F, 4.32F, 9.32F, 0.35F, 0.34F), PartPose.ZERO);
        root.addOrReplaceChild("lip_left", CubeListBuilder.create().texOffs(0, 0)
                .addBox(-4.66F, -5.3F, -4.32F, 0.34F, 0.35F, 8.64F), PartPose.ZERO);
        root.addOrReplaceChild("lip_right", CubeListBuilder.create().texOffs(0, 0)
                .addBox(4.32F, -5.3F, -4.32F, 0.34F, 0.35F, 8.64F), PartPose.ZERO);
        // raised centre pad + diagonal fold
        root.addOrReplaceChild("band_pad", CubeListBuilder.create().texOffs(0, 0)
                .addBox(-3.6F, -6.95F, -4.75F, 7.2F, 1.6F, 0.3F), PartPose.ZERO);
        root.addOrReplaceChild("wrap_diagonal", CubeListBuilder.create().texOffs(0, 0)
                .addBox(-4.3F, -0.52F, -0.16F, 8.6F, 1.05F, 0.32F),
                PartPose.offsetAndRotation(0.0F, -6.15F, -4.83F, 0.0F, 0.0F, 0.16F));

        // knot moved off the centre-back to the right rear corner, so it never
        // reads as a bow between the shoulder blades
        PartDefinition knot = root.addOrReplaceChild("knot_base", CubeListBuilder.create().texOffs(20, 0)
                        .addBox(-0.85F, -0.8F, 0.0F, 1.7F, 1.6F, 0.55F),
                PartPose.offsetAndRotation(3.25F, -6.1F, 3.25F, 0.0F, 0.785F, 0.0F));
        knot.addOrReplaceChild("knot_loop_a", CubeListBuilder.create().texOffs(20, 0)
                        .addBox(-1.35F, -0.55F, 0.3F, 1.15F, 1.1F, 0.3F),
                PartPose.offsetAndRotation(-0.5F, 0.0F, 0.4F, 0.0F, 0.0F, 0.55F));
        knot.addOrReplaceChild("knot_loop_b", CubeListBuilder.create().texOffs(20, 0)
                        .addBox(0.2F, -0.55F, 0.3F, 1.15F, 1.1F, 0.3F),
                PartPose.offsetAndRotation(0.5F, 0.0F, 0.4F, 0.0F, 0.0F, -0.55F));
        knot.addOrReplaceChild("knot_wrap", CubeListBuilder.create().texOffs(20, 0)
                        .addBox(-1.05F, -0.28F, 0.55F, 2.1F, 0.56F, 0.3F),
                PartPose.offsetAndRotation(0.0F, 0.0F, 0.55F, 0.0F, 0.0F, 0.24F));
    }

    /** Animated tail attachment points (head-local px), used by the renderer. */
    public static final float[][] HEADBAND_TAIL_ORIGINS = {
            {3.05F, -5.15F, 4.0F},
            {3.55F, -5.15F, 3.75F},
    };

    // ── eye patch (anchored at real eye level, small buckle) ────────────

    private static void buildEyePatch(PartDefinition root) {
        root.addOrReplaceChild("patch", CubeListBuilder.create().texOffs(0, 48)
                .addBox(0.4F, -6.3F, -4.8F, 3.4F, 3.0F, 0.6F), PartPose.ZERO);
        root.addOrReplaceChild("strap_front", CubeListBuilder.create().texOffs(0, 48)
                .addBox(-4.6F, -5.4F, -4.6F, 9.2F, 0.7F, 0.5F), PartPose.ZERO);
        root.addOrReplaceChild("strap_back", CubeListBuilder.create().texOffs(0, 48)
                .addBox(-4.6F, -5.4F, 4.1F, 9.2F, 0.7F, 0.5F), PartPose.ZERO);
        root.addOrReplaceChild("strap_left", CubeListBuilder.create().texOffs(0, 48)
                .addBox(-4.6F, -5.4F, -4.1F, 0.5F, 0.7F, 8.2F), PartPose.ZERO);
        root.addOrReplaceChild("strap_right", CubeListBuilder.create().texOffs(0, 48)
                .addBox(4.1F, -5.4F, -4.1F, 0.5F, 0.7F, 8.2F), PartPose.ZERO);
        root.addOrReplaceChild("rivet", CubeListBuilder.create().texOffs(32, 48)
                .addBox(-0.5F, -5.9F, -5.0F, 0.7F, 0.7F, 0.4F), PartPose.ZERO);
    }

    // ── eye wrap (blindfold over the eyes, knot + tails at the back) ────
    // Verified from the official Steve/Alex skin textures: the eye row is
    // exactly faceRow 4, i.e. model y -4..-3. The cloth spans y -5.0..-2.6.
    // Built as padded cloth, not flat boxes: three stacked front strips (the
    // middle bulges), 45°-chamfered corners, a knot bundle at the back.
    // Outer surfaces sit at |4.55|+ so the wrap renders above the skin's
    // second (hair) layer, which is inflated +0.5 around the head.

    private static void buildEyeWrap(PartDefinition root) {
        root.addOrReplaceChild("blind_front_top", CubeListBuilder.create().texOffs(0, 48)
                .addBox(-4.6F, -5.0F, -4.55F, 9.2F, 0.8F, 0.5F), PartPose.ZERO);
        root.addOrReplaceChild("blind_front_mid", CubeListBuilder.create().texOffs(0, 48)
                .addBox(-4.6F, -4.2F, -4.72F, 9.2F, 1.0F, 0.62F), PartPose.ZERO);
        root.addOrReplaceChild("blind_front_bot", CubeListBuilder.create().texOffs(0, 48)
                .addBox(-4.6F, -3.2F, -4.55F, 9.2F, 0.6F, 0.5F), PartPose.ZERO);
        root.addOrReplaceChild("blind_back", CubeListBuilder.create().texOffs(0, 48)
                .addBox(-4.6F, -5.0F, 4.1F, 9.2F, 2.4F, 0.5F), PartPose.ZERO);
        root.addOrReplaceChild("blind_left", CubeListBuilder.create().texOffs(0, 48)
                .addBox(-4.6F, -5.0F, -4.1F, 0.5F, 2.4F, 8.2F), PartPose.ZERO);
        root.addOrReplaceChild("blind_right", CubeListBuilder.create().texOffs(0, 48)
                .addBox(4.1F, -5.0F, -4.1F, 0.5F, 2.4F, 8.2F), PartPose.ZERO);
        // 45° corner cubes soften the box into rounded cloth
        addWrapBevel(root, "bevel_fl", -4.06F, -4.06F, 0.785F);
        addWrapBevel(root, "bevel_fr", 4.06F, -4.06F, -0.785F);
        addWrapBevel(root, "bevel_bl", -4.06F, 4.06F, -0.785F);
        addWrapBevel(root, "bevel_br", 4.06F, 4.06F, 0.785F);
        // no protruding back knot: two thin strips overlap at a shallow angle
        root.addOrReplaceChild("back_overlap_a", CubeListBuilder.create().texOffs(20, 48)
                        .addBox(-1.5F, -4.75F, 4.42F, 3.2F, 1.8F, 0.26F),
                PartPose.offsetAndRotation(0.0F, 0.0F, 4.5F, 0.0F, 0.0F, 0.10F));
        root.addOrReplaceChild("back_overlap_b", CubeListBuilder.create().texOffs(20, 48)
                        .addBox(-1.1F, -4.55F, 4.55F, 2.7F, 1.4F, 0.24F),
                PartPose.offsetAndRotation(0.0F, 0.0F, 4.6F, 0.0F, 0.0F, -0.12F));
        // soft cheek flaps: the cloth sags past the eyes instead of ending in a hard line
        root.addOrReplaceChild("cheek_l", CubeListBuilder.create().texOffs(0, 48)
                        .addBox(1.8F, -3.45F, -4.78F, 2.4F, 0.55F, 0.6F),
                PartPose.offsetAndRotation(3.0F, 0.0F, -4.4F, 0.0F, 0.0F, -0.10F));
        root.addOrReplaceChild("cheek_r", CubeListBuilder.create().texOffs(0, 48)
                        .addBox(-4.2F, -3.45F, -4.78F, 2.4F, 0.55F, 0.6F),
                PartPose.offsetAndRotation(-3.0F, 0.0F, -4.4F, 0.0F, 0.0F, 0.10F));
    }

    /** Chamfer cube rotated 45° around Y at one vertical corner of the wrap. */
    private static void addWrapBevel(PartDefinition root, String name, float px, float pz, float yaw) {
        root.addOrReplaceChild(name, CubeListBuilder.create().texOffs(0, 48)
                        .addBox(-0.5F, -5.0F, -0.5F, 1.0F, 2.4F, 1.0F),
                PartPose.offsetAndRotation(px, 0.0F, pz, 0.0F, yaw, 0.0F));
    }

    // ── dragon horns (swept-back ridges rooted at the front head corners) ─
    // Reference shape: long horns leaving the front corners, sweeping up and
    // BACK over the head with a ridge ring at the base and a smooth taper,
    // tips flaring slightly outward (Sketchfab dragon-horn refs).

    private static void buildDragonHorn(PartDefinition root, String name,
                                        float px, float py, float pz, float side) {
        PartDefinition parent = root.addOrReplaceChild(name + "_base",
                CubeListBuilder.create().texOffs(32, 48)
                        .addBox(-0.75F, -1.4F, -0.75F, 1.5F, 1.4F, 1.5F),
                PartPose.offsetAndRotation(px, py, pz, 0.15F, 0.0F, 0.15F * side));
        parent = parent.addOrReplaceChild(name + "_ring",
                CubeListBuilder.create().texOffs(32, 48)
                        .addBox(-0.8F, -0.5F, -0.8F, 1.6F, 0.5F, 1.6F),
                PartPose.offsetAndRotation(0.0F, -1.4F, 0.0F, -0.06F, 0.0F, 0.0F));
        float[] widths = {1.3F, 1.15F, 1.05F, 0.95F, 0.85F, 0.7F, 0.45F};
        float[] heights = {1.6F, 1.6F, 1.6F, 1.6F, 1.5F, 1.4F, 1.0F};
        float[] pitches = {-0.18F, -0.20F, -0.22F, -0.24F, -0.25F, -0.22F, -0.12F};
        float prevH = 0.5F;
        for (int i = 0; i < widths.length; i++) {
            float s = widths[i];
            float roll = (i < 4 ? 0.07F : 0.05F) * side;
            parent = parent.addOrReplaceChild(name + "_s" + i,
                    CubeListBuilder.create().texOffs(32, 48)
                            .addBox(-s / 2.0F, -heights[i], -s / 2.0F, s, heights[i], s),
                    PartPose.offsetAndRotation(0.0F, -prevH, 0.0F, pitches[i], 0.0F, roll));
            prevH = heights[i];
        }
    }

    // ── ram horns (bighorn spiral hugging the sides of the head) ─────────
    // Reference shape (bighorn-ram curl): the horn leaves the front corner,
    // sweeps BACK along the side of the head, curls down and comes forward
    // again, its tip pointing forward-down — read from the front as a big
    // C-spiral. Growth-ring ridges: short, slightly wider bands between the
    // long segments.

    private static void buildRamCurl(PartDefinition root, String name,
                                     float px, float py, float pz, float side) {
        PartDefinition parent = root.addOrReplaceChild(name + "_base",
                CubeListBuilder.create().texOffs(32, 48)
                        .addBox(-0.9F, -1.6F, -0.9F, 1.8F, 1.6F, 1.8F),
                PartPose.offsetAndRotation(px, py, pz, 0.30F, 0.0F, 0.38F * side));
        parent = parent.addOrReplaceChild(name + "_ring",
                CubeListBuilder.create().texOffs(32, 48)
                        .addBox(-0.95F, -0.55F, -0.95F, 1.9F, 0.55F, 1.9F),
                PartPose.offsetAndRotation(0.0F, -1.6F, 0.0F, 0.0F, 0.0F, 0.0F));
        // {width, height, pitch, yaw} — yaw is mirrored by `side`; negative
        // pitch bends the chain back, positive curls the tip forward
        float[][] segs = {
                {1.4F, 1.5F, -0.30F, -0.30F},  // sweep back, hugging the head side
                {1.2F, 0.6F, -0.10F, -0.08F},   // growth ring
                {1.35F, 1.4F, -0.40F, -0.26F},  // down + back
                {1.15F, 0.6F, -0.10F, -0.08F},  // growth ring
                {1.2F, 1.3F, -0.45F, -0.14F},   // bottom of the curl
                {1.0F, 0.5F, -0.10F, -0.06F},   // growth ring
                {1.0F, 1.2F, -0.25F, 0.12F},    // turning forward + outward
                {0.75F, 0.5F, 0.05F, 0.10F},    // growth ring
                {0.8F, 1.1F, 0.30F, 0.26F},     // tip curls forward
                {0.5F, 0.85F, 0.35F, 0.20F},    // sharp tip pointing forward
        };
        float prevH = 0.55F;
        for (int i = 0; i < segs.length; i++) {
            float[] s = segs[i];
            parent = parent.addOrReplaceChild(name + "_s" + i,
                    CubeListBuilder.create().texOffs(32, 48)
                            .addBox(-s[0] / 2.0F, -s[1], -s[0] / 2.0F, s[0], s[1], s[0]),
                    PartPose.offsetAndRotation(0.0F, -prevH, 0.0F, s[2], s[3] * side, 0.0F));
            prevH = s[1];
        }
    }

    // ── demon horn (single, sprouting from one side of the forehead) ─────
    // Reference shape (classic devil horn): smooth, thick at the base with a
    // small plate anchoring it to the skin, S-curved to a sharp tip.

    private static void buildDemonHorn(PartDefinition root) {
        PartDefinition parent = root.addOrReplaceChild("demon_plate",
                CubeListBuilder.create().texOffs(32, 48)
                        .addBox(-1.0F, -0.6F, -0.45F, 2.0F, 0.6F, 1.1F),
                PartPose.offsetAndRotation(1.7F, -7.0F, -3.7F, 0.22F, 0.0F, 0.0F));
        parent = parent.addOrReplaceChild("demon_ring",
                CubeListBuilder.create().texOffs(32, 48)
                        .addBox(-0.85F, -0.55F, -0.85F, 1.7F, 0.55F, 1.7F),
                PartPose.offsetAndRotation(0.0F, -0.6F, 0.0F, 0.30F, 0.0F, 0.0F));
        parent = parent.addOrReplaceChild("demon_1",
                CubeListBuilder.create().texOffs(32, 48)
                        .addBox(-0.75F, -1.7F, -0.75F, 1.5F, 1.7F, 1.5F),
                PartPose.offsetAndRotation(0.0F, -0.5F, 0.0F, 0.40F, 0.0F, 0.0F));
        parent = parent.addOrReplaceChild("demon_2",
                CubeListBuilder.create().texOffs(32, 48)
                        .addBox(-0.65F, -1.6F, -0.65F, 1.3F, 1.6F, 1.3F),
                PartPose.offsetAndRotation(0.0F, -1.7F, 0.0F, -0.30F, 0.0F, 0.0F));
        parent = parent.addOrReplaceChild("demon_3",
                CubeListBuilder.create().texOffs(32, 48)
                        .addBox(-0.55F, -1.4F, -0.55F, 1.1F, 1.4F, 1.1F),
                PartPose.offsetAndRotation(0.0F, -1.6F, 0.0F, -0.26F, 0.0F, 0.0F));
        parent = parent.addOrReplaceChild("demon_4",
                CubeListBuilder.create().texOffs(32, 48)
                        .addBox(-0.42F, -1.2F, -0.42F, 0.84F, 1.2F, 0.84F),
                PartPose.offsetAndRotation(0.0F, -1.4F, 0.0F, -0.22F, 0.0F, 0.0F));
        parent.addOrReplaceChild("demon_5",
                CubeListBuilder.create().texOffs(32, 48)
                        .addBox(-0.26F, -1.1F, -0.26F, 0.52F, 1.1F, 0.52F),
                PartPose.offsetAndRotation(0.0F, -1.2F, 0.0F, -0.16F, 0.0F, 0.0F));
    }

    // ── imp horns (small smooth pair on the forehead) ────────────────────

    private static void buildImpHorn(PartDefinition root, String name, float px, float side) {
        PartDefinition parent = root.addOrReplaceChild(name + "_0",
                CubeListBuilder.create().texOffs(32, 48)
                        .addBox(-0.68F, -1.5F, -0.68F, 1.36F, 1.5F, 1.36F),
                PartPose.offsetAndRotation(px, -7.0F, -3.7F, 0.40F, 0.0F, 0.30F * side));
        parent = parent.addOrReplaceChild(name + "_1",
                CubeListBuilder.create().texOffs(32, 48)
                        .addBox(-0.56F, -1.4F, -0.56F, 1.12F, 1.4F, 1.12F),
                PartPose.offsetAndRotation(0.0F, -1.5F, 0.0F, -0.26F, 0.0F, 0.0F));
        parent = parent.addOrReplaceChild(name + "_2",
                CubeListBuilder.create().texOffs(32, 48)
                        .addBox(-0.44F, -1.2F, -0.44F, 0.88F, 1.2F, 0.88F),
                PartPose.offsetAndRotation(0.0F, -1.4F, 0.0F, -0.24F, 0.0F, 0.0F));
        parent = parent.addOrReplaceChild(name + "_3",
                CubeListBuilder.create().texOffs(32, 48)
                        .addBox(-0.3F, -1.0F, -0.3F, 0.6F, 1.0F, 0.6F),
                PartPose.offsetAndRotation(0.0F, -1.2F, 0.0F, -0.20F, 0.0F, 0.0F));
        parent.addOrReplaceChild(name + "_4",
                CubeListBuilder.create().texOffs(32, 48)
                        .addBox(-0.16F, -0.9F, -0.16F, 0.32F, 0.9F, 0.32F),
                PartPose.offsetAndRotation(0.0F, -1.0F, 0.0F, -0.14F, 0.0F, 0.0F));
    }
}
