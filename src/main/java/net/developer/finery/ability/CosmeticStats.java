package net.developer.finery.ability;

import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.AttributeModifier.Operation;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;

/**
 * Worn cosmetics that raise a real statistic instead of showing a status effect.
 * The modifier is keyed so equip/unequip and login can add/clear it without
 * touching modifiers from potions or beacons.
 */
public final class CosmeticStats {

    private CosmeticStats() {
    }

    public static void setMaxHealth(LivingEntity entity, String key, boolean on, double amount) {
        if (!(entity instanceof Player player)) {
            return;
        }
        //? if <1.21 {
        AttributeInstance instance = player.getAttribute(Attributes.MAX_HEALTH);
        if (instance == null) {
            return;
        }
        java.util.UUID id = java.util.UUID.nameUUIDFromBytes(
                ("finery:" + key).getBytes(java.nio.charset.StandardCharsets.UTF_8));
        if (on) {
            if (instance.getModifier(id) == null) {
                instance.addPermanentModifier(new AttributeModifier(id, "finery:" + key, amount, Operation.ADDITION));
            }
        } else if (instance.getModifier(id) != null) {
            instance.removeModifier(id);
        }
        //?} else {
        /*EntityAttributeInstance instance = player.getAttributeInstance(healthAttribute());
        if (instance == null) {
            return;
        }
        net.minecraft.resources.ResourceLocation id = net.minecraft.resources.ResourceLocation.of("finery", key);
        if (on) {
            if (instance.getModifier(id) == null) {
                instance.addPersistentModifier(new EntityAttributeModifier(id, amount, Operation.ADD_VALUE));
            }
        } else if (instance.getModifier(id) != null) {
            instance.removeModifier(id);
        }
        *///?}
    }

    public static void clearWornBonuses(Player player) {
        setMaxHealth(player, "crown_health", false, 0.0D);
        setMaxHealth(player, "locket_health", false, 0.0D);
    }

    //? if >=1.21 {
    /*private static net.minecraft.core.Holder<net.minecraft.world.entity.ai.attributes.Attribute> healthAttribute() {
        //? if <1.21.2 {
        return EntityAttributes.MAX_HEALTH;
        //?} else {
        /^return EntityAttributes.MAX_HEALTH;
        ^///?}
    }
    *///?}
}
