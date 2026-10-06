"""Build the user-approved reusable base, without filling any BD targets."""
import hashlib
import json
import xml.etree.ElementTree as ET
from copy import deepcopy

from extract_raxx_variables import ROOT, XSI, inspect_rule, read_json

TEMPLATE = "templates/LE-base-v1.xml"
MANIFEST = "templates/base-manifest.json"
INSTRUCTIONS = {
    36: "2 MULTI T7: ALL AFFIXES / ALL EQUIPMENT TYPES; NO BD TARGET REQUIRED.",
    51: "T6 TARGETS: CHOOSE TYPES YOUR BD(S) USE.",
    52: "Duplicate TARGET T6/T7 rules for each BD / equipment type",
    53: "so the right target affixes stay on the right equipment type.",
    56: "4 ALL T7 PHASE: ONE RULE, ALL AFFIXES AND EQUIPMENT TYPES.",
    57: "DEFAULT ON. DISABLE [4 ALL T7 PHASE] MANUALLY AFTER THIS STAGE.",
    58: "3 TARGET + T7: A BD AFFIX AT ANY TIER AND A T7 ON THE SAME ITEM.",
    59: "FILL PER BD / TYPE. KEEP ABOVE [4 ALL T7 PHASE]. NO FP GATE.",
}


def set_pool(condition, pool, count):
    condition.find("affixes").clear()
    for i in pool:
        ET.SubElement(condition.find("affixes"), "int").text = str(i)
    for field, text in {"minOnTheSameItem": str(count), "advanced": "true",
                        "comparsion": "MORE_OR_EQUAL", "comparsionValue": "7",
                        "combinedComparsion": "ANY"}.items():
        condition.find(field).text = text


def main():
    source = read_json("sources/manifest.json")["baseline"]
    raw = (ROOT / source["local_path"]).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == source["sha256"]
    flags = read_json("sources/builds/strict-variable-reference.json")
    pool = sorted(map(int, flags["special_affix_type"]))
    root = ET.fromstring(raw)
    nodes = sorted(root.find("rules"), key=lambda r: int(r.findtext("Order")))
    rules = {i: r for i, r in enumerate(nodes, 1)}
    for i in range(38, 48):
        rules[i].find("nameOverride").text = "[1 TARGET T7] " + rules[i].findtext("nameOverride")
    for i, name in INSTRUCTIONS.items():
        rules[i].find("nameOverride").text = name
    for i, count, name in [(48, 2, "[2 MULTI T7] ALL AFFIXES / ALL EQUIPMENT"),
                           (60, 1, "[4 ALL T7 PHASE] DISABLE MANUALLY AFTER THIS STAGE"),
                           (62, 1, "[3 TARGET + T7] FILL TARGETS PER BD / EQUIPMENT TYPE")]:
        c = next(c for c in rules[i].find("conditions") if c.get(XSI + "type") == "AffixCondition")
        set_pool(c, pool, count)
        rules[i].find("nameOverride").text = name
    # R60 replaces both old broad pools and follows the target-aware R62.
    original_scope = next(c for c in rules[48].find("conditions") if c.get(XSI + "type") == "SubTypeCondition")
    old_scope = next(c for c in rules[60].find("conditions") if c.get(XSI + "type") == "SubTypeCondition")
    rules[60].find("conditions").remove(old_scope)
    rules[60].find("conditions").append(deepcopy(original_scope))
    for c in list(rules[62].find("conditions")):
        if c.get(XSI + "type") == "CorruptionCondition":
            rules[62].find("conditions").remove(c)
    order = [i for i in rules if i not in {60, 61}]
    order.insert(order.index(62) + 1, 60)
    for position, i in enumerate(order):
        rules[i].find("Order").text = str(position)
    root.find("rules")[:] = [rules[i] for i in reversed(order)]
    root.find("name").text = "LE Base Template v1"
    root.find("description").text = "Raxx-derived template. Fill BD targets; manually disable [4 ALL T7 PHASE] after collecting."
    ET.register_namespace("i", XSI[1:-1])
    ET.indent(root, space="  ")
    (ROOT / "templates").mkdir(exist_ok=True)
    (ROOT / TEMPLATE).write_bytes(ET.tostring(root, encoding="utf-8", xml_declaration=True))
    current = {r: b for b, r in enumerate(order, 1)}
    manifest = {"name": "LE Base Template v1", "file": TEMPLATE,
                "sha256": hashlib.sha256((ROOT / TEMPLATE).read_bytes()).hexdigest(),
                "source": source, "configured_for_builds": [], "final_bd_filter": False,
                "full_affix_ids": pool, "full_affix_metadata": "sources/builds/strict-variable-reference.json",
                "full_affix_metadata_sha256": hashlib.sha256((ROOT / "sources/builds/strict-variable-reference.json").read_bytes()).hexdigest(),
                "scope_types": inspect_rule(rules[48])["types"], "source_rule_order": order,
                "rule_count": len(order), "removed_source_rules": [61],
                "layers": [
                    {"id": "C1", "name": "对应部位BD目标T7", "source_rules": list(range(38, 48)), "requires_bd_type_targets": True},
                    {"id": "C2", "name": "任意双／多T7全量保护", "source_rules": [48], "requires_bd_type_targets": False},
                    {"id": "C3", "name": "BD目标不限阶数＋T7", "source_rules": [62], "requires_bd_type_targets": True},
                    {"id": "C4", "name": "单T7阶段全量收集", "source_rules": [60], "requires_bd_type_targets": False,
                     "default_enabled": True, "auto_level_exit": False, "player_disables_manually": True}],
                "target_defaults_are_raxx_examples": True}
    for layer in manifest["layers"]:
        layer["base_rules"] = [current[r] for r in layer["source_rules"]]
    (ROOT / MANIFEST).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    guide = ["# 当前基底：LE Base Template v1", "",
             "用户已确认以下四类，今后以此模板定制BD。XML：[LE-base-v1.xml](../templates/LE-base-v1.xml)；机器清单：[base-manifest.json](../templates/base-manifest.json)。R是冻结原版编号，B是新模板Order+1。", "",
             "| 优先类别 | 当前B入口／原R入口 | 条件 | 默认与退出方式 |", "|---|---|---|---|"]
    for layer, condition in zip(manifest["layers"], ["对应类型至少1条BD目标T≥7", "全词缀池至少2条T≥7，不要求BD目标", "至少1条BD目标、阶数不限，同时全池至少1条T≥7", "全池至少1条T≥7；前三类先匹配，实际兜底额外单T7"]):
        guide.append(f"| {layer['id']} {layer['name']} | {'／'.join('B'+str(b) for b in layer['base_rules'])}；原{'／'.join('R'+str(r) for r in layer['source_rules'])} | {condition} | {'默认开启，无自动等级退出，玩家手动关闭' if layer['id']=='C4' else '常驻；目标入口需要填写' if layer['requires_bd_type_targets'] else '常驻'} |")
    guide += ["", f"全量词缀池来自冻结version150数据库，共{len(pool)}个ID；覆盖普通、实验及其他特殊类别，不按BD目标裁剪。装备范围保留原23类普通装备（15类武器／副手＋8类护甲／饰品／遗物），不包含神像／祭坛。后续更新词库时重建模板；这里不保证覆盖未来新增ID。", "",
              "C4只有一条，名称为[4 ALL T7 PHASE]，覆盖上述所有装备类型。它放在C3之后；关闭它不会关闭前三类。XML门槛为至少1条T7，并未伪造恰好1条条件；通过先匹配C1、C2、C3，剩下的才是没有BD目标的单T7。", "",
              "C3不加FP或未腐化限制，按用户要求符合收集条件就保留；保留不保证可制作。未腐化物品才可继续锻造，Havoc还要求4条未封印词缀，见[官方符文说明](https://support.lastepoch.com/hc/en-us/articles/46361877750043-Runes-and-Glyphs)。", "",
              "原双崇高R48的T6＋T6／T7＋T6常驻门槛改为双／多T7。原R63／64的T6过渡规则继续保留0–84级；85级退出的是T6层，C4没有这个自动退出。其他资源、暗金、实验、碎片、神像和开荒规则沿用原版。", "",
              "## 玩家待办", "",
              "- 填写C1和C3的BD目标。C1各部位原值与C3的10项原值只是Raxx示例，不是本次两个BD的真实名单；必须用Strict部位目标替换。",
              "- C3按BD／装备类型复制并绑定，使用与C1相同的部位目标池，但目标阶数不限。不要将不同部位的需求直接混池；武器、副手和遗物类型仍需审阅。",
              "- 阶段结束后，玩家手动取消勾选[4 ALL T7 PHASE]这一条；没有指定角色等级，不自动关闭。",
              "- 原R29职业隐藏保持关闭。如后续启用或调整顺序，不能让它抢先隐藏承诺全量保护的T7。",
              "- 继续完成[原模板其他待办](PLAYER_TODO.md)。R81／82／83、神像等仍有未填入口；此文件是基底模板，尚未配置为两个BD的最终成品。",
              "- 其他实验／碎片等规则也可能显示T7；关闭C4只撤掉额外单T7的兜底路径。", "",
              "## 复现", "", "先运行python -X utf8 scripts/build_base_template.py，再运行scripts/verify_base_template.py和scripts/extract_raxx_variables.py。保留原始Raxx和两份Strict字节，旧187条XML不重建。检查结果见[基底验证](../analysis/base-template-validation.json)；XML导入、封印计数和提示效果仍待客户端核对。", ""]
    (ROOT / "docs/BASE_TEMPLATE.md").write_text("\n".join(guide), encoding="utf-8", newline="\n")
    assert (ROOT / source["local_path"]).read_bytes() == raw
    print(json.dumps({"template": TEMPLATE, "rules": len(order), "full_affixes": len(pool), "stage_rule": current[60], "final_bd_filter": False}))


if __name__ == "__main__":
    main()
