package net.developer.finery.ability;

import net.developer.finery.item.WingStyle;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.core.Holder;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
//? if >=1.21.5 {
/*import net.minecraft.particle.DragonBreathParticleEffect;
*///?}
import net.minecraft.core.Holder;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.phys.AABB;

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
    public WingStyle getOverlay() {
        return switch (this) {
            case DEVIL -> WingStyle.DEVIL;
            case DRAGON -> WingStyle.DRAGON;
            case ANGEL -> WingStyle.ANGEL;
            case BUTTERFLY -> WingStyle.BUTTERFLY;
        };
    }

    public void tick(LivingEntity entity) {
        if (!(entity.getCommandSenderWorld() instanceof ServerLevel world) || !(entity instanceof Player player)) {
            return;
        }

        boolean airborne = !player.onGround() && !player.isInWater();
        boolean falling = !player.onGround() && player.fallDistance > 1.5F;
        if (falling) {
            apply(player, MobEffects.SLOW_FALLING, 60, 0);
        }

        ParticleOptions particle;
        int interval;
        switch (this) {
            case DEVIL -> {
                particle = ParticleTypes.FLAME;
                interval = 6;
                apply(player, MobEffects.FIRE_RESISTANCE, 40, 0);
                if (player.getHealth() < player.getMaxHealth() * 0.4F) {
                    apply(player, MobEffects.DAMAGE_BOOST, 40, 1);
                    apply(player, MobEffects.MOVEMENT_SPEED, 40, 1);
                }
                if (player.hurtTime > 0) {
                    LivingEntity attacker = player.getLastHurtByMob();
                    if (attacker != null && attacker.distanceToSqr(player) < 16.0D) {
                        //? if >=1.20.5 {
                        /*attacker.setOnFireFor(4.0F);
                        *///?} else {
                        attacker.igniteForSeconds(4);
                        //?}
                    }
                }
            }
            case DRAGON -> {
                particle = ParticleTypes.SMOKE;
                interval = 10;
                apply(player, MobEffects.DAMAGE_RESISTANCE, 40, 0);
                if (airborne) {
                    apply(player, MobEffects.DAMAGE_BOOST, 40, 1);
                    apply(player, MobEffects.MOVEMENT_SPEED, 40, 0);
                }

                UUID id = player.getUUID();
                double lastY = LAST_Y.getOrDefault(id, player.getY());
                double descent = lastY - player.getY();
                LAST_Y.put(id, player.getY());

                if (player.onGround()) {
                    float fall = FALL_ACCUM.getOrDefault(id, 0.0F);
                    if (!player.isInWater() && fall >= SLAM_MIN_FALL
                            && world.getGameTime() >= SLAM_READY.getOrDefault(id, 0L)) {
                        SLAM_READY.put(id, world.getGameTime() + SLAM_COOLDOWN);
                        slam(world, player);
                    }
                    FALL_ACCUM.put(id, 0.0F);
                } else if (!player.isInWater() && descent > 0.0D) {
                    FALL_ACCUM.merge(id, (float) descent, Float::sum);
                }
            }
            case ANGEL -> {
                particle = ParticleTypes.END_ROD;
                interval = 10;
                apply(player, MobEffects.REGENERATION, 40, 0);
            }
            case BUTTERFLY -> {
                particle = ParticleTypes.CHERRY_LEAVES;
                interval = 8;
                apply(player, MobEffects.JUMP, 40, 1);
                apply(player, MobEffects.MOVEMENT_SPEED, 40, 0);
            }
            default -> throw new IllegalStateException();
        }

        if (player.tickCount % interval == 0) {
            trail(world, player, particle);
        }
    }

    /** Dragon landing shockwave: damages and hurls nearby hostile mobs away. */
    private static void slam(ServerLevel world, Player player) {
        AABB area = player.getBoundingBox().inflate(4.5D, 2.5D, 4.5D);
        for (LivingEntity target : world.getEntitiesOfClass(LivingEntity.class, area,
                candidate -> candidate instanceof Enemy && candidate.isAlive())) {
            target.knockback(1.4D, player.getX() - target.getX(), player.getZ() - target.getZ());
            //? if >=1.21.2 {
            /*target.hurt(world, player.getDamageSources().playerAttack(player), 6.0F);
            *///?} else {
            target.hurt(player.damageSources().playerAttack(player), 6.0F);
            //?}
        }
        world.sendParticles(ParticleTypes.EXPLOSION_EMITTER,
                player.getX(), player.getY() + 0.1D, player.getZ(), 1, 0.0D, 0.0D, 0.0D, 0.0D);
        //? if >=1.21.5 {
        /*world.sendParticles(DragonBreathParticleEffect.of(ParticleTypes.DRAGON_BREATH, 1.0F),
                player.getX(), player.getY() + 0.2D, player.getZ(), 40, 2.4D, 0.4D, 2.4D, 0.05D);
        *///?} else {
        world.sendParticles(ParticleTypes.DRAGON_BREATH,
                player.getX(), player.getY() + 0.2D, player.getZ(), 40, 2.4D, 0.4D, 2.4D, 0.05D);
        //?}
        world.playSound(null, player.getX(), player.getY(), player.getZ(),
                SoundEvents.ENDER_DRAGON_GROWL, SoundSource.PLAYERS, 0.7F, 0.9F);
    }

    private static void trail(ServerLevel world, Player player, ParticleOptions particle) {
        double yaw = Math.toRadians(player.yBodyRot);
        double x = player.getX() + Math.sin(yaw) * 0.4 + (world.random.nextDouble() - 0.5) * 0.7;
        double y = player.getY() + 0.6 + world.random.nextDouble() * 1.0;
        double z = player.getZ() - Math.cos(yaw) * 0.4 + (world.random.nextDouble() - 0.5) * 0.7;
        world.sendParticles(particle, x, y, z, 1, 0.0, 0.0, 0.0, 0.01);
    }

    //? if <1.20.5 {
    private static void apply(LivingEntity entity, Holder<MobEffect> effect, int duration, int amplifier) {
        MobEffectInstance current = entity.getEffect(effect);
        if (current == null || current.getDuration() < duration / 2) {
            entity.addEffect(new MobEffectInstance(effect, duration, amplifier, true, false, true));
        }
    }
    //?} else {
    /*private static void apply(LivingEntity entity, RegistryEntry<StatusEffect> effect, int duration, int amplifier) {
        StatusEffectInstance current = entity.getStatusEffect(effect);
        if (current == null || current.getDuration() < duration / 2) {
            entity.addStatusEffect(new StatusEffectInstance(effect, duration, amplifier, true, false, true));
        }
    }
    *///?}
}
