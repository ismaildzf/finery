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
import net.developer.finery.ability.WingAbility;
import net.developer.finery.registry.ModItems;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
//? if <1.20.5 {
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
//?} else {
/*import net.minecraft.item.tooltip.TooltipType;
*///?}
//? if >=1.21.5 {
/*import net.minecraft.component.type.TooltipDisplayComponent;
import java.util.ArrayList;
import java.util.function.Consumer;
*///?}
import net.minecraft.network.chat.Component;
import net.minecraft.ChatFormatting;
import net.minecraft.resources.ResourceLocation;

import java.util.List;

/**
 * Legendary wings, bound to the Accessories "back" slot. Wings and capes are
 * mutually exclusive by design: {@link #canEquip} refuses to equip a wing while
 * any cape is worn, and {@link CapeItem#canEquip} refuses a cape while any wing
 * is worn.
 */
public class WingItem extends Item implements ICurioItem {

    private final String variant;
    private final WingAbility ability;
    private final CapeRarity rarity;
    private final String hintKey;

    private ResourceLocation wingTexture;

    public WingItem(Properties settings, String variant, WingAbility ability,
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

    public WingAbility getAbility() {
        return ability;
    }

    public WingStyle getOverlay() {
        return ability.getOverlay();
    }

    public CapeRarity getRarity() {
        return rarity;
    }

    /** Texture path: assets/finery/textures/wings/{variant}.png */
    public ResourceLocation getWingTexture() {
        if (wingTexture == null) {
            wingTexture = new ResourceLocation(Finery.MOD_ID, "textures/wings/" + variant + ".png");
        }
        return wingTexture;
    }

    /** Model classpath: /assets/finery/wingmodels/{variant}.json */
    public String getWingModelPath() {
        return "/assets/" + Finery.MOD_ID + "/wingmodels/" + variant + ".json";
    }

    @Override
    public void curioTick(SlotContext reference, ItemStack stack) {
        if (reference.entity() != null) {
            ability.tick(reference.entity());
        }
    }

    @Override
    public boolean canEquip(SlotContext reference, ItemStack stack) {
        if (!ProviderRegistry.slotName(SlotKind.WINGS).equals(reference.identifier())) {
            return false;
        }
        LivingEntity entity = reference.entity();
        if (entity == null) {
            return true;
        }
        return !ProviderRegistry.isWornAny(entity, ModItems.ALL);
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
    public boolean isFoil(ItemStack stack) {
        return true;
    }

    //? if <1.20.5 {
    @Override
    public void appendHoverText(ItemStack stack, Level world, List<Component> tooltip, TooltipFlag context) {
        addTooltip(stack, tooltip);
    }
    //?} elif >=1.20.5 && <1.21.5 {
    /*@Override
    public void appendHoverText(ItemStack stack, Item.TooltipContext context, List<Text> tooltip, TooltipType type) {
        addTooltip(stack, tooltip);
    }
    *///?} else {
    /*@Override
    public void appendHoverText(ItemStack stack, Item.TooltipContext context, TooltipDisplayComponent displayComponent,
                              Consumer<Text> textConsumer, TooltipType type) {
        List<Text> lines = new ArrayList<>();
        addTooltip(stack, lines);
        lines.forEach(textConsumer);
    }
    *///?}

    private void addTooltip(ItemStack stack, List<Component> tooltip) {
        tooltip.add(Component.translatable(rarity.tooltipKey())
                .withStyle(rarity.color(), ChatFormatting.BOLD)
                .append(Component.literal(" • ").withStyle(ChatFormatting.DARK_GRAY))
                .append(Component.translatable("item.finery.tooltip.wing").withStyle(ChatFormatting.GRAY)));
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
        tooltip.add(Component.translatable("item.finery.wing.exclusive")
                .withStyle(ChatFormatting.DARK_GRAY, ChatFormatting.ITALIC));
    }
}
