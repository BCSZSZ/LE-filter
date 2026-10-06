"""Inventory the two user-supplied planner snapshots; do not generate filters."""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = json.loads((ROOT / "sources/game-reference.json").read_text(encoding="utf-8"))
MANIFEST = json.loads((ROOT / "sources/builds/manifest.json").read_text(encoding="utf-8"))
TYPES = {v: k for k, v in REF["equipment_enum"].items()}
builds = {}
all_uniques, all_affixes = set(), set()

for slug in ("flay-mana-lich", "skeleton-necromancer"):
    path = ROOT / "sources/builds" / (slug + ".json")
    assert hashlib.sha256(path.read_bytes()).hexdigest() == MANIFEST["inputs"][slug]["sha256"]
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    equipment = [i for slot, i in data["items"].items() if slot != "altar"]
    idols = [i for i in data["idols"] if i is not None]
    objects = list(data["items"].values()) + idols
    uniques = {i["uniqueID"] for i in equipment if "uniqueID" in i}
    regular = {a["id"] for i in objects for a in i.get("affixes", [])}
    corrupted = {a["id"] for i in objects for a in i.get("corruptedAffixes", [])}
    assert {str(i) for i in uniques} <= REF["uniques"].keys()
    assert {str(i) for i in regular | corrupted} <= REF["affixes"].keys()
    all_uniques |= uniques
    all_affixes |= regular | corrupted
    configurations = Counter(json.dumps(i, sort_keys=True) for i in idols)
    rolls = {v for i in objects for key in ("uniqueRolls", "implicits") for v in i.get(key, [])}
    rolls |= {a["roll"] for i in objects for key in ("affixes", "corruptedAffixes") for a in i.get(key, [])}
    inventory = []
    for slot, item in data["items"].items():
        entry = {"slot": slot, "item_type_id": item["itemType"],
                 "item_type": TYPES[item["itemType"]], "subtype_id": item["subType"],
                 "unique_id": item.get("uniqueID"), "corrupted": item.get("corrupted", False)}
        if "uniqueID" in item:
            entry["unique_name"] = REF["uniques"][str(item["uniqueID"])]["en"]
        for key in ("affixes", "corruptedAffixes"):
            entry[key] = [{**a, "name_en": REF["affixes"][str(a["id"])]["en"],
                           "name_zh": REF["affixes"][str(a["id"])]["zh"]} for a in item.get(key, [])]
        inventory.append(entry)
    builds[slug] = {
        "source": path.relative_to(ROOT).as_posix(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "class_id": data["class"], "mastery_id": data["mastery"],
        "counts": {"equipment": len(equipment), "altars": int("altar" in data["items"]),
                   "unique_instances": sum("uniqueID" in i for i in equipment),
                   "distinct_unique_ids": len(uniques), "idol_objects": len(idols),
                   "distinct_idol_configurations": len(configurations),
                   "regular_array_affix_ids": len(regular), "corrupted_affix_ids": len(corrupted),
                   "all_affix_ids": len(regular | corrupted),
                   "selected_blessings": sum(i is not None for i in data["blessings"]),
                   "passive_history_entries": len(data["passives"]["history"]),
                   "skill_trees": len(data["skillTrees"])},
        "unique_ids": sorted(uniques), "regular_array_affix_ids": sorted(regular),
        "corrupted_affix_ids": sorted(corrupted), "recorded_roll_values": sorted(rolls),
        "items": inventory,
        "idol_configurations": [{"count": count, "item": json.loads(key)} for key, count in sorted(configurations.items())],
        "skills": {key: {"history_entries": len(value["history"]), "position": value["position"]}
                   for key, value in data["skillTrees"].items()},
        "passive_history_position": data["passives"]["position"],
        "priority_fields": [{"slot": slot, "affix_id": a["id"], "priority": a["priority"]}
                            for slot, item in data["items"].items() for a in item.get("affixes", []) if "priority" in a],
    }

result = {"reference_game_version": REF["game_version"], "game_execution_tested": False,
          "combined_unique_ids": sorted(all_uniques), "combined_affix_ids": sorted(all_affixes),
          "builds": builds}
out = ROOT / "analysis/build-inputs.json"
out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
print(json.dumps({slug: build["counts"] for slug, build in builds.items()}, ensure_ascii=False))
