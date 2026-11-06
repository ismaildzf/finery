package net.developer.finery.client;

import net.developer.finery.Finery;
import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.screens.ConnectScreen;
import net.minecraft.client.multiplayer.ServerData;
import net.minecraft.client.multiplayer.resolver.ServerAddress;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import top.theillusivec4.curios.api.CuriosApi;

/**
 * Visual smoke test, opt-in with -Dfinery.autotest=true.
 * The server cycles one item per cosmetic family every 140 ticks; this takes a
 * screenshot per phase plus one of the adjust screen.
 */
@Mod.EventBusSubscriber(modid = Finery.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE, value = Dist.CLIENT)
public final class ClientSelfTest {
    private static final String[] SHOTS = {
            "1-cape-set", "2-angel", "3-devil", "4-dragon", "5-butterfly", "6-hat-scarf", "7-horns-torc", "8-dyed"
    };

    private static int ticks;
    private static int shot;
    private static boolean adjustShot;
    private static int retries;
    private static int retryDelay = 100;

    private ClientSelfTest() {
    }

    @SubscribeEvent
    public static void tick(TickEvent.ClientTickEvent event) {
        if (event.phase != TickEvent.Phase.END || System.getProperty("finery.autotest") == null) {
            return;
        }
        Minecraft client = Minecraft.getInstance();
        if (client.player == null || client.level == null) {
            ticks = 0;
            if (client.screen instanceof net.minecraft.client.gui.screens.DisconnectedScreen && retries < 3) {
                if (--retryDelay <= 0) {
                    retries++;
                    retryDelay = 200;
                    Finery.LOGGER.info("[Autotest] reconnecting, attempt {}", retries + 1);
                    ConnectScreen.startConnecting(client.screen, client,
                            ServerAddress.parseString("127.0.0.1:25565"),
                            new ServerData("autotest", "127.0.0.1:25565", false), false);
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
            grab(client, SHOTS[shot]);
            shot++;
        }
        if (ticks == 1240) {
            client.setScreen(new CosmeticAdjustScreen(null));
        }
        if (ticks == 1300 && !adjustShot) {
            adjustShot = true;
            Finery.LOGGER.info("[Autotest] adjust screen open={}", client.screen != null);
            grab(client, "8-adjust-screen");
        }
        if (ticks == 1360) {
            client.setScreen(null);
            Finery.LOGGER.info("[Autotest] result shots={} adjust={} worn={}", shot, adjustShot, worn(client));
        }
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
