"""Freeze exact set membership from the catalog's verified version150 source."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build():
    catalog = json.loads((ROOT / "sources/tool-catalog.json").read_text(encoding="utf-8"))
    source = catalog["source_urls"]["db"]
    raw = (ROOT / ".cache/db.js").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == source["sha256"]
    db = json.loads((ROOT / ".cache/db.json").read_text(encoding="utf-8"))["itemDB"]
    sets = {}
    for row in db["setBonusList"]:
        if row["setID"]:
            sets[str(row["setID"])] = {"id": row["setID"], "name_key": row["nameKey"], "members": []}
    for uid, row in db["uniqueList"]["uniques"].items():
        if row["isSetItem"]:
            assert catalog["uniques"][uid]["set"]
            sets[str(row["setId"])]["members"].append(int(uid))
    for group in sets.values():
        group["members"].sort()
        assert group["members"]
    members = [uid for group in sets.values() for uid in group["members"]]
    assert len(members) == len(set(members))
    assert set(members) == {int(uid) for uid, row in catalog["uniques"].items() if row["set"]}
    return {"version": catalog["version"], "source": source, "sets": sets}


if __name__ == "__main__":
    result = build()
    (ROOT / "sources/item-sets.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                                                 encoding="utf-8", newline="\n")
    print(f"Frozen {len(result['sets'])} sets / {sum(len(g['members']) for g in result['sets'].values())} items")
