package net.developer.finery.provider;

import java.util.List;

import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;

/** One accessory backend (Curios, Accessories, Trinkets). */
public interface SlotProvider {
    String id();

    boolean isLoaded();

    boolean isWorn(LivingEntity entity, Item item);

    List<ItemStack> stacksIn(LivingEntity entity, SlotKind kind);

    /** Provider-side slot id for a logical slot. */
    String slotName(SlotKind kind);
}
