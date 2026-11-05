package net.developer.finery.ability;

import net.developer.finery.item.WingStyle;
import net.minecraft.entity.LivingEntity;
import net.minecraft.entity.effect.StatusEffect;
import net.minecraft.entity.effect.StatusEffectInstance;
import net.minecraft.entity.effect.StatusEffects;
import net.minecraft.entity.mob.Monster;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.particle.ParticleEffect;
import net.minecraft.particle.ParticleTypes;
//? if >=1.21.5 {
import net.minecraft.particle.DragonBreathParticleEffect;
//?}
import net.minecraft.registry.entry.RegistryEntry;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.sound.SoundCategory;
import net.minecraft.sound.SoundEvents;
import net.minecraft.util.math.Box;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * Legendary wing kits. Every wing catches long falls; on top of that each one
 * owns a distinct domain:
 *
 *  - DEVIL     : fire immunity + burns attackers + hellfire fury near death
 *  - DRAGON    : dragon hide + sky strength + a landing shockwave
 *  - ANGEL     : constant grace + fall immunity + a divine last-second shield
 *  - BUTTERFLY : permanent agility + a chance to flutter away from any hit
 */
public enum WingAbility {
    DEVIL,
    DRAGON,
    ANGEL,
    BUTTERFLY;

    /** Last known Y and accumulated descent per player; slow-falling zeroes
     *  vanilla fallDistance, so descent is tracked independently. */
    private static final Map<UUID, Double> LAST_Y = new HashMap<>();
    private static final Map<UUID, Float> FALL_ACCUM = new HashMap<>();
    private static final Map<UUID, Long> SLAM_READY = new HashMap<>();

    private static final long SLAM_COOLDOWN = 200L;
    private static final float SLAM_MIN_FALL = 3.0F;

    /** Mesh family rendered for this wing. */
    public WingStyle getStyle() {
        return switch (this) {
            case DEVIL -> WingStyle.DEVIL;
            case DRAGON -> WingStyle.DRAGON;
            case ANGEL -> WingStyle.ANGEL;
            case BUTTERFLY -> WingStyle.BUTTERFLY;
        };
    }

    public void tick(LivingEntity entity) {
        if (!(entity.getEntityWorld() instanceof ServerWorld world) || !(entity instanceof PlayerEntity player)) {
            return;
        }

        boolean airborne = !player.isOnGround() && !player.isTouchingWater();
        boolean falling = !player.isOnGround() && player.fallDistance > 1.5F;
        if (falling) {
            apply(player, StatusEffects.SLOW_FALLING, 60, 0);
        }

        ParticleEffect particle;
        int interval;
        switch (this) {
            case DEVIL -> {
                particle = ParticleTypes.FLAME;
                interval = 6;
                apply(player, StatusEffects.FIRE_RESISTANCE, 40, 0);
                if (player.getHealth() < player.getMaxHealth() * 0.4F) {
                    apply(player, StatusEffects.STRENGTH, 40, 1);
                    apply(player, StatusEffects.SPEED, 40, 1);
                }
                if (player.hurtTime > 0) {
                    LivingEntity attacker = player.getAttacker();
                    if (attacker != null && attacker.squaredDistanceTo(player) < 16.0D) {
                        //? if >=1.20.5 {
                        attacker.setOnFireFor(4.0F);
                        //?} else {
                        /*attacker.setOnFireFor(4);
                        *///?}
                    }
                }
            }
            case DRAGON -> {
                particle = ParticleTypes.SMOKE;
                interval = 10;
                apply(player, StatusEffects.RESISTANCE, 40, 0);
                if (airborne) {
                    apply(player, StatusEffects.STRENGTH, 40, 1);
                    apply(player, StatusEffects.SPEED, 40, 0);
                }

                UUID id = player.getUuid();
                double lastY = LAST_Y.getOrDefault(id, player.getY());
                double descent = lastY - player.getY();
                LAST_Y.put(id, player.getY());

                if (player.isOnGround()) {
                    float fall = FALL_ACCUM.getOrDefault(id, 0.0F);
                    if (!player.isTouchingWater() && fall >= SLAM_MIN_FALL
                            && world.getTime() >= SLAM_READY.getOrDefault(id, 0L)) {
                        SLAM_READY.put(id, world.getTime() + SLAM_COOLDOWN);
                        slam(world, player);
                    }
                    FALL_ACCUM.put(id, 0.0F);
                } else if (!player.isTouchingWater() && descent > 0.0D) {
                    FALL_ACCUM.merge(id, (float) descent, Float::sum);
                }
            }
            case ANGEL -> {
                particle = ParticleTypes.END_ROD;
                interval = 10;
                apply(player, StatusEffects.REGENERATION, 40, 0);
            }
            case BUTTERFLY -> {
                particle = ParticleTypes.CHERRY_LEAVES;
                interval = 8;
                apply(player, StatusEffects.JUMP_BOOST, 40, 1);
                apply(player, StatusEffects.SPEED, 40, 0);
            }
            default -> throw new IllegalStateException();
        }

        if (player.age % interval == 0) {
            trail(world, player, particle);
        }
    }

    /** Dragon landing shockwave: damages and hurls nearby hostile mobs away. */
    private static void slam(ServerWorld world, PlayerEntity player) {
        Box area = player.getBoundingBox().expand(4.5D, 2.5D, 4.5D);
        for (LivingEntity target : world.getEntitiesByClass(LivingEntity.class, area,
                candidate -> candidate instanceof Monster && candidate.isAlive())) {
            target.takeKnockback(1.4D, player.getX() - target.getX(), player.getZ() - target.getZ());
            //? if >=1.21.2 {
            target.damage(world, player.getDamageSources().playerAttack(player), 6.0F);
            //?} else {
            /*target.damage(player.getDamageSources().playerAttack(player), 6.0F);
            *///?}
        }
        world.spawnParticles(ParticleTypes.EXPLOSION_EMITTER,
                player.getX(), player.getY() + 0.1D, player.getZ(), 1, 0.0D, 0.0D, 0.0D, 0.0D);
        //? if >=1.21.5 {
        world.spawnParticles(DragonBreathParticleEffect.of(ParticleTypes.DRAGON_BREATH, 1.0F),
                player.getX(), player.getY() + 0.2D, player.getZ(), 40, 2.4D, 0.4D, 2.4D, 0.05D);
        //?} else {
        /*world.spawnParticles(ParticleTypes.DRAGON_BREATH,
                player.getX(), player.getY() + 0.2D, player.getZ(), 40, 2.4D, 0.4D, 2.4D, 0.05D);
        *///?}
        world.playSound(null, player.getX(), player.getY(), player.getZ(),
                SoundEvents.ENTITY_ENDER_DRAGON_GROWL, SoundCategory.PLAYERS, 0.7F, 0.9F);
    }

    private static void trail(ServerWorld world, PlayerEntity player, ParticleEffect particle) {
        double yaw = Math.toRadians(player.bodyYaw);
        double x = player.getX() + Math.sin(yaw) * 0.4 + (world.random.nextDouble() - 0.5) * 0.7;
        double y = player.getY() + 0.6 + world.random.nextDouble() * 1.0;
        double z = player.getZ() - Math.cos(yaw) * 0.4 + (world.random.nextDouble() - 0.5) * 0.7;
        world.spawnParticles(particle, x, y, z, 1, 0.0, 0.0, 0.0, 0.01);
    }

    //? if <1.20.5 {
    /*private static void apply(LivingEntity entity, StatusEffect effect, int duration, int amplifier) {
        StatusEffectInstance current = entity.getStatusEffect(effect);
        if (current == null || current.getDuration() < duration / 2) {
            entity.addStatusEffect(new StatusEffectInstance(effect, duration, amplifier, true, false, true));
        }
    }
    *///?} else {
    private static void apply(LivingEntity entity, RegistryEntry<StatusEffect> effect, int duration, int amplifier) {
        StatusEffectInstance current = entity.getStatusEffect(effect);
        if (current == null || current.getDuration() < duration / 2) {
            entity.addStatusEffect(new StatusEffectInstance(effect, duration, amplifier, true, false, true));
        }
    }
    //?}
}
