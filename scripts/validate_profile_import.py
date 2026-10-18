"""Audit profile-only T6/T7 targets, slot provenance and packaged-engine inputs."""
from copy import deepcopy
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tool"))
from browser_runtime import browser_bootstrap, dispatch_json
from build_shuriken_marksman_requirements import BUILD_ID, build_documents, build_xml_documents
from engine import CATALOG, generate
from extract_shuriken_profiles import profile_bundle
from letools import import_profiles, decode_key
from character_save import decode_character
from requirements import read_document


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", type=Path, help="Optional pre-change file hashes and target snapshot")
    args = parser.parse_args()
    original = build_xml_documents()[0]
    updated, leveling = build_documents()
    bundle = profile_bundle()
    imported = import_profiles(bundle)
    assert read_document(updated)["profile"] == imported["profile"]
    assert sum(len(g["affixes"]) for g in updated["targets"]["equipment"]) == 28
    assert leveling == build_xml_documents()[1]
    frozen = ROOT / f"requirements/{BUILD_ID}.endgame.json"
    assert updated == json.loads(frozen.read_text(encoding="utf-8"))
    boot = browser_bootstrap()
    templates = boot["config"]["builds"]
    assert len(templates) == 6 and {b["id"] for b in templates if b["enabled"]} == {"flay-mana-lich", "skeleton-necromancer"}
    native = {}

    def record(name, request):
        output = json.loads(dispatch_json(json.dumps(request)))
        native[name] = {"request": request, "output": output}
        return output

    record("four-profile-import", {"path": "/api/profiles/import", "payload": {"bundle": bundle}})
    for index, entry in enumerate(bundle["profiles"]):
        record(f"single-profile-{index + 1}", {"path": "/api/profiles/import", "payload": {
            "bundle": {**bundle, "profiles": [entry]}}})
    personal = {"id": imported["id"], "name": imported["name"], "enabled": True,
                "profiles": {"endgame": imported["profile"], "leveling": {"affixes": [], "bases": []}},
                "requirement_sources": {"endgame": imported["source"]}}
    personal_config = {**deepcopy(boot["config"]), "main_id": personal["id"], "builds": [personal]}
    record("personal-filter", {"path": "/api/generate", "payload": {"config": personal_config}})
    native_rows = json.loads((ROOT / "sources/builds/maxroll-character-api-2026-10-18.json").read_text(encoding="utf-8"))["responses"]
    oracle_rows = json.loads((ROOT / "sources/builds/letools-character-api-2026-10-18.json").read_text(encoding="utf-8"))["responses"]
    compared_items = 0
    for raw, oracle in zip(native_rows, oracle_rows):
        actual = decode_character(raw["response"], raw["response"]["characterName"])
        expected = oracle["response"]["buildInfo"]["data"]
        pairs = [(item, expected["equipment"][slot]) for slot, item in actual["equipment"].items()]
        pairs += list(zip(actual["idols"], expected["idols"]))
        for a, b in pairs:
            for field in ("affixes", "sealedAffix", "primordialAffix", "corruptedAffix"):
                left = a.get(field, []) if field == "affixes" else ([a[field]] if a.get(field) else [])
                right = b.get(field, []) if field == "affixes" else ([b[field]] if b.get(field) else [])
                assert sorted((x["id"], x["tier"]) for x in left) == sorted((int(decode_key(x["id"])), x["tier"]) for x in right)
            compared_items += 1
    assert compared_items == 76
    excluded, accepted = {}, 0
    for source in imported["source"]["profiles"]:
        for item in source["items"]:
            for detail in item["affix_details"]:
                if not item["type"].startswith("IDOL_") and detail["target"]:
                    assert detail["origin"] == "affixes" and detail["tier"] in {6, 7}
                    accepted += 1
                if detail.get("excluded"):
                    excluded[detail["excluded"]] = excluded.get(detail["excluded"], 0) + 1
    rows = []
    # The six individual templates, every pairing with shuriken, and the full set.
    selections = [{b["id"]} for b in templates]
    selections += [{BUILD_ID, b["id"]} for b in templates if b["id"] != BUILD_ID]
    selections += [{BUILD_ID, "flay-mana-lich", "skeleton-necromancer"},
                   {BUILD_ID, "flay-lich-allie-guide", "bleed-skeleton-roamer-guide-835"},
                   {BUILD_ID, "flay-lich-allie-guide", "bleed-skeleton-roamer-guide-835", "ice-heartseeker-planner-al0dkyek"}]
    selections += [{b["id"] for b in templates}]
    for selected in selections:
        for main_id in sorted(selected):
            config = deepcopy(boot["config"])
            config["main_id"] = main_id
            for build in config["builds"]:
                build["enabled"] = build["id"] in selected
            before = deepcopy(config)
            request = {"path": "/api/generate", "payload": {"config": config}}
            result = record("+".join(sorted(selected)) + "/" + main_id, request)
            assert config == before
            if "error" in result:
                assert "超过200条" in result["error"] and len(selected) >= 4
                row = {"selected": sorted(selected), "main": main_id, "error": result["error"], "truncated": False}
            else:
                assert result["count"] <= 200 and not result["warnings"]
                row = {"selected": sorted(selected), "main": main_id, "count": result["count"], "sha256": result["sha256"]}
            rows.append(row)
    preserved = {}
    previous = json.loads(args.before.read_text(encoding="utf-8")) if args.before else None
    names = previous["preserved_files"] if previous else subprocess.check_output(["git", "ls-tree", "-r", "--name-only", "HEAD", "--", "sources", "templates", "filters", "requirements", "tool/engine.py", "tool/requirements.py"], cwd=ROOT).decode().splitlines()
    for name in names:
        if name == f"requirements/{BUILD_ID}.endgame.json":
            continue
        raw = (ROOT / name).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        assert digest == (previous["preserved_files"][name] if previous else hashlib.sha256(subprocess.check_output(["git", "show", f"HEAD:{name}"], cwd=ROOT)).hexdigest()), name
        preserved[name] = digest
    output = native[BUILD_ID + "/" + BUILD_ID]["output"]
    artifact = ROOT / "outputs/profile-t6-t7-2026-10-19/追心手里剑.xml"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(output["xml"], encoding="utf-8", newline="\n")
    result = {"date": "2026-10-19", "status": "passed", "target_counts": {k: len(v) for k, v in updated["targets"].items()},
              "rawOracleItemsWithEqualIdsTiersAndSlots": compared_items, "acceptedEquipmentAffixOccurrences": accepted,
              "excludedAffixOccurrences": excluded, "profileOnlyTemplate": True, "standaloneRules": output["count"],
              "standaloneXml": artifact.relative_to(ROOT).as_posix(),
              "new_uniques": [{"id": uid, "name": CATALOG["uniques"][str(uid)]["zh"]} for uid in updated["targets"]["uniques"] if uid not in original["targets"]["uniques"]],
              "sources": [{"url": p["url"], "items": len(p["items"])} for p in imported["source"]["profiles"]],
              "equipment_ordinary_ids": sum(len(g["affixes"]) for g in updated["targets"]["equipment"]),
              "cases": rows, "preserved_files": preserved,
              "network_reader_validation": "Fresh native API bytes from the same four profiles; decoder IDs, tiers and slot roles cross-checked against 76 frozen independent LETools items.",
              "browser_bookmark_execution_tested": False, "game_client_tested": False}
    if previous:
        old = previous["old_shuriken"]["targets"]
        result["previousTargetCounts"] = {k: len(v) for k, v in old.items()}
        result["equipmentChanges"] = [{"type": g["type"],
            "removed": sorted({a for x in old["equipment"] if x["type"] == g["type"] for a in x["affixes"]} - set(g["affixes"])),
            "added": sorted(set(g["affixes"]) - {a for x in old["equipment"] if x["type"] == g["type"] for a in x["affixes"]})}
            for g in updated["targets"]["equipment"]]
        result["removedUniqueTargets"] = sorted(set(old["uniques"]) - set(updated["targets"]["uniques"]))
    (ROOT / "analysis/profile-tier-validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    cache = ROOT / ".cache/profile-import"
    cache.mkdir(exist_ok=True)
    (cache / "tier-native.json").write_text(json.dumps(native, ensure_ascii=False), encoding="utf-8")
    print(f"PASS: {len(rows)} combinations, {len(native)} WASM inputs, {len(preserved)} frozen files unchanged")


if __name__ == "__main__":
    main()
