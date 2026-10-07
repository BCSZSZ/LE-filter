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
                 ROOT / "scripts/generate_current_filter.py"]
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
    priority_gaps = []
    for row in manifest["equipment_priorities"]:
        target = next(r for r in targets if r["strict"]["family"] == "tier7" and r["strict"]["types"] == [row["type"]])
        priority_gaps.append({**row, "absent_from_part_t7_pool": sorted(set(row["ordered_affix_ids"]) - set(target["strict"]["affix_pools"][0]))})
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
              "identical_targets": targets, "screenshot_equipment_coverage": priority_gaps,
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
                      "screenshot_equipment_coverage": priority_gaps,
                      "skeleton_current_idol_layers": len(result["current_skeleton_idols"]),
                      "filters_and_generator_unchanged": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
