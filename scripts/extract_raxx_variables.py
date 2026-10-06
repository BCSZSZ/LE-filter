"""Extract Strict evidence for Raxx's editable inputs; never write a filter."""
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
XSI = "{http://www.w3.org/2001/XMLSchema-instance}"
# id, title, Raxx slots, instructional slots, editable fields, Strict evidence families
VARIABLES = [
    ("V01", "BD暗金名单", [15], [9, 10, 11], "UniqueId名单；保留原珍贵名单", ["planner"]),
    ("V02", "需要的套装名单", [16], [9, 10, 11], "UniqueId名单", ["planner"]),
    ("V03", "中低潜能名单的取舍", [13, 14], [9, 10, 11], "保留／删除哪些名字；潜能门槛不变", ["planner"]),
    ("V04", "职业隐藏", [29], [25, 26, 27, 28], "排除职业req、启用状态、是否移动位置", []),
    ("V05", "各部位BIS目标", list(range(38, 48)), list(range(30, 36)), "装备类型、目标词缀；穿戴用途的底材／遗物类型", ["tier7"]),
    ("V06", "双崇高的装备范围", [48], [36], "武器／副手类型；职业去留与V04协调", ["tier7"]),
    ("V07", "宽T7武器／副手素材", [60], [49, 51, 52, 53, 54, 56, 57], "装备类型、宽词缀池；不加制作素材底材限制", ["tier7"]),
    ("V08", "宽T7护甲／饰品素材", [61], [49, 51, 56, 57], "宽词缀池；不是将BIS池直接复制到宽池", ["tier7", "class_t7"]),
    ("V09", "Havoc素材", [62], [58, 59], "装备类型、第一份宽T7池、第二份好词缀池", ["havoc"]),
    ("V10", "T6目标素材", [63, 64], [49, 50, 51, 52, 53, 54, 55], "装备类型与更挑选的词缀池；保留84级上限", ["tier6"]),
    ("V11", "实验词缀", [68, 69], [65, 66, 67], "R68是否关闭；R69的目标词缀与是否启用", ["experimental"]),
    ("V12", "冠军词缀", [70], [65, 66], "目标词缀与是否启用；默认关闭", ["champion"]),
    ("V13", "早期腐化属性", [75], [71, 72], "想保留的腐化词缀；保留59级上限", ["tier7", "tier6", "idol_bis", "idol_single", "altar"]),
    ("V14", "升华底材与阵营", [81], [79, 80], "装备类型／底材、是否采用、CoF条件是否保留", ["ascend"]),
    ("V15", "定向收集底材", [82], [78], "装备类型和具体subtype；不导入Strict双词缀门槛", ["rare_base", "crafting_base"]),
    ("V16", "当前紧缺碎片", [83], [77, 78], "紧缺词缀列表与是否采用，必须结合库存", ["shatter"]),
    ("V17", "职业碎片", list(range(84, 89)), [76, 77], "保留哪些职业收集；需要哪些职业词缀", ["class_shatter", "class_t7"]),
    ("V18", "进攻／防御碎片", [89, 90], [76, 77], "所需词缀与是否采用，保留T5门槛", ["shatter", "class_shatter"]),
    ("V19", "BIS神像", list(range(99, 127)), list(range(91, 98)), "按BD、尺寸、底材分组；普通计数与腐化参考分开；Flay分1／2项", ["idol_bis", "idol_single"]),
    ("V20", "神像祭坛", [127], [98], "需要的祭坛底材和词缀；至少1项、阶数不限", ["altar"]),
    ("V21", "过渡神像", [128, 129], [91, 93], "加入需要的职业词缀；保留数量2／1与89／74级上限", ["idol_bis", "idol_single"]),
    ("V22", "开荒武器／副手及优选底材", list(range(136, 146)), list(range(130, 134)), "开荒类型、具体底材、是否采用；终局数据仅供参考", ["tier7", "rare_base"]),
    ("V23", "早期武器／副手分支", [152, 153, 154, 157, 158, 159], [130, 131, 132, 133], "按开荒玩法选择分支／类型；终局装备不能证明开荒路线", ["tier7"]),
    ("V24", "早期兜底与进度选择", [73, 74, 75], [71, 72], "可选提前关闭或降低角色等级上限；默认沿用原版", []),
]
NOTES = {
    "V01": "Strict只提供目标名字。补入R15后采用Raxx的无潜能门槛保护，不新建BD的1／2／3LP层；不删除原珍贵物品。",
    "V02": "只按冻结数据库的物品类型分开套装；导出名单里的SET字样不能证明每个名字都是套装。",
    "V03": "Strict能证明需要哪些物品，不能证明其余412项都不要。保留原LP2／WW17及LP1／WW14门槛。",
    "V04": "Strict未给出玩家永远不玩的职业。不能自动将主套路之外的职业排除；原R29关闭。",
    "V05": "部位池可作为BIS候选。武器／副手手位、直接穿戴底材仍需确认；不从暗金目标名字反推制作底材。",
    "V06": "提取两BD实际出现的装备类型供裁剪。双崇高仍按原至少两条T6，不导入Strict的T7＋T6／双T7门槛。",
    "V07": "Strict给出的部位目标池较窄，不足以替代Raxx近乎全部可用词缀的宽T7素材池。类型可确定，宽池取舍待审。",
    "V08": "职业T7目标可补充情报，不能把整个R61改成Strict的Class Specific规则。宽T7池仍需审阅。",
    "V09": "分别提取好词缀池与通用T7池，不把1156项全池当作BD好词缀。保留Raxx两份词缀条件，不新增FP1／52或未封印门槛。",
    "V10": "取Strict的类型／词缀，保留Raxx角色0–84级、目标T6及以上的策略。Strict的全等级收集不转移。",
    "V11": "找到实验目标不等于本轮已启用R69。R68原本保留所有预选的稀有崇高实验物品，可选择关闭；不默认缩成BD的两项。两规则没有单独的实验词缀T6／T7门槛。",
    "V12": "关闭的通用Champion规则只能作为参考，不能证明两个BD需要全部冠军词缀。",
    "V13": "仅提取目标池里类型6的腐化属性。记录Strict中OnlyUncorrupted与腐化目标并存的矛盾；不因此新增全等级腐化分支。",
    "V14": "目标暗金名单不能证明玩家想用升华符文获得它们。Strict升华规则关闭且类型为空，必须另定升华用途。",
    "V15": "Rare Strict给出定向底材，Eternal Gauntlets是通用制作底材参考，不宣称BD必须。来源中的词缀／FP／稀有度不附加到R82。",
    "V16": "Strict的Shatter池是碎片候选，不是玩家真实紧缺库存。R83空池必须填写或明确不采用。",
    "V17": "原五职业规则T4、MAGIC／RARE／EXALTED不变。来源只证明词缀候选；是否保留整职业广池需审阅。",
    "V18": "Strict不能完整决定词缀应归进攻还是防御，也不能决定当前缺口。保留原R89／90的T5门槛。",
    "V19": "按冻结类型资料将普通词缀与腐化词缀（specialAffixType=6）分开，腐化词缀不参与普通目标计数，原始混合池完整保留。Flay按用户本轮审阅记录1项候选／2项组合毕业两层，均保留Weaver与Lagon底材；这是用户定制，不冒充Strict原规则。其他BD配对仍待审阅。Large Omen跨职业底材入口仍标为待判别。",
    "V20": "Strict的祭坛池与底材分开记录。R127原有数量1、advanced=false，实际不设阶数门槛；不导入Strict的T6／T7、前后缀合计或双崇高层。不同底材对应不同词缀时保留分组。",
    "V21": "普通词缀与腐化参考分开，仅普通词缀供R128／129补充与计数；保留原广泛过渡池与等级退出。Flay用户指定的1／2项层另记在V19，其他BD不自动新增常驻层。",
    "V22": "Strict针对强化时间线起步。Rare Strict底材及终局类型不能直接当开荒BIS；缺开荒阶段证据，原预填仍列供核对。",
    "V23": "只能识别终局用到哪些类型。开荒可能采用不同技能与武器，未确认前不自动关闭原早期分支。",
    "V24": "Strict不包含个人进度偏好。原暗金／崇高／腐化兜底等级分别0–79／0–59／0–59，作为本轮基准。",
}


def read_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8-sig"))


def split_affixes(ids, special_types):
    """Classify by database type, never by names or a hard-coded affix list."""
    ids = sorted(set(ids))
    return {"non_corrupted_affix_ids": [i for i in ids if special_types[str(i)] != 6],
            "corrupted_affix_ids": [i for i in ids if special_types[str(i)] == 6]}


def value(node):
    if node.get(XSI + "nil") == "true":
        return None
    if not len(node):
        return (node.text or "").strip()
    if all(c.tag in {"int", "EquipmentType", "FactionID"} for c in node):
        return [value(c) for c in node]
    groups = {}
    for c in node:
        groups.setdefault(c.tag, []).append(value(c))
    return {k: v if len(v) > 1 else v[0] for k, v in groups.items()}


def family(name):
    if name == "Uniques & Sets From Planner (Optional: Add More)":
        return "planner"
    if name == "Tier 7 - Class Specific Affixes":
        return "class_t7"
    if re.fullmatch(r"Tier [67] - .+", name):
        return "tier" + name[5]
    if name.startswith("Strict - ") and name != "Strict - Weaver Idols":
        return "idol_bis"
    if name.startswith("1 Affix - "):
        return "idol_single"
    if name in {"Strict - Weaver Idols", "Reflect Idols (Alt Leveling)", "Unique Idols"}:
        return "generic_idol"
    if name.startswith("Rare Strict "):
        return "rare_base"
    if name == "Tier 7 Eternal Gauntlets":
        return "crafting_base"
    if name == "Tier 7 Highly Craftable Items (52+ FP)":
        return "maxroll_only_crafting"
    if name in {"Wanted Affix & Tier 7 (Rune of Havoc)", "Wanted Experimental & Tier 7 (Rune of Havoc)"}:
        return "havoc"
    if name == "Wanted Experimental Affixes":
        return "experimental"
    if name == "Shatter / Removal (Edit Affixes)":
        return "shatter"
    if name == "Shatter / Removal (Class Specific Affixes)":
        return "class_shatter"
    if name.startswith("Generic Good Altars"):
        return "generic_altar"
    if "Altar" in name and name != "All Altars":
        return "altar"
    if name == "CoF Rune of Ascendance (Select Item Type)":
        return "ascend"
    if name == "Champion Affixes (40)":
        return "champion"
    return "other"


def inspect_rule(node):
    conditions = [{"kind": c.get(XSI + "type"), "fields": value(c)} for c in node.find("conditions")]
    pools = [[int(e.text) for e in c.findall("affixes/int")] for c in node.find("conditions") if c.get(XSI + "type") == "AffixCondition"]
    subtype = next((c for c in node.find("conditions") if c.get(XSI + "type") == "SubTypeCondition"), None)
    return {"enabled": node.findtext("isEnabled") == "true", "action": node.findtext("type"), "name": node.findtext("nameOverride") or "",
            "types": [e.text for e in subtype.findall("type/EquipmentType")] if subtype is not None else [],
            "subtypes": [int(e.text) for e in subtype.findall("subTypes/int")] if subtype is not None else [],
            "affix_pools": pools, "unique_ids": sorted({int(e.text) for e in node.findall("conditions/Condition/Uniques/UniqueId")}), "conditions": conditions}


def gate_text(row):
    parts = []
    for c in row["conditions"]:
        f, kind = c["fields"], c["kind"]
        if kind == "AffixCondition":
            part = f"至少{f['minOnTheSameItem']}项"
            if f["advanced"] == "true":
                ops = {"ANY": "不限", "EQUAL": "=", "MORE_OR_EQUAL": "≥", "MORE": ">"}
                for label, field, number in [("单项T", "comparsion", "comparsionValue"), ("合计T", "combinedComparsion", "combinedComparsionValue")]:
                    part += "，" + label + ops[f[field]] + (f[number] if f[field] != "ANY" else "")
            else:
                part += "，阶数不限（advanced=false）"
            parts.append(part)
        elif kind == "CharacterLevelCondition":
            parts.append(f"角色{f['minimumLvl']}–{f['maximumLvl']}级（含上限）")
        elif kind == "RarityCondition":
            parts.append("稀有度=" + f["rarity"])
        elif kind == "CorruptionCondition":
            parts.append("未腐化" if f["Corruption"] == "OnlyUncorrupted" else "腐化")
        elif kind == "PotentialCondition":
            parts.append("潜能配置=" + "/".join(k + ":" + v for k, v in f.items() if v is not None and v != ""))
        elif kind == "FactionCondition":
            parts.append("原阵营条件=" + str(f))
    return "；".join(parts) or "没有额外阶数／等级门槛"


def main():
    protected = sorted([*ROOT.glob("filters/*.xml"), ROOT / "sources/Raxx's S5 Ultimate Filter v1.0.txt", *ROOT.glob("sources/builds/maxroll-*-strict.xml")])
    hashes_before = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    manifest, strict = read_json("sources/manifest.json"), read_json("sources/builds/maxroll-strict-manifest.json")
    def frozen(spec):
        path = spec.get("file", spec.get("local_path"))
        raw = (ROOT / path).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == spec["sha256"], path
        return ET.fromstring(raw)
    base_nodes = sorted(frozen(manifest["baseline"]).find("rules"), key=lambda r: int(r.findtext("Order")))
    base = {i: inspect_rule(r) for i, r in enumerate(base_nodes, 1)}
    ref = read_json("sources/game-reference.json")
    supplement = read_json(strict["reference_supplement"])
    for section in ["affixes", "uniques"]:
        ref[section].update(supplement[section])
    ref["subtypes"].update(read_json("sources/builds/review-reference.json")["subtypes"])
    flags = read_json("sources/builds/strict-variable-reference.json")
    assert flags["source_db"] == ref["source_urls"]["db"]
    def names(section, ids):
        return "、".join(ref[section][str(i)]["zh"] + f"（{i}）" for i in ids) or "无"
    def scope(row):
        types = "、".join(ref["equipment_names"][t]["zh"] + ("（" + t.split("_")[1].replace("x", "×") + "）" if t.startswith("IDOL_") and t != "IDOL_ALTAR" else "") for t in row["types"]) or "未限定类型"
        bases = "、".join(ref["subtypes"][t + ":" + str(i)]["zh"] for t in row["types"] for i in row["subtypes"])
        return types + ("；底材=" + bases if bases else "；底材不限／未选")
    def destinations(vid, slots, row):
        if vid == "V17":
            ids = set(i for pool in row["affix_pools"] for i in pool)
            return [n for n in slots if ids & set(base[n]["affix_pools"][0])]
        if vid not in {"V05", "V19", "V22", "V23"}:
            return slots
        found = []
        for n in slots:
            original = base[n]
            if n in {38, 39, 136, 137} and not set(row["types"]) & set(base[60]["types"]):
                continue
            if n in {39, 137} and all(t.startswith("TWO_HANDED") for t in row["types"]):
                continue
            if original["types"] and not set(original["types"]) & set(row["types"]):
                continue
            if vid == "V19" and original["subtypes"] and row["subtypes"] and not set(original["subtypes"]) & set(row["subtypes"]):
                continue
            found.append(n)
        return found
    evidence = []
    for slug, spec in strict["inputs"].items():
        for pos, node in enumerate(frozen(spec).find("rules"), 1):
            row = inspect_rule(node)
            row.update(build=slug, x=pos, family=family(row["name"]))
            evidence.append(row)
    variables = []
    for vid, title, slots, instructions, fields, families in VARIABLES:
        matches = [r for r in evidence if r["family"] in families]
        if vid in {"V07", "V23"}:
            matches = [r for r in matches if set(r["types"]) & set(base[60]["types"])]
        if vid == "V08":
            matches = [r for r in matches if r["family"] == "class_t7" or set(r["types"]) & set(base[61]["types"])]
        candidates = []
        for row in matches:
            ids = sorted(set(i for pool in row["affix_pools"] for i in pool))
            if vid == "V09":
                ids = sorted(row["affix_pools"][0])
            elif vid in {"V06", "V15", "V22", "V23"}:
                ids = []
            if vid == "V13":
                ids = split_affixes(ids, flags["special_affix_type"])["corrupted_affix_ids"]
                if not ids:
                    continue
            selected = row["unique_ids"]
            if vid in {"V01", "V02"}:
                selected = [i for i in selected if flags["is_set_item"][str(i)] == (vid == "V02")]
            target_slots = destinations(vid, slots, row)
            candidates.append({"build": row["build"], "x": row["x"], "enabled_in_source": row["enabled"], "candidate_raxx_slots": target_slots, "mapping_requires_review": vid in {"V05", "V19"} and len(target_slots) > 1, "types": row["types"], "subtypes": row["subtypes"], "affix_ids": ids, "affix_pools": row["affix_pools"] if vid not in {"V06", "V15", "V22", "V23"} else [], "unique_ids": selected})
            if vid in {"V19", "V21"}:
                classified = split_affixes(ids, flags["special_affix_type"])
                candidates[-1]["corrupted_affix_ids"] = classified["corrupted_affix_ids"]
                candidates[-1]["affix_ids"] = classified["non_corrupted_affix_ids"]
                candidates[-1]["count_scope"] = "ordinary_target_affixes_only; corruption_status_unrestricted"
        variables.append({"id": vid, "title": title, "raxx_slots": slots, "instruction_slots": instructions, "editable_fields": fields,
                          "instruction_texts": {str(n): base[n]["name"] for n in instructions},
                          "strict_families": families, "baseline_defaults": {str(n): base[n] for n in slots}, "evidence": candidates,
                          "status": "有启用来源候选，待审阅" if any(c["enabled_in_source"] for c in candidates) else "仅关闭来源参考，不自动采用" if candidates else "Strict未给出可直接填写的值", "interpretation": NOTES[vid]})
        if vid == "V02":
            variables[-1]["status"] = "两份目标名单均未发现套装；保留R16原预设"
        elif vid in {"V07", "V08"}:
            variables[-1]["status"] = "类型／目标已提取；宽素材池不能由Strict窄池直接决定"
        elif vid in {"V22", "V23"}:
            variables[-1]["status"] = "仅有终局类型／底材参考；开荒证据缺失"
        elif vid in {"V16", "V18"}:
            variables[-1]["status"] = "碎片候选已提取；实际库存缺口未提供"
        elif vid == "V19":
            variables[-1]["status"] = "Flay四层已按用户要求记录；其他神像配对仍待审阅"
    for row in evidence:
        row["variable_ids"] = [v["id"] for v in variables if any(c["build"] == row["build"] and c["x"] == row["x"] for c in v["evidence"])]
    idol_candidates = next(v["evidence"] for v in variables if v["id"] == "V19")
    idol_classification = {"stage": "Strict idol affix classification only; no output filter", "strict_inputs": strict["inputs"],
                           "metadata_file": "sources/builds/strict-variable-reference.json", "metadata_source": flags["source_db"],
                           "method": "Affix IDs from Strict; corrupted iff database specialAffixType=6; guide not used",
                           "rules": [{"build": c["build"], "x": c["x"], "enabled_in_source": c["enabled_in_source"],
                                      "types": c["types"], "subtypes": c["subtypes"],
                                      "source_affix_ids": sorted({i for pool in c["affix_pools"] for i in pool}),
                                      "non_corrupted_affix_ids": c["affix_ids"], "corrupted_affix_ids": c["corrupted_affix_ids"]} for c in idol_candidates]}
    assert all(set(c["source_affix_ids"]) == set(c["non_corrupted_affix_ids"]) | set(c["corrupted_affix_ids"]) for c in idol_classification["rules"])
    idol_layers = []
    for c in idol_candidates:
        source = next(r for r in evidence if r["build"] == c["build"] and r["x"] == c["x"])
        if c["build"] != "flay-mana-lich" or source["family"] != "idol_single" or not c["enabled_in_source"]:
            continue
        for count in [2, 1]:  # Stronger layer must precede its one-affix fallback.
            idol_layers.append({"build": c["build"], "types": c["types"], "subtypes": c["subtypes"], "affix_ids": c["affix_ids"],
                                "min_matching_ordinary_affixes": count, "advanced": False, "character_level_limit": None,
                                "required_affix_ids": [], "corruption_status": "unrestricted", "corrupted_affixes_counted": False,
                                "tier": "组合毕业" if count == 2 else "收集候选", "sound_role": "graduation" if count == 2 else "ordinary",
                                "source_x": [e["x"] for e in idol_candidates if e["build"] == c["build"] and e["types"] == c["types"]],
                                "policy_source": "User review on 2026-10-06; not an unchanged Strict predicate"})
    unique = {s: sorted({i for r in evidence if r["build"] == s and r["family"] == "planner" and r["enabled"] for i in r["unique_ids"]}) for s in strict["inputs"]}
    union = sorted(set().union(*map(set, unique.values())))
    missing = sorted(set(union) - set(base[15]["unique_ids"]))
    def tier_map(tier):
        return {(r["build"], tuple(r["types"]), tuple(r["subtypes"])): sorted(r["affix_pools"][0]) for r in evidence if r["family"] == tier and r["enabled"]}
    tier_pools_equal = tier_map("tier6") == tier_map("tier7")
    blue = {n for n, r in base.items() if base_nodes[n - 1].findtext("color") == "12" and not r["enabled"]}
    fixed_instructions = {1, 2, 3, 4, 5, 6, 7, 17, 18}
    covered = fixed_instructions | {n for v in variables for n in v["instruction_slots"]}
    assert covered == blue and len(blue) == 56, (blue - covered, covered - blue)
    assert len(evidence) == 271 and len(union) == 20
    assert sum(r["family"] in {"tier6", "tier7"} and r["enabled"] for r in evidence) == 38
    assert all(len(r["affix_pools"]) == 2 and len(r["affix_pools"][1]) == 1156 for r in evidence if r["family"] == "havoc")
    assert all(not r["variable_ids"] for r in evidence if r["family"] in {"generic_idol", "generic_altar", "maxroll_only_crafting"})
    assert all(len(c["affix_ids"]) < 1156 for v in variables for c in v["evidence"])
    assert all(c["candidate_raxx_slots"] for v in variables for c in v["evidence"]), "Every candidate needs a Raxx input destination"
    assert len(idol_layers) == 4 and [c["affix_ids"] for c in idol_layers] == [[843, 854], [843, 854], [876, 886], [876, 886]]
    assert all(flags["special_affix_type"][str(i)] != 6 for v in variables if v["id"] in {"V19", "V21"} for c in v["evidence"] for i in c["affix_ids"])
    result = {"stage": "Raxx variables and Strict evidence only; no output filter", "baseline": manifest["baseline"], "strict_inputs": strict["inputs"],
              "reference_files_sha256": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in ["sources/game-reference.json", strict["reference_supplement"], "sources/builds/review-reference.json", "sources/builds/strict-variable-reference.json"]},
              "roles": {"main": "flay-mana-lich", "secondary": "skeleton-necromancer", "shared": "main", "role_assignment_is_default": True},
              "variables": variables, "strict_rules": evidence, "target_ids": unique, "target_union": union, "r15_missing_targets": missing, "tier6_tier7_target_pools_equal": tier_pools_equal,
              "user_reviewed_flay_idol_layers": idol_layers,
              "fixed_instruction_slots": sorted(fixed_instructions), "unmodified_files_sha256": hashes_before}
    catalog = [
        "# Raxx原版：需要填写或审阅的变量", "",
        "由extract_raxx_variables.py读取冻结原版后生成。R编号=原版Order+1。本表只登记变量和原始默认值，没有给出最终filter。", "",
        "## 本轮保留的原版收集策略", "",
        "1. 稀有共通暗金：R15原名单143项保留，0LP也留。",
        "2. BD关联暗金：把目标名字补入同一个R15名单，0LP也留；不新增BD独立LP分层。",
        "3. 高潜能暗金：R12不限制名字，LP3／WW20起；R13／14仍用原名单与LP2／WW17、LP1／WW14门槛。",
        "4. 传奇、套装与资源：R8全部传奇、R16需要的套装、R19–24资源沿用原版。",
        "5. 装备：BIS目标与宽T7制作素材分开；双崇高至少两条T6；T6收集在85级退出。",
        "6. 神像：BIS默认至少两项；过渡神像分别90／75级退出；祭坛R127至少一项、阶数不限。",
        "7. 早期腐化：R75只收已选腐化属性、角色0–59级；不添加全等级宽松腐化分支。",
        "8. R37的T8池与R163最终隐藏沿用原版，本轮不扩池或增加规则。", "",
        "## 变量总表", "", "| 变量 | 填写内容 | R入口 | Strict能提供的情报 |", "|---|---|---|",
        *[f"| {v['id']} {v['title']} | {v['editable_fields']} | {', '.join('R'+str(n) for n in v['raxx_slots'])} | {', '.join(v['strict_families']) or '需要玩家信息'} |" for v in variables], "",
        "## 每个入口的原值与保留门槛", "",
    ]
    review = ["# Strict提取结果：Raxx变量审阅结论", "", "从两份Strict提取BD情报，再匹配Raxx填空入口；另记录用户审阅确定的Flay神像定制。没有生成或更新最终XML。", "", "本次默认Flay为主、Skeleton为副；共享按主处理，两者同等收集。角色身份只作为情报归属，颜色尚未写入filter。", "", "## 先审阅的结论", "", f"1. 稀有共通暗金：保留R15原143项。", f"2. BD关联暗金：两份Strict各11种，共20种（共享253／416）；原R15缺{len(missing)}种：{names('uniques', missing)}。其余目标已在R15，无需重复加入。", "3. 本轮没有增加正文中的5种替代暗金，也没有导入Planner JSON中的精确神像组合；这些不是Strict直接导出的情报，另列后续核对。", "4. 19份部位T7池作为BIS候选，19份T6池作为T6候选；Raxx宽T7素材策略单独审阅。", "5. 神像普通与腐化词缀已分开，腐化不参与普通目标计数；Flay按用户审阅记录4条1／2项候选层，其他配对不自动推断。", "6. Strict的LP分层、FP52、全等级T6、通用Weaver／反伤、祭坛分层不直接移植；Flay单词缀层来自用户明确要求。", "", "以下变量与[变量总表](RAXX_VARIABLES.md)对应，X编号为各Strict文件的XML物理位置。原门槛见变量总表；来源门槛仅作为证据，不代表采用。", ""]
    lookup = {(r["build"], r["x"]): r for r in evidence}
    for v in variables:
        catalog += [f"### {v['id']}｜{v['title']}", "", "可填字段：" + v["editable_fields"] + "。", "", "处理原则：" + v["interpretation"], ""]
        for n, row in v["baseline_defaults"].items():
            pools = "/".join(names("affixes", p) if 0 < len(p) <= 15 else str(len(p)) + "项" for p in row["affix_pools"])
            catalog.append(f"- R{n}（{'启用' if row['enabled'] else '关闭'}）：{scope(row)}；词缀池={pools or '无'}；名字名单={len(row['unique_ids'])}项；{gate_text(row)}。")
        catalog.append("")
        vid = v["id"]
        review += [f'<a id="{vid.lower()}"></a>', "", f"## {vid}｜{v['title']}", "", "结论状态：" + v["status"] + "。", "", v["interpretation"], ""]
        if vid == "V01":
            review += ["| 目标物品 | 情报归属 | 原R15状态 |", "|---|---|---|"]
            for i in union:
                owners = [s for s in unique if i in unique[s]]
                role = "共享，按主处理" if len(owners) == 2 else "主Flay" if owners[0] == "flay-mana-lich" else "副Skeleton"
                review.append(f"| {names('uniques', [i])} | {role} | {'已在名单' if i in base[15]['unique_ids'] else '需要追加'} |")
            review += ["", f"本轮候选填法：保留原143项，追加{len(missing)}项后名单共{len(set(base[15]['unique_ids']) | set(union))}项。来源为Flay X121与Skeleton X132；这是情报结论，没有写入XML。", ""]
            continue
        if vid in {"V02", "V03"}:
            review += ["两份主名单中的20项全部被冻结类型资料标为暗金，未发现BD套装目标，R16原21项继续保留。" if vid == "V02" else "本轮无依据裁剪原412项。20种BD目标已由V01的无潜能门槛名单保护，不必再增加潜能分层。", ""]
            continue
        if vid in {"V06", "V07", "V08", "V22", "V23"}:
            for slug in ["flay-mana-lich", "skeleton-necromancer"]:
                candidates = [c for c in v["evidence"] if c["build"] == slug and c["enabled_in_source"]]
                types = sorted({t for c in candidates for t in c["types"]})
                review.append("- " + strict["inputs"][slug]["name"] + "可证明的终局类型：" + "、".join(ref["equipment_names"][t]["zh"] for t in types) + "。")
            review += ["", "具体目标词缀见[V05](#v05)；上述类型只表示情报范围。", ""]
            if vid in {"V07", "V08"}:
                original = set(base[v["raxx_slots"][0]]["affix_pools"][0])
                wanted = {i for c in v["evidence"] if c["enabled_in_source"] for i in c["affix_ids"]}
                review += [f"原宽池有{len(original)}项；Strict已知目标中，原宽池未包含：{names('affixes', sorted(wanted - original))}。这些是补充情报，不能据此删除宽池的其余可用属性。", ""]
            continue
        if vid == "V10" and tier_pools_equal:
            review += ["程序逐部位核对：19份T6池与对应19份T7池的类型、底材和词缀列表完全相同，具体候选复用[V05](#v05)。Raxx两层用途不同：T6是挑选目标，宽T7是制作储备，不能因此合成同一窄池。", "", "T6来源定位：", ""]
            for slug in ["flay-mana-lich", "skeleton-necromancer"]:
                review.append("- " + strict["inputs"][slug]["name"] + "：" + "、".join(scope(c).split("；")[0] + f" X{c['x']}" for c in v["evidence"] if c["build"] == slug) + "。")
            review += ["", "原R63／64的角色0–84级条件继续作为基准，不采用Strict的全等级拾取。", ""]
            continue
        if vid == "V21":
            for n in v["raxx_slots"]:
                original = set(base[n]["affix_pools"][0])
                wanted = {i for c in v["evidence"] if c["enabled_in_source"] for i in c["affix_ids"]}
                review.append(f"- R{n}原预填池未包含的目标情报：{names('affixes', sorted(wanted - original))}。这些是可考虑补充的缺项，不替换原通用池。")
            review += ["", "每个BD、尺寸及底材关系见[V19](#v19)，仍按原数量2／1与角色0–89／0–74级退出。", ""]
            continue
        if vid == "V19":
            review += ["### Flay：用户审阅指定的候选层", "", "两项层优先于同底材的一项层，均advanced=false、不限阶数。毕业表示两个普通目标齐全，不表示数值满roll。声音只记录两种不同用途，尚未选择具体游戏音效。", "", "| 类型／底材 | 普通目标池 | 至少命中 | 提示层 |", "|---|---|---|---|"]
            for c in idol_layers:
                review.append(f"| {scope(c)} | {names('affixes', c['affix_ids'])} | {c['min_matching_ordinary_affixes']}项 | {c['tier']}；{'独立毕业声' if c['sound_role'] == 'graduation' else '普通提示'} |")
            review += ["", "这些层与Strict原规则有两点明确差别：腐化ID不凑普通目标数量；两项层也保留用户指定的Lagon底材。厚实一项层会保留只有886的神像，这是候选而非必有点燃。若要求876必有，可用独立词缀条件表达，尚未静默改成这个更严版本。", "", "普通／腐化分离已自动化，ID来自Strict、类别由词库查得，无需攻略；见[独立自动分类结果](STRICT_IDOL_CLASSIFICATION.md)。机制、攻略意图与必须／可选条件见[Flay神像审阅](FLAY_IDOL_REVIEW.md)。下面保留源规则对照，最后一列门槛针对源混合池，不能直接套到剥离后的普通池。", ""]
        if v["evidence"]:
            review += ["| BD／来源 | 可参考R入口 | 类型／底材 | 普通目标（计数） | 腐化参考（不计数） | 原Strict门槛（混合池） |", "|---|---|---|---|---|---|"] if vid == "V19" else ["| BD／来源 | 可参考R入口 | 类型／底材 | 提取情报 | 来源门槛（仅参考） |", "|---|---|---|---|---|"]
            groups = {}
            for c in v["evidence"]:
                source = lookup[(c["build"], c["x"])]
                key = (c["build"], tuple(c["types"]), tuple(c["subtypes"]), tuple(c["affix_ids"]), tuple(c.get("corrupted_affix_ids", [])), c["enabled_in_source"])
                if vid != "V13":
                    key += (gate_text(source),)
                groups.setdefault(key, []).append(c)
            for entries in groups.values():
                c = entries[0]
                role = "主Flay" if c["build"] == "flay-mana-lich" else "副Skeleton"
                refs = "／".join("X" + str(e["x"]) for e in entries)
                ids = c["affix_pools"][0] if vid == "V09" else c["affix_ids"]
                detail = "定向底材候选，词缀条件不移植" if vid == "V15" else names("affixes", ids)
                if vid == "V09":
                    detail += "；另有1156项通用T7池"
                gates = "／".join(dict.fromkeys(gate_text(lookup[(e["build"], e["x"])]) for e in entries))
                cells = [role + " " + refs + ("（关闭，只参考）" if not c["enabled_in_source"] else ""), "／".join("R" + str(n) for n in c["candidate_raxx_slots"]) + ("（待判别）" if c["mapping_requires_review"] else ""), scope(c), detail, gates]
                if vid == "V19":
                    cells.insert(4, names("affixes", c["corrupted_affix_ids"]))
                review.append("| " + " | ".join(s.replace("|", "/") for s in cells) + " |")
            review.append("")
        if not v["evidence"]:
            review += ["未导出可直接填写的候选；保留未决状态，不用空值冒充已配置。", ""]
    review += ["## 仍需Review的决定", "", "- R15目标是否只采用这20种，或随后再加入有正文／Planner依据的替代品。", "- 宽T7素材池的保留范围；BIS窄池不能代替它。", "- Flay普通两项池与1／2项层已按用户要求记录；其他BD的普通词缀配对仍需确认，腐化不凑数。", "- Flay厚实一项层按用户列表可只有886；若要求点燃876必有，需明确采用必须条件。891备用来自攻略，未加入这4层。", "- 是否采用普通实验词缀、升华、定向底材、各类碎片；碎片必须结合库存。", "- 开荒是否在本次用途内；若需要，补开荒阶段的武器／副手及底材。", "- 原版R29／R69／R70默认关闭，R81／R82／R83等仍有待配置入口；本轮并未决定最终开关。", "", "## 程序与证据", "", "运行：`python -X utf8 scripts/extract_raxx_variables.py`。完整候选、原值与来源条件见[机器结果](../analysis/raxx-variable-extraction.json)，检查见[验证结果](../analysis/variable-extraction-validation.json)。冻结原版与两份Strict哈希校验通过；已有filter原文件保持不变。旧187条试制稿保留作历史，本轮Review以这份变量结论为准。", ""]
    classification_doc = ["# Strict神像词缀：自动分类结果", "", "本页由extract_raxx_variables.py生成；无需攻略文字、Planner JSON或人工指定某个ID是否腐化。它只提取和分类情报，不生成filter。", "",
                          "Strict直接提供目标词缀ID，但没有逐词缀的腐化类别标签。程序读取已冻结的词缀数据库：specialAffixType=6归腐化，其余归非腐化；神像普通目标计数只使用非腐化池。这里不按中文名称猜测，腐化伤害（18）也不会因此被错判为腐化专属词缀。", "",
                          "CorruptionCondition描述物品是否腐化，与每个词缀的类别是两个不同字段。Strict选择了某项腐化属性，可以自动提取这个选择；其重要性、必须／可选以及备用关系仍由用户或攻略补充决定。", "",
                          "数据库覆盖的ID均自动分类；如果出现词库未收录的ID，查表会报错，不默认归入普通。类型资料来自Last Epoch Tools的version150冻结快照，运行时无需联网。", "",
                          "| BD／Strict来源 | 神像类型 | 非腐化目标 | 腐化目标（普通计数排除） |", "|---|---|---|---|"]
    for c in idol_classification["rules"]:
        role = "Flay" if c["build"] == "flay-mana-lich" else "Skeleton"
        kinds = "、".join(ref["equipment_names"][t]["zh"] for t in c["types"])
        classification_doc.append(f"| {role} X{c['x']} | {kinds} | {names('affixes', c['non_corrupted_affix_ids'])} | {names('affixes', c['corrupted_affix_ids'])} |")
    classification_doc += ["", "Flay中型X17／X21的源池含843、854、1069、1070，自动分为普通843／854与腐化1069／1070；厚实X18／X22含876、886、1070，自动分为普通876／886与腐化1070。源ID和具体底材完整保存在[机器结果](../analysis/strict-idol-affix-classification.json)，词缀类别来自[冻结类型资料](../sources/builds/strict-variable-reference.json)。", "",
                           "这些源规则中的ID全部来自Strict。843／854等组合是否毕业、1069或1070是否追求，以及891备用关系属于另一层决策；见[Flay神像审阅](FLAY_IDOL_REVIEW.md)。", ""]
    for path, data in [("analysis/raxx-variables.json", {"baseline": manifest["baseline"], "variables": [{k: v[k] for k in ["id", "title", "raxx_slots", "instruction_slots", "instruction_texts", "editable_fields", "baseline_defaults", "interpretation"]} for v in variables]}), ("analysis/raxx-variable-extraction.json", result), ("analysis/strict-idol-affix-classification.json", idol_classification)]:
        (ROOT / path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    for path, content in [("docs/RAXX_VARIABLES.md", catalog), ("docs/STRICT_VARIABLE_REVIEW.md", review), ("docs/STRICT_IDOL_CLASSIFICATION.md", classification_doc)]:
        (ROOT / path).write_text("\n".join(content).rstrip() + "\n", encoding="utf-8", newline="\n")
    hashes_after = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    assert hashes_before == hashes_after, "Extraction must never modify source or output filters"
    assert sorted(ROOT.glob("filters/*.xml")) == [p for p in protected if p.parent == ROOT / "filters"], "No new filter may be created"
    validation = {"passed": True, "variable_groups": len(variables), "blue_instructions_covered": len(blue), "strict_rules_recorded": len(evidence), "families": dict(sorted(Counter(r["family"] for r in evidence).items())), "enabled_tier_pools": 38, "target_unique_ids": len(union), "sets_in_planner_targets": sum(flags["is_set_item"][str(i)] for i in union), "r15_missing_targets": missing, "idol_corrupted_affixes_excluded_from_ordinary_counts": True, "strict_idol_rules_automatically_classified": len(idol_candidates), "guide_used_for_affix_classification": False, "user_reviewed_flay_idol_layers": len(idol_layers), "filters_and_source_bytes_unchanged": True, "filter_generated": False, "game_execution_tested": False}
    (ROOT / "analysis/variable-extraction-validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(validation, ensure_ascii=False))


if __name__ == "__main__":
    main()
