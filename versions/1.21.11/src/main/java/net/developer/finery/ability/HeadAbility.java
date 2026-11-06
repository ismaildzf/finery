package net.developer.finery.ability;

import net.minecraft.world.entity.LivingEntity;
import net.minecraft.core.Holder;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.player.Player;
import net.minecraft.core.Holder;
import net.minecraft.server.level.ServerLevel;

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
        if (!(entity.level() instanceof ServerLevel) || !(entity instanceof Player player)) {
            return;
        }

        switch (this) {
            case FORTUNE -> persistent(player, MobEffects.LUCK, 0);
            case REFLEX -> {
                if (player.hurtTime > 6 && !player.hasEffect(MobEffects.SPEED)) {
                    apply(player, MobEffects.SPEED, 60, 0);
                }
            }
            case STEADY_GAZE -> {
                if (player.hasEffect(MobEffects.BLINDNESS)) {
                    player.removeEffect(MobEffects.BLINDNESS);
                }
            }
            case VITALITY -> CosmeticStats.setMaxHealth(player, "crown_health", true, 4.0D);
            case DIVE_FURY -> {
                if (!player.onGround() && !player.isInWater() && !player.isPassenger()) {
                    apply(player, MobEffects.STRENGTH, 30, 0);
                }
            }
            case GORE_CHARGE -> {
                if (player.isSprinting() && !player.isPassenger()) {
                    apply(player, MobEffects.STRENGTH, 30, 0);
                }
            }
            case HELLFIRE -> apply(player, MobEffects.FIRE_RESISTANCE, 300, 0);
            case IMP_VIGOR -> apply(player, MobEffects.ABSORPTION, 300, 0);
            case SHADOW_SIGHT -> {
                if (player.hasEffect(MobEffects.DARKNESS)) {
                    player.removeEffect(MobEffects.DARKNESS);
                }
            }
        }
    }

    /** Equipment passives: applied once while worn and removed on unequip. */
    public void onEquip(LivingEntity entity) {
        if (entity instanceof Player player) {
            switch (this) {
                case VITALITY -> CosmeticStats.setMaxHealth(player, "crown_health", true, 4.0D);
                case FORTUNE -> persistent(player, MobEffects.LUCK, 0);
                default -> {
                }
            }
        }
    }

    public void onUnequip(LivingEntity entity) {
        if (entity instanceof Player player) {
            switch (this) {
                case VITALITY -> CosmeticStats.setMaxHealth(player, "crown_health", false, 0.0D);
                case FORTUNE -> player.removeEffect(MobEffects.LUCK);
                default -> {
                }
            }
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
