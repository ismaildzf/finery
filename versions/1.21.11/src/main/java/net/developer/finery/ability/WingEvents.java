package net.developer.finery.ability;

import net.developer.finery.Finery;
import net.developer.finery.provider.ProviderRegistry;
import net.developer.finery.registry.ModItems;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.core.Holder;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.fml.common.Mod;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Damage-time wing passives:
 * ANGEL ignores fall damage and shields a lethal hit once per minute;
 * BUTTERFLY has a 30% chance to dodge and flutter away.
 */
@EventBusSubscriber(modid = Finery.MOD_ID)
public final class WingEvents {
    private static final Map<UUID, Long> SHIELD_READY = new HashMap<>();
    private static final Map<UUID, Long> DODGE_READY = new HashMap<>();

    private static final long SHIELD_COOLDOWN = 1200L;
    private static final long DODGE_COOLDOWN = 240L;
    private static final float DODGE_CHANCE = 0.30F;

    private WingEvents() {
    }

    @SubscribeEvent
    public static void onAttack(LivingIncomingDamageEvent event) {
        LivingEntity entity = event.getEntity();
        if (!(entity instanceof ServerPlayer player) || event.getAmount() <= 0.0F) {
            return;
        }
        DamageSource source = event.getSource();
        if (source.is(DamageTypeTags.BYPASSES_INVULNERABILITY)) {
            return;
        }
        if (!(player.level() instanceof ServerLevel world)) {
            return;
        }

        if (source.is(DamageTypeTags.IS_FALL) && wearing(player, ModItems.ANGEL_WINGS)) {
            world.sendParticles(ParticleTypes.END_ROD,
                    player.getX(), player.getY() + 0.2D, player.getZ(), 16, 0.5D, 0.3D, 0.5D, 0.03D);
            world.playSound(null, player.getX(), player.getY(), player.getZ(),
                    SoundEvents.ALLAY_AMBIENT_WITH_ITEM, SoundSource.PLAYERS, 0.8F, 1.2F);
            event.setCanceled(true);
            return;
        }

        if (source.getEntity() instanceof LivingEntity && wearing(player, ModItems.BUTTERFLY_WINGS)) {
            long now = world.getGameTime();
            UUID id = player.getUUID();
            if (now >= DODGE_READY.getOrDefault(id, 0L) && player.getRandom().nextFloat() < DODGE_CHANCE) {
                DODGE_READY.put(id, now + DODGE_COOLDOWN);
                apply(player, MobEffects.INVISIBILITY, 60, 0);
                apply(player, MobEffects.SPEED, 80, 1);
                world.sendParticles(ParticleTypes.CHERRY_LEAVES,
                        player.getX(), player.getY() + 1.0D, player.getZ(), 28, 0.7D, 0.8D, 0.7D, 0.02D);
                world.playSound(null, player.getX(), player.getY(), player.getZ(),
                        SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.PLAYERS, 1.0F, 1.6F);
                event.setCanceled(true);
                return;
            }
        }

        if (wearing(player, ModItems.ANGEL_WINGS)
                && !source.is(DamageTypeTags.BYPASSES_EFFECTS)
                && player.getHealth() - event.getAmount() < player.getMaxHealth() * 0.3F) {
            long now = world.getGameTime();
            UUID id = player.getUUID();
            if (now >= SHIELD_READY.getOrDefault(id, 0L)) {
                SHIELD_READY.put(id, now + SHIELD_COOLDOWN);
                cleanse(player);
                apply(player, MobEffects.ABSORPTION, 120, 1);
                apply(player, MobEffects.RESISTANCE, 120, 1);
                apply(player, MobEffects.REGENERATION, 120, 1);
                world.sendParticles(ParticleTypes.TOTEM_OF_UNDYING,
                        player.getX(), player.getY() + 1.0D, player.getZ(), 40, 0.6D, 1.0D, 0.6D, 0.35D);
                world.sendParticles(ParticleTypes.END_ROD,
                        player.getX(), player.getY() + 1.0D, player.getZ(), 20, 0.8D, 1.0D, 0.8D, 0.08D);
                world.playSound(null, player.getX(), player.getY(), player.getZ(),
                        SoundEvents.TOTEM_USE, SoundSource.PLAYERS, 1.0F, 1.1F);
            }
        }
    }

    private static boolean wearing(Player player, Item item) {
        return ProviderRegistry.isWorn(player, item);
    }

    private static void cleanse(Player player) {
        List<MobEffectInstance> harmful = new ArrayList<>();
        for (MobEffectInstance instance : player.getActiveEffects()) {
            if (instance.getEffect().value().getCategory() == MobEffectCategory.HARMFUL) {
                harmful.add(instance);
            }
        }
        for (MobEffectInstance instance : harmful) {
            Holder<MobEffect> effect = instance.getEffect();
            player.removeEffect(effect);
        }
    }

    private static void apply(LivingEntity entity, Holder<MobEffect> effect, int duration, int amplifier) {
        entity.addEffect(new MobEffectInstance(effect, duration, amplifier, true, false, true));
    }
}
