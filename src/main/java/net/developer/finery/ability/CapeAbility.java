package net.developer.finery.ability;

import net.minecraft.block.BlockState;
import net.minecraft.block.Blocks;
import net.minecraft.entity.LivingEntity;
import net.minecraft.entity.effect.StatusEffect;
import net.minecraft.entity.effect.StatusEffectInstance;
import net.minecraft.entity.effect.StatusEffects;
import net.minecraft.entity.mob.Monster;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.entity.vehicle.BoatEntity;
import net.minecraft.particle.ParticleEffect;
import net.minecraft.particle.ParticleTypes;
//? if >=1.21.5 {
import net.minecraft.particle.DragonBreathParticleEffect;
//?}
import net.minecraft.registry.entry.RegistryEntry;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.util.TypeFilter;
import net.minecraft.util.math.Box;

/**
 * Per-cape passive abilities, balanced by rarity tier:
 *
 *  - UNCOMMON (craftable): out-of-combat utility only.
 *  - EPIC (structure loot): domain combat or strong utility.
 *  - LEGENDARY (ancient city / end city): real combat kits.
 *
 * Abilities tick server-side only; particles are broadcast to nearby players.
 */
public enum CapeAbility {
    /** Uncommon: never burns. */
    FLAME_WARD,
    /** Uncommon: ocean exploration (Dolphin's Grace + Water Breathing in water). */
    TIDES_GRACE,
    /** Epic (village loot): Hero of the Village trade perk. */
    MERCHANT_CHARM,
    /** Uncommon: Slow Falling while sneaking. */
    VOIDSTEP,
    /** Legendary: Darkness immunity + Strength & Speed while in the dark. */
    SCULK_VEIL,
    /** Legendary: Slow Falling on long falls + Strength & Speed burst when hurt. */
    DRACONIC_GRACE,
    /** Epic: boat speed + Strength while fighting on water. */
    SEA_LEGS,
    /** Epic: Speed + Haste while standing on sand (desert domain). */
    DESERT_STRIDE,
    /** Epic: Resistance + Regeneration when below 3 hearts. */
    LAST_STAND,
    /** Epic: permanent Night Vision + Haste. */
    ARCANE_INSIGHT,
    /** Epic: Jump Boost + silent Speed while sneaking. */
    WINDBORNE,
    /** Epic: withering aura against nearby monsters + personal Wither immunity. */
    UNDYING_EMBER;

    private static final int DARK_LIGHT_THRESHOLD = 8;

    public void tick(LivingEntity entity) {
        if (!(entity.getEntityWorld() instanceof ServerWorld world) || !(entity instanceof PlayerEntity player)) {
            return;
        }

        switch (this) {
            case FLAME_WARD -> {
                if (player.isOnFire()) {
                    player.extinguish();
                    trail(world, player, ParticleTypes.FLAME, 5);
                }
            }
            case TIDES_GRACE -> {
                if (player.isTouchingWater()) {
                    apply(player, StatusEffects.DOLPHINS_GRACE, 260, 0);
                    apply(player, StatusEffects.WATER_BREATHING, 260, 0);
                    trail(world, player, ParticleTypes.BUBBLE, 8);
                }
            }
            case MERCHANT_CHARM -> {
                apply(player, StatusEffects.HERO_OF_THE_VILLAGE, 300, 0);
                trail(world, player, ParticleTypes.HAPPY_VILLAGER, 12);
            }
            case VOIDSTEP -> {
                if (player.isSneaking()) {
                    apply(player, StatusEffects.SLOW_FALLING, 40, 0);
                }
                trail(world, player, ParticleTypes.PORTAL, 10);
            }
            case SCULK_VEIL -> {
                // the deep dark holds no fear - and no blindness
                if (player.hasStatusEffect(StatusEffects.DARKNESS)) {
                    player.removeStatusEffect(StatusEffects.DARKNESS);
                }
                if (world.getLightLevel(player.getBlockPos()) < DARK_LIGHT_THRESHOLD) {
                    apply(player, StatusEffects.STRENGTH, 40, 0);
                    apply(player, StatusEffects.SPEED, 40, 0);
                    trail(world, player, ParticleTypes.SCULK_SOUL, 14);
                } else {
                    trail(world, player, ParticleTypes.SCULK_SOUL, 24);
                }
            }
            case DRACONIC_GRACE -> {
                // wings catch long falls
                if (player.fallDistance > 3.0F) {
                    apply(player, StatusEffects.SLOW_FALLING, 80, 0);
                    //? if >=1.21.5 {
                    trail(world, player, DragonBreathParticleEffect.of(ParticleTypes.DRAGON_BREATH, 1.0F), 4);
                    //?} else {
                    /*trail(world, player, ParticleTypes.DRAGON_BREATH, 4);
                    *///?}
                }
                // draconic rage when struck (the buff itself is the cooldown)
                if (player.hurtTime > 6 && !player.hasStatusEffect(StatusEffects.STRENGTH)) {
                    apply(player, StatusEffects.STRENGTH, 80, 0);
                    apply(player, StatusEffects.SPEED, 80, 0);
                    //? if >=1.21.5 {
                    burst(world, player, DragonBreathParticleEffect.of(ParticleTypes.DRAGON_BREATH, 1.0F), 8);
                    //?} else {
                    /*burst(world, player, ParticleTypes.DRAGON_BREATH, 8);
                    *///?}
                }
            }
            case SEA_LEGS -> {
                boolean atSea = player.getVehicle() instanceof BoatEntity || player.isTouchingWater();
                if (player.getVehicle() instanceof BoatEntity) {
                    apply(player, StatusEffects.SPEED, 40, 0);
                }
                if (atSea) {
                    apply(player, StatusEffects.STRENGTH, 40, 0);
                    trail(world, player, ParticleTypes.SPLASH, 8);
                }
            }
            case DESERT_STRIDE -> {
                BlockState below = world.getBlockState(player.getBlockPos().down());
                if (below.isOf(Blocks.SAND) || below.isOf(Blocks.RED_SAND)
                        || below.isOf(Blocks.SANDSTONE) || below.isOf(Blocks.RED_SANDSTONE)) {
                    apply(player, StatusEffects.SPEED, 40, 0);
                    apply(player, StatusEffects.HASTE, 40, 0);
                    trail(world, player, ParticleTypes.CRIT, 12);
                }
            }
            case LAST_STAND -> {
                if (player.getHealth() < 6.0F) {
                    // the totem refuses your death (re-applied while critical)
                    apply(player, StatusEffects.RESISTANCE, 60, 0);
                    apply(player, StatusEffects.REGENERATION, 60, 0);
                    if (player.age % 20 == 0) {
                        burst(world, player, ParticleTypes.TOTEM_OF_UNDYING, 6);
                    }
                }
            }
            case ARCANE_INSIGHT -> {
                apply(player, StatusEffects.NIGHT_VISION, 420, 0);
                apply(player, StatusEffects.HASTE, 40, 0);
                trail(world, player, ParticleTypes.ENCHANT, 12);
            }
            case WINDBORNE -> {
                apply(player, StatusEffects.JUMP_BOOST, 40, 0);
                if (player.isSneaking()) {
                    apply(player, StatusEffects.SPEED, 40, 0);
                }
                //? if >=1.21 {
                trail(world, player, ParticleTypes.SMALL_GUST, 14);
                //?} else {
                 /*trail(world, player, ParticleTypes.CLOUD, 14); 
                *///?}
            }
            case UNDYING_EMBER -> {
                if (player.hasStatusEffect(StatusEffects.WITHER)) {
                    player.removeStatusEffect(StatusEffects.WITHER);
                }
                // withering aura against hostile mobs
                if (player.age % 20 == 0) {
                    Box area = player.getBoundingBox().expand(4.0D);
                    for (LivingEntity target : world.getEntitiesByType(
                            TypeFilter.instanceOf(LivingEntity.class), area, e -> e instanceof Monster)) {
                        target.addStatusEffect(new StatusEffectInstance(
                                StatusEffects.WITHER, 60, 0, true, true, false));
                    }
                }
                trail(world, player, ParticleTypes.SMOKE, 10);
            }
        }
    }

    //? if <1.20.5 {
    
    /*private static void apply(LivingEntity entity, StatusEffect effect, int duration, int amplifier) {
        StatusEffectInstance current = entity.getStatusEffect(effect);
        if (current == null || current.getDuration() < duration / 2) {
            entity.addStatusEffect(new StatusEffectInstance(effect, duration, amplifier, true, false, false));
        }
    }
    
    *///?} else {
    private static void apply(LivingEntity entity, RegistryEntry<StatusEffect> effect, int duration, int amplifier) {
        StatusEffectInstance current = entity.getStatusEffect(effect);
        if (current == null || current.getDuration() < duration / 2) {
            entity.addStatusEffect(new StatusEffectInstance(effect, duration, amplifier, true, false, false));
        }
    }
    //?}

    /** Emits a small particle wisp behind the wearer every {@code interval} ticks. */
    private static void trail(ServerWorld world, PlayerEntity player, ParticleEffect particle, int interval) {
        if (player.age % interval != 0) {
            return;
        }
        double yaw = Math.toRadians(player.bodyYaw);
        double x = player.getX() + Math.sin(yaw) * 0.4 + (world.random.nextDouble() - 0.5) * 0.5;
        double y = player.getY() + 0.4 + world.random.nextDouble() * 1.0;
        double z = player.getZ() - Math.cos(yaw) * 0.4 + (world.random.nextDouble() - 0.5) * 0.5;
        world.spawnParticles(particle, x, y, z, 1, 0.0, 0.0, 0.0, 0.01);
    }

    /** A one-shot particle burst around the wearer. */
    private static void burst(ServerWorld world, PlayerEntity player, ParticleEffect particle, int count) {
        world.spawnParticles(particle, player.getX(), player.getY() + 1.0, player.getZ(),
                count, 0.4, 0.5, 0.4, 0.05);
    }
}
