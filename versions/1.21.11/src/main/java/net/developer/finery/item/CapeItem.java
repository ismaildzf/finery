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
import net.developer.finery.ability.CapeAbility;
import net.developer.finery.registry.ModItems;
import net.minecraft.world.entity.LivingEntity;
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
public class CapeItem extends Item implements ICurioItem {

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

    public CapeItem(Properties settings, String variant, CapeAbility ability, CapeRarity rarity, String hintKey) {
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
            capeTexture = Identifier.fromNamespaceAndPath(Finery.MOD_ID, "textures/cape/" + capeVariant + ".png");
        }
        return capeTexture;
    }

    // ── Accessory Interface Implementation ──────────────────────────────

    @Override
    public void onEquip(SlotContext reference, ItemStack stack, ItemStack previous) {
        // Called when the cape is placed into the accessory slot
    }

    @Override
    public void onUnequip(SlotContext reference, ItemStack stack, ItemStack previous) {
        // Called when the cape is removed from the accessory slot
    }

    @Override
    public void curioTick(SlotContext reference, ItemStack stack) {
        if (reference.entity() != null) {
            ability.tick(reference.entity());
        }
    }

    @Override
    public boolean canEquip(SlotContext reference, ItemStack stack) {
        if (!reference.identifier().equals(ProviderRegistry.slotName(SlotKind.CAPE))) {
            return false;
        }
        LivingEntity entity = reference.entity();
        if (entity == null) {
            return true;
        }
        return !ProviderRegistry.isWornAny(entity, ModItems.WINGS);
    }

    @Override
    public boolean canUnequip(SlotContext reference, ItemStack stack) {
        return true;
    }

    // ── Display ─────────────────────────────────────────────────────────

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
                .append(Component.translatable("item.finery.tooltip.cape").withStyle(ChatFormatting.GRAY)));
        tooltip.add(Component.translatable("item.finery.tooltip.ability")
                .withStyle(ChatFormatting.GOLD, ChatFormatting.BOLD)
                .append(Component.translatable("item.finery." + capeVariant + "_cape.ability")
                        .withStyle(ChatFormatting.GOLD, ChatFormatting.ITALIC)));
        for (String line : Component.translatable("item.finery." + capeVariant + "_cape.desc")
                .getString().split("\n", -1)) {
            tooltip.add(Component.literal(line));
        }
        if (hintKey != null) {
            tooltip.add(Component.translatable("item.finery.tooltip.obtain").withStyle(ChatFormatting.DARK_GRAY)
                    .append(Component.translatable(hintKey).withStyle(ChatFormatting.DARK_GRAY)));
        }
        tooltip.add(Component.translatable("item.finery.cape.exclusive")
                .withStyle(ChatFormatting.DARK_GRAY, ChatFormatting.ITALIC));
    }
}
