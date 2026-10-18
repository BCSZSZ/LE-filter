# Razorfall为何不在通用0LP规则：来源与实际输出核查

> 2026-10-19更新：玩家已要求取消通用规则的主动去重，当前337会完整保留在通用池。下文的去重复现及161／175／167计数是变更前证据；现行策略与验证见[通用规则固定](../COMMON_RULE_STABILITY.md)。

核查日期：2026-10-18～19，日本时间。本报告核查掉落资料、现有保护名单、实际生成XML及线上运行包，未修改生成器、名单、BD需求或既有冻结资料。机器记录见[生成与线上核查](../../analysis/razorfall-protection-audit.json)。

## 结论

- **剃刀降临Razorfall，ID337，确实是世界随机暗金，reroll为80%。** 实时详情页、实时发布脚本、已冻结Tunklab字段、本机1.5.2.2原生UniqueList及LETools version152缓存一致，不存在这件物品被资料误标为非随机的证据。[Tunklab详情](https://lastepoch.tunklab.com/unique/razorfall)、[Tunklab发布脚本](https://lastepoch.tunklab.com/_next/static/chunks/2k6d3rtcxh7q6.js)
- **当前181种通用暗金基础池已经包含337。** 按当前冻结资料“非隐藏、可随机掉落、reroll>0、非套装、非神像”的口径，共97种暗金装备，97种全部在基础池，缺集为空。这里不能把用户看到的“不显示”解释为“Razorfall的reroll为0”或“名单遗漏337”。[当前冻结名单](../../sources/common-unique-protection.json)、[现行保护说明](../COMMON_UNIQUE_PROTECTION.md)
- **已复现它在“追心手里剑”方案中不列入通用规则的原因：前置BD保护去重。** 模板明确需要337，0LP先命中“BD暗金0LP也留”；因此通用规则省去该ID。将337从该BD目标中移除，它立即回到通用规则，两种情况均为SHOW。其他模板单独启用及默认Strict组合中，337本来就在通用规则。[手里剑明确目标](../../requirements/heartseeker-shuriken-marksman.endgame.json)、[去重实现](../../tool/engine.py)、[生成复现](../../analysis/razorfall-protection-audit.json)
- 同期全量交叉核查没有发现“非随机却有正reroll”的物品，也没有发现这三个数据来源在随机资格、物品类型、套装身份和reroll上的版本冲突。只检查资料与保护基础池，不能据此证明任意roll实例、任意用户旧XML均能显示。

## Razorfall的逐层证据

| 证据 | 版本／读取方式 | ID337的结果 |
|---|---|---|
| [Tunklab详情页](https://lastepoch.tunklab.com/unique/razorfall) | 本次通过浏览工具实时读取 | Boots／Vanguard Boots；世界随机；reroll 80%；标签rare；同类型单件Unique Boots预言1.37% |
| [Tunklab发布脚本](https://lastepoch.tunklab.com/_next/static/chunks/2k6d3rtcxh7q6.js) | 本次HTTP200读取字面文本，未执行远程JavaScript；uniques数据声明1.5.2 | `uniqueId:337`、`isSetItem:!1`、`canDropRandomly:!0`、`rerollChance:.8`、`baseType:3` |
| [冻结Tunklab对照资料](../../sources/tunklab-unique-reroll-2026-10-18.json) | 与上列发布脚本SHA-256一致 | `can_drop_randomly=true`、`reroll_chance=0.8`、`type=BOOTS`、`set=false` |
| [原生UniqueList冻结字段](../../sources/unique-drop-inputs-2026-10-18.json) | 游戏1.5.2.2，resources.assets的PathID11278 | `canDropRandomly=1`、`rerollChance=0.800000011920929`、`hideFromPlayers=0`、`isSetItem=0`、`baseType=3`、`subTypes=[10]` |
| [LETools version152发布数据库](https://www.lastepochtools.com/data/version152/db/js/8e688d145b13a6e9719c917369f90558.js) | 使用既有缓存并校验原JS及解码JSON哈希；未声称本次线上抓取成功 | `canDropRandomly=1`、`rerollChance=0.8`、`hideFromPlayers=0`、`isSetItem=0`、`baseTypeId=3`、`subTypeIds=[10]`，该站`rarityTier=T1` |

Tunklab脚本本次响应7,963,341字节，SHA-256为`05cb81a6a3b098ac872164740071ec4ee3deceab6251b30555536d052ee45391`，与现有冻结证据完全相同。LETools缓存原JS的SHA-256为`8a0293233b168b1eb425d7a9490bf7ad26f0d33f445fe2f5a3f0704432ee4cc5`，解码JSON为`b9f44fb8f44b8b1d455539c3bb11c47a53fc39e9933dadd53280f5669d4fe37e`，均与[冻结来源记录](../../sources/unique-drop-inputs-2026-10-18.json)一致。

`rare`和`T1`是各数据库的描述或分类，不代表项目已确认的六件T0。reroll表示随机抽中候选后触发重抽的参数，**80%不是实际掉率，也不能直接写成20%掉率**；实际身份分布还取决于同类型有效候选池、等级／职业约束和60次重抽上限。计算口径及原生证据见[暗金选择器资料](UNIQUE_PICKER_DROP_DATA.md)与[原生代码摘录](../../sources/unique-drop-native-evidence-2026-10-18.json)。

## 全量交叉核查与“其他遗漏”的范围

本次将Tunklab原始发布数据487个ID、LETools缓存489个ID和原生UniqueList489个ID按ID连接，比较`canDropRandomly`、`isSetItem`、装备类型／底材范围及`rerollChance`。原生reroll为float，数值比较允许`1e-7`绝对误差；其余字段逐值比较。[Tunklab原始来源](https://lastepoch.tunklab.com/_next/static/chunks/2k6d3rtcxh7q6.js)、[LETools原始来源](https://www.lastepochtools.com/data/version152/db/js/8e688d145b13a6e9719c917369f90558.js)、[原生字段快照](../../sources/unique-drop-inputs-2026-10-18.json)

| 对比／检查 | 结果 |
|---|---|
| Tunklab与原生共有487个ID的上述字段 | 零冲突 |
| LETools与原生489个ID的上述字段 | 零冲突 |
| Tunklab未公开但原生存在的2个ID | 46鲨齿锯、69光明传家宝；均隐藏、不可随机、reroll=0 |
| 非随机且reroll>0 | Tunklab、LETools及原生三者均为0件 |
| 非隐藏且随机正reroll的全部物品 | 123件＝97种非套装暗金装备＋23件套装＋3种暗金神像 |
| 97种暗金装备减去当前181种暗金基础池 | 空集，没有另一件同口径的ID遗漏 |
| 23件正reroll套装减去当前全部61件套装池 | 空集；套装本来单独全收，不按reroll筛选 |

3种正reroll暗金神像为[奇点246](https://lastepoch.tunklab.com/unique/singularity)、[自然之怒462](https://lastepoch.tunklab.com/unique/natural_wrath)、[焦土485](https://lastepoch.tunklab.com/unique/scorched_earth)。它们不计入97种普通暗金装备，由独立可选暗金神像规则管理；不能仅因不在通用装备规则就认定漏保。[共通神像规则说明](../TOOL_GUIDE.md)

上述“无遗漏”只指本次明确口径的基础ID池，并不等于181种条目在生成时都逐项清除了历史Rolls限制，也不等于每件物品都必须出现在名为“通用暗金0LP保护”的那一条规则。现行策略会把已由更前面的T0或BD目标覆盖的ID从低档通用池省去，实际显示由首次命中规则决定；具体输出问题应检查前置覆盖、规则开关、原有Rolls对象及导出版本。[现行生成约定](../COMMON_UNIQUE_PROTECTION.md)

## 实际生成复现：先命中BD保护，所以通用规则省去

生成器先从全部启用BD的终局目标取并集（套装扩展、T0另列），生成主／副BD的0LP保护；构建通用规则时再扣除这些已覆盖ID。决定去重的是当前方案中实际启用的BD目标，和左侧尚未应用的模板草稿不同。[目标与归属](../../tool/engine.py)、[手里剑需求中的337](../../requirements/heartseeker-shuriken-marksman.endgame.json)

用真实`engine.generate`输出XML，核对按Order升序的规则，并用现有有限匹配器查337的首次命中。以下保持共通暗金开关开启，仅改变模板或337是否为目标：[完整机器记录](../../analysis/razorfall-protection-audit.json)

| 场景 | 通用暗金规则ID数 | 337在该规则内 | 337的0LP首次命中 |
|---|---:|---|---|
| 一个启用BD、全部目标为空 | 175 | 是 | 通用暗金0LP保护，SHOW |
| 默认Strict两BD组合 | 161 | 是 | 通用暗金0LP保护，SHOW |
| 追心手里剑单独启用 | 167 | 否 | 主BD暗金0LP也留，第62条，SHOW |
| 同一手里剑方案，只移除337目标 | 168 | 是 | 通用暗金0LP保护，SHOW |

第62条只指本次手里剑单模板的98条输出，其他组合的编号会改变。0LP的BD保护不增加LP、WW、等级或属性roll门槛；单模板337的1LP命中灵感BD目标规则、2LP命中彗星BD目标规则、3LP命中通用彗星规则，均为SHOW。未作为BD目标时，通用规则保留的337旧Rolls为0～4号，每项MinRoll=0／MaxRoll=255，未收窄属性数值区间。[XML结构与有限首命中结果](../../analysis/razorfall-protection-audit.json)

### 同样从通用规则去重的装备

在“追心手里剑”单模板中，以下8件既属于181种基础暗金池，也属于启用BD明确目标，因此由同一条前置BD保护承接。剃刀降临之外还有7件；这张表描述的是规则归属变化，没有发现掉落保护缺口。[逐ID归属记录](../../analysis/razorfall-protection-audit.json)

| ID | 名称 | 0LP保护位置 |
|---:|---|---|
| 92 | 丛林女王的储物腰带 · Jungle Queen's Chaps of Holding | BD暗金0LP也留 |
| 133 | 西塔拉的谜团 · Xithara's Conundrum | BD暗金0LP也留 |
| 256 | 山之巅 · Peak of the Mountain | BD暗金0LP也留 |
| 337 | 剃刀降临 · Razorfall | BD暗金0LP也留 |
| 413 | 破碎世界 · Shattered Worlds | BD暗金0LP也留 |
| 436 | 纷争之翼 · Wings of Discord | BD暗金0LP也留 |
| 459 | 毁灭机巧 · Artifice of Devastation | BD暗金0LP也留 |
| 477 | 不息狂怒 · Unsated Rage | BD暗金0LP也留 |

另外61／208／277／473／476／478六件T0始终由独立最高彗星规则承接，也不会重复列入通用低档池。手里剑通用暗金规则因此为`181－8－6＝167`。当前方案如增加其他BD或个人目标，去重名单会随之变化。[六件T0冻结来源](../../sources/ultra-rare-uniques.json)、[生成记录](../../analysis/razorfall-protection-audit.json)

### 全量覆盖与线上版本

- 9组场景：空目标、默认Strict组合、六份模板分别单独启用、手里剑移除337目标。每组97种正reroll非套装暗金均被覆盖；181种通用暗金＋61件套装共242个ID也全部有启用的SHOW规则，且位于所有HIDE规则之前。结构核对要求该SHOW仅含UniqueModifiersCondition，数值边界为完整0～255或原有空值；没有将有限匹配器忽略Rolls的行为当作完整客户端证明。[逐场景结果](../../analysis/razorfall-protection-audit.json)
- 本次另运行`python -X utf8 -m unittest discover -s tool -p test_common_protection.py -v`，7项共通保护测试通过。[测试记录](../../analysis/razorfall-protection-audit.json)
- 实际读取[在线工作台](https://bcszsz.github.io/LE-filter/)及其[版本1fb0405870f8d772运行包](https://bcszsz.github.io/LE-filter/runtime.zip?v=1fb0405870f8d772)，HTTP200。线上引擎、bootstrap、词库、保护名单与全部需求文件共12份逐字节匹配本地，线上基础池也含337。线上部署版本不支持“当前运行包没有337”的猜测；用户已打开的旧标签页是否持有旧运行时，未访问核实。[文件哈希及响应记录](../../analysis/razorfall-protection-audit.json)

## 证据边界

本报告包括公开页面、发布数据库、已校验缓存、冻结原生字段、实际生成XML与线上文件核查，没有访问用户当前浏览器的个人保存方案，也没有取得用户所指的实际XML或物品roll实例，没有执行游戏客户端掉落、物品显示或音效实测。“追心手里剑的前置BD去重”已在当前模板中复现；不能在缺少用户实际配置时断言用户的个人方案必然与模板相同。详情页实时读取成功；发布脚本及线上运行包通过HTTP直接读取成功；LETools只使用已验证缓存。没有根据reroll或稀有度标签推造实际自然掉率，也没有据此新增或删除任何保护条目。
