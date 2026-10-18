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
    validation = json.loads((ROOT / "analysis/profile-tier-validation.json").read_text(encoding="utf-8"))

    def affixes(values):
        return "、".join(f"{CATALOG['affixes'][str(i)]['zh']} {i}" for i in values) or "—"

    def bases(group, pair=False):
        values = group.get("pair_bases", group["bases"]) if pair else group["bases"]
        return "、".join(f"{CATALOG['bases'][f'{group['type']}:{i}']['zh']} {i}" for i in values) or "不限"

    lines = ["# 追心手里剑：四个角色实际普通槽T6／T7需求", "",
             "2026-10-19按玩家要求重新生成，稳定id仍为`heartseeker-shuriken-marksman`，默认未勾选。暗金、装备、神像和祭坛全部仅取四个角色当前配装，不再合并旧XML。与冰追心及其他BD独立，已有个人保存不会自动覆盖。更新保存可重新应用模版，或导入[同id终局需求](../requirements/heartseeker-shuriken-marksman.endgame.json)。[练级需求](../requirements/heartseeker-shuriken-marksman.leveling.json)保持空。", "",
             "## 来源与边界", "",
             "原[Shuriken Marksman XML](../sources/builds/maxroll-shuriken-marksman-very-strict.xml)137条、原SHA及物理X编号保持为历史证据；`build_xml_documents()`继续保留用于追溯，本次不提供目标。", "",
             "本次重新读取同四个公开profile，共76件，冻结[当前原始API字节](../sources/builds/shuriken-profile-bundle-2026-10-19.json)，按真实词缀槽位及阶数提取。旧[UI摘录](../sources/builds/heartseeker-shuriken-profiles-2026-10-18.json)和两份旧API快照保持。MaadCity的手套、腰带、遗物与旧快照不同。", ""]
    for p in current["source"]["profiles"]:
        lines.append(f"- [{p['character']} · {p['account']}]({p['url']})：{len(p['items'])}件物品。")
    lines += ["", "当前13暗金／10装备组、28项普通槽T6／T7目标／11神像组／1祭坛，无独立05。各部位按四角色来源顺序取并集；不猜优先级，不从终局补练级。旧56项装备目标和15组神像不再作为输入。", "",
              "## 所需暗金", "", "| ID | 名称 | 装备角色 |", "|---|---|---|"]
    for uid in targets["uniques"]:
        owners = "、".join(p["character"] for p in current["source"]["profiles"] if any(i["unique_id"] == uid for i in p["items"]))
        lines.append(f"| {uid} | {CATALOG['uniques'][str(uid)]['zh']} | {owners} |")
    lines += ["", "先驱者之针344仍是角色明确目标；通用针规则也完整保留，前方BD版本负责身份提示。暗金神像不生成普通神像组；暗金固有属性及自身底材不转成素材门槛。459毁灭机巧仅来自旧XML，当前四角色无人装备，故退出本BD目标，通用保护仍独立。", "",
              "## 装备词缀", "", "| 部位 | 实际普通槽T6／T7目标 | 腐化6参考（不参与普通目标） |", "|---|---|---|"]
    for group in targets["equipment"]:
        lines.append(f"| {CATALOG['types'][group['type']]['zh']} | {affixes(group['affixes'])} | {affixes(group.get('corrupted', []))} |")
    lines += ["", "目标同时要求实际普通槽、阶数恰好T6／T7及已知词缀类别。普通ID位于腐化槽时也排除，T5及以下、T8、封印／其他附加槽不进入装备目标。MaadCity新腰带713是普通槽T7实验词缀，因此保留；实验类别不是腐化槽。旧快照手套腐化敏捷503被排除，但S5Luciann普通槽T6敏捷仍可使503进入手套并集，不按ID一刀切。缺少阶数的旧角色JSON报错并要求重新读取，不能猜高阶。", "",
              "## 神像", "", "| 类型 | 一项底材 | 两项底材 | 普通0／5目标 | 附魔4参考 | 腐化6参考 |", "|---|---|---|---|---|---|"]
    for group in targets["idols"]:
        lines.append(f"| {group['type']} | {bases(group)} | {bases(group, True)} | {affixes(group['affixes'])} | {affixes(group.get('enchanted', []))} | {affixes(group.get('corrupted', []))} |")
    lines += ["", "仅取profile实际神像的类型及底材，同范围取并集，不恢复旧XML宽范围。普通神像只计0／5，腐化槽普通ID被排除，附魔4和腐化6不凑两项；神像和祭坛不套装备T6／T7筛选，不限制未来掉落物品的腐化状态。", "",
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
    lines += ["", f"当前独立{validation['standaloneRules']}条。[直接导入XML](../{validation['standaloneXml']})由现行引擎生成，始终合并两阶段。沿用200条上限，超限报错且不截断。[原生验证](../analysis/profile-tier-validation.json)和[WASM对照](../analysis/profile-tier-wasm-validation.json)检查输入、组合、完整输出及冻结文件；76件旧快照的普通／封印／腐化槽ID和阶数逐项与独立LETools API相等。未做游戏客户端实测。", "",
              "```powershell", "python -X utf8 scripts/extract_shuriken_profiles.py", "python -X utf8 scripts/build_shuriken_marksman_requirements.py", "python -X utf8 scripts/validate_profile_import.py", "python -X utf8 scripts/render_shuriken_profile_review.py", "```", ""]
    (ROOT / "docs/SHURIKEN_MARKSMAN_REVIEW.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print("Rendered docs/SHURIKEN_MARKSMAN_REVIEW.md")


if __name__ == "__main__":
    main()
