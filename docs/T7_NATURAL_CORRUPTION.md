# 巨石腐化对普通自然掉落T7的影响

调查日期：2026-10-17；本机 Last Epoch **1.5.2.2**，Steam build `25816319`，build hash `8dfd6929fe2d10f2e77b7ed4c8e6910f49b2736b`。证据来自实际 `GameAssembly.dll` 与 `PermaLoad.bundle`。没有启动游戏、采样掉落或读取线上服务器状态。

## 结论

**普通自然掉落受巨石腐化影响，不能把普通崇高预言的水平曲线推广到自然掉落，更不能说腐化在任何情况下都不影响T级。**

需要分清三层：

1. 固定词缀身份、装备类型、物品等级、初始raw rarity、生成上下文和观星台倍率时，普通词缀的 `RollTier`／`GetAffixTierUpgradeChance` 直接公式不含巨石腐化。
2. 自然掉落的前置稀有度生成读取巨石稀有度加成。腐化改变raw rarity混合，进而改变词缀数量、魔法物品的自然崇高抑制，以及观星台稀有转崇高的进入比例。因此，**每个普通装备落点**及**每件最终崇高物品**的1T7／2T7概率不能都当常数。
3. 每次击杀、每张地图或每小时拿到几件，还受装备落点数、怪物／奖励来源及击杀速度影响。这些不是“每件装备内有几条T7”的同一个分母。

此外，部分普通时间线的腐化会提高地区等级；特殊词缀还有直接读取腐化的独立阶数算法。两者也不支持“任何情况下都无影响”的说法。

## 一、普通怪物自然掉落的完整入口

以下RVA均相对于本机 `GameAssembly.dll`。Cpp2IL dummy程序集仅用于方法名、签名和字段偏移；实际行为核对原生指令。

| 入口／方法 | RVA | 本轮核准的连接 |
|---|---|---|
| `ItemDrop.DropItem(bool,...)`／异步MoveNext | `0x1107770`／`0x112D600` | 怪物掉落取地区等级；MoveNext在`0x112DE7C`调用静态DropItem |
| 静态`ItemDrop.DropItem` | `0x1107830` | 处理掉落检定、普通掉落与额外保证稀有分支 |
| 普通掉落lambda `'<DropItem>b__3'` | `0x1130420` | 在`0x1130512`调用SpawnItemAtPoint |
| `GenerateItems.SpawnItemAtPoint` | `0x11CAF30` | 普通随机分支将itemType／subType／rarity设为−1；在`0x11CB59E`调用spawnRandomItem |
| `GenerateItems.spawnRandomItem` | `0x11D1BF0` | 在`0x11D1D64`调用initialiseRandomItemData；普通路径rollModifiers为空 |
| `initialiseRandomItemData` | `0x11CFB00` | `0x11CFD09`调用RollBaseItem，`0x11CFD50`调用GenerateAffixes；上下文为Normal |
| `RollBaseItem` | `0x11C7060` | rarity=−1才在`0x11C7CD3`调用RollRarity；预言的指定rarity绕过它 |
| `RollRarity` | `0x11C9B30` | 读取ActiveRun.increasedItemRarity，做暗金／套装检定及普通rarity额外重抽 |
| `GenerateAffixes`→`RollAffixes` | `0x11C0530`→`0x11C5E90` | 普通装备在`0x11C0D92`进入RollAffixes |
| `RollTier`／`GetAffixTierUpgradeChance` | `0x11CA480`／`0x11C26F0` | 按等级、rarity、词缀权重和观星台倍率产生普通词缀阶数 |

怪物的“额外保证稀有”是另一分支：helper `'<DropItem>g__spawnRandomItemForActor|1'`（`0x112F140`）在`0x112F4AF`–`0x112F4B4`选raw3／4，并在`0x112F509`调用spawnRandomItem。因此，“普通怪物的一地装备”可能混有随机rarity与保证稀有来源；不能假定每件都只经过同一个RollRarity入口。

## 二、腐化如何进入Item Rarity

`MonolithRun.updateCorruptionMod`（`0x12F4C10`）先删除旧persistent mod；若当前时间线允许corruption mod且腐化大于0，加入时间线指定的mod。

- `0x12F4E31`读取 `web.corruption`（`+0x30`）。
- `0x12F4E52`调用 `EchoWeb.GetMonsterPowerMultiplierFromCorruption`（`0x12B18E0`）。
- `0x12F4E57`减1，将结果作为effectModifier传给 `ActiveMonolithMonsterMod.NewPersistentMod`（`0x12A7170`）。
- NewPersistentMod在`0x12A71CA`写入其effectModifier字段`+0x1C`。
- `MonolithRun.calculateIncreasedRarityAndExperienceFromMods`（`0x12F2850`）在`0x12F2991`–`0x12F29A4`累加 `(1+effectModifier)×mod.increasedItemRarity`，写入run的`+0x70`。

实际资源 **Monster Power From Corruption Mod**：pathID `4764908917144808128`，modKey `993139884`，`increasedItemRarity=0.01f`。例如Heorot Timeline（pathID `2322533088954582737`）的普通和强化难度均启用hasCorruptionMod并引用该key。

令C为非负腐化，P为上述原生helper的输出；名义常数写成：

```text
P(C) = 0                                      C=0
     = 0.6×C                                  0<C≤100
     = 0.002×C^1.52 + 1.055×C − 47.692955      C>100

I(C) = I_other + 0.01×P(C)
```

I是代码里的“增加稀有度”比例：`I=.6`表示增加60%，不是0.6%。P的常数与分支位于`0x12B18EF`–`0x12B193F`；幂计算调用在`0x12B190C`。

| 腐化C | P(C) | 仅腐化提供的I | 增加稀有度百分比 |
|---:|---:|---:|---:|
| 0 | 0 | 0 | 0% |
| 100 | 60 | 0.600000 | 60.000000% |
| 300 | 280.455124 | 2.804551 | 280.455124% |
| 1000 | 1079.922656 | 10.799227 | 1079.922656% |

注意：`calculateIncreasedRarityAndExperienceFromMods`末段还给`+0x74`的Experience加腐化收益；**那段经验计算不是这里的Item Rarity公式**。Item Rarity来自前面的mod累加链。

## 三、Item Rarity怎样改变raw rarity和词缀数量

`RollRarity`在`0x11C9CC3`读取run.increasedItemRarity；大于0时，在`0x11C9D68`乘`0.36f`，通过整数部分加小数概率得到额外重抽次数：

```text
x = 0.36×I
K = floor(x) + Bernoulli(frac(x))
```

`0x11C9D78`–`0x11C9DDD`决定K；`0x11C9DE0`–`0x11C9E2D`重抽K次，只保留最大的roll。`0x11C9E55`检查当前场景是否Monolith；巨石保留这个最大值，非巨石在`0x11C9E9A`重新取独立均匀roll。

在100级，`CalculateRarityBoundaries`（`0x11BCBF0`）给raw0／1／2／3／4的累积边界是：

```text
[0.13, 0.35, 0.84, 0.93, 1]
```

raw rarity是**生成前的数值**，不是最终白／蓝／黄／紫标签。`RollAffixes`在`0x11C631B`取得部位最大词缀数，并在`0x11C6330`–`0x11C6339`取它与raw rarity的较小值。对最大四词缀的普通装备，raw0–4因此分别提供0–4个词缀槽。

暗金／套装检定发生在普通rarity重抽之前。I也会在`0x11C9CCE`–`0x11C9CEB`影响其机会。因此不能把初始roll当成完全未筛选的U(0,1)后直接求最大值。

为了给出可复核例子，下面固定ilvl100、其他IIR=0、uniqueAndSetDropRateMultiplier=1、`0x11C9C85`的额外1.5标记关闭、全局等级至少20，并**排除已返回暗金／套装的物品**。令：

```text
c = (0.00156 + 0.00730) × [1 + 0.6×ln(1+I)]
n = floor(0.36×I)，f = frac(0.36×I)

F(t) = 0                                                     t<c
     = (t−c)/(1−c) × [(1−f)×t^n + f×t^(n+1)]                 c≤t≤1
```

在各边界对F作差，即得条件raw rarity分布：

| 腐化 | raw0／0槽 | raw1／1槽 | raw2／2槽 | raw3／3槽 | raw4／4槽 |
|---:|---:|---:|---:|---:|---:|
| 0 | 12.222289% | 22.196662% | 49.438021% | 9.080453% | 7.062574% |
| 100 | 9.745328% | 19.698733% | 51.475427% | 10.595144% | 8.485367% |
| 300 | 1.493894% | 10.312617% | 58.426985% | 16.092615% | 13.673889% |
| 1000 | 0.005525% | 0.602719% | 41.924498% | 27.505349% | 29.961909% |

这不是T7概率表。它证明：即使固定100级、没有给RollTier增加腐化系数，自然掉落也会从少槽物品移向多槽物品。具体T7率还要对这些分支继续计算，不能把“4槽29.96%”误读成“T7率29.96%”。

## 四、稀有度改变自然崇高抑制及CoF11入池比例

普通 `RollTier` 在`0x11CA77D`检查raw rarity：raw1／2存在95%阻止自然崇高的检定；raw3及以上绕过。故腐化造成的raw混合变化，除了增加槽位，还会减少这种魔法物品抑制的占比。

固定100级、同一条允许T6的普通词缀、该装备类型上权重w=1、满观星台M=1.5／Q=2，在进入后续保底以前：

```text
raw3／4：P(该词缀自然成为T7) = .14×(.045×1.5)×(.066×1.5×2)
                                 = 0.187110%
raw1／2：上值再乘.05              = 0.0093555%
```

同一个raw分支内这些数不随腐化变化；没有固定raw分支而观察总体词缀时，其混合比例会随腐化变化。自然升阶函数和参数详见 [T7_LENS_DATAMINING.md](T7_LENS_DATAMINING.md)。

CoF11又增加一条间接通道：

| 检查 | 原生证据 |
|---|---|
| 初始物品isRare | `RollAffixes:0x11C60EE`；`Item.rarityIsRare:0x122FB30`接受raw3–6，普通RollRarity中适用的是3／4 |
| forceExalted尚未开启 | `0x11C60FB`；已开启则跳过 |
| 地区等级至少45 | `0x11C610B`调用`ZoneInfoManager.get_ZoneLevelHighEnoughToDropExaltedItemsThroughCoF`；该getter `0x18A7840`在`0x18A786E`比较`0x2D`并setge |
| 阶级11加成已启用 | `CircleOfFortune.ToggleRank`的rank11分支`0x208D18A`，于`0x208D1D9`写生成器`+0x7C=.25` |
| 25%检定成功后开启force | `0x11C6149`读该机会，`0x11C614E`检定，`0x11C6157`设forceExalted=true |

在上表的受控例子里，raw3／4合计占比由C100的19.080512%变为C1000的57.467258%。若CoF11开启且地区≥45，随机普通装备进入这次force标志的总体比例因而从 **4.770128%变为14.366814%**。这是开启后续保证崇高的比例，**不是最终崇高率，也不是T7率**；已有自然崇高还会影响保底步骤是否真正升级某槽。

怪物“额外保证稀有”的入口还在`0x112F38D`调用`GetChanceForGuaranteedRareToForceExalted`（`0x1108470`）：等级≤50为0，否则`.15×(L−50)/50`，100级为15%；它可使用CoF6的ChanceToForceExaltedMultiplier。它不等同于上述CoF11的25%，也不能直接重复施加到普通崇高预言。

## 五、三个分母怎样计算

令D为本报告限定的**普通非暗金／套装装备落点**，E为它最终含T6及以上普通词缀成为崇高，K为最终恰好T7条数。r_n(C)是腐化C时raw n的比例；g_n,k是给定该分支（包括其force检定）最终恰好k条T7的概率，e_n是最终崇高的概率。

```text
P(K=k | D,C)   = Σ_n r_n(C) × g_n,k
P(K=k | E,D,C) = [Σ_n r_n(C) × g_n,k] / [Σ_n r_n(C) × e_n]   k≥1
```

因此，1T7／2T7“占所有普通装备的比例”与“占最终紫装的比例”是两个数；即使同一公式里g_n,k不直接读取腐化，权重r_n(C)和条件分母也能变。各指标的增幅不必相同，不能把其中一项的倍数套给其余指标。

每次击杀或每小时的期望数量还须乘入相应的装备落点数，并处理额外保证稀有、冠军、宝箱等各来源。此报告没有把IIR或怪物强度倍率当作每小时T7收益倍率，也没有在未给击杀速度时推算效率。

## 六、地区等级与特殊词缀的额外反例

普通时间线也可能因腐化跨过自然T7的ilvl90门槛。`EchoWeb.getZoneLevel`（`0x12BDDD0`）在`0x12BDE5A`读取web.corruption并于`0x12BDE60`调用`Difficulty.getLevel`（`0x1320F80`）。后者在additionalCorruptionEffect=1时计算：

```text
L = min(100, baseLevel + corruption / corruptionRequiredPerLevel 的整数商)
```

`ZoneInfoManager.ApplyMonolithLevelScaling`（`0x18A7080`）在`0x18A7094`取得该等级，再在`0x18A70A4`转入`SetZoneLevel`（`0x18A76A0`），因此不是只改UI显示。Reign of Dragons Timeline7（资产pathID `4320164323684558167`）的普通难度资源是baseLevel85、每10腐化加1级、腐化上限50，故C0的L85到C50的L90。强化难度baseLevel100、additionalCorruptionEffect=2，保持100。因此，前文“普通直接RollTier无腐化项”必须附带**固定物品等级**这一前提。

`RollSpecialAffixTier(itemLevel,corruption)`（`0x11CA000`）则有独立的腐化额外阶数检定；实际放逐法师调用链与数值见 [T7_SPECIAL_CORRUPTION.md](T7_SPECIAL_CORRUPTION.md)。不能将特殊词缀的公式套在普通词缀上，也不能因普通公式不读腐化就否认这条分支。

普通崇高预言的奖励等级和raw rarity由另一入口指定，且其普通路径不进入上述自然RollRarity；详见 [T7_PROPHECY_CORRUPTION.md](T7_PROPHECY_CORRUPTION.md)。

## 本机证据与复算

可随仓库查看的原生指令、时间线配置及计算表摘要见[冻结证据](../analysis/t7-corruption-effects-evidence.json)。

| 文件 | SHA256 |
|---|---|
| GameAssembly.dll | `d5f9fb458f0e9878e697a92b590a586a52fd77e645f8bf87bb4f2b74c6c56567` |
| global-metadata.dat | `81ff3419726bb5cf8e4f86eace2b2df2638ec4bc6ffed8a7a5dbaf09aa6f7bed` |
| PermaLoad.bundle | `7fac4caacd757f5f821f0e5c15f6eccf573aa8ebf89d3f464d124dc2e72ac93c` |

原生反汇编、当前资产字段及本轮计算只保存在本机 `.cache/t7-natural-corruption/`：`mine.py`、`asset_Monster_Power_From_Corruption_Mod_4764908917144808128.json`、`timeline-corruption-assets.json`、`examples.py`及`rarity-examples.json`。运行`examples.py`可复算IIR和raw混合表，包含归一及非负检查。计算使用名义常数和连续均匀随机数，未枚举float32随机端点的微小差异。

未修改游戏或过滤器，没有将静态还原写成客户端实测。所有结论限定上述文件hash对应版本；线上热更新、其他特殊奖励及插件改写不在本轮验证范围。
