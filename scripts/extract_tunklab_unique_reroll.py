"""Freeze Tunklab reroll evidence without changing the active protection list."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DATA = {"url": "https://lastepoch.tunklab.com/_next/static/chunks/2k6d3rtcxh7q6.js",
        "sha256": "05cb81a6a3b098ac872164740071ec4ee3deceab6251b30555536d052ee45391"}
PAGE = {"url": "https://lastepoch.tunklab.com/_next/static/chunks/1xxez1-nu7zct.js",
        "sha256": "8e041c386013b405503d32745e747c06de6863f2681b322f0d5f8a291f768223"}


def build():
    for source in (DATA, PAGE):
        path = ROOT / ".cache/tunklab" / source["url"].rsplit("/", 1)[-1]
        if hashlib.sha256(path.read_bytes()).hexdigest() != source["sha256"]:
            raise ValueError(f"Tunklab来源哈希不符：{path.name}")
    text = (ROOT / ".cache/tunklab/2k6d3rtcxh7q6.js").read_text(encoding="utf-8")
    catalog = json.loads((ROOT / "sources/tool-catalog.json").read_text(encoding="utf-8"))
    types = json.loads((ROOT / "sources/game-reference.json").read_text(encoding="utf-8"))["equipment_enum"]
    reverse = {value: key for key, value in types.items()}
    # Read literal metadata only; do not execute the site's JavaScript.
    pattern = re.compile(r'\{name:("(?:\\.|[^"\\])*"),displayName:("(?:\\.|[^"\\])*"),uniqueId:(\d+),isSetItem:(![01]),')
    matches = list(pattern.finditer(text))
    items = []
    for index, match in enumerate(matches):
        block = text[match.start():matches[index + 1].start() if index + 1 < len(matches) else len(text)]
        def field(key):
            return re.search(r'(?:[,{])' + key + r':([^,}\]]+)', block)[1]
        uid = int(match[3])
        entry = catalog["uniques"][str(uid)]
        is_set = match[4] == "!0"
        typ = reverse[int(field("baseType"))]
        assert (entry["type"] is None or typ == entry["type"]) and is_set == entry["set"], uid
        reroll = float(field("rerollChance"))
        assert 0 <= reroll <= 1, uid
        items.append({"id": uid, "en": entry["en"], "zh": entry["zh"], "type": typ, "set": is_set,
                      "catalog_hidden": entry["hidden"],
                      "is_cocooned": bool(re.search(r'(?:[,{])isCocoonedItem:!0', block)),
                      "source_name": json.loads(match[2]) or json.loads(match[1]),
                      "can_drop_randomly": field("canDropRandomly") == "!0", "reroll_chance": reroll})
    ids = [item["id"] for item in items]
    assert len(ids) == len(set(ids))
    assert {int(uid) for uid, item in catalog["uniques"].items() if not item["hidden"]} <= set(ids)
    positive = [item for item in items if not item["catalog_hidden"] and item["can_drop_randomly"] and item["reroll_chance"] > 0]
    equipment = [item for item in positive if not item["type"].startswith("IDOL_")]
    return {"version": 1, "retrieved_on": "2026-10-18", "url": "https://lastepoch.tunklab.com/uniques",
            "sources": {"data": DATA, "page": PAGE},
            "display_logic": "can_drop_randomly ? reroll_chance : '-'; Lens of Curiosity off. This is comparison evidence, not an applied replacement list.",
            "summary": {"dataItems": len(items), "positiveRandomReroll": len(positive),
                        "equipmentUniques": sum(not item["set"] for item in equipment),
                        "sets": sum(item["set"] for item in equipment), "uniqueIdols": len(positive) - len(equipment)},
            "items": sorted(items, key=lambda item: item["id"])}


if __name__ == "__main__":
    document = build()
    path = ROOT / "sources/tunklab-unique-reroll-2026-10-18.json"
    path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(document["summary"])
