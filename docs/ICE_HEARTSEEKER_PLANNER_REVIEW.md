# 冰追心：玩家修订与AL0dkyek来源审阅

当前模板以玩家2026-10-18提供的`LE-filter (10).xml`为准，[冻结原文件](../sources/builds/ice-heartseeker-player-2026-10-18.xml)的SHA-256为`8facbd4310b104d7b3b447565faba68aa5d808cb534de3ad09375559f601eb61`。初次导入时，按当时引擎重新生成的完整79条XML与玩家文件逐字节一致；后续离线重建仍读取这份修订。实验默认关闭、通用暗金／套装拆分等后续共通约定独立生效，当前核对BD目标规则一致，不要求共通规则复刻旧导出。

初版来源为[玩家提供的构建器](https://www.lastepochtools.com/planner/zh/AL0dkyek)，2026-10-17提取。页面显示神射手、100级、赛季5、游戏1.5.2。原始快照保持不变，供历史对照；不从终局配装推断练级路线、替代暗金或拾取最低阶数。

## 2026-10-18玩家修订

| 位置 | 从初版删除 | 新增 |
|---|---|---|
| 头盔 | 虚空抗性7、增加生命25 | — |
| 手套 | 元素抗性80 | 暴击几率5 |
| 腰带 | 提高生命52 | 冰霜抗性17、魔力再生330 |
| 弓 | 击杀时恢复生命20 | — |
| 无懈祭坛9 | 每个折射神像生命1100、每个异端神像每秒能量护盾1096 | — |

只从本BD明确的目标单T7、神像一项目标、祭坛及暗金0LP规则提取目标；共通规则、全词库大池和拆解列表不转成BD需求。所有相关单T7、双T7与非目标T7层都由原引擎重建，初次导入用完整XML相等核对各层目标及提示；后续共通策略更新继续核对BD规则，不移植额外门槛。

XML中的词缀ID已数值排序，无法还原网页手动调整的需求优先级；当前保留仍选中词条的原列表顺序，新词条追加。XML没有记录的腐化、附魔与固定随机池参考沿用旧Planner并标明来源，不能当作本次玩家文件确认。作者视频只读到页面元数据和简介，未取得具体推荐，按玩家要求以本次修改为准；见[视频核验边界](ICE_HEARTSEEKER_VIDEO_REVIEW.md)。

初版记录11件常规装备、1个祭坛与8枚神像；11种不同暗金包括野望宝座211。修订后仍为10组装备、4组神像与1组祭坛，没有独立制作底材。练级保持空白。原始链接和词缀页签记录见[冻结UI选取记录](../sources/builds/letools-planner-al0dkyek-ui.json)，解码与分类见[离线快照](../sources/builds/letools-planner-al0dkyek-extracted.json)。

默认模板名称为“冰追心”，稳定ID为`ice-heartseeker-planner-al0dkyek`，与两份独立攻略模板同等定位，默认未勾选。终局与空白练级需求分别保存，加入个人方案后仍按本BD计分，不与其他BD凑目标。现行引擎试生成：独立79条；Allie＋835＋冰追心组合不论三者谁为主均173条；旧Strict两BD＋冰追心组合不论三者谁为主均130条。全部五份模板按主BD会产生201–216条，超过200即报错，不截断或改策略。

在[在线工作台](https://bcszsz.github.io/LE-filter/)勾选“冰追心”，点击“应用所选BD”即可编辑。当前保存中要追加它，可以导入[终局需求JSON](../requirements/ice-heartseeker-planner-al0dkyek.endgame.json)；[练级JSON](../requirements/ice-heartseeker-planner-al0dkyek.leveling.json)独立留空。同id导入只更新该阶段，原有其他BD与个人方案保持。

## 暗金本体

这些是构建器明确穿戴的本体候选；两枚不息狂怒使用同一个UniqueID，收集池只保留一次。所有暗金本体沿用工作台已有无LP门槛兜底及共通高潜能层，不把此处传奇成品的词缀数量变成LP要求。

| 源槽位 | 本体 | UniqueID |
|---|---|---|
| 头盔 | [雪盲](https://www.lastepochtools.com/db/zh/items/UAzBsIJiA) | 2 |
| 胸甲 | [囚禁之迹](https://www.lastepochtools.com/db/zh/items/UAzBsBYA4HYg) | 487 |
| 手套 | [抵御元素](https://www.lastepochtools.com/db/zh/items/UAzDMBYHYE4g) | 479 |
| 靴子 | [哀霜](https://www.lastepochtools.com/db/zh/items/UAzCMYTiA) | 19 |
| 腰带 | [埃莱克的创新](https://www.lastepochtools.com/db/zh/items/UAzDsBZgJiA) | 402 |
| 主手弓 | [凛冬统御](https://www.lastepochtools.com/db/zh/items/UAzBsEYFYE4g) | 159 |
| 副手箭袋 | [特罗卡之牙](https://www.lastepochtools.com/db/zh/items/UAzDMEYBYDYg) | 146 |
| 护身符 | [真视玻璃](https://www.lastepochtools.com/db/zh/items/UAzAcBYGYE4g) | 439 |
| 戒指1 | [不息狂怒](https://www.lastepochtools.com/db/zh/items/UAwRmBYHZKA) | 477 |
| 戒指2 | [不息狂怒](https://www.lastepochtools.com/db/zh/items/UAwRmBYHZKA) | 477 |
| 遗物 | [破碎世界](https://www.lastepochtools.com/db/zh/items/UAwNgTALAjAzEA) | 413 |
| 暗金神像 | [野望宝座](https://www.lastepochtools.com/db/zh/items/UAzCsCYEZKA) | 211 |

暗金自身的底材名称和subType用于来源核对，未加到素材底材限制或独立05。全部11件常规装备都是暗金本体，因此本快照没有明确普通制作底材。

## 装备后加词缀

下表普通目标池已按玩家XML更新，腐化参考仍来自初版Planner。暗金卡片的固有能力与未带阶数的本体词条没有导入素材目标。普通／实验候选依据冻结词库special类别，不靠物品是否腐化或页签标题猜类别；本构建没有选中实验词缀。表内沿用仍选中词条的原顺序、新项追加，未宣称它等于作者的需求优先级。

| 部位 | 普通目标池 | special=6腐化参考 |
|---|---|---|
| 头盔 | 敏捷（503）、弓箭元素伤害（489）、冰霜抗性（17） | — |
| 胸甲 | 追心箭等级（761）、敏捷（503） | — |
| 手套 | 敏捷（503）、冰霜抗性（17）、暴击几率（5） | 冰霜抗性与虚空抗性（1027） |
| 靴子 | 敏捷（503）、冰霜抗性（17）、闪避时躲避与提高躲避值（760） | — |
| 腰带 | 冰霜伤害（16）、提高躲避值（59）、冰霜抗性（17）、魔力再生（330） | 使用药剂时恢复魔力与使用药剂时获得能量护盾（997） |
| 主手弓 | 暴击率和弓攻击速度（672）、弓箭攻击速度（432） | 提高弓箭攻击速度与弓箭击中时施放冰锥几率（969） |
| 副手箭袋 | 敏捷（503）、弓箭攻击速度（432）、冰霜抗性（17）、元素抗性（80） | 提高弓箭攻击速度与弓箭击中时施放冰锥几率（969） |
| 护身符 | 暴击伤害加成（6）、冰霜抗性（17）、提高躲避值（59） | — |
| 戒指1 | — | 增加暴击加成与每点敏捷提高暴击几率（1075） |
| 戒指2 | 敏捷（503）、冰霜抗性（17）、毒素抗性（19） | — |
| 遗物 | 敏捷（503）、暴击伤害加成（6） | — |

初版戒指1没有普通后加词缀；与戒指2合并后的RING普通池为敏捷503、冰霜抗性17、毒素抗性19，本次XML完整保留。初版弓上的T1击杀回血20已由玩家明确删除，不在重建时补回；原配装显示的T1／T6／T7只描述配装，不成为过滤器最低门槛。

头盔的增加生命25与戒指2的毒素抗性19位于源编辑器的“腐化词缀”页签，但其ID在version152数据库与冻结词库均为special=0。初版均作为普通候选；本次玩家删除25、保留19，原快照的source_tab不变。戒指1的1075在源卡片前缀位置展示，但数据库是special=6，故只作腐化参考，不凑普通目标数。类别、来源页签与玩家选择是独立证据。

## 固定随机池能力

抵御元素与不息狂怒的以下能力属于special=7。即使UI将它们放在封印／原始／腐化页签，也不能据此当普通T7制作素材；默认只留来源参考，本体仍按UniqueID收集，未新增UniqueModifiersCondition的Rolls门槛。类别已用[页面实际加载的version152物品数据库](https://www.lastepochtools.com/data/version152/db/js/8e688d145b13a6e9719c917369f90558.js)与冻结词库交叉核对。

| 源槽位 | 固定随机池参考 |
|---|---|
| 手套 | 每8%溢出上限冰霜抗性使承受持续伤害（至多200%溢出上限冰霜抗性）（1145）、每8%溢出上限冰霜抗性提高冷却恢复速度（至多200%溢出上限冰霜抗性）（1147） |
| 戒指1 | 你拥有血迸之怒（1126） |
| 戒指2 | 你拥有锐利之怒（1117） |

戒指1的1075与1126在所示卡片上有明确文字和阶数，但相应页签未提供selected链接。两条通过独一的完整效果／能力名与词库精确匹配；raw UI记录保留该证据和resolution字段，不将它们冒充直接取得的原始API字段。其余词缀ID均由已选节点的原链接解码。

## 神像与祭坛

同一类型和底材的普通候选在本BD内合并，仍保持一项／两项层；special=4附魔及special=6腐化只参考，不能凑普通两项。这里展示7枚非暗金神像归成的4组；佩戴数量和格子坐标不变成掉落过滤条件。[构建器神像区](https://www.lastepochtools.com/planner/zh/AL0dkyek)

| 类型／底材 | 配装数量 | 普通候选 | 附魔参考 | 腐化参考 |
|---|---|---|---|---|
| 异端精装玛加莎神像（IDOL_2x2:11） | 1 | 共享·暴击伤害加成（743）、弓箭暴击几率（492） | 提高暴击几率与增加暴击伤害加成（892） | 召唤物免疫冰缓（1044） |
| 大型黯影预兆神像（IDOL_1x3:14） | 3 | 共享·暴击伤害加成（743）、弓箭暴击几率（492）、持弓时提高伤害（462）、弓箭伤害（491） | — | 暴击伤害加成（1052）、秒狂怒（使用闪避后）（1112）、狂怒效果至你自身（1029） |
| 中型编织者神像（IDOL_1x1_LAGON:1） | 2 | 你与你的召唤物冰霜抗性穿透（847）、冰霜抗性与召唤物冰霜抗性（850） | — | 召唤物毒素抗性（1064）、击中时施加虚弱几率（1069） |
| 中型拉贡神像（IDOL_1x1_LAGON:0） | 1 | 能量护盾维持（142）、冰霜抗性（112） | — | 降低承受暴击额外伤害（1066） |

大型黯影预兆神像的743与492虽不在普通1×3的canRollOn范围，原页面明确选用了它们，故完整保留743／492／462／491。预兆与普通尺寸词缀范围不能混为一谈；本次没有通过普通尺寸范围删除已观察到的预兆组合。异端／编织者底材沿用源明确类型，不用词库legacy标记推断当前获取路径或改成别的底材。

野望宝座211单独计入暗金池，卡片上的狂怒效果1029保留为该暗金神像的腐化参考；没有给211创造普通神像一项／两项规则。

祭坛为无懈祭坛IDOL_ALTAR:9；玩家XML保留1095预兆神像上限、1089折射栏位前后缀效果、1093折射栏位前缀效果，删除初版的1100每个折射神像生命与1096每个异端神像每秒能量护盾。1093虽在源腐化页签，词库special=0，且是明确祭坛目标，仍进入实际目标池；没有把本体固有的能量护盾衰减阈值当成额外词缀目标。[原所选祭坛底材](https://www.lastepochtools.com/db/zh/items/IIwBgLKIJwrQ)

## 提取方法与验证边界

浏览器成功显示原构建器并逐个打开装备／神像编辑器，只读取DOM中当前物品链接、已用词缀页签的selected链接和显示阶数，没有读取隐藏JavaScript状态。原始API响应未取得，冻结文件明确是选取字段的UI快照。原生“战利品过滤器”导出不包含本次暗金装备的后加普通词缀，因此未拿该XML代替完整目标来源。

链接压缩键按页面[planner.js](https://www.lastepochtools.com/planner/js/planner.js?1791683649)使用的LZ-String URI算法解码：去掉首个类别字母；A类得到十进制词缀ID；U类得到三位subType＋三位UniqueID；I类得到1＋三位itemType＋三位subType＋三位变体。比如UAzBsEYFYE4g→006159，表示凛冬统御159、源暗金底材6；IIwBgLKIJwrQ→1041009000，表示类型41、底材9的祭坛。这里没有将暗金subType当普通素材范围。

新增离线提取器`python -X utf8 scripts/extract_ice_heartseeker_planner.py`只读取冻结UI选取记录与已提交词库。其86个物品／词缀压缩键结果已与页面实际前端codec逐个比对，零差异；45个不同词缀ID的special及前后缀类别、11种暗金的类型与底材均与version152数据库一致。数据库与前端脚本URL、SHA-256和所用条目摘录保存在快照reference。

初版核对了页面所选配装、ID编码、离线目标分类；本次补核了玩家XML的目标恢复与完整输出相等。没有运行游戏客户端、导入游戏过滤器或检验真实掉落。后续仍可继续指摘这份BD需求，不回写两份Flay或骷髅来源。

来源文件：

- [选取字段UI快照](../sources/builds/letools-planner-al0dkyek-ui.json)
- [解码与分类快照](../sources/builds/letools-planner-al0dkyek-extracted.json)
- [离线提取器](../scripts/extract_ice_heartseeker_planner.py)
- [玩家修订XML](../sources/builds/ice-heartseeker-player-2026-10-18.xml)
- [以玩家修订为准的重建脚本](../scripts/build_ice_heartseeker_requirements.py)

## 工作台验证

初次导入时全套70项测试通过，审计检查20组组合、32个明确素材／祭坛目标案例及42份原有输入与引擎字节保持；普通目标相对初版恰好五处变化。需求JSON往返与离线重建相等，独立79条XML与玩家原文件逐字节相等。此历史记录见[目标验证](../analysis/ice-heartseeker-validation.json)。后续共通开关变化的当前检查见[通用规则验证](../analysis/common-protection-validation.json)，BD目标仍与玩家源相同。

初版实际静态网页已核对五份模板、新BD默认未勾选、单独应用、目标显示、空练级、刷新恢复保存与79／173条预览；[2026-10-17浏览器记录](../analysis/ice-heartseeker-browser-validation.json)和[初版截图](images/ice-heartseeker-preview.jpg)仅描述初版。当前玩家修订重新打包Pyodide WASM，在Node环境下对独立及三份新来源组合的三种主BD共4组场景，与本地Python的完整XML、规则元数据及警告逐项相等，见[WASM对照](../analysis/ice-heartseeker-wasm-validation.json)。没有把内置浏览器导出提示当作Blob文件下载实测。

复现新增审计及打包对照：

```powershell
python -X utf8 scripts/build_ice_heartseeker_requirements.py
python -X utf8 scripts/validate_ice_heartseeker.py
python -X utf8 scripts/build_pages.py
node scripts/validate_ice_heartseeker_wasm.mjs
```
