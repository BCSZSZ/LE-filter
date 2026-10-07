"""Build target-only requirements from the guide's frozen linked table data."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tool"))
from engine import CATALOG
from requirements import read_document


def build_document():
    path = ROOT / "sources/builds/letools-guide-zh-835-extracted.json"
    facts = json.loads(path.read_text(encoding="utf-8"))
    targets = {key: [] for key in ("uniques", "equipment", "altars", "idols", "bases")}
    for row in facts["equipment"]:
        for item in row["items"]:
            if item["category"] == "unique":
                targets["uniques"].append(item["id"])
            elif item["type"] != "IDOL_ALTAR":
                targets["bases"].append({"type": item["type"], "bases": [item["id"]]})
        # Main/offhand tables cover several weapon families. Intersect their
        # ordinary pools with each listed family's actual affix range.
        for typ in dict.fromkeys(item["type"] for item in row["items"]):
            ordinary, corrupted, enchanted = [], [], []
            for item in row["affixes"]:
                aid, data = item["id"], CATALOG["affixes"][str(item["id"])]
                if data["special"] == 6:
                    corrupted.append(aid)
                elif data["special"] == 4:
                    enchanted.append(aid)
                elif typ in data["types"]:
                    ordinary.append(aid)
                elif row["slot"] not in {"weapon1", "weapon2"}:
                    raise ValueError(f"Unexpected guide affix scope: {typ}/{aid}")
            if not ordinary:
                continue
            group = {"type": typ, "bases": [], "affixes": ordinary}
            if corrupted:
                group["corrupted"] = corrupted
            if enchanted:
                group["enchanted"] = enchanted
            if typ == "IDOL_ALTAR":
                group["bases"] = [item["id"] for item in row["items"]]
            targets["altars" if typ == "IDOL_ALTAR" else "equipment"].append(group)
    for row in facts["idols"]:
        item = row["items"][0]
        # Omen idols can use affixes otherwise reserved for larger class idols.
        targets["idols"].append({"type": item["type"], "bases": [item["id"]],
                                  "affixes": [a["id"] for a in row["affixes"]]})
    targets["uniques"] = sorted(set(targets["uniques"]))
    document = {"format": "le-filter-requirements", "version": 1,
                "id": "bleed-skeleton-roamer-guide-835", "name": "流血骷髅游荡者 · 攻略835",
                "stage": "endgame", "targets": targets,
                "source": {"name": facts["title"], "url": facts["url"],
                           "updated": facts["source_updated"], "scope": "公共装备与神像推荐表，包含替代候选；不绑定单一变体",
                           "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                           "warnings": ["本文件收集公共推荐表中的替代品，并不表示这些装备需要同时穿戴。",
                                        "表中生命链接实际为提高生命52；按链接ID保存，未改成增加生命51。",
                                        "护身符1085、1086只存腐化参考，不计普通目标。",
                                        "大型幽冥预兆神像保留266、287；预兆允许更大神像的词缀。",
                                        "练级的8词缀与5底材另存同id的leveling需求；七个变体仍独立记录。"]}}
    read_document(document)
    return document


def build_leveling_document():
    facts = json.loads((ROOT / "sources/builds/letools-guide-zh-835-extracted.json").read_text(encoding="utf-8"))
    document = build_document()
    document["stage"] = "leveling"
    document["targets"] = {"affixes": [a["id"] for a in facts["leveling"]["targets"]],
                           "bases": [{"type": b["type"], "bases": [b["id"]]} for b in facts["leveling"]["bases"]]}
    document["source"]["scope"] = "练级正文：所需词缀与底材"
    document["source"]["warnings"] = []
    read_document(document)
    return document


def render_review(document):
    targets = document["targets"]
    def names(category, ids, typ=None):
        return "、".join(f"{CATALOG[category][f'{typ}:{i}' if category == 'bases' else str(i)]['zh']}（{i}）" for i in ids) or "—"
    lines = ["# 流血骷髅游荡者：攻略835需求审阅", "",
             f"来源：[原攻略]({document['source']['url']})，页面更新于2026-10-06，本次提取于2026-10-07。", "",
             "范围是公共装备与神像推荐表，包含替代候选；未选择七个变体中的某一个。它与旧Maxroll骷髅Strict是独立BD，不修改旧来源。本次已重新核对在线推荐表及练级清单，目标ID与原快照一致；终局五类与练级两份列表分别生成。", "",
             "共25种暗金／套装、13组装备部位目标、3组神像、1组祭坛、3种独立制作底材。下表由实际JSON和冻结词库生成；来源顺序只方便审阅，不作为词缀筛选优先级。", "",
             "## 暗金／套装候选", "", "这里记录需要收集的候选，不表示必须同时穿戴，也不要求先有LP。蜂农梳、蜂农烟熏器和西纳提亚的亡者复苏是套装，仍使用共通uniques ID列表。", "",
             "| 部位／类型 | 目标 |", "|---|---|"]
    for typ in dict.fromkeys(CATALOG["uniques"][str(i)]["type"] for i in targets["uniques"]):
        ids = [i for i in targets["uniques"] if CATALOG["uniques"][str(i)]["type"] == typ]
        lines.append(f"| {CATALOG['types'][typ]['zh']} | {names('uniques', ids)} |")
    lines += ["", "## 装备词缀目标", "", "目标素材默认不限底材；独立制作底材列在下方。主手／副手推荐表涉及多种装备类型，按对应类型实际可出词缀取交集，未把单手锤、盾牌不具备的普通词缀加入池。普通池包括攻略明确列出的实验词缀；腐化单列参考。", "",
              "| 部位／类型 | 普通／实验目标池 | 腐化参考 |", "|---|---|---|"]
    for group in targets["equipment"]:
        lines.append(f"| {CATALOG['types'][group['type']]['zh']} | {names('affixes', group['affixes'])} | {names('affixes', group.get('corrupted', []))} |")
    lines += ["", "胸甲192来自本次攻略的明确链接；旧Strict只有406的事实不变。表中“生命”的链接指向提高生命52，按链接保存，未猜成增加生命51。护身符1085／1086为腐化参考，普通池只有945；它们不能凑普通双目标T7。", "",
              "## 神像与祭坛", "", "| 类别 | 类型／底材 | 普通目标池 |", "|---|---|---|"]
    for category in ["idols", "altars"]:
        for group in targets[category]:
            lines.append(f"| {'神像' if category == 'idols' else '祭坛'} | {CATALOG['types'][group['type']]['zh']}；{names('bases', group['bases'], group['type'])} | {names('affixes', group['affixes'])} |")
    lines += ["", "谦卑神像的870／868、中型神像的855／851是后缀候选；整个池保留，不要求一件具有池内全部词缀。攻略的×9／×3是佩戴配置数量，不变成掉落过滤条件。", "",
              "大型幽冥预兆神像保留266＋287。266在普通词库范围中属于巨型神像，但预兆能获得通常属于更大神像的词缀，不能直接用普通尺寸范围删掉它。[官方机制说明](https://forum.lastepoch.com/t/last-epoch-shattered-omens-patch-notes/80571/)确认预兆掉落时已腐化；物品已腐化与266／287自身是普通目标是两件事。", "",
              "## 独立制作底材", "", "| 类型 | 底材 |", "|---|---|"]
    for group in targets["bases"]:
        lines.append(f"| {CATALOG['types'][group['type']]['zh']} | {names('bases', group['bases'], group['type'])} |")
    lines += ["", "## 审阅边界与使用", "",
              "JSON只描述目标池及其类型／底材范围，腐化与附魔只记录参考。T7／T6、LP／WW、声音、主副颜色、等级和规则顺序由现有基底转换程序处理，不由攻略覆盖。神像沿用普通池一项／两项层，祭坛保持一项层；此文不宣称任意两项都是整套BD的最终毕业配置。", "",
              "在工作台点击“导入BD需求JSON”，选择requirements/bleed-skeleton-roamer-guide-835.endgame.json。练级正文另存同id的leveling.json，只含词缀与底材两份列表。编辑后点“保存本BD需求JSON”；重新导入同id只替换该阶段目标，保留另一个阶段及主副身份。可继续勾选与其他BD合并。", "",
              "重建：python -X utf8 scripts/build_guide_835_requirements.py。脚本读取已解码的来源快照和冻结词库，不依赖网页、网络或.cache；快照附原链接、解码结果及七个变体索引。网页读取和修改保存、JSON转换及有限匹配测试与游戏客户端实测分别验证；本次不生成最终XML文件。", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    output = ROOT / "requirements/bleed-skeleton-roamer-guide-835.endgame.json"
    output.parent.mkdir(exist_ok=True)
    document = build_document()
    output.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    (output.parent / "bleed-skeleton-roamer-guide-835.leveling.json").write_text(
        json.dumps(build_leveling_document(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    (ROOT / "docs/BLEED_SKELETON_GUIDE_REVIEW.md").write_text(render_review(document), encoding="utf-8", newline="\n")
    print(output.relative_to(ROOT))
    print({key: len(value) for key, value in document["targets"].items()})
