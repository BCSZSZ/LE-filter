"""Audit an exported XML and optionally compare pre-change generator outputs.

This inspects XML predicates; it does not emulate item generation or the client.
"""
import argparse
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from copy import deepcopy
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tool"))
import engine as e


def without_rule_names(root):
    root = deepcopy(root)
    for rule in root.find("rules"):
        rule.find("nameOverride").text = None
    return e.tree(root)


def idol_entry(rule):
    name = rule.findtext("nameOverride") or ""
    match = re.match(r"^\[(主|副) (神像[一两]普通目标)\] (.*)$", name)
    if not match:
        return None
    facts = e.inspect_rule(rule)
    typ, bases = facts["types"][0], facts["subtypes"]
    type_name = e.CATALOG["types"][typ]["zh"]
    base_names = "、".join(e.CATALOG["bases"][f"{typ}:{bid}"]["zh"] for bid in bases)
    rest = match[3].split(" · 底材", 1)[0]
    scope = next(label for label in (base_names, type_name + "（底材不限）", type_name)
                 if label and rest.endswith(" " + label))
    return rule, {"role": match[1], "category": match[2], "owners": [rest[:-len(scope)].rstrip()]}


def target(rule):
    facts = e.inspect_rule(rule)
    condition = deepcopy(e.condition(rule, "AffixCondition"))
    count = int(condition.findtext("minOnTheSameItem"))
    condition.find("affixes").clear()
    condition.find("minOnTheSameItem").text = "1"
    others = [e.tree(c) for c in rule.find("conditions")
              if c.get(e.XSI + "type") not in {"SubTypeCondition", "AffixCondition"}]
    return {"number": int(rule.findtext("Order")) + 1, "name": facts["name"],
            "types": facts["types"], "bases": facts["subtypes"],
            "affixes": facts["affix_pools"][0], "count": count,
            "shape": (e.tree(condition), sorted(others, key=repr))}


def covers(earlier, later):
    # At least n from B forces at least n - |B-A| from A. No assumptions
    # about currently droppable bases or legal prefix/suffix pairs are needed.
    return (earlier["shape"] == later["shape"]
            and set(later["types"]) <= set(earlier["types"])
            and (not earlier["bases"] or bool(later["bases"])
                 and set(later["bases"]) <= set(earlier["bases"]))
            and later["count"] - len(set(later["affixes"]) - set(earlier["affixes"])) >= earlier["count"])


def compare_baseline(path):
    baseline = json.loads(path.read_text(encoding="utf-8"))
    cases = []
    for name, case in baseline["cases"].items():
        config = deepcopy(case["config"])
        try:
            current = e.generate(config)
        except ValueError as error:
            assert case.get("error") == str(error), name
            cases.append({"case": name, "same_limit_error": str(error)})
            continue
        assert config == case["config"], name
        previous = case["output"]
        assert without_rule_names(ET.fromstring(previous["xml"])) == without_rule_names(ET.fromstring(current["xml"])), name
        for old, new in zip(previous["rules"], current["rules"]):
            assert {k: v for k, v in old.items() if k != "name"} == {k: v for k, v in new.items() if k != "name"}, name
            assert old["name"] == new["name"] or old["category"].startswith("神像"), name
        for key in ("count", "enabled", "mode", "warnings"):
            assert previous[key] == current[key], (name, key)
        cases.append({"case": name, "count": current["count"], "only_idol_names_changed": True})
    for name, digest in baseline["frozen_hashes"].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    return {"before_engine_sha256": baseline["engine_sha256"],
            "after_engine_sha256": hashlib.sha256((ROOT / "tool/engine.py").read_bytes()).hexdigest(),
            "unchanged_source_files": len(baseline["frozen_hashes"]), "cases": cases}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("xml", type=Path)
    parser.add_argument("--report", type=Path, default=ROOT / "analysis/idol-rule-audit.json")
    parser.add_argument("--relabeled", type=Path)
    parser.add_argument("--baseline", type=Path)
    args = parser.parse_args()
    raw = args.xml.read_bytes()
    root = ET.fromstring(raw)
    original = deepcopy(root)
    rules = sorted(root.find("rules"), key=lambda r: int(r.findtext("Order")))
    assert [int(r.findtext("Order")) for r in rules] == list(range(len(rules)))
    entries = [entry for rule in rules if (entry := idol_entry(rule)) is not None]
    targets = [target(rule) for rule, _ in entries]
    predicates, names = defaultdict(list), defaultdict(list)
    for rule in rules:
        predicates[(e.signature(rule), rule.findtext("type"), rule.findtext("isEnabled"))].append(int(rule.findtext("Order")) + 1)
    for row in targets:
        names[row["name"]].append(row)
    repeated = []
    for name, rows in names.items():
        if len(rows) < 2:
            continue
        pairs = []
        for a, b in combinations(rows, 2):
            overlap = (not a["bases"] or not b["bases"] or bool(set(a["bases"]) & set(b["bases"])))
            pairs.append({"rules": [a["number"], b["number"]], "scope_overlap": overlap,
                          "shared_bases": sorted(set(a["bases"]) & set(b["bases"])),
                          "shared_affixes": sorted(set(a["affixes"]) & set(b["affixes"])),
                          "earlier_covers_later": covers(a, b), "later_covers_earlier": covers(b, a)})
        repeated.append({"name": name, "rules": [{k: v for k, v in row.items() if k != "shape"} for row in rows], "pairs": pairs})
    shadowed = [{"earlier": a["number"], "later": b["number"]}
                for a, b in combinations(targets, 2) if covers(a, b)]
    old_names = {int(r.findtext("Order")) + 1: r.findtext("nameOverride") for r in rules}
    e.label_idol_rules(entries)
    assert without_rule_names(original) == without_rule_names(root)
    assert len({r.findtext("nameOverride") for r, _ in entries}) == len(entries)
    changed = [{"number": int(r.findtext("Order")) + 1,
                "before": old_names[int(r.findtext("Order")) + 1], "after": r.findtext("nameOverride")}
               for r, _ in entries if old_names[int(r.findtext("Order")) + 1] != r.findtext("nameOverride")]
    report = {"date": "2026-10-24", "input_name": args.xml.name,
              "input_sha256": hashlib.sha256(raw).hexdigest(), "count": len(rules),
              "bd_idol_rule_count": len(entries),
              "same_predicates": [ns for ns in predicates.values() if len(ns) > 1],
              "wholly_shadowed_idol_rules": shadowed, "same_idol_name_groups": repeated,
              "relabeled": changed, "non_name_fields_unchanged": True,
              "scope": "XML conditions and original Python outputs; no item-spawn simulation or game-client test"}
    if args.baseline:
        report["generator_comparison"] = compare_baseline(args.baseline)
    if args.relabeled:
        args.relabeled.parent.mkdir(parents=True, exist_ok=True)
        args.relabeled.write_bytes(ET.tostring(root, encoding="utf-8", xml_declaration=True) + b"\n")
        output_path = args.relabeled.resolve()
        report["relabeled_xml"] = (output_path.relative_to(ROOT).as_posix() if output_path.is_relative_to(ROOT)
                                   else output_path.as_posix())
        report["relabeled_xml_sha256"] = hashlib.sha256(args.relabeled.read_bytes()).hexdigest()
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: {len(rules)} rules; {len(entries)} BD idol rules; {len(repeated)} repeated-name groups; "
          f"{len(shadowed)} wholly shadowed idol rules; only {len(changed)} labels changed")
    if args.baseline:
        comparison = report["generator_comparison"]
        print(f"PASS: {len(comparison['cases'])} generator scenarios; {comparison['unchanged_source_files']} source files unchanged")


if __name__ == "__main__":
    main()
