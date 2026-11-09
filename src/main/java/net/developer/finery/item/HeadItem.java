package net.developer.finery.item;

import net.developer.finery.FineryConfig;
//? if >=1.21.10 {
import io.wispforest.accessories.api.core.AccessoryItem;
//?} else {
/*import io.wispforest.accessories.api.AccessoryItem;
*///?}
import io.wispforest.accessories.api.slot.SlotReference;
import net.developer.finery.Finery;
import net.developer.finery.ability.HeadAbility;
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
 * Head cosmetics (hats, horns, headbands, eye patches).
 *
 * Bound to the Accessories "hat" or "face" slot via data-driven tags:
 *   data/accessories/tags/item/hat.json
 *   data/accessories/tags/item/face.json
 *
 * Rendered by the client's HeadAccessoryRenderer via {@link #getHeadTexture()}.
 */
public class HeadItem extends AccessoryItem {

    private final String variant;
    private final String slotName;
    private final HeadAbility ability;
    private final CapeRarity rarity;
    private final String hintKey;

    private Identifier headTexture;

    public HeadItem(Settings settings, String variant, String slotName,
                    HeadAbility ability, CapeRarity rarity, String hintKey) {
        super(settings);
        this.variant = variant;
        this.slotName = slotName;
        this.ability = ability;
        this.rarity = rarity;
        this.hintKey = hintKey;
    }

    public String getVariant() {
        return variant;
    }

    public String getSlotName() {
        return slotName;
    }

    /** Texture path: assets/finery/textures/head/{variant}.png */
    public Identifier getHeadTexture() {
        if (headTexture == null) {
            headTexture = Identifier.of(Finery.MOD_ID, "textures/head/" + variant + ".png");
        }
        return headTexture;
    }

    /** Overridden by dyable pieces, which pick a tinted sheet per stack. */
    public Identifier getHeadTexture(ItemStack stack) {
        return getHeadTexture();
    }

    public CapeRarity getRarity() {
        return rarity;
    }

    @Override
    public void onEquip(ItemStack stack, SlotReference reference) {
        if (!FineryConfig.get().abilityEnabled(stack, FineryConfig.Group.HEAD)) {
            return;
        }
        if (reference.entity() != null) {
            ability.onEquip(reference.entity());
        }
    }

    @Override
    public void onUnequip(ItemStack stack, SlotReference reference) {
        if (reference.entity() != null) {
            ability.onUnequip(reference.entity());
        }
    }

    @Override
    public void tick(ItemStack stack, SlotReference reference) {
        if (!FineryConfig.get().abilityEnabled(stack, FineryConfig.Group.HEAD)) {
            return;
        }
        if (reference.entity() != null) {
            ability.tick(reference.entity());
        }
    }

    @Override
    public boolean canEquip(ItemStack stack, SlotReference reference) {
        return slotName.equals(reference.slotName());
    }

    @Override
    public boolean canUnequip(ItemStack stack, SlotReference reference) {
        return true;
    }

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
                .append(Text.translatable("item.finery.tooltip.head").formatted(Formatting.GRAY)));
        tooltip.add(Text.translatable("item.finery.tooltip.ability")
                .formatted(Formatting.GOLD, Formatting.BOLD)
                .append(Text.translatable("item.finery." + variant + ".ability")
                        .formatted(Formatting.GOLD, Formatting.ITALIC)));
        for (String line : Text.translatable("item.finery." + variant + ".desc")
                .getString().split("\n", -1)) {
            tooltip.add(Text.literal(line));
        }
        if (hintKey != null) {
            tooltip.add(Text.translatable("item.finery.tooltip.obtain").formatted(Formatting.DARK_GRAY)
                    .append(Text.translatable(hintKey).formatted(Formatting.DARK_GRAY)));
        }
        addExtraTooltip(stack, tooltip);
    }

    /** Extra lines for subclasses (dyable pieces add their current colour). */
    protected void addExtraTooltip(ItemStack stack, List<Text> tooltip) {
    }
}


