package net.developer.finery.item;

import net.developer.finery.provider.ProviderRegistry;
import net.developer.finery.provider.SlotKind;
import top.theillusivec4.curios.api.SlotContext;
import top.theillusivec4.curios.api.type.capability.ICurioItem;

import net.developer.finery.Finery;
import net.developer.finery.ability.NeckAbility;
import net.minecraft.world.item.ItemStack;
import net.minecraft.network.chat.Component;
import net.minecraft.ChatFormatting;
import net.minecraft.resources.ResourceLocation;

/**
 * Neckwear whose cloth colour is chosen per stack by a dye.
 * Same approach as {@link DyeableHeadItem}: the dye id selects a pre-tinted
 * sheet, and a crafting grid with any dye applies it.
 */
public class DyeableNeckItem extends NeckItem {

    private final int defaultDye;

    public DyeableNeckItem(Properties settings, String variant, NeckAbility ability,
                           CapeRarity rarity, String hintKey, int defaultDye) {
        super(settings, variant, ability, rarity, hintKey);
        this.defaultDye = defaultDye;
    }

    public int defaultDye() {
        return defaultDye;
    }

    @Override
    public ResourceLocation getNeckTexture(ItemStack stack) {
        return new ResourceLocation(Finery.MOD_ID,
                "textures/neck/" + get() + "_" + CosmeticDye.suffix(CosmeticDye.get(stack, defaultDye)) + ".png");
    }

    @Override
    public Component getName(ItemStack stack) {
        return Component.translatable("item.finery.dyed_name",
                        CosmeticDye.colorName(CosmeticDye.get(stack, defaultDye)),
                        Component.translatable(getDescriptionId()))
                .withStyle(getRarity().color());
    }

    @Override
    protected void addExtraTooltip(ItemStack stack, java.util.List<Component> tooltip) {
        tooltip.add(Component.translatable("item.finery.tooltip.dye",
                        CosmeticDye.colorName(CosmeticDye.get(stack, defaultDye)))
                .withStyle(ChatFormatting.DARK_GRAY));
    }
}
