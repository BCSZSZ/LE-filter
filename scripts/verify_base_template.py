"""Check template changes and bounded T7 cases; not a game emulator."""
import hashlib
import json
import xml.etree.ElementTree as ET

from build_base_template import INSTRUCTIONS, MANIFEST
from extract_raxx_variables import ROOT, XSI, read_json, value
from verify_generated_filter import predicate


def main():
    m = read_json(MANIFEST)
    raw = (ROOT / m["file"]).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == m["sha256"]
    source = (ROOT / m["source"]["local_path"]).read_bytes()
    assert hashlib.sha256(source).hexdigest() == m["source"]["sha256"]
    original = sorted(ET.fromstring(source).find("rules"), key=lambda r: int(r.findtext("Order")))
    rules = sorted(ET.fromstring(raw).find("rules"), key=lambda r: int(r.findtext("Order")))
    assert len(rules) == 162 <= 200 and [int(r.findtext("Order")) for r in rules] == list(range(162))
    assert sorted(m["source_rule_order"]) == [i for i in range(1, 164) if i != 61]
    changed = set(range(38, 49)) | {60, 62} | set(INSTRUCTIONS)
    unchanged = 0
    for r, n in zip(rules, m["source_rule_order"], strict=True):
        if n in set(range(38, 48)) | set(INSTRUCTIONS):
            before, after = value(original[n-1]), value(r)
            for field in ["Order", "nameOverride"]:
                del before[field], after[field]
            assert before == after, n
        if n in changed:
            continue
        before, after = value(original[n-1]), value(r)
        del before["Order"], after["Order"]
        assert before == after, n
        unchanged += 1
    assert hashlib.sha256((ROOT / m["full_affix_metadata"]).read_bytes()).hexdigest() == m["full_affix_metadata_sha256"]
    pool = sorted(map(int, read_json(m["full_affix_metadata"])["special_affix_type"]))
    assert pool == m["full_affix_ids"]
    groups = {l["id"]: [rules[b-1] for b in l["base_rules"]] for l in m["layers"]}
    for group in ["C2", "C3", "C4"]:
        c = next(c for c in groups[group][0].find("conditions") if c.get(XSI+"type") == "AffixCondition")
        assert [int(e.text) for e in c.findall("affixes/int")] == pool
        assert c.findtext("minOnTheSameItem") == ("2" if group == "C2" else "1")
        assert c.findtext("comparsion") == "MORE_OR_EQUAL" and c.findtext("comparsionValue") == "7"
        assert c.findtext("combinedComparsion") == "ANY" and c.findtext("advanced") == "true"
    assert groups["C4"][0].findtext("isEnabled") == "true"
    for group in ["C2", "C3", "C4"]:
        kinds = {c.get(XSI+"type") for c in groups[group][0].find("conditions")}
        assert kinds == {"AffixCondition", "SubTypeCondition"}
    good = [c for c in groups["C3"][0].find("conditions") if c.get(XSI+"type") == "AffixCondition"][1]
    assert good.findtext("advanced") == "false" and good.findtext("minOnTheSameItem") == "1"
    for r in [groups["C2"][0], groups["C4"][0]]:
        assert {e.text for e in r.findall("conditions/Condition/type/EquipmentType")} == set(m["scope_types"])
    assert max(m["layers"][0]["base_rules"]) < m["layers"][1]["base_rules"][0] < m["layers"][2]["base_rules"][0] < m["layers"][3]["base_rules"][0]
    cases = [
        ("target T7", "BOOTS", {28: 7}, "C1", True, False),
        ("two unrelated T7", "BOOTS", {503: 7, 1: 7}, "C2", True, False),
        ("three unrelated T7", "BOOTS", {503: 7, 1: 7, 17: 7}, "C2", True, False),
        ("target low tier plus T7", "BOOTS", {503: 7, 28: 4}, "C3", True, False),
        ("unrelated single T7", "BOOTS", {503: 7, 17: 5}, "C4", True, False),
        ("phase off removes fallback", "BOOTS", {503: 7}, None, False, False),
        ("phase off keeps target", "BOOTS", {28: 7}, "C1", False, False),
        ("phase off keeps multi", "BOOTS", {503: 7, 1: 7}, "C2", False, False),
        ("phase off keeps target plus T7", "BOOTS", {503: 7, 28: 4}, "C3", False, False),
        ("corrupted zero FP still kept", "BOOTS", {503: 7, 28: 4}, "C3", False, True),
        ("two IDs absent from old 623", "HELMET", {1154: 7, 1156: 7}, "C2", True, False),
        ("single ID absent from old broad pools", "HELMET", {1156: 7}, "C4", True, False),
        ("double T6 has no permanent T7 protection", "BOOTS", {503: 6, 1: 6}, None, True, False),
        ("idols are outside equipment scope", "IDOL_1x1_LAGON", {843: 7, 854: 7}, None, True, False),
        ("target T7 wins even with another T7", "BOOTS", {28: 7, 503: 7}, "C1", True, False),
    ]
    results = []
    for name, typ, affixes, expected, phase_on, corrupted in cases:
        item = {"type": typ, "base": 0, "affixes": affixes, "level": 100,
                "rarity": "EXALTED", "corrupted": corrupted, "fp": 0}
        actual = None
        for group, rs in groups.items():
            if group == "C4" and not phase_on:
                continue
            if any(all(predicate(c, item) is True for c in r.find("conditions")) for r in rs):
                actual = group
                break
        assert actual == expected, (name, actual, expected)
        results.append({"case": name, "expected": expected, "actual": actual})
    report = {"passed": True, "rule_count": len(rules), "full_affix_ids": len(pool),
              "unrelated_source_rules_unchanged": unchanged, "bounded_t7_module_cases": results,
              "checks_whole_configured_filter": False, "game_execution_tested": False}
    (ROOT / "analysis/base-template-validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in report.items() if k != "bounded_t7_module_cases"}))


if __name__ == "__main__":
    main()
