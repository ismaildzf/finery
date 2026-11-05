package net.developer.finery.item;

import net.developer.finery.Finery;
import net.developer.finery.ability.HeadAbility;
import net.minecraft.item.ItemStack;
import net.minecraft.text.Text;
import net.minecraft.util.Formatting;
import net.minecraft.util.Identifier;

/**
 * Head cosmetic whose cloth colour is chosen per stack by a dye.
 * The dye id picks one of the pre-tinted sheets at texture time, so the
 * renderer stays untouched. Recoloured in a crafting grid with any dye.
 */
public class DyeableHeadItem extends HeadItem {

    private final int defaultDye;

    public DyeableHeadItem(Settings settings, String variant, String slot,
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
        return Identifier.of(Finery.MOD_ID,
                "textures/head/" + getVariant() + "_" + CosmeticDye.suffix(CosmeticDye.get(stack, defaultDye)) + ".png");
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
