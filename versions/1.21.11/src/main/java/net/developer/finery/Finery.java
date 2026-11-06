package net.developer.finery;

import net.developer.finery.recipe.DyeCosmeticRecipe;
import net.developer.finery.registry.ModItems;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.crafting.RecipeSerializer;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.event.lifecycle.FMLCommonSetupEvent;
import net.neoforged.neoforge.registries.DeferredRegister;
import net.minecraft.core.registries.BuiltInRegistries;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import top.theillusivec4.curios.api.CuriosApi;
import top.theillusivec4.curios.api.type.capability.ICurioItem;

@Mod(Finery.MOD_ID)
public class Finery {
    public static final String MOD_ID = "finery";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);
    public static final DeferredRegister<RecipeSerializer<?>> RECIPES =
            DeferredRegister.create(BuiltInRegistries.RECIPE_SERIALIZER, MOD_ID);

    public Finery(IEventBus modBus, ModContainer container) {
        ModItems.register(modBus);
        RECIPES.register(modBus);
        RECIPES.register("cosmetic_dyeing", () -> DyeCosmeticRecipe.SERIALIZER);
        modBus.addListener(this::commonSetup);
        LOGGER.info("[Finery] NeoForge 1.20.1 port constructed");
    }

    private void commonSetup(FMLCommonSetupEvent event) {
        event.enqueueWork(() -> {
            ModItems.bind();
            for (Item item : ModItems.ALL) CuriosApi.registerCurio(item, (ICurioItem) item);
            for (Item item : ModItems.HEADS) CuriosApi.registerCurio(item, (ICurioItem) item);
            for (Item item : ModItems.NECKS) CuriosApi.registerCurio(item, (ICurioItem) item);
            for (Item item : ModItems.WINGS) CuriosApi.registerCurio(item, (ICurioItem) item);
            LOGGER.info("[Finery] Registered 35 cosmetics with Curios");
        });
    }
}
