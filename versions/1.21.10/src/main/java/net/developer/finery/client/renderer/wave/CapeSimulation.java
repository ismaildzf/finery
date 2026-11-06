package net.developer.finery.client.renderer.wave;

/**
 * Rope simulation for one worn cape.
 *
 * Ported from tr7zw's WaveyCapes (MIT) versionless/sim/CapeSimulation +
 * StickSimulation (itself a Java port of Sebastian Lague's rope video).
 * A cape is a rope of {@link #PART_COUNT} points; point 0 is pinned to the
 * player, the rest fall under gravity and are constrained to unit spacing.
 * The rendered ribbon reads the lerped point positions each frame.
 */
public class CapeSimulation {

    public static final int PART_COUNT = 16;
    private static final int ITERATIONS = 3;
    private static final float MAX_BEND = 5.0F;

    private final float[] x = new float[PART_COUNT];
    private final float[] y = new float[PART_COUNT];
    private final float[] prevX = new float[PART_COUNT];
    private final float[] prevY = new float[PART_COUNT];

    private float gravity = 25.0F;
    private boolean sneaking;

    private float dirX;
    private float dirY;

    public CapeSimulation() {
        for (int i = 0; i < PART_COUNT; i++) {
            y[i] = -i;
            prevY[i] = -i;
        }
    }

    public boolean isShiftKeyDown() {
        return sneaking;
    }

    public void setShiftKeyDown(boolean sneaking) {
        this.sneaking = sneaking;
    }

    public void setGravity(float gravity) {
        this.gravity = gravity;
    }

    /** Shifts the pinned point 0 (cape anchor) by the given amounts. */
    public void applyMovement(float dx, float dy) {
        prevX[0] = x[0];
        prevY[0] = y[0];
        x[0] += dx;
        y[0] += dy;
    }

    public void simulate() {
        applyGravity();
        preventClipping();
        preventHardBends();
        applyMotion();
        limitLength();
    }

    public float lerpX(int index, float delta) {
        return lerp(delta, prevX[index], x[index]);
    }

    public float lerpY(int index, float delta) {
        return lerp(delta, prevY[index], y[index]);
    }

    // ── internals (ported) ──────────────────────────────────────────────

    private static float lerp(float delta, float start, float end) {
        return start + delta * (end - start);
    }

    private void applyGravity() {
        float fall = gravity * (50.0F / 1000.0F);
        for (int i = 1; i < PART_COUNT; i++) {
            prevX[i] = x[i];
            prevY[i] = y[i];
            y[i] -= fall;
        }
    }

    private void preventClipping() {
        // points can never pass the anchor towards the player's body
        for (int i = 1; i < PART_COUNT; i++) {
            if (x[i] - x[0] > 0) {
                x[i] = x[0];
            }
        }
    }

    private void preventHardBends() {
        for (int i = PART_COUNT - 2; i >= 1; i--) {
            double angle = Math.atan2(y[i + 1] - y[i], x[i + 1] - x[i])
                    - Math.atan2(y[i - 1] - y[i], x[i - 1] - x[i]);
            angle *= 57.2958;
            if (angle > 360) {
                angle -= 360;
            }
            if (angle < -360) {
                angle += 360;
            }
            double abs = Math.abs(angle);
            if (abs < 180 - MAX_BEND) {
                replace(i, angle, 180 - MAX_BEND + 1);
            }
            if (abs > 180 + MAX_BEND) {
                replace(i, angle, 180 + MAX_BEND - 1);
            }
        }
    }

    private void replace(int i, double angle, double target) {
        double theta = target / 57.2958;
        float px = x[i - 1] - x[i];
        float py = y[i - 1] - y[i];
        if (angle < 0) {
            theta *= -1;
        }
        double cs = Math.cos(theta);
        double sn = Math.sin(theta);
        x[i + 1] = (float) ((px * cs) - (py * sn) + x[i]);
        y[i + 1] = (float) ((px * sn) + (py * cs) + y[i]);
    }

    private void applyMotion() {
        for (int i = 0; i < ITERATIONS; i++) {
            for (int a = PART_COUNT - 2; a >= 0; a--) {
                direction(a, a + 1);
                separate(a, a + 1);
            }
        }
    }

    private void limitLength() {
        for (int a = 0; a < PART_COUNT - 1; a++) {
            direction(a, a + 1);
            x[a + 1] = x[a] - dirX;
            y[a + 1] = y[a] - dirY;
        }
    }

    private void direction(int a, int b) {
        dirX = x[a] - x[b];
        dirY = y[a] - y[b];
        float f = (float) Math.sqrt(dirX * dirX + dirY * dirY);
        if (f < 1.0E-4F) {
            dirX = 0;
            dirY = 0;
        } else {
            dirX /= f;
            dirY /= f;
        }
    }

    private void separate(int a, int b) {
        float centreX = (x[a] + x[b]) / 2;
        float centreY = (y[a] + y[b]) / 2;
        if (a != 0) {
            x[a] = centreX + dirX / 2;
            y[a] = centreY + dirY / 2;
        }
        x[b] = centreX - dirX / 2;
        y[b] = centreY - dirY / 2;
    }
}
