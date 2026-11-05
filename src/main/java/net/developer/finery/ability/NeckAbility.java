package net.developer.finery.ability;

import net.minecraft.block.Blocks;
import net.minecraft.entity.LivingEntity;
import net.minecraft.entity.effect.StatusEffect;
import net.minecraft.entity.effect.StatusEffectInstance;
import net.minecraft.entity.effect.StatusEffects;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.registry.entry.RegistryEntry;
import net.minecraft.server.world.ServerWorld;

/**
 * Passive abilities for the neckwear chapter. Same server-side tick pattern
 * as the cape/head abilities; scarves lean utility, amulets carry the meat.
 */
public enum NeckAbility {
    /** Scarf: immune to freezing. */
    WARMTH,
    /** Onyx collar: Slow Falling while sneaking. */
    GLIDEWALK,
    /** Coral amulet: constant Conduit Power. */
    CORAL_CONDUIT,
    /** Moon locket: constant Night Vision. */
    MOONLIGHT,
    /** Serpent torc: poison immunity. */
    ANTIVENOM,
    /** Tundra torc: Speed I on ice and snow. */
    FROSTSTRIDE,
    /** Ember pendant: constant Fire Resistance. */
    EMBERHEART,
    /** Prayer beads: constant Regeneration I. */
    BLESSING,
    /** Heart locket: Health Boost II (+2 hearts). */
    VITALITY,
    /** Dragonbone torc: constant Strength I. */
    DRAGON_MIGHT;

    public void tick(LivingEntity entity) {
        if (!(entity.getEntityWorld() instanceof ServerWorld) || !(entity instanceof PlayerEntity player)) {
            return;
        }

        switch (this) {
            case WARMTH -> {
                if (player.getFrozenTicks() > 0) {
                    player.setFrozenTicks(0);
                }
            }
            case GLIDEWALK -> {
                if (player.isSneaking()) {
                    apply(player, StatusEffects.SLOW_FALLING, 40, 0);
                }
            }
            case CORAL_CONDUIT -> apply(player, StatusEffects.CONDUIT_POWER, 200, 0);
            case MOONLIGHT -> {
                if (player.getEntityWorld().isNight()) {
                    apply(player, StatusEffects.NIGHT_VISION, 300, 0);
                }
            }
            case ANTIVENOM -> {
                if (player.hasStatusEffect(StatusEffects.POISON)) {
                    player.removeStatusEffect(StatusEffects.POISON);
                }
            }
            case FROSTSTRIDE -> {
                if (player.getFrozenTicks() > 0) {
                    player.setFrozenTicks(0);
                }
                var below = player.getSteppingBlockState();
                if (below.isOf(Blocks.SNOW) || below.isOf(Blocks.SNOW_BLOCK) || below.isOf(Blocks.ICE)
                        || below.isOf(Blocks.PACKED_ICE) || below.isOf(Blocks.BLUE_ICE)
                        || below.isOf(Blocks.POWDER_SNOW)) {
                    apply(player, StatusEffects.SPEED, 40, 0);
                }
            }
            case EMBERHEART -> apply(player, StatusEffects.FIRE_RESISTANCE, 120, 0);
            case BLESSING -> apply(player, StatusEffects.REGENERATION, 120, 0);
            case VITALITY -> CosmeticStats.setMaxHealth(player, "locket_health", true, 8.0D);
            case DRAGON_MIGHT -> {
                if (player.getHealth() <= player.getMaxHealth() * 0.5F) {
                    apply(player, StatusEffects.STRENGTH, 60, 0);
                }
            }
        }
    }

    /** Equipment passives: applied once while worn and removed on unequip. */
    public void onEquip(LivingEntity entity) {
        if (entity instanceof PlayerEntity player && this == VITALITY) {
            CosmeticStats.setMaxHealth(player, "locket_health", true, 8.0D);
        }
    }

    public void onUnequip(LivingEntity entity) {
        if (entity instanceof PlayerEntity player && this == VITALITY) {
            CosmeticStats.setMaxHealth(player, "locket_health", false, 0.0D);
        }
    }

    //? if <1.20.5 {
    /*private static void persistent(LivingEntity entity, StatusEffect effect, int amplifier) {
        var current = entity.getStatusEffect(effect);
        if (current == null || current.getAmplifier() < amplifier) {
            entity.addStatusEffect(new StatusEffectInstance(effect, Integer.MAX_VALUE, amplifier, true, false, false));
        }
    }

    private static void apply(LivingEntity entity, StatusEffect effect, int duration, int amplifier) {
        StatusEffectInstance current = entity.getStatusEffect(effect);
        if (current == null || current.getDuration() < duration / 2) {
            entity.addStatusEffect(new StatusEffectInstance(effect, duration, amplifier, true, false, false));
        }
    }
    *///?} else {
    private static void persistent(LivingEntity entity, RegistryEntry<StatusEffect> effect, int amplifier) {
        var current = entity.getStatusEffect(effect);
        if (current == null || current.getAmplifier() < amplifier) {
            entity.addStatusEffect(new StatusEffectInstance(effect, Integer.MAX_VALUE, amplifier, true, false, false));
        }
    }

    private static void apply(LivingEntity entity, RegistryEntry<StatusEffect> effect, int duration, int amplifier) {
        StatusEffectInstance current = entity.getStatusEffect(effect);
        if (current == null || current.getDuration() < duration / 2) {
            entity.addStatusEffect(new StatusEffectInstance(effect, duration, amplifier, true, false, false));
        }
    }
    //?}
}
