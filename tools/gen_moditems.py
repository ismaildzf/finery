"""Generate the NeoForge ModItems from the converted Fabric registry declarations."""

import re

SRC = r"C:\MinecraftModding\mods\finery-neoforge\_port\mojmap-src2\net\developer\finary\registry\ModItems.java"
SRC = SRC.replace("finary", "finery")
OUT = r"C:\MinecraftModding\mods\finery-neoforge-spike\src\main\java\net\developer\finery\registry\ModItems.java"

text = open(SRC, encoding="utf-8").read()
decl = re.compile(r"public static final (CapeItem|HeadItem|NeckItem|WingItem) (\w+) = (\w+)\((.*?)\);", re.S)

items = []
for match in decl.finditer(text):
    kind, field, helper, args = match.groups()
    args = " ".join(args.split())
    first = re.match(r'"([^"]+)"', args).group(1)
    rest = args[len(re.match(r'"[^"]+"', args).group(0)):].lstrip(", ")
    items.append((kind, field, helper, first, rest))

families = {"CapeItem": "ALL", "HeadItem": "HEADS", "NeckItem": "NECKS", "WingItem": "WINGS"}
header = '''package net.developer.finery.registry;

import net.developer.finery.Finery;
import net.developer.finery.ability.CapeAbility;
import net.developer.finery.ability.HeadAbility;
import net.developer.finery.ability.NeckAbility;
import net.developer.finery.ability.WingAbility;
import net.developer.finery.item.CapeItem;
import net.developer.finery.item.CapeRarity;
import net.developer.finery.item.DyeableHeadItem;
import net.developer.finery.item.DyeableNeckItem;
import net.developer.finery.item.HeadItem;
import net.developer.finery.item.NeckItem;
import net.developer.finery.item.WingItem;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

import java.util.ArrayList;
import java.util.List;

/** NeoForge item registry. Static fields are bound after registration in common setup. */
public final class ModItems {
    public static final DeferredRegister<Item> ITEMS = DeferredRegister.create(ForgeRegistries.ITEMS, Finery.MOD_ID);
    public static final DeferredRegister<CreativeModeTab> TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, Finery.MOD_ID);

'''

body = []
bind_lines = []
family_holders = {v: [] for v in families.values()}

for kind, field, helper, name, rest in items:
    body.append(f"    public static {kind} {field};")
    body.append(f"    private static final RegistryObject<{kind}> {field}_H = {helper}(\"{name}\", {rest});")
    bind_lines.append(f"        {field} = {field}_H.get();")
    family_holders[families[kind]].append(f"{field}_H")

body.append("")
lists = []
for family, holders in family_holders.items():
    holder_list = ", ".join(holders)
    upper = family.replace("ALL", "ALL")
    body.append(f"    private static final List<RegistryObject<? extends Item>> {family}_HOLDERS = List.of({holder_list});")
    body.append(f"    public static List<? extends Item> {family};")
    lists.append(family)

body.append(f'''
    public static final RegistryObject<CreativeModeTab> TAB = TABS.register("finery", () -> CreativeModeTab.builder()
            .title(Component.translatable("itemGroup.finery"))
            .icon(() -> new ItemStack({items[0][1]}_H.get()))
            .displayItems((params, output) -> {{
                for (RegistryObject<? extends Item> holder : ALL_HOLDERS) output.accept(holder.get());
                for (RegistryObject<? extends Item> holder : HEADS_HOLDERS) output.accept(holder.get());
                for (RegistryObject<? extends Item> holder : NECKS_HOLDERS) output.accept(holder.get());
                for (RegistryObject<? extends Item> holder : WINGS_HOLDERS) output.accept(holder.get());
            }})
            .build());

    private ModItems() {{
    }}

    public static void register(DeferredRegister<Item> bus) {{
        ITEMS.register(bus);
        TABS.register(bus);
    }}

    /** Runs after registries are frozen. */
    public static void bind() {{
''' + "\n".join(bind_lines) + '''

        ALL = List.copyOf(ALL_HOLDERS.stream().map(RegistryObject::get).toList());
        HEADS = List.copyOf(HEADS_HOLDERS.stream().map(RegistryObject::get).toList());
        NECKS = List.copyOf(NECKS_HOLDERS.stream().map(RegistryObject::get).toList());
        WINGS = List.copyOf(WINGS_HOLDERS.stream().map(RegistryObject::get).toList());
        Finery.LOGGER.info("[Finery] Registered {{}} capes, {{}} head cosmetics, {{}} neckwear and {{}} wings.",
                ALL.size(), HEADS.size(), NECKS.size(), WINGS.size());
    }}

    private static Item.Properties settings() {{
        return new Item.Properties().stacksTo(1);
    }}

    private static RegistryObject<CapeItem> register(String name, String variant, CapeAbility ability,
                                                    CapeRarity rarity, String hintKey) {{
        return ITEMS.register(name, () -> new CapeItem(settings(), variant, ability, rarity, hintKey));
    }}

    private static RegistryObject<HeadItem> registerHead(String name, String variant, String slot,
                                                         HeadAbility ability, CapeRarity rarity, String hintKey) {{
        return ITEMS.register(name, () -> new HeadItem(settings(), variant, slot, ability, rarity, hintKey));
    }}

    private static RegistryObject<HeadItem> registerDyeableHead(String name, String variant, String slot,
                                                                HeadAbility ability, CapeRarity rarity,
                                                                String hintKey, int defaultDye) {{
        return ITEMS.register(name, () -> new DyeableHeadItem(settings(), variant, slot, ability, rarity, hintKey, defaultDye));
    }}

    private static RegistryObject<NeckItem> registerNeck(String name, String variant, NeckAbility ability,
                                                         CapeRarity rarity, String hintKey) {{
        return ITEMS.register(name, () -> new NeckItem(settings(), variant, ability, rarity, hintKey));
    }}

    private static RegistryObject<NeckItem> registerDyeableNeck(String name, String variant, NeckAbility ability,
                                                                CapeRarity rarity, String hintKey, int defaultDye) {{
        return ITEMS.register(name, () -> new DyeableNeckItem(settings(), variant, ability, rarity, hintKey, defaultDye));
    }}

    private static RegistryObject<WingItem> registerWing(String name, String variant, WingAbility ability,
                                                         String hintKey) {{
        return ITEMS.register(name, () -> new WingItem(settings().fireResistant(), variant, ability,
                CapeRarity.LEGENDARY, hintKey));
    }}
}}
''')

open(OUT, "w", encoding="utf-8").write(header + "\n".join(body))
print("items", len(items), "families", {k: len(v) for k, v in family_holders.items()})
