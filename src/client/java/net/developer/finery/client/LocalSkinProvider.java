package net.developer.finery.client;

//? if =1.21.1 {
/*import net.minecraft.client.MinecraftClient;
import net.minecraft.client.network.AbstractClientPlayerEntity;
import net.minecraft.client.texture.NativeImage;
import net.minecraft.client.texture.NativeImageBackedTexture;
import net.minecraft.client.util.SkinTextures;
import net.minecraft.util.Identifier;
*///?} elif >=1.21.10 {
import net.minecraft.client.MinecraftClient;
import net.minecraft.client.network.AbstractClientPlayerEntity;
import net.minecraft.client.texture.NativeImage;
import net.minecraft.client.texture.NativeImageBackedTexture;
import net.minecraft.entity.player.PlayerSkinType;
import net.minecraft.entity.player.SkinTextures;
import net.minecraft.util.AssetInfo;
import net.minecraft.util.Identifier;

//?}

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * Offline local-skin override for dev play.
 *
 * WHY: In a dev environment the player has no Mojang session, so no skin is
 * fetched and the local player renders as Steve/Alex. Instead of requiring a
 * real Microsoft login (DevAuth) we simply load a PNG from disk.
 *
 * HOW: If config/finery/skin.png exists (path is relative to the run
 * directory), its pixels are registered as a texture and wrapped in a
 * SkinTextures object returned only for the local player. Slim vs wide is
 * auto-detected the same way vanilla skins are: on slim (Alex-style) textures
 * the 4px-wide arm area at x50..55 is unused, so pixel (50,16) is transparent.
 */
//? if =1.21.1 {
/*public final class LocalSkinProvider {

    private static final Identifier TEXTURE_ID = Identifier.of("finery", "local_skin");
    private static final Path SKIN_FILE = Path.of("config", "finery", "skin.png");

    private static SkinTextures localSkin;
    private static boolean attempted;

    private LocalSkinProvider() {}

    /^*
     * @return custom SkinTextures when {@code player} is the local player and a
     *         skin file is present, otherwise null (fall back to vanilla).
     ^/
    public static SkinTextures getLocalSkin(AbstractClientPlayerEntity player) {
        if (player != MinecraftClient.getInstance().player) {
            return null;
        }
        if (!attempted) {
            attempted = true;
            localSkin = load();
        }
        return localSkin;
    }

    private static SkinTextures load() {
        if (!Files.isRegularFile(SKIN_FILE)) {
            return null;
        }
        try (InputStream in = Files.newInputStream(SKIN_FILE)) {
            NativeImage image = NativeImage.read(in);
            SkinTextures.Model model = image.getOpacity(50, 16) == 0
                    ? SkinTextures.Model.SLIM
                    : SkinTextures.Model.WIDE;
            MinecraftClient.getInstance().getTextureManager()
                    .registerTexture(TEXTURE_ID, new NativeImageBackedTexture(image));
            return new SkinTextures(TEXTURE_ID, null, null, null, model, false);
        } catch (IOException e) {
            return null;
        }
    }
}
*///?} elif >=1.21.10 {
public final class LocalSkinProvider {

    private static final Identifier TEXTURE_ID = Identifier.of("finery", "local_skin");
    // The player renderer looks textures up by AssetInfo.texturePath(), so the
    // dynamic texture has to be registered under that exact id.
    private static final Identifier TEXTURE_PATH = Identifier.of("finery", "textures/local_skin.png");
    private static final Path SKIN_FILE = Path.of("config", "finery", "skin.png");

    private static SkinTextures localSkin;
    private static boolean attempted;

    private LocalSkinProvider() {}

    // @return custom SkinTextures when the given player is the local player
    // and a skin file is present, otherwise null (fall back to vanilla).
    public static SkinTextures getLocalSkin(AbstractClientPlayerEntity player) {
        if (player != MinecraftClient.getInstance().player) {
            return null;
        }
        if (!attempted) {
            attempted = true;
            localSkin = load();
        }
        return localSkin;
    }

    private static SkinTextures load() {
        if (!Files.isRegularFile(SKIN_FILE)) {
            return null;
        }
        try (InputStream in = Files.newInputStream(SKIN_FILE)) {
            NativeImage image = NativeImage.read(in);
            PlayerSkinType model = image.getOpacity(50, 16) == 0
                    ? PlayerSkinType.SLIM
                    : PlayerSkinType.WIDE;
            MinecraftClient.getInstance().getTextureManager()
                    .registerTexture(TEXTURE_PATH,
                            new NativeImageBackedTexture(() -> TEXTURE_PATH.toString(), image));
            return new SkinTextures(new AssetInfo.TextureAssetInfo(TEXTURE_ID, TEXTURE_PATH), null, null, model, false);
        } catch (IOException e) {
            return null;
        }
    }
}

//?} else {
/*public final class LocalSkinProvider {

    // 1.20.1 has no SkinTextures API - the local-skin dev override is
    // unavailable here, so the local player renders with the vanilla default.
    private LocalSkinProvider() {}

    public static Object getLocalSkin(Object player) {
        return null;
    }
}
*///?}
