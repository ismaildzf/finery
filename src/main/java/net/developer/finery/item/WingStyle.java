package net.developer.finery.item;

import net.developer.finery.provider.ProviderRegistry;
import net.developer.finery.provider.SlotKind;
import top.theillusivec4.curios.api.SlotContext;
import top.theillusivec4.curios.api.type.capability.ICurioItem;

/** Mesh family used by the client wing renderer. */
public enum WingStyle {
    /** Angel v3: drooping primaries plus a raised covert sheet. */
    ANGEL,
    /** Forewing + hindwing butterfly silhouette. */
    BUTTERFLY,
    /** Baked bat wing with bone fingers and a torn crimson membrane. */
    DEVIL,
    /** Baked black dragon wing with an exposed skeletal arm. */
    DRAGON
}
