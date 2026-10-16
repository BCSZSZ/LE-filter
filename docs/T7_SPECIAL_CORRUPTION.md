# 巨石腐化直接影响T级的真实反例：放逐法师实验词缀

调查日期：2026-10-17。范围为本机 Last Epoch **1.5.2.2**、Steam build **25816319** 的实际资源与 native 代码静态核验，没有启动游戏采样。

**“巨石腐化在任何情况下都不影响T级”不成立。** 已确认的反例是放逐法师／符文监牢掉落的实验装备：在相同物品等级下，巨石腐化会增加其**那一条实验词缀**掷出T7的机会。这是最终词缀阶数的变化，不能只解释为特殊物品掉得更多。普通崇高装备预言仍排除此分支，原有结论见 [T7_PROPHECY_CORRUPTION.md](T7_PROPHECY_CORRUPTION.md)。

## 1. 一条真实可达的实验掉落调用链

实际 `Random Encounter Data` 的 PermaLoad pathID 为 **3669649646199173902**。其 `imprisonedMageActorData` 指向放逐法师数据，`possibleExperimentalItemTypes=[3,4,2]`，即靴子、手套、腰带。`droppedExperimentalItemsAreGiftable=true`、`droppedExperimentalItemsAreAlwaysClassComptaible=false`。这些是游戏资源的实际字段，不是根据装备名称猜测。资产完整导出（`.cache/t7-special-corruption/RandomEncounterData.json`）

在启用掉落的 RunePrisonItemDrops 死亡入口中，调用链如下。所有地址均为同一 GameAssembly.dll 的RVA。

| 步骤 | RVA | 实际行为 |
|---|---|---|
| `RunePrisonItemDrops.Start` | `0x156693A` | 将其死亡处理绑定到 `Dying.deathEvent` |
| `RunePrisonItemDrops.OnDeath` | `0x1565792` | 跳转到 `SpawnExperimentalItem` |
| `SpawnExperimentalItem` | `0x1565A75` | 保存实际生成等级，后续作为特殊词缀的 itemLevel |
| 检查巨石 | `0x1565B31` | 调用 `MonolithGameplayManager.HasActiveWeb` |
| 巨石腐化取值 | **`0x1565B80`** | 从 ActiveRun→EchoWeb 的 `+0x30` 字段取值，保存到本地捕获数据 `+0x14` |
| 无巨石时 | `0x1565BD8` | 同一捕获值写0 |
| 生成普通实验装备底体 | `0x1566D5D` | 先调用 `initialiseRandomItemData` |
| 取出捕获的腐化 | **`0x1566D72`** | 把上述 `+0x14` 读出，传作 corruption |
| 设置特殊词缀参数 | `0x1566D82`、`0x1566D8D`、`0x1566D92` | `minTier=null`，`specialAffixType=Experimental=1` |
| 添加实验词缀 | **`0x1566D9A`** | 调用 `GenerateItems.TryAddSpecialAffix` |

证据：Start（`.cache/t7-special-corruption/RunePrisonItemDrops-Start.asm`）、OnDeath（`.cache/t7-special-corruption/RunePrisonItemDrops-OnDeath.asm`）、SpawnExperimentalItem（`.cache/t7-special-corruption/RunePrisonItemDrops-SpawnExperimentalItem.asm`）、实际生成与掉落helper（`.cache/t7-special-corruption/RunePrisonItemDrops-'_SpawnExperimentalItem_g__GenerateAndDropExperimentalItem_5_0'.asm`）。

这里的腐化字段与 `MonolithGameplayManager.CurrentCorruption` getter 的取值链完全一致：getter在 `0x1D82D16–0x1D82D28` 同样读取 ActiveRun→EchoWeb→`+0x30`。它是**区域巨石Corruption**，不是物品的 Corrupted 状态或物品腐化结果。getter原生实现（`.cache/t7-special-corruption/MonolithGameplayManager-get_CurrentCorruption.asm`）

## 2. 腐化确实参与特殊词缀的阶数投掷

`TryAddSpecialAffix`（RVA **0x11CC920**）先按实际物品类型与底材选择兼容的实验词缀；必要时移除一条同类词缀以容纳它。随后在 **0x11CCBA8** 调用 `RollSpecialAffixTier(itemLevel, corruption)`。原生实现（`.cache/t7-special-corruption/GenerateItems-TryAddSpecialAffix.asm`）

`RollSpecialAffixTier`（RVA **0x11CA000**）的T7部分为：

```text
p7 = itemLevel >= 90 ? (itemLevel - 89) / 2750 : 0

if Roll(p7):
    return tierIndex 6    # T7
if Roll(corruption / 1000) and Roll(p7):
    return tierIndex 6    # T7

# 两次T7机会均未成功，才继续掷T6及以下。
```

对应指令：`0x11CA08E`计算 `corruption/1000`；`0x11CA0A0–0x11CA0AF`计算等级T7基础机会；`0x11CA1A5`第一次掷T7；`0x11CA1EB`掷腐化提供的第二次机会；`0x11CA22C`第二次掷同一T7概率；`0x11CA46E`返回6。T6也有对应的 `corruption/400` 第二次机会，除法位于 `0x11CA097`。这些都发生在阶数选择内，非物品数量判定。完整原生实现（`.cache/t7-special-corruption/GenerateItems-RollSpecialAffixTier.asm`）

在通常独立投掷模型下，固定100级时 `p=11/2750=0.004`，实验词缀成为T7的设计概率为：

`P(T7) = p + (1−p) × clamp(C/1000, 0, 1) × p`

| 巨石腐化C | 100级实验词缀为T7 |
|---:|---:|
| 0 | 0.40000% |
| 100 | 0.43984% |
| 200 | 0.47968% |
| 400 | 0.55936% |
| 600 | 0.63904% |
| 1000 | **0.79840%** |
| 1500 | 0.79840% |

表中是**新加的那一条实验词缀**为T7的概率，不是整件装备“恰好一条T7”或“至少一条T7”的概率。数值使用名义设计小数；native使用float32及有限PRNG，未将此静态推导称为客户端实测。1000以上时这一次额外T7投掷机会已饱和，不能外推为无上限线性增长。计算与常数字节核验（`.cache/t7-special-corruption/evidence.json`）

实际 MasterAffixesList 包含12条实验词缀：673–679、710–714，全部 `specialAffixType=1`、前缀、具有8阶配置；可出部位分别为上述手套／靴子／腰带。例如手套的673“Experimental Ward on Kill”就在真实兼容池中。其ID、可出类型和阶数配置均已从 pathID **2955332227439360059** 核对，见 evidence.json（`.cache/t7-special-corruption/evidence.json`） 的 experimentalAffixes。

## 3. 这不是随后被覆盖的中间阶数

`TryAddSpecialAffix` 的 minTier 在本入口是null，因此不会触发其最低阶数覆盖。该函数在 **0x11CCC9D** 把返回值直接传给 `AddAffixNoCostOrChecks`；再经 `ItemAffix` 构造函数的 **0x1215F36** 写入 `tierIndex`。返回6确实成为内部index6，即T7。AddAffix（`.cache/t7-special-corruption/ItemData-AddAffixNoCostOrChecks.asm`）、ItemAffix构造（`.cache/t7-special-corruption/ItemAffix-.ctor.asm`）

实验helper在添加成功后，只调用 `GiveItemCurrentGiftingTargets`（0x1566E62）、`RebuildID`（0x1566E71）与 `DropAfterDelay`（0x1566EDE）；没有再调用词缀阶数生成或物品腐化。延时coroutine在 **0x11F12E5** 把同一item交给 `DropItemAtPoint`。后者处理额外物品、复制与落地，不重新掷该实验词缀阶数。helper（`.cache/t7-special-corruption/RunePrisonItemDrops-'_SpawnExperimentalItem_g__GenerateAndDropExperimentalItem_5_0'.asm`）、延时安排（`.cache/t7-special-corruption/GenerateItems-DropAfterDelay.asm`）、coroutine（`.cache/t7-special-corruption/'_DropAfterDelayCoroutine_d__154'-MoveNext.asm`）、落地实现（`.cache/t7-special-corruption/GenerateItems-DropItemAtPoint.asm`）

## 4. 本次结论的边界

- **普通崇高装备预言**：specialAffix为空，initialise在0x11CFEBE直接跳过整个添加特殊词缀段；此反例不改变该模式的水平腐化曲线。[对应调用链](T7_PROPHECY_CORRUPTION.md)
- **指定实验／冠军预言**：实际奖励810–813、820–823属于特殊BossLoot分支；其资源分别使用Experimental组10、Champion组11，最低特殊词缀index依次为−1／−1／5／6。不能把它们混入普通23类崇高奖励。全部资源及BossLoot对象保存在本轮缓存；本报告的定量反例选择已经逐步证实的放逐法师天然实验掉落，而不把名字或资源字段单独当成完整掉率证明。资产索引（`.cache/t7-special-corruption/asset-index.json`）
- **冠军加词缀**：已定位的 `TryAddChampionAffix`→`TryRollAndAddChampionAffix` 使用独立的 ChampionDataList.affixTierWeightings 及等级权重，未走本次实验词缀的 `RollSpecialAffixTier`。不能将上面的腐化公式移植到冠军词缀。冠军原生实现（`.cache/t7-special-corruption/ChampionDataList-TryRollAndAddChampionAffix.asm`）、实际配置（`.cache/t7-special-corruption/ChampionDataList.json`）
- **预腐化装备与Nemesis**：物品Corrupted结果、预腐化处理和Nemesis升阶是其他机制；没有仅因方法名含“腐化”就将它们当成巨石C的直接反例。本次不穷举其全部入口，也不据此声称它们在所有情形都与巨石腐化无关。一个已确认的最终实验词缀反例已足以否定“任何情况下都不影响”。

## 来源完整性

可随仓库查看的对象hash、关键常数、调用链及T7计算表见[冻结证据](../analysis/t7-corruption-effects-evidence.json)。

当前 `GameAssembly.dll` SHA-256：`d5f9fb458f0e9878e697a92b590a586a52fd77e645f8bf87bb4f2b74c6c56567`。当前 `PermaLoad.bundle` SHA-256：`7fac4caacd757f5f821f0e5c15f6eccf573aa8ebf89d3f464d124dc2e72ac93c`。

RandomEncounterData、ChampionDataList、8个特殊预言奖励、8个BossLoot对象及MasterAffixesList共 **19个对象**，均从当前bundle以 `parse_as_dict(check_read=True)` 完整复读，与缓存逐项相等。对象pathID、CAB名、字节数及原始负载SHA-256见 evidence.json（`.cache/t7-special-corruption/evidence.json`）。关键除数1000／400／2750也直接核对了当前DLL的float字节。复现脚本为 mine.py（`.cache/t7-special-corruption/mine.py`）、verify_evidence.py（`.cache/t7-special-corruption/verify_evidence.py`）；Cpp2IL仅用于签名、字段布局及枚举，不把其存根方法体当作实现。
