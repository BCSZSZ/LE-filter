"""Decode the frozen AL0dkyek selected-field UI snapshot without a network."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "sources/builds/letools-planner-al0dkyek-ui.json"
OUTPUT = ROOT / "sources/builds/letools-planner-al0dkyek-extracted.json"
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-$"


def decode_key(key: str) -> str:
    """LETools drops a category character before LZ-String URI decompression."""
    encoded = key[1:].replace(" ", "+")
    values = [ALPHABET.index(c) for c in encoded]
    index, mask = 0, 32

    def bits(count: int) -> int:
        nonlocal index, mask
        result = 0
        for offset in range(count):
            if index >= len(values):
                raise ValueError(f"Truncated compressed key: {key}")
            result |= bool(values[index] & mask) << offset
            mask >>= 1
            if not mask:
                index += 1
                mask = 32
        return result

    code = bits(2)
    if code == 2:
        return ""
    previous = chr(bits(8 if code == 0 else 16))
    dictionary = {0: "", 1: "", 2: "", 3: previous}
    output = [previous]
    width, enlarge, size = 3, 4, 4
    while True:
        code = bits(width)
        if code in (0, 1):
            dictionary[size] = chr(bits(8 if code == 0 else 16))
            code = size
            size += 1
            enlarge -= 1
        elif code == 2:
            return "".join(output)
        if enlarge == 0:
            enlarge = 1 << width
            width += 1
        if code in dictionary:
            current = dictionary[code]
        elif code == size:
            current = previous + previous[0]
        else:
            raise ValueError(f"Invalid compressed dictionary index: {key}")
        output.append(current)
        dictionary[size] = previous + current[0]
        size += 1
        enlarge -= 1
        previous = current
        if enlarge == 0:
            enlarge = 1 << width
            width += 1


def build_snapshot() -> dict:
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    catalog = json.loads((ROOT / "sources/tool-catalog.json").read_text(encoding="utf-8"))
    reference = json.loads((ROOT / "sources/game-reference.json").read_text(encoding="utf-8"))
    equipment_enum = reference["equipment_enum"]
    reverse_types = {value: name for name, value in equipment_enum.items()}
    for aid, data in raw.get("reference", {}).get("affixes", {}).items():
        frozen = catalog["affixes"][aid]
        assert frozen["special"] == data["specialAffixType"], aid
        assert frozen["prefix"] == (data["type"] == 0), aid

    def item(row: dict) -> dict:
        key = row["item_key"]
        decoded = decode_key(key)
        result = {"name": row["name"], "source_key": key, "decoded_key": decoded,
                  "url": f"https://www.lastepochtools.com/db/zh/items/{key}"}
        if key.startswith("U"):
            if len(decoded) != 6:
                raise ValueError(f"Unexpected unique key format: {key}/{decoded}")
            uid = int(decoded[3:])
            typ = catalog["uniques"][str(uid)]["type"]
            result.update(itemType=equipment_enum[typ], subType=int(decoded[:3]), uniqueID=uid)
            current = raw.get("reference", {}).get("uniques", {}).get(str(uid))
            if current:
                assert result["itemType"] == current["baseTypeId"], uid
                assert result["subType"] in current["subTypeIds"], uid
        elif key.startswith("I"):
            if len(decoded) != 10 or decoded[0] != "1":
                raise ValueError(f"Unexpected base key format: {key}/{decoded}")
            type_id, subtype = int(decoded[1:4]), int(decoded[4:7])
            typ = reverse_types[type_id]
            assert f"{typ}:{subtype}" in catalog["bases"], (key, typ, subtype)
            result.update(itemType=type_id, subType=subtype)
        else:
            raise ValueError(f"Unknown item category: {key}")
        result["type"] = typ
        if row.get("base_key"):
            base = decode_key(row["base_key"])
            assert int(base[1:4]) == result["itemType"]
            assert int(base[4:7]) == result["subType"]
            result["base_source_key"] = row["base_key"]
        result.update({name: [] for name in
                       ("affixes", "corruptedAffixes", "enchantedAffixes", "fixedAffixes")})
        rows = [{"id": int(decode_key(affix_key)), "tier": tier,
                 "source_tab": tab, "source_key": affix_key}
                for tab, affix_key, tier in row["affixes"]]
        rows += [{**affix, "source_tab": affix["source_tab"]}
                 for affix in row.get("resolved_card_affixes", [])]
        for affix in rows:
            aid = affix["id"]
            data = catalog["affixes"][str(aid)]  # Unknown IDs must fail.
            special = data["special"]
            affix.update(name=data["zh"], special=special)
            if affix.get("source_key"):
                section = "prefixes" if data["prefix"] else "suffixes"
                affix["url"] = f"https://www.lastepochtools.com/db/zh/{section}/{affix['source_key']}"
            destination = {0: "affixes", 2: "affixes", 5: "affixes", 4: "enchantedAffixes",
                           6: "corruptedAffixes", 7: "fixedAffixes"}.get(special)
            if destination is None:
                raise ValueError(f"Unreviewed special affix category: {aid}/{special}")
            result[destination].append(affix)
        return result

    items = {slot: item(row) for slot, row in raw["items"].items()}
    idols = [{"position": [int(p) for p in position.split("-")], **item(row)}
             for position, row in raw["idols"].items()]
    return {"url": raw["url"], "extracted_on": raw["extracted_on"],
            "title": raw["title"], "game_version": raw["game_version"],
            "data_version": raw["data_version"],
            "source_snapshot": RAW.relative_to(ROOT).as_posix(),
            "source_snapshot_sha256": hashlib.sha256(RAW.read_bytes()).hexdigest(),
            "method": raw["method"], "notes": raw["notes"],
            "decoder": "Remove key category character; LZ-String decompressFromEncodedURIComponent. A: decimal affix ID. U: 3-digit subType + 3-digit UniqueID. I: 1 + 3-digit itemType + 3-digit subType + 3-digit variant.",
            "reference": raw.get("reference", {}),
            "planner": {"level": 100, "class_name": "神射手", "items": items, "idols": idols,
                        "leveling_targets": None},
            "game_client_tested": False}


if __name__ == "__main__":
    snapshot = build_snapshot()
    OUTPUT.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8", newline="\n")
    print(OUTPUT.relative_to(ROOT))
    print({"items": len(snapshot["planner"]["items"]), "idols": len(snapshot["planner"]["idols"])})
