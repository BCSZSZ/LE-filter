"""Audit template union, independent profile imports and packaged-engine inputs."""
from copy import deepcopy
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
from letools import import_profiles, merge_targets


def main():
    original = build_xml_documents()[0]
    updated, leveling = build_documents()
    bundle = profile_bundle()
    imported = import_profiles(bundle)
    assert updated["targets"] == merge_targets(original["targets"], imported["profile"])
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
    for name in subprocess.check_output(["git", "ls-tree", "-r", "--name-only", "HEAD", "--", "sources", "templates", "filters", "requirements", "tool/engine.py", "tool/requirements.py"], cwd=ROOT).decode().splitlines():
        if name == f"requirements/{BUILD_ID}.endgame.json":
            continue
        raw = (ROOT / name).read_bytes()
        assert raw == subprocess.check_output(["git", "show", f"HEAD:{name}"], cwd=ROOT), name
        preserved[name] = hashlib.sha256(raw).hexdigest()
    result = {"date": "2026-10-18", "status": "passed", "target_counts": {k: len(v) for k, v in updated["targets"].items()},
              "new_uniques": [{"id": uid, "name": CATALOG["uniques"][str(uid)]["zh"]} for uid in updated["targets"]["uniques"] if uid not in original["targets"]["uniques"]],
              "sources": [{"url": p["url"], "items": len(p["items"])} for p in imported["source"]["profiles"]],
              "equipment_ordinary_ids": sum(len(g["affixes"]) for g in updated["targets"]["equipment"]),
              "cases": rows, "preserved_files": preserved,
              "network_reader_validation": "same-origin fetch sequence tested with fixtures; source fields verified against fetched LETools profile/planner JavaScript and visible UI",
              "browser_bookmark_execution_tested": False, "game_client_tested": False}
    (ROOT / "analysis/profile-import-validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    (ROOT / ".cache/profile-import/native.json").write_text(json.dumps(native, ensure_ascii=False), encoding="utf-8")
    (ROOT / ".cache/profile-import/bundle.json").write_text(json.dumps(bundle, ensure_ascii=False), encoding="utf-8")
    print(f"PASS: {len(rows)} combinations, {len(native)} WASM inputs, {len(preserved)} frozen files unchanged")


if __name__ == "__main__":
    main()
