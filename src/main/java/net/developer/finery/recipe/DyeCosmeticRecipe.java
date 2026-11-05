package net.developer.finery.recipe;

import net.developer.finery.item.CosmeticDye;
import net.developer.finery.item.DyeableHeadItem;
import net.developer.finery.item.DyeableNeckItem;
import net.minecraft.item.DyeItem;
import net.minecraft.item.ItemStack;
import net.minecraft.recipe.RecipeSerializer;
import net.minecraft.recipe.SpecialCraftingRecipe;
import net.minecraft.recipe.book.CraftingRecipeCategory;
import net.minecraft.world.World;

import java.util.List;

//? if <1.20.5 {
/*import com.google.gson.JsonObject;
import net.minecraft.inventory.RecipeInputInventory;
import net.minecraft.network.PacketByteBuf;
import net.minecraft.registry.DynamicRegistryManager;
import net.minecraft.util.Identifier;
*///?} else {
import com.mojang.serialization.MapCodec;
import net.minecraft.network.RegistryByteBuf;
import net.minecraft.network.codec.PacketCodec;
import net.minecraft.recipe.input.CraftingRecipeInput;
import net.minecraft.registry.RegistryWrapper;
//?}

/**
 * One dyeable cosmetic + one dye, in any slots, produces the same piece in that colour.
 * Implemented as a special recipe so the colour can live on the stack.
 */
//? if <1.20.5 {
/*public class DyeCosmeticRecipe extends SpecialCraftingRecipe {

    public DyeCosmeticRecipe(Identifier id, CraftingRecipeCategory category) {
        super(id, category);
    }

    @Override
    public boolean matches(RecipeInputInventory input, World world) {
        return find(input.getInputStacks()) != null;
    }

    @Override
    public ItemStack craft(RecipeInputInventory input, DynamicRegistryManager manager) {
        return result(input.getInputStacks());
    }

    @Override
    public boolean fits(int width, int height) {
        return width * height >= 2;
    }

    @Override
    public RecipeSerializer<?> getSerializer() {
        return SERIALIZER;
    }

    private static Match find(List<ItemStack> stacks) {
        ItemStack cosmetic = ItemStack.EMPTY;
        int dye = -1;
        for (ItemStack stack : stacks) {
            if (stack.isEmpty()) {
                continue;
            }
            if (stack.getItem() instanceof DyeItem dyeItem) {
                if (dye >= 0) {
                    return null;
                }
                dye = dyeItem.getColor().ordinal();
            } else if (stack.getItem() instanceof DyeableHeadItem || stack.getItem() instanceof DyeableNeckItem) {
                if (!cosmetic.isEmpty()) {
                    return null;
                }
                cosmetic = stack;
            } else {
                return null;
            }
        }
        if (cosmetic.isEmpty() || dye < 0) {
            return null;
        }
        return new Match(cosmetic, dye);
    }

    private static ItemStack result(List<ItemStack> stacks) {
        Match match = find(stacks);
        if (match == null) {
            return ItemStack.EMPTY;
        }
        ItemStack out = match.cosmetic.copy();
        out.setCount(1);
        CosmeticDye.set(out, match.dye);
        return out;
    }

    private record Match(ItemStack cosmetic, int dye) {
    }

    public static final RecipeSerializer<DyeCosmeticRecipe> SERIALIZER = new RecipeSerializer<>() {
        @Override
        public DyeCosmeticRecipe read(Identifier id, JsonObject json) {
            return new DyeCosmeticRecipe(id, CraftingRecipeCategory.EQUIPMENT);
        }

        @Override
        public DyeCosmeticRecipe read(Identifier id, PacketByteBuf buf) {
            return new DyeCosmeticRecipe(id, CraftingRecipeCategory.EQUIPMENT);
        }

        @Override
        public void write(PacketByteBuf buf, DyeCosmeticRecipe recipe) {
        }
    };
}
*///?} else {
public class DyeCosmeticRecipe extends SpecialCraftingRecipe {

    public DyeCosmeticRecipe(CraftingRecipeCategory category) {
        super(category);
    }

    @Override
    public boolean matches(CraftingRecipeInput input, World world) {
        return find(input.getStacks()) != null;
    }

    @Override
    public ItemStack craft(CraftingRecipeInput input, RegistryWrapper.WrapperLookup lookup) {
        return result(input.getStacks());
    }

    //? if <1.21.3 {
    /*@Override
    public boolean fits(int width, int height) {
        return width * height >= 2;
    }
    *///?}

    @Override
    public RecipeSerializer<? extends SpecialCraftingRecipe> getSerializer() {
        return SERIALIZER;
    }

    private static Match find(List<ItemStack> stacks) {
        ItemStack cosmetic = ItemStack.EMPTY;
        int dye = -1;
        for (ItemStack stack : stacks) {
            if (stack.isEmpty()) {
                continue;
            }
            if (stack.getItem() instanceof DyeItem dyeItem) {
                if (dye >= 0) {
                    return null;
                }
                dye = dyeItem.getColor().ordinal();
            } else if (stack.getItem() instanceof DyeableHeadItem || stack.getItem() instanceof DyeableNeckItem) {
                if (!cosmetic.isEmpty()) {
                    return null;
                }
                cosmetic = stack;
            } else {
                return null;
            }
        }
        if (cosmetic.isEmpty() || dye < 0) {
            return null;
        }
        return new Match(cosmetic, dye);
    }

    private static ItemStack result(List<ItemStack> stacks) {
        Match match = find(stacks);
        if (match == null) {
            return ItemStack.EMPTY;
        }
        ItemStack out = match.cosmetic.copy();
        out.setCount(1);
        CosmeticDye.set(out, match.dye);
        return out;
    }

    private record Match(ItemStack cosmetic, int dye) {
    }

    private static final DyeCosmeticRecipe PROTOTYPE =
            new DyeCosmeticRecipe(CraftingRecipeCategory.EQUIPMENT);

    public static final RecipeSerializer<DyeCosmeticRecipe> SERIALIZER = new RecipeSerializer<>() {
        private final MapCodec<DyeCosmeticRecipe> mapCodec = MapCodec.unit(PROTOTYPE);
        private final PacketCodec<RegistryByteBuf, DyeCosmeticRecipe> packetCodec =
                PacketCodec.ofStatic((buf, recipe) -> { }, buf -> PROTOTYPE);

        @Override
        public MapCodec<DyeCosmeticRecipe> codec() {
            return mapCodec;
        }

        @Override
        public PacketCodec<RegistryByteBuf, DyeCosmeticRecipe> packetCodec() {
            return packetCodec;
        }
    };
}
//?}
