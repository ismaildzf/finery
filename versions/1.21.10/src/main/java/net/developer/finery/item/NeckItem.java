package net.developer.finery.item;

import net.developer.finery.provider.ProviderRegistry;
import net.developer.finery.provider.SlotKind;
import top.theillusivec4.curios.api.SlotContext;
import top.theillusivec4.curios.api.type.capability.ICurioItem;

//? if >=1.21.10 {
/*import io.wispforest.accessories.api.core.AccessoryItem;
*///?} else {
//?}
import net.developer.finery.Finery;
import net.developer.finery.ability.NeckAbility;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
//? if <1.20.5 {
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.level.Level;
//?} else {
/*import net.minecraft.item.tooltip.TooltipType;
*///?}
//? if >=1.21.5 {
/*import net.minecraft.component.type.TooltipDisplayComponent;
import java.util.ArrayList;
import java.util.function.Consumer;
*///?}
import java.util.ArrayList;
import java.util.function.Consumer;
import net.minecraft.network.chat.Component;
import net.minecraft.ChatFormatting;
import net.minecraft.resources.ResourceLocation;

import java.util.List;

/**
 * Neckwear (scarves, amulets, torcs).
 *
 * Bound to the Accessories "necklace" slot via
 * data/accessories/tags/item/necklace.json and rendered by the client's
 * NeckAccessoryRenderer via {@link #getNeckTexture()}.
 */
public class NeckItem extends Item implements ICurioItem {

    private final String variant;
    private final NeckAbility ability;
    private final CapeRarity rarity;
    private final String hintKey;

    private ResourceLocation neckTexture;

    public NeckItem(Properties settings, String variant, NeckAbility ability,
                    CapeRarity rarity, String hintKey) {
        super(settings);
        this.variant = variant;
        this.ability = ability;
        this.rarity = rarity;
        this.hintKey = hintKey;
    }

    public String get() {
        return variant;
    }

    /** Texture path: assets/finery/textures/neck/{variant}.png */
    public ResourceLocation getNeckTexture() {
        if (neckTexture == null) {
            neckTexture = ResourceLocation.fromNamespaceAndPath(Finery.MOD_ID, "textures/neck/" + variant + ".png");
        }
        return neckTexture;
    }

    /** Overridden by dyable pieces, which pick a tinted sheet per stack. */
    public ResourceLocation getNeckTexture(ItemStack stack) {
        return getNeckTexture();
    }

    public CapeRarity getRarity() {
        return rarity;
    }

    @Override
    public void onEquip(SlotContext reference, ItemStack stack, ItemStack previous) {
        if (reference.entity() != null) {
            ability.onEquip(reference.entity());
        }
    }

    @Override
    public void onUnequip(SlotContext reference, ItemStack stack, ItemStack previous) {
        if (reference.entity() != null) {
            ability.onUnequip(reference.entity());
        }
    }

    @Override
    public void curioTick(SlotContext reference, ItemStack stack) {
        if (reference.entity() != null) {
            ability.tick(reference.entity());
        }
    }

    @Override
    public boolean canEquip(SlotContext reference, ItemStack stack) {
        return "necklace".equals(reference.identifier());
    }

    @Override
    public boolean canUnequip(SlotContext reference, ItemStack stack) {
        return true;
    }

    @Override
    public Component getName(ItemStack stack) {
        return super.getName(stack).copy().withStyle(rarity.color());
    }

    @Override
    public void appendHoverText(ItemStack stack, Item.TooltipContext context, TooltipDisplay display,
                                Consumer<Component> consumer, TooltipFlag flag) {
        List<Component> lines = new ArrayList<>();
        addTooltip(stack, lines);
        lines.forEach(consumer);
    }

    private void addTooltip(ItemStack stack, List<Component> tooltip) {
        tooltip.add(Component.translatable(rarity.tooltipKey())
                .withStyle(rarity.color(), ChatFormatting.BOLD)
                .append(Component.literal(" • ").withStyle(ChatFormatting.DARK_GRAY))
                .append(Component.translatable("item.finery.tooltip.neck").withStyle(ChatFormatting.GRAY)));
        tooltip.add(Component.translatable("item.finery.tooltip.ability")
                .withStyle(ChatFormatting.GOLD, ChatFormatting.BOLD)
                .append(Component.translatable("item.finery." + variant + ".ability")
                        .withStyle(ChatFormatting.GOLD, ChatFormatting.ITALIC)));
        for (String line : Component.translatable("item.finery." + variant + ".desc")
                .getString().split("\n", -1)) {
            tooltip.add(Component.literal(line));
        }
        if (hintKey != null) {
            tooltip.add(Component.translatable("item.finery.tooltip.obtain").withStyle(ChatFormatting.DARK_GRAY)
                    .append(Component.translatable(hintKey).withStyle(ChatFormatting.DARK_GRAY)));
        }
        addExtraTooltip(stack, tooltip);
    }

    /** Extra lines for subclasses (dyable pieces add their current colour). */
    protected void addExtraTooltip(ItemStack stack, List<Component> tooltip) {
    }
}
