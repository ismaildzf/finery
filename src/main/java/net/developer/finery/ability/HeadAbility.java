package net.developer.finery.ability;

import net.minecraft.entity.LivingEntity;
import net.minecraft.entity.effect.StatusEffect;
import net.minecraft.entity.effect.StatusEffectInstance;
import net.minecraft.entity.effect.StatusEffects;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.registry.entry.RegistryEntry;
import net.minecraft.server.world.ServerWorld;

/**
 * Passive abilities for the head cosmetics. Same server-side tick pattern
 * as the cape abilities; head pieces carry lighter effects than capes.
 */
public enum HeadAbility {
    /** Wizard hat: Fortune - Luck I while worn (fishing & loot luck). */
    FORTUNE,
    /** Bandanna: Ninja Reflex - Speed I for 3s when struck. */
    REFLEX,
    /** Eye patch: Steady Gaze - immune to Blindness. */
    STEADY_GAZE,
    /** Crown: Royal Vitality - Health Boost I (+2 hearts). */
    VITALITY,
    /** Dragon horns: Dive Fury - Strength I while airborne. */
    DIVE_FURY,
    /** Ram horns: Gore Charge - Strength I while sprinting. */
    GORE_CHARGE,
    /** Devil's horn: Hellfire - constant Fire Resistance while worn. */
    HELLFIRE,
    /** Imp horns: Impish Vigor - Absorption shield that keeps replenishing. */
    IMP_VIGOR,
    /** Eyewrap: Shadow Sight - clears Darkness. */
    SHADOW_SIGHT;

    public void tick(LivingEntity entity) {
        if (!(entity.getEntityWorld() instanceof ServerWorld) || !(entity instanceof PlayerEntity player)) {
            return;
        }

        switch (this) {
            case FORTUNE -> persistent(player, StatusEffects.LUCK, 0);
            case REFLEX -> {
                if (player.hurtTime > 6 && !player.hasStatusEffect(StatusEffects.SPEED)) {
                    apply(player, StatusEffects.SPEED, 60, 0);
                }
            }
            case STEADY_GAZE -> {
                if (player.hasStatusEffect(StatusEffects.BLINDNESS)) {
                    player.removeStatusEffect(StatusEffects.BLINDNESS);
                }
            }
            case VITALITY -> CosmeticStats.setMaxHealth(player, "crown_health", true, 4.0D);
            case DIVE_FURY -> {
                if (!player.isOnGround() && !player.isTouchingWater() && !player.hasVehicle()) {
                    apply(player, StatusEffects.STRENGTH, 30, 0);
                }
            }
            case GORE_CHARGE -> {
                if (player.isSprinting() && !player.hasVehicle()) {
                    apply(player, StatusEffects.STRENGTH, 30, 0);
                }
            }
            case HELLFIRE -> apply(player, StatusEffects.FIRE_RESISTANCE, 300, 0);
            case IMP_VIGOR -> apply(player, StatusEffects.ABSORPTION, 300, 0);
            case SHADOW_SIGHT -> {
                if (player.hasStatusEffect(StatusEffects.DARKNESS)) {
                    player.removeStatusEffect(StatusEffects.DARKNESS);
                }
            }
        }
    }

    /** Equipment passives: applied once while worn and removed on unequip. */
    public void onEquip(LivingEntity entity) {
        if (entity instanceof PlayerEntity player) {
            switch (this) {
                case VITALITY -> CosmeticStats.setMaxHealth(player, "crown_health", true, 4.0D);
                case FORTUNE -> persistent(player, StatusEffects.LUCK, 0);
                default -> {
                }
            }
        }
    }

    public void onUnequip(LivingEntity entity) {
        if (entity instanceof PlayerEntity player) {
            switch (this) {
                case VITALITY -> CosmeticStats.setMaxHealth(player, "crown_health", false, 0.0D);
                case FORTUNE -> player.removeStatusEffect(StatusEffects.LUCK);
                default -> {
                }
            }
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
