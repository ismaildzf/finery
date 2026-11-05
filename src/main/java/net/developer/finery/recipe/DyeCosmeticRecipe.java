package net.developer.finery.recipe;

import com.google.gson.JsonObject;
import net.developer.finery.item.CosmeticDye;
import net.developer.finery.item.DyeableHeadItem;
import net.developer.finery.item.DyeableNeckItem;
import net.minecraft.core.NonNullList;
import net.minecraft.core.RegistryAccess;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.inventory.CraftingContainer;
import net.minecraft.world.item.DyeItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.CraftingBookCategory;
import net.minecraft.world.item.crafting.CustomRecipe;
import net.minecraft.world.item.crafting.RecipeSerializer;
import net.minecraft.world.level.Level;

import java.util.List;

/** One dyeable cosmetic + one dye, in any slots, produces the same piece in that colour. */
public class DyeCosmeticRecipe extends CustomRecipe {
    public DyeCosmeticRecipe(ResourceLocation id, CraftingBookCategory category) {
        super(id, category);
    }

    @Override
    public boolean matches(CraftingContainer input, Level level) {
        return find(input.getItems()) != null;
    }

    @Override
    public ItemStack assemble(CraftingContainer input, RegistryAccess registries) {
        return result(input.getItems());
    }

    @Override
    public boolean canCraftInDimensions(int width, int height) {
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
                dye = dyeItem.getDyeColor().ordinal();
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
        public DyeCosmeticRecipe fromJson(ResourceLocation id, JsonObject json) {
            return new DyeCosmeticRecipe(id, CraftingBookCategory.EQUIPMENT);
        }

        @Override
        public DyeCosmeticRecipe fromNetwork(ResourceLocation id, FriendlyByteBuf buf) {
            return new DyeCosmeticRecipe(id, CraftingBookCategory.EQUIPMENT);
        }

        @Override
        public void toNetwork(FriendlyByteBuf buf, DyeCosmeticRecipe recipe) {
        }
    };
}
