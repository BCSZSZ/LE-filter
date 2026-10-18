"""Rebuild Ice Heartseeker from the player's frozen revision, offline."""
from copy import deepcopy
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tool"))
from engine import CATALOG, MANIFEST, extract, inspect_rule
from requirements import read_document

SOURCE = ROOT / "sources/builds/letools-planner-al0dkyek-extracted.json"
PLAYER_SOURCE = ROOT / "sources/builds/ice-heartseeker-player-2026-10-18.xml"
PLAYER_SHA256 = "8facbd4310b104d7b3b447565faba68aa5d808cb534de3ad09375559f601eb61"
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


def build_planner_documents():
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


def build_documents():
    planner, leveling = build_planner_documents()
    raw = PLAYER_SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != PLAYER_SHA256:
        raise ValueError("玩家修订XML与冻结哈希不符。")
    root = ET.fromstring(raw)
    rules = root.find("rules")
    # Recover only this BD's explicit target layers. Common pools and thresholds
    # belong to the engine, and must not become BD targets or leveling goals.
    rules[:] = sorted(rules, key=lambda node: int(node.findtext("Order")))
    labels = {"BD目标单T7": "equipment", "神像一普通目标": "idols",
              "祭坛一项目标": "altars", "BD暗金0LP也留": "uniques"}
    assignments = {}
    for index, node in enumerate(rules, 1):
        row = inspect_rule(node)
        assignments[str(index)] = next((category for label, category in labels.items()
                                       if row["enabled"] and row["name"].startswith(f"[主 {label}] 冰追心 ")), "")
    recovered = extract(ET.tostring(root, encoding="unicode"), assignments)
    if recovered["warnings"]:
        raise ValueError(recovered["warnings"])
    targets = {key: [] for key in planner["targets"]}
    targets["uniques"] = recovered["profile"]["uniques"]
    for category in ("equipment", "altars", "idols", "bases"):
        for item in recovered["profile"][category]:
            group = {key: deepcopy(item[key]) for key in ("type", "bases", "affixes", "pair_bases", "corrupted", "enchanted")
                     if key in item and (item[key] or key in {"bases", "affixes"})}
            group.setdefault("bases", [])
            if group.get("pair_bases") == group["bases"]:
                group.pop("pair_bases")
            previous = next((g for g in planner["targets"][category]
                             if g["type"] == group["type"] and g.get("bases", []) == group["bases"]), {})
            # Generated XML sorts IDs and cannot recover the user's UI priority.
            # Retain surviving source order; append new IDs in XML order.
            old_order = previous.get("affixes", [])
            group["affixes"] = [aid for aid in old_order if aid in group.get("affixes", [])] + [
                aid for aid in group.get("affixes", []) if aid not in old_order]
            # These references were never emitted into XML. Retain them with
            # explicit Planner provenance; they do not add matching targets.
            for field in ("corrupted", "enchanted"):
                if previous.get(field) and not group.get(field):
                    group[field] = deepcopy(previous[field])
            targets[category].append(group)
    source = {
        "name": "冰追心 · 玩家修订XML",
        "file": PLAYER_SOURCE.relative_to(ROOT).as_posix(),
        "original_filename": "LE-filter (10).xml",
        "updated": "2026-10-18",
        "sha256": PLAYER_SHA256,
        "scope": "玩家导出的冰追心终局目标完整替换；共通规则仍由原引擎生成",
        "planner_reference": planner["source"],
        "video_reference": {
            "url": "https://www.bilibili.com/video/BV1oupP6wEcS/",
            "verification": "仅取得页面元数据与简介，未核验视频中的逐条推荐；以玩家修订为准",
        },
        "warnings": [
            "XML不保存界面词条优先级；保留原列表中仍选中的词条顺序，新词条按XML顺序追加。",
            "XML未编码的腐化、附魔及固定属性参考沿用冻结Planner，并非本次XML确认的推荐。",
            "未从终局或共通拆解池推断练级目标；练级需求独立留空。",
        ],
    }
    endgame = {**planner, "targets": targets, "source": source}
    read_document(endgame)
    return endgame, leveling


if __name__ == "__main__":
    for document in build_documents():
        path = ROOT / f"requirements/{BUILD_ID}.{document['stage']}.json"
        path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(path.relative_to(ROOT))
        print({key: len(values) for key, values in document["targets"].items()})
