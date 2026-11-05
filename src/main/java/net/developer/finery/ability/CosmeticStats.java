package net.developer.finery.ability;

import net.minecraft.entity.LivingEntity;
import net.minecraft.entity.attribute.EntityAttributeInstance;
import net.minecraft.entity.attribute.EntityAttributeModifier;
import net.minecraft.entity.attribute.EntityAttributeModifier.Operation;
import net.minecraft.entity.attribute.EntityAttributes;
import net.minecraft.entity.player.PlayerEntity;

/**
 * Worn cosmetics that raise a real statistic instead of showing a status effect.
 * The modifier is keyed so equip/unequip and login can add/clear it without
 * touching modifiers from potions or beacons.
 */
public final class CosmeticStats {

    private CosmeticStats() {
    }

    public static void setMaxHealth(LivingEntity entity, String key, boolean on, double amount) {
        if (!(entity instanceof PlayerEntity player)) {
            return;
        }
        //? if <1.21 {
        /*EntityAttributeInstance instance = player.getAttributeInstance(EntityAttributes.GENERIC_MAX_HEALTH);
        if (instance == null) {
            return;
        }
        java.util.UUID id = java.util.UUID.nameUUIDFromBytes(
                ("finery:" + key).getBytes(java.nio.charset.StandardCharsets.UTF_8));
        if (on) {
            if (instance.getModifier(id) == null) {
                instance.addPersistentModifier(new EntityAttributeModifier(id, "finery:" + key, amount, Operation.ADDITION));
            }
        } else if (instance.getModifier(id) != null) {
            instance.removeModifier(id);
        }
        *///?} else {
        EntityAttributeInstance instance = player.getAttributeInstance(healthAttribute());
        if (instance == null) {
            return;
        }
        net.minecraft.util.Identifier id = net.minecraft.util.Identifier.of("finery", key);
        if (on) {
            if (instance.getModifier(id) == null) {
                instance.addPersistentModifier(new EntityAttributeModifier(id, amount, Operation.ADD_VALUE));
            }
        } else if (instance.getModifier(id) != null) {
            instance.removeModifier(id);
        }
        //?}
    }

    public static void clearWornBonuses(PlayerEntity player) {
        setMaxHealth(player, "crown_health", false, 0.0D);
        setMaxHealth(player, "locket_health", false, 0.0D);
    }

    //? if >=1.21 {
    private static net.minecraft.registry.entry.RegistryEntry<net.minecraft.entity.attribute.EntityAttribute> healthAttribute() {
        //? if <1.21.2 {
        /*return EntityAttributes.GENERIC_MAX_HEALTH;
        *///?} else {
        return EntityAttributes.MAX_HEALTH;
        //?}
    }
    //?}
}
