# 普通崇高预言的真实装备与职业词缀池

研究日期：2026-10-17（日本时间）。研究对象是本机 Last Epoch **1.5.2.2**，Steam build **25816319** 的游戏配置及 native 代码。没有启动游戏或采样掉落。本文件只建立可计算输入；概率值由另行实现的枚举模型负责。

## 交付及范围

可随仓库使用的精简输入为[冻结词缀池](../sources/t7-equipment-pools.json)，保留全部计算字段、底材ID、职业映射及来源hash。以下缓存为本机调查材料，不参与运行和发布。

profiles.json（本机缓存 `.cache/t7-all-equipment/profiles.json`） 提供 **23 种普通装备、36 个按掉落底材职业条件化的词缀池**；每个池保留真实 typeID、classRequirement、affixEffectModifier、全部合格底材、前后缀 ID、实际 weighting、T6Compatibility 及最大效果门槛。提取脚本为 build_profiles.py（本机缓存 `.cache/t7-all-equipment/build_profiles.py`），复读验证为 verify_profiles.py（本机缓存 `.cache/t7-all-equipment/verify_profiles.py`）。

完整 PermaLoad 对象索引中，GenericEquipment=0、rarityType=Group=1、rarityGroup=Exalted=5 的预言奖励共24项：下表23种装备，另有祭坛41／奖励515。本轮按请求排除祭坛，也排除神像、冠军、实验、T7保证及首领特殊奖励。23种普通奖励全部为 itemTypeType=ID=0、ilvl=100、subType=-1；没有指定特殊 affix、职业或子职业，alwaysRequireClassCompatibility=false。Group5 的 forceExalted=true 来自实际 GetChosenRarityAndForceExalt 分支，不是从“Exalted”名字猜测。完整奖励索引（本机缓存 `.cache/t7-all-equipment/all-ordinary-exalted-reward-index.json`）、奖励完整字段（本机缓存 `.cache/t7-all-equipment/exalted-rewards.json`）、native rarity 分支（本机缓存 `.cache/t7-mining-assets/item-creation-rarity-force.asm`），RVA 0x12199A0。

## 装备种类与当前可掉落范围

MasterItemsList.disabledBaseTypesToRoll 为 [24,11]，分别为弩和拳套；这两类也没有可掉落底材，不能沿用0–24全部可选。其余下表的底材均通过 cannotDrop=false、levelRequirement≤100；复核结果还同时满足普通效果 Default=0、非腐化、非legacy、无额外 itemTags、无子职业限制。所有这些普通装备 maximumAffixes=4。MasterItemsList（本机缓存 `.cache/t7-mining-assets/MasterItemsList.json`），pathID 331809119198608226；getAcceptableSubType native（本机缓存 `.cache/t7-all-equipment/getAcceptableSubType.asm`），RVA 0x11CE530，特别是0x11CE7C0–0x11CE7CE。

中文部位和底材名只引用现有[冻结词库](../sources/tool-catalog.json)作显示，不用它代替本机池、职业限制或权重。职业中文名为显示别名，计算以枚举数值及英文键为准。

| typeID | 部位 | 底材 classRequirement | 可掉落底材数 | affixEffectModifier | 普通预言ID |
|---:|---|---|---:|---:|---:|
| 0 | 头盔 | Primalist1／Mage2／Sentinel4／Acolyte8／Rogue16 | 65 | 0 | 100 |
| 1 | 胸甲 | Primalist1／Mage2／Sentinel4／Acolyte8／Rogue16 | 65 | 0.5 | 101 |
| 2 | 腰带 | 通用0 | 10 | 0 | 102 |
| 3 | 靴子 | 通用0 | 11 | 0 | 103 |
| 4 | 手套 | 通用0 | 11 | 0 | 104 |
| 5 | 单手斧 | 通用0 | 12 | 0.75 | 105 |
| 6 | 匕首 | 通用0 | 11 | 0.75 | 106 |
| 7 | 单手锤 | 通用0 | 11 | 0.75 | 107 |
| 8 | 权杖 | 通用0 | 9 | 0.75 | 108 |
| 9 | 单手剑 | 通用0 | 11 | 0.75 | 109 |
| 10 | 魔杖 | 通用0 | 11 | 0.75 | 110 |
| 12 | 双手斧 | 通用0 | 12 | 2.20000005 | 112 |
| 13 | 双手锤 | 通用0 | 10 | 2.20000005 | 113 |
| 14 | 双手长矛 | 通用0 | 13 | 2.20000005 | 114 |
| 15 | 双手长杖 | 通用0 | 14 | 2.20000005 | 115 |
| 16 | 双手剑 | 通用0 | 10 | 2.20000005 | 116 |
| 17 | 箭袋 | 通用0 | 9 | 0 | 117 |
| 18 | 盾牌 | 通用0 | 14 | 0.170000002 | 118 |
| 19 | 副手法器 | 通用0 | 13 | 0.170000002 | 119 |
| 20 | 护身符 | 通用0 | 10 | 0.170000002 | 120 |
| 21 | 戒指 | 通用0 | 10 | 0 | 121 |
| 22 | 遗物 | 通用0／Primalist1／Mage2／Sentinel4／Acolyte8／Rogue16 | 48 | 0 | 122 |
| 23 | 弓 | Rogue16 | 11 | 0.75 | 123 |

ItemList.GetEquipmentSubItemAndAffixEffectModifier 先取 BaseEquipmentItem.affixEffectModifier；只有 OmenIdol subtype 才覆盖为 Omen 效果。本轮合格装备 subtype 均为 Default，所以同一部位／职业内，底材效果与词缀池相同。无需为概率计算假设这些底材等权；对这些条件池，底材权重如何分布不改变结果。native（本机缓存 `.cache/t7-all-equipment/GetEquipmentSubItemAndAffixEffectModifier.asm`），RVA 0x1224E30，读基底0x1224EF9，Omen覆盖0x1224F8F。

## 职业下拉的准确含义

可以独立选择“物品种类”和“**掉落底材职业**”。准确的映射是：头盔／胸甲允许五职业；遗物允许通用及五职业；弓仅Rogue；其余19类仅通用。JSON的 classSelector.allowedCombinations 给出每个合法组合对应的 profile ID。不能把“掉落底材职业”无提示改称“玩家职业”。MasterItemsList（本机缓存 `.cache/t7-mining-assets/MasterItemsList.json`） 的每个 subItems.classRequirement；ItemList 枚举（本机缓存 `.cache/t7-all-equipment/types/ItemList.decompiled.cs`）。

普通预言并不保证只产生玩家职业的底材：其 alwaysRequireClassCompatibility=false；SpawnItemsForPlayer 在0x121BBCE仍调用 rollRandomlyRequiresClassCompatibility，后者在全局等级值≥50的分支只做0.8f的兼容投掷（10–49为0.9，低于10为true）。getAcceptableSubType 再按实际玩家职业筛选，也有多次重试后的放宽路径。TryRollEquipmentSubtype 还会额外抽底材并选择更高等级者。因此不能直接按五职业等权、底材数量占比或“80%自己+20%其他”合并。若需要“某玩家职业获得的所有普通预言装备”无条件概率，必须另枚举上述分支与底材升级；本JSON没有伪造这种混合权重。SpawnItemsForPlayer（本机缓存 `.cache/t7-all-equipment/SpawnItemsForPlayer.asm`），RVA0x121B5C0；兼容投掷（本机缓存 `.cache/t7-all-equipment/rollRandomlyRequiresClassCompatibility.asm`），RVA0x11D18E0；底材选择（本机缓存 `.cache/t7-all-equipment/getAcceptableSubType.asm`）；升级选择（本机缓存 `.cache/t7-all-equipment/GenerateItems-TryRollEquipmentSubtype.asm`），RVA0x11CCF90。

词缀职业限制使用掉落底材的 classRequirement，而非直接使用玩家职业：IsValidAffix 在0x11C2FC8读取 EquipmentItem+0x40，再交给 Affix.CanRollOn。两个枚举位不同：装备 None=0、Primalist=1、Mage=2、Sentinel=4、Acolyte=8、Rogue=16；词缀 ClassSpecificity.None=0 表示不限，NonSpecific=1只匹配通用，其他五职业位分别为2、4、8、16、32。精确匹配逻辑已按 MatchesSpecificity native 实现，不能直接拿两个数相与。IsValidAffix（本机缓存 `.cache/t7-native/IsValidAffix.asm`），RVA0x11C2F60；CanRollOn（本机缓存 `.cache/t7-native/CanRollOn.asm`），RVA0x11B11A0；MatchesSpecificity（本机缓存 `.cache/t7-all-equipment/EpochExtensions-MatchesSpecificity.asm`），RVA0x10E2FA0。

| 条件池 | classRequirement | 底材数 | 前缀数 | 后缀数 | 自然T6受限ID |
|---|---:|---:|---:|---:|---|
| 头盔·野蛮人 | 1 | 13 | 44 | 18 | 无 |
| 头盔·法师 | 2 | 11 | 39 | 19 | 无 |
| 头盔·守卫 | 4 | 12 | 40 | 18 | 无 |
| 头盔·侍祭 | 8 | 14 | 41 | 19 | 无 |
| 头盔·游侠 | 16 | 15 | 49 | 18 | 无 |
| 胸甲·野蛮人 | 1 | 12 | 44 | 16 | 7、10、13、17、19、24、45 |
| 胸甲·法师 | 2 | 12 | 42 | 17 | 7、10、13、17、19、24、45 |
| 胸甲·守卫 | 4 | 12 | 41 | 16 | 7、10、13、17、19、24、45、656 |
| 胸甲·侍祭 | 8 | 14 | 44 | 17 | 7、10、13、17、19、24、45 |
| 胸甲·游侠 | 16 | 15 | 50 | 16 | 7、10、13、17、19、24、45 |
| 腰带 | 0 | 10 | 19 | 20 | 无 |
| 靴子 | 0 | 11 | 7 | 17 | 无 |
| 手套 | 0 | 11 | 19 | 21 | 无 |
| 单手斧 | 0 | 12 | 22 | 24 | 无 |
| 匕首 | 0 | 11 | 22 | 21 | 无 |
| 单手锤 | 0 | 11 | 20 | 17 | 无 |
| 权杖 | 0 | 9 | 26 | 19 | 无 |
| 单手剑 | 0 | 11 | 22 | 23 | 无 |
| 魔杖 | 0 | 11 | 15 | 15 | 无 |
| 双手斧 | 0 | 12 | 22 | 27 | 427 |
| 双手锤 | 0 | 10 | 20 | 20 | 427 |
| 双手长矛 | 0 | 13 | 21 | 25 | 427 |
| 双手长杖 | 0 | 14 | 25 | 19 | 无 |
| 双手剑 | 0 | 10 | 21 | 25 | 427 |
| 箭袋 | 0 | 9 | 15 | 18 | 无 |
| 盾牌 | 0 | 14 | 9 | 18 | 7、10、13、17、19、24、45 |
| 副手法器 | 0 | 13 | 15 | 13 | 7、10、13、17、19、24 |
| 护身符 | 0 | 10 | 34 | 18 | 7、10、13、17、19、24、45 |
| 戒指 | 0 | 10 | 25 | 17 | 无 |
| 遗物·通用 | 0 | 3 | 28 | 14 | 无 |
| 遗物·野蛮人 | 1 | 9 | 34 | 14 | 无 |
| 遗物·法师 | 2 | 9 | 30 | 14 | 无 |
| 遗物·守卫 | 4 | 9 | 32 | 14 | 无 |
| 遗物·侍祭 | 8 | 9 | 32 | 14 | 无 |
| 遗物·游侠 | 16 | 9 | 29 | 14 | 无 |
| 弓 | 16 | 11 | 15 | 17 | 无 |

以上池只用 specialAffixType=Standard=0、levelRequirement≤100、canRollOn含当前 EquipmentType 且职业匹配的实际词缀。普通装备的 canRollOn 无需神像 subtype group 特例；GetSubTypeGroup 对29／30以外返回None，而本轮type仅0–23。权重取第一个当前equipmentType的 specificRerollChances.weighting，否则取 weighting；不能全设1。JSON共1665个profile-affix行，其中132行使用部位权重覆盖。MasterAffixesList（本机缓存 `.cache/t7-mining-assets/MasterAffixesList.json`），pathID 2955332227439360059；GetWeighting（本机缓存 `.cache/t7-all-equipment/Affix-GetWeighting.asm`），RVA0x11B2D00；GetSubTypeGroup（本机缓存 `.cache/t7-all-equipment/SubTypeGroupExtensionMethods-GetSubTypeGroup.asm`），RVA0x1246750。

## T6Compatibility与强制崇高的计算边界

普通词缀中的特殊配置只有九项：7／10／13／17／19／24／45七种抗性为 MaximumAffixEffectModifier=2、上限0；427“Less Bonus Damage Taken from Critical Strikes”和656“Sentinel Endurance While Warpathing”为 Incompatible=1。前者七抗性仍可在胸甲／盾／法器／护符池中被选为低阶，不能从初始池删掉；只是自然RollTier的T6/T7路径受效果门槛限制。法器没有物理抗性45。427只在双手斧／锤／长矛／剑；656只在守卫胸甲。其余 Normal=0。MasterAffixesList（本机缓存 `.cache/t7-mining-assets/MasterAffixesList.json`） 对应字段；RollTier（本机缓存 `.cache/t7-all-equipment/GenerateItems-RollTier.asm`），RVA0x11CA480，门槛0x11CA7DC–0x11CA805。

自然兼容判定不能擅自应用到所有后处理。forceExalted 在镜片后从完整已有词缀列表抽一条，抽到已有≥T6即停；若初抽低阶不兼容则按原生成顺序寻找首个 Normal=0替补。native 的Maximum分支仍读初抽定义，不是候选，因此不是“首个满足其自身最大门槛的候选”。没有替补时仍继续改初抽项；找到已有T7替补也没有再检查tier，可能重新写为T6/T7。排序与前后缀身份、兼容类型必须保留，不能照搬戒指的无序池压缩。此处已与既有force核查（本机缓存 `.cache/t7-mining-force/findings.md`）交叉核对；本轮native副本（本机缓存 `.cache/t7-all-equipment/GenerateItems-RollAffixes.asm`），RVA0x11C6D5F–0x11C6FE5。

## 证据完整性

PermaLoad.bundle：`7fac4caacd757f5f821f0e5c15f6eccf573aa8ebf89d3f464d124dc2e72ac93c`。GameAssembly.dll：`d5f9fb458f0e9878e697a92b590a586a52fd77e645f8bf87bb4f2b74c6c56567`。两份主数据库和23个普通奖励，共25个对象，均重新从当前bundle以UnityPy parse_as_dict(check_read=True)完整读取，逐项与导出数据相等；没有只凭奖励名字推断。每个对象的pathID、CAB名、字节数与原始负载SHA-256见asset-evidence.json（本机缓存 `.cache/t7-all-equipment/asset-evidence.json`）。原始bundle的路径及当前安装版本也已保留。

Cpp2IL反编译文件只用于签名、字段offset及枚举，不把其空方法体视为实现；关键行为逐条读取上述同一SHA的native代码。有限枚举与静态配置核验不等于游戏客户端实测。冻结词库、已有过滤器和生成策略均未修改。
