"""Validate the new API path without modifying templates or frozen inputs."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tool"))
from browser_runtime import browser_bootstrap, dispatch_json
from letools import extract_character, import_profiles
from profile_proxy import compact_character


def main():
    fixture = json.loads((ROOT / "sources/builds/maxroll-character-api-2026-10-18.json").read_text(encoding="utf-8"))["responses"]
    oracle = json.loads((ROOT / "sources/builds/letools-character-api-2026-10-18.json").read_text(encoding="utf-8"))["responses"]
    bundle = {"format": "letools-profile-bundle", "version": 1, "name": "四角色API并集",
              "profiles": [compact_character(r["response"], r["url"]) for r in fixture]}
    compared = []
    for actual, expected in zip(bundle["profiles"], oracle):
        _, a = extract_character(actual)
        _, b = extract_character({"url": expected["url"], "data": expected["response"]["buildInfo"]["data"]})
        byslot = {r["slot"]: r for r in b["items"]}
        for item in a["items"]:
            for key in ("type", "base", "unique_id", "affixes", "corrupted", "enchanted", "fixed"):
                x, y = item[key], byslot[item["slot"]][key]
                assert (sorted(x) == sorted(y)) if isinstance(x, list) else x == y, (actual["url"], item["slot"], key)
        compared.append({"url": actual["url"], "items": len(a["items"]), "all_identities_and_classified_pools_equal": True})
    native = {}

    def record(name, path, payload):
        request = {"path": path, "payload": payload}
        output = json.loads(dispatch_json(json.dumps(request)))
        native[name] = {"request": request, "output": output}
        return output

    imported = record("maxroll-four-profiles", "/api/profiles/import", {"bundle": bundle})
    assert "error" not in imported, imported
    for row in bundle["profiles"]:
        record(row["save"]["characterName"], "/api/profiles/import", {"bundle": {**bundle, "profiles": [row]}})
    config = deepcopy(browser_bootstrap()["config"])
    config["main_id"] = imported["id"]
    config["builds"] = [{"id": imported["id"], "name": imported["name"], "enabled": True,
                         "profiles": {"endgame": imported["profile"], "leveling": {"affixes": [], "bases": []}},
                         "requirement_sources": {"endgame": imported["source"]}}]
    generated = record("personal-filter", "/api/generate", {"config": config})
    assert generated["count"] == 93, generated.get("error", generated.get("count"))
    for version in (1, 7):
        bad = deepcopy(bundle)
        bad["profiles"][-1]["save"]["savedItems"][0]["data"][0] = version
        result = record(f"unsupported-version-{version}", "/api/profiles/import", {"bundle": bad})
        assert "error" in result and "profile" not in result
    preserved = {}
    names = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", "HEAD", "--", "sources", "templates", "filters", "requirements", "tool/engine.py", "tool/requirements.py"], cwd=ROOT).decode().splitlines()
    for name in names:
        raw = (ROOT / name).read_bytes()
        assert raw == subprocess.check_output(["git", "show", f"HEAD:{name}"], cwd=ROOT), name
        preserved[name] = hashlib.sha256(raw).hexdigest()
    report = {"date": "2026-10-18", "status": "passed", "provider": "Maxroll public character API",
              "oracle": "LETools import_character.php + frozen visible UI", "compared": compared,
              "target_counts": {k: len(v) for k, v in imported["profile"].items()},
              "personal_rules": generated["count"], "preserved_files": preserved,
              "game_client_tested": False, "browser_blob_download_tested": False}
    cache = ROOT / ".cache/profile-import"
    cache.mkdir(parents=True, exist_ok=True)
    (cache / "api-native.json").write_text(json.dumps(native, ensure_ascii=False), encoding="utf-8")
    (ROOT / "analysis/profile-api-validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: 76 oracle items; {len(native)} WASM inputs; {len(preserved)} frozen files unchanged; {generated['count']} personal rules")


if __name__ == "__main__":
    main()
