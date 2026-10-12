"""Freeze visible T0 equipment from the catalog's verified version150 source."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build():
    catalog = json.loads((ROOT / "sources/tool-catalog.json").read_text(encoding="utf-8"))
    source = catalog["source_urls"]["db"]
    assert hashlib.sha256((ROOT / ".cache/db.js").read_bytes()).hexdigest() == source["sha256"]
    db = json.loads((ROOT / ".cache/db.json").read_text(encoding="utf-8"))["itemDB"]
    uniques = []
    for uid, row in db["uniqueList"]["uniques"].items():
        if row["rarityTier"] != "T0" or row["hideFromPlayers"] or row["isSetItem"]:
            continue
        entry = catalog["uniques"][uid]
        assert not entry["hidden"] and not entry["set"] and not entry["type"].startswith("IDOL_")
        uniques.append({"id": int(uid), "en": entry["en"], "zh": entry["zh"], "type": entry["type"],
                        "rarity_tier": row["rarityTier"], "reroll_chance": row["rerollChance"]})
    uniques.sort(key=lambda u: u["id"])
    assert {u["id"] for u in uniques} == {61, 208, 277, 473, 476, 478}
    return {"version": catalog["version"], "source": source,
            "selection": "Visible non-set T0 equipment; six items confirmed by the player on 2026-10-12.",
            "uniques": uniques}


if __name__ == "__main__":
    result = build()
    (ROOT / "sources/ultra-rare-uniques.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Frozen {len(result['uniques'])} T0 uniques")
