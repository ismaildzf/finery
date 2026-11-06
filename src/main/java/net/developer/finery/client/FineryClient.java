package net.developer.finery.client;

import com.mojang.blaze3d.platform.InputConstants;
import net.developer.finery.Finery;
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
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.PauseScreen;
import net.minecraft.network.chat.Component;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RegisterKeyMappingsEvent;
import net.minecraftforge.client.event.ScreenEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;
import org.lwjgl.glfw.GLFW;
import top.theillusivec4.curios.api.client.CuriosRendererRegistry;

@Mod.EventBusSubscriber(modid = Finery.MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
public final class FineryClient {
    public static final KeyMapping ADJUST_KEY = new KeyMapping(
            "key.finery.adjust", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_K, "key.categories.finery");

    private FineryClient() {
    }

    @SubscribeEvent
    public static void clientSetup(FMLClientSetupEvent event) {
        event.enqueueWork(() -> {
            for (CapeItem item : ModItems.ALL) {
                CuriosRendererRegistry.register(item, CapeAccessoryRenderer::new);
            }
            for (HeadItem item : ModItems.HEADS) {
                CuriosRendererRegistry.register(item, HeadAccessoryRenderer::new);
            }
            for (NeckItem item : ModItems.NECKS) {
                CuriosRendererRegistry.register(item, NeckAccessoryRenderer::new);
            }
            for (WingItem item : ModItems.WINGS) {
                CuriosRendererRegistry.register(item, WingAccessoryRenderer::new);
            }
            Finery.LOGGER.info("[Finery] Registered 35 Curios renderers");
        });
    }

    @SubscribeEvent
    public static void registerKeys(RegisterKeyMappingsEvent event) {
        event.register(ADJUST_KEY);
    }

    @Mod.EventBusSubscriber(modid = Finery.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE, value = Dist.CLIENT)
    static final class ForgeEvents {
        private ForgeEvents() {
        }

        @SubscribeEvent
        static void clientTick(TickEvent.ClientTickEvent event) {
            if (event.phase != TickEvent.Phase.END) {
                return;
            }
            Minecraft client = Minecraft.getInstance();
            if (client.level == null) {
                return;
            }
            CapeWaveManager.tick(client);
            while (ADJUST_KEY.consumeClick()) {
                if (client.player != null) {
                    client.setScreen(new CosmeticAdjustScreen(null));
                }
            }
        }

        @SubscribeEvent
        static void screenInit(ScreenEvent.Init.Post event) {
            if (event.getScreen() instanceof PauseScreen) {
                int lowest = event.getScreen().height / 4 + 96;
                for (net.minecraft.client.gui.components.events.GuiEventListener listener : event.getListenersList()) {
                    if (listener instanceof Button button) {
                        lowest = Math.max(lowest, button.getY() + button.getHeight());
                    }
                }
                int x = event.getScreen().width / 2 - 100;
                int y = Math.min(lowest + 4, event.getScreen().height - 24);
                event.addListener(Button.builder(Component.translatable("finery.menu.adjust"),
                                button -> Minecraft.getInstance().setScreen(new CosmeticAdjustScreen(event.getScreen())))
                        .bounds(x, y, 200, 20)
                        .build());
            }
        }
    }
}
