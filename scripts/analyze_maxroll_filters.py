"""Inventory the two frozen Maxroll Strict exports; do not generate a filter."""
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
XSI = "{http://www.w3.org/2001/XMLSchema-instance}"
MANIFEST = json.loads((ROOT / "sources/builds/maxroll-strict-manifest.json").read_text(encoding="utf-8"))
REF = json.loads((ROOT / "sources/game-reference.json").read_text(encoding="utf-8"))
SUP = json.loads((ROOT / MANIFEST["reference_supplement"]).read_text(encoding="utf-8"))


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


result = {"game_execution_tested": False, "numbering": "physical XML position; no explicit Order fields", "builds": {}}
lines = ["# Maxroll Strict 完整规则定位索引", "", "由 scripts/analyze_maxroll_filters.py 离线生成。X编号是XML物理位置，不是Raxx的Order编号；两份文件均无Order。完整条件、重复Uniques对象、nil与显示字段保存在analysis/maxroll-strict.json；原始XML保持字节不变。", ""]

for slug, source in MANIFEST["inputs"].items():
    raw = (ROOT / source["file"]).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == source["sha256"]
    text = raw.decode("utf-8-sig")
    root = ET.fromstring(raw)
    blocks = list(re.finditer(r"<Rule>.*?</Rule>", text, re.S))
    nodes = list(root.find("rules"))
    assert len(blocks) == len(nodes)
    rules = []
    for pos, (node, block) in enumerate(zip(nodes, blocks), 1):
        fields = {c.tag: value(c) for c in node if c.tag != "conditions"}
        assert "Order" not in fields
        conditions = [{"kind": c.get(XSI + "type"), "fields": value(c)} for c in node.find("conditions")]
        rules.append({"xml_position": pos, "source_lines": [text.count("\n", 0, block.start()) + 1, text.count("\n", 0, block.end()) + 1], "fields": fields, "conditions": conditions})
    affixes = {x.text for c in root.findall("rules/Rule/conditions/Condition") if c.get(XSI + "type") == "AffixCondition" for x in c.findall("affixes/int")}
    uniques = {x.text for x in root.findall("rules/Rule/conditions/Condition/Uniques/UniqueId")}
    assert affixes <= REF["affixes"].keys() | SUP["affixes"].keys()
    assert uniques <= REF["uniques"].keys() | SUP["uniques"].keys()
    planner_node = next(n for n in nodes if n.findtext("nameOverride") == "Uniques & Sets From Planner (Optional: Add More)")
    selected = {int(x.text) for x in planner_node.findall("conditions/Condition/Uniques/UniqueId")}
    build = json.loads((ROOT / f"sources/builds/{slug}.json").read_text(encoding="utf-8-sig"))
    expected = {i["uniqueID"] for i in build["items"].values() if "uniqueID" in i}
    counts = Counter(c["kind"] for r in rules for c in r["conditions"])
    row = {"source": source["file"], "sha256": source["sha256"], "metadata": {c.tag: value(c) for c in root if c.tag != "rules"}, "counts": {"rules": len(rules), "enabled": sum(r["fields"]["isEnabled"] == "true" for r in rules), "disabled": sum(r["fields"]["isEnabled"] == "false" for r in rules), "affix_ids": len(affixes), "unique_ids": len(uniques)}, "condition_counts": dict(sorted(counts.items())), "planner_unique_ids": sorted(selected), "planner_uniques_missing_from_json": sorted(selected - expected), "json_uniques_missing_from_planner_rule": sorted(expected - selected), "rules": rules}
    assert not row["json_uniques_missing_from_planner_rule"]
    result["builds"][slug] = row
    lines += ["## " + root.findtext("name"), "", "来源：[原始XML](../" + source["file"] + ")。", "", "| X编号 | 状态／动作 | 原始名称 | 条件类型，完整字段见机器索引 |", "|---:|---|---|---|"]
    for r in rules:
        f = r["fields"]
        state = ("启用" if f["isEnabled"] == "true" else "关闭") + "/" + f["type"]
        kinds = "、".join(c["kind"] for c in r["conditions"])
        lines.append(f"| X{r['xml_position']} | {state} | {(f['nameOverride'] or '无名称').replace('|', '/')} | {kinds} |")
    lines.append("")

(ROOT / "analysis/maxroll-strict.json").write_text(json.dumps(result, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
(ROOT / "docs/MAXROLL_RULE_INDEX.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")
print(json.dumps({slug: {**b["counts"], "planner_unique_ids": b["planner_unique_ids"], "extra_vs_json": b["planner_uniques_missing_from_json"]} for slug, b in result["builds"].items()}, ensure_ascii=False))
