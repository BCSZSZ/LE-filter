# 求索镜片与暗金预言概率

核查日期：2026-10-19；游戏版本1.5.2.2。本文是本机游戏资源与原生指令的静态分析，不是游戏客户端掉落实验。只为暗金选择器补充固定参考信息，不扩展筛选开关、职业场景、套装预言或裂隙野兽计算器。

## 结论与统一口径

求索镜片对应英文 **Lens Of Curiosity**、`ProphecySlot.LensType.Curiosity = 7`。本机英文／中文本地化共同使用键 `Item_Names.Item_SubType_Name_109_7`。命运8级解锁；本次沿用100级、命运12、忽略职业偏置的同类型通用池，每件普通暗金预言奖励各算一次，不累计额外奖励次数。[本次原生证据](../../sources/curiosity-lens-native-evidence-2026-10-19.json)、[原有掉落模型](UNIQUE_PICKER_DROP_DATA.md)

镜片压缩的是同池每个物品的接受权重，而非把目标的最终概率乘某个固定倍数。令原始拒绝重抽概率为 `r`：

```text
e = 0.800000011920929             # 序列化游戏字段的float值
w = 1-r
w_curiosity = clamp(w^e, 0, 1)   # 对r<1；r≥1保留原值
r_curiosity = 1-w_curiosity
```

同一池所有ID都要变换，再用原来有限重抽算法归一化。求索改变普通预言奖励中的暗金身份分布，不增加所有世界掉落的暗金概率；它也不把Boss限定或先古物品加入随机池。[原生证据](../../sources/curiosity-lens-native-evidence-2026-10-19.json)；[官方1.5镜片说明](https://lastepoch.com/1-5/patchnotes/#lenses)将Curiosity描述为压缩Unique／Set权重，红戒变常见、Kestrel变少见。

## 原生调用与参数

游戏`GameAssembly.dll` SHA-256为 `d5f9fb458f0e9878e697a92b590a586a52fd77e645f8bf87bb4f2b74c6c56567`。Cpp2IL只用来定位方法、字段和枚举；以下行为来自实际DLL指令，不采用其空方法体作为实现。[冻结指令与字段摘录](../../sources/curiosity-lens-native-evidence-2026-10-19.json)

| 原生证据 | 行为 |
|---|---|
| `ProphecyData`，PermaLoad.bundle PathID3864826814730378121 | 序列化`curiosityLensUniqueWeightDilutionExponent`为0.800000011920929，与构造函数0x20A9C1B写入0x3F4CCCCD一致；并非只读默认值。 |
| `BuildLensRollModifiers` RVA0x20B0DD0；实际switch表0x20B1080 | 枚举7跳至0x20B0F6C，检查Unique或Set稀有度，写`compressUniqueAndSetWeights=true`和上述指数。没有排除神像部位。 |
| `UniqueList.ApplyUniqueWeightCompression` RVA0x126E1A0 | 对`1-r`求幂、限0至1，再转回拒绝率；无镜片、未启用压缩、r≥1时保留原值。 |
| `UniqueList.rollUnique` RVA0x1270F10 | 在循环中内联相同压缩。预言路径`failOnReroll=false`，因此压缩后的拒绝率参与重抽。重抽仍有60次上限。 |
| `SpawnRewardForPlayer`→`spawnSpecificItemAtPoint`→`initialiseRandomItemData`→`RollBaseItem` | 同一镜片modifier最终传入rollUnique；Unique稀有度7和Set稀有度8共用该分支。GetItemType先选类型的过程不读取此modifier。 |

Tunklab原始发布代码的压缩函数也为`1-Math.pow(1-r,e)`，其发布参数为`.8`；仅作旁证，数值以本机资源为准。相关原始片段和SHA-256已冻结，不执行远程JavaScript。[该站镜片页](https://lastepoch.tunklab.com/item/lens_of_curiosity)、[该站参数源码](https://lastepoch.tunklab.com/_next/static/chunks/24lkeki6rom7u.js)、[该站压缩函数源码](https://lastepoch.tunklab.com/_next/static/chunks/22kpwgh7gfu9v.js)

## 有限重抽与独立复算

池中有N个有效ID，变换后拒绝率为rᵢ，q为它们的平均值。先均匀提议一个ID，拒绝后重新均匀提议。允许60次拒绝；第61个候选不再检验、直接接受。因此无镜片和求索都使用：

```text
P(i) = (1-rᵢ)/N × Σ(q^k, k=0…59) + q^60/N
```

这与既有`scripts/build_unique_drop_catalog.py`的`reroll_distribution`一致。增加求索只需变换该函数的整池输入。无穷重抽近似`wᵢ/Σw`不保留最后强制接受项，不能代替上述原生有限公式；`w^e/w`也只是提议接受权重之比，不是最终掉率之比。[原有模型与证据](UNIQUE_PICKER_DROP_DATA.md)、[本次复算记录](../../sources/curiosity-lens-native-evidence-2026-10-19.json)

下表由独立逐轮概率传播复算，并与闭式公式对照；概率分母仍为对应普通暗金预言的每件奖励。使用原生float参数的解析值，不宣称模拟了每条CPU浮点运算的舍入。

| 物品 | 同类型池大小 | 无镜片 | 求索镜片 | 倍率 |
|---|---:|---:|---:|---:|
| 死亡之舞476 | 21 | 0.006848757830% | 0.025947122103% | 3.788588 |
| 红戒277 | 16 | 0.165699925129% | 0.351643152617% | 2.122168 |
| 奥利安之眼61 | 18 | 0.234521354046% | 0.455438027253% | 1.941990 |

例如死亡之舞原始reroll为0.9990000128746033；求索后拒绝率约0.9960189696261188。不能把99.9%或0.3981%的接受权重直接显示为该靴子的最终预言掉率。[冻结输入](../../sources/unique-drop-inputs-2026-10-18.json)、[复算记录](../../sources/curiosity-lens-native-evidence-2026-10-19.json)

## 神像、套装和正reroll边界

当前世界随机非套装中有100个正reroll物品。求索展示值可为这些物品全部附带，但必须保留神像的两步抽取：先按原生重复类型列表`[25,30,33,32,33,30,29]`选择baseType，然后在该类型内部压缩并重抽。镜片不改变第一步的尺寸占比。[原有神像原生证据](UNIQUE_PICKER_DROP_DATA.md#暗金神像与套装)、[本次modifier传递证据](../../sources/curiosity-lens-native-evidence-2026-10-19.json)

正reroll神像只有246、462、485。其中奇点246和485各是其类型的唯一有效ID，求索前后都为1/7，即约14.285714%；权重上升不能让只有一个候选的条件概率超过1。462从约12.698412672%变为13.013983690%。这些同值或小幅提升仍可照实显示。

原生镜片同样支持Set，但普通Unique预言不生成套装。本轮不把套装加进Unique分母，也不为套装、Boss或先古物品虚构“普通暗金预言＋求索”数值。正reroll本身不能越过随机掉落资格、稀有度、等级或类型范围。[原有池构造](UNIQUE_PICKER_DROP_DATA.md)、[本次证据](../../sources/curiosity-lens-native-evidence-2026-10-19.json)

## 屠夫冠冕449

449是先古头盔：`isPrimordialItem=1`、`canDropRandomly=0`，原始reroll=0也不使它进入世界暗金预言池。它有固定兑换成本：20先古尖牙、40先古犄角、20000远古骨骼。[冻结原生物品字段](../../sources/unique-drop-inputs-2026-10-18.json)、[本次449摘录](../../sources/curiosity-lens-native-evidence-2026-10-19.json)

“无固定掉率”是未指定野兽条件下没有一个统一百分比，**不表示没有掉落来源或无法获取**。官方1.3.2将原先只能购买的先古物品也加入裂隙野兽掉落，并明确机会随有效进化数、与兑换材料对应的奖励材料量、腐化和命运Boss奖励加成改变。该更新还修正命运Boss奖励加成对仅掉落先古的适用。[官方1.3.2说明](https://forum.lastepoch.com/t/last-epoch-patch-1-3-2-notes/79385)

普通暗金模型缺少这只野兽的进化状态、奖励材料及其数量、腐化和实际奖励加成，不能用449的reroll=0或“1/25先古”推定掉率。本轮适宜的静态信息是“裂隙野兽／先古材料兑换”及固定兑换成本；不为此增加设置。这里没有完成裂隙野兽的独立全链路概率模型，不能将仅掉落先古的`TryGetDropOnlyUnique`分支直接套给可兑换的449。

## 与已有T7计算器的关系

现有`/probability/`及`scripts/build_prophecy_probability.py`计算崇高装备的词缀阶数、身份池和镜片升阶；它们没有计算指定暗金ID。暗金选择器已有独立原生Unique模型，本次求索继续用该模型、同一有限重抽函数与冻结输入计算，不能称为从T7页面直接调用出来。两者可共享“依据原生代码、离线精确枚举／解析计算”的验证标准，但不是同一随机过程。[T7计算器说明](../PROPHECY_CALCULATOR.md)、[暗金模型说明](UNIQUE_PICKER_DROP_DATA.md)
