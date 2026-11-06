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
import net.developer.finery.ability.HeadAbility;
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
import net.minecraft.resources.Identifier;

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
public class HeadItem extends Item implements ICurioItem {

    private final String variant;
    private final String slotName;
    private final HeadAbility ability;
    private final CapeRarity rarity;
    private final String hintKey;

    private Identifier headTexture;

    public HeadItem(Properties settings, String variant, String slotName,
                    HeadAbility ability, CapeRarity rarity, String hintKey) {
        super(settings);
        this.variant = variant;
        this.slotName = slotName;
        this.ability = ability;
        this.rarity = rarity;
        this.hintKey = hintKey;
    }

    public String get() {
        return variant;
    }

    public String getSlotName() {
        return slotName;
    }

    /** Texture path: assets/finery/textures/head/{variant}.png */
    public Identifier getHeadTexture() {
        if (headTexture == null) {
            headTexture = Identifier.fromNamespaceAndPath(Finery.MOD_ID, "textures/head/" + variant + ".png");
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
        String expected = ProviderRegistry.slotName("face".equals(slotName) ? SlotKind.FACE : SlotKind.HAT);
        return expected.equals(reference.identifier());
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
                .append(Component.translatable("item.finery.tooltip.head").withStyle(ChatFormatting.GRAY)));
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
