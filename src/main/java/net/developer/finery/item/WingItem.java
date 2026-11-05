package net.developer.finery.item;

import io.wispforest.accessories.api.AccessoriesCapability;
//? if >=1.21.10 {
import io.wispforest.accessories.api.core.AccessoryItem;
//?} else {
/*import io.wispforest.accessories.api.AccessoryItem;
*///?}
import io.wispforest.accessories.api.slot.SlotReference;
import net.developer.finery.Finery;
import net.developer.finery.ability.WingAbility;
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
 * Legendary wings, bound to the Accessories "back" slot. Wings and capes are
 * mutually exclusive by design: {@link #canEquip} refuses to equip a wing while
 * any cape is worn, and {@link CapeItem#canEquip} refuses a cape while any wing
 * is worn.
 */
public class WingItem extends AccessoryItem {

    private final String variant;
    private final WingAbility ability;
    private final CapeRarity rarity;
    private final String hintKey;

    private Identifier wingTexture;

    public WingItem(Settings settings, String variant, WingAbility ability,
                    CapeRarity rarity, String hintKey) {
        super(settings);
        this.variant = variant;
        this.ability = ability;
        this.rarity = rarity;
        this.hintKey = hintKey;
    }

    public String getVariant() {
        return variant;
    }

    public WingAbility getAbility() {
        return ability;
    }

    public WingStyle getStyle() {
        return ability.getStyle();
    }

    public CapeRarity getRarity() {
        return rarity;
    }

    /** Texture path: assets/finery/textures/wings/{variant}.png */
    public Identifier getWingTexture() {
        if (wingTexture == null) {
            wingTexture = Identifier.of(Finery.MOD_ID, "textures/wings/" + variant + ".png");
        }
        return wingTexture;
    }

    /** Model classpath: /assets/finery/wingmodels/{variant}.json */
    public String getWingModelPath() {
        return "/assets/" + Finery.MOD_ID + "/wingmodels/" + variant + ".json";
    }

    @Override
    public void tick(ItemStack stack, SlotReference reference) {
        if (reference.entity() != null) {
            ability.tick(reference.entity());
        }
    }

    @Override
    public boolean canEquip(ItemStack stack, SlotReference reference) {
        if (!"back".equals(reference.slotName())) {
            return false;
        }
        LivingEntity entity = reference.entity();
        if (entity == null) {
            return true;
        }
        return AccessoriesCapability.getOptionally(entity)
                .map(capability -> {
                    for (CapeItem cape : ModItems.ALL) {
                        if (!capability.getEquipped(cape).isEmpty()) {
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

    @Override
    public Text getName(ItemStack stack) {
        return super.getName(stack).copy().formatted(rarity.color());
    }

    @Override
    public boolean hasGlint(ItemStack stack) {
        return true;
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
                .append(Text.literal(" • ").formatted(Formatting.DARK_GRAY))
                .append(Text.translatable("item.finery.tooltip.wing").formatted(Formatting.GRAY)));
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
        tooltip.add(Text.translatable("item.finery.wing.exclusive")
                .formatted(Formatting.DARK_GRAY, Formatting.ITALIC));
    }
}
