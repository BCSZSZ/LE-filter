"""Decode the frozen, visibly selected LETools UI fields; no network."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tool"))
from letools import import_profiles

SOURCE = ROOT / "sources/builds/heartseeker-shuriken-profiles-2026-10-18.json"


def profile_bundle():
    snapshot = json.loads(SOURCE.read_text(encoding="utf-8"))
    result = {"format": "letools-profile-bundle", "version": 1, "name": "追心手里剑 · 四角色并集", "profiles": []}
    for row in snapshot["profiles"]:
        data = {"equipment": {}, "idols": []}
        assert len(row["items"]) == 19, row["character"]
        for item in row["items"]:
            converted = {"id": item["item_key"], "affixes": []}
            for affix in item["affixes"]:
                value = {"id": affix["link"].split("/")[-1]}
                field = {"sealedAffixes": "sealedAffix", "primordialAffixes": "primordialAffix",
                         "corruptedAffixes": "corruptedAffix"}.get(affix["tab"])
                if field:
                    converted[field] = value
                else:
                    converted["affixes"].append(value)
            if item["slot"].startswith("idol-"):
                data["idols"].append(converted)
            else:
                data["equipment"][item["slot"]] = converted
        result["profiles"].append({"url": row["url"], "data_version": snapshot["game_version"], "data": data})
    return result


def extracted_document():
    result = import_profiles(profile_bundle())["document"]
    result["source"].update(file=SOURCE.relative_to(ROOT).as_posix(),
                            sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                            extracted_on="2026-10-18", method="冻结可见UI摘录解码；不是原生API响应")
    return deepcopy(result)


if __name__ == "__main__":
    document = extracted_document()
    path = ROOT / "analysis/shuriken-profile-targets.json"
    path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print({k: len(v) for k, v in document["targets"].items()})
