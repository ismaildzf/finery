package net.developer.finery.client;

import io.wispforest.accessories.api.client.AccessoriesRendererRegistry;
import net.developer.finery.client.renderer.CapeAccessoryRenderer;
import net.developer.finery.client.renderer.head.HeadAccessoryRenderer;
import net.developer.finery.client.renderer.neck.NeckAccessoryRenderer;
import net.developer.finery.client.renderer.wave.CapeWaveManager;
import net.developer.finery.client.renderer.wing.WingAccessoryRenderer;
import net.developer.finery.item.CapeItem;
import net.developer.finery.item.HeadItem;
import net.developer.finery.item.NeckItem;
import net.developer.finery.item.WingItem;
import net.developer.finery.registry.ModItems;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.api.EnvType;
import net.fabricmc.api.Environment;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.fabricmc.fabric.api.client.keybinding.v1.KeyBindingHelper;
import net.fabricmc.fabric.api.client.screen.v1.ScreenEvents;
import net.fabricmc.fabric.api.client.screen.v1.Screens;
import net.minecraft.client.MinecraftClient;
import net.minecraft.client.gui.screen.GameMenuScreen;
import net.minecraft.client.gui.screen.Screen;
import net.minecraft.client.gui.widget.ButtonWidget;
import net.minecraft.client.gui.widget.ClickableWidget;
import net.minecraft.client.option.KeyBinding;
import net.minecraft.client.util.InputUtil;
import net.minecraft.text.Text;
//? if >=1.21.10 {
import net.minecraft.util.Identifier;
//?}
import org.lwjgl.glfw.GLFW;

/**
 * Client-side initializer for Finery.
 *
 * Registers an accessory renderer for every cape/head item so the Accessories
 * API draws them on the player when equipped, ticks the cloth simulation, and
 * wires up the head-cosmetic adjustment entry points: the K key and an
 * "Adjust Cosmetics..." button in the pause menu.
 */
@Environment(EnvType.CLIENT)
public class FineryClient implements ClientModInitializer {

    @Override
    public void onInitializeClient() {
        for (CapeItem cape : ModItems.ALL) {
            AccessoriesRendererRegistry.registerRenderer(cape, CapeAccessoryRenderer::new);
        }
        for (HeadItem head : ModItems.HEADS) {
            AccessoriesRendererRegistry.registerRenderer(head, HeadAccessoryRenderer::new);
        }
        for (NeckItem neck : ModItems.NECKS) {
            AccessoriesRendererRegistry.registerRenderer(neck, NeckAccessoryRenderer::new);
        }
        for (WingItem wing : ModItems.WINGS) {
            AccessoriesRendererRegistry.registerRenderer(wing, WingAccessoryRenderer::new);
        }
        ClientTickEvents.END_CLIENT_TICK.register(CapeWaveManager::tick);

        KeyBinding adjustKey = KeyBindingHelper.registerKeyBinding(new KeyBinding(
                "key.finery.adjust",
                InputUtil.Type.KEYSYM,
                GLFW.GLFW_KEY_K,
                //? if >=1.21.10 {
                KeyBinding.Category.create(Identifier.of("finery", "finery"))
                //?} else {
                /*"key.categories.finery"
                *///?}
        ));
        ClientTickEvents.END_CLIENT_TICK.register(client -> {
            while (adjustKey.wasPressed()) {
                if (client.player != null) {
                    client.setScreen(new CosmeticAdjustScreen(null));
                }
            }
        });

        ScreenEvents.AFTER_INIT.register((client, screen, scaledWidth, scaledHeight) -> {
            if (screen instanceof GameMenuScreen) {
                addAdjustButton(client, screen);
            }
        });

    }

    /** Adds the adjust-screen button right under the save/quit button. */
    private static void addAdjustButton(MinecraftClient client, Screen screen) {
        Text quitLabel = Text.translatable("menu.returnToMenu");
        Text disconnectLabel = Text.translatable("menu.disconnect");
        ButtonWidget anchor = null;
        for (ClickableWidget widget : Screens.getButtons(screen)) {
            if (widget instanceof ButtonWidget button
                    && (button.getMessage().equals(quitLabel) || button.getMessage().equals(disconnectLabel))) {
                anchor = button;
                break;
            }
        }
        if (anchor == null) {
            return;
        }
        Screens.getButtons(screen).add(ButtonWidget.builder(Text.translatable("finery.menu.adjust"),
                        b -> client.setScreen(new CosmeticAdjustScreen(screen)))
                .dimensions(anchor.getX(), anchor.getY() + 24, anchor.getWidth(), 20)
                .build());
    }
}
