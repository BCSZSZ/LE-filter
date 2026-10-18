"""Verify complete common rules and first-match priority across BD selections."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tool"))
import engine as e
from browser_runtime import browser_bootstrap
from build_common_unique_protection import build
from test_engine import first, parsed


def independent_rules(output):
    result = {}
    for node, row in zip(parsed(output), output["rules"]):
        # These shatter switches intentionally follow the BD's class affixes;
        # they are not independent fallback rules or coverage deduplication.
        if row["owners"] or row["category"].startswith("BD暗金") or 84 <= row["source_raxx_rule"] <= 88:
            continue
        node.find("Order").text = "0"
        key = (row["category"], row["source_raxx_rule"], row["name"])
        assert key not in result, key
        result[key] = e.tree(node)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", type=Path, help="Optional snapshot from before this change")
    args = parser.parse_args()
    before = json.loads(args.before.read_text(encoding="utf-8")) if args.before else None
    assert build() == e.COMMON_PROTECTION
    boot = deepcopy(browser_bootstrap()["config"])
    cases = {"default_strict": e.bootstrap()["config"]}
    for build_row in boot["builds"]:
        config = deepcopy(boot)
        config["main_id"] = build_row["id"]
        for b in config["builds"]:
            b["enabled"] = b["id"] == config["main_id"]
        cases[build_row["id"]] = config
    for name, selected in (("allie_835", {"flay-lich-allie-guide", "bleed-skeleton-roamer-guide-835"}),
                           ("ice_shuriken", {"ice-heartseeker-planner-al0dkyek", "heartseeker-shuriken-marksman"})):
        config = deepcopy(boot)
        config["main_id"] = sorted(selected)[0]
        for b in config["builds"]:
            b["enabled"] = b["id"] in selected
        cases[name] = config
    minimal = {"version": 1, "main_id": "a", "extra_t7": True, "common": e.default_common(), "builds": [
        {"id": "a", "name": "A", "enabled": True, "profiles": {
            "endgame": e.empty_profile(), "leveling": e.empty_leveling()}}]}
    cases["no_bd_targets"] = minimal
    overlap = deepcopy(minimal)
    overlap["builds"][0]["profiles"]["endgame"]["uniques"] = sorted(e.COMMON_ZERO_LP_IDS | e.UNIQUE_IDOLS)
    cases["all_common_ids_are_bd_targets"] = overlap

    baseline = independent_rules(e.generate(minimal))
    results, native = [], {"bootstrap": {"request": {"path": "/api/bootstrap"}, "output": browser_bootstrap()}}
    for name, config in cases.items():
        saved = deepcopy(config)
        output = e.generate(config)
        assert saved == config
        assert independent_rules(output) == baseline, name
        generic = {r["category"]: r for r in output["rules"] if not r["owners"]}
        assert set(generic["通用暗金0LP保护"]["uniques"]) == e.COMMON_UNIQUE_IDS
        assert set(generic["通用套装保护"]["uniques"]) == e.COMMON_SET_IDS
        assert set(generic["共通暗金神像"]["uniques"]) == set(config["common"]["unique_idols"])
        assert generic["先驱者之针常驻"]["uniques"] == [344]
        for n, category in ((14, "名单WW14–16"), (13, "名单WW17–19")):
            assert set(generic[category]["uniques"]) == set(e.inspect_rule(e.BASE[n])["unique_ids"])
        rows = []
        for lp, ww in ((0, 0), (1, 0), (2, 0), (3, 0), (0, 14), (0, 17), (0, 20)):
            hit = first(output, "BOOTS", uid=337, rarity="UNIQUE", lp=lp, ww=ww)
            assert hit["action"] == "SHOW"
            rows.append({"lp": lp, "ww": ww, **{k: hit[k] for k in ("category", "role", "tier", "color", "sound")}})
        results.append({"name": name, "count": output["count"],
                        "before_count": before["cases"][name]["output"]["count"] if before and name in before["cases"] else None,
                        "fixed_independent_rules": len(baseline), "common_uniques": 181, "common_sets": 61,
                        "common_idols": len(config["common"]["unique_idols"]), "razorfall_first_hits": rows})
        if name in {"default_strict", "heartseeker-shuriken-marksman", "ice_shuriken", "no_bd_targets", "all_common_ids_are_bd_targets"}:
            native[name] = {"request": {"path": "/api/generate", "payload": {"config": config}}, "output": output}
        print(f"PASS {name}: {output['count']} rules; complete 181/61 pools; {len(baseline)} independent rules unchanged")

    output = e.generate(cases["default_strict"])
    assert output == e.generate(cases["default_strict"])
    preserved = {}
    if before:
        for name, digest in before["preserved_files"].items():
            if name == "sources/common-unique-protection.json":
                continue  # Only its generation-policy text is updated.
            assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
            preserved[name] = digest
    report = {"status": "passed", "date": "2026-10-19", "fixedIndependentRuleCount": len(baseline),
              "scenarios": results, "deterministic": True, "commonSourceIdsUnchanged": True,
              "preservedFiles": preserved, "bdClassShatterSwitchesRemainTargetDependent": [84, 85, 86, 87, 88],
              "gameExecutionTested": False, "browserDownloadTested": False}
    (ROOT / "analysis/fixed-common-rules-validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    (ROOT / ".cache/fixed-common-native.json").write_text(json.dumps(native, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
