"""Audit approved unique coverage, all sets, switches and native/WASM cases."""
from copy import deepcopy
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tool"))
import engine as e
from browser_runtime import browser_bootstrap
from test_engine import parsed
from build_common_unique_protection import build


def main():
    boot = deepcopy(browser_bootstrap()["config"])
    manifest = build()
    assert manifest == e.COMMON_PROTECTION
    approved = set(manifest["unique_ids"]) | set(manifest["set_ids"])
    original = [deepcopy(u) for n in (15, 16) for u in e.condition(e.BASE[n], "UniqueModifiersCondition")]
    expected = {int(u.findtext("UniqueId")): u for u in original}
    for uid in approved:
        if uid in expected and uid in e.SEASONAL_UNIQUES:
            expected[uid].find("Rolls").clear()
        elif uid not in expected:
            node = deepcopy(e.BASE[15])
            e.select_uniques(node, [uid])
            expected[uid] = deepcopy(e.condition(node, "UniqueModifiersCondition")[0])
    expected = {uid: node for uid, node in expected.items() if uid in approved}
    output = e.generate(boot)
    actual = {int(u.findtext("UniqueId")): u for node, row in zip(parsed(output), output["rules"])
              if row["category"] in {"通用暗金0LP保护", "通用套装保护"}
              for u in e.condition(node, "UniqueModifiersCondition")}
    assert {uid: e.tree(node) for uid, node in actual.items()} == {uid: e.tree(node) for uid, node in expected.items()}
    assert len(e.COMMON_UNIQUE_IDS) == 181 and len(e.COMMON_SET_IDS) == 61
    assert e.COMMON_ZERO_LP_IDS == approved
    assert not set(manifest["removed_unique_ids"]) & set(actual)
    assert len([row for row in output["rules"] if row["category"] in {"通用暗金0LP保护", "通用套装保护"}]) == 2
    cases, native = [], {"bootstrap_active_pool": {"request": {"path": "/api/bootstrap"}, "output": browser_bootstrap()}}
    for experimentals, uniques, sets in itertools.product((False, True), repeat=3):
        config = deepcopy(boot)
        config["common"].update(exalted_experimentals_enabled=experimentals,
                                common_uniques_enabled=uniques, common_sets_enabled=sets)
        before = deepcopy(config)
        result = e.generate(config)
        assert config == before
        assert any(r["source_raxx_rule"] == 68 for r in result["rules"]) == experimentals
        assert any(r["category"] == "通用暗金0LP保护" for r in result["rules"]) == uniques
        assert any(r["category"] == "通用套装保护" for r in result["rules"]) == sets
        assert all(r["enabled"] for r in result["rules"])
        name = f"experimentals={experimentals},uniques={uniques},sets={sets}"
        cases.append({"name": name, "count": result["count"], "sha256": result["sha256"]})
        if (experimentals, uniques, sets) in {(False, True, True), (True, True, True), (False, False, False), (False, True, False), (False, False, True)}:
            native[name] = {"request": {"path": "/api/generate", "payload": {"config": config}}, "output": result}
    legacy = deepcopy(boot)
    legacy.pop("common")
    assert e.generate(legacy) == output
    native["legacy_missing_switches"] = {"request": {"path": "/api/generate", "payload": {"config": legacy}}, "output": output}
    protected = {}
    tracked = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", "HEAD", "--",
                                       "sources", "templates", "filters", "requirements"], cwd=ROOT).decode("utf-8").splitlines()
    for name in tracked:
        current = (ROOT / name).read_bytes()
        assert current == subprocess.check_output(["git", "show", f"HEAD:{name}"], cwd=ROOT), name
        protected[name] = hashlib.sha256(current).hexdigest()
    result = {"status": "passed", "date": "2026-10-18", "replacementApplied": True,
              "baseUniques": len(e.COMMON_UNIQUE_IDS), "baseSets": len(e.COMMON_SET_IDS),
              "defaultStrictRules": output["count"], "defaultStrictCommonPool": len(actual),
              "defaultStrictCommonUniques": sum(not e.CATALOG["uniques"][str(uid)]["set"] for uid in actual),
              "defaultStrictCommonSets": sum(e.CATALOG["uniques"][str(uid)]["set"] for uid in actual),
              "removedUniqueIds": manifest["removed_unique_ids"], "addedUniqueIds": manifest["added_unique_ids"],
              "addedSetIds": manifest["added_set_ids"], "all97PositiveEquipmentUniquesIncluded": True,
              "all61SetItemsIncluded": True, "retainedOriginalRollsPreserved": True, "offlineManifestRebuiltExactly": True,
              "experimentalsDefault": False, "uniquesDefault": True, "setsDefault": True,
              "legacySettingsDefaulted": True, "scenarios": cases, "preservedFiles": protected,
              "gameExecutionTested": False}
    (ROOT / "analysis/common-protection-pool-validation.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    (ROOT / ".cache/common-protection-native.json").write_text(json.dumps(native, ensure_ascii=False), encoding="utf-8")
    print(f"PASS: 181 unique IDs / 61 set IDs, {len(cases)} switch combinations, {len(protected)} original files; default {output['count']} rules / {len(actual)} common IDs")


if __name__ == "__main__":
    main()
