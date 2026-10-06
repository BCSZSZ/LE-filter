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
    style = read_json(m["feedback_reference"]["local_path"])
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
             "Flay主套路粉色，Skeleton副套路蓝色；同层同时匹配两个套路时，主套路先匹配，因此共享按主。收集条件取两者并集。通用高潜能／多T7先匹配时使用通用档色；T8兜底为铁匠，不计入T7数量。", "",
             "神像普通目标不包含腐化词缀。Flay两项齐全层优先、一项层仍常驻；骷髅两项目标为候选，不保证任意两项就是最佳前后缀配对。", "",
             f"额外单T7阶段兜底是G{m['stage_rule']}，默认开启，玩家手动关闭，无等级自动退出。T6目标层保留0–84级。各条件在同一规则内必须同时满足。", "",
             "声音分类和v2能否区分的核对见[四档提示审阅](SOUND_STYLE_REVIEW.md)。当前三T7彗星→双T7含BD目标灵感→任意双T7开始→目标单T7；C2目标、C1、C3、T6分别按主一组、副一组排列。静音沿用原颜色设置。", ""]
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
        if entry.get("shared_unique_ids"):
            lines.append("- 其中共享需求：" + names("uniques", entry["shared_unique_ids"]) + "；并入主套路提示。")
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
        lines += ["", "提示：" + color + "；" + ("强调" if r.findtext("emphasized") == "true" else "普通字体") + "；声音=" + style["sounds"][r.findtext("SoundId")]["zh"] +
                  "；地图图标=" + style["map_icons"][r.findtext("MapIconId")]["zh"] + "；光柱=" + r.findtext("BeamSizeOverride") + "。", ""]
    appendix = ["# 当前成品：完整名单与唯一属性边界", "", "由实际XML提取；门槛与启用状态见[逐条规则](CURRENT_RULES_REVIEW.md)。", ""]
    for (section, values), key in pools.items():
        appendix += [f'<a id="{key.lower()}"></a>', "", f"## {key}｜{len(values)}项", "", "| ID | 中文 | 英文 |", "|---:|---|---|"]
        appendix.extend(f"| {i} | {ref[section][str(i)]['zh']} | {ref[section][str(i)]['en']} |" for i in values)
        appendix.append("")
    appendix += ['<a id="roll-bounds"></a>', "", "## 原暗金唯一属性roll编码边界", "", "原364项边界保留；WW1–13静音名单另引用一份，共728次。不是面板数值或新增BD潜能门槛。当前LP与WW分为独立规则，实际提示仍待客户端核对。", "", "| G | 暗金ID | 属性索引 | 最小编码 | 最大编码 |", "|---:|---:|---:|---|---|"]
    appendix.extend(f"| {n} | {uid} | {roll} | {low or '不限'} | {high or '不限'} |" for n, uid, roll, low, high in bounds)
    guide = ["# 最新版：Flay Mana Lich＋Skeleton Necromancer v3", "",
             f"[可导入XML](../{m['output']})｜[{m['rules']}条可审阅规则](CURRENT_RULES_REVIEW.md)｜[完整名单](CURRENT_RULE_POOLS.md)。", "",
             "基于[LE Base Template v1](BASE_TEMPLATE.md)，Flay为主套路／粉色，骷髅Nec为副套路／蓝色，共享按主处理。两者同等收集；原187条试制与138条v2保留为历史。四档方案和原v2能否区分见[提示审阅表](SOUND_STYLE_REVIEW.md)。", "",
             "## 当前收集策略", "",
             "- 暗金：20种Strict目标均有0LP保护；珍贵名单仍152项。主套路名单合并共享2项与专属9项。按用户本轮要求，任意1LP／2LP均有独立提示，突破原412项潜能白名单；BD的1LP另响灵感。LP与WW条件分开，WW采用已确认的14／17／20门槛；低两档仍用原潜能白名单并补3项BD目标。未达14的非BD WW名单保留项静音。",
             "- 装备：19份目标按BD／装备类型分别绑定。先收任意至少3条T7（彗星），再收双T7且至少一条是对应部位BD目标T7（灵感），其余任意双T7（开始）；C1收BD目标单T7（开始），C3收非目标单T7＋BD目标不限阶数（铁匠）。C1／C2／C3／C4的T7条件均为恰好7阶，T8不计入。全量T7计数覆盖1156冻结ID，通用C2／C4保留原23类装备。C2目标层、C1与C3各自主一组、副一组。两条T7之外仅有低阶BD目标，不算双T7含目标层。",
             "- T8及以上：仅作铁匠档保留兜底，位于多T7、BD目标及实验／冠军规则之后、静音C4之前。全1156项池与无等级上限保留，不随C4关闭；T8本身不证明BD需要或可作为传奇合成素材。",
             f"- 额外单T7阶段：G{m['stage_rule']}默认开启，名称含[C4 额外单T7阶段：手动关闭]，没有等级退出；静音、无图标、无光柱。阶段结束后只关闭这一条，前三类继续保留。其他实验／碎片／底材规则仍可能显示单T7。",
             "- T6：为0–84级补收对应部位的BD目标T6，85级自动不匹配。匕首／单手斧同池等价合并，19条压成18条；主一组、副一组，静音无图标。其他部位目标池不同，不混池；双T6没有常驻保护。",
             "- Flay神像：中型843／854、厚实876／886，各有两项齐全和至少一项两层；Weaver与Lagon均保留。两项灵感、一项开始；腐化不凑数，不要求腐化。厚实只有886仍属候选，876必需条件与891备用没有静默加入。",
             "- 骷髅神像：使用Strict两项目标入口，剥离腐化词缀，普通目标至少2项、阶数不限。原来源底材保留，包括Large Omen的多个职业底材；本轮没有根据类名猜测更窄配对。通用过渡两项／一项层仍在90／75级退出。",
             "- 祭坛：按BD绑定底材与目标池，采用Raxx至少一项、阶数不限；不移植Strict合计T8／T10或双崇高门槛。祭坛的腐化目标保留在其目标池，神像普通池另行剥离腐化。",
             "- 定向底材：五类Strict底材已填入Raxx入口并启用，不附加Strict词缀／FP门槛。永恒臂铠为共享制作底材，属于宽收集。",
             "- 可选项：职业隐藏、冠军词缀、升华、紧缺碎片、普通实验词缀与未给出的开荒优选底材关闭。普通实验目标676／679和紧缺碎片候选36／825／945已填入，按需要手动开启；崇高实验装备及通用进攻／防御碎片沿用基底。仅保留侍祭职业碎片，其他四职业碎片关闭。", "",
             "- 提示：只有四档有声音的规则有地图图标与光柱。静音明确设SoundId=1、MapIconId=1（无，不是默认0）、BeamOverride=true／NONE；沿用基底或BD规则原有颜色、强调设置，不因静音额外设灰色／白色。主副光柱匹配粉／蓝；四档光柱依次小／中／大／最大。XML无逐条音量字段，没有实际听音或客户端验证。", "",
             "## 玩家待办", "",
             f"1. 单T7储备足够后，手动关闭G{m['stage_rule']} [C4 额外单T7阶段：手动关闭]；它不会随等级关闭。",
             "2. 没有定向底材需求时关闭Target base五条；其Raxx门槛较宽，会保留指定底材的普通／魔法／稀有／崇高物品。",
             "3. 对照库存调整碎片收集。紧缺入口默认关闭；魔力34、暴击避免97未冒充库存缺口，可按实际需要补入。",
             "4. 需要普通实验目标时开启Optional wanted experimentals；需要升华或冠军词缀时先填写对应目标。",
             "5. Flay没有腐化虚弱1069时，攻略891备用组合可后续补充；Skeleton的必须／可选前后缀配对及跨职业Omen取舍也可以继续细化。",
             f"6. 导入后核对{m['rules']}条规则、排序、颜色与声音。封印／特殊词缀计数、LP／WW边界和客户端兼容性尚未实测。开荒专属优选底材未提供，不能把终局配装当开荒路线。", "",
             "## 复现与证据", "", "```powershell", "python -X utf8 scripts/extract_raxx_variables.py", "python -X utf8 scripts/generate_current_filter.py", "python -X utf8 scripts/verify_current_filter.py", "python -X utf8 scripts/render_current_filter.py", "```", "",
             "离线使用已提交的模板、Strict、词库与审阅结果，无需Downloads或缓存。来源与G／B／R／X对应见[生成报告](../analysis/current-filter-report.json)，结构和有限案例见[验证报告](../analysis/current-filter-validation.json)。验证不充当游戏客户端实测。", ""]
    for path, content in [("docs/CURRENT_RULES_REVIEW.md", lines), ("docs/CURRENT_RULE_POOLS.md", appendix), ("docs/CURRENT_FILTER_GUIDE.md", guide)]:
        (ROOT / path).write_text("\n".join(content).rstrip() + "\n", encoding="utf-8", newline="\n")
    alert_doc = ["# 当前全部规则：声音与图标分类", "", "从实际v3 XML读取，包含关闭规则的预设档。旧v2情况、能力缺口及分类理由见[审阅结论](SOUND_STYLE_REVIEW.md)。", "",
                 "| G | 名称 | 状态 | 声音 | 图标 | 光柱 |", "|---:|---|---|---|---|---|"]
    for r, row in zip(rules, m["output_rules"], strict=True):
        alert_doc.append(f"| {row['number']} | {row['name'] or '基底通用／最终隐藏'} | {'启用' if row['enabled'] else '关闭'} | {row['sound_name']} | {style['map_icons'][r.findtext('MapIconId')]['zh']} | {r.findtext('BeamSizeOverride')} |")
    (ROOT / "docs/CURRENT_ALERT_INDEX.md").write_text("\n".join(alert_doc) + "\n", encoding="utf-8", newline="\n")
    assert sum(line.startswith("### G") for line in lines) == m["rules"]
    print({"review_rules": m["rules"], "large_lists": len(pools), "preserved_roll_bounds": len(bounds)})


if __name__ == "__main__":
    main()
