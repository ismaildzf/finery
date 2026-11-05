package net.developer.finery.provider;

import java.util.List;

import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.fml.ModList;
import top.theillusivec4.curios.api.CuriosApi;

public final class CuriosProvider implements SlotProvider {
    @Override
    public String id() {
        return "curios";
    }

    @Override
    public boolean isLoaded() {
        return ModList.get().isLoaded("curios");
    }

    @Override
    public boolean isWorn(LivingEntity entity, Item item) {
        return CuriosApi.getCuriosInventory(entity).map(handler -> handler.isEquipped(item)).orElse(false);
    }

    @Override
    public List<ItemStack> stacksIn(LivingEntity entity, SlotKind kind) {
        return CuriosApi.getCuriosInventory(entity)
                .map(handler -> handler.findCurios(slotName(kind)).stream().map(result -> result.stack()).toList())
                .orElse(List.of());
    }

    @Override
    public String slotName(SlotKind kind) {
        return switch (kind) {
            case CAPE -> "back";
            case WINGS -> "back";
            case HAT -> "head";
            case FACE -> "charm";
            case NECKLACE -> "necklace";
        };
    }
}
