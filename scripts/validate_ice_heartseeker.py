"""Audit the player's replacement template without running the game."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tool"))
import engine as e
from browser_runtime import browser_bootstrap
from build_ice_heartseeker_requirements import BUILD_ID, SOURCE, PLAYER_SOURCE, build_documents, build_planner_documents
from extract_ice_heartseeker_planner import build_snapshot
from requirements import read_document, write_document
from test_engine import first, parsed


def main():
    assert build_snapshot() == json.loads(SOURCE.read_text(encoding="utf-8"))
    documents = build_documents()
    boot = deepcopy(browser_bootstrap()["config"])
    # Keep this audit's original five-source baseline when the library grows.
    baseline = {"flay-mana-lich", "skeleton-necromancer", "flay-lich-allie-guide",
                "bleed-skeleton-roamer-guide-835", BUILD_ID}
    boot["builds"] = [b for b in boot["builds"] if b["id"] in baseline]
    template = next(b for b in boot["builds"] if b["id"] == BUILD_ID)
    assert len(boot["builds"]) == 5 and not template["enabled"]
    assert e.generate(boot) == e.generate(e.bootstrap()["config"])
    for document in documents:
        frozen = json.loads((ROOT / f"requirements/{BUILD_ID}.{document['stage']}.json").read_text(encoding="utf-8"))
        assert document == frozen == write_document(template, document["stage"])
        assert read_document(document)["profile"] == template["profiles"][document["stage"]]
    assert template["profiles"]["leveling"] == e.empty_leveling()

    scenarios, native = [], {}
    strict = {"flay-mana-lich", "skeleton-necromancer"}
    guides = {"flay-lich-allie-guide", "bleed-skeleton-roamer-guide-835"}
    selections = [{BUILD_ID}, strict | {BUILD_ID}, guides | {BUILD_ID},
                  {b["id"] for b in boot["builds"]}]
    selections += [{b["id"], BUILD_ID} for b in boot["builds"] if b["id"] != BUILD_ID]
    for selected in selections:
        for main_id in sorted(selected):
            config = deepcopy(boot)
            config["main_id"] = main_id
            for build in config["builds"]:
                build["enabled"] = build["id"] in selected
            before = deepcopy(config)
            scenario = {"selected": sorted(selected), "main": main_id}
            try:
                output = e.generate(config)
            except ValueError as error:
                limit = re.fullmatch(r"这些BD生成(\d+)条规则，超过200条。请减少选中的BD或目标分组；没有截断规则。", str(error))
                assert limit is not None and len(selected) == 5, str(error)
                scenario.update(status="rule_limit", count=int(limit[1]), truncated=False)
            else:
                assert output["count"] <= 200 and not output["warnings"]
                assert all(r["enabled"] for r in output["rules"])
                nodes = parsed(output)
                assert [int(r.findtext("Order")) for r in nodes] == list(range(output["count"]))
                assert nodes[-1].findtext("type") == "HIDE"
                predicates = [(e.signature(r), r.findtext("type")) for r in nodes]
                assert len(predicates) == len(set(predicates))
                scenario.update(status="generated", count=output["count"], sha256=output["sha256"])
                if selected in ({BUILD_ID}, guides | {BUILD_ID}):
                    key = "+".join(sorted(selected)) + "/" + main_id
                    native[key] = {"request": {"path": "/api/generate", "payload": {"config": config}}, "output": output}
            assert config == before
            scenarios.append(scenario)

    config = deepcopy(boot)
    config["main_id"] = BUILD_ID
    for build in config["builds"]:
        build["enabled"] = build["id"] == BUILD_ID
    output = e.generate(config)
    assert e.generate(config) == output
    assert output["xml"].encode("utf-8") == PLAYER_SOURCE.read_bytes()
    changes = []
    original, _ = build_planner_documents()
    for category in ("equipment", "altars", "idols"):
        for group in documents[0]["targets"][category]:
            previous = next(g for g in original["targets"][category]
                            if (g["type"], g["bases"]) == (group["type"], group["bases"]))
            added = sorted(set(group["affixes"]) - set(previous["affixes"]))
            removed = sorted(set(previous["affixes"]) - set(group["affixes"]))
            if added or removed:
                changes.append({"category": category, "type": group["type"], "added": added, "removed": removed})
    checks = []
    for group in template["profiles"]["endgame"]["equipment"]:
        for aid in group["affixes"]:
            assert e.CATALOG["affixes"][str(aid)]["special"] not in {4, 6, 7}
            row = first(output, group["type"], {aid: 7})
            assert (row["category"], row["tier"]) == ("BD目标单T7", 2), row
            checks.append({"type": group["type"], "affix": aid, "tier": 7, "category": row["category"]})
    for group in template["profiles"]["endgame"]["altars"]:
        for aid in group["affixes"]:
            row = first(output, group["type"], {aid: 1}, base=group["bases"][0], rarity="RARE", corrupted=True)
            assert (row["category"], row["tier"]) == ("祭坛一项目标", 2), row
            checks.append({"type": group["type"], "base": group["bases"][0], "affix": aid, "category": row["category"]})

    protected = {}
    changed_inputs = {f"requirements/{BUILD_ID}.endgame.json"}
    tracked = subprocess.check_output(["git", "ls-files", "-z", "sources", "templates", "filters", "requirements",
                                       "tool/engine.py", "tool/requirements.py"], cwd=ROOT).decode("utf-8").split("\0")
    for name in filter(None, tracked):
        if name in changed_inputs:
            continue
        committed = subprocess.check_output(["git", "show", f"HEAD:{name}"], cwd=ROOT)
        current = (ROOT / name).read_bytes()
        assert committed == current, name
        protected[name] = hashlib.sha256(current).hexdigest()
    result = {
        "status": "passed", "date": "2026-10-18", "gameExecutionTested": False,
        "baselineCommit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source": {"file": PLAYER_SOURCE.relative_to(ROOT).as_posix(),
                   "sha256": hashlib.sha256(PLAYER_SOURCE.read_bytes()).hexdigest(),
                   "originalFilename": documents[0]["source"]["original_filename"]},
        "completePlayerXmlEqual": True, "targetChangesFromPlanner": changes,
        "targetCounts": {key: len(values) for key, values in documents[0]["targets"].items()},
        "levelingEmpty": True, "templateInitiallySelected": False, "defaultOutputUnchanged": True,
        "requirementsRoundtrip": True, "deterministic": True, "scenarios": scenarios,
        "symbolicCases": checks, "preservedFiles": protected,
    }
    destination = ROOT / "analysis/ice-heartseeker-validation.json"
    destination.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    cache = ROOT / ".cache"
    cache.mkdir(exist_ok=True)
    (cache / "ice-heartseeker-native.json").write_text(json.dumps(native, ensure_ascii=False), encoding="utf-8")
    print(f"PASS: {len(scenarios)} combinations, {len(checks)} source target cases, {len(protected)} preserved files")


if __name__ == "__main__":
    main()
