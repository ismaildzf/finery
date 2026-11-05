package net.developer.finery.item;

import net.developer.finery.provider.ProviderRegistry;
import net.developer.finery.provider.SlotKind;
import top.theillusivec4.curios.api.SlotContext;
import top.theillusivec4.curios.api.type.capability.ICurioItem;

import net.minecraft.ChatFormatting;

/** RPG rarity tiers: colors item names and adds a rarity tooltip line. */
public enum CapeRarity {
    UNCOMMON(ChatFormatting.GREEN, "item.finery.rarity.uncommon"),
    EPIC(ChatFormatting.LIGHT_PURPLE, "item.finery.rarity.epic"),
    LEGENDARY(ChatFormatting.GOLD, "item.finery.rarity.legendary");

    private final ChatFormatting color;
    private final String tooltipKey;

    CapeRarity(ChatFormatting color, String tooltipKey) {
        this.color = color;
        this.tooltipKey = tooltipKey;
    }

    public ChatFormatting color() {
        return color;
    }

    public String tooltipKey() {
        return tooltipKey;
    }
}
