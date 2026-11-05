package net.developer.finery.client;

import io.wispforest.accessories.api.AccessoriesCapability;
import net.developer.finery.Finery;
import net.developer.finery.item.HeadItem;
import net.developer.finery.item.NeckItem;
import net.developer.finery.item.WingItem;
import net.developer.finery.registry.ModItems;
import net.fabricmc.api.EnvType;
import net.fabricmc.api.Environment;
//? if >=1.21.10 {
import net.minecraft.client.input.KeyInput;
//?}
import net.minecraft.client.gui.DrawContext;
import net.minecraft.client.gui.screen.Screen;
import net.minecraft.client.gui.screen.ingame.InventoryScreen;
import net.minecraft.client.gui.widget.ButtonWidget;
import net.minecraft.item.Item;
import net.minecraft.item.ItemStack;
import net.minecraft.text.Text;
import net.minecraft.util.Formatting;
import org.lwjgl.glfw.GLFW;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * Adjustment screen for worn head/neck/wing cosmetics: a live player preview in
 * the middle (drag the mouse over it to rotate, exactly like the inventory), the
 * worn items listed on the left, and nudge controls on the right. Every
 * change is applied and persisted immediately (see {@link CosmeticAdjustments}),
 * so WYSIWYG — press Done when it fits.
 *
 * Opened with K in-game or via the "Adjust Cosmetics..." button added to the
 * pause menu.
 */
@Environment(EnvType.CLIENT)
public class CosmeticAdjustScreen extends Screen {

    private static final float[] STEPS = {0.25F, 0.5F, 1.0F};

    private final Screen parent;
    private final List<Item> worn = new ArrayList<>();
    private final List<ButtonWidget> itemButtons = new ArrayList<>();

    private int index;
    private int stepIndex = 1;
    private ButtonWidget stepButton;

    public CosmeticAdjustScreen(Screen parent) {
        super(Text.translatable("finery.adjust.title"));
        this.parent = parent;
    }

    @Override
    protected void init() {
        worn.clear();
        itemButtons.clear();
        if (this.client != null && this.client.player != null) {
            AccessoriesCapability.getOptionally(this.client.player).ifPresent(capability -> {
                for (HeadItem item : ModItems.HEADS) {
                    if (!capability.getEquipped(item).isEmpty()) {
                        worn.add(item);
                    }
                }
                for (NeckItem item : ModItems.NECKS) {
                    if (!capability.getEquipped(item).isEmpty()) {
                        worn.add(item);
                    }
                }
                for (WingItem item : ModItems.WINGS) {
                    if (!capability.getEquipped(item).isEmpty()) {
                        worn.add(item);
                    }
                }
            });
        }
        index = Math.min(index, Math.max(0, worn.size() - 1));

        int centerX = this.width / 2;
        int centerY = this.height / 2;
        int leftX = Math.max(4, centerX - 174);
        int rightX = Math.min(this.width - 114, centerX + 64);
        int w = 110;
        int h = 20;

        // left column: worn head items + done
        int y = centerY - 62;
        for (int i = 0; i < worn.size(); i++) {
            final int idx = i;
            ButtonWidget button = ButtonWidget.builder(new ItemStack(worn.get(i)).getName(),
                            b -> selectItem(idx))
                    .dimensions(leftX, y, 130, h)
                    .build();
            itemButtons.add(button);
            addDrawableChild(button);
            y += 24;
        }
        addDrawableChild(ButtonWidget.builder(Text.translatable("finery.adjust.done"), b -> close())
                .dimensions(leftX, centerY + 62, 130, h)
                .build());

        // right column: nudge controls + step + reset
        y = centerY - 86;
        addDrawableChild(nudgeButton("finery.adjust.up", 0, -1, 0, rightX, y, w, h));
        y += 24;
        addDrawableChild(nudgeButton("finery.adjust.down", 0, 1, 0, rightX, y, w, h));
        y += 24;
        addDrawableChild(nudgeButton("finery.adjust.left", -1, 0, 0, rightX, y, w, h));
        y += 24;
        addDrawableChild(nudgeButton("finery.adjust.right", 1, 0, 0, rightX, y, w, h));
        y += 24;
        addDrawableChild(nudgeButton("finery.adjust.out", 0, 0, -1, rightX, y, w, h));
        y += 24;
        addDrawableChild(nudgeButton("finery.adjust.in", 0, 0, 1, rightX, y, w, h));
        y += 28;
        stepButton = ButtonWidget.builder(stepText(), b -> {
            stepIndex = (stepIndex + 1) % STEPS.length;
            b.setMessage(stepText());
        }).dimensions(rightX, y, w, h).build();
        addDrawableChild(stepButton);
        y += 24;
        addDrawableChild(ButtonWidget.builder(Text.translatable("finery.adjust.reset"), b -> resetCurrent())
                .dimensions(rightX, y, w, h)
                .build());

        refreshItemButtons();
    }

    private Text stepText() {
        return Text.translatable("finery.adjust.step", String.format(Locale.ROOT, "%.2f", STEPS[stepIndex]));
    }

    private ButtonWidget nudgeButton(String key, float dx, float dy, float dz, int x, int y, int w, int h) {
        return ButtonWidget.builder(Text.translatable(key), b -> nudge(dx, dy, dz))
                .dimensions(x, y, w, h)
                .build();
    }

    private void selectItem(int newIndex) {
        if (newIndex >= 0 && newIndex < worn.size()) {
            index = newIndex;
            refreshItemButtons();
        }
    }

    private void refreshItemButtons() {
        for (int i = 0; i < itemButtons.size(); i++) {
            if (i == index) {
                itemButtons.get(i).setMessage(
                        Text.literal("▶ ").append(new ItemStack(worn.get(i)).getName()).formatted(Formatting.YELLOW));
            } else {
                itemButtons.get(i).setMessage(new ItemStack(worn.get(i)).getName());
            }
        }
    }

    private Item currentItem() {
        return worn.isEmpty() ? null : worn.get(index);
    }

    /** Model variant of a worn cosmetic (head, neck or wing). */
    private static String variantOf(Item item) {
        if (item instanceof HeadItem head) {
            return head.getVariant();
        }
        if (item instanceof NeckItem neck) {
            return neck.getVariant();
        }
        if (item instanceof WingItem wing) {
            return wing.getVariant();
        }
        return null;
    }

    private void nudge(float dx, float dy, float dz) {
        Item item = currentItem();
        if (item == null) {
            return;
        }
        String variant = variantOf(item);
        if (variant == null) {
            return;
        }
        float step = STEPS[stepIndex];
        float[] offset = CosmeticAdjustments.get(variant);
        float x = offset == null ? 0.0F : offset[0];
        float y = offset == null ? 0.0F : offset[1];
        float z = offset == null ? 0.0F : offset[2];
        CosmeticAdjustments.set(variant, x + dx * step, y + dy * step, z + dz * step);
    }

    private void resetCurrent() {
        Item item = currentItem();
        if (item != null) {
            String variant = variantOf(item);
            if (variant != null) {
                CosmeticAdjustments.set(variant, 0.0F, 0.0F, 0.0F);
            }
        }
    }

    //? if >=1.21.10 {
    @Override
    public boolean keyPressed(KeyInput input) {
        switch (input.key()) {
            case GLFW.GLFW_KEY_UP -> {
                nudge(0, -1, 0);
                return true;
            }
            case GLFW.GLFW_KEY_DOWN -> {
                nudge(0, 1, 0);
                return true;
            }
            case GLFW.GLFW_KEY_LEFT -> {
                nudge(-1, 0, 0);
                return true;
            }
            case GLFW.GLFW_KEY_RIGHT -> {
                nudge(1, 0, 0);
                return true;
            }
            case GLFW.GLFW_KEY_PAGE_UP -> {
                nudge(0, 0, -1);
                return true;
            }
            case GLFW.GLFW_KEY_PAGE_DOWN -> {
                nudge(0, 0, 1);
                return true;
            }
            case GLFW.GLFW_KEY_R -> {
                resetCurrent();
                return true;
            }
            default -> {
            }
        }
        return super.keyPressed(input);
    }
    //?} else {
    /*@Override
    public boolean keyPressed(int keyCode, int scanCode, int modifiers) {
        switch (keyCode) {
            case GLFW.GLFW_KEY_UP -> {
                nudge(0, -1, 0);
                return true;
            }
            case GLFW.GLFW_KEY_DOWN -> {
                nudge(0, 1, 0);
                return true;
            }
            case GLFW.GLFW_KEY_LEFT -> {
                nudge(-1, 0, 0);
                return true;
            }
            case GLFW.GLFW_KEY_RIGHT -> {
                nudge(1, 0, 0);
                return true;
            }
            case GLFW.GLFW_KEY_PAGE_UP -> {
                nudge(0, 0, -1);
                return true;
            }
            case GLFW.GLFW_KEY_PAGE_DOWN -> {
                nudge(0, 0, 1);
                return true;
            }
            case GLFW.GLFW_KEY_R -> {
                resetCurrent();
                return true;
            }
            default -> {
            }
        }
        return super.keyPressed(keyCode, scanCode, modifiers);
    }
    *///?}

    @Override
    public void render(DrawContext context, int mouseX, int mouseY, float delta) {
        // Screen.render draws the blurred background itself, so everything of
        // ours goes AFTER it — drawing before it buries the preview under the blur
        super.render(context, mouseX, mouseY, delta);

        int centerX = this.width / 2;
        int centerY = this.height / 2;

        drawPreview(context, mouseX, mouseY);

        context.drawCenteredTextWithShadow(this.textRenderer, this.title, centerX, 14, 0xFFFFFF);

        Item item = currentItem();
        if (item != null) {
            float[] offset = CosmeticAdjustments.get(variantOf(item));
            float x = offset == null ? 0.0F : offset[0];
            float y = offset == null ? 0.0F : offset[1];
            float z = offset == null ? 0.0F : offset[2];
            context.drawCenteredTextWithShadow(this.textRenderer,
                    Text.literal(String.format(Locale.ROOT, "X %+.2f   Y %+.2f   Z %+.2f", x, y, z)),
                    centerX, centerY + 84, 0xFFE084);
        } else {
            context.drawCenteredTextWithShadow(this.textRenderer,
                    Text.translatable("finery.adjust.empty"), centerX, centerY + 84, 0xFF5555);
        }
    }

    /** Live player preview, drawn exactly like the vanilla inventory does it. */
    private void drawPreview(DrawContext context, int mouseX, int mouseY) {
        if (this.client == null || this.client.player == null) {
            return;
        }
        int centerX = this.width / 2;
        int centerY = this.height / 2;
        int x1 = centerX - 52;
        int y1 = centerY - 60;
        int x2 = centerX + 52;
        int y2 = centerY + 60;

        context.fill(x1 - 2, y1 - 2, x2 + 2, y2 + 2, 0xFF3B3B46);
        context.fill(x1, y1, x2, y2, 0xFF121217);
        //? if >=1.21 {
        InventoryScreen.drawEntity(context, x1, y1, x2, y2, 50, 0.0625F, mouseX, mouseY, this.client.player);
        //?} else {
        /*InventoryScreen.drawEntity(context, centerX, centerY, 50, mouseX, mouseY, this.client.player);
        *///?}
    }

    @Override
    public void close() {
        if (this.client != null) {
            this.client.setScreen(this.parent);
        }
    }
}
