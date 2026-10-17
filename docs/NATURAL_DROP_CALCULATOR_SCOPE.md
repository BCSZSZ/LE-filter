# 普通随机掉落计算器的范围与条件化

调查日期：2026-10-17。本机 Last Epoch **1.5.2.2**，Steam build `25816319`，build hash `8dfd6929fe2d10f2e77b7ed4c8e6910f49b2736b`。本报告核对实际原生代码及已安装资产，没有启动游戏或采样掉落。基础腐化公式及自然掉落入口见 [T7_NATURAL_CORRUPTION.md](T7_NATURAL_CORRUPTION.md)。

## 可准确复现的计算范围

最小闭合范围是：**100级巨石普通随机掉落中，初次 `RollRarity` 进入普通／魔法／稀有分支（raw0–4）、最终属于所选装备类型及底材职业的装备**。初始 `forceExalted=false`，不带预言镜片；随后正常执行命运之环的词缀倍率和稀有转崇高规则。

本轮补充资产核准：在这个100级、生成前不指定类型／底材的普通随机调用中，初次暗金／套装不会通过失败替换回流。因此也可将范围表述为**该普通随机掉落来源中，所选类型及底材职业的非暗金／套装装备**。这里是先让原生流程正常选择类型，再对最终类型条件化；不是生成前强行指定类型。此等价不能推广到定向掉落、其他unique替换策略或额外来源。

必须区别下列分母：

- 所选类型的上述全部普通分支装备，包括没有词缀的普通装备及未成为崇高的装备。
- 上述装备中，最终至少有一条T6或T7、成为崇高的装备。
- 所有怪物来源或全部地面装备。这还包括额外保证稀有、冠军、实验、固定奖励等，当前范围不能代表其加权总和，也不能代表每次击杀／每小时的数量。

“恰好1T7／2T7”分别按最终有1条／2条T7计数，不能与至少1条／至少2条交换。稀有和崇高是同一生成流程的前后状态，初始raw rarity与最终物品rarity不是同一个变量。

## 活动暗金加成应默认关闭

`GenerateItems.RollRarity`（RVA `0x11C9B30`）在 `0x11C9C64`–`0x11C9C85` 读取：

`Features.events`（静态字段 `+0x58`）→`EventFeatures.BoostUniqueDrops50p`（`+0x38`）→`Feature.Enabled`（`+0x10`）。

该开关为活动功能，不是命运之环rank。`EventFeatures::.ctor`（`0x10E6290`）在 `0x10E647E` 明写Enabled=false，并在 `0x10E6492` 将该Feature放入 `events+0x38`。`Feature::.ctor` 的字段布局与metadata对应。命运之环 `ToggleRank` 的0–12区间没有写入该活动字段。

因此，**静态、无额外活动的默认计算应关闭暗金50%加成**。静态文件不能证明线上服务此刻是否开启活动；页面应将前提写为“无活动暗金加成”。

100级、暗金／套装倍率输入为1时，令 `I` 为巨石累计的increasedItemRarity：

\[
c=(0.00156+0.0073)\,[1+0.6\ln(1+I)].
\]

若开启此活动，只有暗金项变成 `1.5×0.0073`，套装项 `0.00156` 不乘1.5；不能将整个 `c` 乘1.5。原生常量为float32，公式中的小数是其名义值。

命运之环rank4的M=1.5、rank9的Q=2及rank11的稀有转崇高p=.25影响后续词缀／force流程，**不修改这里的c或普通 `RollRarity` 的raw0–4初始混合**。rank6的保证稀有强制崇高倍率用于另一来源分支，见下文。

证据缓存：`.cache/t7-natural-corruption/GenerateItems__RollRarity.asm.txt`、`.cache/t7-natural-corruption/EventFeatures__.ctor.asm.txt`、`.cache/t7-natural-corruption/Features__.cctor.asm.txt`；字段metadata反编译位于 `.cache/t7-natural-scope/`。

## 腐化与额外地图稀有度

本轮固定100级，普通腐化配置下：

\[
I=0.01\,Power(C)+I_{other},\qquad
extra=0.36I.
\]

`extra` 的整数部分与小数伯努利抽样决定普通稀有度额外抽样次数，取最大值。完整分段 `Power(C)`、阈值及CDF见自然腐化报告。

`I_other=0` 的意思是**除了腐化自带加成，没有其他回响／怪物等累积稀有度加成**，不是将全部Item Rarity归零。必须明确这是一个控制场景；真实地图的其他modifier可使相同腐化下的结果不同。固定100级也排除了普通时间线随腐化提升地区等级的通道。

## 必须按所选装备类型重新加权raw rarity

`RollBaseItem`（`0x11C7060`）先在 `0x11C7CD3` 调用 `RollRarity`，再选装备类型。`Item.rarityCanRollAsIdol`（`0x122FAE0`）只对raw2和未指定rarity=-1返回true；自然随机分支在调用前已有raw0–4，因此仅raw2允许神像分流。

关键调用：

| RVA | 行为 |
|---|---|
| `0x11C8705` | 初始forceExalted=true时直接排除神像；本轮自然初始false |
| `0x11C872D` | 用当前raw rarity调用rarityCanRollAsIdol |
| `0x11C8732` | 将结果取反，得到excludeIdols |
| `0x11C8740`／`0x11C874E` | 传入excludeIdols，调用RollBaseType |
| `0x11C8FC0` | RollBaseType：42个候选均匀取样，再按禁用、等级、职业亲和、神像规则拒绝重抽 |
| `0x11D0410` | rerollBaseType：按角色class对应的亲和掩码选择重抽概率 |
| `0x122D530` | idolRerollChance：读取全局神像重抽概率0.1 |

数据来自 `MasterItemsList`，PermaLoad pathID `331809119198608226`：42个候选类型、禁用ID11／24、全局神像重抽概率名义0.1。不能先将列表缩成23类再均匀抽，也不能将非当前职业类型全删掉。

令 `a_i` 为某类型每次被抽到后的接受概率，`A_gear` 为正常装备类型接受概率之和，`A_idols` 为神像之和。忽略下述可量化的极小重抽上限尾项时：

\[
k=\frac{A_{gear}}{A_{gear}+A_{idols}},\qquad
P(raw=n\mid type=i,ordinary)\propto
\begin{cases}k\,P(raw=2\mid ordinary),&n=2,\\P(raw=n\mid ordinary),&n\ne2.\end{cases}
\]

类型自身的 `a_i` 在分子／分母中抵消；raw2的神像分流因子不会抵消。因此，直接把类型选择前的raw0–4混合套到所选装备会产生偏差。

`A_idols=0.8820000157…`。本机float32数据得到：

| 实际掉落角色职业 | A_gear | k（省略上限尾项） |
|---|---:|---:|
| Primalist／Sentinel | 19.850000024… | 0.9574570705… |
| 法师（Mage） | 19.400000036… | 0.9565131637… |
| 侍祭（Acolyte） | 20.150000036… | 0.9580639020… |
| 游侠（Rogue） | 20.449999988… | 0.9586536651… |

**这里的职业是实际角色职业，不是掉落底材的职业归属。** 两个参数有不同含义。最小界面可以明确固定一种实际角色职业，或另外提供角色职业选择；不能用“底材职业”代替它。

RollBaseType在1000次拒绝后会返回第1001个未经验证的候选（上限门槛 `0x11C9200`）。因此精确返回概率为：

\[
P_i=\frac{a_i}{A}(1-q^{1000})+\frac{q^{1000}}{42},\qquad q=1-A/42.
\]

两个raw组分别使用有／无神像的A。严格Bayes因子因这条尾项有极小类型差异；本轮所选普通装备的差异量级小于约 `10^-267`，可在显示精度上省略，同时记录误差界。类型34–41的正常接受权重均为0，祭坛41不能用普通23类计算范围支持；上述未经验证的尾项不构成有意义的正常祭坛掉落模型。

独立复核脚本、完整42类型权重、每种角色职业和上限证据：`.cache/t7-natural-tool/type-selection.json`。该缓存是开发核查资料；运行期应使用项目冻结的验证数据，不能依赖cache路径。

## 底材职业条件对各raw组共用

`RollBaseItem` 在 `0x11C8968` 调用 `TryRollEquipmentSubtype`（`0x11CCF90`），后者在 `0x11CD065`／`0x11CD15C` 调用 `getAcceptableSubType`（`0x11CE530`）。实参为类型、等级、tags、class compatibility开关、class／subclass、词缀兼容及affix effectiveness条件；不传入raw rarity，也没有读取物品rarity。

普通随机路径的 `rollRandomlyRequiresClassCompatibility`（`0x11D18E0`）按地区等级采样兼容性：等级≥50时为名义0.8（`0x11D198E`），10–49为0.9，低于10为true；该函数不读取raw rarity。

`getAcceptableSubType` 按底材最低等级、是否禁用、游戏状态、class compatibility和tags等筛选；`TryRollEquipmentSubtype` 的较高等级底材升级抽样也只读类型配置与等级。在固定类型、100级、实际角色职业、相同调用策略下，进一步要求某一底材职业的成功因子跨raw0–4共用，所以在上述Bayes条件化中抵消。底材职业仍改变可用词缀池及后续T7概率，不能从概率工具移除。

证据缓存：`.cache/t7-corruption/RollBaseItem.asm.txt`、`.cache/t7-natural-corruption/GenerateItems__TryRollEquipmentSubtype.asm.txt`、`.cache/t7-natural-corruption/GenerateItems__getAcceptableSubType.asm.txt`、`.cache/t7-natural-corruption/GenerateItems__rollRandomlyRequiresClassCompatibility.asm.txt`。

## 额外保证稀有不是每个落点必有的步骤

静态 `ItemDrop.DropItem`（`0x1107830`）接受 `guaranteedAdditionalRare`。在 `0x1107F7C` 判该标记、在 `0x1107F8A` 判itemDropChance>0后，才进入额外保证稀有helper `'<DropItem>g__spawnRandomItemForActor|1'`（`0x112F140`）。普通随机落点lambda `'<DropItem>b__3'`（`0x1130420`）是另一个来源。

保证稀有helper在 `0x112F482`–`0x112F4B4` 选择名义70%的raw3／30%的raw4，并在 `0x112F509` 生成物品。它还在 `0x112F38D` 调用 `GetChanceForGuaranteedRareToForceExalted`（`0x1108470`）：100级基础p=.15，命运rank6再作用于此来源的force机会。不能把该来源的p=.15或其rank6倍率普遍加到普通RollRarity分支。

要输出所有怪物来源的混合概率，必须另外统计各怪物／场景的该标记、落点数量及其他奖励来源权重。当前固定普通随机分支明确排除此来源即可，不需要虚构通用权重。

## 通用暗金替换路径存在，本轮指定调用的失败回流为零

通用 `RollBaseItem` 确实存在回流路径：调用 `UniqueList.rollUnique`（`0x1270F10`，调用点 `0x11C7E7D`）返回false后，默认替换路线在 `0x11C7EC9` 做名义50%抽样，写成raw3或raw4（`0x11C7F0B`）；另一替换策略会写raw0。无效unique条目／空subItems还可经 `0x11C85A2` 路线写raw0。

不过，默认 `UniqueRerollReplacement.OtherUniqueOrSetMatchingRarity=0` 在 `0x11C7DB5`–`0x11C7DC5` 将 `failOnReroll=false` 传给rollUnique。候选池非空时，rollUnique即使反复命中暗金稀有度重抽，也在60次上限后返回一个暗金（`0x127144A`–`0x127146A`），不会因为一次“稀有暗金重抽”就掉回普通装备。候选池为空才在 `0x12712B8`–`0x12712CB` 返回false；`failOnReroll=true` 的其他策略另有返回false路径。

为核准本次普通随机来源，另从 `resources.assets` 的 **UniqueList pathID11278** 恢复并完整读取322416字节对象：489条unique，330条canDropRandomly，uniqueID无重复。330条随机掉落条目的subTypes全部非空，每个baseType／subType组合均在MasterItemsList存在。

恢复使用本机Cpp2IL dummy的字段声明生成type tree，修正工具遗漏的Unity内建 `m_Enabled` 对齐；`m_Script` 独立匹配原始资源的fileID1／pathID11455，`read_typetree(check_read=True)` 验证整个对象消费完毕。native `Entry.hasLevelRequirementAtOrBelow`（`0x125ADF0`）及 `Entry.hasClassCompatibleSubType`（`0x125AC00`）的过滤条件逐一与资产核对。

100级、未指定type／subtype、mustBeRandomDrop=true、不指定legendaryType、未要求subclass的候选数量如下：

| class compatibility | 实际角色职业 | 非套装候选 | 套装候选 |
|---|---|---:|---:|
| false | 任意 | 276 | 54 |
| true | Primalist | 236 | 46 |
| true | Mage | 238 | 44 |
| true | Sentinel | 230 | 45 |
| true | Acolyte | 234 | 43 |
| true | Rogue | 242 | 48 |

所有池非空。`UniqueList.BuildDictionary`（`0x126E230`）不按类别过滤，登记所有uniqueID；`getUnique`（`0x1270190`）按该ID返回原条目。结合默认failOnReroll=false的60次重抽上限，**本调用的rollUnique=false、无法解析ID、空subTypes三种普通fallback均不可达**。因此，先排除初次unique／set分支，在这个已核准的调用中不会漏掉失败替换进来的普通装备。

该结论只适用于生成前未限定type／subtype的100级普通随机调用。限定类型、底材、legendaryType等的其他来源可能形成空候选，`failOnReroll=true` 策略也可在非空池失败，不能无条件宣称整个游戏的暗金回流为零。

证据缓存：`.cache/t7-natural-scope/unique-fallback-audit.json`、`.cache/t7-natural-scope/audit_unique_fallback.py`、`.cache/t7-natural-scope/UniqueList.resource.json`、`.cache/t7-natural-scope/UniqueList.typetree.json`、`.cache/t7-natural-scope/extract_unique_resource.py`；native指令在 `.cache/t7-natural-corruption/UniqueList__rollUnique.asm.txt`、`.cache/t7-natural-corruption/UniqueList__BuildDictionary.asm.txt`、`.cache/t7-natural-corruption/UniqueList__getUnique.asm.txt`、`.cache/t7-corruption/RollBaseItem.asm.txt`。

## 证据身份与复核边界

- 原生实现：`GameAssembly.dll`，SHA256 `d5f9fb458f0e9878e697a92b590a586a52fd77e645f8bf87bb4f2b74c6c56567`。
- metadata：SHA256 `81ff3419726bb5cf8e4f86eace2b2df2638ec4bc6ffed8a7a5dbaf09aa6f7bed`。Cpp2IL dummy仅用于字段／签名／RVA，空方法体不是实现证据。
- `PermaLoad.bundle`：SHA256 `7fac4caacd757f5f821f0e5c15f6eccf573aa8ebf89d3f464d124dc2e72ac93c`；装备数据库对象pathID `331809119198608226`。
- `resources.assets`：SHA256 `6694168ed890fdfa7e48a857758a435d548df008788a4c24f5830230278f9684`；UniqueList pathID11278、322416字节，原始对象SHA256 `9e0b906fbd0be82beaa1f0070c64c55f30a88d82ba48ebbc8c8bd0bfa14d8516`。

这是指定版本的静态代码及资产调查。没有客户端掉落实测、线上活动状态验证、怪物来源总体加权或每小时效率结论。
