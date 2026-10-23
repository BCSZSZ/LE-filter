"""Validate per-BD idol shape unions and rebuild the supplied XML's idol section."""
import argparse
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tool"))
import engine as e
from audit_idol_rules import idol_entry


def ordered(root):
    return sorted(root.find("rules"), key=lambda r: int(r.findtext("Order")))


def non_idol_rules(root):
    result = []
    for rule in ordered(root):
        if idol_entry(rule) is not None:
            continue
        rule = deepcopy(rule)
        rule.find("Order").text = None
        result.append(e.tree(rule))
    return result


def union_scopes(scopes):
    return sorted(set().union(*map(set, scopes))) if scopes and all(scopes) else []


def check_output(output, config):
    rows = [r for r in output["rules"] if r["category"].startswith("神像")]
    keys = [(tuple(r["owners"]), r["role"], r["category"], tuple(r["types"])) for r in rows]
    assert len(keys) == len(set(keys)), "Repeated shape within a BD/target-count tier"
    builds = {b["name"]: b for b in config["builds"] if b["enabled"]}
    for row in rows:
        assert len(row["types"]) == len(row["owners"]) == 1
        groups = [g for g in builds[row["owners"][0]]["profiles"]["endgame"]["idols"]
                  if g["type"] == row["types"][0] and g["affixes"]]
        assert row["affixes"] == [sorted({i for g in groups for i in g["affixes"]})]
        field = "pair_bases" if row["tier"] == 3 else "bases"
        assert row["bases"] == union_scopes([g.get(field, g["bases"]) for g in groups])
    return len(rows)


def compare_baseline(path):
    baseline = json.loads(path.read_text(encoding="utf-8"))
    cases = []
    for name, before in baseline["cases"].items():
        config = deepcopy(before["config"])
        try:
            after = e.generate(config)
        except ValueError as error:
            assert "超过200条" in str(error) and "没有截断规则" in str(error)
            cases.append({"case": name, "before_error": before.get("error"), "after_error": str(error)})
            continue
        assert config == before["config"]
        idol_count = check_output(after, config)
        previous = before.get("output")
        if previous:
            assert non_idol_rules(ET.fromstring(previous["xml"])) == non_idol_rules(ET.fromstring(after["xml"])), name
        cases.append({"case": name, "before": previous["count"] if previous else None,
                      "after": after["count"], "idol_rules": idol_count, "non_idol_rules_unchanged": bool(previous)})
    for name, digest in baseline["frozen_hashes"].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    return {"cases": cases, "unchanged_source_files": len(baseline["frozen_hashes"])}


def rebuild_sample(path, output_path):
    raw = path.read_bytes()
    root = ET.fromstring(raw)
    original = deepcopy(root)
    entries = [entry for rule in ordered(root) if (entry := idol_entry(rule)) is not None]
    groups = defaultdict(lambda: defaultdict(lambda: {"affixes": set(), "bases": [], "pair_bases": []}))
    old_groups = defaultdict(list)
    for rule, row in entries:
        assert len(rule.find("conditions")) == 2
        facts = e.inspect_rule(rule)
        scope = groups[(row["role"], row["owners"][0])][facts["types"][0]]
        scope["affixes"].update(facts["affix_pools"][0])
        field = "pair_bases" if row["category"] == "神像两普通目标" else "bases"
        scope[field].append(facts["subtypes"])
        old_groups[(row["role"], tuple(row["owners"]), row["category"], tuple(facts["types"]))].append(int(rule.findtext("Order")) + 1)
    config = {"version": 1, "main_id": None, "extra_t7": False, "builds": []}
    for index, ((role, name), shapes) in enumerate(groups.items()):
        profile = e.empty_profile()
        for typ, shape in shapes.items():
            assert shape["bases"], "A pair-only XML cannot recover the candidate source scope"
            profile["idols"].append({"type": typ, "affixes": sorted(shape["affixes"]),
                                     "bases": union_scopes(shape["bases"]),
                                     "pair_bases": union_scopes(shape["pair_bases"] or shape["bases"])})
        build = {"id": f"sample-{index}", "name": name, "enabled": True,
                 "profiles": {"endgame": profile, "leveling": e.empty_leveling()}}
        config["builds"].append(build)
        if role == "主":
            assert config["main_id"] is None
            config["main_id"] = build["id"]
    generated = e.generate(config)
    check_output(generated, config)
    replacements = {(row["role"], tuple(row["owners"]), row["category"], tuple(row["types"])): node
                    for node, row in zip(ordered(ET.fromstring(generated["xml"])), generated["rules"])
                    if row["category"].startswith("神像")}
    assert replacements.keys() <= old_groups.keys(), "New cue groups require explicit placement"
    seen, rules, changes = set(), [], []
    for rule in ordered(root):
        entry = idol_entry(rule)
        if entry is None:
            rules.append(rule)
            continue
        _, row = entry
        facts = e.inspect_rule(rule)
        key = (row["role"], tuple(row["owners"]), row["category"], tuple(facts["types"]))
        if key in seen or key not in replacements:
            continue
        seen.add(key)
        replacement = replacements[key]
        rule.find("conditions")[:] = deepcopy(replacement.find("conditions")[:])
        rule.find("nameOverride").text = replacement.findtext("nameOverride")
        rules.append(rule)
        facts = e.inspect_rule(rule)
        changes.append({"old_rules": old_groups[key], "new_rule": len(rules), "name": facts["name"],
                        "bases": facts["subtypes"], "affixes": [
                            {"id": i, "name": e.CATALOG["affixes"][str(i)]["zh"]} for i in facts["affix_pools"][0]]})
    for index, rule in enumerate(rules):
        rule.find("Order").text = str(index)
    root.find("rules")[:] = list(reversed(rules))
    assert non_idol_rules(original) == non_idol_rules(root)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(ET.tostring(root, encoding="utf-8", xml_declaration=True) + b"\n")
    return {"input_sha256": hashlib.sha256(raw).hexdigest(), "before": len(original.find("rules")),
            "after": len(rules), "idol_rules_before": len(entries), "idol_rules_after": len(replacements),
            "non_idol_rules_unchanged_except_order": True, "original_idol_cues_preserved": True,
            "output": output_path.relative_to(ROOT).as_posix(),
            "output_sha256": hashlib.sha256(output_path.read_bytes()).hexdigest(), "groups": changes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xml", type=Path)
    parser.add_argument("--baseline", type=Path)
    args = parser.parse_args()
    report = {"date": "2026-10-24", "engine_sha256": hashlib.sha256((ROOT / "tool/engine.py").read_bytes()).hexdigest(),
              "policy": "one rule per BD, idol type and ordinary target-count tier; union source pools/scopes", "game_client_tested": False}
    if args.baseline:
        report["generator"] = compare_baseline(args.baseline)
    if args.xml:
        report["sample"] = rebuild_sample(args.xml, ROOT / "outputs/idol-shape-2026-10-24/LE-filter-idol-shapes.xml")
    (ROOT / "analysis/idol-shape-validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("PASS:", len(report.get("generator", {}).get("cases", [])), "generator scenarios")
    if "sample" in report:
        print("PASS: sample", report["sample"]["before"], "->", report["sample"]["after"], "rules")


if __name__ == "__main__":
    main()
