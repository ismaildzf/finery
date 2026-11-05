package net.developer.finery.ability;

import io.wispforest.accessories.api.AccessoriesCapability;
import net.developer.finery.registry.ModItems;
import net.fabricmc.fabric.api.entity.event.v1.ServerLivingEntityEvents;
import net.minecraft.entity.LivingEntity;
import net.minecraft.entity.damage.DamageSource;
import net.minecraft.entity.effect.StatusEffect;
import net.minecraft.entity.effect.StatusEffectCategory;
import net.minecraft.entity.effect.StatusEffectInstance;
import net.minecraft.entity.effect.StatusEffects;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.item.Item;
import net.minecraft.particle.ParticleTypes;
import net.minecraft.registry.entry.RegistryEntry;
import net.minecraft.registry.tag.DamageTypeTags;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.sound.SoundCategory;
import net.minecraft.sound.SoundEvents;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Damage-time wing passives that a periodic tick cannot express:
 *
 *  - ANGEL     : ignores all fall damage; a hit that would drop the player under
 *                30% health triggers a divine shield before mitigation.
 *  - BUTTERFLY : 30% chance to cancel any entity hit and flutter away unseen.
 */
public final class WingEvents {

    private static final Map<UUID, Long> SHIELD_READY = new HashMap<>();
    private static final Map<UUID, Long> DODGE_READY = new HashMap<>();

    private static final long SHIELD_COOLDOWN = 1200L;
    private static final long DODGE_COOLDOWN = 240L;
    private static final float DODGE_CHANCE = 0.30F;

    private WingEvents() {
    }

    public static void register() {
        ServerLivingEntityEvents.ALLOW_DAMAGE.register(WingEvents::allowDamage);
    }

    private static boolean allowDamage(LivingEntity entity, DamageSource source, float amount) {
        if (!(entity instanceof ServerPlayerEntity player) || amount <= 0.0F) {
            return true;
        }
        if (source.isIn(DamageTypeTags.BYPASSES_INVULNERABILITY)) {
            return true;
        }

        ServerWorld world = (ServerWorld) player.getEntityWorld();
        if (source.isIn(DamageTypeTags.IS_FALL) && wearing(player, ModItems.ANGEL_WINGS)) {
            world.spawnParticles(ParticleTypes.END_ROD,
                    player.getX(), player.getY() + 0.2D, player.getZ(), 16, 0.5D, 0.3D, 0.5D, 0.03D);
            world.playSound(null, player.getX(), player.getY(), player.getZ(),
                    SoundEvents.ENTITY_ALLAY_AMBIENT_WITH_ITEM, SoundCategory.PLAYERS, 0.8F, 1.2F);
            return false;
        }

        if (source.getAttacker() instanceof LivingEntity && wearing(player, ModItems.BUTTERFLY_WINGS)) {
            long now = world.getTime();
            UUID id = player.getUuid();
            if (now >= DODGE_READY.getOrDefault(id, 0L) && player.getRandom().nextFloat() < DODGE_CHANCE) {
                DODGE_READY.put(id, now + DODGE_COOLDOWN);
                apply(player, StatusEffects.INVISIBILITY, 60, 0);
                apply(player, StatusEffects.SPEED, 80, 1);
                world.spawnParticles(ParticleTypes.CHERRY_LEAVES,
                        player.getX(), player.getY() + 1.0D, player.getZ(), 28, 0.7D, 0.8D, 0.7D, 0.02D);
                world.playSound(null, player.getX(), player.getY(), player.getZ(),
                        SoundEvents.BLOCK_AMETHYST_BLOCK_CHIME, SoundCategory.PLAYERS, 1.0F, 1.6F);
                return false;
            }
        }

        if (wearing(player, ModItems.ANGEL_WINGS)
                && !source.isIn(DamageTypeTags.BYPASSES_EFFECTS)
                && player.getHealth() - amount < player.getMaxHealth() * 0.3F) {
            long now = world.getTime();
            UUID id = player.getUuid();
            if (now >= SHIELD_READY.getOrDefault(id, 0L)) {
                SHIELD_READY.put(id, now + SHIELD_COOLDOWN);
                cleanse(player);
                apply(player, StatusEffects.ABSORPTION, 120, 1);
                apply(player, StatusEffects.RESISTANCE, 120, 1);
                apply(player, StatusEffects.REGENERATION, 120, 1);
                world.spawnParticles(ParticleTypes.TOTEM_OF_UNDYING,
                        player.getX(), player.getY() + 1.0D, player.getZ(), 40, 0.6D, 1.0D, 0.6D, 0.35D);
                world.spawnParticles(ParticleTypes.END_ROD,
                        player.getX(), player.getY() + 1.0D, player.getZ(), 20, 0.8D, 1.0D, 0.8D, 0.08D);
                world.playSound(null, player.getX(), player.getY(), player.getZ(),
                        SoundEvents.ITEM_TOTEM_USE, SoundCategory.PLAYERS, 1.0F, 1.1F);
            }
        }

        return true;
    }

    private static boolean wearing(PlayerEntity player, Item item) {
        return AccessoriesCapability.getOptionally(player)
                .map(capability -> !capability.getEquipped(item).isEmpty())
                .orElse(false);
    }

    //? if <1.20.5 {
    /*private static void cleanse(PlayerEntity player) {
        for (StatusEffectInstance instance : List.copyOf(player.getStatusEffects())) {
            StatusEffect effect = instance.getEffectType();
            if (effect.getCategory() == StatusEffectCategory.HARMFUL) {
                player.removeStatusEffect(effect);
            }
        }
    }
    *///?} else {
    private static void cleanse(PlayerEntity player) {
        for (StatusEffectInstance instance : List.copyOf(player.getStatusEffects())) {
            RegistryEntry<StatusEffect> effect = instance.getEffectType();
            if (effect.value().getCategory() == StatusEffectCategory.HARMFUL) {
                player.removeStatusEffect(effect);
            }
        }
    }
    //?}

    //? if <1.20.5 {
    /*private static void apply(LivingEntity entity, StatusEffect effect, int duration, int amplifier) {
        entity.addStatusEffect(new StatusEffectInstance(effect, duration, amplifier, true, false, true));
    }
    *///?} else {
    private static void apply(LivingEntity entity, RegistryEntry<StatusEffect> effect, int duration, int amplifier) {
        entity.addStatusEffect(new StatusEffectInstance(effect, duration, amplifier, true, false, true));
    }
    //?}
}
