"""Build the Ice Heartseeker targets from the frozen planner snapshot, offline."""
from copy import deepcopy
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tool"))
from engine import CATALOG, MANIFEST
from requirements import read_document

SOURCE = ROOT / "sources/builds/letools-planner-al0dkyek-extracted.json"
BUILD_ID = "ice-heartseeker-planner-al0dkyek"
TYPE_IDS = json.loads((ROOT / "sources/game-reference.json").read_text(encoding="utf-8"))["equipment_enum"]
TYPES = {value: key for key, value in TYPE_IDS.items()}


def append_ids(target, values):
    for value in values:
        if value not in target:
            target.append(value)


def affix_groups(item):
    result = {"affixes": [], "corrupted": [], "enchanted": [], "fixed": []}
    for field in ("affixes", "corruptedAffixes", "enchantedAffixes", "fixedAffixes"):
        for affix in item.get(field, []):
            aid = affix["id"]
            data = CATALOG["affixes"].get(str(aid))
            if data is None:
                raise ValueError(f"构建器词缀{aid}未在冻结词库中。")
            category = {4: "enchanted", 6: "corrupted", 7: "fixed"}.get(data["special"], "affixes")
            append_ids(result[category], [aid])
    return result


def build_documents():
    facts = json.loads(SOURCE.read_text(encoding="utf-8"))
    planner = facts["planner"]
    targets = {key: [] for key in ("uniques", "equipment", "altars", "idols", "bases")}
    fixed_references = []
    unique_idol_references = []

    def add_item(item, slot):
        if item is None:
            return
        typ = TYPES[item["itemType"]]
        unique = item.get("uniqueID")
        if unique is not None:
            append_ids(targets["uniques"], [unique])
        pools = affix_groups(item)
        fixed = pools.pop("fixed")
        if fixed:
            fixed_references.append({"slot": slot, "type": typ, "ids": fixed})
        if typ == "IDOL_ALTAR":
            # Altar corruption is an actual target, outside ordinary idol counts.
            append_ids(pools["affixes"], pools.pop("corrupted"))
            append_ids(pools["affixes"], pools.pop("enchanted"))
            category, bases = "altars", [item["subType"]]
        elif typ.startswith("IDOL_"):
            if unique is not None:
                if any(pools.values()):
                    unique_idol_references.append({"slot": slot, "unique_id": unique, "type": typ,
                                                   "bases": [item["subType"]],
                                                   **{key: values for key, values in pools.items() if values}})
                return
            category, bases = "idols", [item["subType"]]
        elif typ in MANIFEST["scope_types"]:
            category, bases = "equipment", []
            if unique is None:
                base_group = next((g for g in targets["bases"] if g["type"] == typ), None)
                if base_group is None:
                    base_group = {"type": typ, "preferred_bases": [], "bases": []}
                    targets["bases"].append(base_group)
                append_ids(base_group["bases"], [item["subType"]])
        else:
            raise ValueError(f"构建器含未处理物品类型{typ}。")
        if not any(pools.values()):
            return
        group = next((g for g in targets[category] if g["type"] == typ and g["bases"] == bases), None)
        if group is None:
            group = {"type": typ, "bases": bases, "affixes": []}
            targets[category].append(group)
        for key, values in pools.items():
            if values:
                append_ids(group.setdefault(key, []), values)

    for slot, item in planner["items"].items():
        add_item(item, slot)
    for index, item in enumerate(planner["idols"]):
        add_item(item, f"idol{index + 1}")
    targets["uniques"].sort()
    source = {
        "name": "冰追心 · Last Epoch Tools 构建器 AL0dkyek",
        "url": "https://www.lastepochtools.com/planner/zh/AL0dkyek",
        "extracted_on": facts["extracted_on"],
        "sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "scope": "玩家指定构建器的当前终局配装；装备后加词缀、神像、祭坛及明确普通底材",
        "fixed_affix_references": fixed_references,
        "unique_idol_references": unique_idol_references,
        "warnings": [
            "保留构建器明确选择的全部后加词缀，包括低阶候选，供玩家后续调整优先级或删减。",
            "暗金固有属性、暗金自身底材、技能及祝福不转成普通词缀素材要求。",
            "神像按所示类型与底材收集普通0／5目标，附魔4与腐化6只作参考；祭坛腐化作为实际目标。",
            "暗金固定随机池词缀7另存来源参考，不加入普通T7素材池或增加暗金属性数值门槛。",
            "暗金神像按暗金ID收集，其附加参考另存来源，不生成普通神像目标层。",
            "构建器未提供练级路线或替代配装，练级需求留空。",
        ],
    }
    endgame = {"format": "le-filter-requirements", "version": 1, "id": BUILD_ID,
               "name": "冰追心", "stage": "endgame", "targets": targets, "source": source}
    leveling = deepcopy(endgame)
    leveling["stage"] = "leveling"
    leveling["targets"] = {"affixes": [], "bases": []}
    leveling["source"].pop("fixed_affix_references")
    leveling["source"].pop("unique_idol_references")
    leveling["source"]["scope"] = "练级需求未提供，独立留空，待玩家补充"
    leveling["source"]["warnings"] = ["当前来源只提供终局配装，未从终局推断练级目标。"]
    for document in (endgame, leveling):
        read_document(document)
    return endgame, leveling


if __name__ == "__main__":
    for document in build_documents():
        path = ROOT / f"requirements/{BUILD_ID}.{document['stage']}.json"
        path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(path.relative_to(ROOT))
        print({key: len(values) for key, values in document["targets"].items()})
