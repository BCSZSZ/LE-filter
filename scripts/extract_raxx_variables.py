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
    ("V06", "双／多T7全量保护", [48], [36], "全量词缀与原23类装备；不按BD目标裁剪", []),
    ("V07", "单T7阶段全量收集", [60], [49, 51, 52, 53, 54, 56, 57], "默认开启的一条阶段规则；玩家手动关闭", []),
    ("V08", "原护甲宽池入口（已并入V07）", [61], [49, 51, 56, 57], "原R61仅追溯；新基底不再有独立规则", []),
    ("V09", "BD目标不限阶数＋T7", [62], [58, 59], "按BD／装备类型绑定目标池；目标不限阶数、另有全池T7", ["tier7"]),
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
    "V05": (
        "原设计：优先标记各部位最想要的T7词缀，供直接穿戴或给暗金制作传奇。R38–47只要求所选目标中至少1条T≥7，没有角色等级上限。这里的BIS是值得查看的候选，不保证整件装备毕业；另外几条词缀、底材和制作潜能仍需查看。"
        "\n\n阶段：面向终局目标，过渡期掉落也收。只要最佳T7有价值，即使其他属性不理想，也可能值得留下作为制作素材。"
        "\n\n填写：Strict部位T7池提供候选，仍须按BD和装备类型绑定。武器／副手手位、直接穿戴底材需确认；作者仅建议穿戴用途选具体底材，传奇制作素材不据暗金底材反推同一subtype。"),
    "V06": "用户确认的C2：原R48改为全量词缀中至少2条T≥7，原23类装备不限BD目标、没有角色等级退出。原623项池扩到冻结词库全部1156项，双T6／T7＋T6不再由此常驻保护。本层无需从Strict填写目标池。",
    "V07": "用户确认的C4：原R60与R61合成一条，覆盖原23类装备及全1156项词缀，至少1条T≥7，默认启用、没有角色等级退出，由玩家阶段结束后手动关闭。它位于C1／C2／C3之后，实际兜底没有BD目标的单T7；关闭它保留前三类。本层不从Strict取窄池。",
    "V08": "原R61已移除，其护甲／饰品／遗物范围并入V07的一条全类型阶段收集。V08编号仅用于追溯原版，不再是当前基底需要填写的独立入口。原42／343项池只作历史参考。",
    "V09": "用户确认的C3：对应装备类型至少1条BD目标、阶数不限，同时全池至少1条T≥7。Strict部位T7规则只提供与V05相同的目标名单，不沿用其T7门槛；按BD／装备类型分别绑定。原R62的10项只是模板示例，必须替换；Wanted/Havoc全局混池保留在原Strict记录中，不取代部位绑定。新基底不加FP、未封印计数或未腐化限制，先匹配C1／C2，再由本层保护目标低阶＋非目标单T7。保留不保证可以Havoc制作。",
    "V10": (
        "原设计：T7尚未充裕时，补收更挑选的目标T6素材。R63／64要求至少1条所选目标T≥6，角色0–84级，85级起不再匹配；原武器／副手池16项，其他装备池338项，不限具体底材。门槛是T6及以上，并非恰好T6；T7往往先被前面的规则显示。"
        "\n\n阶段：作者明确安排的过渡补充收集。85级是Raxx收紧拾取的策略，不要求玩家换掉身上的T6。新V06只保护双／多T7，双T6不再由它常驻保护；实验物品或碎片等其他显示路径仍可能保留T6。V07单T7阶段层没有85级自动退出。"
        "\n\n填写：取Strict的类型／词缀，保留Raxx的0–84级条件；Strict的全等级收集不转移。T6也属于崇高，传奇制作的材料条件未限定只能T7，符合其他制作要求的T6也可使用，见[官方稀有度说明](https://support.lastepoch.com/hc/en-us/articles/46362011564187-Rarity)与[传奇制作说明](https://support.lastepoch.com/hc/en-us/articles/46361924310555-Legendary-Items)。"),
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
    active = read_json("templates/base-manifest.json")
    protected = sorted([*ROOT.glob("filters/*.xml"), ROOT / active["file"], ROOT / "sources/Raxx's S5 Ultimate Filter v1.0.txt", *ROOT.glob("sources/builds/maxroll-*-strict.xml")])
    hashes_before = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    manifest, strict = read_json("sources/manifest.json"), read_json("sources/builds/maxroll-strict-manifest.json")
    def frozen(spec):
        path = spec.get("file", spec.get("local_path"))
        raw = (ROOT / path).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == spec["sha256"], path
        return ET.fromstring(raw)
    base_nodes = sorted(frozen(manifest["baseline"]).find("rules"), key=lambda r: int(r.findtext("Order")))
    base = {i: inspect_rule(r) for i, r in enumerate(base_nodes, 1)}
    template_nodes = sorted(frozen(active).find("rules"), key=lambda r: int(r.findtext("Order")))
    current = {r: (b, inspect_rule(node)) for b, (r, node) in enumerate(zip(active["source_rule_order"], template_nodes, strict=True), 1)}
    assert active["source"]["sha256"] == manifest["baseline"]["sha256"]
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
        if vid == "V23":
            matches = [r for r in matches if set(r["types"]) & set(base[60]["types"])]
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
            candidates[-1]["candidate_template_slots"] = [current[n][0] for n in target_slots if n in current]
            if vid in {"V19", "V21"}:
                classified = split_affixes(ids, flags["special_affix_type"])
                candidates[-1]["corrupted_affix_ids"] = classified["corrupted_affix_ids"]
                candidates[-1]["affix_ids"] = classified["non_corrupted_affix_ids"]
                candidates[-1]["count_scope"] = "ordinary_target_affixes_only; corruption_status_unrestricted"
        variables.append({"id": vid, "title": title, "raxx_slots": slots, "instruction_slots": instructions, "editable_fields": fields,
                          "instruction_texts": {str(n): base[n]["name"] for n in instructions},
                          "template_instruction_texts": {str(current[n][0]): current[n][1]["name"] for n in instructions if n in current},
                          "template_slots": {str(n): current[n][0] for n in slots if n in current},
                          "template_default_overrides": {str(current[n][0]): current[n][1] for n in slots if n in current and current[n][1] != base[n]},
                          "strict_families": families, "baseline_defaults": {str(n): base[n] for n in slots}, "evidence": candidates,
                          "status": "有启用来源候选，待审阅" if any(c["enabled_in_source"] for c in candidates) else "仅关闭来源参考，不自动采用" if candidates else "Strict未给出可直接填写的值", "interpretation": NOTES[vid]})
        if vid == "V02":
            variables[-1]["status"] = "两份目标名单均未发现套装；保留R16原预设"
        elif vid in {"V06", "V07", "V08"}:
            variables[-1]["status"] = {"V06": "用户确认：双／多T7全量常驻", "V07": "用户确认：一条全量阶段规则，玩家手动关闭", "V08": "已并入V07，不再填写"}[vid]
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
    targets = {v["id"]: {(c["build"], tuple(c["types"]), tuple(c["subtypes"])): c["affix_ids"] for c in v["evidence"] if c["enabled_in_source"]} for v in variables if v["id"] in {"V05", "V09"}}
    assert targets["V05"] == targets["V09"] and len(targets["V05"]) == 19
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
    result = {"stage": "Active reusable base template and Strict evidence; no final BD filter", "baseline": manifest["baseline"], "active_template": active, "strict_inputs": strict["inputs"],
              "reference_files_sha256": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in ["sources/game-reference.json", strict["reference_supplement"], "sources/builds/review-reference.json", "sources/builds/strict-variable-reference.json"]},
              "roles": {"main": "flay-mana-lich", "secondary": "skeleton-necromancer", "shared": "main", "role_assignment_is_default": True},
              "variables": variables, "strict_rules": evidence, "target_ids": unique, "target_union": union, "r15_missing_targets": missing, "tier6_tier7_target_pools_equal": tier_pools_equal, "c1_c3_targets_equal_by_build_and_type": True,
              "user_reviewed_flay_idol_layers": idol_layers,
              "fixed_instruction_slots": sorted(fixed_instructions), "unmodified_files_sha256": hashes_before}
    catalog = [
        "# 新基底：需要填写或审阅的变量", "",
        "当前基底为[LE Base Template v1](BASE_TEMPLATE.md)。R编号追溯冻结原版，B编号=新模板Order+1。V编号保留以便追溯；T7四类以C1→C2→C3→C4顺序匹配。本表读取真实新模板，未生成两个BD最终filter。", "",
        "## 当前基底收集策略", "",
        "1. 稀有共通暗金：R15原名单143项保留，0LP也留。",
        "2. BD关联暗金：把目标名字补入同一个R15名单，0LP也留；不新增BD独立LP分层。",
        "3. 高潜能暗金：R12不限制名字，LP3／WW20起；R13／14仍用原名单与LP2／WW17、LP1／WW14门槛。",
        "4. 传奇、套装与资源：R8全部传奇、R16需要的套装、R19–24资源沿用原版。",
        "5. 装备：BD目标T7、双／多T7全量、BD目标不限阶数＋T7、额外单T7阶段全量四类。阶段层默认开启且由玩家手动关闭；双T6不再由原R48常驻保护，原R63／64的T6过渡层仍在85级退出。",
        "6. 神像：BIS默认至少两项；过渡神像分别90／75级退出；祭坛R127至少一项、阶数不限。",
        "7. 早期腐化：R75只收已选腐化属性、角色0–59级；不添加全等级宽松腐化分支。",
        "8. R37的T8池与R163最终隐藏沿用原版，本轮不扩池或增加规则。", "",
        "## 变量总表", "", "| 变量 | 填写内容 | 原R入口 | 当前B入口 | Strict情报／用户决定 |", "|---|---|---|---|---|",
        *[f"| {v['id']} {v['title']} | {v['editable_fields']} | {', '.join('R'+str(n) for n in v['raxx_slots'])} | {', '.join('B'+str(n) for n in v['template_slots'].values()) or '已并入V07'} | {', '.join(v['strict_families']) or '用户决定／玩家信息'} |" for v in variables], "",
        "## 当前基底入口与门槛", "",
    ]
    review = ["# 新基底：Strict变量审阅结论", "", "当前基底是[LE Base Template v1](BASE_TEMPLATE.md)，已落实用户确认的T7四类。此处提取BD填空情报，尚未生成两个BD的最终filter。", "", "本次默认Flay为主、Skeleton为副；共享按主处理，两者同等收集。角色身份作为情报归属，模板尚未填写两BD目标及显示身份。", "", "## 先审阅的结论", "", "1. 稀有共通暗金：保留原R15的143项。", f"2. BD关联暗金：两份Strict各11种，共20种（共享253／416）；原R15缺{len(missing)}种：{names('uniques', missing)}。其余目标已在R15，无需重复加入。", "3. 本轮没有增加正文中的5种替代暗金，也没有导入Planner JSON中的精确神像组合；这些不是Strict直接导出的情报。", "4. 19份部位目标池同时供C1目标T7与C3目标不限阶数＋T7使用，按BD／类型绑定；C2、C4全量池已由用户确认，不用Strict窄池填写。", "5. 神像普通与腐化已自动分开；Flay的4条1／2项候选层保持用户审阅结果，尚未填写到通用模板。", "6. Strict的LP分层、FP52、全等级T6、祭坛分层等不直接移植；C4手动退出来自本次用户确认，T6继续原0–84级过渡。", "", "以下与[变量总表](RAXX_VARIABLES.md)对应。R追溯原版，B为新模板位置，X为Strict物理位置；源门槛仅为证据。", ""]
    lookup = {(r["build"], r["x"]): r for r in evidence}
    for v in variables:
        catalog += [f"### {v['id']}｜{v['title']}", "", "可填字段：" + v["editable_fields"] + "。", "", "处理原则：" + v["interpretation"], ""]
        for r, n in v["template_slots"].items():
            row = current[int(r)][1]
            pools = "/".join(names("affixes", p) if 0 < len(p) <= 15 else str(len(p)) + "项" for p in row["affix_pools"])
            catalog.append(f"- B{n}（{'启用' if row['enabled'] else '关闭'}）：{scope(row)}；词缀池={pools or '无'}；名字名单={len(row['unique_ids'])}项；{gate_text(row)}。")
        catalog.append("")
        vid = v["id"]
        if vid == "V05":
            review += [
                '<a id="equipment-purpose"></a>', "", "## V05–V10：收集目的与过渡范围", "",
                "当前采用用户确认的四类。C1→C2→C3→C4是匹配顺序，V编号只是沿用原入口编号。C1／C2／C3常驻；C4是默认开启、玩家手动结束的单T7收集阶段；V10另有0–84级T6过渡。", "",
                "原623／42／343项预填池只作[历史对照](RAXX_DEFAULT_EQUIPMENT_POOLS.md)。新C2和C4使用冻结词库全部1156项及原23类装备，无需按BD裁剪；C3的T7计数也用全池，目标则按BD／类型绑定。", "",
                "| 类别／变量 | 当前B入口／原R入口 | 当前条件 | 用途与退出 |", "|---|---|---|---|",
                "| C1／V05 | B38–47／R38–47 | 对应类型至少1条BD目标T≥7 | 终局目标候选；过渡期也收，无等级退出 |",
                "| C2／V06 | B48／R48 | 全池至少2条T≥7，不要求BD目标 | 双／多T7常驻保护；不再保护双T6或T7＋T6 |",
                "| C3／V09 | B60／R62 | 对应类型至少1条BD目标、阶数不限，同时全池至少1条T≥7 | 留目标低阶＋非目标T7，无FP或未腐化收集限制；保留不保证可制作 |",
                "| C4／V07 | B61／R60，合并R61 | 全池至少1条T≥7；前三类先匹配 | 额外单T7阶段兜底，默认开启，玩家手动关闭，无自动等级退出 |",
                "| V08历史入口 | 原R61已移除 | 原护甲／饰品／遗物宽池并入C4 | 不再独立填写或开关 |",
                "| V10 | B62–63／R63–64 | 至少1条所选目标T≥6，角色0–84级 | T7不足时补收目标T6，85级退出 |", "",
                "### 用几个例子区分", "",
                "以下只比较这些收集入口，假设BD／类型目标已正确填写：", "",
                "- 90级掉落一件只有1条BD目标T7的装备：C1仍保留，其他词缀不一定毕业。",
                "- 90级掉落两条非BD目标T7：C2仍保留；两条T6不再享受C2的常驻保护。",
                "- 非目标T7＋对应部位的BD目标T4：C3保留；即使C4已经关闭也保留。",
                "- 非目标单T7，整件没有BD目标：C4开启时保留，玩家关闭后撤掉这条兜底路径。实验／碎片等其他规则仍可能显示它。",
                "- 只有一条所选目标T6的装备：80级可由V10补收；85级后这条补收路径退出。它是否被整个filter保留，还要看其他规则，不能据此断言全部隐藏。", "",
                "当前优先顺序是B38–47 → B48 → B60 → B61 → B62／63。原R60移到R62之后，R61删除，避免全量阶段层先于目标候选显示。C4的XML写至少1条T7，通过先匹配前三类表达剩余单T7，不增加未经验证的最多1条条件。", "",
                "原设计依据：[冻结原版XML](../sources/Raxx%27s%20S5%20Ultimate%20Filter%20v1.0.txt)及作者视频[13:08起](https://www.youtube.com/watch?v=l3CRNP95YX8&t=788s)、[14:29起](https://www.youtube.com/watch?v=l3CRNP95YX8&t=869s)。当前四类来自用户确认，真实模板与待办见[新基底说明](BASE_TEMPLATE.md)。", "",
            ]
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
        if vid in {"V06", "V07", "V08"}:
            review += ["本项已按用户决定落实到[新基底](BASE_TEMPLATE.md)，不从Strict部位目标裁剪全量池。原值仅保留作追溯。", ""]
            continue
        if vid in {"V22", "V23"}:
            for slug in ["flay-mana-lich", "skeleton-necromancer"]:
                candidates = [c for c in v["evidence"] if c["build"] == slug and c["enabled_in_source"]]
                types = sorted({t for c in candidates for t in c["types"]})
                review.append("- " + strict["inputs"][slug]["name"] + "可证明的终局类型：" + "、".join(ref["equipment_names"][t]["zh"] for t in types) + "。")
            review += ["", "具体目标词缀见[V05](#v05)；上述类型只表示情报范围。", ""]
            continue
        if vid == "V10" and tier_pools_equal:
            review += ["程序逐部位核对：19份T6池与对应19份T7池的类型、底材和词缀列表完全相同，具体候选复用[V05](#v05)。相同的是Strict来源目标：C1要求目标T7，C3目标不限阶数但另须全池T7，V10要求目标T6且85级退出；C4全量阶段池不随BD收窄。", "", "T6来源定位：", ""]
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
            review += ["| BD／来源 | 当前B入口／原R入口 | 类型／底材 | 普通目标（计数） | 腐化参考（不计数） | 原Strict门槛（混合池） |", "|---|---|---|---|---|---|"] if vid == "V19" else ["| BD／来源 | 当前B入口／原R入口 | 类型／底材 | 提取情报 | 来源门槛（仅参考） |", "|---|---|---|---|---|"]
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
                ids = c["affix_ids"]
                detail = "定向底材候选，词缀条件不移植" if vid == "V15" else names("affixes", ids)
                if vid == "V09":
                    detail += "；本层目标阶数不限，T7计数用新基底全池"
                gates = "／".join(dict.fromkeys(gate_text(lookup[(e["build"], e["x"])]) for e in entries))
                destination = "／".join("B" + str(n) for n in c["candidate_template_slots"]) + "（原" + "／".join("R" + str(n) for n in c["candidate_raxx_slots"]) + "）"
                cells = [role + " " + refs + ("（关闭，只参考）" if not c["enabled_in_source"] else ""), destination + ("（待判别）" if c["mapping_requires_review"] else ""), scope(c), detail, gates]
                if vid == "V19":
                    cells.insert(4, names("affixes", c["corrupted_affix_ids"]))
                review.append("| " + " | ".join(s.replace("|", "/") for s in cells) + " |")
            review.append("")
        if not v["evidence"]:
            review += ["未导出可直接填写的候选；保留未决状态，不用空值冒充已配置。", ""]
    review += ["## 仍需Review的决定", "", "- R15目标是否只采用这20种，或随后再加入有正文／Planner依据的替代品。", "- C1／C3各目标与装备类型的绑定，尤其主手／副手及遗物；四类收集策略与C2／C4全量范围已确认。", "- Flay普通两项池与1／2项层已按用户要求记录；其他BD的普通词缀配对仍需确认，腐化不凑数。", "- Flay厚实一项层按用户列表可只有886；若要求点燃876必有，需明确采用必须条件。891备用来自攻略，未加入这4层。", "- 是否采用普通实验词缀、升华、定向底材、各类碎片；碎片必须结合库存。", "- 开荒是否在本次用途内；若需要，补开荒阶段的武器／副手及底材。", "- 原版R29／R69／R70默认关闭，R81／R82／R83等仍有待配置入口；这些开关尚未定制，C4默认开启、由玩家阶段结束后手动关闭已确定。", "", "## 程序与证据", "", "运行：`python -X utf8 scripts/extract_raxx_variables.py`；模板重建与验证见[新基底说明](BASE_TEMPLATE.md)。完整候选、原值与来源条件见[机器结果](../analysis/raxx-variable-extraction.json)，检查见[验证结果](../analysis/variable-extraction-validation.json)。冻结原版、两份Strict及当前模板均校验哈希；提取过程不改XML。旧187条试制稿保留作历史，两个BD的最终filter尚未生成。", ""]
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
    for path, data in [("analysis/raxx-variables.json", {"baseline": manifest["baseline"], "active_template": active, "variables": [{k: v[k] for k in ["id", "title", "raxx_slots", "instruction_slots", "instruction_texts", "template_instruction_texts", "editable_fields", "baseline_defaults", "template_slots", "template_default_overrides", "interpretation"]} for v in variables]}), ("analysis/raxx-variable-extraction.json", result), ("analysis/strict-idol-affix-classification.json", idol_classification)]:
        (ROOT / path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    default_pools = ["# Raxx原版：V06–V08已经预填的范围", "",
                     "由extract_raxx_variables.py从冻结原版及名字库生成，以下为原始预选，仅作历史对照。当前[新基底](BASE_TEMPLATE.md)已把双／多T7与阶段单T7改为全1156项词缀范围，原R60／61合成一条；本页不代表当前配置。", "",
                     "三条均启用、没有角色等级退出条件、不限具体subtype。原版出处：[冻结XML](../sources/Raxx%27s%20S5%20Ultimate%20Filter%20v1.0.txt)；填写原则与Strict候选见[变量审阅结论](STRICT_VARIABLE_REVIEW.md#equipment-purpose)。", ""]
    for v in variables:
        if v["id"] not in {"V06", "V07", "V08"}:
            continue
        for n, row in v["baseline_defaults"].items():
            ids = row["affix_pools"][0]
            default_pools += [f"## {v['id']}／R{n}｜{row['name']}", "", "装备范围：" + scope(row) + "。", "",
                              "原门槛：" + gate_text(row) + f"。预选词缀共{len(ids)}项，下面按原列表顺序完整列出。", "",
                              "| ID | 中文 | 英文 |", "|---:|---|---|"]
            default_pools += [f"| {i} | {ref['affixes'][str(i)]['zh']} | {ref['affixes'][str(i)]['en']} |" for i in ids]
            default_pools.append("")
    for path, content in [("docs/RAXX_VARIABLES.md", catalog), ("docs/STRICT_VARIABLE_REVIEW.md", review), ("docs/STRICT_IDOL_CLASSIFICATION.md", classification_doc), ("docs/RAXX_DEFAULT_EQUIPMENT_POOLS.md", default_pools)]:
        (ROOT / path).write_text("\n".join(content).rstrip() + "\n", encoding="utf-8", newline="\n")
    hashes_after = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    assert hashes_before == hashes_after, "Extraction must never modify source or output filters"
    assert sorted(ROOT.glob("filters/*.xml")) == [p for p in protected if p.parent == ROOT / "filters"], "No new filter may be created"
    validation = {"passed": True, "active_template_loaded": True, "template_rule_count": active["rule_count"], "template_full_affix_ids": len(active["full_affix_ids"]), "stage_rule_requires_manual_disable": active["layers"][3]["player_disables_manually"], "c1_c3_targets_equal_by_build_and_type": True, "variable_groups": len(variables), "blue_instructions_covered": len(blue), "strict_rules_recorded": len(evidence), "families": dict(sorted(Counter(r["family"] for r in evidence).items())), "enabled_tier_pools": 38, "target_unique_ids": len(union), "sets_in_planner_targets": sum(flags["is_set_item"][str(i)] for i in union), "r15_missing_targets": missing, "idol_corrupted_affixes_excluded_from_ordinary_counts": True, "strict_idol_rules_automatically_classified": len(idol_candidates), "guide_used_for_affix_classification": False, "user_reviewed_flay_idol_layers": len(idol_layers), "filters_and_source_bytes_unchanged": True, "filter_generated": False, "final_bd_filter_generated": False, "game_execution_tested": False}
    (ROOT / "analysis/variable-extraction-validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(validation, ensure_ascii=False))


if __name__ == "__main__":
    main()
