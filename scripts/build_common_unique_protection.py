"""Freeze the approved unique policy and every set item from offline inputs."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ("templates/LE-base-v1.xml", "templates/base-manifest.json",
          "sources/seasonal-unique-protection.json", "sources/tunklab-unique-reroll-2026-10-18.json",
          "sources/tool-catalog.json", "sources/item-sets.json")


def read(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def build():
    catalog = read("sources/tool-catalog.json")["uniques"]
    metadata = {u["id"]: u for u in read("sources/tunklab-unique-reroll-2026-10-18.json")["items"]}
    manifest = read("templates/base-manifest.json")
    base = (ROOT / manifest["file"]).read_bytes()
    assert hashlib.sha256(base).hexdigest() == manifest["sha256"]
    rules = dict(zip(manifest["source_rule_order"], sorted(ET.fromstring(base).find("rules"),
                                                        key=lambda r: int(r.findtext("Order")))))
    legacy = {int(u.text) for n in (15, 16) for u in rules[n].findall("./conditions/Condition/Uniques/UniqueId")}
    legacy.update(u["id"] for release in read("sources/seasonal-unique-protection.json")["releases"] for u in release["uniques"])
    legacy = {uid for uid in legacy if not catalog[str(uid)]["type"].startswith("IDOL_")}
    old_uniques = {uid for uid in legacy if not catalog[str(uid)]["set"]}
    removed = {uid for uid in old_uniques if metadata[uid]["can_drop_randomly"] and metadata[uid]["reroll_chance"] == 0
               and not metadata[uid]["is_cocooned"]}
    positive = {uid for uid, item in metadata.items() if not item["catalog_hidden"] and not item["set"]
                and not item["type"].startswith("IDOL_") and not item["is_cocooned"]
                and item["can_drop_randomly"] and item["reroll_chance"] > 0}
    uniques = (old_uniques - removed) | positive
    sets = {int(uid) for uid, item in catalog.items() if item["set"] and not item["hidden"]}
    relationships = read("sources/item-sets.json")["sets"]
    assert sets == {uid for group in relationships.values() for uid in group["members"]}
    assert len(old_uniques) == 138 and len(positive) == 97 and len(uniques) == 181
    assert removed == {13, 296, 311, 422, 460, 474, 480}
    assert len(sets) == 61 and len(relationships) == 24
    assert len(positive - old_uniques) == 50 and len(sets - legacy) == 40
    return {"version": 1, "approved_on": "2026-10-18",
            "policy": {"unique_scope": "Non-set equipment only; unique idols and Harbinger's Needle remain independent.",
                       "retain_legacy": "Cocooned, non-random and positive-reroll legacy uniques.",
                       "remove": "Only legacy non-set uniques that can drop randomly and have zero reroll.",
                       "add": "All visible non-set equipment uniques with positive random-drop reroll.",
                       "sets": "All visible set items, regardless of reroll; one separately switchable rule.",
                       "deduplication": "Keep common rules and their full pools fixed, including T0 and enabled BD overlap; first match selects the earlier cue."},
            "counts": {"old_uniques": len(old_uniques), "removed_uniques": len(removed),
                       "added_uniques": len(positive - old_uniques), "uniques": len(uniques),
                       "sets": len(sets), "set_groups": len(relationships), "added_sets": len(sets - legacy)},
            "unique_ids": sorted(uniques), "set_ids": sorted(sets),
            "removed_unique_ids": sorted(removed), "added_unique_ids": sorted(positive - old_uniques),
            "added_set_ids": sorted(sets - legacy),
            "sources": [{"file": name, "sha256": hashlib.sha256((ROOT / name).read_bytes()).hexdigest()} for name in INPUTS]}


def render(document):
    catalog = read("sources/tool-catalog.json")["uniques"]
    metadata = {u["id"]: u for u in read("sources/tunklab-unique-reroll-2026-10-18.json")["items"]}
    added = set(document["added_unique_ids"])
    lines = ["# 当前通用暗金与全部套装保护", "",
             "2026-10-18落实保护范围，2026-10-19按玩家要求固定通用名单。暗金与套装分别一条规则、两个独立开关，均默认开启；崇高实验默认关闭。", "",
             "## 当前口径", "",
             "①②③④只讨论非套装暗金装备。旧138暗金中，茧化23、世界随机reroll=0的7、限定Boss／裂隙体系60、正reroll47、其他特殊奖励1。套装全部独立，既不进入②，也不随暗金reroll筛选移除。", "",
             "- **暗金181种**：旧138种移出②的7种，补入缺少的50种正reroll暗金。保留全部旧茧化、原限定来源与特殊奖励，正reroll暗金共97种已全部覆盖。",
             "- **套装61件／24套**：覆盖当前冻结词库全部套装，包含蜂农三件及旧名单之外40件，不受reroll筛选影响。",
             "- **生成两条规则**：`[通用暗金0LP保护]`、`[通用套装保护]`。每条只用一份UniqueModifiersCondition；新增ID不加Rolls、LP、WW或角色等级门槛，保留旧非赛季条目的原Rolls对象。",
             "- 六件T0仍用独立最高彗星提示；10种可选暗金神像及先驱者之针344仍各自独立。页面和通用暗金规则均显示完整181种，包含六件T0。",
             "- 通用暗金固定181种、套装固定61件，共通神像按自己的选择保留完整名单；与T0或BD重合也保留，由游戏按Order首次命中前方规则。切换BD及主副不裁剪通用名单。关掉通用开关仍保留BD明确需求、套装补全及更高LP／WW规则。",
             "- 已有浏览器保存的开关和BD目标保留；刷新页面后重新导出XML、导入游戏，才会更新游戏中的filter。", "",
             "## 移出通用暗金的7种", "",
             "只移出世界随机且基础reroll为0的暗金；这里不包含任何套装。", "",
             "| ID | 名称 |", "|---:|---|"]
    for uid in document["removed_unique_ids"]:
        lines.append(f"| {uid} | {catalog[str(uid)]['zh']} · {catalog[str(uid)]['en']} |")
    lines += ["", "296是WW暗金；移出本条通用保护不等于最终隐藏。BD明确需要上述ID时照常收集。", "",
              "## 完整暗金池：181种", "", "| ID | 名称 | 保留口径 | 本轮新增 |", "|---:|---|---|---|"]
    for uid in document["unique_ids"]:
        item = catalog[str(uid)]
        meta = metadata[uid]
        reason = "茧化" if meta["is_cocooned"] else "原限定来源／特殊奖励" if not meta["can_drop_randomly"] else f"世界随机reroll {meta['reroll_chance'] * 100:g}%"
        lines.append(f"| {uid} | {item['zh']} · {item['en']} | {reason} | {'是' if uid in added else '—'} |")
    lines += ["", "## 全部套装：24套／61件", "", "按冻结套装ID列出完整部件；整套名称不作推断。", "",
              "| 套装ID | 部件 |", "|---:|---|"]
    for sid, group in read("sources/item-sets.json")["sets"].items():
        names = "、".join(f"{catalog[str(uid)]['zh']}（{uid}）" for uid in group["members"])
        lines.append(f"| {sid} | {names} |")
    lines += ["", "## 冻结输入与验证", "",
              "- [运行期名单](../sources/common-unique-protection.json)：181暗金／61套装及新增、移出ID；源文件哈希完整保留。",
              "- [旧名单分类研究](COMMON_UNIQUE_CLASSIFICATION.md)和[纯reroll历史对照](COMMON_UNIQUE_COMPARISON.md)保留作为旧口径证据；此前204种候选包含套装筛选，已由本文181暗金＋全部61套装的242种基础池替代。",
              "- `python -X utf8 scripts/build_common_unique_protection.py`离线重建名单与本文；运行期不访问Tunklab、网络或开发缓存，Pages运行ZIP包含新名单。",
              "- [2026-10-19固定通用规则核查](COMMON_RULE_STABILITY.md)：同类去重、WW补充规则、首次命中和当前验证；此前记录中的161／175计数属于旧生成逻辑。",
              "- [原生与8组开关验证](../analysis/common-protection-pool-validation.json)、[7组WASM完整输出对照](../analysis/common-protection-pool-wasm-validation.json)、[网页开关／刷新／预览核对](../analysis/common-protection-pool-browser-validation.json)及[界面截图](images/common-protection-pool.jpg)。旧基底、赛季名单、BD需求及历史XML字节保持。验证不是游戏客户端实测。", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    document = build()
    (ROOT / "sources/common-unique-protection.json").write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    (ROOT / "docs/COMMON_UNIQUE_PROTECTION.md").write_text(render(document), encoding="utf-8", newline="\n")
    print(document["counts"])
