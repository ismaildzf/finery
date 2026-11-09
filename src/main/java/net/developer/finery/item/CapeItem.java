package net.developer.finery.item;

import net.developer.finery.FineryConfig;
import io.wispforest.accessories.api.AccessoriesCapability;
//? if >=1.21.10 {
import io.wispforest.accessories.api.core.AccessoryItem;
//?} else {
/*import io.wispforest.accessories.api.AccessoryItem;
*///?}
import io.wispforest.accessories.api.slot.SlotReference;
import net.developer.finery.Finery;
import net.developer.finery.ability.CapeAbility;
import net.developer.finery.registry.ModItems;
import net.minecraft.entity.LivingEntity;
import net.minecraft.item.Item;
import net.minecraft.item.ItemStack;
//? if <1.20.5 {
/*import net.minecraft.client.item.TooltipContext;
import net.minecraft.world.World;
*///?} else {
import net.minecraft.item.tooltip.TooltipType;
//?}
//? if >=1.21.5 {
import net.minecraft.component.type.TooltipDisplayComponent;
import java.util.ArrayList;
import java.util.function.Consumer;
//?}
import net.minecraft.text.Text;
import net.minecraft.util.Formatting;
import net.minecraft.util.Identifier;

import java.util.List;

/**
 * Base class for all cape items.
 *
 * Implements the Accessories API's {@link Accessory} interface so this item
 * can be placed into the "cape" accessory slot. The slot binding itself is
 * done via the data-driven tag file at:
 *   data/accessories/tags/item/cape.json
 *
 * Each cape carries one {@link CapeAbility} that ticks while the cape is worn,
 * an RPG {@link CapeRarity} that colors its name, and a tooltip block
 * (rarity + ability + description + obtain hint).
 */
public class CapeItem extends AccessoryItem {

    /** Identifies the texture variant (e.g. "crimson", "warden"). */
    private final String capeVariant;

    /** Passive ability applied while this cape is worn. */
    private final CapeAbility ability;

    /** RPG rarity tier (name color + tooltip line). */
    private final CapeRarity rarity;

    /** Translation key for the "how to obtain" tooltip line (nullable). */
    private final String hintKey;

    /** Cached texture identifier for client-side rendering. */
    private Identifier capeTexture;

    public CapeItem(Settings settings, String variant, CapeAbility ability, CapeRarity rarity, String hintKey) {
        super(settings);
        this.capeVariant = variant;
        this.ability = ability;
        this.rarity = rarity;
        this.hintKey = hintKey;
    }

    public String getCapeVariant() {
        return capeVariant;
    }

    public CapeAbility getAbility() {
        return ability;
    }

    public CapeRarity getRarity() {
        return rarity;
    }

    /**
     * Returns the texture Identifier for this cape.
     * Texture path: assets/finery/textures/cape/{variant}.png
     */
    public Identifier getCapeTexture() {
        if (capeTexture == null) {
            capeTexture = Identifier.of(Finery.MOD_ID, "textures/cape/" + capeVariant + ".png");
        }
        return capeTexture;
    }

    // â”€â”€ Accessory Interface Implementation â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    @Override
    public void onEquip(ItemStack stack, SlotReference reference) {
        // Called when the cape is placed into the accessory slot
    }

    @Override
    public void onUnequip(ItemStack stack, SlotReference reference) {
        // Called when the cape is removed from the accessory slot
    }

    @Override
    public void tick(ItemStack stack, SlotReference reference) {
        if (!FineryConfig.get().abilityEnabled(stack, FineryConfig.Group.CAPE)) {
            return;
        }
        if (reference.entity() != null) {
            ability.tick(reference.entity());
        }
    }

    @Override
    public boolean canEquip(ItemStack stack, SlotReference reference) {
        if (!reference.slotName().equals("cape")) {
            return false;
        }
        if (!FineryConfig.get().exclusiveCapeAndWings) {
            return true;
        }
        LivingEntity entity = reference.entity();
        if (entity == null) {
            return true;
        }
        return AccessoriesCapability.getOptionally(entity)
                .map(capability -> {
                    for (WingItem wing : ModItems.WINGS) {
                        if (!capability.getEquipped(wing).isEmpty()) {
                            return false;
                        }
                    }
                    return true;
                })
                .orElse(true);
    }

    @Override
    public boolean canUnequip(ItemStack stack, SlotReference reference) {
        return true;
    }

    // â”€â”€ Display â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    @Override
    public Text getName(ItemStack stack) {
        return super.getName(stack).copy().formatted(rarity.color());
    }

    //? if <1.20.5 {
    /*@Override
    public void appendTooltip(ItemStack stack, World world, List<Text> tooltip, TooltipContext context) {
        addTooltip(stack, tooltip);
    }
    *///?} elif >=1.20.5 && <1.21.5 {
    /*@Override
    public void appendTooltip(ItemStack stack, Item.TooltipContext context, List<Text> tooltip, TooltipType type) {
        addTooltip(stack, tooltip);
    }
    *///?} else {
    @Override
    public void appendTooltip(ItemStack stack, Item.TooltipContext context, TooltipDisplayComponent displayComponent,
                              Consumer<Text> textConsumer, TooltipType type) {
        List<Text> lines = new ArrayList<>();
        addTooltip(stack, lines);
        lines.forEach(textConsumer);
    }
    //?}

    private void addTooltip(ItemStack stack, List<Text> tooltip) {
        tooltip.add(Text.translatable(rarity.tooltipKey())
                .formatted(rarity.color(), Formatting.BOLD)
                .append(Text.literal(" â€¢ ").formatted(Formatting.DARK_GRAY))
                .append(Text.translatable("item.finery.tooltip.cape").formatted(Formatting.GRAY)));
        tooltip.add(Text.translatable("item.finery.tooltip.ability")
                .formatted(Formatting.GOLD, Formatting.BOLD)
                .append(Text.translatable("item.finery." + capeVariant + "_cape.ability")
                        .formatted(Formatting.GOLD, Formatting.ITALIC)));
        for (String line : Text.translatable("item.finery." + capeVariant + "_cape.desc")
                .getString().split("\n", -1)) {
            tooltip.add(Text.literal(line));
        }
        if (hintKey != null) {
            tooltip.add(Text.translatable("item.finery.tooltip.obtain").formatted(Formatting.DARK_GRAY)
                    .append(Text.translatable(hintKey).formatted(Formatting.DARK_GRAY)));
        }
        tooltip.add(Text.translatable("item.finery.cape.exclusive")
                .formatted(Formatting.DARK_GRAY, Formatting.ITALIC));
    }
}


