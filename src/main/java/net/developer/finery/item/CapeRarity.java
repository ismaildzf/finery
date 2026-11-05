package net.developer.finery.item;

import net.minecraft.util.Formatting;

/** RPG rarity tiers: colors item names and adds a rarity tooltip line. */
public enum CapeRarity {
    UNCOMMON(Formatting.GREEN, "item.finery.rarity.uncommon"),
    EPIC(Formatting.LIGHT_PURPLE, "item.finery.rarity.epic"),
    LEGENDARY(Formatting.GOLD, "item.finery.rarity.legendary");

    private final Formatting color;
    private final String tooltipKey;

    CapeRarity(Formatting color, String tooltipKey) {
        this.color = color;
        this.tooltipKey = tooltipKey;
    }

    public Formatting color() {
        return color;
    }

    public String tooltipKey() {
        return tooltipKey;
    }
}
