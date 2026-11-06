package net.developer.finery.provider;

import java.util.List;

import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.neoforged.fml.ModList;

/**
 * Optional second backend for NeoForge 1.20.1. The port starts with Curios;
 * this provider is filled in after Phase 0 proves the rendering path.
 */
public final class AccessoriesProvider implements SlotProvider {
    @Override
    public String id() {
        return "accessories";
    }

    @Override
    public boolean isLoaded() {
        return false;
    }

    @Override
    public boolean isWorn(LivingEntity entity, Item item) {
        return false;
    }

    @Override
    public List<ItemStack> stacksIn(LivingEntity entity, SlotKind kind) {
        return List.of();
    }

    @Override
    public String slotName(SlotKind kind) {
        return kind.name().toLowerCase();
    }
}
