"""Freeze the searchable catalog from the project's verified version150 cache."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ref = json.loads((ROOT / "sources/game-reference.json").read_text(encoding="utf-8"))
for key, filename in [("db", "db.js"), ("en", "en.json"), ("zh", "zh.json")]:
    assert hashlib.sha256((ROOT / ".cache" / filename).read_bytes()).hexdigest() == ref["source_urls"][key]["sha256"]
db = json.loads((ROOT / ".cache/db.json").read_text(encoding="utf-8"))["itemDB"]
langs = {lang: json.loads((ROOT / f".cache/{lang}.json").read_text(encoding="utf-8")) for lang in ["en", "zh"]}


def names(key):
    return {lang: data.get(key, key).replace("''", "'") for lang, data in langs.items()}


types = ref["equipment_enum"]
reverse = {i: name for name, i in types.items()}
affixes = {}
for section in ["singleAffixes", "multiAffixes"]:
    for key, row in db["affixList"][section].items():
        affixes[key] = {"id": int(key), **names(row["lootFilterOverrideNameKey"] or row["affixDisplayNameKey"]),
                        "types": [reverse[i] for i in row["canRollOn"]], "special": row["specialAffixType"],
                        "class": row["classSpecificity"], "prefix": row["type"] == 0}
uniques = {key: {"id": int(key), **names(row["displayNameKey"]), "type": reverse[row["baseTypeId"]],
                 "set": bool(row["isSetItem"]), "hidden": bool(row["hideFromPlayers"])}
           for key, row in db["uniqueList"]["uniques"].items()}
for key, row in ref["uniques"].items():
    if key not in uniques:
        uniques[key] = {"id": int(key), "en": row["en"], "zh": row["zh"],
                        "type": reverse.get(row.get("base_type_id")), "set": False, "hidden": True}
bases = {}
for typ, item in db["itemList"]["equippable"].items():
    for key, row in item["subItems"].items():
        bases[f"{reverse[int(typ)]}:{key}"] = {"id": int(key), "type": reverse[int(typ)],
                                              **names(row["displayNameKey"]), "level": row["levelRequirement"],
                                              "legacy": bool(row["cannotDrop"] or row["isLegacySubType"] or row["obsoleteItem"])}
catalog = {"version": ref["game_version"], "source_urls": {k: ref["source_urls"][k] for k in ["db", "en", "zh"]},
           "types": ref["equipment_names"], "affixes": affixes, "uniques": uniques, "bases": bases}
assert len(affixes) == 1156
(ROOT / "sources/tool-catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
print(json.dumps({k: len(catalog[k]) for k in ["affixes", "uniques", "bases"]}))
