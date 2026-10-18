"""Research the old protection pool; never edit the active filter membership."""
import hashlib
import json
from pathlib import Path

from compare_common_unique_protection import compare

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "sources/common-unique-drop-sources-2026-10-18.json"
ZERO_EVIDENCE = ROOT / "sources/zero-reroll-drop-sources-2026-10-18.json"
LABELS = {
    1: "茧化物品",
    2: "世界随机掉落且reroll=0",
    3: "Boss／裂隙野兽定向来源，非世界随机",
    4: "世界随机掉落且reroll>0",
    5: "其他限定奖励",
}


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def count(items):
    return {"total": len(items), "uniques": sum(not i["set"] for i in items),
            "sets": sum(i["set"] for i in items)}


def build():
    comparison = compare()
    evidence = read(EVIDENCE)
    sources = {i["id"]: i for i in evidence["items"]}
    old_equipment = comparison["groups"]["overlap"] + comparison["groups"]["old_only"]
    old = sorted((i for i in old_equipment if not i["set"]), key=lambda i: i["id"])
    additions = [i for i in comparison["groups"]["new_only"] if not i["set"]]
    approved = read(ROOT / "sources/common-unique-protection.json")
    groups = {n: [] for n in LABELS}
    for item in old:
        source = sources[item["id"]]
        has_boss_source = (source["is_primordial"] or item["id"] == 444
                           or bool(source.get("tunklab_boss_links"))
                           or any(row.get("monsterNameKey") and not row.get("soulGambler")
                                  for row in source["letools_monster_item_drops"]))
        if item["is_cocooned"]:
            category = 1
        elif item["can_drop_randomly"]:
            category = 4 if item["reroll_chance"] > 0 else 2
        else:
            category = 3 if has_boss_source else 5
        groups[category].append({**item, "category": category, "drop_source": source})

    # The five groups must partition the unchanged old pool. Positive candidates
    # come from the published random-pool metadata, not a hand-maintained ID list.
    assert len(old) == len({i["id"] for i in old}) == 138
    assert {n: len(v) for n, v in groups.items()} == {1: 23, 2: 7, 3: 60, 4: 47, 5: 1}
    assert {i["id"] for i in groups[2]} == {i["id"] for i in read(ZERO_EVIDENCE)["items"] if not i["set"]}
    assert all(not i["can_drop_randomly"] and i["reroll_chance"] == 0 for i in groups[3] + groups[5])
    assert sum(i["drop_source"]["is_primordial"] for i in groups[3]) == 25
    assert [i["id"] for i in groups[5]] == [416]
    assert len(groups[4]) + len(additions) == 97
    retained = [i for n, items in groups.items() if n != 2 for i in items]
    candidate = sorted(retained + additions, key=lambda i: i["id"])
    assert len(candidate) == len({i["id"] for i in candidate}) == 181
    assert {i["id"] for i in candidate} == set(approved["unique_ids"])
    assert {i["id"] for i in groups[4] + additions} <= {i["id"] for i in candidate}
    return {"date": "2026-10-18", "status": "unique_only_classification_with_applied_policy", "replacementApplied": True,
            "scope": "Non-set equipment uniques only, before T0/BD deduplication. All sets are independent and retained.",
            "evidence": [{"file": p.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                         for p in (EVIDENCE, ZERO_EVIDENCE)],
            "category3Convention": "Includes Rift Beast restricted drops and Evolution's End lineage reward; does not assert one exclusive boss or exclude vendor/echo alternatives.",
            "counts": {"old": count(old), "categories": {str(n): count(v) for n, v in groups.items()},
                       "positiveRerollAllEquipment": count(groups[4] + additions),
                       "positiveRerollMissing": count(additions), "retainedOld": count(retained),
                       "candidateRemove2AndComplete4": count(candidate),
                       "oldSetsSeparate": count([i for i in old_equipment if i["set"]]),
                       "allSetsRetained": len(approved["set_ids"])},
            "groups": {str(n): items for n, items in groups.items()},
            "positiveRerollAdditions": [{**i, "drop_source": sources[i["id"]]} for i in additions],
            "candidateIds": [i["id"] for i in candidate],
            "separatePositiveRerollIdols": comparison["separatePositiveRerollIdols"],
            "checks": {"oldUniquePoolPartitionedExactlyOnce": True, "all97PositiveUniquesCovered": True,
                       "onlyCategory2RemovedFromOldUniques": True, "setsExcludedFromNumberedGroups": True,
                       "candidateMatchesActiveUniquePool": True}}


def source_label(item):
    source = item["drop_source"]
    if item["is_cocooned"]:
        return "茧化容器；不以其可能开出的成品分类"
    if item["can_drop_randomly"]:
        return f"世界随机；reroll {item['reroll_chance'] * 100:g}%"
    if source["is_primordial"]:
        return "Rift Beast（官方1.3.2已补全）；部分另可兑换"
    if item["id"] == 444:
        return "Rift Beast：结束谱系奖励（官方补丁说明）"
    if item["id"] == 416:
        return "完成The Grand Brewery的保证奖励"
    names = [row["name"] for row in source.get("tunklab_boss_links", [])]
    if not names:
        names = [row["monsterNameKey"].removeprefix("Actors.Actor_Name_")
                 for row in source["letools_monster_item_drops"] if row.get("monsterNameKey")]
    text = "、".join(dict.fromkeys(names))
    if source.get("tunklab_echo_links"):
        text += "；另有编织回响完成奖励"
    return text


def render(report):
    lines = ["# 旧通用暗金名单：五类掉落来源核查", "",
             "2026-10-18按玩家订正：①②③④仅以非套装暗金为对象，套装全部单独保留。新口径已落实到[当前生成器名单](COMMON_UNIQUE_PROTECTION.md)。", "",
             "这里分类旧138种暗金，包含前置T0／BD会覆盖的ID；旧21件套装移出编号分类，当前套装规则覆盖全部61件／24套。独立的10种暗金神像与先驱者之针344不在本表内。旧暗金来自Raxx选择与三个赛季追加，并非统一的稀有度筛选。", "",
             "## 分类结果", "",
             "| 类别 | 暗金数量 | 当前处理 |", "|---|---:|---|"]
    for n, label in LABELS.items():
        c = report["counts"]["categories"][str(n)]
        lines.append(f"| {n}．{label} | {c['total']} | {'移出通用池' if n == 2 else '保留'} |")
    lines += ["", "五类互斥合计138种暗金。第③类将裂隙野兽及其谱系奖励作为限定Boss体系统计；它不表示只能由一个有名字的Boss掉落，也不排除兑换、编织回响等奖励途径。进化终焉444在这里随裂隙体系列入③，若按‘结束流程奖励’列入⑤，只会改变分类数量，不改变保留结论。", "",
              "**第③、⑤类的页面reroll通常显示‘－’，不能写成页面显示0%。** 已读取底层数据的reroll字段为0，但因为不进世界随机池，这个字段不用于衡量其定向稀有度。‘只删世界随机且0’必须同时判断`canDropRandomly`，不能直接删所有原始`rerollChance=0`的ID。[Tunklab主表](https://lastepoch.tunklab.com/uniques)", "",
              "## 世界随机reroll为0：只计7暗金，蜂农套装另行保留", "",
              "此前10件包括7暗金、3蜂农套装。套装77／78／79已从②移出，仍由全部套装规则保护。7暗金详情均明确世界随机、无reroll，不是Boss专属；指定类型奖励节点不等于该时间线Boss专属。原始10件交叉核查作为历史证据保留在[专项来源报告](research/ZERO_REROLL_DROP_SOURCES.md)。", "",
              "## 先古与特殊来源的修正", "",
              "旧名单包含全部25种先古暗金。官方1.3初版说明是22种可兑换、3种仅裂隙野兽掉落；**官方1.3.2又明确让此前仅可购买的先古暗金也能由裂隙野兽掉落**。因此，Tunklab部分详情页只写‘Not random drop’，不能据此归为仅商店兑换。本报告将25种全部归入③，保留兑换作为额外来源。[官方1.3初版](https://forum.lastepoch.com/t/last-epoch-beneath-ancient-skies-patch-notes/78635/2)、[官方1.3.2修正](https://forum.lastepoch.com/t/last-epoch-patch-1-3-2-notes/79385)", "",
              "③的60种可再分为34种其他限定Boss来源、25种先古暗金、1种进化终焉444。进化终焉的谱系结束奖励由官方说明支持；Tunklab该页仅写非随机。⑤只剩酿酒大师的皮带扣416，来源是完成The Grand Brewery保证奖励，页面将其记为回响完成掉落，故单列；该回响本身要求击败酿酒师。[官方谱系说明](https://forum.lastepoch.com/t/last-epoch-beneath-ancient-skies-patch-notes/78635/2)、[腰带详情](https://lastepoch.tunklab.com/unique/brewmasters_buckle)、[回响完成奖励](https://lastepoch.tunklab.com/echo/the_grand_brewery)", "",
              "例如乌凯罗斯的扭曲之心216同时有Emperor of Corpses及编织回响完成奖励，所以本文使用‘Boss定向来源’，不把‘有Boss来源’写成‘无任何其他获取途径’。[216实际来源](https://lastepoch.tunklab.com/unique/twisted_heart_of_uhkeiros)", "",
              "## 已落实的‘只移出②、补齐④’，套装独立", "",
              "- 旧138暗金移出②的7种后，保留131种。茧化及所有旧非世界随机来源均保留。",
              "- ④在全部可见非套装暗金装备中共有97种。旧名单只覆盖47种，还差50种。",
              "- 补齐50种后，暗金池181种；套装独立保留全部61件，不按reroll筛选。基础池合计242个物品ID，不是XML规则数量，默认Strict仍96条。",
              "- 3个正reroll暗金神像：奇点246、自然之怒462、焦土485，仍归独立暗金神像类别；六件T0仍由独立最高提示保护。",
              "- 从通用名单移出不等于最终隐藏。BD明确目标、套装补全、更高LP及WW规则可能继续保留相同物品；例如296属于WW暗金。", ""]
    tables = [(str(n), f"{n}．{LABELS[n]}：{len(report['groups'][str(n)])}种", report["groups"][str(n)]) for n in LABELS]
    tables.append(("additions", "④本轮补入的50种暗金", report["positiveRerollAdditions"]))
    for key, title, items in tables:
        lines += [f"## {title}", "", "| ID | 名称／详情 | 类别 | reroll／状态 | 来源核查 |", "|---:|---|---|---|---|"]
        for item in items:
            name = f"[{item['zh']} · {item['en']}]({item['drop_source']['url']})"
            lines.append(f"| {item['id']} | {name} | {'套装' if item['set'] else '暗金'} | {item['tunklab_display']} | {source_label(item)} |")
        lines.append("")
    lines += ["## 证据、复现与边界", "",
              "- [完整结构化分类](../analysis/common-unique-classification.json)：138个旧暗金ID各出现一次，五类数量、50个新增与181个现行暗金ID完整保留，套装独立计数。",
              "- [本次来源快照](../sources/common-unique-drop-sources-2026-10-18.json)：214个比较ID的详情URL、先古标记、旧LETools定向来源记录，以及本次读取的84个非随机／茧化详情页来源片段和原HTML哈希。",
              "- [原reroll快照](../sources/tunklab-unique-reroll-2026-10-18.json)与[10件专项证据](../sources/zero-reroll-drop-sources-2026-10-18.json)：不以详情页缺少来源为唯一判据；先古与谱系补充以官方补丁说明为准。LETools为已取得的version152缓存，本轮重取403，不冒称实时取得。",
              "- 离线重建：`python -X utf8 scripts/classify_common_unique_protection.py`。脚本只写本分类报告与对应analysis JSON；生成器另读已确认的冻结名单。",
              "- 这是XML名单事实、数据库来源与官方说明的研究，没有作游戏客户端掉落实测；reroll百分比不是物品的全局掉落概率。", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    report = build()
    (ROOT / "analysis/common-unique-classification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    (ROOT / "docs/COMMON_UNIQUE_CLASSIFICATION.md").write_text(render(report), encoding="utf-8", newline="\n")
    print(json.dumps(report["counts"], ensure_ascii=False))
