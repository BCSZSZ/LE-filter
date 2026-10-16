"""Freeze the reviewed asset extraction, without copying game binaries."""

from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]


def main():
    path = ROOT / ".cache/t7-all-equipment/profiles.json"
    source = json.loads(path.read_text(encoding="utf-8-sig"))
    result = {k: source[k] for k in (
        "version", "scope", "gameVersion", "steamBuildID", "GameAssemblySHA256",
        "assetBundleSHA256", "sourceObjects", "classRequirementEnum",
        "affixClassSpecificityEnum", "poolSelectionRules", "classSelector", "equipmentTypes")}
    result["extractionSHA256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    result["profiles"] = []
    for profile in source["profiles"]:
        frozen = {k: profile[k] for k in (
            "id", "name", "typeID", "typeKey", "nameEn", "classRequirement",
            "classRequirementName", "classRequirementNameZh", "maximumAffixes",
            "affixEffectModifier", "subTypeAffixEffectiveness", "prophecyReward")}
        frozen["subtypeIDs"] = [s["id"] for s in profile["droppableSubtypes"]]
        frozen["affixes"] = [{k: a[k] for k in (
            "id", "type", "weight", "t6Compatibility",
            "maximumAffixEffectModifierForT6", "naturalT6Eligible")}
                            for a in profile["affixes"]]
        result["profiles"].append(frozen)
    output = ROOT / "sources/t7-equipment-pools.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8", newline="\n")
    print(f"Frozen {len(result['equipmentTypes'])} types / {len(result['profiles'])} pools")


if __name__ == "__main__":
    main()
