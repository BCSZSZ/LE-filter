"""Render every generated rule as Chinese review text, using frozen ID names."""
import hashlib
import xml.etree.ElementTree as ET
from collections import Counter

from generate_filter import ROOT, XSI, read_json

BASE_TITLES = {
    8: "所有传奇", 12: "通用高潜能暗金", 13: "通用名单暗金：第二潜能层",
    14: "通用名单暗金：第一潜能层", 15: "指定珍贵暗金", 16: "指定套装",
    19: "全部雕文", 20: "钥匙类资源", 21: "全部共鸣", 22: "全部符文",
    23: "全部词缀碎片", 24: "全部编织回响", 29: "未选择排除职业，职业隐藏关闭",
    37: "所有T8物品", 48: "两个套路装备类型上的双崇高",
    60: "重复的通用T7武器入口，关闭", 70: "未指定冠军词缀需求，关闭",
    73: "80级前的全部暗金兜底", 74: "60级前的崇高兜底",
    81: "未指定升华目标，关闭", 85: "法师碎片收集，关闭", 86: "原始者碎片收集，关闭",
    87: "游侠碎片收集，关闭", 88: "守卫碎片收集，关闭", 89: "额外进攻碎片收集，关闭",
    134: "60级前的崇高及以上物品兜底", 135: "60级前的开荒神像",
    136: "未指定开荒武器底材，关闭", 137: "未指定开荒副手底材，关闭",
    138: "开荒项链优选底材", 139: "开荒腰带优选底材", 140: "开荒胸甲优选底材",
    141: "开荒鞋子优选底材", 142: "开荒头盔优选底材", 143: "开荒戒指优选底材",
    144: "开荒手套优选底材", 145: "开荒遗物优选底材",
    146: "50级前的T3及以上物理抗性／生命拆解素材", 147: "50级前的T3及以上移速／冷却拆解素材", 148: "50级前的T3及以上抗性拆解素材",
    149: "30级前的T2及以上物理抗性／生命装备", 150: "30级前的T2及以上移速／冷却装备", 151: "30级前的T2及以上抗性装备",
    152: "未使用弓，关闭", 153: "前期近战武器", 154: "未使用魔杖或法杖，关闭",
    155: "30级前的全部稀有物品", 156: "12级前的遗物", 157: "未使用施法副手，关闭",
    158: "未使用箭袋，关闭", 159: "未使用盾牌，关闭", 160: "12级前的银戒指",
    161: "12级前的红宝石项链", 162: "10级前的全部物品兜底", 163: "最终隐藏",
}
TITLES = {"build_unique": "目标暗金", "unique_idols": "暗金神像", "tier7": "T7装备素材",
          "class_t7": "职业词缀恰好T7", "tier6": "T6装备素材", "experimental_exalted": "带目标实验词缀的崇高物品",
          "experimental": "目标实验词缀，普通阶也收", "corrupted_supplement": "目标腐化属性候选，任意阶",
          "rare_base": "指定底材上的双词缀候选", "shatter": "普通词缀拆解素材", "class_shatter": "职业词缀拆解素材",
          "health_shatter": "过渡生命碎片素材", "idol_pair": "Planner精确神像组合", "idol_strict": "Strict神像候选",
          "altar": "祭坛候选", "guide_altar": "可选护甲祭坛底材", "idol_one_affix": "单目标词缀神像候选"}
RARITIES = dict(zip("NORMAL MAGIC RARE EXALTED UNIQUE SET LEGENDARY".split(), "普通 魔法 稀有 崇高 暗金 套装 传奇".split()))
COLOR_NAMES = {"0": "白色", "3": "金黄", "4": "橙黄", "5": "橙色", "7": "红色", "8": "粉色", "11": "淡紫", "12": "蓝色", "15": "薄荷绿", "16": "亮绿"}
FLAGS = {"AllGlyphs": "全部雕文", "AllKeys": "全部钥匙类别", "AllResonances": "全部共鸣",
         "AllRunes": "全部符文", "AllShards": "全部词缀碎片", "AllWovenEchoes": "全部编织回响"}


def render():
    report = read_json("analysis/transfer-report.json")
    raw = (ROOT / report["output"]).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == report["output_sha256"]
    ref = read_json("sources/game-reference.json")
    sup = read_json("sources/builds/maxroll-reference-supplement.json")
    for section in ["affixes", "uniques"]:
        ref[section].update(sup[section])
    ref["subtypes"].update(read_json("sources/builds/review-reference.json")["subtypes"])
    rules = sorted(ET.fromstring(raw).find("rules"), key=lambda r: int(r.findtext("Order")))
    assert len(rules) == len(report["output_rules"])
    build_titles = {"flay-mana-lich": "Flay Mana Lich", "skeleton-necromancer": "Skeleton Necromancer"}
    main = build_titles[report["display"]["main_build"]]
    secondary = "、".join(build_titles[s] for s in report["display"]["secondary_builds"])
    pools, bounds = {}, []

    def named(section, value):
        entry = ref[section][str(value)]
        return entry["zh"] + f"（{value}）"

    def pool(section, values):
        if section == "affixes" and len(values) == 1156:
            return "Strict全词缀参考池（1156项，不按BD限定词缀）"
        if len(values) <= 22:
            return "、".join(named(section, i) for i in values) or "空选择"
        key = (section, tuple(values))
        pools.setdefault(key, f"P{len(pools) + 1}")
        return f"[名单{pools[key]}，{len(values)}项](RULES_REVIEW_POOLS.md#{pools[key].lower()})"

    def cmp(c, field, number):
        op = c.findtext(field)
        return "不限制" if op == "ANY" else {"MORE": ">", "MORE_OR_EQUAL": "≥", "EQUAL": "="}[op] + c.findtext(number)

    def describe(c, number):
        kind = c.get(XSI + "type")
        if kind == "AffixCondition":
            values = [int(e.text) for e in c.findall("affixes/int")]
            text = "词缀范围：" + pool("affixes", values) + f"；同一件至少命中{c.findtext('minOnTheSameItem')}项。"
            if c.findtext("advanced") != "true":
                return text + "阶数不设门槛（高级筛选未启用）。"
            return text + "单项阶数" + cmp(c, "comparsion", "comparsionValue") + "；命中词缀阶数合计" + cmp(c, "combinedComparsion", "combinedComparsionValue") + "。"
        if kind == "SubTypeCondition":
            types = [e.text for e in c.findall("type/EquipmentType")]
            bases = [e.text for e in c.findall("subTypes/int")]
            type_names = [ref["equipment_names"][t]["zh"] + ("（" + t.split("_")[1].replace("x", "×") + "）" if t.startswith("IDOL_") and t != "IDOL_ALTAR" else "") for t in types]
            text = "物品类型：" + ("、".join(type_names) if types else "未限定（空类型选择）") + "。"
            if not bases:
                return text + "底材不限。"
            return text + "底材仅限：" + "、".join(ref["subtypes"][t + ":" + s]["zh"] + f"（{t}:{s}）" for t in types for s in bases) + "。"
        if kind == "CharacterLevelCondition":
            return f"角色等级{c.findtext('minimumLvl')}–{c.findtext('maximumLvl')}，包含上下限。"
        if kind == "RarityCondition":
            return "稀有度：" + "、".join(RARITIES[s] for s in c.findtext("rarity").split()) + "。"
        if kind == "CorruptionCondition":
            return {"OnlyUncorrupted": "只收未腐化物品。", "OnlyCorrupted": "只收腐化物品。"}[c.findtext("Corruption")]
        if kind == "PotentialCondition":
            labels = {"LegendaryPotential": "传奇潜能LP", "WeaversWill": "编织者意志WW", "WeaversTouch": "编织者触碰", "ForgingPotential": "制作潜能FP"}
            parts = [labels[e.tag[3:]] + ("≥" if e.tag.startswith("Min") else "≤") + e.text for e in c if e.text and e.get(XSI + "nil") != "true"]
            return "潜能配置：" + "；".join(parts) + "。LP/WW的组合适用方式按原XML保留，尚未客户端实测。" if any("LP" in p or "WW" in p for p in parts) else "潜能条件：" + "；".join(parts) + "。"
        if kind == "UniqueModifiersCondition":
            objects = c.findall("Uniques")
            values = [int(u.findtext("UniqueId")) for u in objects]
            text = "仅限物品：" + pool("uniques", values) + "。"
            start = len(bounds)
            for u in objects:
                for roll in u.findall("Rolls/UniqueModifierWithRollId"):
                    low, high = roll.findtext("Modifier/MinRoll"), roll.findtext("Modifier/MaxRoll")
                    if low or high:
                        bounds.append((number, int(u.findtext("UniqueId")), roll.findtext("RollId"), low, high))
            if len(bounds) > start:
                text += f"另有{len(bounds) - start}项唯一属性roll编码边界，见[附录](RULES_REVIEW_POOLS.md#roll-bounds)；不换算成面板属性门槛。"
            return text
        if kind == "AffixCountCondition":
            return "封印／词缀数量配置：" + "；".join(("未封印（sealedType=NotSealed）" if e.tag == "sealedType" and e.text == "NotSealed" else e.tag + "=" + (e.text or "空")) for e in c) + "。与阶数条件的具体计数联动待客户端验证。"
        if kind == "ClassCondition":
            return "职业要求选择：" + (c.findtext("req") or "空") + "（None表示没有配置排除职业）。"
        if kind == "FactionCondition":
            return "阵营标记：" + "、".join("命运之环CoF" if e.text == "CircleOfFortune" else e.text for e in c.findall("EligibleFactions/FactionID")) + "。"
        if kind in {"GlyphCondition", "KeysCondition", "ResonancesCondition", "RuneCondition", "CraftingMaterialsCondition", "WovenEchoesCondition"}:
            return "资源选择：" + "；".join(FLAGS[e.text] for e in c) + "。"
        raise AssertionError("Untranslated condition: " + kind)

    lines = [
        "# 主套路＋副套路：逐条中文规则审阅稿", "",
        f"本次默认对应：**主套路＝{main}，副套路＝{secondary}**。粉色表示主套路，蓝色表示副套路；两者共享的条件按主套路显示为粉色。以后颜色跟随主／副身份。主副需求同等保留，Raxx通用珍贵物品、质量分层和材料保留原提示样式。", "",
        f"本文由实际成品XML逐条翻译，覆盖{report['rules']}条（{report['enabled']}启用／{report['rules'] - report['enabled']}关闭），按游戏匹配顺序G1→G{report['rules']}排列。本轮调整主副显示身份；拾取条件、门槛及规则次序沿用上一版。你可以直接按G编号提出修改。", "",
        "## 阅读约定", "",
        "- 一条规则内的不同条件全部同时满足；多条启用显示规则之间形成收集并集。第一个命中决定提示样式。",
        "- 本文‘共享’指同部位、同门槛的交集词缀，或完整条件相同的规则。物品用不同词缀分别命中两个套路时，仍按先命中的层显示；通用T8／双崇高等上层提示也可能先命中。",
        "- 词缀列表‘至少1项’表示任选其中一项；‘至少2项／3项’按对应列表计数。精确列表含2项且要求2项时，必须两条都有。",
        "- 词缀名字里的‘共享·’是游戏本地化原名，和本过滤器的主副共享关系无关。例如‘共享·击中时施加流血几率’仍可属于副套路专属需求。",
        "- T表示词缀阶数；FP是制作潜能；角色等级限制不等于物品需求等级。‘阶数不设门槛’不会将未启用的保存值误当门槛。",
        "- 0LP目标有无潜能限制兜底；潜能分层也单独列出原配置值。LP/WW组合、封印计数及特殊神像计数还需客户端核对。",
        "- 关闭规则不参与当前匹配。后面列出其保留条件，便于审阅，不代表建议直接启用空选择。",
        "- 大名单单独放在[名单附录](RULES_REVIEW_POOLS.md)，每项有中文、英文与ID；本页逐条写清门槛，完整XML见[成品](../" + report["output"] + ")。", "",
        "## 先审阅这些收集策略", "",
        "- 目标与替代暗金共25种，0LP也保留；有重复之后需要按实际收藏进度收紧。",
        "- T6与T7按各自装备类型匹配，100级仍收T6。武器素材分别限制巫妖的单手斧／匕首与死灵的双手斧。",
        "- 单目标词缀神像G149–154、宽Weaver G156、反伤G157仍启用；这是当前Strict里的宽松收集层。",
        "- G88–102是任意阶目标腐化属性候选；G148收护甲祭坛底材，没有额外词缀／阶数门槛。",
        "- 资源、Raxx通用暗金／套装、低等级兜底仍保留；只有G187最终隐藏，职业隐藏G26关闭。", "",
        "| 规则段 | 审阅内容 |", "|---|---|",
        "| G1–12 | 主副目标暗金、共享名单、潜能分层与0LP兜底 |",
        "| G13–27 | 通用珍贵物品、材料、职业隐藏关闭与T8 |",
        "| G28–82 | 部位T7、双崇高、Havoc／FP52制作候选、部位T6 |",
        "| G83–102 | 实验词缀、低等级兜底、腐化属性候选 |",
        "| G103–118 | 升华关闭、指定底材双词缀、拆解碎片 |",
        "| G119–133 | 精确神像组合、备用组合、Strict混合词缀池 |",
        "| G134–157 | 祭坛、单词缀神像、可选方案与宽泛神像 |",
        "| G158–187 | 开荒规则及最终隐藏 |", "",
        "## 玩家仍需决定和完成的事项", "",
        "- 已够的暗金、T6素材和神像要随收藏进度收紧；特别检查上面的0LP兜底与单词缀／宽Weaver神像层。",
        "- 碎片库存足够后收紧G109–111。魔力34、暴击避免97不在当前Strict默认拆解池，缺少时另加明确需求。",
        "- 按配装选择876＋891虚弱备用神像（G127）、护甲祭坛底材（G148）及可选腐化暴击避免神像（G155）。",
        "- 使用已有装备核对导入后的规则数量、排序和提示，记录未确认计数的实际表现。完整逐项操作见[使用说明与玩家待办](COMBINED_FILTER_GUIDE.md#仍需玩家做的事)。", "",
        "## 按匹配顺序的全部规则", "",
    ]
    for r, row in zip(rules, report["output_rules"]):
        n, category = row["number"], row["category"]
        role = {"MAIN": "主套路／粉色", "SECONDARY": "副套路／蓝色", "COMMON": "基底通用"}[row["display_role"]]
        if len(row["owners"]) > 1:
            role += "（共享，归主套路）"
        title = BASE_TITLES[row["template"]] if category == "raxx" else TITLES.get(category)
        label = row.get("label", "")
        if category == "build_unique":
            title += "：潜能分层" if " LP" in label else "：无潜能门槛兜底"
        if category == "crafting":
            title = "实验词缀＋任意T7的Havoc候选" if "Experimental" in label else "好词缀＋任意T7的Havoc候选" if "Havoc" in label else "FP52高制作潜能候选" if "52+ FP" in label else "永恒臂铠T7制作候选"
        if category == "guide_idol":
            title = "点燃＋虚弱备用神像" if "Frailty" in label else "可选腐化暴击避免神像"
        if category == "idol_generic":
            title = "通用反伤神像" if "Reflect" in label else "宽Weaver神像候选"
        assert title, category
        lines += [f"### G{n}｜{title}｜{role}", "", "状态：" + ("启用" if row["enabled"] else "关闭，不参与当前匹配") + "；动作：" + ("显示" if r.findtext("type") == "SHOW" else "隐藏") + "。", ""]
        conditions = list(r.find("conditions"))
        lines.extend("- " + describe(c, n) for c in conditions)
        if not conditions:
            lines.append("- 无条件：前面的规则都未命中时，隐藏剩余全部物品。")
        color = COLOR_NAMES[r.findtext("color")] if r.findtext("recolor") == "true" else "原色"
        effects = [color, "大写强调" if r.findtext("emphasized") == "true" else "普通字体", "Begin提示音" if r.findtext("SoundId") == "6" else "静音"]
        if r.findtext("BeamOverride") == "true":
            effects.append("沿用基底指定光柱")
        if r.findtext("MapIconId") != "0":
            effects.append("沿用基底地图图标")
        lines += ["", "提示：" + "；".join(effects) + "。", ""]
    appendix = ["# 规则审阅稿：名单附录", "", "从实际XML提取；同一名单复用，未省略名单里的选择项。词缀阶数与启用状态以[逐条审阅稿](RULES_REVIEW.md)为准。", ""]
    for (section, values), key in pools.items():
        appendix += [f"<a id=\"{key.lower()}\"></a>", "", f"## {key}｜{'词缀' if section == 'affixes' else '物品'}名单｜{len(values)}项", "", "| ID | 中文 | 英文 |", "|---:|---|---|"]
        for i in values:
            entry = ref[section][str(i)]
            appendix.append(f"| {i} | {entry['zh'].replace('|', '/')} | {entry['en'].replace('|', '/')} |")
        appendix.append("")
    appendix += ['<a id="roll-bounds"></a>', "", "## 唯一属性roll编码边界", "", "以下是原XML保存的编码值，不代表同数值的面板属性。无边界的nil不列为限制。", "", "| G | 物品 | 唯一属性索引 | 最小编码 | 最大编码 |", "|---:|---|---:|---|---|"]
    appendix.extend(f"| {n} | {named('uniques', uid)} | {roll} | {low or '不限'} | {high or '不限'} |" for n, uid, roll, low, high in bounds)
    for path, content in [("docs/RULES_REVIEW.md", lines), ("docs/RULES_REVIEW_POOLS.md", appendix)]:
        (ROOT / path).write_text("\n".join(content).rstrip() + "\n", encoding="utf-8", newline="\n")
    assert sum(1 for s in lines if s.startswith("### G")) == len(rules)
    print({"review_rules": len(rules), "large_lists": len(pools), "roll_bounds": len(bounds), "conditions": dict(Counter(c.get(XSI + 'type') for r in rules for c in r.find('conditions')))})


if __name__ == "__main__":
    render()
