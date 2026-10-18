"""Build the independent Heartseeker Shuriken template from frozen XML."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tool"))
from engine import empty_leveling, extract, inspect_rule
from requirements import write_document
from letools import merge_targets

BUILD_ID = "heartseeker-shuriken-marksman"
SOURCE = ROOT / "sources/builds/maxroll-shuriken-marksman-very-strict.xml"
SOURCE_SHA256 = "9a79e7351c3a114e746839a4fd8e605cfc8ffc53ab59cfbe1bf17e0ab4312cdf"


def build_xml_documents():
    raw = SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError("追心手里剑来源XML与冻结哈希不符。")
    xml = raw.decode("utf-8-sig")
    root = ET.fromstring(xml)
    rows = [inspect_rule(node) for node in root.find("rules")]
    data = extract(xml)
    if data["warnings"]:
        raise ValueError(data["warnings"])
    profile = data["profile"]
    # The importer determines scope and ordinary/reference categories. Keep the
    # original XML list order for the player's editable affix priority.
    for category in ("equipment", "altars", "idols"):
        for group in profile[category]:
            for field in ("affixes", "corrupted", "enchanted"):
                pool = set(group[field])
                group[field] = list(dict.fromkeys(aid for ref in group["sources"]
                                                 for affixes in rows[ref["x"] - 1]["affix_pools"]
                                                 for aid in affixes if aid in pool))
    selected = [{"x": r["x"], "name": r["name"], "category": r["category"], "gate": r["gate"]}
                for r in data["rules"] if r["category"]]
    source = {
        "name": "追心手里剑 · 玩家提供的 Shuriken Marksman XML",
        "file": SOURCE.relative_to(ROOT).as_posix(),
        "sha256": SOURCE_SHA256,
        "extracted_on": "2026-10-18",
        "original_name": root.findtext("name"),
        "original_description": root.findtext("description"),
        "scope": "已启用的BD专属暗金、部位T7、神像及祭坛目标；独立于冰追心",
        "selected_rules": selected,
        "warnings": [
            "来源Very Strict只提供目标；LP、阶数、未腐化、颜色、声音及排序门槛由工作台现行基底决定。",
            "普通神像仅计0／5类，附魔4与腐化6另存参考；一项与两项目标的底材范围保留来源差异。",
            "装备词条沿用XML列表顺序，来源未声明需求重要程度，可在个人方案调整。",
            "通用Alt Leveling规则未提供本BD独立练级路线，练级目标留空。",
        ],
    }
    build = {"id": BUILD_ID, "name": "追心手里剑",
             "profiles": {"endgame": profile, "leveling": empty_leveling()},
             "requirement_sources": {"endgame": source}}
    build["requirement_sources"]["leveling"] = {
        key: deepcopy(source[key]) for key in ("name", "file", "sha256", "extracted_on")}
    build["requirement_sources"]["leveling"].update(
        scope="未提供本BD独立练级目标，留空待玩家补充",
        warnings=["未从终局目标或通用Alt Leveling规则推断本BD练级需求。"])
    return tuple(write_document(build, stage) for stage in ("endgame", "leveling"))


def build_documents():
    from extract_shuriken_profiles import extracted_document
    endgame, leveling = build_xml_documents()
    profiles = extracted_document()
    endgame["targets"] = merge_targets(endgame["targets"], profiles["targets"])
    endgame["source"] = {**profiles["source"], "name": "追心手里剑 · 原XML与四个天梯角色并集",
                         "xml_reference": endgame["source"],
                         "scope": "原Very Strict模板目标与玩家指定四个角色当前配装的并集；练级独立留空"}
    return endgame, leveling


if __name__ == "__main__":
    for document in build_documents():
        path = ROOT / f"requirements/{BUILD_ID}.{document['stage']}.json"
        path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(path.relative_to(ROOT))
        print({key: len(values) for key, values in document["targets"].items()})
