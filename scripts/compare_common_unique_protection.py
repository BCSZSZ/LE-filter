"""Compare the existing fixed pool with the proposed Tunklab criterion."""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tool"))
import engine as e

SOURCE = ROOT / "sources/tunklab-unique-reroll-2026-10-18.json"


def compare():
    evidence = json.loads(SOURCE.read_text(encoding="utf-8"))
    metadata = {u["id"]: u for u in evidence["items"]}
    provenance = defaultdict(list)
    for number in (15, 16):
        for uid in e.inspect_rule(e.BASE[number])["unique_ids"]:
            provenance[uid].append(f"Raxx R{number}")
    for release in e.read_json("sources/seasonal-unique-protection.json")["releases"]:
        for item in release["uniques"]:
            provenance[item["id"]].append("赛季" + release["version"])
    old = set(provenance) - e.UNIQUE_IDOLS
    proposed = {uid for uid, item in metadata.items() if not item["catalog_hidden"] and not item["is_cocooned"]
                and item["can_drop_randomly"] and item["reroll_chance"] > 0 and uid not in e.UNIQUE_IDOLS}
    def record(uid):
        item = metadata[uid]
        status = "主表隐藏（茧化）" if item["is_cocooned"] else "非随机，显示－" if not item["can_drop_randomly"] else f"{item['reroll_chance'] * 100:g}%"
        return {**item, "tunklab_display": status, "old_sources": provenance.get(uid, [])}
    groups = {key: [record(uid) for uid in sorted(pool)]
              for key, pool in (("overlap", old & proposed), ("old_only", old - proposed), ("new_only", proposed - old))}
    def count(pool):
        return {"uniques": sum(not e.CATALOG["uniques"][str(uid)]["set"] for uid in pool),
                "sets": sum(e.CATALOG["uniques"][str(uid)]["set"] for uid in pool), "total": len(pool)}
    config = e.bootstrap()["config"]
    claimed = {uid for build in config["builds"] if build["enabled"]
               for uid in e.expand_unique_sets(build["profiles"]["endgame"]["uniques"])}
    pruned = claimed | e.ULTRA_RARE_UNIQUES
    return {"date": "2026-10-18", "status": "comparison_only", "replacementApplied": False,
            "source": {"file": SOURCE.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                       "url": evidence["url"]},
            "scope": "Equipment and sets before T0/BD deduplication; unique idols retain their independent category.",
            "counts": {"old": count(old), "proposed": count(proposed), "overlap": count(old & proposed),
                       "old_only": count(old - proposed), "new_only": count(proposed - old)},
            "oldOnlyReasons": dict(Counter("cocooned_hidden" if metadata[uid]["is_cocooned"] else
                                           "not_random_dash" if not metadata[uid]["can_drop_randomly"] else "random_reroll_zero"
                                           for uid in old - proposed)),
            "defaultStrictAfterDeduplication": {"old": count(old - pruned), "proposed": count(proposed - pruned),
                                               "overlap": count((old & proposed) - pruned),
                                               "old_only": count((old - proposed) - pruned),
                                               "new_only": count((proposed - old) - pruned)},
            "separatePositiveRerollIdols": [record(uid) for uid in sorted(e.UNIQUE_IDOLS)
                                           if metadata[uid]["can_drop_randomly"] and metadata[uid]["reroll_chance"] > 0],
            "groups": groups}


def render(report):
    lines = ["# 通用0LP保护：旧名单与Tunklab口径对照", "",
             "2026-10-18。旧名单完整保留，新的reroll口径尚未应用。", "",
             "旧名单是冻结Raxx R15珍贵暗金、R16部分套装与1.3／1.4／1.5新增名单的并集；暗金神像已拆成独立类别，不在此表内。旧表不是统一reroll阈值筛选。新口径是Tunklab可随机掉落、默认镜片关闭时reroll严格大于0。非随机物品的‘－’不当作非零数值，茧化物品在主表隐藏。", "",
             "下表比较完整基础池，尚未扣除前置T0及当前BD目标；因此与当前默认Strict组合实际显示的143种有所区别。", "",
             "| 范围 | 暗金 | 套装 | 合计 |", "|---|---:|---:|---:|"]
    for key, label in (("old", "旧名单"), ("proposed", "新口径 reroll > 0"), ("overlap", "两者重合"),
                       ("old_only", "仅旧名单有"), ("new_only", "仅新口径有")):
        item = report["counts"][key]
        lines.append(f"| {label} | {item['uniques']} | {item['sets']} | {item['total']} |")
    lines += ["", "旧名单独有94种：61种非随机掉落、主表显示‘－’；23种茧化物品、主表隐藏；10种可随机掉落但reroll为0。非随机掉落不等于常见，也不能只用随机掉落reroll比较其稀有度。", "",
              "套装差分很明确：旧名单独有的是蜂农烟熏器77、蜂农防护服78、蜂农梳79，reroll均为0；新口径独有的是耀阳胸铠86（20%）、耀阳重盔87（50%）、哈瓦尔的誓约97（20%）、泽里克的贪婪139（50%）、费洛波尔的毅力228（40%）。", "",
              "例如大失血11、短暂休息132、烟雾编织者136、灰烬之歌37在新口径中新增；破碎世界413、虚无353、真视玻璃439等在旧名单中保留，却不能由随机掉落reroll > 0覆盖。", "",
              "保留旧名单再补入全部55种新候选时，合计214种（188暗金、26套装）；这只是并集大小，本次没有据此改过滤器。", "",
              "## 实际默认组合与独立规则", ""]
    actual = report["defaultStrictAfterDeduplication"]
    lines += [f"扣除已由T0及旧Strict两BD前置规则保护的ID后，旧通用池为{actual['old']['total']}种；新口径候选池为{actual['proposed']['total']}种。这里的扣除只省略重复规则，不能误读成删除T0或BD需求。", "",
              "六件T0在两种基础池中均有，仍由独立最高提示规则收集。奇点246、自然之怒462、焦土485符合正reroll，但属于独立暗金神像类别；不将它们补回装备／套装池。BD明确需要的套装补全也独立于本次比较。", ""]
    for key, label in (("old_only", "仅旧名单有：94种"), ("new_only", "仅新口径有：55种"), ("overlap", "两者重合：65种")):
        lines += [f"## {label}", "", "| ID | 名称 | 类别 | Tunklab reroll／状态 | 旧名单来源 |",
                  "|---:|---|---|---|---|"]
        for item in report["groups"][key]:
            lines.append(f"| {item['id']} | {item['zh']} · {item['en']} | {'套装' if item['set'] else '暗金'} | {item['tunklab_display']} | {'、'.join(item['old_sources']) or '—'} |")
        lines.append("")
    lines += ["## 证据与边界", "",
              "- [Tunklab唯一与套装主表](https://lastepoch.tunklab.com/uniques)：同时读取该页实际发布的数据与显示逻辑；关闭Lens of Curiosity，以基础reroll比较。",
              "- [冻结reroll证据](../sources/tunklab-unique-reroll-2026-10-18.json)：487条发布元数据、来源脚本URL与SHA-256，完整覆盖本地可见词库；不在工具运行期联网。",
              "- [机器对照](../analysis/common-unique-comparison.json)：全部ID、归属、集合大小及去重后的对照。",
              "- [冻结基底](../templates/LE-base-v1.xml)与[旧赛季追加名单](../sources/seasonal-unique-protection.json)保持原字节；原Rolls结构没有移除或改写。",
              "- 本次只作名单与来源数据比较，没有进行游戏掉落实测，也没有把reroll百分比当作全局掉落概率。", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    report = compare()
    (ROOT / "analysis/common-unique-comparison.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    (ROOT / "docs/COMMON_UNIQUE_COMPARISON.md").write_text(render(report), encoding="utf-8", newline="\n")
    print(report["counts"])
    print(report["oldOnlyReasons"])
