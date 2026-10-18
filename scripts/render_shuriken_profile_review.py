"""Render the current template targets and additions from frozen inputs."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tool"))
from engine import CATALOG
from build_shuriken_marksman_requirements import build_documents, build_xml_documents


def main():
    current = build_documents()[0]
    old = build_xml_documents()[0]
    targets = current["targets"]
    validation = json.loads((ROOT / "analysis/profile-import-validation.json").read_text(encoding="utf-8"))

    def affixes(values):
        return "、".join(f"{CATALOG['affixes'][str(i)]['zh']} {i}" for i in values) or "—"

    def bases(group, pair=False):
        values = group.get("pair_bases", group["bases"]) if pair else group["bases"]
        return "、".join(f"{CATALOG['bases'][f'{group['type']}:{i}']['zh']} {i}" for i in values) or "不限"

    lines = ["# 追心手里剑：原XML与四个天梯角色的需求并集", "",
             "2026-10-18按玩家要求更新已有模版，稳定id仍为`heartseeker-shuriken-marksman`，默认未勾选。原Very Strict的全部目标保留，追加四个角色的当前配装。与冰追心及其他BD独立，已有个人保存不会自动覆盖。更新保存可重新应用模版，或导入[同id终局需求](../requirements/heartseeker-shuriken-marksman.endgame.json)。[练级需求](../requirements/heartseeker-shuriken-marksman.leveling.json)保持空。", "",
             "## 来源与边界", "",
             "原[Shuriken Marksman XML](../sources/builds/maxroll-shuriken-marksman-very-strict.xml)137条、原SHA及物理X编号保留。原模版从28条已启用专属规则提取11暗金／10装备组／7神像组／1祭坛；未移植源LP、T阶、颜色或隐藏门槛。原始Very Strict目标重建函数`build_xml_documents()`继续保留。", "",
             "新增[四角色UI摘录](../sources/builds/heartseeker-shuriken-profiles-2026-10-18.json)由Profile→View in Build Planner→逐件装备及全部已用词缀页签读取，共76件。它是可见UI证据，不是原生API响应；原始名称、物品／词缀链接和卡片文字可追溯。", ""]
    for p in current["source"]["profiles"]:
        lines.append(f"- [{p['character']} · {p['account']}]({p['url']})：{len(p['items'])}件物品。")
    lines += ["", "仅四角色配装的并集为13暗金／10装备组／11神像组／1祭坛；与原模版合并后为14暗金／10装备组、56项普通部位目标／15神像组／1祭坛，无独立05。原列表顺序在前，新增项追加；不猜优先级，不从终局补练级。", "",
              "## 所需暗金", "", "| ID | 名称 | 本次新增 |", "|---|---|---|"]
    for uid in targets["uniques"]:
        lines.append(f"| {uid} | {CATALOG['uniques'][str(uid)]['zh']} | {'是' if uid not in old['targets']['uniques'] else '原目标'} |")
    lines += ["", "先驱者之针344是角色明确装备的暗金神像，故同时保留为需求ID；生成时沿用共通常驻去重，不生成普通神像组。暗金本体固有属性和自身底材不转成普通素材门槛。", "",
              "## 装备词缀", "", "| 部位 | 普通目标（原顺序＋新追加） | 腐化6参考 |", "|---|---|---|"]
    for group in targets["equipment"]:
        lines.append(f"| {CATALOG['types'][group['type']]['zh']} | {affixes(group['affixes'])} | {affixes(group.get('corrupted', []))} |")
    lines += ["", "按冻结ID类别分类，不按页签：例如MaadCity手套腐化页签的敏捷503仍为普通ID；MAONG护身符腐化页签的持续伤害72也属于普通ID。戒指封印栏的狂怒固定池7只存来源参考，不计普通T7。角色当前装备中偶然出现的低阶词缀也按并集保留，可由玩家在个人方案删减。", "",
              "## 神像", "", "| 类型 | 一项底材 | 两项底材 | 普通0／5目标 | 附魔4参考 | 腐化6参考 |", "|---|---|---|---|---|---|"]
    for group in targets["idols"]:
        lines.append(f"| {group['type']} | {bases(group)} | {bases(group, True)} | {affixes(group['affixes'])} | {affixes(group.get('enchanted', []))} | {affixes(group.get('corrupted', []))} |")
    lines += ["", "相同类型、相同底材范围的候选取并集；不同范围单独保留。原Large／Grand一项10–14、两项4／9／10–14的范围完整保留，没有把新异端9的目标扩展到原全部预兆。普通神像只计0／5，附魔4和腐化6不凑两项；阶数不限，不限制物品的附魔／腐化状态。", "",
              "## 祭坛", ""]
    for group in targets["altars"]:
        lines.append(f"- {bases(group)}：{affixes(group['affixes'])}。")
    lines += ["", "祭坛普通、腐化和附魔作为实际目标，与指定底材共同成立；不移植源总阶数门槛。", "",
              "## 规则数量与验证", "", "| 已选BD | 主BD | 规则数／结果 |", "|---|---|---|"]
    for row in validation["cases"]:
        if "heartseeker-shuriken-marksman" not in row["selected"]:
            continue
        names = {"heartseeker-shuriken-marksman": "追心手里剑", "ice-heartseeker-planner-al0dkyek": "冰追心",
                 "flay-mana-lich": "Strict Flay", "skeleton-necromancer": "Strict Skeleton",
                 "flay-lich-allie-guide": "Allie", "bleed-skeleton-roamer-guide-835": "835"}
        lines.append(f"| {'＋'.join(names[i] for i in row['selected'])} | {names[row['main']]} | {row.get('count', row.get('error'))} |")
    lines += ["", "独立97条；当前配装四角色个人并集单独93条。沿用200条上限，超限报错且不截断。[原生验证](../analysis/profile-import-validation.json)和[WASM对照](../analysis/profile-import-wasm-validation.json)检查输入、组合、完整输出与冻结文件字节；[导入使用说明](PROFILE_IMPORT.md)说明多链接直接读取及验证边界。未做游戏客户端实测。", "",
              "```powershell", "python -X utf8 scripts/extract_shuriken_profiles.py", "python -X utf8 scripts/build_shuriken_marksman_requirements.py", "python -X utf8 scripts/validate_profile_import.py", "python -X utf8 scripts/render_shuriken_profile_review.py", "```", ""]
    (ROOT / "docs/SHURIKEN_MARKSMAN_REVIEW.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print("Rendered docs/SHURIKEN_MARKSMAN_REVIEW.md")


if __name__ == "__main__":
    main()
