"""Freeze audited RollBaseType inputs; development only, never run by Pages."""

from pathlib import Path
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
AUDITED_SHA256 = "94b06433deb98a716784a33d365b3141fee67533b9b522ce38aa4e0f87ecbacf"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path,
                        default=ROOT / ".cache/t7-natural-tool/type-selection.json")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "sources/t7-natural-type-selection.json")
    args = parser.parse_args()
    raw = args.input.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == AUDITED_SHA256, "Extraction changed; re-audit first"
    source = json.loads(raw)
    types = source["parameters"]["ordinaryEquipmentTypeIDs"]
    assert set(types) == set(range(24)) - {11}
    assert source["parameters"]["candidateCount"] == 42
    players = []
    for player in source["playerClasses"]:
        coefficients = player["ordinaryTypeCoefficients"]
        assert {row["typeID"] for row in coefficients} == set(types)
        assert player["classRequirementMask"] == 1 << player["classID"]
        players.append({
            "id": player["classID"], "name": player["nameZh"],
            "nameEn": player["name"],
            "classRequirementMask": player["classRequirementMask"],
            "raw2EquipmentFactorByType": {
                str(row["typeID"]): row["raw2RelativeCoefficientDoublePrecision"]
                for row in coefficients},
            "modes": {name: {key: mode[key] for key in (
                "excludeIdols", "acceptedWeightSum", "candidateCount",
                "all1000CandidatesRejectedProbability", "acceptWeightsByTypeID")}
                      for name, mode in player["modes"].items()},
        })
    result = {key: source[key] for key in (
        "version", "gameVersion", "steamBuildID", "sourceSHA256",
        "sourceObjectPathID", "GameAssemblySHA256", "methods", "parameters",
        "formulas", "subtypeClassConditioning")}
    result.update({
        "scope": "ilvl100 initial ordinary raw0..4 random branch, initial forceExalted=false; conditioned on ordinary equipment type and equipment base class",
        "auditedExtractionSHA256": AUDITED_SHA256,
        "players": players,
    })
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8", newline="\n")
    print(f"Frozen {len(players)} player classes x {len(types)} equipment types")


if __name__ == "__main__":
    main()
