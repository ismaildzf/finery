import json
import pathlib

base = pathlib.Path(__file__).resolve().parents[1] / "src" / "main" / "resources" / "assets" / "finery" / "lang"
en_p = base / "en_us.json"
ar_p = base / "ar_sa.json"

en = json.loads(en_p.read_text(encoding="utf-8"))
ar = json.loads(ar_p.read_text(encoding="utf-8"))

en["item.finery.voidwing.desc"] = (
    "Plumage from a dragon's dusk, swallowed by the sculk beneath the Ancient City. "
    "See in darkness, shrug off the Darkness effect, and gain Resistance I while airborne."
)
en["item.finery.fae_wings.desc"] = (
    "Wings from the hidden court of the woodland mansion, dusted in fern-green plumes. "
    "Jump Boost I and Luck I at all times, and Speed I while airborne."
)

ar["item.finery.voidwing.desc"] = (
    "\u0631\u064a\u0634 \u0645\u0646 \u063a\u0631\u0648\u0628 \u062a\u0646\u064a\u0646 "
    "\u0627\u0628\u062a\u0644\u0639\u0647 \u0627\u0644\u0633\u0643\u0644\u0643 \u062a\u062d\u062a "
    "\u0627\u0644\u0645\u062f\u064a\u0646\u0629 \u0627\u0644\u0642\u062f\u064a\u0645\u0629. "
    "\u062a\u0631\u0649 \u0641\u064a \u0627\u0644\u0638\u0644\u0627\u0645\u060c "
    "\u0648\u0644\u0627 \u064a\u0624\u062b\u0631 \u0641\u064a\u0643 \u062a\u0623\u062b\u064a\u0631 "
    "\u0627\u0644\u0638\u0644\u0627\u0645\u060c \u0648\u062a\u062d\u0635\u0644 \u0639\u0644\u0649 "
    "\u0645\u0642\u0627\u0648\u0645\u0629 I \u0623\u062b\u0646\u0627\u0621 \u0648\u062c\u0648\u062f\u0643 "
    "\u0641\u064a \u0627\u0644\u0647\u0648\u0627\u0621."
)
ar["item.finery.fae_wings.desc"] = (
    "\u0623\u062c\u0646\u062d\u0629 \u0645\u0646 \u0628\u0644\u0627\u0637 \u0642\u0635\u0631 "
    "\u0627\u0644\u063a\u0627\u0628\u0629 \u0627\u0644\u062e\u0641\u064a\u060c \u0645\u0643\u0633\u0648\u0629 "
    "\u0628\u0631\u064a\u0634 \u0623\u062e\u0636\u0631 \u0643\u0627\u0644\u0633\u0631\u062e\u0633. "
    "\u0642\u0641\u0632 I \u0648\u062d\u0638 I \u062f\u0627\u0626\u0645\u0627\u0646\u060c "
    "\u0648\u0633\u0631\u0639\u0629 I \u0623\u062b\u0646\u0627\u0621 \u0648\u062c\u0648\u062f\u0643 "
    "\u0641\u064a \u0627\u0644\u0647\u0648\u0627\u0621."
)

en_p.write_text(json.dumps(en, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
ar_p.write_text(json.dumps(ar, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("lang updated")
