package net.developer.finery;

import com.mojang.brigadier.arguments.StringArgumentType;
import net.developer.finery.item.CapeItem;
import net.developer.finery.item.HeadItem;
import net.developer.finery.item.NeckItem;
import net.developer.finery.item.WingItem;
import net.developer.finery.provider.ProviderRegistry;
import net.developer.finery.provider.SlotKind;
import net.developer.finery.registry.ModItems;
import net.minecraft.commands.Commands;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.fml.common.Mod;
import top.theillusivec4.curios.api.CuriosApi;
import top.theillusivec4.curios.api.type.capability.ICuriosItemHandler;

/** Admin helper: /finery equip &lt;variant&gt; gives and wears one cosmetic. */
@EventBusSubscriber(modid = Finery.MOD_ID)
public final class FineryCommands {
    private FineryCommands() {
    }

    @SubscribeEvent
    public static void register(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("finery")
                .requires(source -> source.hasPermission(2))
                .then(Commands.literal("equip")
                        .then(Commands.argument("variant", StringArgumentType.word())
                                .executes(ctx -> {
                                    ServerPlayer player = ctx.getSource().getPlayerOrException();
                                    String variant = StringArgumentType.getString(ctx, "variant");
                                    Item item = find(variant);
                                    if (item == null) {
                                        Finery.LOGGER.warn("[Finery] unknown cosmetic {}", variant);
                                        return 0;
                                    }
                                    ItemStack stack = new ItemStack(item);
                                    player.getInventory().add(stack.copy());
                                    String slot = slotFor(item);
                                    CuriosApi.getCuriosInventory(player).ifPresent(handler ->
                                            handler.getStacksHandler(slot).ifPresent(stacks ->
                                                    stacks.getStacks().setStackInSlot(0, stack)));
                                    return 1;
                                }))));
    }

    private static String slotFor(Item item) {
        if (item instanceof CapeItem) {
            return ProviderRegistry.slotName(SlotKind.CAPE);
        }
        if (item instanceof WingItem) {
            return ProviderRegistry.slotName(SlotKind.WINGS);
        }
        if (item instanceof HeadItem head) {
            return ProviderRegistry.slotName("face".equals(head.getSlotName()) ? SlotKind.FACE : SlotKind.HAT);
        }
        return ProviderRegistry.slotName(SlotKind.NECKLACE);
    }

    private static Item find(String variant) {
        for (CapeItem item : ModItems.ALL) {
            if (item.getCapeVariant().equals(variant)) {
                return item;
            }
        }
        for (HeadItem item : ModItems.HEADS) {
            if (item.get().equals(variant)) {
                return item;
            }
        }
        for (NeckItem item : ModItems.NECKS) {
            if (item.get().equals(variant)) {
                return item;
            }
        }
        for (WingItem item : ModItems.WINGS) {
            if (item.get().equals(variant)) {
                return item;
            }
        }
        return null;
    }
}
