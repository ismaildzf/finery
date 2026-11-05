package net.developer.finery;

import com.mojang.brigadier.CommandDispatcher;
import net.developer.finery.registry.ModItems;
import net.minecraft.commands.Commands;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import top.theillusivec4.curios.api.CuriosApi;

@Mod.EventBusSubscriber(modid = Finery.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class TestCommands {
    private TestCommands() {
    }

    @SubscribeEvent
    public static void register(RegisterCommandsEvent event) {
        CommandDispatcher<?> dispatcher = event.getDispatcher();
        event.getDispatcher().register(Commands.literal("finerytest")
                .then(Commands.literal("equip").executes(ctx -> {
                    ServerPlayer player = ctx.getSource().getPlayerOrException();
                    CuriosApi.getCuriosInventory(player).ifPresent(handler -> {
                        handler.getCurios().keySet().forEach(slot ->
                                Finery.LOGGER.info("[Finery] slot available: {}", slot));
                        handler.setEquippedCurio("necklace", 0, new ItemStack(ModItems.AZURE_CAPE));
                    });
                    return 1;
                })));
    }
}
