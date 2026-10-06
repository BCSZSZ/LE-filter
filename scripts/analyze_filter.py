"""Read the frozen baseline; regenerate inventories and structural validation."""
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
XSI = "{http://www.w3.org/2001/XMLSchema-instance}"
REF = json.loads((ROOT / "sources/game-reference.json").read_text(encoding="utf-8"))
MANIFEST = json.loads((ROOT / "sources/manifest.json").read_text(encoding="utf-8"))
COLORS = {0: "原色/白", 3: "金黄", 4: "橙黄", 5: "橙", 7: "红", 8: "粉", 11: "淡紫", 12: "蓝", 15: "薄荷绿", 16: "亮绿"}
KINDS = set("AffixCondition SubTypeCondition CharacterLevelCondition RarityCondition UniqueModifiersCondition PotentialCondition CorruptionCondition FactionCondition ClassCondition WovenEchoesCondition CraftingMaterialsCondition RuneCondition ResonancesCondition KeysCondition GlyphCondition".split())


def value(node):
    if node.get(XSI + "nil") == "true":
        return None
    if not len(node):
        return (node.text or "").strip()
    if all(c.tag in {"int", "EquipmentType", "FactionID"} for c in node):
        return [value(c) for c in node]
    grouped = {}
    for child in node:
        grouped.setdefault(child.tag, []).append(value(child))
    return {k: v if len(v) > 1 else v[0] for k, v in grouped.items()}


def read_rules(path):
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    root = ET.fromstring(raw)
    blocks = list(re.finditer(r"<Rule>.*?</Rule>", text, re.S))
    rules = []
    for pos, (node, block) in enumerate(zip(root.find("rules"), blocks), 1):
        fields = {c.tag: value(c) for c in node if c.tag != "conditions"}
        rules.append({"number": int(fields["Order"]) + 1, "xml_position": pos,
                      "source_lines": [text.count("\n", 0, block.start()) + 1, text.count("\n", 0, block.end()) + 1],
                      "fields": fields, "conditions": [{"kind": c.get(XSI + "type"), "fields": value(c)} for c in node.find("conditions")]})
    assert len(rules) == len(root.find("rules")) == len(blocks)
    return root, sorted(rules, key=lambda r: r["number"])


def list_text(items, section):
    if not items:
        return "空列表"
    names = [REF[section][str(i)]["zh"] + f"({i})" for i in items[:4]]
    return "、".join(names) + (f"等 {len(items)} 项" if len(items) > 4 else "")


def describe(c):
    k, f = c["kind"], c["fields"]
    if k == "AffixCondition":
        names = list_text(f["affixes"], "affixes")
        text = f"词缀：{names}；至少 {f['minOnTheSameItem']} 条"
        if f["advanced"] == "true":
            op = {"ANY": "不限", "MORE": ">", "MORE_OR_EQUAL": "≥"}
            text += "；单条 T " + op[f["comparsion"]] + (f["comparsionValue"] if f["comparsion"] != "ANY" else "")
            text += "；合计 T " + op[f["combinedComparsion"]] + (f["combinedComparsionValue"] if f["combinedComparsion"] != "ANY" else "")
        else:
            text += "；advanced=false，保存的阶数阈值不作为已启用限制"
        return text
    if k == "SubTypeCondition":
        ts, ids = f["type"], f["subTypes"]
        names = "、".join(REF["equipment_names"][t]["zh"] for t in ts) if ts else "空类型（广泛匹配，见说明）"
        bases = [REF["subtypes"][t + ":" + i]["zh"] + f"({i})" for t in ts for i in ids]
        return "物品：" + names + ("；底材：" + "、".join(bases) if bases else "；底材不限")
    if k == "CharacterLevelCondition":
        return f"角色等级 {f['minimumLvl']}–{f['maximumLvl']}"
    if k == "RarityCondition":
        return "稀有度：" + f["rarity"]
    if k == "UniqueModifiersCondition":
        us = f["Uniques"] if isinstance(f["Uniques"], list) else [f["Uniques"]]
        return f"指定暗金/套装 {len(us)} 项；见 SELECTED_UNIQUES.md；roll 边界为空或 0–255"
    if k == "PotentialCondition":
        return f"LP≥{f['MinLegendaryPotential']} 或 WW≥{f['MinWeaversWill']}（其余边界为空）"
    if k == "CorruptionCondition":
        return "腐化状态：" + f["Corruption"]
    if k == "ClassCondition":
        return "职业需求：" + f["req"] + "（未选职业；此隐藏规则默认关闭）"
    if k == "FactionCondition":
        return "物品阵营标记：" + ", ".join(f["EligibleFactions"])
    assert k in KINDS, k
    return k + "：" + ", ".join(str(v) for v in f.values())


def dump(path, data):
    (ROOT / path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


path = ROOT / MANIFEST["baseline"]["local_path"]
root, rules = read_rules(path)
_, old = read_rules(ROOT / MANIFEST["video_era_filter"]["local_path"])
assert [r["number"] for r in rules] == list(range(1, 164))
assert [r["xml_position"] for r in rules] == list(range(163, 0, -1))
assert hashlib.sha256(path.read_bytes()).hexdigest() == MANIFEST["baseline"]["sha256"]
assert hashlib.sha256((ROOT / MANIFEST["video_era_filter"]["local_path"]).read_bytes()).hexdigest() == MANIFEST["video_era_filter"]["sha256"]
seen = Counter(c["kind"] for r in rules for c in r["conditions"])
assert set(seen) == KINDS
affix_ids = {str(i) for r in rules for c in r["conditions"] if c["kind"] == "AffixCondition" for i in c["fields"]["affixes"]}
unique_ids = {str(u["UniqueId"]) for r in rules for c in r["conditions"] if c["kind"] == "UniqueModifiersCondition" for u in c["fields"]["Uniques"]}
assert affix_ids <= REF["affixes"].keys() and unique_ids <= REF["uniques"].keys()
roll_bounds = [x.text for x in root.findall("rules/Rule/conditions/Condition/Uniques/Rolls/UniqueModifierWithRollId/Modifier/*") if x.get(XSI + "nil") != "true"]
assert set(roll_bounds) == {"0", "255"}
dump("analysis/rules.json", {"source_sha256": MANIFEST["baseline"]["sha256"], "metadata": {c.tag: value(c) for c in root if c.tag != "rules"}, "rules": rules})
changes = [{"number": a["number"], "name": b["fields"]["nameOverride"], "before": {"fields": a["fields"], "conditions": a["conditions"]}, "after": {"fields": b["fields"], "conditions": b["conditions"]}} for a, b in zip(old, rules) if a["fields"] != b["fields"] or a["conditions"] != b["conditions"]]
assert [x["number"] for x in changes] == [15, 20, 29, 61, 82, 83, 91]
dump("analysis/version-diff.json", changes)

lines = ["# 完整规则索引", "", "由 scripts/analyze_filter.py 离线生成。编号按 Order+1，越小越优先；XML 物理存储顺序相反。完整字段、完整选择列表及源文件行号在 analysis/rules.json。", "", "空词缀列表和空类型的含义见 FILTER_GUIDE.md；不能按名称推定条件。S1=None、S6=Begin 来自社区格式映射；M 为原始地图图标 ID。", "", "| 编号 | 状态/动作 | 原始名称 | 条件（同一规则内共同满足） | 显示/提示 |", "|---:|---|---|---|---|"]
for r in rules:
    f = r["fields"]
    note = f["isEnabled"] == "false" and f["color"] == "12"
    state = "说明条目/关闭" if note else ("启用" if f["isEnabled"] == "true" else "关闭") + "/" + f["type"]
    condition = "说明用占位条件；保持关闭" if note else "；".join(describe(c) for c in r["conditions"]) or "无条件，匹配全部"
    style = (COLORS[int(f["color"])] if f["recolor"] == "true" else "保留原色") + f"；S{f['SoundId']}；M{f['MapIconId']}"
    style += "；强调" if f["emphasized"] == "true" else ""
    style += f"；光柱 {f['BeamSizeOverride']}/色号{f['BeamColorOverride']}" if f["BeamOverride"] == "true" else ""
    name = f["nameOverride"] or ("显示所有传奇" if r["number"] == 8 else "最终隐藏全部")
    lines.append(f"| {r['number']} | {state} | {name.replace('|', '/')} | {condition} | {style} |")
(ROOT / "docs/RULE_INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

lines = ["# 词缀与底材 ID 对照", "", "社区 version150 数据及其游戏本地化文本的冻结摘录；不等于游戏引擎行为验证。完整映射、适用物品类型和出处哈希见 sources/game-reference.json。", "", "## 词缀", "", "| ID | 中文 | 英文 |", "|---:|---|---|"]
for i in sorted(affix_ids, key=int):
    a = REF["affixes"][i]
    lines.append(f"| {i} | {a['zh']} | {a['en']} |")
lines += ["", "## 底材", "", "ID 必须和物品类型组合使用，不是全局唯一编号。", "", "| 类型:ID | 中文 | 英文 |", "|---|---|---|"]
for i, a in sorted(REF["subtypes"].items()):
    lines.append(f"| {i} | {a['zh']} | {a['en']} |")
(ROOT / "docs/ID_REFERENCE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

selected = {n: {u["UniqueId"] for c in rules[n - 1]["conditions"] if c["kind"] == "UniqueModifiersCondition" for u in c["fields"]["Uniques"]} for n in [13, 14, 15, 16]}
lines = ["# 暗金与套装选择清单", "", "第12条只要求 UNIQUE 与潜能门槛，无名字白名单。第13/14条各选412项且列表相同，第15条选143项，第16条选21项。勾选的是已有列表，不保证未来新增物品会自动进入。第15条没有 LP=0 条件。", "", "旧 ID 46、69、248 的名字仅在本地化中找到，当前社区物品数据库没有对应条目；不推断其当前掉落状态。", "", "| ID | 中文 | 英文 | R13 | R14 | R15 | R16 | 映射状态 |", "|---:|---|---|---|---|---|---|---|"]
for i in sorted(unique_ids, key=int):
    a = REF["uniques"][i]
    flags = " | ".join("✓" if i in selected[n] else "" for n in selected)
    lines.append(f"| {i} | {a['zh']} | {a['en']} | {flags} | {'仅本地化' if a.get('status') else '数据库+本地化'} |")
(ROOT / "docs/SELECTED_UNIQUES.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

validation = {"status": "passed_structural_and_reference_checks", "game_execution_tested": False, "rules": len(rules), "enabled": sum(r['fields']['isEnabled'] == 'true' for r in rules), "disabled": sum(r['fields']['isEnabled'] == 'false' for r in rules), "instruction_rows": sum(r['fields']['isEnabled'] == 'false' and r['fields']['color'] == '12' for r in rules), "condition_counts": dict(sorted(seen.items())), "affix_ids": len(affix_ids), "unique_ids": len(unique_ids), "unique_ids_only_in_localization": [46, 69, 248], "subtype_mappings": len(REF['subtypes']), "unique_roll_non_null_bound_count": len(roll_bounds), "changed_rule_numbers": [c['number'] for c in changes], "enabled_empty_affix_rule_numbers": [r['number'] for r in rules if r['fields']['isEnabled'] == 'true' and any(c['kind'] == 'AffixCondition' and not c['fields']['affixes'] for c in r['conditions'])], "enabled_empty_item_type_rule_numbers": [r['number'] for r in rules if r['fields']['isEnabled'] == 'true' and any(c['kind'] == 'SubTypeCondition' and not c['fields']['type'] for c in r['conditions'])]}
assert (validation['enabled'], validation['disabled'], validation['instruction_rows']) == (104, 59, 56)
assert rules[28]['fields']['isEnabled'] == 'false' and rules[28]['conditions'][0]['fields']['req'] == 'None'
assert rules[134]['conditions'][1]['fields']['advanced'] == 'false'
dump("analysis/validation.json", validation)
print(json.dumps({k: validation[k] for k in ['status', 'rules', 'enabled', 'disabled', 'affix_ids', 'unique_ids']}, ensure_ascii=False))
