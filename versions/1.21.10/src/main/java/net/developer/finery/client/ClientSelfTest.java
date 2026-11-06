package net.developer.finery.client;

import net.developer.finery.Finery;
import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.screens.ConnectScreen;
import net.minecraft.client.multiplayer.ServerData;
import net.minecraft.client.multiplayer.resolver.ServerAddress;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.fml.common.Mod;
import top.theillusivec4.curios.api.CuriosApi;

/**
 * Visual smoke test, opt-in with -Dfinery.autotest=true.
 * The server cycles one item per cosmetic family every 140 ticks; this takes a
 * screenshot per phase plus one of the adjust screen.
 */
@EventBusSubscriber(modid = Finery.MOD_ID, value = Dist.CLIENT)
public final class ClientSelfTest {
    private static final String[] SHOTS = {
            "1-cape-set", "2-angel", "3-devil", "4-dragon", "5-butterfly", "6-hat-scarf", "7-horns-torc", "8-dyed"
    };

    private static int ticks;
    private static int shot;
    /** 1.21.9+ stores frames as deferred submit nodes, so the capture has to wait for a finished frame. */
    private static String pendingShot;
    private static boolean adjustShot;
    private static boolean sideShot;
    private static int retries;
    private static int retryDelay = 100;

    private ClientSelfTest() {
    }

    @SubscribeEvent
    public static void tick(ClientTickEvent.Post event) {
        if (System.getProperty("finery.autotest") == null) {
            return;
        }
        Minecraft client = Minecraft.getInstance();
        if (client.screen instanceof net.minecraft.client.gui.screens.PauseScreen) {
            client.setScreen(null);
        }
        if (client.player == null || client.level == null) {
            ticks = 0;
            if (client.screen instanceof net.minecraft.client.gui.screens.DisconnectedScreen && retries < 3) {
                if (--retryDelay <= 0) {
                    retries++;
                    retryDelay = 200;
                    Finery.LOGGER.info("[Autotest] reconnecting, attempt {}", retries + 1);
                    ConnectScreen.startConnecting(client.screen, client,
                            ServerAddress.parseString("127.0.0.1:25565"),
                            new ServerData("autotest", "127.0.0.1:25565", ServerData.Type.OTHER), false, null);
                }
            }
            return;
        }
        ticks++;
        if (ticks == 40) {
            client.options.setCameraType(CameraType.THIRD_PERSON_BACK);
        }
        if (shot < SHOTS.length && ticks == 100 + shot * 140) {
            Finery.LOGGER.info("[Autotest] phase shot {} worn={}", SHOTS[shot], worn(client));
            pendingShot = SHOTS[shot];
            shot++;
        }
        if (ticks == 1130 || ticks == 1160 || ticks == 1190 || ticks == 1220) {
            pendingShot = "M-motion-" + ticks;
        }
        if (ticks == 1240) {
            client.setScreen(new CosmeticAdjustScreen(null));
        }
        if (ticks == 1300 && !adjustShot) {
            adjustShot = true;
            Finery.LOGGER.info("[Autotest] adjust screen open={}", client.screen != null);
            pendingShot = "8-adjust-screen";
        }
        if (ticks == 1310) {
            client.setScreen(null);
        }
        if (ticks == 1320) {
            client.options.setCameraType(CameraType.THIRD_PERSON_FRONT);
        }
        if (ticks == 1340 && !sideShot) {
            sideShot = true;
            pendingShot = "9-other-side";
        }
        if (ticks == 1370) {
            Finery.LOGGER.info("[Autotest] result shots={} adjust={} worn={}", shot, adjustShot, worn(client));
        }
    }

    @SubscribeEvent
    public static void frame(net.neoforged.neoforge.client.event.RenderFrameEvent.Post event) {
        if (pendingShot == null) {
            return;
        }
        String label = pendingShot;
        pendingShot = null;
        grab(Minecraft.getInstance(), label);
    }

    private static String worn(Minecraft client) {
        return CuriosApi.getCuriosInventory(client.player)
                .map(handler -> handler.getCurios().entrySet().stream()
                        .filter(entry -> !entry.getValue().getStacks().getStackInSlot(0).isEmpty())
                        .map(entry -> entry.getKey() + "=" + entry.getValue().getStacks().getStackInSlot(0)
                                .getItem().getDescriptionId())
                        .toList().toString())
                .orElse("no curio handler");
    }

    private static void grab(Minecraft client, String label) {
        Screenshot.grab(client.gameDirectory, client.getMainRenderTarget(),
                message -> Finery.LOGGER.info("[Autotest] {} screenshot {}", label, message.getString()));
    }
}
