"""Compare the two Skeleton exports and screenshot targets; never write a filter."""
import hashlib
import json
import xml.etree.ElementTree as ET
from collections import Counter

from extract_raxx_variables import ROOT, family, gate_text, inspect_rule, read_json, value


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_filter(spec):
    path = ROOT / spec["file"]
    assert digest(path) == spec["sha256"], path
    root, seen, rows = ET.parse(path).getroot(), Counter(), []
    for x, node in enumerate(root.find("rules"), 1):
        row = inspect_rule(node)
        seen[row["name"]] += 1
        row.update(x=x, occurrence=seen[row["name"]], family=family(row["name"]))
        row["rule_fields"] = {c.tag: value(c) for c in node if c.tag != "conditions"}
        rows.append(row)
    return {"name": root.findtext("name"), "description": root.findtext("description"),
            "rule_count": len(rows), "enabled": sum(r["enabled"] for r in rows)}, rows


def main():
    manifest = read_json("sources/builds/skeleton-investigation-manifest.json")
    protected = [*ROOT.glob("filters/*.xml"), *ROOT.glob("templates/*"),
                 ROOT / "sources/Raxx's S5 Ultimate Filter v1.0.txt",
                 *ROOT.glob("sources/builds/maxroll-*-strict.xml"),
                 ROOT / "scripts/generate_current_filter.py",
                 ROOT / "analysis/raxx-variable-extraction.json"]
    before = {p.relative_to(ROOT).as_posix(): digest(p) for p in protected if p.is_file()}
    flags = read_json("sources/builds/strict-variable-reference.json")["special_affix_type"]
    ref = read_json("sources/game-reference.json")
    ref["affixes"].update(read_json("sources/builds/maxroll-reference-supplement.json")["affixes"])
    old_meta, old_rows = load_filter(manifest["inputs"]["strict"])
    new_meta, new_rows = load_filter(manifest["inputs"]["very_strict"])
    for row in old_rows + new_rows:
        assert all(str(i) in flags for pool in row["affix_pools"] for i in pool)
    old, new = [{(r["name"], r["occurrence"]): r for r in rows} for rows in (old_rows, new_rows)]
    changes, targets = [], []
    for key, a in old.items():
        if key not in new:
            continue
        b = new[key]
        fields = [k for k in a if k not in {"x", "rule_fields"} and a[k] != b[k]]
        metadata_fields = [k for k in sorted(a["rule_fields"].keys() | b["rule_fields"].keys()) if a["rule_fields"].get(k) != b["rule_fields"].get(k)]
        if fields or metadata_fields:
            changes.append({"name": a["name"], "occurrence": a["occurrence"],
                            "strict_x": a["x"], "very_strict_x": b["x"], "changed_fields": fields,
                            "changed_rule_fields": {k: [a["rule_fields"].get(k), b["rule_fields"].get(k)] for k in metadata_fields},
                            "strict_gate": gate_text(a), "very_strict_gate": gate_text(b)})
        if a["family"] not in {"tier7", "idol_single", "idol_bis"}:
            continue
        ids = sorted({i for pool in a["affix_pools"] for i in pool})
        assert not fields, a["name"]
        targets.append({"strict": a, "very_strict": b, "conditions_and_target_selection_identical": True,
                        "affixes": [{"id": i, **ref["affixes"][str(i)], "special_affix_type": flags[str(i)]} for i in ids],
                        "corrupted_ids": [i for i in ids if flags[str(i)] == 6],
                        "enchanted_ids": [i for i in ids if flags[str(i)] == 4],
                        "core_idol_ids": [i for i in ids if flags[str(i)] in {0, 5}] if a["family"].startswith("idol") else [],
                        "equipment_material_ids": [i for i in ids if flags[str(i)] in {0, 1}] if a["family"] == "tier7" else []})
    extraction_path = "analysis/raxx-variable-extraction.json"
    v05 = next(v for v in read_json(extraction_path)["variables"] if v["id"] == "V05")
    equipment_plan = []
    for c in v05["evidence"]:
        if not c["enabled_in_source"]:
            continue
        ids = sorted({i for i in c["affix_ids"] if flags[str(i)] not in {4, 6}})
        equipment_plan.append({"build": c["build"], "strict_x": c["x"], "types": c["types"],
                               "target_affix_ids": ids, "target_count": len(ids),
                               "single_target_t7_minimum": 1,
                               "double_target_t7_minimum": 2 if len(ids) >= 2 else None,
                               "single_affix_tier": {"comparison": "EQUAL", "value": 7}})
    for row in manifest["idol_priorities"]:
        pool = {i for t in targets if t["strict"]["family"] == "idol_bis" and t["strict"]["types"] == [row["type"]] for i in t["strict"]["affix_pools"][0]}
        assert set(row["ordered_affix_ids"]) <= pool
    current = read_json("analysis/current-filter-report.json")
    assert digest(ROOT / current["output"]) == current["output_sha256"]
    skeleton = [r for r in current["output_rules"] if "skeleton-necromancer" in r["owners"]]
    assert before == {p: digest(ROOT / p) for p in before}
    result = {"manifest": manifest, "strict": old_meta, "very_strict": new_meta,
              "comparison": {"matched_rules": len(old.keys() & new.keys()), "changed": changes,
                             "removed": [{"x": r["x"], "name": r["name"], "family": r["family"]} for k, r in old.items() if k not in new],
                             "added": [{"x": r["x"], "name": r["name"], "family": r["family"]} for k, r in new.items() if k not in old]},
              "identical_targets": targets,
              "equipment_plan_source": {"file": extraction_path, "sha256": digest(ROOT / extraction_path)},
              "equipment_target_policy": "Use each build/part filter target pool only, with corruption/enchantment references separated; no Guide/Planner additions or priority-based selection. Keep single-target T7; when n >= 2 add one condition selecting the whole pool with minimum 2 targets exactly tier 7. Never enumerate pairs into separate rules.",
              "equipment_t7_collection_plan": equipment_plan,
              "idol_count_policy": {"target_pool": "core_idol_ids", "one_target_minimum": 1,
                                    "two_targets_minimum": 2, "affix_tier": "ANY",
                                    "ignored_special_affix_types": [4, 6],
                                    "restrict_item_enchantment_or_corruption_state": False,
                                    "target_source": "Strict normal target pool; no Guide/Planner pair narrowing"},
              "very_strict_rule_inventory": [{k: r[k] for k in ("x", "name", "occurrence", "family", "enabled", "action")} for r in new_rows],
              "current_filter_sha256": current["output_sha256"],
              "current_skeleton_idols": [r for r in skeleton if r["category"].startswith("idol")],
              "current_skeleton_target_double_t7": [r for r in skeleton if r["category"] == "C2_target"],
              "protected_sha256": before, "filters_and_generator_unchanged": True,
              "game_execution_tested": False}
    (ROOT / "analysis/skeleton-strict-investigation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"strict_rules": len(old_rows), "very_strict_rules": len(new_rows),
                      "identical_target_rules": len(targets), "changed": len(changes),
                      "removed": len(old.keys() - new.keys()), "added": len(new.keys() - old.keys()),
                      "equipment_plans": len(equipment_plan),
                      "skeleton_current_idol_layers": len(result["current_skeleton_idols"]),
                      "filters_and_generator_unchanged": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
