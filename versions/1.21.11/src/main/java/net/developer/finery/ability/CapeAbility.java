package net.developer.finery.ability;

import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.core.Holder;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.vehicle.boat.Boat;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.particles.PowerParticleOption;
//? if >=1.21.5 {
/*import net.minecraft.particle.DragonBreathParticleEffect;
*///?}
import net.minecraft.core.Holder;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.entity.EntityTypeTest;
import net.minecraft.world.phys.AABB;

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
        if (!(entity.level() instanceof ServerLevel world) || !(entity instanceof Player player)) {
            return;
        }

        switch (this) {
            case FLAME_WARD -> {
                if (player.isOnFire()) {
                    player.clearFire();
                    trail(world, player, ParticleTypes.FLAME, 5);
                }
            }
            case TIDES_GRACE -> {
                if (player.isInWater()) {
                    apply(player, MobEffects.DOLPHINS_GRACE, 260, 0);
                    apply(player, MobEffects.WATER_BREATHING, 260, 0);
                    trail(world, player, ParticleTypes.BUBBLE, 8);
                }
            }
            case MERCHANT_CHARM -> {
                apply(player, MobEffects.HERO_OF_THE_VILLAGE, 300, 0);
                trail(world, player, ParticleTypes.HAPPY_VILLAGER, 12);
            }
            case VOIDSTEP -> {
                if (player.isShiftKeyDown()) {
                    apply(player, MobEffects.SLOW_FALLING, 40, 0);
                }
                trail(world, player, ParticleTypes.PORTAL, 10);
            }
            case SCULK_VEIL -> {
                // the deep dark holds no fear - and no blindness
                if (player.hasEffect(MobEffects.DARKNESS)) {
                    player.removeEffect(MobEffects.DARKNESS);
                }
                if (world.getMaxLocalRawBrightness(player.blockPosition()) < DARK_LIGHT_THRESHOLD) {
                    apply(player, MobEffects.STRENGTH, 40, 0);
                    apply(player, MobEffects.SPEED, 40, 0);
                    trail(world, player, ParticleTypes.SCULK_SOUL, 14);
                } else {
                    trail(world, player, ParticleTypes.SCULK_SOUL, 24);
                }
            }
            case DRACONIC_GRACE -> {
                // wings catch long falls
                if (player.fallDistance > 3.0F) {
                    apply(player, MobEffects.SLOW_FALLING, 80, 0);
                    //? if >=1.21.5 {
                    /*trail(world, player, DragonBreathParticleEffect.of(ParticleTypes.DRAGON_BREATH, 1.0F), 4);
                    *///?} else {
                    trail(world, player, PowerParticleOption.create(ParticleTypes.DRAGON_BREATH, 1.0F), 4);
                    //?}
                }
                // draconic rage when struck (the buff itself is the cooldown)
                if (player.hurtTime > 6 && !player.hasEffect(MobEffects.STRENGTH)) {
                    apply(player, MobEffects.STRENGTH, 80, 0);
                    apply(player, MobEffects.SPEED, 80, 0);
                    //? if >=1.21.5 {
                    /*burst(world, player, DragonBreathParticleEffect.of(ParticleTypes.DRAGON_BREATH, 1.0F), 8);
                    *///?} else {
                    burst(world, player, PowerParticleOption.create(ParticleTypes.DRAGON_BREATH, 1.0F), 8);
                    //?}
                }
            }
            case SEA_LEGS -> {
                boolean atSea = player.getVehicle() instanceof Boat || player.isInWater();
                if (player.getVehicle() instanceof Boat) {
                    apply(player, MobEffects.SPEED, 40, 0);
                }
                if (atSea) {
                    apply(player, MobEffects.STRENGTH, 40, 0);
                    trail(world, player, ParticleTypes.SPLASH, 8);
                }
            }
            case DESERT_STRIDE -> {
                BlockState below = world.getBlockState(player.blockPosition().below());
                if (below.is(Blocks.SAND) || below.is(Blocks.RED_SAND)
                        || below.is(Blocks.SANDSTONE) || below.is(Blocks.RED_SANDSTONE)) {
                    apply(player, MobEffects.SPEED, 40, 0);
                    apply(player, MobEffects.HASTE, 40, 0);
                    trail(world, player, ParticleTypes.CRIT, 12);
                }
            }
            case LAST_STAND -> {
                if (player.getHealth() < 6.0F) {
                    // the totem refuses your death (re-applied while critical)
                    apply(player, MobEffects.RESISTANCE, 60, 0);
                    apply(player, MobEffects.REGENERATION, 60, 0);
                    if (player.tickCount % 20 == 0) {
                        burst(world, player, ParticleTypes.TOTEM_OF_UNDYING, 6);
                    }
                }
            }
            case ARCANE_INSIGHT -> {
                apply(player, MobEffects.NIGHT_VISION, 420, 0);
                apply(player, MobEffects.HASTE, 40, 0);
                trail(world, player, ParticleTypes.ENCHANT, 12);
            }
            case WINDBORNE -> {
                apply(player, MobEffects.JUMP_BOOST, 40, 0);
                if (player.isShiftKeyDown()) {
                    apply(player, MobEffects.SPEED, 40, 0);
                }
                //? if >=1.21 {
                /*trail(world, player, ParticleTypes.SMALL_GUST, 14);
                *///?} else {
                 trail(world, player, ParticleTypes.CLOUD, 14); 
                //?}
            }
            case UNDYING_EMBER -> {
                if (player.hasEffect(MobEffects.WITHER)) {
                    player.removeEffect(MobEffects.WITHER);
                }
                // withering aura against hostile mobs
                if (player.tickCount % 20 == 0) {
                    AABB area = player.getBoundingBox().inflate(4.0D);
                    for (LivingEntity target : world.getEntitiesOfClass(
                            LivingEntity.class, area, e -> e instanceof Enemy)) {
                        target.addEffect(new MobEffectInstance(
                                MobEffects.WITHER, 60, 0, true, true, false));
                    }
                }
                trail(world, player, ParticleTypes.SMOKE, 10);
            }
        }
    }

    //? if <1.20.5 {
    
    private static void apply(LivingEntity entity, Holder<MobEffect> effect, int duration, int amplifier) {
        MobEffectInstance current = entity.getEffect(effect);
        if (current == null || current.getDuration() < duration / 2) {
            entity.addEffect(new MobEffectInstance(effect, duration, amplifier, true, false, false));
        }
    }
    
    //?} else {
    /*private static void apply(LivingEntity entity, RegistryEntry<StatusEffect> effect, int duration, int amplifier) {
        StatusEffectInstance current = entity.getStatusEffect(effect);
        if (current == null || current.getDuration() < duration / 2) {
            entity.addStatusEffect(new StatusEffectInstance(effect, duration, amplifier, true, false, false));
        }
    }
    *///?}

    /** Emits a small particle wisp behind the wearer every {@code interval} ticks. */
    private static void trail(ServerLevel world, Player player, ParticleOptions particle, int interval) {
        if (player.tickCount % interval != 0) {
            return;
        }
        double yaw = Math.toRadians(player.yBodyRot);
        double x = player.getX() + Math.sin(yaw) * 0.4 + (world.random.nextDouble() - 0.5) * 0.5;
        double y = player.getY() + 0.4 + world.random.nextDouble() * 1.0;
        double z = player.getZ() - Math.cos(yaw) * 0.4 + (world.random.nextDouble() - 0.5) * 0.5;
        world.sendParticles(particle, x, y, z, 1, 0.0, 0.0, 0.0, 0.01);
    }

    /** A one-shot particle burst around the wearer. */
    private static void burst(ServerLevel world, Player player, ParticleOptions particle, int count) {
        world.sendParticles(particle, player.getX(), player.getY() + 1.0, player.getZ(),
                count, 0.4, 0.5, 0.4, 0.05);
    }
}
