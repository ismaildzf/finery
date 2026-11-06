package net.developer.finery.item;

import net.developer.finery.provider.ProviderRegistry;
import net.developer.finery.provider.SlotKind;
import top.theillusivec4.curios.api.SlotContext;
import top.theillusivec4.curios.api.type.capability.ICurioItem;

import net.developer.finery.Finery;
import net.developer.finery.ability.HeadAbility;
import net.minecraft.world.item.ItemStack;
import net.minecraft.network.chat.Component;
import net.minecraft.ChatFormatting;
import net.minecraft.resources.Identifier;

/**
 * Head cosmetic whose cloth colour is chosen per stack by a dye.
 * The dye id picks one of the pre-tinted sheets at texture time, so the
 * renderer stays untouched. Recoloured in a crafting grid with any dye.
 */
public class DyeableHeadItem extends HeadItem {

    private final int defaultDye;

    public DyeableHeadItem(Properties settings, String variant, String slot,
                           HeadAbility ability, CapeRarity rarity, String hintKey,
                           int defaultDye) {
        super(settings, variant, slot, ability, rarity, hintKey);
        this.defaultDye = defaultDye;
    }

    public int defaultDye() {
        return defaultDye;
    }

    @Override
    public Identifier getHeadTexture(ItemStack stack) {
        return Identifier.fromNamespaceAndPath(Finery.MOD_ID,
                "textures/head/" + get() + "_" + CosmeticDye.suffix(CosmeticDye.get(stack, defaultDye)) + ".png");
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
