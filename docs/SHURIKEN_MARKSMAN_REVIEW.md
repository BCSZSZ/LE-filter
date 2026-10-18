# 追心手里剑：四个角色实际普通槽T6／T7需求

2026-10-19按玩家要求重新生成，稳定id仍为`heartseeker-shuriken-marksman`，默认未勾选。暗金、装备、神像和祭坛全部仅取四个角色当前配装，不再合并旧XML。与冰追心及其他BD独立，已有个人保存不会自动覆盖。更新保存可重新应用模版，或导入[同id终局需求](../requirements/heartseeker-shuriken-marksman.endgame.json)。[练级需求](../requirements/heartseeker-shuriken-marksman.leveling.json)保持空。

## 来源与边界

原[Shuriken Marksman XML](../sources/builds/maxroll-shuriken-marksman-very-strict.xml)137条、原SHA及物理X编号保持为历史证据；`build_xml_documents()`继续保留用于追溯，本次不提供目标。

本次重新读取同四个公开profile，共76件，冻结[当前原始API字节](../sources/builds/shuriken-profile-bundle-2026-10-19.json)，按真实词缀槽位及阶数提取。旧[UI摘录](../sources/builds/heartseeker-shuriken-profiles-2026-10-18.json)和两份旧API快照保持。MaadCity的手套、腰带、遗物与旧快照不同。

- [MAONG · vsnail](https://www.lastepochtools.com/profile/vsnail/character/MAONG)：19件物品。
- [ShurikenAmhali · Amhali](https://www.lastepochtools.com/profile/Amhali/character/ShurikenAmhali)：19件物品。
- [S5Luciann · chachapieng](https://www.lastepochtools.com/profile/chachapieng/character/S5Luciann)：19件物品。
- [MaadCity · 47x47](https://www.lastepochtools.com/profile/47x47/character/MaadCity)：19件物品。

当前13暗金／10装备组、28项普通槽T6／T7目标／11神像组／1祭坛，无独立05。各部位按四角色来源顺序取并集；不猜优先级，不从终局补练级。旧56项装备目标和15组神像不再作为输入。

## 所需暗金

| ID | 名称 | 装备角色 |
|---|---|---|
| 256 | 山之巅 | MAONG、ShurikenAmhali、S5Luciann、MaadCity |
| 436 | 纷争之翼 | MAONG、ShurikenAmhali、S5Luciann、MaadCity |
| 271 | 聚集怒火 | MAONG、ShurikenAmhali、S5Luciann、MaadCity |
| 189 | 猩红秘藏 | MAONG、ShurikenAmhali、S5Luciann、MaadCity |
| 134 | 利拉卡的利爪 | MAONG、ShurikenAmhali、S5Luciann、MaadCity |
| 17 | 护体印痕 | MAONG |
| 337 | 剃刀降临 | MAONG、ShurikenAmhali、S5Luciann、MaadCity |
| 477 | 不息狂怒 | MAONG、ShurikenAmhali、S5Luciann、MaadCity |
| 133 | 西塔拉的谜团 | MAONG、ShurikenAmhali、S5Luciann、MaadCity |
| 413 | 破碎世界 | MAONG、ShurikenAmhali、S5Luciann、MaadCity |
| 92 | 丛林女王的储物腰带 | ShurikenAmhali、S5Luciann |
| 402 | 埃莱克的创新 | MaadCity |
| 344 | 先驱者之针 | MaadCity |

先驱者之针344仍是角色明确目标；通用针规则也完整保留，前方BD版本负责身份提示。暗金神像不生成普通神像组；暗金固有属性及自身底材不转成素材门槛。459毁灭机巧仅来自旧XML，当前四角色无人装备，故退出本BD目标，通用保护仍独立。

## 装备词缀

| 部位 | 实际普通槽T6／T7目标 | 腐化6参考（不参与普通目标） |
|---|---|---|
| 头盔 | 手里剑等级 611、提高生命 52、投掷物理伤害 471、追心箭反曲几率 762 | 增加敏捷与提高躲避值 1017 |
| 胸甲 | 提高生命 52、敏捷 503、投掷物理伤害 471 | 免疫晕眩与提高闪避冷却时间 1012、耐伤阈值与耐伤阈值增加至能量护盾衰减阈值 1008、全技能等级与增加魔力 1014 |
| 弓 | 弓箭攻击速度 432、暴击伤害加成 6 | 增加暴击几率与弓箭暴击时施放手里剑几率 966 |
| 箭袋 | 弓箭攻击速度 432 | 增加暴击几率与弓箭暴击时施放手里剑几率 966 |
| 手套 | 投掷伤害 88、复合生命 36、敏捷 503、几率粉碎护甲于击中时 86 | 提高施法速度与直接施放法术时获得能量护盾 1005、提高攻击与施法速度 1004 |
| 腰带 | 投掷伤害 88、提高躲避值 59、暴击避免与增加躲避值 97、使用药水时实验性穿越冷却恢复 713 | 元素抗性与腐化抗性 1024、增加投掷伤害与投掷护甲粉碎几率 995 |
| 靴子 | 移动速度 28、敏捷 503 | 闪避净化异常状态几率与提高承受的异常状态伤害 991、元素抗性与腐化抗性 1024 |
| 戒指 | 投掷伤害与降低魔力消耗 507 | 提高持续伤害与持续伤害转化为生命偷取 1074、物理抗性与虚空抗性 1023、增加智力与每秒获得能量护盾 1016 |
| 护身符 | 投掷伤害 88、物理抗性穿透 33、增加躲避值 8、元素抗性 80、提高躲避值 59 | — |
| 遗物 | 投掷伤害 88、暴击伤害加成 6 | 增加力量与增加护甲 1018 |

目标同时要求实际普通槽、阶数恰好T6／T7及已知词缀类别。普通ID位于腐化槽时也排除，T5及以下、T8、封印／其他附加槽不进入装备目标。MaadCity新腰带713是普通槽T7实验词缀，因此保留；实验类别不是腐化槽。旧快照手套腐化敏捷503被排除，但S5Luciann普通槽T6敏捷仍可使503进入手套并集，不按ID一刀切。缺少阶数的旧角色JSON报错并要求重新读取，不能猜高阶。

## 神像

| 类型 | 一项底材 | 两项底材 | 普通0／5目标 | 附魔4参考 | 腐化6参考 |
|---|---|---|---|---|---|
| IDOL_2x1 | 谦卑编织者神像 1 | 谦卑编织者神像 1 | 增加投掷伤害与提高投掷伤害 873、活力与增加生命再生 862、虚空抗性与召唤物虚空抗性 868、腐化抗性与召唤物腐化抗性 867、击杀时恢复生命与增加生命 860、腐化抗性 114 | — | 你与你的召唤物所有抗性 1070、躲避值（闪避期间） 1059 |
| IDOL_1x4 | 异端巨型暗影神像 9 | 异端巨型暗影神像 9 | 投掷物理伤害 470、游侠反曲几率与弓箭伤害 763、持弓时提高伤害 462 | 提高暴击几率与增加暴击伤害加成 892、持弓时提高伤害与重复施放弓箭攻击几率 935、伤害偏斜几率与提高躲避值 933、提高移动速度与提高伤害 894 | 弓箭伤害 1037 |
| IDOL_2x2 | 异端精装玛加莎神像 11 | 异端精装玛加莎神像 11 | 投掷伤害 490、共享·暴击伤害加成 743 | 提高暴击几率与增加暴击伤害加成 892、提高投掷伤害与双持时提高伤害 934、急速效果与闪避时急速持续时间 936 | 免疫迟缓 1043 |
| IDOL_3x1 | 宏伟黯影预兆神像 14 | 宏伟黯影预兆神像 14 | 投掷伤害 490、共享·暴击伤害加成 743、弓箭暴击几率 492 | — | 免疫冰缓 1031、狂怒效果至你自身 1029 |
| IDOL_1x1_ETERRA | 小型伊泰拉神像 0 | 小型伊泰拉神像 0 | 躲避值 118、腐化抗性 114、共享·物理伤害 319 | — | 击中时施加虚弱几率 1069 |
| IDOL_1x3 | 异端大型暗影神像 9 | 异端大型暗影神像 9 | 元素抗性 117、躲避值与提高生命 942、弓箭伤害 491 | 提高暴击几率与增加暴击伤害加成 892、能量护盾衰减阈值与每秒获得能量护盾 897 | 提高闪避冷却恢复速度 1050 |
| IDOL_1x2 | 厚实编织者神像 1 | 厚实编织者神像 1 | 提高暴击几率与暴击伤害加成 878、冰霜抗性与召唤物冰霜抗性 885、击杀时恢复生命与提高生命 880、元素抗性与召唤物元素抗性 886 | — | 你与你的召唤物所有抗性 1070、躲避值（闪避期间） 1059 |
| IDOL_2x2 | 精装玛加莎神像 4 | 精装玛加莎神像 4 | 共享·暴击伤害加成 743、投掷伤害 490 | — | 免疫迟缓 1043 |
| IDOL_1x3 | 大型黯影预兆神像 14 | 大型黯影预兆神像 14 | 毒素抗性 116、游侠反曲几率与弓箭伤害 763 | — | 免疫迟缓 1043 |
| IDOL_1x2 | 厚实拉贡神像 0 | 厚实拉贡神像 0 | 元素抗性 117、药剂恢复生命转化为能量护盾 123 | — | 躲避值（闪避期间） 1059 |
| IDOL_3x1 | 异端宏伟玛加莎神像 9 | 异端宏伟玛加莎神像 9 | 击中时施加中毒几率 140、投掷伤害 490 | 中毒持续时间与弓箭击中时投掷酸液瓶几率（3秒冷却时间） 937、猩红帷幕持续时间与每层猩红帷幕使流血几率 931 | — |

仅取profile实际神像的类型及底材，同范围取并集，不恢复旧XML宽范围。普通神像只计0／5，腐化槽普通ID被排除，附魔4和腐化6不凑两项；神像和祭坛不套装备T6／T7筛选，不限制未来掉落物品的腐化状态。

## 祭坛

- 金字塔祭坛 11：提高生命自装备的每个巨型神像 1099、生命自每个折射栏位的神像 1100、折射栏位神像前缀效果 1093、折射栏位神像后缀效果 1094、降低承受暴击额外伤害自装备的每个异端神像 1097、生命自装备的每个预兆神像 1088、折射栏位神像前缀与后缀效果 1089、能量护盾衰减阈值自每个折射栏位的神像 1103、腐化神像上限 1108。

祭坛普通、腐化和附魔作为实际目标，与指定底材共同成立；不移植源总阶数门槛。

## 规则数量与验证

| 已选BD | 主BD | 规则数／结果 |
|---|---|---|
| 追心手里剑 | 追心手里剑 | 96 |
| 追心手里剑＋Strict Skeleton | 追心手里剑 | 123 |
| 追心手里剑＋Strict Skeleton | Strict Skeleton | 123 |
| Strict Flay＋追心手里剑 | Strict Flay | 120 |
| Strict Flay＋追心手里剑 | 追心手里剑 | 120 |
| Allie＋追心手里剑 | Allie | 137 |
| Allie＋追心手里剑 | 追心手里剑 | 137 |
| 835＋追心手里剑 | 835 | 150 |
| 835＋追心手里剑 | 追心手里剑 | 150 |
| 追心手里剑＋冰追心 | 追心手里剑 | 127 |
| 追心手里剑＋冰追心 | 冰追心 | 125 |
| Strict Flay＋追心手里剑＋Strict Skeleton | Strict Flay | 147 |
| Strict Flay＋追心手里剑＋Strict Skeleton | 追心手里剑 | 147 |
| Strict Flay＋追心手里剑＋Strict Skeleton | Strict Skeleton | 147 |
| 835＋Allie＋追心手里剑 | 835 | 190 |
| 835＋Allie＋追心手里剑 | Allie | 190 |
| 835＋Allie＋追心手里剑 | 追心手里剑 | 190 |
| 835＋Allie＋追心手里剑＋冰追心 | 835 | 这些BD生成219条规则，超过200条。请减少选中的BD或目标分组；没有截断规则。 |
| 835＋Allie＋追心手里剑＋冰追心 | Allie | 这些BD生成219条规则，超过200条。请减少选中的BD或目标分组；没有截断规则。 |
| 835＋Allie＋追心手里剑＋冰追心 | 追心手里剑 | 这些BD生成221条规则，超过200条。请减少选中的BD或目标分组；没有截断规则。 |
| 835＋Allie＋追心手里剑＋冰追心 | 冰追心 | 这些BD生成219条规则，超过200条。请减少选中的BD或目标分组；没有截断规则。 |
| 835＋Allie＋Strict Flay＋追心手里剑＋冰追心＋Strict Skeleton | 835 | 这些BD生成256条规则，超过200条。请减少选中的BD或目标分组；没有截断规则。 |
| 835＋Allie＋Strict Flay＋追心手里剑＋冰追心＋Strict Skeleton | Allie | 这些BD生成247条规则，超过200条。请减少选中的BD或目标分组；没有截断规则。 |
| 835＋Allie＋Strict Flay＋追心手里剑＋冰追心＋Strict Skeleton | Strict Flay | 这些BD生成262条规则，超过200条。请减少选中的BD或目标分组；没有截断规则。 |
| 835＋Allie＋Strict Flay＋追心手里剑＋冰追心＋Strict Skeleton | 追心手里剑 | 这些BD生成264条规则，超过200条。请减少选中的BD或目标分组；没有截断规则。 |
| 835＋Allie＋Strict Flay＋追心手里剑＋冰追心＋Strict Skeleton | 冰追心 | 这些BD生成262条规则，超过200条。请减少选中的BD或目标分组；没有截断规则。 |
| 835＋Allie＋Strict Flay＋追心手里剑＋冰追心＋Strict Skeleton | Strict Skeleton | 这些BD生成262条规则，超过200条。请减少选中的BD或目标分组；没有截断规则。 |

当前独立96条。[直接导入XML](../outputs/profile-t6-t7-2026-10-19/追心手里剑.xml)由现行引擎生成，始终合并两阶段。沿用200条上限，超限报错且不截断。[原生验证](../analysis/profile-tier-validation.json)和[WASM对照](../analysis/profile-tier-wasm-validation.json)检查输入、组合、完整输出及冻结文件；76件旧快照的普通／封印／腐化槽ID和阶数逐项与独立LETools API相等。未做游戏客户端实测。

```powershell
python -X utf8 scripts/extract_shuriken_profiles.py
python -X utf8 scripts/build_shuriken_marksman_requirements.py
python -X utf8 scripts/validate_profile_import.py
python -X utf8 scripts/render_shuriken_profile_review.py
```
