"""Render the actual current XML and its remaining player choices in Chinese."""
import hashlib
import xml.etree.ElementTree as ET

from extract_raxx_variables import gate_text, inspect_rule
from generate_current_filter import REPORT
from generate_filter import ROOT, XSI, read_json
from render_rules_review import COLOR_NAMES, FLAGS


def main():
    m = read_json(REPORT)
    raw = (ROOT / m["output"]).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == m["output_sha256"]
    rules = sorted(ET.fromstring(raw).find("rules"), key=lambda r: int(r.findtext("Order")))
    ref = read_json("sources/game-reference.json")
    supplement = read_json("sources/builds/maxroll-reference-supplement.json")
    for section in ["affixes", "uniques"]:
        ref[section].update(supplement[section])
    ref["subtypes"].update(read_json("sources/builds/review-reference.json")["subtypes"])
    pools, bounds = {}, []

    def names(section, values):
        if section == "affixes" and len(values) == 1156:
            return "冻结词库全量1156项（不按BD裁剪）"
        if len(values) > 20:
            key = (section, tuple(values))
            pools.setdefault(key, f"P{len(pools) + 1}")
            return f"[名单{pools[key]}，{len(values)}项](CURRENT_RULE_POOLS.md#{pools[key].lower()})"
        return "、".join(ref[section][str(i)]["zh"] + f"（{i}）" for i in values) or "空选择"

    def scope(row):
        parts = [ref["equipment_names"][t]["zh"] + ("（" + t.split("_")[1].replace("x", "×") + "）" if t.startswith("IDOL_") and t != "IDOL_ALTAR" else "") for t in row["types"]]
        text = "、".join(parts) or "未限定装备类型／该条件不按类型筛选"
        if row["subtypes"]:
            text += "；底材=" + "、".join(ref["subtypes"][t + ":" + str(i)]["zh"] for t in row["types"] for i in row["subtypes"])
        elif row["types"]:
            text += "；底材不限"
        return text

    lines = ["# 最新Flay＋骷髅Nec：逐条可审阅规则", "",
             f"从实际[成品XML](../{m['output']})生成，共{m['rules']}条（{m['enabled']}启用）。G=当前成品Order+1；B=新基底入口；R=冻结Raxx入口。", "",
             "Flay主套路粉色，Skeleton副套路蓝色；同层同时匹配两个套路时，主套路先匹配，因此共享按主。收集条件取两者并集。不同层以最早匹配的层提示；基底通用样式保留。", "",
             "神像普通目标不包含腐化词缀。Flay两项齐全层优先、一项层仍常驻；骷髅两项目标为候选，不保证任意两项就是最佳前后缀配对。", "",
             f"额外单T7阶段兜底是G{m['stage_rule']}，默认开启，玩家手动关闭，无等级自动退出。T6目标层保留0–84级。各条件在同一规则内必须同时满足。", ""]
    for r, entry in zip(rules, m["output_rules"], strict=True):
        n = entry["number"]
        row = inspect_rule(r)
        role = {"MAIN": "主套路／粉色", "SECONDARY": "副套路／蓝色", "COMMON": "基底通用"}[entry["role"]]
        if len(entry["owners"]) == 2:
            role += "（共享）"
        title = entry["name"] or {8: "所有传奇", 19: "全部雕文", 20: "钥匙类资源", 21: "全部共鸣",
                                  22: "全部符文", 23: "全部词缀碎片", 24: "全部编织回响", 163: "最终隐藏"}[entry["source_raxx_rule"]]
        lines += [f"### G{n}｜{title}｜{role}", "",
                  f"{'启用' if entry['enabled'] else '关闭'}；{'显示' if row['action'] == 'SHOW' else '隐藏'}；B{entry['base_rule']}／原R{entry['source_raxx_rule']}。", "",
                  "- 类型：" + scope(row) + "。"]
        lines.extend("- 词缀条件" + str(i + 1) + "的范围：" + names("affixes", pool) + "。" for i, pool in enumerate(row["affix_pools"]))
        if row["unique_ids"]:
            lines.append("- 指定物品：" + names("uniques", row["unique_ids"]) + "。")
        lines.append("- 门槛：" + gate_text(row) + "。")
        start = len(bounds)
        for c in r.find("conditions"):
            kind = c.get(XSI + "type")
            if kind in {"GlyphCondition", "KeysCondition", "ResonancesCondition", "RuneCondition", "CraftingMaterialsCondition", "WovenEchoesCondition"}:
                lines.append("- 资源：" + "、".join(FLAGS[e.text] for e in c) + "。")
            elif kind == "ClassCondition":
                lines.append("- 职业隐藏要求=" + c.findtext("req") + "，当前关闭。")
            elif kind == "UniqueModifiersCondition":
                for u in c.findall("Uniques"):
                    for roll in u.findall("Rolls/UniqueModifierWithRollId"):
                        low, high = roll.findtext("Modifier/MinRoll"), roll.findtext("Modifier/MaxRoll")
                        if low or high:
                            bounds.append((n, int(u.findtext("UniqueId")), roll.findtext("RollId"), low, high))
        if len(bounds) > start:
            lines.append(f"- 保留{len(bounds) - start}项唯一属性roll编码边界，见[边界附录](CURRENT_RULE_POOLS.md#roll-bounds)，不换算成面板门槛。")
        if not len(r.find("conditions")):
            lines.append("- 无条件：前面的显示规则均未匹配时，隐藏其余物品。")
        color = COLOR_NAMES[r.findtext("color")] if r.findtext("recolor") == "true" else "原色"
        lines += ["", "提示：" + color + "；" + ("强调" if r.findtext("emphasized") == "true" else "普通字体") + "；" + ("Begin声音" if r.findtext("SoundId") == "6" else "静音") + "。", ""]
    appendix = ["# 当前成品：完整名单与唯一属性边界", "", "由实际XML提取；门槛与启用状态见[逐条规则](CURRENT_RULES_REVIEW.md)。", ""]
    for (section, values), key in pools.items():
        appendix += [f'<a id="{key.lower()}"></a>', "", f"## {key}｜{len(values)}项", "", "| ID | 中文 | 英文 |", "|---:|---|---|"]
        appendix.extend(f"| {i} | {ref[section][str(i)]['zh']} | {ref[section][str(i)]['en']} |" for i in values)
        appendix.append("")
    appendix += ['<a id="roll-bounds"></a>', "", "## 原暗金唯一属性roll编码边界", "", "从原名单保留，并非面板数值或新增BD潜能门槛。LP／WW组合和实际提示仍待客户端核对。", "", "| G | 暗金ID | 属性索引 | 最小编码 | 最大编码 |", "|---:|---:|---:|---|---|"]
    appendix.extend(f"| {n} | {uid} | {roll} | {low or '不限'} | {high or '不限'} |" for n, uid, roll, low, high in bounds)
    guide = ["# 最新版：Flay Mana Lich＋Skeleton Necromancer v2", "",
             f"[可导入XML](../{m['output']})｜[{m['rules']}条可审阅规则](CURRENT_RULES_REVIEW.md)｜[完整名单](CURRENT_RULE_POOLS.md)。", "",
             "基于[LE Base Template v1](BASE_TEMPLATE.md)，Flay为主套路／粉色，骷髅Nec为副套路／蓝色，共享按主处理。两者同等收集；原187条试制保留为历史。", "",
             "## 当前收集策略", "",
             "- 暗金：20种Strict目标均有0LP保护；目标补入原143项珍贵名单，合并152项。保留原通用高潜能层，不另建BD的1／2／3LP分层。本次不添加5种旧正文替代品。",
             "- 装备：19份目标按BD／装备类型分别绑定，C1收目标T7，C3收目标任意阶＋任意T7；C2保护任意双／多T7。C2／C3的T7计数及C4覆盖全部1156冻结ID，C2／C4保留原23类装备。",
             f"- 额外单T7阶段：G{m['stage_rule']}默认开启，名称含[4 ALL T7 PHASE]，没有等级退出。阶段结束后只关闭这一条，前三类继续保留。其他实验／碎片／底材规则仍可能显示单T7。",
             "- T6：按两BD目标补收，保持角色0–84级；双T6没有常驻双／多T7保护。目标候选不保证整件装备毕业或可制作。",
             "- Flay神像：中型843／854、厚实876／886，各有两项齐全和至少一项两层；Weaver与Lagon均保留。两项层Begin声音，一项层静音；腐化不凑数，不要求腐化。厚实只有886仍属候选，876必需条件与891备用没有静默加入。",
             "- 骷髅神像：使用Strict两项目标入口，剥离腐化词缀，普通目标至少2项、阶数不限。原来源底材保留，包括Large Omen的多个职业底材；本轮没有根据类名猜测更窄配对。通用过渡两项／一项层仍在90／75级退出。",
             "- 祭坛：按BD绑定底材与目标池，采用Raxx至少一项、阶数不限；不移植Strict合计T8／T10或双崇高门槛。祭坛的腐化目标保留在其目标池，神像普通池另行剥离腐化。",
             "- 定向底材：五类Strict底材已填入Raxx入口并启用，不附加Strict词缀／FP门槛。永恒臂铠为共享制作底材，属于宽收集。",
             "- 可选项：职业隐藏、冠军词缀、升华、紧缺碎片、普通实验词缀与未给出的开荒优选底材关闭。普通实验目标676／679和紧缺碎片候选36／825／945已填入，按需要手动开启；崇高实验装备及通用进攻／防御碎片沿用基底。仅保留侍祭职业碎片，其他四职业碎片关闭。", "",
             "## 玩家待办", "",
             f"1. 单T7储备足够后，手动关闭G{m['stage_rule']} [4 ALL T7 PHASE]；它不会随等级关闭。",
             "2. 没有定向底材需求时关闭Target base五条；其Raxx门槛较宽，会保留指定底材的普通／魔法／稀有／崇高物品。",
             "3. 对照库存调整碎片收集。紧缺入口默认关闭；魔力34、暴击避免97未冒充库存缺口，可按实际需要补入。",
             "4. 需要普通实验目标时开启Optional wanted experimentals；需要升华或冠军词缀时先填写对应目标。",
             "5. Flay没有腐化虚弱1069时，攻略891备用组合可后续补充；Skeleton的必须／可选前后缀配对及跨职业Omen取舍也可以继续细化。",
             f"6. 导入后核对{m['rules']}条规则、排序、颜色与声音。封印／特殊词缀计数、LP／WW组合和客户端兼容性尚未实测。开荒专属优选底材未提供，不能把终局配装当开荒路线。", "",
             "## 复现与证据", "", "```powershell", "python -X utf8 scripts/extract_raxx_variables.py", "python -X utf8 scripts/generate_current_filter.py", "python -X utf8 scripts/verify_current_filter.py", "python -X utf8 scripts/render_current_filter.py", "```", "",
             "离线使用已提交的模板、Strict、词库与审阅结果，无需Downloads或缓存。来源与G／B／R／X对应见[生成报告](../analysis/current-filter-report.json)，结构和有限案例见[验证报告](../analysis/current-filter-validation.json)。验证不充当游戏客户端实测。", ""]
    for path, content in [("docs/CURRENT_RULES_REVIEW.md", lines), ("docs/CURRENT_RULE_POOLS.md", appendix), ("docs/CURRENT_FILTER_GUIDE.md", guide)]:
        (ROOT / path).write_text("\n".join(content).rstrip() + "\n", encoding="utf-8", newline="\n")
    assert sum(line.startswith("### G") for line in lines) == m["rules"]
    print({"review_rules": m["rules"], "large_lists": len(pools), "preserved_roll_bounds": len(bounds)})


if __name__ == "__main__":
    main()
