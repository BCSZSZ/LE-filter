"""Audit the shared double-T7 XML policy; no game client is executed."""

from collections import Counter
from copy import deepcopy
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tool"))
import engine as e
from browser_runtime import browser_bootstrap
from test_engine import first, parsed


def main():
    boot = browser_bootstrap()["config"]
    strict = {"flay-mana-lich", "skeleton-necromancer"}
    guides = {"flay-lich-allie-guide", "bleed-skeleton-roamer-guide-835"}
    selected_sets = [*[{b["id"]} for b in boot["builds"]], strict, guides,
                     {b["id"] for b in boot["builds"]}]
    scenarios = []
    for selected in selected_sets:
        for main_id in sorted(selected):
            config = deepcopy(boot)
            config["main_id"] = main_id
            for build in config["builds"]:
                build["enabled"] = build["id"] in selected
            before = deepcopy(config)
            output = e.generate(config)
            assert config == before
            nodes = parsed(output)
            signatures = [(e.signature(n), n.findtext("type")) for n in nodes]
            assert len(signatures) == len(set(signatures))
            counts = Counter(r["category"] for r in output["rules"])
            assert not counts["BD双目标T7"]
            assert counts["任意双T7"] == 1 and counts["三词条双T7"] == 2
            assert output["count"] <= 200
            assert all(r["enabled"] for r in output["rules"])
            scenarios.append({"selected": sorted(selected), "main": main_id,
                              "count": output["count"], "sha256": output["sha256"],
                              "targetCometRules": counts["双T7含BD目标T7"],
                              "emptySlotRules": counts["三词条双T7"],
                              "duplicatePredicates": 0, "inputUnchanged": True})
    config = deepcopy(e.bootstrap()["config"])
    before = deepcopy(config)
    output = e.generate(config)
    assert e.generate(config)["xml"] == output["xml"]
    assert config == before
    cases = [
        ({503: 7, 17: 7, 1: 7}, "任意至少三T7", 4, {}),
        ({34: 7, 503: 7, 17: 2, 1: 2}, "双T7含BD目标T7", 4, {}),
        ({406: 7, 503: 7, 17: 2, 1: 2}, "双T7含BD目标T7", 4, {}),
        ({34: 7, 406: 7, 17: 2, 1: 2}, "双T7含BD目标T7", 4, {}),
        ({503: 7, 17: 7, 1: 2}, "三词条双T7", 4, {}),
        ({503: 7, 2: 2, 17: 7}, "三词条双T7", 4, {}),
        ({34: 4, 503: 7, 17: 7, 1: 2}, "任意双T7", 3, {}),
        ({34: 8, 503: 7, 17: 7, 1: 2}, "任意双T7", 3, {}),
        ({503: 7, 17: 7}, "任意双T7", 3, {}),
        ({34: 7, 503: 8}, "BD目标单T7", 2, {}),
        ({503: 7, 17: 7, 1: 2, 45: 3}, "三词条双T7", 4, {"sealed_affixes": [45]}),
        ({503: 7, 2: 2, 17: 7, 1: 2, 45: 3}, "任意双T7", 3, {"sealed_affixes": [45]}),
    ]
    results = []
    for affixes, category, tier, extra in cases:
        row = first(output, affixes=affixes, **extra)
        assert (row["category"], row["tier"]) == (category, tier), row
        results.append({"affixes": affixes, **extra, "category": category,
                        "tier": tier, "nameColor": row["color"]})
    protected = [*ROOT.glob("filters/*.xml"), *ROOT.glob("templates/*"),
                 *ROOT.glob("sources/*"), *ROOT.glob("sources/builds/*"),
                 *ROOT.glob("sources/video-era/*"), *ROOT.glob("requirements/*.json"),
                 *ROOT.glob("tool/probability_web/*"),
                 ROOT / "analysis/prophecy-probabilities.json"]
    hashes = {}
    for path in sorted(set(p for p in protected if p.is_file())):
        relative = path.relative_to(ROOT).as_posix()
        committed = subprocess.run(["git", "show", f"HEAD:{relative}"], cwd=ROOT,
                                   capture_output=True)
        if committed.returncode:
            continue
        assert path.read_bytes() == committed.stdout, relative
        hashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    result = {
        "status": "passed", "date": "2026-10-17", "gameExecutionTested": False,
        "baselineCommit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "policy": {"comet": ["at least 3 exact T7", "at least 2 exact T7 and at least 1 matching BD target T7",
                              "at least 2 exact T7 and exactly 3 non-sealed affixes"],
                   "inspiration": "remaining at least 2 exact T7", "removedIndependentPairLayer": True},
        "nativeEvidence": {
            "gameVersion": "1.5.2.2",
            "GameAssemblySHA256": "d5f9fb458f0e9878e697a92b590a586a52fd77e645f8bf87bb4f2b74c6c56567",
            "AffixCountCondition.Match": "0x19685C0", "GetNonSealedPrefixAndSuffixCount": "0x1201DD0",
            "fields": {"minPrefixes": "0x10", "maxPrefixes": "0x18", "minSuffixes": "0x20",
                       "maxSuffixes": "0x28", "sealedType": "0x30"},
            "emptySlotCompositions": [[1, 2], [2, 1]], "sealedType": "Any"},
        "aggregation": "Only one-target Comet predicates with equal type/base scopes union their enabled BD pools",
        "scenarios": scenarios, "symbolicCases": results, "defaultCount": output["count"],
        "defaultDeterministic": True, "frozenFilesByteIdentical": hashes,
    }
    destination = ROOT / "analysis/comet-double-t7-validation.json"
    destination.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"PASS: {len(scenarios)} configurations, {len(results)} cases, {len(hashes)} preserved files")


if __name__ == "__main__":
    main()
