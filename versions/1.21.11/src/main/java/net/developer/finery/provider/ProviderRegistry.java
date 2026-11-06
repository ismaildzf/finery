package net.developer.finery.provider;

import java.util.List;

import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;

/** Picks the first loaded provider; NeoForge order is Curios, then Accessories. */
public final class ProviderRegistry {
    private static final List<SlotProvider> PROVIDERS = List.of(
            new CuriosProvider(),
            new AccessoriesProvider()
    );

    private static SlotProvider active;
    private static boolean resolved;

    private ProviderRegistry() {
    }

    public static SlotProvider active() {
        if (!resolved) {
            resolved = true;
            for (SlotProvider provider : PROVIDERS) {
                if (provider.isLoaded()) {
                    active = provider;
                    break;
                }
            }
        }
        return active;
    }

    public static boolean isWorn(LivingEntity entity, Item item) {
        SlotProvider provider = active();
        return provider != null && provider.isWorn(entity, item);
    }

    public static List<ItemStack> stacksIn(LivingEntity entity, SlotKind kind) {
        SlotProvider provider = active();
        return provider == null ? List.of() : provider.stacksIn(entity, kind);
    }

    public static String slotName(SlotKind kind) {
        SlotProvider provider = active();
        return provider == null ? kind.name().toLowerCase() : provider.slotName(kind);
    }

    public static boolean isWornAny(LivingEntity entity, List<? extends Item> items) {
        for (Item item : items) {
            if (isWorn(entity, item)) {
                return true;
            }
        }
        return false;
    }

    public static void reset() {
        active = null;
        resolved = false;
    }
}
