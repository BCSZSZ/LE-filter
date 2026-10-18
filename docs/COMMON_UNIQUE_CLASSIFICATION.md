# 旧通用暗金名单：五类掉落来源核查

2026-10-18按玩家订正：①②③④仅以非套装暗金为对象，套装全部单独保留。新口径已落实到[当前生成器名单](COMMON_UNIQUE_PROTECTION.md)。

这里分类旧138种暗金，包含前置T0／BD会覆盖的ID；旧21件套装移出编号分类，当前套装规则覆盖全部61件／24套。独立的10种暗金神像与先驱者之针344不在本表内。旧暗金来自Raxx选择与三个赛季追加，并非统一的稀有度筛选。

## 分类结果

| 类别 | 暗金数量 | 当前处理 |
|---|---:|---|
| 1．茧化物品 | 23 | 保留 |
| 2．世界随机掉落且reroll=0 | 7 | 移出通用池 |
| 3．Boss／裂隙野兽定向来源，非世界随机 | 60 | 保留 |
| 4．世界随机掉落且reroll>0 | 47 | 保留 |
| 5．其他限定奖励 | 1 | 保留 |

五类互斥合计138种暗金。第③类将裂隙野兽及其谱系奖励作为限定Boss体系统计；它不表示只能由一个有名字的Boss掉落，也不排除兑换、编织回响等奖励途径。进化终焉444在这里随裂隙体系列入③，若按‘结束流程奖励’列入⑤，只会改变分类数量，不改变保留结论。

**第③、⑤类的页面reroll通常显示‘－’，不能写成页面显示0%。** 已读取底层数据的reroll字段为0，但因为不进世界随机池，这个字段不用于衡量其定向稀有度。‘只删世界随机且0’必须同时判断`canDropRandomly`，不能直接删所有原始`rerollChance=0`的ID。[Tunklab主表](https://lastepoch.tunklab.com/uniques)

## 世界随机reroll为0：只计7暗金，蜂农套装另行保留

此前10件包括7暗金、3蜂农套装。套装77／78／79已从②移出，仍由全部套装规则保护。7暗金详情均明确世界随机、无reroll，不是Boss专属；指定类型奖励节点不等于该时间线Boss专属。原始10件交叉核查作为历史证据保留在[专项来源报告](research/ZERO_REROLL_DROP_SOURCES.md)。

## 先古与特殊来源的修正

旧名单包含全部25种先古暗金。官方1.3初版说明是22种可兑换、3种仅裂隙野兽掉落；**官方1.3.2又明确让此前仅可购买的先古暗金也能由裂隙野兽掉落**。因此，Tunklab部分详情页只写‘Not random drop’，不能据此归为仅商店兑换。本报告将25种全部归入③，保留兑换作为额外来源。[官方1.3初版](https://forum.lastepoch.com/t/last-epoch-beneath-ancient-skies-patch-notes/78635/2)、[官方1.3.2修正](https://forum.lastepoch.com/t/last-epoch-patch-1-3-2-notes/79385)

③的60种可再分为34种其他限定Boss来源、25种先古暗金、1种进化终焉444。进化终焉的谱系结束奖励由官方说明支持；Tunklab该页仅写非随机。⑤只剩酿酒大师的皮带扣416，来源是完成The Grand Brewery保证奖励，页面将其记为回响完成掉落，故单列；该回响本身要求击败酿酒师。[官方谱系说明](https://forum.lastepoch.com/t/last-epoch-beneath-ancient-skies-patch-notes/78635/2)、[腰带详情](https://lastepoch.tunklab.com/unique/brewmasters_buckle)、[回响完成奖励](https://lastepoch.tunklab.com/echo/the_grand_brewery)

例如乌凯罗斯的扭曲之心216同时有Emperor of Corpses及编织回响完成奖励，所以本文使用‘Boss定向来源’，不把‘有Boss来源’写成‘无任何其他获取途径’。[216实际来源](https://lastepoch.tunklab.com/unique/twisted_heart_of_uhkeiros)

## 已落实的‘只移出②、补齐④’，套装独立

- 旧138暗金移出②的7种后，保留131种。茧化及所有旧非世界随机来源均保留。
- ④在全部可见非套装暗金装备中共有97种。旧名单只覆盖47种，还差50种。
- 补齐50种后，暗金池181种；套装独立保留全部61件，不按reroll筛选。基础池合计242个物品ID，不是XML规则数量，默认Strict仍96条。
- 3个正reroll暗金神像：奇点246、自然之怒462、焦土485，仍归独立暗金神像类别；六件T0仍由独立最高提示保护。
- 从通用名单移出不等于最终隐藏。BD明确目标、套装补全、更高LP及WW规则可能继续保留相同物品；例如296属于WW暗金。

## 1．茧化物品：23种

| ID | 名称／详情 | 类别 | reroll／状态 | 来源核查 |
|---:|---|---|---|---|
| 379 | [茧化短剑 · Cocooned Short Sword](https://lastepoch.tunklab.com/unique/cocooned_short_sword) | 暗金 | 主表隐藏（茧化） | 茧化容器；不以其可能开出的成品分类 |
| 380 | [茧化斧 · Cocooned Cleaver](https://lastepoch.tunklab.com/unique/cocooned_cleaver) | 暗金 | 主表隐藏（茧化） | 茧化容器；不以其可能开出的成品分类 |
| 381 | [茧化棍棒 · Cocooned Club](https://lastepoch.tunklab.com/unique/cocooned_club) | 暗金 | 主表隐藏（茧化） | 茧化容器；不以其可能开出的成品分类 |
| 382 | [茧化巨剑 · Cocooned Great Sword](https://lastepoch.tunklab.com/unique/cocooned_great_sword) | 暗金 | 主表隐藏（茧化） | 茧化容器；不以其可能开出的成品分类 |
| 383 | [茧化巨斧 · Cocooned Great Axe](https://lastepoch.tunklab.com/unique/cocooned_great_axe) | 暗金 | 主表隐藏（茧化） | 茧化容器；不以其可能开出的成品分类 |
| 384 | [茧化巨锤 · Cocooned Great Mace](https://lastepoch.tunklab.com/unique/cocooned_great_mace) | 暗金 | 主表隐藏（茧化） | 茧化容器；不以其可能开出的成品分类 |
| 385 | [茧化长矛 · Cocooned Spear](https://lastepoch.tunklab.com/unique/cocooned_spear) | 暗金 | 主表隐藏（茧化） | 茧化容器；不以其可能开出的成品分类 |
| 386 | [茧化长杖 · Cocooned Staff](https://lastepoch.tunklab.com/unique/cocooned_staff) | 暗金 | 主表隐藏（茧化） | 茧化容器；不以其可能开出的成品分类 |
| 387 | [茧化胸甲 · Cocooned Cuirass](https://lastepoch.tunklab.com/unique/cocooned_cuirass) | 暗金 | 主表隐藏（茧化） | 茧化容器；不以其可能开出的成品分类 |
| 388 | [茧化匕首 · Cocooned Dagger](https://lastepoch.tunklab.com/unique/cocooned_dagger) | 暗金 | 主表隐藏（茧化） | 茧化容器；不以其可能开出的成品分类 |
| 389 | [茧化权杖 · Cocooned Sceptre](https://lastepoch.tunklab.com/unique/cocooned_sceptre) | 暗金 | 主表隐藏（茧化） | 茧化容器；不以其可能开出的成品分类 |
| 390 | [茧化魔杖 · Cocooned Wand](https://lastepoch.tunklab.com/unique/cocooned_wand) | 暗金 | 主表隐藏（茧化） | 茧化容器；不以其可能开出的成品分类 |
| 391 | [茧化弓 · Cocooned Bow](https://lastepoch.tunklab.com/unique/cocooned_bow) | 暗金 | 主表隐藏（茧化） | 茧化容器；不以其可能开出的成品分类 |
| 392 | [茧化箭袋 · Cocooned Quiver](https://lastepoch.tunklab.com/unique/cocooned_quiver) | 暗金 | 主表隐藏（茧化） | 茧化容器；不以其可能开出的成品分类 |
| 393 | [茧化盾牌 · Cocooned Shield](https://lastepoch.tunklab.com/unique/cocooned_shield) | 暗金 | 主表隐藏（茧化） | 茧化容器；不以其可能开出的成品分类 |
| 394 | [茧化法器 · Cocooned Catalyst](https://lastepoch.tunklab.com/unique/cocooned_catalyst) | 暗金 | 主表隐藏（茧化） | 茧化容器；不以其可能开出的成品分类 |
| 395 | [茧化遗物 · Cocooned Relic](https://lastepoch.tunklab.com/unique/cocooned_relic) | 暗金 | 主表隐藏（茧化） | 茧化容器；不以其可能开出的成品分类 |
| 396 | [茧化戒指 · Cocooned Ring](https://lastepoch.tunklab.com/unique/cocooned_ring) | 暗金 | 主表隐藏（茧化） | 茧化容器；不以其可能开出的成品分类 |
| 397 | [茧化护身符 · Cocooned Amulet](https://lastepoch.tunklab.com/unique/cocooned_amulet) | 暗金 | 主表隐藏（茧化） | 茧化容器；不以其可能开出的成品分类 |
| 398 | [茧化手套 · Cocooned Gloves](https://lastepoch.tunklab.com/unique/cocooned_gloves) | 暗金 | 主表隐藏（茧化） | 茧化容器；不以其可能开出的成品分类 |
| 399 | [茧化腰带 · Cocooned Belt](https://lastepoch.tunklab.com/unique/cocooned_belt) | 暗金 | 主表隐藏（茧化） | 茧化容器；不以其可能开出的成品分类 |
| 400 | [茧化靴子 · Cocooned Boots](https://lastepoch.tunklab.com/unique/cocooned_boots) | 暗金 | 主表隐藏（茧化） | 茧化容器；不以其可能开出的成品分类 |
| 401 | [茧化头盔 · Cocooned Helmet](https://lastepoch.tunklab.com/unique/cocooned_helmet) | 暗金 | 主表隐藏（茧化） | 茧化容器；不以其可能开出的成品分类 |

## 2．世界随机掉落且reroll=0：7种

| ID | 名称／详情 | 类别 | reroll／状态 | 来源核查 |
|---:|---|---|---|---|
| 13 | [泰坦之心 · Titan Heart](https://lastepoch.tunklab.com/unique/titan_heart) | 暗金 | 0% | 世界随机；reroll 0% |
| 296 | [被抹灭者的降临 · Advent of the Erased](https://lastepoch.tunklab.com/unique/advent_of_the_erased) | 暗金 | 0% | 世界随机；reroll 0% |
| 311 | [誊录錾剑 · Transcriber's Graver](https://lastepoch.tunklab.com/unique/transcribers_graver) | 暗金 | 0% | 世界随机；reroll 0% |
| 422 | [瓶中闪电 · Lightning in a Bottle](https://lastepoch.tunklab.com/unique/lightning_in_a_bottle) | 暗金 | 0% | 世界随机；reroll 0% |
| 460 | [劳普的足迹 · Laup's Path](https://lastepoch.tunklab.com/unique/laups_path) | 暗金 | 0% | 世界随机；reroll 0% |
| 474 | [融合元素 · Fused Elements](https://lastepoch.tunklab.com/unique/fused_elements) | 暗金 | 0% | 世界随机；reroll 0% |
| 480 | [险境映像 · Perilous Reflection](https://lastepoch.tunklab.com/unique/perilous_reflection) | 暗金 | 0% | 世界随机；reroll 0% |

## 3．Boss／裂隙野兽定向来源，非世界随机：60种

| ID | 名称／详情 | 类别 | reroll／状态 | 来源核查 |
|---:|---|---|---|---|
| 175 | [全能 · Omnis](https://lastepoch.tunklab.com/unique/omnis) | 暗金 | 非随机，显示－ | Shade of Orobyss |
| 179 | [暮色巨口 · Apathy's Maw](https://lastepoch.tunklab.com/unique/apathys_maw) | 暗金 | 非随机，显示－ | Shade of Orobyss |
| 180 | [破碎锁链 · Shattered Chains](https://lastepoch.tunklab.com/unique/shattered_chains) | 暗金 | 非随机，显示－ | Shade of Orobyss |
| 216 | [乌凯罗斯的扭曲之心 · Twisted Heart of Uhkeiros](https://lastepoch.tunklab.com/unique/twisted_heart_of_uhkeiros) | 暗金 | 非随机，显示－ | Emperor of Corpses；另有编织回响完成奖励 |
| 253 | [山之麓 · Foot of the Mountain](https://lastepoch.tunklab.com/unique/foot_of_the_mountain) | 暗金 | 非随机，显示－ | Stone Titan's Heart |
| 254 | [山之貌 · Face of the Mountain](https://lastepoch.tunklab.com/unique/face_of_the_mountain) | 暗金 | 非随机，显示－ | Stone Titan's Heart |
| 255 | [山之核 · Core of the Mountain](https://lastepoch.tunklab.com/unique/core_of_the_mountain) | 暗金 | 非随机，显示－ | Stone Titan's Heart |
| 256 | [山之巅 · Peak of the Mountain](https://lastepoch.tunklab.com/unique/peak_of_the_mountain) | 暗金 | 非随机，显示－ | Stone Titan's Heart |
| 258 | [献祭者的奉献 · Immolator's Oblation](https://lastepoch.tunklab.com/unique/immolators_oblation) | 暗金 | 非随机，显示－ | Fire Lich Cremorus |
| 339 | [混沌黑刃 · Black Blade of Chaos](https://lastepoch.tunklab.com/unique/black_blade_of_chaos) | 暗金 | 非随机，显示－ | Harbinger of Chaos、Aberroth、Herald of Oblivion；另有编织回响完成奖励 |
| 345 | [凛冬克星 · Bane of Winter](https://lastepoch.tunklab.com/unique/bane_of_winter) | 暗金 | 非随机，显示－ | Aberroth、Harbinger of Tyranny、Herald of Oblivion；另有编织回响完成奖励 |
| 347 | [天命 · The Inevitable](https://lastepoch.tunklab.com/unique/the_inevitable) | 暗金 | 非随机，显示－ | Harbinger of Fear、Aberroth、Herald of Oblivion；另有编织回响完成奖励 |
| 353 | [虚无 · Nihilis](https://lastepoch.tunklab.com/unique/nihilis) | 暗金 | 非随机，显示－ | Aberroth、Herald of Oblivion |
| 354 | [空无之墙 · Wall of Nothing](https://lastepoch.tunklab.com/unique/wall_of_nothing) | 暗金 | 非随机，显示－ | Harbinger of Treason、Aberroth、Herald of Oblivion；另有编织回响完成奖励 |
| 355 | [阿波罗斯的命令 · Aberroth's Command](https://lastepoch.tunklab.com/unique/aberroths_command) | 暗金 | 非随机，显示－ | Aberroth、Harbinger of Defilement、Herald of Oblivion；另有编织回响完成奖励 |
| 357 | [无界树种 · Seed of Ekkidrasil](https://lastepoch.tunklab.com/unique/seed_of_ekkidrasil) | 暗金 | 非随机，显示－ | Aberroth、Herald of Oblivion |
| 358 | [失效征兆 · Null Portent](https://lastepoch.tunklab.com/unique/null_portent) | 暗金 | 非随机，显示－ | Aberroth、Herald of Oblivion |
| 361 | [相位点 · Phase Point](https://lastepoch.tunklab.com/unique/phase_point) | 暗金 | 非随机，显示－ | Harbinger of Pride、Aberroth、Herald of Oblivion；另有编织回响完成奖励 |
| 364 | [事件视界 · Event Horizon](https://lastepoch.tunklab.com/unique/event_horizon) | 暗金 | 非随机，显示－ | Aberroth、Harbinger of Destruction、Herald of Oblivion；另有编织回响完成奖励 |
| 365 | [世界分离者 · World Splitter](https://lastepoch.tunklab.com/unique/world_splitter) | 暗金 | 非随机，显示－ | Aberroth、Harbinger of Hatred、Herald of Oblivion；另有编织回响完成奖励 |
| 366 | [午夜烈焰 · Flames of Midnight](https://lastepoch.tunklab.com/unique/flames_of_midnight) | 暗金 | 非随机，显示－ | Aberroth、Harbinger of Ash、Herald of Oblivion；另有编织回响完成奖励 |
| 367 | [天界末日 · Celestial Doom](https://lastepoch.tunklab.com/unique/celestial_doom) | 暗金 | 非随机，显示－ | Harbinger of War、Aberroth、Herald of Oblivion；另有编织回响完成奖励 |
| 403 | [山之魂 · Soul of the Mountain](https://lastepoch.tunklab.com/unique/soul_of_the_mountain) | 暗金 | 非随机，显示－ | Draal Queen |
| 411 | [玛加莎的面容 · Countenance of Majasa](https://lastepoch.tunklab.com/unique/countenance_of_majasa) | 暗金 | 非随机，显示－ | Goddess of Blood |
| 413 | [破碎世界 · Shattered Worlds](https://lastepoch.tunklab.com/unique/shattered_worlds) | 暗金 | 非随机，显示－ | Herald of Oblivion |
| 415 | [不朽台钳 · Immortal Vise](https://lastepoch.tunklab.com/unique/immortal_vise) | 暗金 | 非随机，显示－ | Herald of Oblivion |
| 417 | [克洛托的针刺 · Clotho's Needle](https://lastepoch.tunklab.com/unique/clothos_needle) | 暗金 | 非随机，显示－ | Fateweaver Clotho |
| 423 | [传奇交织 · Legends Entwined](https://lastepoch.tunklab.com/unique/legends_entwined) | 暗金 | 非随机，显示－ | Rift Beast（官方1.3.2已补全）；部分另可兑换 |
| 424 | [暴君颅骨 · Tyrant's Skull](https://lastepoch.tunklab.com/unique/tyrants_skull) | 暗金 | 非随机，显示－ | Rift Beast（官方1.3.2已补全）；部分另可兑换 |
| 425 | [野火余烬 · Wildfire Embers](https://lastepoch.tunklab.com/unique/wildfire_embers) | 暗金 | 非随机，显示－ | Rift Beast（官方1.3.2已补全）；部分另可兑换 |
| 426 | [眩光棘林 · Thicket of Blinding Light](https://lastepoch.tunklab.com/unique/thicket_of_blinding_light) | 暗金 | 非随机，显示－ | Rift Beast（官方1.3.2已补全）；部分另可兑换 |
| 427 | [原初谐律 · Harmony of the First](https://lastepoch.tunklab.com/unique/harmony_of_the_first) | 暗金 | 非随机，显示－ | Rift Beast（官方1.3.2已补全）；部分另可兑换 |
| 428 | [棘影猛攻 · Onslaught of Cerata](https://lastepoch.tunklab.com/unique/onslaught_of_cerata) | 暗金 | 非随机，显示－ | Rift Beast（官方1.3.2已补全）；部分另可兑换 |
| 429 | [不朽石之花 · Blossom of Immortal Stone](https://lastepoch.tunklab.com/unique/blossom_of_immortal_stone) | 暗金 | 非随机，显示－ | Rift Beast（官方1.3.2已补全）；部分另可兑换 |
| 430 | [阿努洛克的合唱 · Chorus of the Anurok](https://lastepoch.tunklab.com/unique/chorus_of_the_anurok) | 暗金 | 非随机，显示－ | Rift Beast（官方1.3.2已补全）；部分另可兑换 |
| 431 | [创世残骸 · Carrion of Creation](https://lastepoch.tunklab.com/unique/carrion_of_creation) | 暗金 | 非随机，显示－ | Rift Beast（官方1.3.2已补全）；部分另可兑换 |
| 432 | [骨火之角 · Horn of the Bone Wisp](https://lastepoch.tunklab.com/unique/horn_of_the_bone_wisp) | 暗金 | 非随机，显示－ | Rift Beast（官方1.3.2已补全）；部分另可兑换 |
| 433 | [神圣巢穴 · Reliquary Nest](https://lastepoch.tunklab.com/unique/reliquary_nest) | 暗金 | 非随机，显示－ | Rift Beast（官方1.3.2已补全）；部分另可兑换 |
| 434 | [冷漠面具 · Mask of Indifference](https://lastepoch.tunklab.com/unique/mask_of_indifference) | 暗金 | 非随机，显示－ | Rift Beast（官方1.3.2已补全）；部分另可兑换 |
| 435 | [原识永存 · Permanence of Primal Knowledge](https://lastepoch.tunklab.com/unique/permanence_of_primal_knowledge) | 暗金 | 非随机，显示－ | Rift Beast（官方1.3.2已补全）；部分另可兑换 |
| 436 | [纷争之翼 · Wings of Discord](https://lastepoch.tunklab.com/unique/wings_of_discord) | 暗金 | 非随机，显示－ | Rift Beast（官方1.3.2已补全）；部分另可兑换 |
| 437 | [原始节奏 · Primal Cadence](https://lastepoch.tunklab.com/unique/primal_cadence) | 暗金 | 非随机，显示－ | Rift Beast（官方1.3.2已补全）；部分另可兑换 |
| 438 | [磨石木槌 · Whetstone Gavel](https://lastepoch.tunklab.com/unique/whetstone_gavel) | 暗金 | 非随机，显示－ | Rift Beast（官方1.3.2已补全）；部分另可兑换 |
| 439 | [真视玻璃 · Truesight Glass](https://lastepoch.tunklab.com/unique/truesight_glass) | 暗金 | 非随机，显示－ | Rift Beast（官方1.3.2已补全）；部分另可兑换 |
| 440 | [蓝羽绑带 · Bluefeather Band](https://lastepoch.tunklab.com/unique/bluefeather_band) | 暗金 | 非随机，显示－ | Rift Beast（官方1.3.2已补全）；部分另可兑换 |
| 441 | [多头蛇弧光 · Hydra Arc](https://lastepoch.tunklab.com/unique/hydra_arc) | 暗金 | 非随机，显示－ | Rift Beast（官方1.3.2已补全）；部分另可兑换 |
| 442 | [维洛西恩之颌 · Velocyn's Jaw](https://lastepoch.tunklab.com/unique/velocyns_jaw) | 暗金 | 非随机，显示－ | Rift Beast（官方1.3.2已补全）；部分另可兑换 |
| 444 | [进化终焉 · Evolution's End](https://lastepoch.tunklab.com/unique/evolutions_end) | 暗金 | 非随机，显示－ | Rift Beast：结束谱系奖励（官方补丁说明） |
| 445 | [灵体木质部 · Spirit Xylem](https://lastepoch.tunklab.com/unique/spirit_xylem) | 暗金 | 非随机，显示－ | Rift Beast（官方1.3.2已补全）；部分另可兑换 |
| 446 | [狂战士之牙 · Fangs of the Berserker](https://lastepoch.tunklab.com/unique/fangs_of_the_berserker) | 暗金 | 非随机，显示－ | Rift Beast（官方1.3.2已补全）；部分另可兑换 |
| 447 | [先祖集群之骨 · Bones of the Ancestral Pack](https://lastepoch.tunklab.com/unique/bones_of_the_ancestral_pack) | 暗金 | 非随机，显示－ | Rift Beast（官方1.3.2已补全）；部分另可兑换 |
| 448 | [星血筑师 · Architects of Astral Blood](https://lastepoch.tunklab.com/unique/architects_of_astral_blood) | 暗金 | 非随机，显示－ | Rift Beast（官方1.3.2已补全）；部分另可兑换 |
| 449 | [屠夫冠冕 · The Butcher's Crown](https://lastepoch.tunklab.com/unique/the_butchers_crown) | 暗金 | 非随机，显示－ | Rift Beast（官方1.3.2已补全）；部分另可兑换 |
| 469 | [流亡 · Exulis](https://lastepoch.tunklab.com/unique/exulis) | 暗金 | 非随机，显示－ | Vision of the Observer |
| 470 | [毁灭之眼 · Oculus of Ruin](https://lastepoch.tunklab.com/unique/oculus_of_ruin) | 暗金 | 非随机，显示－ | Vision of the Observer |
| 472 | [赫罗特的憩息 · Heorot's Repose](https://lastepoch.tunklab.com/unique/heorots_repose) | 暗金 | 非随机，显示－ | Morditas |
| 477 | [不息狂怒 · Unsated Rage](https://lastepoch.tunklab.com/unique/unsated_rage) | 暗金 | 非随机，显示－ | Morditas |
| 479 | [抵御元素 · Withstand the Elements](https://lastepoch.tunklab.com/unique/withstand_the_elements) | 暗金 | 非随机，显示－ | Morditas |
| 487 | [囚禁之迹 · Vestige of Imprisonment](https://lastepoch.tunklab.com/unique/vestige_of_imprisonment) | 暗金 | 非随机，显示－ | God of Bloodshed |
| 488 | [莫迪塔斯的复仇 · Morditas' Vengeance](https://lastepoch.tunklab.com/unique/morditas_vengeance) | 暗金 | 非随机，显示－ | God of Bloodshed |

## 4．世界随机掉落且reroll>0：47种

| ID | 名称／详情 | 类别 | reroll／状态 | 来源核查 |
|---:|---|---|---|---|
| 35 | [雷恩之眼 · Eye of Reen](https://lastepoch.tunklab.com/unique/eye_of_reen) | 暗金 | 70% | 世界随机；reroll 70% |
| 45 | [莫迪塔斯的领域 · Morditas' Reach](https://lastepoch.tunklab.com/unique/morditas_reach) | 暗金 | 80% | 世界随机；reroll 80% |
| 53 | [瑞耶的光翼 · Rahyeh's Light](https://lastepoch.tunklab.com/unique/rahyehs_light) | 暗金 | 80% | 世界随机；reroll 80% |
| 61 | [奥利安之眼 · Orian's Eye](https://lastepoch.tunklab.com/unique/orians_eye) | 暗金 | 97% | 世界随机；reroll 97% |
| 84 | [终末游牧民的传家宝 · Heirloom of the Last Nomad](https://lastepoch.tunklab.com/unique/heirloom_of_the_last_nomad) | 暗金 | 70% | 世界随机；reroll 70% |
| 91 | [火龙靴 · Fiery Dragon Shoes](https://lastepoch.tunklab.com/unique/fiery_dragon_shoes) | 暗金 | 70% | 世界随机；reroll 70% |
| 92 | [丛林女王的储物腰带 · Jungle Queen's Chaps of Holding](https://lastepoch.tunklab.com/unique/jungle_queens_chaps_of_holding) | 暗金 | 90% | 世界随机；reroll 90% |
| 125 | [大海无量 · Oceareon](https://lastepoch.tunklab.com/unique/oceareon) | 暗金 | 85% | 世界随机；reroll 85% |
| 126 | [死亡之握 · Mortality's Grasp](https://lastepoch.tunklab.com/unique/mortalitys_grasp) | 暗金 | 70% | 世界随机；reroll 70% |
| 149 | [全视 · Omnividence](https://lastepoch.tunklab.com/unique/omnividence) | 暗金 | 90% | 世界随机；reroll 90% |
| 167 | [渡鸦的崛起 · Ravens' Rise](https://lastepoch.tunklab.com/unique/ravens_rise) | 暗金 | 80% | 世界随机；reroll 80% |
| 169 | [艾尔冈的庇护 · Aergon's Refuge](https://lastepoch.tunklab.com/unique/aergons_refuge) | 暗金 | 75% | 世界随机；reroll 75% |
| 172 | [松鼠使者 · Herald of the Scurry](https://lastepoch.tunklab.com/unique/herald_of_the_scurry) | 暗金 | 70% | 世界随机；reroll 70% |
| 176 | [奥罗拉的沙漏 · Aurora's Time Glass](https://lastepoch.tunklab.com/unique/auroras_time_glass) | 暗金 | 80% | 世界随机；reroll 80% |
| 183 | [利维坦刻刀 · Leviathan Carver](https://lastepoch.tunklab.com/unique/leviathan_carver) | 暗金 | 70% | 世界随机；reroll 70% |
| 187 | [血上加霜 · Salt the Wound](https://lastepoch.tunklab.com/unique/salt_the_wound) | 暗金 | 85% | 世界随机；reroll 85% |
| 195 | [伊泰拉的天平 · Scales of Eterra](https://lastepoch.tunklab.com/unique/scales_of_eterra_fire_cold) | 暗金 | 70% | 世界随机；reroll 70% |
| 196 | [伊泰拉的天平 · Scales of Eterra](https://lastepoch.tunklab.com/unique/scales_of_eterra_cold_lightning) | 暗金 | 70% | 世界随机；reroll 70% |
| 197 | [伊泰拉的天平 · Scales of Eterra](https://lastepoch.tunklab.com/unique/scales_of_eterra_fire_lightning) | 暗金 | 70% | 世界随机；reroll 70% |
| 198 | [荣誉堡垒 · Bastion of Honour](https://lastepoch.tunklab.com/unique/bastion_of_honour) | 暗金 | 90% | 世界随机；reroll 90% |
| 208 | [贪婪虚空 · Ravenous Void](https://lastepoch.tunklab.com/unique/ravenous_void) | 暗金 | 98% | 世界随机；reroll 98% |
| 220 | [死亡之拥 · Death's Embrace](https://lastepoch.tunklab.com/unique/deaths_embrace) | 暗金 | 85% | 世界随机；reroll 85% |
| 221 | [草木皆兵 · Paranoia](https://lastepoch.tunklab.com/unique/paranoia) | 暗金 | 90% | 世界随机；reroll 90% |
| 232 | [哈卡尔的凤凰 · Hakar's Phoenix](https://lastepoch.tunklab.com/unique/hakars_phoenix) | 暗金 | 70% | 世界随机；reroll 70% |
| 235 | [森之蕨叶 · Silvafrond](https://lastepoch.tunklab.com/unique/silvafrond) | 暗金 | 70% | 世界随机；reroll 70% |
| 272 | [亚伦的意志 · Aaron's Will](https://lastepoch.tunklab.com/unique/aarons_will) | 暗金 | 75% | 世界随机；reroll 75% |
| 277 | [阿特拉里亚的红戒指 · Red Ring of Atlaria](https://lastepoch.tunklab.com/unique/red_ring_of_atlaria) | 暗金 | 98% | 世界随机；reroll 98% |
| 310 | [错乱折跃 · Wrongwarp](https://lastepoch.tunklab.com/unique/wrongwarp) | 暗金 | 80% | 世界随机；reroll 80% |
| 318 | [朝暮轮转 · The Shattered Cycle](https://lastepoch.tunklab.com/unique/the_shattered_cycle) | 暗金 | 72% | 世界随机；reroll 72% |
| 327 | [被抹灭者的圣餐仪式 · Communion of the Erased](https://lastepoch.tunklab.com/unique/communion_of_the_erased) | 暗金 | 70% | 世界随机；reroll 70% |
| 335 | [幽灵领主的港湾 · Wraithlord's Harbour](https://lastepoch.tunklab.com/unique/wraithlords_harbour) | 暗金 | 35% | 世界随机；reroll 35% |
| 336 | [纳奥的牙齿 · Naal's Tooth](https://lastepoch.tunklab.com/unique/naals_tooth) | 暗金 | 80% | 世界随机；reroll 80% |
| 337 | [剃刀降临 · Razorfall](https://lastepoch.tunklab.com/unique/razorfall) | 暗金 | 80% | 世界随机；reroll 80% |
| 420 | [处刑者的献祭 · Executioner's Tithe](https://lastepoch.tunklab.com/unique/executioners_tithe) | 暗金 | 50% | 世界随机；reroll 50% |
| 443 | [肌肤大军 · Army of Skin](https://lastepoch.tunklab.com/unique/army_of_skin) | 暗金 | 25% | 世界随机；reroll 25% |
| 450 | [不屈冲锋 · Unbroken Charge](https://lastepoch.tunklab.com/unique/unbroken_charge) | 暗金 | 70% | 世界随机；reroll 70% |
| 458 | [朝暮足袋 · Tabi of Dusk and Dawn](https://lastepoch.tunklab.com/unique/tabi_of_dusk_and_dawn) | 暗金 | 30% | 世界随机；reroll 30% |
| 459 | [毁灭机巧 · Artifice of Devastation](https://lastepoch.tunklab.com/unique/artifice_of_devastation) | 暗金 | 30% | 世界随机；reroll 30% |
| 461 | [灰烬觉醒 · Ash Wake](https://lastepoch.tunklab.com/unique/ash_wake) | 暗金 | 30% | 世界随机；reroll 30% |
| 463 | [瑞耶之拥 · Rahyeh's Embrace](https://lastepoch.tunklab.com/unique/rahyehs_embrace) | 暗金 | 50% | 世界随机；reroll 50% |
| 471 | [不屈军团 · Unbroken Legion](https://lastepoch.tunklab.com/unique/unbroken_legion) | 暗金 | 20% | 世界随机；reroll 20% |
| 473 | [永恒之池 · Eternal Font](https://lastepoch.tunklab.com/unique/eternal_font) | 暗金 | 99.8% | 世界随机；reroll 99.8% |
| 475 | [吞噬知识 · Devoured Knowledge](https://lastepoch.tunklab.com/unique/devoured_knowledge) | 暗金 | 20% | 世界随机；reroll 20% |
| 476 | [死亡之舞 · Death Dance](https://lastepoch.tunklab.com/unique/death_dance) | 暗金 | 99.9% | 世界随机；reroll 99.9% |
| 478 | [幻灵赠礼 · Gift of the Eidolon](https://lastepoch.tunklab.com/unique/gift_of_the_eidolon) | 暗金 | 99.9% | 世界随机；reroll 99.9% |
| 483 | [牧人的纪念品 · Wrangler's Keepsake](https://lastepoch.tunklab.com/unique/wranglers_keepsake) | 暗金 | 50% | 世界随机；reroll 50% |
| 484 | [奔放誓言 · Effusive Oath](https://lastepoch.tunklab.com/unique/effusive_oath) | 暗金 | 20% | 世界随机；reroll 20% |

## 5．其他限定奖励：1种

| ID | 名称／详情 | 类别 | reroll／状态 | 来源核查 |
|---:|---|---|---|---|
| 416 | [酿酒大师的皮带扣 · Brewmaster's Buckle](https://lastepoch.tunklab.com/unique/brewmasters_buckle) | 暗金 | 非随机，显示－ | 完成The Grand Brewery的保证奖励 |

## ④本轮补入的50种暗金

| ID | 名称／详情 | 类别 | reroll／状态 | 来源核查 |
|---:|---|---|---|---|
| 11 | [大失血 · Exsanguinous](https://lastepoch.tunklab.com/unique/exsanguinous) | 暗金 | 50% | 世界随机；reroll 50% |
| 30 | [无可争议 · Undisputed](https://lastepoch.tunklab.com/unique/undisputed) | 暗金 | 90% | 世界随机；reroll 90% |
| 37 | [灰烬之歌 · Cinder Song](https://lastepoch.tunklab.com/unique/cinder_song) | 暗金 | 25% | 世界随机；reroll 25% |
| 38 | [炼金术士的勺子 · Alchemist's Ladle](https://lastepoch.tunklab.com/unique/alchemists_ladle) | 暗金 | 50% | 世界随机；reroll 50% |
| 66 | [空心手指 · Hollow Finger](https://lastepoch.tunklab.com/unique/hollow_finger) | 暗金 | 20% | 世界随机；reroll 20% |
| 71 | [瓦尔迪尔的圣餐杯 · Valdyr's Chalice](https://lastepoch.tunklab.com/unique/valdyrs_chalice) | 暗金 | 60% | 世界随机；reroll 60% |
| 73 | [瘟疫载体的长杖 · Plague Bearer's Staff](https://lastepoch.tunklab.com/unique/plague_bearers_staff) | 暗金 | 50% | 世界随机；reroll 50% |
| 76 | [莉亚丝的图章 · Liath's Signet](https://lastepoch.tunklab.com/unique/liaths_signet) | 暗金 | 50% | 世界随机；reroll 50% |
| 80 | [鲜血重击 · Bloodgeon](https://lastepoch.tunklab.com/unique/bloodgeon) | 暗金 | 50% | 世界随机；reroll 50% |
| 93 | [克莫德的囚笼 · Kermode's Cage](https://lastepoch.tunklab.com/unique/kermodes_cage) | 暗金 | 20% | 世界随机；reroll 20% |
| 104 | [苏洛隆的脚步 · Suloron's Step](https://lastepoch.tunklab.com/unique/sulorons_step) | 暗金 | 60% | 世界随机；reroll 60% |
| 108 | [梅尔文的令状 · Melvern's Writ](https://lastepoch.tunklab.com/unique/melverns_writ) | 暗金 | 60% | 世界随机；reroll 60% |
| 132 | [短暂休息 · Transient Rest](https://lastepoch.tunklab.com/unique/transient_rest) | 暗金 | 30% | 世界随机；reroll 30% |
| 133 | [西塔拉的谜团 · Xithara's Conundrum](https://lastepoch.tunklab.com/unique/xitharas_conundrum) | 暗金 | 30% | 世界随机；reroll 30% |
| 136 | [烟雾编织者 · Smoke Weaver](https://lastepoch.tunklab.com/unique/smoke_weaver) | 暗金 | 50% | 世界随机；reroll 50% |
| 145 | [生命轮回 · Life's Journey](https://lastepoch.tunklab.com/unique/lifes_journey) | 暗金 | 50% | 世界随机；reroll 50% |
| 147 | [祈雨之舞 · Raindance](https://lastepoch.tunklab.com/unique/raindance) | 暗金 | 65% | 世界随机；reroll 65% |
| 168 | [原初者的飞翔 · Flight of the First](https://lastepoch.tunklab.com/unique/flight_of_the_first) | 暗金 | 50% | 世界随机；reroll 50% |
| 181 | [玛丽娜的失落灵魂 · Marina's Lost Soul](https://lastepoch.tunklab.com/unique/marinas_lost_soul) | 暗金 | 30% | 世界随机；reroll 30% |
| 222 | [棱镜凝视 · Prismatic Gaze](https://lastepoch.tunklab.com/unique/prismatic_gaze) | 暗金 | 60% | 世界随机；reroll 60% |
| 224 | [审判者 · The Judicator](https://lastepoch.tunklab.com/unique/the_judicator) | 暗金 | 60% | 世界随机；reroll 60% |
| 229 | [维斯拉塞尔的根须 · Roots of Vithrasil](https://lastepoch.tunklab.com/unique/roots_of_vithrasil) | 暗金 | 40% | 世界随机；reroll 40% |
| 242 | [影弦 · Shadow String](https://lastepoch.tunklab.com/unique/shadow_string) | 暗金 | 60% | 世界随机；reroll 60% |
| 249 | [迪奥塔恩的血腥羽毛笔 · Diothaen's Bloody Nib](https://lastepoch.tunklab.com/unique/diothaens_bloody_nib) | 暗金 | 50% | 世界随机；reroll 50% |
| 250 | [托克瑞芬的饥渴 · Torkrefin's Hunger](https://lastepoch.tunklab.com/unique/torkrefins_hunger) | 暗金 | 50% | 世界随机；reroll 50% |
| 251 | [泽乌尔的狩猎 · Zeurial's Hunt](https://lastepoch.tunklab.com/unique/zeurials_hunt) | 暗金 | 20% | 世界随机；reroll 20% |
| 252 | [断绝契约 · Pact Severance](https://lastepoch.tunklab.com/unique/pact_severance) | 暗金 | 50% | 世界随机；reroll 50% |
| 268 | [血腥守护者的巢穴 · Bloodkeeper's Nest](https://lastepoch.tunklab.com/unique/bloodkeepers_nest) | 暗金 | 60% | 世界随机；reroll 60% |
| 269 | [双纽线天平 · Scales of Lemniscate](https://lastepoch.tunklab.com/unique/scales_of_lemniscate) | 暗金 | 50% | 世界随机；reroll 50% |
| 270 | [虫巢意识 · Hive Mind](https://lastepoch.tunklab.com/unique/hive_mind) | 暗金 | 60% | 世界随机；reroll 60% |
| 274 | [神圣枝芽 · Branch of Hallows](https://lastepoch.tunklab.com/unique/branch_of_hallows) | 暗金 | 50% | 世界随机；reroll 50% |
| 275 | [不稳定核心 · Unstable Core](https://lastepoch.tunklab.com/unique/unstable_core) | 暗金 | 50% | 世界随机；reroll 50% |
| 290 | [叛教者的圣所 · Apostate's Sanctuary](https://lastepoch.tunklab.com/unique/apostates_sanctuary) | 暗金 | 64% | 世界随机；reroll 64% |
| 304 | [静电之壳 · Static Shell](https://lastepoch.tunklab.com/unique/static_shell) | 暗金 | 40% | 世界随机；reroll 40% |
| 306 | [流亡者之血 · Blood of the Exile](https://lastepoch.tunklab.com/unique/blood_of_the_exile) | 暗金 | 50% | 世界随机；reroll 50% |
| 307 | [团结之徽 · Crest of Unity](https://lastepoch.tunklab.com/unique/crest_of_unity) | 暗金 | 30% | 世界随机；reroll 30% |
| 316 | [思维巅峰 · Apex of Thought](https://lastepoch.tunklab.com/unique/apex_of_thought) | 暗金 | 40% | 世界随机；reroll 40% |
| 323 | [折磨之轮 · Wheel of Torment](https://lastepoch.tunklab.com/unique/wheel_of_torment) | 暗金 | 50% | 世界随机；reroll 50% |
| 332 | [鲜血鸟栖 · Blood Roost](https://lastepoch.tunklab.com/unique/blood_roost) | 暗金 | 60% | 世界随机；reroll 60% |
| 334 | [英勇利爪 · Talons of Valor](https://lastepoch.tunklab.com/unique/talons_of_valor) | 暗金 | 20% | 世界随机；reroll 20% |
| 338 | [剑刃捕手 · Sword Catcher](https://lastepoch.tunklab.com/unique/sword_catcher) | 暗金 | 60% | 世界随机；reroll 60% |
| 342 | [叛徒之舌 · Traitor's Tongue](https://lastepoch.tunklab.com/unique/traitors_tongue) | 暗金 | 60% | 世界随机；reroll 60% |
| 351 | [电光石火 · Triboelectra](https://lastepoch.tunklab.com/unique/triboelectra) | 暗金 | 30% | 世界随机；reroll 30% |
| 356 | [影匿 · Stealth](https://lastepoch.tunklab.com/unique/stealth) | 暗金 | 60% | 世界随机；reroll 60% |
| 368 | [魔力向导 · Mana Guide](https://lastepoch.tunklab.com/unique/mana_guide) | 暗金 | 30% | 世界随机；reroll 30% |
| 373 | [掠夺者飞镖 · Ravager's Dart](https://lastepoch.tunklab.com/unique/ravagers_dart) | 暗金 | 20% | 世界随机；reroll 20% |
| 374 | [猪猡的珍珠 · Pearls of the Swine](https://lastepoch.tunklab.com/unique/pearls_of_the_swine_blood) | 暗金 | 40% | 世界随机；reroll 40% |
| 375 | [猪猡的珍珠 · Pearls of the Swine](https://lastepoch.tunklab.com/unique/pearls_of_the_swine_fire) | 暗金 | 40% | 世界随机；reroll 40% |
| 376 | [猪猡的珍珠 · Pearls of the Swine](https://lastepoch.tunklab.com/unique/pearls_of_the_swine_poison) | 暗金 | 40% | 世界随机；reroll 40% |
| 414 | [正义陨落 · Downfall of the Righteous](https://lastepoch.tunklab.com/unique/downfall_of_the_righteous) | 暗金 | 20% | 世界随机；reroll 20% |

## 证据、复现与边界

- [完整结构化分类](../analysis/common-unique-classification.json)：138个旧暗金ID各出现一次，五类数量、50个新增与181个现行暗金ID完整保留，套装独立计数。
- [本次来源快照](../sources/common-unique-drop-sources-2026-10-18.json)：214个比较ID的详情URL、先古标记、旧LETools定向来源记录，以及本次读取的84个非随机／茧化详情页来源片段和原HTML哈希。
- [原reroll快照](../sources/tunklab-unique-reroll-2026-10-18.json)与[10件专项证据](../sources/zero-reroll-drop-sources-2026-10-18.json)：不以详情页缺少来源为唯一判据；先古与谱系补充以官方补丁说明为准。LETools为已取得的version152缓存，本轮重取403，不冒称实时取得。
- 离线重建：`python -X utf8 scripts/classify_common_unique_protection.py`。脚本只写本分类报告与对应analysis JSON；生成器另读已确认的冻结名单。
- 这是XML名单事实、数据库来源与官方说明的研究，没有作游戏客户端掉落实测；reroll百分比不是物品的全局掉落概率。
