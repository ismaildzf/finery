package net.developer.finery.client.renderer.wave;

import net.minecraft.client.MinecraftClient;
import net.minecraft.client.network.AbstractClientPlayerEntity;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.util.math.MathHelper;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.UUID;

/**
 * Holds one {@link CapeSimulation} per player wearing an Epic Cape (client side).
 *
 * Per-tick feed ported from tr7zw's WaveyCapes (MIT) CapeHolder#simulate:
 * the vanilla cape anchor lag (player.capeX/Z vs entity position) is projected
 * onto the body yaw to get a forward/backward force, plus a vertical force and
 * small crouch/fall impulses.
 */
public final class CapeWaveManager {

    private static final Map<UUID, CapeSimulation> SIMULATIONS = new HashMap<>();

    //? if >=1.21.10 {
    // At 1.21.10 the player lost its capeX/capeZ anchor lag and prevY fields, so
    // we keep the vanilla damped anchor and previous-Y ourselves.
    private static final Map<UUID, Double> ANCHOR_X = new HashMap<>();
    private static final Map<UUID, Double> ANCHOR_Z = new HashMap<>();
    private static final Map<UUID, Double> LAST_Y = new HashMap<>();
    //?}

    private CapeWaveManager() {
    }

    /** Called by the cape renderer every frame it draws a cape for this player. */
    public static CapeSimulation obtain(AbstractClientPlayerEntity player) {
        CapeSimulation sim = SIMULATIONS.get(player.getUuid());
        if (sim == null) {
            sim = new CapeSimulation();
            // settle the fresh rope so it doesn't visibly snap on first render
            sim.applyMovement(1.0F, 1.0F);
            for (int i = 0; i < 5; i++) {
                step(sim, player);
            }
            SIMULATIONS.put(player.getUuid(), sim);
        }
        return sim;
    }

    /** Client tick hook: advance every tracked cape by one simulation step. */
    public static void tick(MinecraftClient client) {
        if (client.world == null) {
            SIMULATIONS.clear();
            //? if >=1.21.10 {
            ANCHOR_X.clear();
            ANCHOR_Z.clear();
            LAST_Y.clear();
            //?}
            return;
        }
        Iterator<Map.Entry<UUID, CapeSimulation>> it = SIMULATIONS.entrySet().iterator();
        while (it.hasNext()) {
            Map.Entry<UUID, CapeSimulation> entry = it.next();
            PlayerEntity player = client.world.getPlayerByUuid(entry.getKey());
            if (!(player instanceof AbstractClientPlayerEntity clientPlayer)) {
                it.remove();
                continue;
            }
            step(entry.getValue(), clientPlayer);
        }
    }

    private static void step(CapeSimulation sim, AbstractClientPlayerEntity player) {
        //? if >=1.21.10 {
        double prevY = pullLastY(player);
        double anchorDx = pullAnchor(ANCHOR_X, player, player.getX()) - player.getX();
        double anchorDz = pullAnchor(ANCHOR_Z, player, player.getZ()) - player.getZ();
        //?} else {
        /*double prevY = player.prevY;
        double anchorDx = player.capeX - player.getX();
        double anchorDz = player.capeZ - player.getZ();
        *///?}
        float n = player.bodyYaw;
        double o = MathHelper.sin(n * 0.017453292F);
        double p = -MathHelper.cos(n * 0.017453292F);

        boolean underwater = player.isSubmergedInWater();
        float heightMul = underwater ? 12.0F : 6.0F;
        // small backward push when jumping/falling so the cape doesn't fold into itself
        double fallHack = MathHelper.clamp((prevY - player.getY()) * 10.0D, 0.0D, 1.0D);

        sim.setGravity(underwater ? 2.5F : 25.0F);

        boolean crouchTransition = player.isSneaking() && !sim.isSneaking();
        double changeX = (anchorDx * o + anchorDz * p) + fallHack + (crouchTransition ? 3.0D : 0.0D);
        double changeY = ((player.getY() - prevY) * heightMul) + (crouchTransition ? 1.0D : 0.0D);
        sim.setSneaking(player.isSneaking());

        sim.applyMovement((float) changeX, (float) changeY);
        sim.simulate();
    }

    //? if >=1.21.10 {
    // Mirror of vanilla's removed anchor lag: capeX += (x - capeX) * 0.1 per tick.
    private static double pullAnchor(Map<UUID, Double> map, AbstractClientPlayerEntity player, double currentPos) {
        UUID id = player.getUuid();
        double current = map.getOrDefault(id, currentPos);
        map.put(id, current + (currentPos - current) * 0.1D);
        return current;
    }

    private static double pullLastY(AbstractClientPlayerEntity player) {
        UUID id = player.getUuid();
        double prev = LAST_Y.getOrDefault(id, player.getY());
        LAST_Y.put(id, player.getY());
        return prev;
    }
    //?}
}
