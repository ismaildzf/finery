package net.developer.finery.ability;

import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.core.Holder;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.player.Player;
import net.minecraft.core.Holder;
import net.minecraft.server.level.ServerLevel;

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
        if (!(entity.level() instanceof ServerLevel) || !(entity instanceof Player player)) {
            return;
        }

        switch (this) {
            case WARMTH -> {
                if (player.getTicksFrozen() > 0) {
                    player.setTicksFrozen(0);
                }
            }
            case GLIDEWALK -> {
                if (player.isShiftKeyDown()) {
                    apply(player, MobEffects.SLOW_FALLING, 40, 0);
                }
            }
            case CORAL_CONDUIT -> apply(player, MobEffects.CONDUIT_POWER, 200, 0);
            case MOONLIGHT -> {
                long dayTime = player.level().getDayTime() % 24000L;
                if (dayTime >= 13000L && dayTime < 23000L) {
                    apply(player, MobEffects.NIGHT_VISION, 300, 0);
                }
            }
            case ANTIVENOM -> {
                if (player.hasEffect(MobEffects.POISON)) {
                    player.removeEffect(MobEffects.POISON);
                }
            }
            case FROSTSTRIDE -> {
                if (player.getTicksFrozen() > 0) {
                    player.setTicksFrozen(0);
                }
                var below = player.getBlockStateOn();
                if (below.is(Blocks.SNOW) || below.is(Blocks.SNOW_BLOCK) || below.is(Blocks.ICE)
                        || below.is(Blocks.PACKED_ICE) || below.is(Blocks.BLUE_ICE)
                        || below.is(Blocks.POWDER_SNOW)) {
                    apply(player, MobEffects.SPEED, 40, 0);
                }
            }
            case EMBERHEART -> apply(player, MobEffects.FIRE_RESISTANCE, 120, 0);
            case BLESSING -> apply(player, MobEffects.REGENERATION, 120, 0);
            case VITALITY -> CosmeticStats.setMaxHealth(player, "locket_health", true, 8.0D);
            case DRAGON_MIGHT -> {
                if (player.getHealth() <= player.getMaxHealth() * 0.5F) {
                    apply(player, MobEffects.STRENGTH, 60, 0);
                }
            }
        }
    }

    /** Equipment passives: applied once while worn and removed on unequip. */
    public void onEquip(LivingEntity entity) {
        if (entity instanceof Player player && this == VITALITY) {
            CosmeticStats.setMaxHealth(player, "locket_health", true, 8.0D);
        }
    }

    public void onUnequip(LivingEntity entity) {
        if (entity instanceof Player player && this == VITALITY) {
            CosmeticStats.setMaxHealth(player, "locket_health", false, 0.0D);
        }
    }

    //? if <1.20.5 {
    private static void persistent(LivingEntity entity, Holder<MobEffect> effect, int amplifier) {
        var current = entity.getEffect(effect);
        if (current == null || current.getAmplifier() < amplifier) {
            entity.addEffect(new MobEffectInstance(effect, Integer.MAX_VALUE, amplifier, true, false, false));
        }
    }

    private static void apply(LivingEntity entity, Holder<MobEffect> effect, int duration, int amplifier) {
        MobEffectInstance current = entity.getEffect(effect);
        if (current == null || current.getDuration() < duration / 2) {
            entity.addEffect(new MobEffectInstance(effect, duration, amplifier, true, false, false));
        }
    }
    //?} else {
    /*private static void persistent(LivingEntity entity, RegistryEntry<StatusEffect> effect, int amplifier) {
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
    *///?}
}
