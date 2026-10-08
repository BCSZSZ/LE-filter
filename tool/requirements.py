"""Common target-only document, shared by guide and filter imports."""
from copy import deepcopy

from engine import CATALOG, empty_profile, to_leveling, validate_leveling, validate_profile

FORMAT = "le-filter-requirements"
CATEGORIES = ("uniques", "equipment", "altars", "idols", "bases")
GROUP_FIELDS = {"type", "bases", "affixes", "pair_bases", "corrupted", "enchanted"}
BASE_FIELDS = {"type", "bases", "preferred_bases"}


def read_document(document):
    if not isinstance(document, dict) or document.get("format") != FORMAT or document.get("version") != 1:
        raise ValueError("请导入version=1的BD需求JSON；整套工具配置请用“载入配置”。")
    for key in ("id", "name"):
        if not isinstance(document.get(key), str) or not document[key].strip():
            raise ValueError(f"需求JSON缺少{key}。")
    if document.get("stage") not in {"endgame", "leveling"}:
        raise ValueError("stage必须为endgame或leveling。")
    targets = document["targets"]
    leveling = document["stage"] == "leveling"
    compact = leveling and isinstance(targets, dict) and set(targets) == {"affixes", "bases"}
    if not compact and (not isinstance(targets, dict) or set(targets) != set(CATEGORIES)):
        raise ValueError("终局targets填写五类需求；练级targets只填写affixes和bases。")
    profile = empty_profile()
    if compact:
        profile = deepcopy(targets)
        validate_leveling(profile)
    for category in (() if compact else CATEGORIES):
        if not isinstance(targets[category], list):
            raise ValueError(f"{category}必须为列表。")
        profile[category] = deepcopy(targets[category])
        if category == "uniques":
            if any(type(uid) is not int for uid in profile[category]):
                raise ValueError("暗金ID必须为整数。")
            continue
        for group in profile[category]:
            fields = BASE_FIELDS if category == "bases" else GROUP_FIELDS
            if not isinstance(group, dict) or set(group) - fields or not isinstance(group.get("type"), str):
                raise ValueError(f"{category}分组格式不正确。")
            if category != "idols" and "pair_bases" in group:
                raise ValueError("pair_bases只用于神像的两项目标底材范围。")
            for key in ("bases", "affixes", "corrupted", "enchanted"):
                group.setdefault(key, [])
            for key in fields - {"type"}:
                values = group.get(key, [])
                if not isinstance(values, list) or any(type(v) is not int for v in values):
                    raise ValueError(f"{category}.{key}必须为整数ID列表。")
            for key in ("corrupted", "enchanted"):
                special = 6 if key == "corrupted" else 4
                if any(CATALOG["affixes"].get(str(aid), {}).get("special") != special for aid in group[key]):
                    raise ValueError(f"{category}.{key}中存在未知或分类不符的词缀。")
    if not compact:
        validate_profile(profile)
        if leveling:
            profile = to_leveling(profile)
            validate_leveling(profile)
    source = document.get("source", {})
    if not isinstance(source, dict):
        raise ValueError("source必须为对象。")
    if not isinstance(source.get("warnings", []), list) or any(not isinstance(w, str) for w in source.get("warnings", [])):
        raise ValueError("source.warnings必须为文字列表。")
    source = deepcopy(source)
    if leveling and not compact and any(targets.values()):
        source["legacy_targets"] = deepcopy(targets)
        source.setdefault("warnings", []).append("旧练级需求已转换为词缀与底材两份列表，原五类目标保存在来源记录中。")
    return {"id": document["id"], "name": document["name"], "stage": document["stage"],
            "profile": profile, "source": source}


def write_document(build, stage):
    profile = build["profiles"][stage]
    if stage == "leveling":
        targets = to_leveling(profile)
        validate_leveling(targets)
    else:
        validate_profile(profile)
        targets = {"uniques": deepcopy(profile["uniques"])}
    for category in (() if stage == "leveling" else CATEGORIES[1:]):
        targets[category] = []
        for group in profile[category]:
            fields = BASE_FIELDS if category == "bases" else GROUP_FIELDS
            targets[category].append({key: deepcopy(value) for key, value in group.items()
                                      if key in fields and (value or key in {"type", "bases", "affixes", "pair_bases", "preferred_bases"})})
    document = {"format": FORMAT, "version": 1, "id": build["id"], "name": build["name"],
                "stage": stage, "targets": targets}
    source = build.get("requirement_sources", {}).get(stage, build.get("source", {}))
    if source:
        document["source"] = {key: deepcopy(value) for key, value in source.items() if key != "rules"}
    read_document(document)
    return document
