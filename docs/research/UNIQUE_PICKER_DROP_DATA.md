# 暗金选择器的掉落来源与概率

核查日期：2026-10-18。本次只增加独立的选择器数据，不修改原词库、BD目标、过滤器生成条件或概率工具。界面数据为[unique-drop-catalog.json](../../sources/unique-drop-catalog.json)，可用 `python -X utf8 scripts/build_unique_drop_catalog.py` 从[冻结输入](../../sources/unique-drop-inputs-2026-10-18.json)离线重建。

489个原词库ID全部保留：世界随机330、限定Boss／先古来源123、其他特殊来源32、旧／隐藏4。世界随机中包括276件非套装暗金和54件套装；7件随机暗金神像另有奖励类型。来源并非互斥：贪婪虚空208既能世界随机，也有加斯帕和特定编织回响来源，各用自己的概率口径。

## 一手依据

- 游戏版本1.5.2.2的 `GameAssembly.dll`，SHA-256 `d5f9fb458f0e9878e697a92b590a586a52fd77e645f8bf87bb4f2b74c6c56567`。算法取自实际原生代码；Cpp2IL只用于定位字段、方法名、RVA和长度。[关键原生指令摘录](../../sources/unique-drop-native-evidence-2026-10-18.json)已冻结。
- `resources.assets` 中原生UniqueList，PathID11278；原文件SHA-256 `6694168ed890fdfa7e48a857758a435d548df008788a4c24f5830230278f9684`，对象原始字节SHA-256 `9e0b906fbd0be82beaa1f0070c64c55f30a88d82ba48ebbc8c8bd0bfa14d8516`。冻结每个ID的随机资格、隐藏状态、reroll、物品类型、底材、等级与职业要求。
- 原生MasterItemsList来自PermaLoad.bundle，PathID331809119198608226，bundle SHA-256 `7fac4caacd757f5f821f0e5c15f6eccf573aa8ebf89d3f464d124dc2e72ac93c`。用于职业与底材等级判定。
- [Tunklab发布数据库](https://lastepoch.tunklab.com/_next/static/chunks/2k6d3rtcxh7q6.js)是该站公开来源、图片和掉落表的原始数据，SHA-256 `05cb81a6a3b098ac872164740071ec4ee3deceab6251b30555536d052ee45391`。只解析字面数据，没有执行远程JavaScript。保留41个带具体暗金的命名Boss表和6个带具体暗金的编织回响表。
- [LETools version152发布数据库](https://www.lastepochtools.com/data/version152/db/js/8e688d145b13a6e9719c917369f90558.js)使用已有缓存，原JS SHA-256 `8a0293233b168b1eb425d7a9490bf7ad26f0d33f445fe2f5a3f0704432ee4cc5`，解码JSON SHA-256 `b9f44fb8f44b8b1d455539c3bb11c47a53fc39e9933dadd53280f5669d4fe37e`。当前直接访问受403限制，不能表述成新抓取成功。173条暗金定向记录完整保留为补充证据；已有当前命名Boss表的ID不再叠加旧库可能使用的别名。

## 当前静态展示口径

2026-10-19按玩家要求，选择器只保留搜索与物品勾选；按部位分组，每件显示一个主要来源与一个参考值。移除职业／部位筛选、只看已选／旧项开关和多来源展开。已选旧ID继续展示，原保存与过滤规则保持。

`items[id].display`是当前界面唯一读取的展示记录。世界暗金固定用100级、命运12、无镜片、同类型通用池的单件概率，即下述`P(i | pool_all)`；人为忽略职业偏置，用作统一比较的参考，不声称它等于每个职业的实际概率。神像仍按原生两步类型抽取。套装标注“需套装预言”。

Boss／特殊数值取一个主要来源，在该来源中优先最高副本tier，再取开启者奖励及表内上限。每次独立奖励，不合并额外次数；上限不是承诺任意腐化都能达到的最终掉率。破碎王冠保留“符合配方时100%”，先古、茧化等没有固定值的机制保留简短文字。下方完整职业值、各来源、条件和原生证据继续用于研究与复现，不作为界面上的可切换场景。

## 世界掉落的原生预言机制

采用100级区域、命运12、没有镜片的**一件同类型普通暗金预言奖励**。这是奖励物品已确定为暗金之后，抽中指定ID的条件概率，不是击杀怪物掉落该暗金的总概率，也不是完成一整条预言至少出一件的概率。命运12使预言产出更多物品，不改变这里每件的物品身份分布。普通Unique奖励只取非套装；SET不混入Unique分母。

原生链路如下，关键分支和字段均见[原生证据](../../sources/unique-drop-native-evidence-2026-10-18.json)：

| 方法 | RVA | 相关行为 |
|---|---|---|
| ProphecySlotReward.SpawnRewardForPlayer | `0x20B3800` | 固定100级，读取奖励物品类型；对职业兼容作预选检查，再调用实际生成 |
| ItemCreationProperties.GetChosenRarityAndForceExalt | `0x12199A0` | Unique组返回稀有度7，Set组返回8 |
| GenerateItems.rollRandomlyRequiresClassCompatibility | `0x11D18E0` | 区域等级≥50时以原生float `0.800000011920929` 要求职业兼容 |
| GenerateItems.RollBaseItem | `0x11C7060` | Unique使用MustBeNonSetItem；按类型、随机资格、等级及选中的职业约束调用rollUnique |
| UniqueList.rollUnique | `0x1270F10` | 构建候选池，均匀抽ID，按该ID的reroll决定重抽；最多60次重抽 |
| Entry.hasClassCompatibleSubType | `0x125AC00` | 至少一个底材职业匹配即可；这里不要求专精职业 |

令一个有效池有 `N` 个ID，ID `i` 的原始reroll为 `r_i`，平均拒绝率 `q = Σr_i/N`。实际代码在连续60次拒绝后接受最后一次新抽出的候选，因此：

```text
P(i | pool) = (1-r_i)/N × Σ(q^k, k=0…59) + q^60/N
```

最后一项保留了原生次数上限；不能直接把 `1-r_i` 或reroll百分比当成掉率。一般池的尾项很小，但构建脚本没有省略。`reroll_distribution` 为独立纯函数，包括只有一个ID、全拒绝和零次重抽等边界。

对每个职业 `c`，另构建该职业可装备的同类型池 `pool_c`，计算：

```text
P(i | c) = (1-0.800000011920929) × P(i | pool_all)
         + 0.800000011920929 × P(i | pool_c)
```

如果职业池为空，原生预检查失败后使用不强制职业兼容的生成，不能把对应80%写成装备丢失。头盔、胸甲、遗物等因此可能随职业改变；数据保留五职业 `prophecyByClass`，只有五职业相同时才同时给单值 `prophecyProbability`。这些字段供原生研究核对，当前界面统一读取`display`的通用池参考值。所有同类型池ID在结果 `prophecyPools` 中明确保存。

例：红戒277为约0.165700%，界面显示0.17%；奥利安之眼61为约0.234521%，显示0.23%，与本次读取的[Tunklab红戒](https://lastepoch.tunklab.com/unique/red_ring_of_atlaria)、[奥利安之眼](https://lastepoch.tunklab.com/unique/orians_eye)普通Unique预言数值相符。唤骨盔6的原生职业值约12.26%–15.88%，当前界面按约定只显示通用池参考。

## 暗金神像与套装

暗金神像预言不是每种尺寸一个独立奖励。其 `genericItem.itemTypeType=Group`、`itemTypeGroup=Idols`、`rarity=7`。`GetItemType` 的组3分支 `0x1219F80` 先构建“每个随机暗金神像贡献一次baseType”的缓存列表，再均匀选类型；列表中重复类型没有去重，然后才在该类型内部rollUnique。谓词 `0x1230B40` 检查类型25–33及canDropRandomly，选择器 `0x1230BC0` 返回baseType。神像Unique分支不执行上述80%职业偏置。

当前列表对应ID `246、324、325、326、421、462、485`，baseType为 `[25,30,33,32,33,30,29]`。因此类型30和33各占2/7，其余出现的类型各1/7；再乘该类型内部的有限重抽分布。例如奇点246为1/7，约14.285714%；Unvar's Rise324为 `(2/7)×(1/1.8)`，约15.873016%。Tunklab当前[奇点页](https://lastepoch.tunklab.com/unique/singularity)采用所有神像权重一次归一化，显示11.29%；本工具采用本机原生的两步抽取，而非这个近似。

54件世界随机套装在普通Unique预言中的概率为0，明确标注需要套装预言。套装预言有不同的武器／防具／饰品奖励池，加上命运整套掉落机制，不能将它们加入同类型非套装暗金池。7件限定套装来源保留其Boss或特殊奖励条件。本次不提供未经完整建模的套装预言概率。

## 命名Boss与特殊来源

每条命名来源采用**每次独立奖励**的基础掉率及数据库的物品稀有度范围，**不含命运10级的Boss专属奖励加成**，也不冒充一个固定腐化下的最终掉率。用户明确不计算额外奖励次数，因此不把一场战斗、多个独立奖励组或一条回响内的多次奖励合成为“至少一件”。副本T1–T4、强化限定、最低腐化、开启者限制在各来源的 `conditions` 和原始 `rates` 中保留。范围上限是表的最大值，不表示某个有限腐化必然达到。

加权BossLoot组的基础尝试次数为 `a`，该物品权重占比为 `p=w/Σw`。`BossLoot.RollLoot`（`0x11B5B00`）先用StochasticRound处理尝试次数，然后反复从同一drops表加权抽取并追加结果；每次只减少次数，没有从池中移除已抽对象。有效性谓词 `0x11D39D0` 只检查CanDrop，追加函数 `0x11D3B20` 只写输出。按本次单次奖励口径，当 `a<1` 时保留这次奖励是否产生的概率；当 `a≥1` 时只取其中一次，不累计额外抽取：

```text
P(指定物品，单次独立奖励机会) = min(a, 1) × p
```

`single_reward_probability` 是该口径的独立纯函数。`independent_reward_scenarios` 只列有条件的单次概率，不做概率并集。不同等级／副本／腐化门槛不相加。同一个Boss的不同tier在一个location内保留各自rates，并在条件中逐档显示；同值重复奖励可以共享一条展示，但原始组索引全部保留在 `sourceGroups`。例如[乌凯罗斯的扭曲之心](https://lastepoch.tunklab.com/unique/twisted_heart_of_uhkeiros)保留尸骸大帝6%–48%与两个编织回响来源；[贪婪虚空](https://lastepoch.tunklab.com/unique/ravenous_void)保留世界预言0.12%、加斯帕0%–4.5%及两个回响来源；[赫罗特的憩息](https://lastepoch.tunklab.com/unique/heorots_repose)保留莫迪塔斯20%和开启者条件。

以下案例固定了“每次”与“至少一件”的边界：

- [Aberroth](https://lastepoch.tunklab.com/npc/Aterroth)的先驱专属物品：开启者独立奖励为 `1×1/10=10%`，所有玩家的另一次独立奖励为 `0.2×1/10=2%`。两项分别显示，不写11.8%。先驱者之针344的两个独立同值奖励都各为30%，展示30%，不写51%。
- [Herald of Oblivion](https://lastepoch.tunklab.com/npc/UberAterroth)有重复的独立专属池。物品358在每个池中为 `20/42=47.6190476…%`，357为 `16/42=38.0952381…%`，353为 `6/42=14.2857143…%`；不累计为多次出货概率。
- [The Fading Brink](https://lastepoch.tunklab.com/echo/the_fading_brink)要求击败全部十位先驱，完成奖励表含十份先驱奖励。先驱者之针344的**每次先驱奖励**为15%–55%，不把十次合成为80.31%–99.97%。原始十个来源组仍完整保留；放置该回响需要至少300腐化。
- Julra的238：T1为100%、T2为50%、T3为10/24、T4为10/27。各tier的组互斥；T1–T4分别列值，不把不同tier相加，也不把另一档的零机会当成该档已有独立奖励。

- 灵魂赌徒265–267采用每次购买对应部位的副本tier概率，T1至T4为3%、4%、5%、6%；不误标世界掉落或Boss击杀率。
- 25件先古暗金全部有裂隙野兽来源。1.3.2官方补丁将原本只能兑换的先古也加入掉落，其机会随进化数、奖励材料、腐化与命运Boss加成变化；没有一个通用固定百分比。可兑换项保留原生兑换成本。[官方1.3.2说明](https://forum.lastepoch.com/t/last-epoch-patch-1-3-2-notes/79385)
- 茧化23件是编织回响茧化目标的完成奖励，鉴定结果排除Boss专属；不捏造“某一部位必定占1/23”。[官方1.2说明](https://forum.lastepoch.com/t/last-epoch-tombs-of-the-erased-patch-notes/75247)
- 进化终焉444为结束裂隙野兽谱系的奖励，不混作世界随机暗金。[官方1.3说明](https://forum.lastepoch.com/t/last-epoch-beneath-ancient-skies-patch-notes/78635/2)
- 酿酒大师的皮带扣416为完成The Grand Brewery的100%奖励。[该回响](https://lastepoch.tunklab.com/echo/the_grand_brewery)
- 贪婪131为埃尔扎的账本任务奖励；赌徒的谬误130是官方1.2重新加入的第二章阿尔特姆任务奖励。没有沿用已失效的旧任务名，也不把普通版130与灵魂赌徒版265混同。[131详情](https://lastepoch.tunklab.com/unique/avarice)、[官方130回归说明](https://forum.lastepoch.com/t/last-epoch-tombs-of-the-erased-patch-notes/75247/8)

## 破碎王冠的制作来源

物品1不是随机掉落。原生 `ItemData.ChangeToUniqueOfSameItemType`（`0x11FA190`）先检查头盔类型0、底材23（符文面罩／Runed Visage），遍历全部词缀，要求ID53及34同时存在，显示阶数合计至少21；没有跳过封印词缀。条件满足后直接写UniqueID1，跳过随机抽取。[原生证据](../../sources/unique-drop-native-evidence-2026-10-18.json)

`CraftingManager.Forge`（`0x1167F80`）在符文5（升华）的分支支付锻造潜能成本后调用该方法。因此界面写“制作：符文·升华；符合配方时100%”，条件为符文面罩、魔力34、伤害由魔力优先承受53、全部词缀总T≥21（含封印）。该100%是成功执行符合配方的制作结果，不是底材掉落率，也不保证没有锻造潜能的装备能启动制作。

## 旧／隐藏与图片

原词库的46鲨齿锯和69光明传家宝在本机1.5.2.2均为hideFromPlayers=1、canDropRandomly=0；343遗忘之卵也隐藏且不进入随机池，但仍保留涅墨西斯奖励选项说明。248石肤原词库已隐藏、无装备类型，原生也不随机掉落，当前来源与固定概率不编造。四个ID均未从保存数据或词库删除。隐藏不能被解释成“历史物品已从玩家仓库消失”，也不能用343的奖励选项率充当地面掉落率。

487个图标URL取自Tunklab原始image字段，不能由slug猜图片名，例如伊莎多拉头盔图片是 `isadorarevenge.png`。本次对ID0、5、277、379、423、486实际读取图片响应头和32字节PNG签名，均为HTTP206、image/png；没有下载另存远程图片作为显示绕过，另外481个URL只按源字段提供，未逐一声明验证。详细检查记录已随[冻结输入](../../sources/unique-drop-inputs-2026-10-18.json)保存。[红戒图标](https://lastepoch.tunklab.com/img/item/red_ring_of_atlaria.png)

## 验证边界

这里是原生算法与发布数据库的静态分析、条件概率计算和来源核对，没有执行游戏客户端掉落实验。概率采用原生浮点字段的解析值，以解析模型计算；界面按适当精度显示百分比。来源率不包含未建模的活动加成或镜片影响。没有概率时显示来源条件或“未公开固定概率”，不以reroll、稀有度文字或缺少Boss记录推造数值。

最终离线重建结果确定；489条物品均有来源描述。243个含定量原始rates的物品／来源组合中，同一组合没有并存不同等级／腐化门槛的情况，tier与开启者条件均逐项对应概率。原始奖励组索引完整且非空；重复同值奖励只在展示层共用单次数值，不丢原始记录。
