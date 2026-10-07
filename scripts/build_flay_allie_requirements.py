"""Build both target documents from the guide's verified linked recommendations."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tool"))
from engine import CATALOG
from requirements import read_document


def build_documents():
    path = ROOT / "sources/builds/letools-allie-flay-extracted.json"
    facts = json.loads(path.read_text(encoding="utf-8"))
    targets = {key: [] for key in ("uniques", "equipment", "altars", "idols", "bases")}
    equipment, bases = {}, {}

    def group(typ, affixes, base_ids=()):
        result = {"type": typ, "bases": list(base_ids), "affixes": []}
        for affix in affixes:
            aid = affix["id"]
            data = CATALOG["affixes"][str(aid)]
            if typ not in data["types"]:
                raise ValueError(f"Guide affix does not belong to {typ}: {aid}")
            field = {4: "enchanted", 6: "corrupted"}.get(data["special"], "affixes")
            pool = result.setdefault(field, [])
            if aid not in pool:
                pool.append(aid)
        return result

    for row in facts["equipment"]:
        for item in row["items"]:
            if item["category"] == "unique":
                targets["uniques"].append(item["id"])
            else:
                pool = bases.setdefault(item["type"], [])
                if item["id"] not in pool:
                    pool.append(item["id"])
        for typ in dict.fromkeys(item["type"] for item in row["items"]):
            equipment[typ] = group(typ, row["affixes"])
    for row in facts["equipment_supplements"]:
        supplement = group(row["type"], row["affixes"])
        for aid in supplement["affixes"]:
            if aid not in equipment[row["type"]]["affixes"]:
                equipment[row["type"]]["affixes"].append(aid)
    targets["equipment"] = list(equipment.values())
    targets["bases"] = [{"type": typ, "bases": ids} for typ, ids in bases.items()]
    targets["uniques"] = sorted(set(targets["uniques"] + [i["id"] for i in facts["unique_supplements"]]))
    for row in facts["idols"]:
        item = row["items"][0]
        targets["idols"].append(group(item["type"], row["affixes"], [item["id"]]))
    source = {"name": facts["title"], "url": facts["url"], "updated": facts["source_updated"],
              "extracted_on": facts["extracted_on"], "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
              "scope": "Flay装备／神像推荐表与正文明确补充，包含替代品和后期升级；不绑定单一Planner变体",
              "warnings": ["候选池包含替代品，不要求同一件装备或整套装备同时采用所有候选。",
                           "泛指所缺抗性、生命或任意神像而未给出明确目标的条目留待手动补充，没有扩成全量词缀。",
                           "靴子表链接为暴击避免97，正文明确推荐护甲与暴击减伤715；两者均记录为候选。",
                           "更新日志说山之麓已被Transient Rest替代，正文仍推荐山之麓；本次按正文保留253，未从旧日志猜替代品ID。",
                           "武器合成段的虚弱链接429仅适用于护身符／遗物／手套，未加入武器目标，也未猜其他ID。",
                           "正文把智力502推荐给普通腰带，但词库不支持该部位；没有加入腰带目标，原链接另留核对记录。"]}
    common = {"format": "le-filter-requirements", "version": 1,
              "id": "flay-lich-allie-guide", "name": "Flay魔力巫妖 · Allie攻略"}
    endgame = {**common, "stage": "endgame", "targets": targets, "source": source}
    leveling = {**common, "stage": "leveling",
                "targets": {"affixes": [a["id"] for a in facts["leveling"]["targets"]],
                            "bases": [{"type": b["type"], "bases": [b["id"]]} for b in facts["leveling"]["bases"]]},
                "source": {**source, "scope": "Rip Blood／冥府裂缝术士练级正文：平铺词缀与底材",
                           "warnings": ["练级不同阶段的明确词缀取并集；本格式不表达按技能切换词缀池，收紧与80级退出由基底处理。",
                                        "冥府裂缝灵体频率链接748在词库中只适用于胸甲；未猜另一条头盔词缀。"]}}
    for document in (endgame, leveling):
        read_document(document)
    return endgame, leveling


if __name__ == "__main__":
    for document in build_documents():
        output = ROOT / f"requirements/{document['id']}.{document['stage']}.json"
        output.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(output.relative_to(ROOT), {key: len(value) for key, value in document["targets"].items()})
