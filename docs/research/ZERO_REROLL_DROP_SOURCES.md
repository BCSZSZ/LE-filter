# 旧通用保护池：10件随机掉落且 reroll 为0的来源核查

核查日期：2026-10-18。范围仅为旧159种装备／套装池中这10件，不改变保护名单、生成器或BD需求。机器可读证据见[本次来源记录](../../sources/zero-reroll-drop-sources-2026-10-18.json)。

这10件均能世界随机掉落，均不属于Boss专属。此次逐一打开的Tunklab物品详情均明确列出 `Random Drop`、`No reroll chance`、`common`；没有列出命名Boss的定向来源。已有LETools version152数据库中的随机池字段与之相同，而且这10个ID均未出现在其 `monsterItemDrops` 定向记录中。这里的结论是“可世界随机掉落，因此并非Boss专属”，不表示Boss击杀后的普通随机掉落绝不可能产出它们。[Tunklab逐项来源见下表；LETools发布数据](https://www.lastepochtools.com/data/version152/db/js/8e688d145b13a6e9719c917369f90558.js)

| ID | 物品与本次读取的详情页 | 可世界随机掉落 | 随机池reroll | 命名Boss定向记录 | 详情中的时间线奖励节点 |
|---:|---|---|---:|---|---|
| 13 | [泰坦之心／Titan Heart](https://lastepoch.tunklab.com/unique/titan_heart) | 是 | 0% | 未列出 | Blood, Frost, and Death：暗金／套装胸甲节点 |
| 77 | [蜂农烟熏器／Apiarist's Smoker](https://lastepoch.tunklab.com/unique/apiarists_smoker) | 是 | 0% | 未列出 | The Stolen Lance：暗金／套装法杖或法器节点 |
| 78 | [蜂农防护服／Apiarist's Suit](https://lastepoch.tunklab.com/unique/apiarists_suit) | 是 | 0% | 未列出 | Blood, Frost, and Death：暗金／套装胸甲节点 |
| 79 | [蜂农梳／Apiarist's Comb](https://lastepoch.tunklab.com/unique/apiarists_comb) | 是 | 0% | 未列出 | Reign of Dragons：暗金／套装斧、锤或长柄节点 |
| 296 | [被抹灭者的降临／Advent of the Erased](https://lastepoch.tunklab.com/unique/advent_of_the_erased) | 是 | 0% | 未列出 | Spirits of Fire：暗金／套装鞋节点 |
| 311 | [誊录錾剑／Transcriber's Graver](https://lastepoch.tunklab.com/unique/transcribers_graver) | 是 | 0% | 未列出 | Reign of Dragons：暗金／套装剑或匕首节点 |
| 422 | [瓶中闪电／Lightning in a Bottle](https://lastepoch.tunklab.com/unique/lightning_in_a_bottle) | 是 | 0% | 未列出 | Fall of the Empire：暗金／套装腰带节点 |
| 460 | [劳普的足迹／Laup's Path](https://lastepoch.tunklab.com/unique/laups_path) | 是 | 0% | 未列出 | The Last Ruin：暗金／套装遗物节点 |
| 474 | [融合元素／Fused Elements](https://lastepoch.tunklab.com/unique/fused_elements) | 是 | 0% | 未列出 | The Last Ruin：暗金／套装遗物节点 |
| 480 | [险境映像／Perilous Reflection](https://lastepoch.tunklab.com/unique/perilous_reflection) | 是 | 0% | 未列出 | The Black Sun：暗金／套装盾牌节点 |

因此，按照玩家本轮提出的五类，这10件均进入第2类“世界随机掉落且reroll为0”。其中7暗金、3套装；三件套装均属蜂农套装。表中的时间线名字来自“指定类型的暗金／套装奖励节点”，不能把它解释成该时间线Boss专属掉落。十页也都列有升华符文、茧化物品结果等来源；它们是可获得该成品的途径，与成品本身是否为“茧化物品”是两件事。[Tunklab蜂农套装与来源](https://lastepoch.tunklab.com/unique/apiarists_smoker)、[泰坦之心来源](https://lastepoch.tunklab.com/unique/titan_heart)

296是编织者意志暗金，页面明确标注Weaver's Will。这不影响其“世界随机、reroll为0”的来源分类，但后续若调整通用0LP名单，应同时核查现有独立WW保护规则，不把来源分类直接当作最终隐藏效果。[Tunklab被抹灭者的降临](https://lastepoch.tunklab.com/unique/advent_of_the_erased)

## 证据与核验边界

- 10个Tunklab详情页在本次研究中通过网页工具逐一读取。公开元数据的 `canDropRandomly=true`、`rerollChance=0` 与已冻结的[2026-10-18 reroll快照](../../sources/tunklab-unique-reroll-2026-10-18.json)一致。这里只作来源分类；未复测各来源百分比，表中不采用这些百分比作为判定。
- LETools对照使用此前已经取得的version152发布数据库。原始JS位于 `.cache/ice-heartseeker-db-8e688d145b13a6e9719c917369f90558.js`，SHA-256为 `8a0293233b168b1eb425d7a9490bf7ad26f0d33f445fe2f5a3f0704432ee4cc5`；解码JSON为 `.cache/ice-heartseeker-db.json`，SHA-256为 `b9f44fb8f44b8b1d455539c3bb11c47a53fc39e9933dadd53280f5669d4fe37e`。该数据库的341条 `monsterItemDrops` 覆盖105个UniqueID，这10件均无对应行。它的10条Unique记录全部为 `canDropRandomly=1`、`rerollChance=0`、`isCocoonedItem=0`。[LETools原数据URL](https://www.lastepochtools.com/data/version152/db/js/8e688d145b13a6e9719c917369f90558.js)
- 本次再次直接访问LETools发布JS返回403，网页工具也无法读取其物品搜索页，故不把LETools缓存对照表述成“本次实时抓取成功”。当前结论有10个本次实际读取的Tunklab详情页直接支持。
- “未列出定向来源”单独不足以证明所有特殊途径均不存在；“明确可世界随机掉落”足以排除Boss专属。本报告不据此推断其他先古、茧化或限定来源物品。
- 未执行远程JavaScript，也未作游戏客户端掉落实测。
