"""Check the configured Base v1 filter and bounded cases, without emulating LE."""
import hashlib
import json
import xml.etree.ElementTree as ET
from copy import deepcopy

from extract_raxx_variables import inspect_rule
from generate_current_filter import ALERTS, MAIN, SECONDARY, REPORT
from generate_filter import ROOT, XSI, condition, frozen, read_json
from verify_generated_filter import first_match, ids, predicate, structure


def main():
    m = read_json(REPORT)
    raw = (ROOT / m["output"]).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == m["output_sha256"]
    assert hashlib.sha256((ROOT / "analysis/raxx-variable-extraction.json").read_bytes()).hexdigest() == m["extraction_sha256"]
    physical = list(ET.fromstring(raw).find("rules"))
    rules = sorted(physical, key=lambda r: int(r.findtext("Order")))
    rows = m["output_rules"]
    assert len(rules) == len(rows) == m["rules"] <= 200
    assert [int(r.findtext("Order")) for r in physical] == list(reversed(range(len(rules))))
    style = frozen(m["feedback_reference"])
    assert sum(r["disposition"] == "instruction_removed" for r in m["baseline_dispositions"]) == 56
    assert sum(r.findtext("type") == "HIDE" and r.findtext("isEnabled") == "true" for r in rules) == 1
    assert rules[-1].findtext("type") == "HIDE" and not len(rules[-1].find("conditions"))
    assert all(c.get(XSI + "type") for r in rules for c in r.find("conditions"))
    for r, row in zip(rules, rows, strict=True):
        assert row["number"] == int(r.findtext("Order")) + 1
        assert row["enabled"] == (r.findtext("isEnabled") == "true")
        if row["owners"]:
            assert r.findtext("color") == ("8" if MAIN in row["owners"] else "12")
        name, sound, icon, size, _, _ = ALERTS[row["alert_tier"]]
        assert r.findtext("SoundId") == sound and r.findtext("MapIconId") == icon
        assert r.findtext("BeamOverride") == "true" and r.findtext("BeamSizeOverride") == size
        assert style["sounds"][sound]["zh"] == name
        if row["alert_tier"] and row["owners"]:
            assert r.findtext("BeamColorOverride") == ("11" if row["role"] == "MAIN" else "15")
        if not row["alert_tier"]:
            assert icon == "1" and size == "NONE"
        if row["enabled"]:
            for c in r.find("conditions"):
                if c.get(XSI + "type") == "AffixCondition":
                    assert len(c.find("affixes")), row["number"]
                if c.get(XSI + "type") == "SubTypeCondition" and not len(c.find("type")):
                    assert row["source_raxx_rule"] == 37, row["number"]
    groups = {cat: [(r, row) for r, row in zip(rules, rows) if row["category"] == cat]
              for cat in ["C1", "C2", "C3", "C4", "target_t6", "idol_bis", "idol_candidate", "bd_unique"]}
    assert len(groups["C1"]) == len(groups["C3"]) == 19 and len(groups["target_t6"]) == 18
    assert len(groups["C2"]) == 3 and len(groups["C4"]) == 1
    assert len(groups["bd_unique"]) == 2
    full = set(m["base_template"]["full_affix_ids"])
    for cat in ["C2", "C3", "C4"]:
        for r, row in groups[cat]:
            a = condition(r, "AffixCondition")
            assert ids(a, "affixes/int") == full and a.findtext("advanced") == "true"
            assert a.findtext("comparsionValue") == "7" and a.findtext("comparsion") == "MORE_OR_EQUAL"
            assert a.findtext("minOnTheSameItem") == (str(row["minimum_t7"]) if cat == "C2" else "1")
            assert a.findtext("combinedComparsion") == "ANY"
            assert {c.get(XSI + "type") for c in r.find("conditions")} == {"AffixCondition", "SubTypeCondition"}
        if cat != "C3":
            assert {t.text for t in condition(groups[cat][0][0], "SubTypeCondition").find("type")} == set(m["base_template"]["scope_types"])
    assert groups["C4"][0][0].findtext("isEnabled") == "true"
    evidence = read_json("analysis/raxx-variable-extraction.json")
    wanted = {(c["build"], tuple(c["types"])): set(c["affix_ids"])
              for v in evidence["variables"] if v["id"] == "V05" for c in v["evidence"]}
    for cat in ["C1", "C3", "target_t6"]:
        for r, row in groups[cat]:
            typ = tuple(t.text for t in condition(r, "SubTypeCondition").find("type"))
            affixes = [c for c in r.find("conditions") if c.get(XSI + "type") == "AffixCondition"]
            a = affixes[1 if cat == "C3" else 0]
            for t in typ:
                assert ids(a, "affixes/int") == wanted[(row["owners"][0], (t,))]
            assert not len(condition(r, "SubTypeCondition").find("subTypes"))
            assert a.findtext("minOnTheSameItem") == "1"
            if cat == "C3":
                assert len(affixes) == 2 and a.findtext("advanced") == "false"
            else:
                assert a.findtext("advanced") == "true" and a.findtext("comparsionValue") == ("7" if cat == "C1" else "6")
            if cat == "target_t6":
                level = condition(r, "CharacterLevelCondition")
                assert (level.findtext("minimumLvl"), level.findtext("maximumLvl")) == ("0", "84")
    assert [row["minimum_t7"] for _, row in groups["C2"]] == [4, 3, 2]
    assert max(row["number"] for _, row in groups["C2"]) < min(row["number"] for _, row in groups["C1"])
    assert max(row["number"] for _, row in groups["C1"]) < min(row["number"] for _, row in groups["C3"])
    assert max(row["number"] for _, row in groups["C3"]) < m["stage_rule"]
    for cat in ["C1", "C3", "target_t6"]:
        roles = [row["role"] for _, row in groups[cat]]
        assert roles == sorted(roles, key=lambda role: role != "MAIN")
    def expanded_t6(nodes):
        result = set()
        for r in nodes:
            scope = condition(r, "SubTypeCondition")
            rest = tuple(sorted((structure(c) for c in r.find("conditions") if c is not scope), key=repr))
            for t in scope.findall("type/EquipmentType"):
                result.add((r.findtext("nameOverride").split(" - ")[0], t.text, repr(rest), tuple(sorted(ids(scope, "subTypes/int")))))
        return result
    previous = ET.parse(ROOT / "filters/Flay-Mana-Lich+Skeleton-Necromancer-v2.xml")
    old_t6 = [r for r in previous.find("rules") if "Target T6+" in r.findtext("nameOverride", "")]
    assert len(old_t6) == 19 and expanded_t6(old_t6) == expanded_t6([r for r, _ in groups["target_t6"]])
    flags = read_json("sources/builds/strict-variable-reference.json")["special_affix_type"]
    for r, _ in groups["idol_bis"] + groups["idol_candidate"]:
        a = condition(r, "AffixCondition")
        assert a.findtext("advanced") == "false"
        assert all(flags[str(i)] != 6 for i in ids(a, "affixes/int"))
    assert len(groups["idol_candidate"]) == 2 and all(row["owners"] == [MAIN] for _, row in groups["idol_candidate"])
    for r, _ in groups["bd_unique"]:
        assert [c.get(XSI + "type") for c in r.find("conditions")] == ["UniqueModifiersCondition"]
        assert all(not roll.findtext("Modifier/MinRoll") and not roll.findtext("Modifier/MaxRoll") for roll in r.findall("conditions/Condition/Uniques/Rolls/UniqueModifierWithRollId"))
    assert set().union(*(inspect_rule(r)["unique_ids"] for r, _ in groups["bd_unique"])) == set(m["target_union"])
    template = frozen(m["base_template"])
    base = dict(zip(m["base_template"]["source_rule_order"], sorted(template.find("rules"), key=lambda r: int(r.findtext("Order"))), strict=True))
    filled = {15, 29, 37, 70, 75, 81, 83, 85, 86, 87, 88, 128, 129, 136, 137}
    preserved = 0
    for r, row in zip(rules, rows):
        n = row["source_raxx_rule"]
        if (row["category"] == "base" and n not in filled) or row["category"] == "C4" or (row["category"] == "C2" and row["minimum_t7"] == 2):
            before, after = deepcopy(base[n]), deepcopy(r)
            assert structure(before.find("conditions")) == structure(after.find("conditions")), n
            assert before.findtext("type") == after.findtext("type") and before.findtext("isEnabled") == after.findtext("isEnabled")
            preserved += 1
    rare = next(r for r, row in zip(rules, rows) if row["category"] == "base" and row["source_raxx_rule"] == 15)
    old_objects = condition(base[15], "UniqueModifiersCondition").findall("Uniques")
    assert [structure(x) for x in condition(rare, "UniqueModifiersCondition").findall("Uniques")[:len(old_objects)]] == [structure(x) for x in old_objects]
    assert len(inspect_rule(rare)["unique_ids"]) == 152
    cases = [
        ("Flay axe T7", "ONE_HANDED_AXE", {2: 7}, "C1", "MAIN"),
        ("Flay dagger T7", "ONE_HANDED_DAGGER", {718: 7}, "C1", "MAIN"),
        ("Necro axe T7", "TWO_HANDED_AXE", {98: 7}, "C1", "SECONDARY"),
        ("Flay affix on Necro weapon", "TWO_HANDED_AXE", {943: 7}, "C4", "COMMON"),
        ("Weapon affix on helmet", "HELMET", {718: 7}, "C4", "COMMON"),
        ("Necro helmet target", "HELMET", {406: 7}, "C1", "SECONDARY"),
        ("Shared belt target", "BELT", {52: 7}, "C1", "MAIN"),
        ("Any double T7", "HELMET", {503: 7, 1: 7}, "C2", "COMMON"),
        ("Any triple T7", "HELMET", {503: 7, 1: 7, 17: 7}, "C2", "COMMON"),
        ("Flay low target plus T7", "HELMET", {503: 7, 34: 4}, "C3", "MAIN"),
        ("Necro low target plus T7", "HELMET", {503: 7, 406: 4}, "C3", "SECONDARY"),
        ("Stage single T7", "HELMET", {1156: 7}, "C4", "COMMON"),
        ("Phase OFF single T7", "HELMET", {1156: 7}, "base", "COMMON", {"phase_on": False}),
        ("Phase OFF target T7", "HELMET", {34: 7}, "C1", "MAIN", {"phase_on": False}),
        ("Phase OFF double T7", "HELMET", {1153: 7, 1154: 7}, "C2", "COMMON", {"phase_on": False}),
        ("Phase OFF Flay low target", "HELMET", {503: 7, 34: 4}, "C3", "MAIN", {"phase_on": False}),
        ("Phase OFF Necro low target", "HELMET", {503: 7, 406: 4}, "C3", "SECONDARY", {"phase_on": False}),
        ("Corrupted zero FP candidate", "HELMET", {503: 7, 34: 4}, "C3", "MAIN", {"corrupted": True, "phase_on": False}),
        ("Target T6 at 84", "HELMET", {34: 6}, "target_t6", "MAIN", {"level": 84}),
        ("Target T6 at 85", "HELMET", {34: 6}, "base", "COMMON", {"level": 85}),
        ("Flay minor pair Lagon", "IDOL_1x1_LAGON", {843: 1, 854: 1}, "idol_bis", "MAIN"),
        ("Flay minor pair Weaver", "IDOL_1x1_LAGON", {843: 1, 854: 1}, "idol_bis", "MAIN", {"base": 1}),
        ("Flay minor one target", "IDOL_1x1_LAGON", {843: 1}, "idol_candidate", "MAIN"),
        ("Flay corruption is not second target", "IDOL_1x1_LAGON", {843: 1, 1070: 1}, "idol_candidate", "MAIN", {"corrupted": True}),
        ("Flay corruption-only idol", "IDOL_1x1_LAGON", {1069: 1, 1070: 1}, "base", "COMMON", {"corrupted": True}),
        ("Flay stout pair", "IDOL_1x2", {876: 1, 886: 1}, "idol_bis", "MAIN"),
        ("Flay stout single ignite", "IDOL_1x2", {876: 1}, "idol_candidate", "MAIN"),
        ("Flay stout optional resist", "IDOL_1x2", {886: 1}, "idol_candidate", "MAIN"),
        ("Necro ordinary idol pair", "IDOL_1x1_LAGON", {846: 1, 851: 1}, "idol_bis", "SECONDARY", {"base": 1}),
        ("Necro corruption is not second target", "IDOL_1x1_LAGON", {846: 1, 1068: 1}, "base", "COMMON", {"base": 1, "corrupted": True}),
        ("Necro large ordinary pair", "IDOL_1x3", {941: 1, 287: 1}, "idol_bis", "SECONDARY", {"base": 13}),
        ("Double T7 takes precedence over target", "HELMET", {34: 7, 503: 7}, "C2", "COMMON"),
        ("Any quadruple T7", "HELMET", {503: 7, 1: 7, 17: 7, 34: 7}, "C2", "COMMON"),
        ("Any T8 selected by original pool", "HELMET", {34: 8}, "base", "COMMON"),
        ("T8 outside old pool with phase OFF", "HELMET", {1156: 8}, "base", "COMMON", {"phase_on": False}),
        ("Experimental T7 takes precedence over phase", "BOOTS", {674: 7}, "base", "COMMON"),
        ("Experimental target T6 takes precedence over transition", "BOOTS", {676: 6}, "base", "COMMON", {"level": 84}),
        ("Legendary with T8", "HELMET", {34: 8}, "base", "COMMON", {"rarity": "LEGENDARY"}),
        ("Legendary with four T7", "HELMET", {503: 7, 1: 7, 17: 7, 34: 7}, "C2", "COMMON", {"rarity": "LEGENDARY"}),
        ("Legendary fallback", "HELMET", {}, "base", "COMMON", {"rarity": "LEGENDARY"}),
        ("Shared Eternal Gauntlets", "GLOVES", {}, "target_base", "MAIN", {"base": 12, "rarity": "NORMAL"}),
        ("Flay altar any tier", "IDOL_ALTAR", {1089: 1}, "altar", "MAIN", {"base": 3}),
        ("Necro altar any tier", "IDOL_ALTAR", {1093: 1}, "altar", "SECONDARY", {"base": 7}),
    ]
    results = []
    for name, typ, affixes, category, role, *options in cases:
        item = {"type": typ, "affixes": affixes, "level": 100, "base": 0, "fp": 0,
                "rarity": "NORMAL" if typ.startswith("IDOL_") else "EXALTED", "corrupted": False, "phase_on": True}
        item.update(options[0] if options else {})
        active = rules if item["phase_on"] else [r for r in rules if int(r.findtext("Order")) + 1 != m["stage_rule"]]
        number = first_match(active, item)
        assert number is not None, name
        row = rows[number - 1]
        assert (row["category"], row["role"]) == (category, role), (name, row["name"])
        if category == "base" and row["source_raxx_rule"] not in {8, 37, 68}:
            assert rules[number - 1].findtext("type") == "HIDE", name
        if "Experimental" in name:
            assert row["source_raxx_rule"] == 68 and row["alert_tier"] == 1
        if category == "C2":
            assert row["alert_tier"] == {2: 1, 3: 3, 4: 4}[sum(t >= 7 for t in affixes.values())]
        results.append({"case": name, "matched_rule": number, "category": category, "role": role, "sound": row["sound_name"]})
    graduation = {r.findtext("SoundId") for r, _ in groups["idol_bis"]}
    candidate = {r.findtext("SoundId") for r, _ in groups["idol_candidate"]}
    assert graduation == {"9"} and candidate == {"6"}
    t8 = next(r for r, row in zip(rules, rows) if row["source_raxx_rule"] == 37)
    assert ids(condition(t8, "AffixCondition"), "affixes/int") == full
    # Only separate LP or WW ranges and unbounded unique selectors are modelled.
    def unique_match(item):
        for r, row in zip(rules, rows):
            if not row["enabled"]:
                continue
            checks = []
            for c in r.find("conditions"):
                kind = c.get(XSI + "type")
                if kind == "UniqueModifiersCondition":
                    u = next((u for u in c.findall("Uniques") if int(u.findtext("UniqueId")) == item["uid"]), None)
                    if u is not None and any(e.text for e in u.findall("Rolls/UniqueModifierWithRollId/Modifier/*")):
                        checks.append(None)
                    else:
                        checks.append(u is not None)
                elif kind == "PotentialCondition":
                    active = {e.tag for e in c if e.text}
                    dimension = "LegendaryPotential" if any("Legendary" in t for t in active) else "WeaversWill"
                    assert active and all(dimension in t for t in active)
                    value = item["lp"] if dimension == "LegendaryPotential" else item["ww"]
                    low, high = c.findtext("Min" + dimension), c.findtext("Max" + dimension)
                    checks.append((not low or value >= int(low)) and (not high or value <= int(high)))
                else:
                    checks.append(predicate(c, item))
            if False in checks:
                continue
            assert None not in checks, "Unique roll bounds remain unmodelled"
            return row
        raise AssertionError("Missing final hide")
    unique_cases = [(f"Target {uid} LP={lp}", uid, lp, 0, 1 if lp == 0 else 3) for uid in m["target_union"] for lp in [0, 1]]
    unique_cases += [("Any unique LP=" + str(lp), 99999, lp, 0, {1: 2, 2: 3, 3: 4, 4: 4}[lp]) for lp in [1, 2, 3, 4]]
    unique_cases += [("Target WW=" + str(ww), 416, 0, ww, tier) for ww, tier in [(13, 1), (14, 2), (16, 2), (17, 3), (19, 3), (20, 4), (28, 4)]]
    for name, uid, lp, ww, tier in unique_cases:
        item = {"type": "BELT", "affixes": {}, "level": 100, "base": 0, "fp": 0, "rarity": "UNIQUE", "corrupted": False, "uid": uid, "lp": lp, "ww": ww}
        row = unique_match(item)
        assert row["alert_tier"] == tier, (name, row["name"])
        if lp == 0 and ww == 0 or lp == 1 and uid in m["target_union"]:
            assert row["role"] == ("MAIN" if uid in m["target_ids"][MAIN] else "SECONDARY")
        results.append({"case": name, "matched_rule": row["number"], "category": row["category"], "role": row["role"], "sound": row["sound_name"]})
    result = {"passed": True, "rules": len(rules), "enabled": m["enabled"], "stage_rule": m["stage_rule"],
              "full_affix_ids": len(full), "target_uniques": len(m["target_union"]),
              "unchanged_condition_rules": preserved, "t6_expansion_equal_to_v2": True, "sound_and_icon_invariants": True, "bounded_cases": results,
              "game_execution_tested": False, "sealed_affix_counting_tested": False}
    (ROOT / "analysis/current-filter-validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in result.items() if k != "bounded_cases"}))


if __name__ == "__main__":
    main()
