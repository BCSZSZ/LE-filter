"""Audit the sixth template, combinations and original input preservation."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tool"))
import engine as e
from browser_runtime import browser_bootstrap
from build_shuriken_marksman_requirements import BUILD_ID, SOURCE, SOURCE_SHA256, build_documents
from requirements import read_document, write_document
from test_engine import first, parsed


def main():
    documents = build_documents()
    boot = deepcopy(browser_bootstrap()["config"])
    template = next(b for b in boot["builds"] if b["id"] == BUILD_ID)
    assert len(boot["builds"]) == 6 and not template["enabled"]
    assert e.generate(boot) == e.generate(e.bootstrap()["config"])
    for doc in documents:
        frozen = json.loads((ROOT / f"requirements/{BUILD_ID}.{doc['stage']}.json").read_text(encoding="utf-8"))
        assert doc == frozen == write_document(template, doc["stage"])
        assert read_document(doc)["profile"] == template["profiles"][doc["stage"]]
    assert template["profiles"]["leveling"] == e.empty_leveling()

    strict = {"flay-mana-lich", "skeleton-necromancer"}
    guides = {"flay-lich-allie-guide", "bleed-skeleton-roamer-guide-835"}
    ice = "ice-heartseeker-planner-al0dkyek"
    selections = [{BUILD_ID}, *[{BUILD_ID, b["id"]} for b in boot["builds"] if b["id"] != BUILD_ID],
                  strict | {BUILD_ID}, guides | {BUILD_ID}, guides | {ice, BUILD_ID},
                  {b["id"] for b in boot["builds"]}]
    scenarios, native = [], {}
    for selected in selections:
        for main_id in sorted(selected):
            config = deepcopy(boot)
            config["main_id"] = main_id
            for build in config["builds"]:
                build["enabled"] = build["id"] in selected
            before = deepcopy(config)
            row = {"selected": sorted(selected), "main": main_id}
            try:
                output = e.generate(config)
            except ValueError as error:
                limit = re.fullmatch(r"这些BD生成(\d+)条规则，超过200条。请减少选中的BD或目标分组；没有截断规则。", str(error))
                assert limit is not None and int(limit[1]) > 200 and len(selected) >= 4, str(error)
                row.update(status="rule_limit", count=int(limit[1]), truncated=False)
            else:
                assert output["count"] <= 200 and not output["warnings"]
                nodes = parsed(output)
                assert [int(n.findtext("Order")) for n in nodes] == list(range(output["count"]))
                assert all(n.findtext("isEnabled") == "true" for n in nodes)
                predicates = [(e.signature(n), n.findtext("type")) for n in nodes]
                assert len(predicates) == len(set(predicates))
                row.update(status="generated", count=output["count"], sha256=output["sha256"])
                if selected in ({BUILD_ID}, {ice, BUILD_ID}) or main_id == BUILD_ID and selected in (strict | {BUILD_ID}, guides | {BUILD_ID}):
                    native["+".join(sorted(selected)) + "/" + main_id] = {
                        "request": {"path": "/api/generate", "payload": {"config": config}}, "output": output}
            assert config == before
            scenarios.append(row)

    config = deepcopy(boot)
    config["main_id"] = BUILD_ID
    for build in config["builds"]:
        build["enabled"] = build["id"] == BUILD_ID
    output = e.generate(config)
    checks = []
    for group in template["profiles"]["endgame"]["equipment"]:
        for aid in group["affixes"]:
            assert e.CATALOG["affixes"][str(aid)]["special"] not in {4, 6, 7}
            row = first(output, group["type"], {aid: 7}, corrupted=True, fp=0)
            assert (row["category"], row["tier"]) == ("BD目标单T7", 2)
            checks.append({"type": group["type"], "affix": aid, "category": row["category"]})
    for group in template["profiles"]["endgame"]["altars"]:
        for aid in group["affixes"]:
            row = first(output, group["type"], {aid: 1}, base=group["bases"][0], rarity="RARE")
            assert (row["category"], row["tier"]) == ("祭坛一项目标", 2)
            checks.append({"type": group["type"], "base": group["bases"][0], "affix": aid, "category": row["category"]})

    protected = {}
    tracked = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", "HEAD", "--",
                                       "sources", "templates", "filters", "requirements", "tool/engine.py", "tool/requirements.py"],
                                      cwd=ROOT).decode("utf-8").splitlines()
    for name in tracked:
        committed = subprocess.check_output(["git", "show", f"HEAD:{name}"], cwd=ROOT)
        current = (ROOT / name).read_bytes()
        assert current == committed, name
        protected[name] = hashlib.sha256(current).hexdigest()
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_SHA256
    result = {
        "status": "passed", "date": "2026-10-18", "gameExecutionTested": False,
        "baselineCommit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source": {"file": SOURCE.relative_to(ROOT).as_posix(), "sha256": SOURCE_SHA256,
                   "rules": len(ET.fromstring(SOURCE.read_bytes()).find("rules")), "orderFieldsPresent": False},
        "targetCounts": {key: len(values) for key, values in documents[0]["targets"].items()},
        "levelingEmpty": True, "templateInitiallySelected": False, "defaultOutputUnchanged": True,
        "requirementsRoundtrip": True, "scenarios": scenarios, "symbolicCases": checks, "preservedFiles": protected,
    }
    (ROOT / "analysis/shuriken-marksman-validation.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    cache = ROOT / ".cache"
    cache.mkdir(exist_ok=True)
    (cache / "shuriken-marksman-native.json").write_text(json.dumps(native, ensure_ascii=False), encoding="utf-8")
    print(f"PASS: {len(scenarios)} combinations, {len(checks)} target cases, {len(protected)} preserved files")


if __name__ == "__main__":
    main()
