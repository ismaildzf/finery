package net.developer.finery.item;

import net.minecraft.util.Mth;

import net.developer.finery.provider.ProviderRegistry;
import net.developer.finery.provider.SlotKind;
import top.theillusivec4.curios.api.SlotContext;
import top.theillusivec4.curios.api.type.capability.ICurioItem;

import net.minecraft.world.item.DyeItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.nbt.Tag;
import net.minecraft.nbt.IntTag;
import net.minecraft.network.chat.Component;

//? if <1.20.5 {
import net.minecraft.nbt.CompoundTag;
//?} else {
/*import net.minecraft.component.DataComponentTypes;
import net.minecraft.component.type.NbtComponent;
import net.minecraft.nbt.CompoundTag;
*///?}

/**
 * Per-stack dye colour for dyable cosmetics, stored as a vanilla dye id.
 * 1.20.1 still uses raw NBT; every later target stores it in CUSTOM_DATA.
 */
public final class CosmeticDye {

    /** Dye ids in {@link net.minecraft.world.item.DyeColor} ordinal order. */
    public static final String[] NAMES = {
            "white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray",
            "light_gray", "cyan", "purple", "blue", "brown", "green", "red", "black"
    };

    public static final int DEFAULT = 15;
    private static final String KEY = "finery_dye";

    private CosmeticDye() {
    }

    public static int get(ItemStack stack) {
        return get(stack, DEFAULT);
    }

    public static int get(ItemStack stack, int fallback) {
        //? if <1.20.5 {
        return read(stack.getTag(), fallback);
        //?} else {
        /*NbtComponent data = stack.get(DataComponentTypes.CUSTOM_DATA);
        return data == null ? fallback : read(data.copyNbt(), fallback);
        *///?}
    }

    public static void set(ItemStack stack, int dye) {
        //? if <1.20.5 {
        stack.getOrCreateTag().putInt(KEY, dye);
        //?} else {
        /*NbtComponent existing = stack.get(DataComponentTypes.CUSTOM_DATA);
        NbtCompound nbt = existing == null ? new NbtCompound() : existing.copyNbt();
        nbt.putInt(KEY, dye);
        stack.set(DataComponentTypes.CUSTOM_DATA, NbtComponent.of(nbt));
        *///?}
    }

    public static int fromDye(ItemStack stack) {
        return stack.getItem() instanceof DyeItem dye ? dye.getDyeColor().ordinal() : -1;
    }

    public static String suffix(int dye) {
        return NAMES[Math.max(0, Math.min(NAMES.length - 1, dye))];
    }

    public static Component colorName(int dye) {
        return Component.translatable("color.minecraft." + suffix(dye));
    }


    /** Vanilla dye RGB, indexed like {@link #NAMES}. */
    private static final int[] RGB = {
            0xF9FFFE, 0xF9801D, 0xC74EBD, 0x3AB3DA, 0xFED83D, 0x80C71F, 0xF38BAA, 0x474F52,
            0x9D9D97, 0x169C9C, 0x8932B8, 0x3C44AA, 0x835432, 0x5E7C16, 0xB02E26, 0x1D1D21
    };

    public static int rgb(int dye) {
        return RGB[Math.max(0, Math.min(RGB.length - 1, dye))];
    }

    private static int read(CompoundTag nbt, int fallback) {
        if (nbt == null) {
            return fallback;
        }
        Tag tag = nbt.get(KEY);
        return tag instanceof IntTag value ? value.getAsInt() : fallback;
    }
}
