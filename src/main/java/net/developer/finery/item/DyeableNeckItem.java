package net.developer.finery.item;

import net.developer.finery.Finery;
import net.developer.finery.ability.NeckAbility;
import net.minecraft.item.ItemStack;
import net.minecraft.text.Text;
import net.minecraft.util.Formatting;
import net.minecraft.util.Identifier;

/**
 * Neckwear whose cloth colour is chosen per stack by a dye.
 * Same approach as {@link DyeableHeadItem}: the dye id selects a pre-tinted
 * sheet, and a crafting grid with any dye applies it.
 */
public class DyeableNeckItem extends NeckItem {

    private final int defaultDye;

    public DyeableNeckItem(Settings settings, String variant, NeckAbility ability,
                           CapeRarity rarity, String hintKey, int defaultDye) {
        super(settings, variant, ability, rarity, hintKey);
        this.defaultDye = defaultDye;
    }

    public int defaultDye() {
        return defaultDye;
    }

    @Override
    public Identifier getNeckTexture(ItemStack stack) {
        return Identifier.of(Finery.MOD_ID,
                "textures/neck/" + getVariant() + "_" + CosmeticDye.suffix(CosmeticDye.get(stack, defaultDye)) + ".png");
    }

    @Override
    public Text getName(ItemStack stack) {
        return Text.translatable("item.finery.dyed_name",
                        CosmeticDye.colorName(CosmeticDye.get(stack, defaultDye)),
                        Text.translatable(getTranslationKey()))
                .formatted(getRarity().color());
    }

    @Override
    protected void addExtraTooltip(ItemStack stack, java.util.List<Text> tooltip) {
        tooltip.add(Text.translatable("item.finery.tooltip.dye",
                        CosmeticDye.colorName(CosmeticDye.get(stack, defaultDye)))
                .formatted(Formatting.DARK_GRAY));
    }
}
