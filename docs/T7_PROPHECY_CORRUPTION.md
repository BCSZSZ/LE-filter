# 普通崇高预言：区域等级、腐化及观星台阶级的原生调用链

调查日期：2026-10-17。本机版本：Last Epoch **1.5.2.2**，Steam build ID `25816319`，build hash `8dfd6929fe2d10f2e77b7ed4c8e6910f49b2736b`。以下为实际游戏二进制与资源的静态调查；没有启动游戏采样，也没有读取线上服务器运行态。

## 可用于计算器的结论

限定 `GenericEquipment`、`RarityGroup.Exalted` 的**普通崇高装备预言**，使用无镜片、Origin、Finality 或 Quality，并固定物品类型及合法词缀池：

- 奖励生成入口直接传入 **ilvl=100**，不取完成预言所在地的区域等级。区域等级输入可以保留，但该模式的实际奖励等级应显示为100。
- 巨石腐化不会改变该入口的初始稀有度、自然T6/T7升阶、镜片升阶或保证崇高步骤。对同一组输入，单件恰好1T7、恰好2T7的腐化曲线均应为**水平线**。
- 不能套用自然随机掉落的稀有度曲线，也不能把预腐化装备、指定冠军／实验词缀奖励或暗金LP的腐化收益混进此模式。
- 观星台实际原生倍率为：阶级0–3时 `M=1,Q=1`；4–8时 `M=1.5,Q=1`；9–12时 `M=1.5,Q=2`。普通崇高奖励本身在阶级4解锁，0–3只能作为反事实倍率对照。
- Origin、Finality在阶级4解锁，Quality在阶级9解锁。三个升阶镜片的基础触发概率均为 `0.2f`，不随区域等级或巨石腐化增长。

这里的“不随腐化变化”指**已经产生的一件普通崇高预言奖励中有几条T7**。它没有估算完成预言所需时间、每小时获得奖励数、自然掉落数量或其他奖励入口。

## 证据类型与复现边界

原生实现来自：

```text
C:\Program Files (x86)\Steam\steamapps\common\Last Epoch\GameAssembly.dll
```

Cpp2IL生成的 `LE.dll` 仅用于方法名、签名、字段偏移与RVA；空的方法体不作为实现证据。实际分支和常数均读取原生指令。以下地址都是 `GameAssembly.dll` 的RVA，不是文件偏移。

| 文件 | SHA256 |
|---|---|
| GameAssembly.dll | `d5f9fb458f0e9878e697a92b590a586a52fd77e645f8bf87bb4f2b74c6c56567` |
| global-metadata.dat | `81ff3419726bb5cf8e4f86eace2b2df2638ec4bc6ffed8a7a5dbaf09aa6f7bed` |
| PermaLoad.bundle | `7fac4caacd757f5f821f0e5c15f6eccf573aa8ebf89d3f464d124dc2e72ac93c` |

本轮本地反汇编保存在 `.cache/t7-corruption/`；`mine.py` 只读原生文件，输出带RVA、调用名及RIP常数的指令记录。`audit_evidence.py` 另解码阶级跳转表并核对关键指令字节，结果为 `evidence.json`。缓存是开发调查材料，运行计算器不依赖它。三镜片完整概率机制及戒指实例见 [T7_LENS_DATAMINING.md](T7_LENS_DATAMINING.md)。

## 一、奖励等级是入口硬编码的100

实际奖励资源 `0121 Exalted Ring`，`PermaLoad.bundle` pathID `5929883376935552949`：

| 字段 | 值 | 含义 |
|---|---:|---|
| ID | 121 | 普通崇高戒指奖励 |
| itemGenerationType | 0 | GenericEquipment |
| genericItem.itemType | 21 | 戒指 |
| genericItem.subType | −1 | 随机底材 |
| genericItem.ilvl | 100 | 资源配置等级 |
| genericItem.rarityType | 1 | 使用RarityGroup |
| genericItem.rarityGroup | 5 | Exalted |
| unlocksAtRank | 4 | 解锁阶级 |
| corruptionBehaviour／corruptionOutcome | 0／0 | Default／None |

资源中的100还有更强的原生调用证据：

| 调用／指令 | RVA | 已核对行为 |
|---|---|---|
| `ProphecySlotReward.SpawnRewardForPlayer` | `0x20B3800`，长`0x1396` | GenericEquipment分支从`0x20B4489`开始 |
| `GetChosenRarityAndForceExalt`调用 | `0x20B4498` | 先从奖励设置取得raw rarity与forceExalted |
| `mov r9d,0x64` | **`0x20B4B23`** | 直接将第四个本机调用参数ilvl设为100 |
| `spawnSpecificItemAtPoint`调用 | `0x20B4B37` | 传入上述100；此处没有读取区域等级 |
| `GenerateItems.spawnSpecificItemAtPoint` | `0x11D1F80`，长`0x296` | `0x11D1FA0`保存ilvl，`0x11D20BB`原样传给initialise |
| `initialiseRandomItemData`调用 | `0x11D20CF` | 奖励等级仍为100 |
| `GenerateItems.initialiseRandomItemData` | `0x11CFB00`，长`0x74A` | `0x11CFB2B`保存ilvl，`0x11CFD04`传给RollBaseItem，`0x11CFD2A`传给GenerateAffixes |
| `RollBaseItem`入口等级规范化 | `0x11C7232`–`0x11C7281` | 只有负数才回退环境等级；大于100才截至100；传入100原样保留 |

所以本版本的普通预言不只是“资源默认100，可以随区域变动”：**奖励代码本身也直接传100**。计算器若将区域等级80代入此模式的RollTier或词缀池，就会造出该调用链没有的变化。

`SpecificItemProperties.Generate`是另一奖励分支。`SpawnRewardForPlayer`在`0x20B3C5C`读取itemGenerationType，值0直接跳到上述GenericEquipment分支；普通Exalted奖励不会先经过SpecificItem生成再改阶数。

`initialiseRandomItemData`在`0x11CFD48`为GenerateAffixes传入`GenerationContext.Normal=0`，在`0x11CFD22`传入canRollUncraftableTiers=true。自然阶数由`RollTier`（`0x11CA480`，长`0x47F`）按所传等级与词缀资格计算，崇高升阶调用下文的GetAffixTierUpgradeChance；这两个方法均不读取CurrentCorruption。固定100级也排除了地区等级通过自然阶数阈值间接影响本入口的可能。

## 二、为什么null corruption没有把地区腐化偷偷带进来

只检查RollAffixes参数不足以得出全链无影响，因此分别核对了前置稀有度、底材、预腐化、显式腐化和后处理。

### 2.1 指定raw rarity跳过自然RollRarity

`ItemCreationProperties.GetChosenRarityAndForceExalt`，RVA `0x12199A0`，长`0x2A0`，对Exalted组顺序抽取：

| raw rarity／对应词缀数 | 设计概率 | forceExalted |
|---|---:|---|
| 1 | 0.005 | true |
| 2 | 0.995×0.01＝0.00995 | true |
| 3 | 0.995×0.99×0.4＝0.39402 | true |
| 4 | 0.995×0.99×0.6＝0.59103 | true |

这三个检定在 `0x1219B20`、`0x1219B73`、`0x1219BC2`载入常数，均不读取区域等级或腐化。表中使用设计小数，原生是相邻的float32表示。

`GenerateItems.RollBaseItem`，RVA `0x11C7060`，长`0x1F50`，在`0x11C7C7D`检查rarity是否为−1。普通预言已给定1–4，因此`0x11C7CAB`直接写入物品并跳到`0x11C7CF6`；只有−1才会到`0x11C7CD3`调用自然`RollRarity`。因此自然掉落稀有度加成及其额外重抽不能移植到普通崇高预言。

### 2.2 RollBaseItem里的两个CurrentCorruption调用都有其他入口门槛

`spawnSpecificItemAtPoint`在`0x11D2030`明确将nullable corruption置空。此处没有断言“空就是零”；继续追踪的实际结果是：

| `RollBaseItem`中的腐化读取 | 实际用途／门槛 | 普通崇高装备是否进入 |
|---|---|---|
| `0x11C7466`调用`MonolithGameplayManager.get_CurrentCorruption` | baseType107的Woven Echo分支；`0x11C7485`调用`RollWovenEcho` | 否；戒指等普通装备类型小于100，在`0x11C728D`已转入普通装备分支 |
| `0x11C8ABC`调用同一getter | raw rarity7的暗金；`0x11C8A31`的rarity7门槛后计算LP／WW，`0x11C8C08`调用`RollLegendaryProperties` | 否；raw1–4跳过此暗金分支 |

普通底材选择`TryRollEquipmentSubtype`的调用在`0x11C8968`，传入100、选定类型、物品标签与职业兼容条件，没有传入巨石腐化。改变物品类型、职业兼容或底材词缀效果仍可能改变合法词缀池；这与改变区域腐化是不同输入。

### 2.3 普通Exalted不会自动进入预腐化装备路径

`RollBaseItem`入口`0x11C7229`／`0x11C722C`将输出nullable `preCorruptInfo`清空。

之后`0x11C7CF6`–`0x11C7D19`只把raw rarity7／8送往UniqueList查找。raw1–4经`0x11C7F3B`的rarity8比较，直接跳到`0x11C85DE`，跳过整个暗金／套装处理段。

该方法中构造`PreCorruptItemInfo`的调用位于`0x11C8523`；它处在上述暗金／套装段内，且再受特定unique的`+0x78`开关约束。普通Exalted无法走到这里，`preCorruptInfo`维持空值。

`AfterRollingItemForDropOrEncounterReward`，RVA `0x11BBFF0`，长`0x2D7`，在`0x11BC25A`只对非空preCorruptInfo继续，才于`0x11BC2A0`调用`ApplyPreCorruption`。这条后处理不会把普通预言装备变成预腐化装备。

### 2.4 两个显式腐化开关也被关闭

普通GenericEquipment的`SpawnRewardForPlayer`在调用spawnSpecific前写入：

| 设置 | 写入RVA | 值 |
|---|---|---|
| corruptOnDrop | `0x20B4A87` | false |
| forceCorrupt | `0x20B4A80` | CorruptionOutcome.None＝0 |
| specialAffix | `0x20B4A68` | null |
| specialAffixIsChampion | `0x20B4A60` | false |
| minSpecialAffixTier | `0x20B4A58` | null |

`initialiseRandomItemData`在`0x11D0188`检查forceCorrupt；为0时跳过`0x11D01C9`的ApplyCorruptionOutcome。`spawnSpecificItemAtPoint`在`0x11D20D7`检查corruptOnDrop；为false时跳过`0x11D2140`的DetermineCorruptionOutcome与`0x11D2181`的ApplyCorruptionOutcome。

initialise中的另一次环境腐化读取`0x11CFFDF`用于`TryAddSpecialAffix`。普通奖励specialAffix为空，`0x11CFEBB`–`0x11CFEBE`已跳到`0x11D0181`，同样不会执行。指定实验／冠军奖励应单独分析，不能以该分支给普通奖励加额外T7。

最后的`DropItemAtPoint`，RVA `0x11BE1D0`，长`0x53E`，本轮也核对其本体：它处理额外套装／神像、编织相关额外物品、落点与复制，没有再次调用普通词缀生成、镜片升阶或物品腐化。不能把额外物品数量当作当前装备的T7变化。

## 三、镜片升阶本身不读巨石腐化

`SpawnRewardForPlayer`于`0x20B3C4C`调用实例`BuildLensRollModifiers`（`0x20B0C30`），再于`0x20B0DA9`调用静态重载（`0x20B0DD0`）。普通Exalted组在这一步重新选择的raw rarity也均携带forceExalt=true，因此符合这三个镜片的rare/exalted上下文。

静态重载只从ProphecyData读以下升阶机会，复制到ItemRollModifiers：

| 镜片 | 配置字段／ProphecyData偏移 | 原生复制RVA | 实际资产值 |
|---|---|---|---:|
| Origin | originLensPrefixTierUpgradeChance／`+0x90` | `0x20B0EE6`→`0x20B0EFE` | 0.2f |
| Finality | finalityLensSuffixTierUpgradeChance／`+0x94` | `0x20B0F27`→`0x20B0F3F` | 0.2f |
| Quality | qualityLensRandomAffixTierUpgradeChance／`+0xA0` | `0x20B1038`→`0x20B104C` | 0.2f |

实际值来自同一bundle的`Prophecy Data`，pathID `3864826814730378121`，不是只根据C#构造默认值推定。

`RollAffixes`于`0x11C68D0`调用`ApplyRandomAffixTierUpgrades`（`0x11BC630`，长`0x240`）。该方法分别对相应镜片机会做一次检定；选一条合格词缀后，依据当前阶数权重及固定`+1/+2/+3`权重升阶。这些方法不读区域等级、CurrentCorruption或稀有度加成。其后仍执行原有保证崇高逻辑，详见主报告。

这说明需要积分“自然阶数→镜片→保证崇高”，但在此入口中无需再乘一项随巨石腐化增长的镜片系数。

## 四、CoF阶级0–12的实际开关

`CircleOfFortune.ToggleRank`，RVA `0x208CE90`。`0x208CED0`以`rank−1`索引RVA **`0x208D2D8`** 的12项跳转表，已直接解码而非按旧网页描述猜阶级。

`GenerateItems`字段偏移`+0x84`为`ChanceForExaltedAffixesMultiplier`（M），`+0x88`为`ChanceForT7Affixes`（Q）。构造函数`0x11CE360`在`0x11CE451`、`0x11CE45E`均写入float32的1。

| 已启用至阶级 | M | Q | 对普通崇高预言的说明 |
|---|---:|---:|---|
| 0 | 1 | 1 | 未解锁普通崇高奖励 |
| 1 | 1 | 1 | 未解锁普通崇高奖励 |
| 2 | 1 | 1 | 未解锁普通崇高奖励 |
| 3 | 1 | 1 | 未解锁普通崇高奖励 |
| 4 | 1.5 | 1 | 解锁普通崇高；Origin／Finality可用 |
| 5 | 1.5 | 1 | 单件T7倍率同4 |
| 6 | 1.5 | 1 | 单件T7倍率同4；不是此时才启用M |
| 7 | 1.5 | 1 | 单件T7倍率同4 |
| 8 | 1.5 | 1 | 单件T7倍率同4；暗金LP倍率不套用于普通装备 |
| 9 | 1.5 | 2 | 启用Q，Quality可用 |
| 10 | 1.5 | 2 | 单件T7倍率同9 |
| 11 | 1.5 | 2 | 额外稀有转崇高不重复施加到已保证崇高奖励 |
| 12 | 1.5 | 2 | 预言双倍物品开关不改变单件词缀升阶率 |

关键原生分支：

| 阶级 | 表中目标RVA | 设置与证据 |
|---|---|---|
| 4 | `0x208CFCC` | `0x208D04A`载入1.5，`0x208D065`写GenerateItems+0x84；关闭时回1 |
| 6 | `0x208D09A` | `0x208D09F`载入1.5，`0x208D0BA`写CircleOfFortune+0xB0，即ChanceToForceExaltedMultiplier；与M是两个字段 |
| 8 | `0x208D0D3` | `0x208D0F3`写UniquesLPRollMultiplier；不属于普通装备T7倍率 |
| 9 | `0x208D100` | `0x208D13D`载入2，`0x208D158`写GenerateItems+0x88；关闭时回1 |
| 11 | `0x208D18A` | `0x208D1D9`写ChanceForRareItemsToBecomeExalted0To1＝0.25；关闭时回0 |
| 12 | `0x208D1E0` | 写PropheciesGrantDoubleItems布尔值，独立于M/Q |

倍率写入受`GameplayEnvironment.IsSingleplayerOrServer`约束，与掉落在离线或服务端生成的设计一致。当前文档只验证分发客户端附带的对应原生实现，没有宣称验证线上服务器是否另有热更新。

`GetAffixTierUpgradeChance`（`0x11C26F0`，长`0x17B`）在`0x11C27F0`仅对第二步T6→T7读Q；在`0x11C2800`–`0x11C280C`两步均读M。因此M影响自然T6和之后T7，Q只影响T7，不能对整件双T7概率简单乘倍率。

阶级11稀有转崇高位于`RollAffixes`的`0x11C60EC`起：在`0x11C60FB`发现forceExalted已为true就跳到`0x11C6191`，不会再次掷25%。普通Exalted组所有raw rarity分支均为true，故阶级6外部“强制崇高机会倍率”及阶级11的25%都不应再次乘入这类奖励。

镜片解锁取自实际ProphecyData的lensUnlockRanks：Origin枚举4→阶级4，Finality枚举5→4，Quality枚举11→9。`GetUnlockRankForLens`（`0x20A9070`）按枚举索引该列表；不是用镜片名称猜次序。奖励解锁取自各ProphecySlotReward资源。未解锁的组合在计算器中应标记不可用，或明确标为假设对照。

## 尚未声称解决的范围

- 本结论不能扩展成“腐化对全游戏T7没有影响”。自然掉落、暗金LP／WW、预腐化物品、Corrupted Bag和特殊词缀奖励各有其他入口。
- 没有将“固定100级普通预言”的结果当作可改ilvl的真实预言入口。若另提供可改装备等级的研究模式，应明确区分它与实际普通预言。
- 没有测量运行时热更新、插件改写、PRNG状态相关性、单局样本的方差或完成预言的效率。
- 静态调用链支持本版本中的水平腐化曲线；未来版本需重新核对上述文件hash与关键分支。
