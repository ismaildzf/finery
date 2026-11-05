package net.developer.finery;

import com.mojang.brigadier.arguments.StringArgumentType;
import io.wispforest.accessories.api.AccessoriesCapability;
//? if >=1.21.11 {
import net.minecraft.command.permission.LeveledPermissionPredicate;
import net.minecraft.command.permission.PermissionLevel;
//?}
import net.developer.finery.registry.ModItems;
import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;
import net.minecraft.item.ItemStack;
import net.minecraft.server.command.CommandManager;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.text.Text;

import java.util.List;

/**
 * Development helper: equips a cosmetic straight into its Accessories slot so
 * wings/capes can be inspected without juggling the inventory GUI.
 *
 * <p>Usage: {@code /epiccosmetic <variant>} (op level 0 in single-player).</p>
 */
public final class DevCommands {

    private DevCommands() {
    }

    public static void register() {
        CommandRegistrationCallback.EVENT.register((dispatcher, registryAccess, environment) ->
                dispatcher.register(CommandManager.literal("epiccosmetic")
                        //? if >=1.21.11 {
                        .requires(source -> source.getPermissions() instanceof LeveledPermissionPredicate leveled
                                && leveled.getLevel().isAtLeast(PermissionLevel.fromLevel(2)))
                        //?} else {
                        /*.requires(source -> source.hasPermissionLevel(2))
                        *///?}
                        .then(CommandManager.argument("variant", StringArgumentType.word())
                                .suggests((context, builder) -> {
                                    for (var item : ModItems.WINGS) {
                                        builder.suggest(item.getVariant());
                                    }
                                    return builder.buildFuture();
                                })
                                .executes(context -> {
                                    ServerPlayerEntity player = context.getSource().getPlayerOrThrow();
                                    String variant = StringArgumentType.getString(context, "variant");
                                    if (!equip(player, variant)) {
                                        context.getSource().sendError(Text.literal("Unknown cosmetic: " + variant));
                                        return 0;
                                    }
                                    var equipped = AccessoriesCapability.get(player)
                                            .getEquipped(find(variant));
                                    context.getSource().sendFeedback(
                                            () -> Text.literal("Equipped " + variant
                                                    + " (slots=" + equipped.size() + ")"), false);
                                    return 1;
                                }))));
    }

    /** Equips one wing variant into the back slot, clearing whatever was there. */
    public static boolean equip(ServerPlayerEntity player, String variant) {
        List<String> known = ModItems.WINGS.stream().map(item -> item.getVariant()).toList();
        if (!known.contains(variant)) {
            return false;
        }
        AccessoriesCapability capability = AccessoriesCapability.get(player);
        // wings and capes are exclusive, so a test equip clears both slots
        for (String slot : new String[]{"back", "cape"}) {
            var container = capability.getContainers().get(slot);
            if (container != null) {
                for (int i = 0; i < container.getSize(); i++) {
                    container.getAccessories().setStack(i, ItemStack.EMPTY);
                }
            }
        }
        capability.equipAccessory(new ItemStack(find(variant)));
        return true;
    }

    private static net.minecraft.item.Item find(String variant) {
        for (var item : ModItems.WINGS) {
            if (item.getVariant().equals(variant)) {
                return item;
            }
        }
        return ModItems.ANGEL_WINGS;
    }
}
