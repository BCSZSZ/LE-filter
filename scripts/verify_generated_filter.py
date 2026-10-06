"""Structural transfer checks and bounded symbolic cases; not a game emulator."""
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
XSI = "{http://www.w3.org/2001/XMLSchema-instance}"


def structure(node):
    return (node.tag, sorted(node.attrib.items()), (node.text or "").strip(),
            sorted((structure(c) for c in node), key=repr))


def affix(rule):
    return next(c for c in rule.find("conditions") if c.get(XSI + "type") == "AffixCondition")


def ids(node, path):
    return {int(e.text) for e in node.findall(path)}


def compare(value, op, threshold):
    return {"ANY": True, "EQUAL": value == threshold,
            "MORE_OR_EQUAL": value >= threshold, "MORE": value > threshold}[op]


def predicate(c, item):
    """Model only explicit fields used in these hand-picked equipment cases."""
    kind = c.get(XSI + "type")
    if kind == "SubTypeCondition":
        types = [t.text for t in c.findall("type/EquipmentType")]
        bases = ids(c, "subTypes/int")
        return (not types or item["type"] in types) and (not bases or item["base"] in bases)
    if kind == "CharacterLevelCondition":
        return int(c.findtext("minimumLvl")) <= item["level"] <= int(c.findtext("maximumLvl"))
    if kind == "RarityCondition":
        return item["rarity"] in c.findtext("rarity").split()
    if kind == "CorruptionCondition":
        return item["corrupted"] == (c.findtext("Corruption") == "OnlyCorrupted")
    if kind == "AffixCondition":
        selected = ids(c, "affixes/int")
        tiers = [t for i, t in item["affixes"].items() if not selected or i in selected]
        advanced = c.findtext("advanced") == "true"
        if advanced:
            tiers = [t for t in tiers if compare(t, c.findtext("comparsion"), int(c.findtext("comparsionValue")))]
        return len(tiers) >= int(c.findtext("minOnTheSameItem")) and (not advanced or compare(sum(tiers), c.findtext("combinedComparsion"), int(c.findtext("combinedComparsionValue"))))
    if kind == "PotentialCondition":
        # LP/WW combination and sealed-affix counting deliberately remain unmodelled.
        if any(e.text and e.get(XSI + "nil") != "true" and "Forging" not in e.tag for e in c):
            return None
        low, high = c.findtext("MinForgingPotential"), c.findtext("MaxForgingPotential")
        return (not low or item["fp"] >= int(low)) and (not high or item["fp"] <= int(high))
    if kind == "UniqueModifiersCondition":
        return False  # These symbolic cases are ordinary equipment, not uniques.
    if kind in {"GlyphCondition", "KeysCondition", "ResonancesCondition", "RuneCondition", "CraftingMaterialsCondition", "WovenEchoesCondition"}:
        return False  # Equipment cases cannot be crafting resources.
    return None


def first_match(rules, item):
    for r in rules:
        if r.findtext("isEnabled") != "true":
            continue
        values = [predicate(c, item) for c in r.find("conditions")]
        if False in values:
            continue
        return None if None in values else int(r.findtext("Order")) + 1
    raise AssertionError("No final hide rule")


def verify():
    report = json.loads((ROOT / "analysis/transfer-report.json").read_text(encoding="utf-8"))
    raw = (ROOT / report["output"]).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == report["output_sha256"]
    physical = list(ET.fromstring(raw).find("rules"))
    rules = sorted(physical, key=lambda r: int(r.findtext("Order")))
    assert [int(r.findtext("Order")) for r in physical] == list(reversed(range(len(rules))))
    assert len(rules) <= 200 and len(rules) == report["rules"]
    assert [r.findtext("type") for r in rules if r.findtext("isEnabled") == "true" and r.findtext("type") == "HIDE"] == ["HIDE"]
    assert rules[-1].findtext("type") == "HIDE" and not list(rules[-1].find("conditions"))
    assert [r["template"] for r in report["output_rules"]] == sorted(r["template"] for r in report["output_rules"])
    assert sum(r["disposition"] == "player_instruction_removed" for r in report["baseline"]) == 56
    for r in rules:
        if r.findtext("isEnabled") != "true":
            continue
        for c in r.find("conditions"):
            if c.get(XSI + "type") == "AffixCondition":
                assert c.findall("affixes/int"), r.findtext("nameOverride")
            if c.get(XSI + "type") == "SubTypeCondition" and not c.findall("type/EquipmentType"):
                assert int(r.findtext("Order")) + 1 == next(x["number"] for x in report["output_rules"] if x["template"] == 37)

    manifest = json.loads((ROOT / "sources/builds/maxroll-strict-manifest.json").read_text(encoding="utf-8"))
    sources = {slug: list(ET.parse(ROOT / s["file"]).getroot().find("rules")) for slug, s in manifest["inputs"].items()}
    assert len(report["strict"]) == sum(len(s) for s in sources.values()) == 271
    exact, tier = 0, 0
    for source in report["strict"]:
        r = sources[source["build"]][source["xml_position"] - 1]
        if source["disposition"] != "mapped_conditions":
            continue
        numbers = source["output_numbers"]
        assert numbers, source
        name = r.findtext("nameOverride") or ""
        if re.fullmatch(r"Tier [67] - (?!Class Specific Affixes).+", name):
            fragments = [rules[n - 1] for n in numbers if report["output_rules"][n - 1]["category"] == "tier" + name[5]]
            assert set().union(*(ids(affix(f), "affixes/int") for f in fragments)) == ids(affix(r), "affixes/int")
            expected = deepcopy(r.find("conditions"))
            next(c for c in expected if c.get(XSI + "type") == "AffixCondition").find("affixes").clear()
            for fragment in fragments:
                actual = deepcopy(fragment.find("conditions"))
                next(c for c in actual if c.get(XSI + "type") == "AffixCondition").find("affixes").clear()
                assert structure(actual) == structure(expected)
                assert not fragment.find("conditions").findall("Condition/maximumLvl")
            tier += 1
        else:
            assert any(structure(rules[n - 1].find("conditions")) == structure(r.find("conditions")) for n in numbers), source
            exact += 1

    target_ids = set().union(*(set(x) for x in report["target_unique_ids"].values()))
    protected = set()
    for r, row in zip(rules, report["output_rules"]):
        if row["category"] == "build_unique" and not any(c.get(XSI + "type") == "PotentialCondition" for c in r.find("conditions")):
            protected |= ids(r, "conditions/Condition/Uniques/UniqueId")
            assert row["number"] < report["output_rules"][-1]["number"]
    assert protected == target_ids and len(target_ids) == 25
    assert {125, 294, 348, 353, 366, 415, 300, 477} <= protected

    # Each case checks an outcome, not the generator's implementation steps.
    cases = [
        ("100级巫妖T6魔力头盔", "HELMET", 0, {34: 6}, False, 0, "FLAY", "tier6"),
        ("100级死灵T6流血头盔", "HELMET", 15, {406: 6}, False, 0, "NECRO", "tier6"),
        ("死灵T7随从持续伤害双手斧", "TWO_HANDED_AXE", 8, {98: 7}, False, 0, "NECRO", "tier7"),
        ("随从持续伤害单手斧不串入死灵装备池", "ONE_HANDED_AXE", 0, {98: 6}, False, 0, None, "hide"),
        ("两BD共享T7移速鞋", "BOOTS", 0, {28: 7}, False, 0, "SHARED", "tier7"),
        ("两BD共享T6智力遗物", "RELIC", 0, {502: 6}, False, 0, "SHARED", "tier6"),
        ("普通阶实验传送鞋", "BOOTS", 0, {679: 5}, False, 0, "NECRO", "experimental"),
        ("目标词缀T5加另一个T7可做Havoc", "BOOTS", 0, {25: 7, 679: 5}, False, 20, "NECRO", "crafting"),
        ("零FP不能误称Havoc但保留实验素材", "BOOTS", 0, {25: 7, 679: 5}, False, 0, "NECRO", "experimental_exalted"),
        ("死灵底材双词缀合计T4", "RING", 9, {70: 2, 825: 2}, False, 0, "NECRO", "rare_base"),
        ("同底材单词缀T4不满足数量2", "RING", 9, {70: 4}, False, 0, None, "hide"),
        ("巫妖魔力神像精确双词缀", "IDOL_1x1_LAGON", 1, {843: 1, 854: 1}, False, 0, "FLAY", "idol_pair"),
        ("错形状不标成目标配对但保留Strict通用Weaver", "IDOL_2x1", 1, {843: 1, 854: 1}, False, 0, "SHARED", "idol_generic"),
        ("点燃与虚弱备用神像", "IDOL_1x2", 1, {876: 1, 891: 1}, False, 0, "FLAY", "guide_idol"),
        ("100级仍保留Strict单词缀神像", "IDOL_1x1_LAGON", 0, {843: 1}, False, 0, "FLAY", "idol_one_affix"),
        ("死灵三词缀神像未压成两条", "IDOL_1x3", 8, {941: 1, 287: 1, 897: 7}, False, 0, "NECRO", "idol_pair"),
        ("死灵T7祭坛", "IDOL_ALTAR", 7, {1093: 7}, False, 0, "NECRO", "altar"),
        ("巫妖腐化魔力祭坛", "IDOL_ALTAR", 3, {1105: 7}, True, 0, "FLAY", "altar"),
        ("目标腐化属性有独立收集分支", "HELMET", 0, {1022: 1}, True, 0, "FLAY", "corrupted_supplement"),
        ("未请求的普通武器词缀隐藏", "ONE_HANDED_AXE", 0, {98: 5}, False, 0, None, "hide"),
    ]
    outcomes = []
    for label, type_name, base, affixes, corrupted, fp, owner, category in cases:
        item = {"type": type_name, "base": base, "affixes": affixes, "corrupted": corrupted, "fp": fp, "level": 100,
                "rarity": "EXALTED" if max(affixes.values()) >= 6 else "RARE"}
        number = first_match(rules, item)
        assert number is not None, label + ": unmodelled condition"
        row = report["output_rules"][number - 1]
        assert (rules[number - 1].findtext("type") == "HIDE") == (category == "hide"), (label, row)
        if category != "hide":
            assert row["category"] == category, (label, row)
            actual_owner = row["owners"][0] if len(row["owners"]) == 1 else "SHARED"
            assert owner == actual_owner, (label, row)
        outcomes.append({"case": label, "number": number, "name": row["name"]})
    unknown = {"type": "HELMET", "base": 0, "affixes": {503: 7}, "corrupted": False, "fp": 52, "level": 100, "rarity": "EXALTED"}
    assert first_match(rules, unknown) is None, "Do not invent AffixCountCondition semantics"
    result = {"game_execution_tested": False, "passed": True, "rules": len(rules), "target_uniques_without_potential_gate": len(protected),
              "strict_tier_rules_partition_verified": tier, "other_strict_predicates_preserved": exact,
              "symbolic_cases": outcomes, "unmodelled_case": "FP52 and sealedType=NotSealed requires client verification; predictor returns unknown"}
    (ROOT / "analysis/generated-validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"passed": True, "rules": len(rules), "unique_ids": len(protected), "tier_rules": tier, "exact_rules": exact, "symbolic_cases": len(outcomes)}))


if __name__ == "__main__":
    verify()
