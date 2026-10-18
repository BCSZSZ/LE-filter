"""Extract the selected public profiles from frozen native API bytes, offline."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tool"))
from letools import import_profiles

SOURCE = ROOT / "sources/builds/shuriken-profile-bundle-2026-10-19.json"


def profile_bundle():
    snapshot = json.loads(SOURCE.read_text(encoding="utf-8"))
    return deepcopy(snapshot["bundle"])


def extracted_document():
    result = import_profiles(profile_bundle())["document"]
    result["source"].update(file=SOURCE.relative_to(ROOT).as_posix(),
                            sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                            extracted_on="2026-10-19", method="冻结公开角色API序列化字节；普通装备槽仅取实际T6／T7，腐化槽普通词缀排除")
    return deepcopy(result)


if __name__ == "__main__":
    document = extracted_document()
    path = ROOT / "analysis/shuriken-profile-targets.json"
    path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print({k: len(v) for k, v in document["targets"].items()})
