# 完整规则索引

由 scripts/analyze_filter.py 离线生成。编号按 Order+1，越小越优先；XML 物理存储顺序相反。完整字段、完整选择列表及源文件行号在 analysis/rules.json。

空词缀列表和空类型的含义见 FILTER_GUIDE.md；不能按名称推定条件。S1=None、S6=Begin 来自社区格式映射；M 为原始地图图标 ID。

| 编号 | 状态/动作 | 原始名称 | 条件（同一规则内共同满足） | 显示/提示 |
|---:|---|---|---|---|
| 1 | 说明条目/关闭 | Welcome to Raxx's Loot Filter! How to set it up: | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 2 | 说明条目/关闭 | Start at the bottom and scroll up until you see | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 3 | 说明条目/关闭 | <--- this Blue color. These are the instructions for | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 4 | 说明条目/关闭 | how to set up the rules BELOW that blue text. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 5 | 说明条目/关闭 | IF YOU EVER SEE CAPS IN A RULE, it's also an instruction. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 6 | 说明条目/关闭 | Have questions? Ask me at Twitch.tv/Raxxanterax <3 | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 7 | 说明条目/关闭 | This rule guarantees you see every Legendary. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 8 | 启用/SHOW | 显示所有传奇 | 稀有度：LEGENDARY | 保留原色；S1；M0 |
| 9 | 说明条目/关闭 | These rules Show Unique & Set Items. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 10 | 说明条目/关闭 | Make sure your BIS Uniques are shown. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 11 | 说明条目/关闭 | As you progress, make these rules more strict. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 12 | 启用/SHOW | all Uniques with 3LP or 20 WW | 稀有度：UNIQUE；LP≥3 或 WW≥20（其余边界为空） | 橙；S6；M3；强调；光柱 LARGEST/色号7 |
| 13 | 启用/SHOW | all Uniques with 2LP / 17 WW (UNCHECK UNWANTED) | 稀有度：UNIQUE；指定暗金/套装 412 项；见 SELECTED_UNIQUES.md；roll 边界为空或 0–255；LP≥2 或 WW≥17（其余边界为空） | 保留原色；S1；M0 |
| 14 | 启用/SHOW | all Uniques with 1LP / 14 WW (UNCHECK UNWANTED) | 稀有度：UNIQUE；指定暗金/套装 412 项；见 SELECTED_UNIQUES.md；roll 边界为空或 0–255；LP≥1 或 WW≥14（其余边界为空） | 保留原色；S1；M0 |
| 15 | 启用/SHOW | Rarest Uniques at LP0 (ADD BUILD SPECIFIC RARE UNIQUES) | 指定暗金/套装 143 项；见 SELECTED_UNIQUES.md；roll 边界为空或 0–255 | 保留原色；S1；M0 |
| 16 | 启用/SHOW | Rarest Set Items (ADD ONES YOU WANT) | 指定暗金/套装 21 项；见 SELECTED_UNIQUES.md；roll 边界为空或 0–255 | 亮绿；S6；M4；强调 |
| 17 | 说明条目/关闭 | These rules show every "Resource" in Last Epoch. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 18 | 说明条目/关闭 | I would strongly advise to always leave these rules on. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 19 | 启用/SHOW | Glyphs | GlyphCondition：AllGlyphs | 保留原色；S1；M0 |
| 20 | 启用/SHOW | Keys & Resources | KeysCondition：AllKeys | 保留原色；S1；M0 |
| 21 | 启用/SHOW | Resonances | ResonancesCondition：AllResonances | 保留原色；S1；M0 |
| 22 | 启用/SHOW | Runes | RuneCondition：AllRunes | 保留原色；S1；M0 |
| 23 | 启用/SHOW | Shards | CraftingMaterialsCondition：AllShards | 保留原色；S1；M0 |
| 24 | 启用/SHOW | Woven Echoes | WovenEchoesCondition：AllWovenEchoes | 保留原色；S1；M0 |
| 25 | 说明条目/关闭 | This rule hides classes you will never play. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 26 | 说明条目/关闭 | It's placed below the rarest uniques and sets in case | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 27 | 说明条目/关闭 | you ever want to play them. If you want those hidden too | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 28 | 说明条目/关闭 | just drag these rules above the Unique/Set rules. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 29 | 关闭/HIDE | All items from classes you'll never play (SELECT CLASSES). | 职业需求：None（未选职业；此隐藏规则默认关闭） | 保留原色；S1；M0 |
| 30 | 说明条目/关闭 | These are the Golden Rules for the BIS Items in Last Epoch. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 31 | 说明条目/关闭 | Add the Best Affixes for each slot. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 32 | 说明条目/关闭 | Duplicate the Wpn/OH Rules if you use different bases | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 33 | 说明条目/关闭 | to guarantee the right Affix lands on the right base. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 34 | 说明条目/关闭 | Don't add Sub Types unless you're going to wear the item. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 35 | 说明条目/关闭 | Duplicate the Relic rule for each class you're playing. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 36 | 说明条目/关闭 | Uncheck Classes / Wpns / OHs For The Double Exalts. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 37 | 启用/SHOW | All Tier 8 Items | 词缀：所有属性(50)、协调(504)、敏捷(503)、智力(502)等 946 项；至少 1 条；单条 T >7；合计 T 不限；物品：空类型（广泛匹配，见说明）；底材不限 | 金黄；S6；M8；强调；光柱 LARGEST/色号5 |
| 38 | 启用/SHOW | Best Weapon (ADD BEST WEAPON BASE & T7 AFFIXES) | 物品：空类型（广泛匹配，见说明）；底材不限；词缀：暴击伤害加成(6)；至少 1 条；单条 T ≥7；合计 T 不限 | 金黄；S6；M8；强调；光柱 LARGEST/色号5 |
| 39 | 启用/SHOW | Best Offhand (ADD BEST OFFHAND BASE & T7 AFFIXES) | 物品：空类型（广泛匹配，见说明）；底材不限；词缀：增加生命(25)、提高生命(52)、复合生命(36)、暴击伤害加成(6)；至少 1 条；单条 T ≥7；合计 T 不限 | 金黄；S6；M8；强调；光柱 LARGEST/色号5 |
| 40 | 启用/SHOW | Best Helmets (ADD BEST T7 AFFIXES) | 物品：头盔；底材不限；词缀：增加生命(25)、提高生命(52)；至少 1 条；单条 T ≥7；合计 T 不限 | 金黄；S6；M8；强调；光柱 LARGEST/色号5 |
| 41 | 启用/SHOW | Best Body Armour (ADD BEST T7 AFFIXES) | 物品：胸甲；底材不限；词缀：增加生命(25)、提高生命(52)、护甲与降低承受暴击额外伤害(715)；至少 1 条；单条 T ≥7；合计 T 不限 | 金黄；S6；M8；强调；光柱 LARGEST/色号5 |
| 42 | 启用/SHOW | Best Belts (ADD BEST T7 AFFIXES) | 物品：腰带；底材不限；词缀：增加生命(25)、提高生命(52)、复合生命(36)、提高冷却恢复速度(27)等 7 项；至少 1 条；单条 T ≥7；合计 T 不限 | 金黄；S6；M8；强调；光柱 LARGEST/色号5 |
| 43 | 启用/SHOW | Best Boots (ADD BEST T7 AFFIXES) | 物品：靴子；底材不限；词缀：增加生命(25)、复合生命(36)、移动速度(28)、提高冷却恢复速度(27)；至少 1 条；单条 T ≥7；合计 T 不限 | 金黄；S6；M8；强调；光柱 LARGEST/色号5 |
| 44 | 启用/SHOW | Best Gloves (ADD BEST T7 AFFIXES) | 物品：手套；底材不限；词缀：增加生命(25)、复合生命(36)、暴击几率(5)；至少 1 条；单条 T ≥7；合计 T 不限 | 金黄；S6；M8；强调；光柱 LARGEST/色号5 |
| 45 | 启用/SHOW | Best Amulets (ADD BEST T7 AFFIXES) | 物品：护身符；底材不限；词缀：增加生命(25)、暴击伤害加成(6)；至少 1 条；单条 T ≥7；合计 T 不限 | 金黄；S6；M8；强调；光柱 LARGEST/色号5 |
| 46 | 启用/SHOW | Best Rings (ADD BEST T7 AFFIXES) | 物品：戒指；底材不限；词缀：增加生命(25)；至少 1 条；单条 T ≥7；合计 T 不限 | 金黄；S6；M8；强调；光柱 LARGEST/色号5 |
| 47 | 启用/SHOW | Best Relics (ADD BEST T7 AFFIXES) | 物品：遗物；底材：黄铜圣杯(3)、白银圣杯(4)、黄金圣杯(5)；词缀：增加生命(25)、增加生命与生命再生(825)、暴击伤害加成(6)；至少 1 条；单条 T ≥7；合计 T 不限 | 金黄；S6；M8；强调；光柱 LARGEST/色号5 |
| 48 | 启用/SHOW | Double Exalts (UNCHECK UNWANTED WPN & OH TYPES) | 词缀：协调(504)、敏捷(503)、智力(502)、力量(501)等 623 项；至少 2 条；单条 T ≥6；合计 T 不限；物品：头盔、胸甲、腰带、靴子、手套、护身符、戒指、遗物、副手法器、盾牌、箭袋、双手斧、双手锤、双手长矛、双手长杖、双手剑、弓、单手斧、单手锤、权杖、单手剑、魔杖、匕首；底材不限 | 淡紫；S1；M0；强调 |
| 49 | 说明条目/关闭 | Pay very close attention to these rules - they're important. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 50 | 说明条目/关闭 | For the T6 rule pick the best Affixes & Weapon / OH types. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 51 | 说明条目/关闭 | That your class(es) actually use. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 52 | 说明条目/关闭 | Duplicate the T6/T7 Wpn/OH Rules for each different | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 53 | 说明条目/关闭 | base type you use if you want different affixes on them. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 54 | 说明条目/关闭 | Warning: DO NOT PICK SUBTYPES. We're slamming these. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 55 | 说明条目/关闭 | The T6s turn off at 85 b/c we only want T7s then. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 56 | 说明条目/关闭 | For the T7 Rule pick bases, but select nearly every affix | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 57 | 说明条目/关闭 | because we want to bank up T7s to craft. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 58 | 说明条目/关闭 | The Green Rule allows you to Rune of Havoc a T7 | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 59 | 说明条目/关闭 | to a BIS Affix. Very powerful, make sure you use this! | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 60 | 启用/SHOW | Tier 7 Wpns/OHs (CHECK WPN/OH TYPES & DMGS) | 词缀：敏捷(503)、施法速度(4)、法术暴击几率(84)、法术伤害(38)等 42 项；至少 1 条；单条 T ≥7；合计 T 不限；物品：单手斧、单手锤、权杖、单手剑、魔杖、匕首、弓、副手法器、盾牌、箭袋、双手斧、双手锤、双手长矛、双手长杖、双手剑；底材不限 | 淡紫；S1；M0；强调 |
| 61 | 启用/SHOW | Tier 7 Armors (CHECK AFFIXES) | 词缀：敏捷(503)、施法速度(4)、法术暴击几率(84)、法术伤害(38)等 343 项；至少 1 条；单条 T ≥7；合计 T 不限；物品：头盔、胸甲、腰带、靴子、手套、护身符、戒指、遗物；底材不限 | 淡紫；S1；M0；强调 |
| 62 | 启用/SHOW | Tier 7 Havoc (CHECK WPN/OH TYPES & DMGS) | 词缀：魔力与魔力再生(718)、活力(505)、力量(501)、智力(502)等 491 项；至少 1 条；单条 T ≥7；合计 T 不限；词缀：移动速度(28)、提高冷却恢复速度(27)、增加生命(25)、提高生命(52)等 10 项；至少 1 条；advanced=false，保存的阶数阈值不作为已启用限制；物品：权杖、双手斧、匕首、魔杖、单手剑、单手锤、单手斧、弓、双手剑、双手长杖、双手长矛、双手锤、副手法器、盾牌、箭袋、头盔、胸甲、腰带、靴子、手套、护身符、戒指、遗物；底材不限；腐化状态：OnlyUncorrupted | 亮绿；S1；M0；强调 |
| 63 | 启用/SHOW | Tier 6 Wpns/OHs (CHECK WPN/OH TYPES & DMGS) | 词缀：敏捷(503)、暴击伤害加成(6)、暴击几率(5)、持续伤害(72)等 16 项；至少 1 条；单条 T ≥6；合计 T 不限；物品：权杖、双手斧、匕首、魔杖、单手剑、单手锤、单手斧、弓、双手剑、双手长杖、双手长矛、双手锤、副手法器、盾牌、箭袋；底材不限；角色等级 0–84 | 淡紫；S1；M0 |
| 64 | 启用/SHOW | Tier 6 Armors (CHECK AFFIXES) - Turns Off At 85 | 词缀：敏捷(503)、智力(502)、暴击伤害加成(6)、暴击几率(5)等 338 项；至少 1 条；单条 T ≥6；合计 T 不限；物品：头盔、胸甲、腰带、靴子、手套、护身符、戒指、遗物；底材不限；角色等级 0–84 | 淡紫；S1；M0 |
| 65 | 说明条目/关闭 | These rules let you farm Experimental / Champion Affixes. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 66 | 说明条目/关闭 | They're turned off by default b/c not many builds use them. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 67 | 说明条目/关闭 | Exalted Experimentals are on because they're rare. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 68 | 启用/SHOW | Exalted Experimentals (TURN OFF IF YOU DON'T USE) | 词缀：实验性急速效果(676)、实验性狂热效果(677)、穿越时获取的实验性护盾(678)、使用穿越技能传送的实验性随从(679)等 12 项；至少 1 条；advanced=false，保存的阶数阈值不作为已启用限制；稀有度：EXALTED | 保留原色；S1；M0 |
| 69 | 关闭/SHOW | Experimentals (TURN ON RULE & SELECT AFFIXES) | 词缀：击杀时的实验性护盾(673)、实验性的闪避等级和忍耐阈值(674)、每失去一点生命值时获得的实验性护盾(675)、实验性急速效果(676)等 12 项；至少 1 条；advanced=false，保存的阶数阈值不作为已启用限制 | 保留原色；S1；M0 |
| 70 | 关闭/SHOW | Champion Affixes (TURN ON RULE & SELECT AFFIXES) | 词缀：死亡之握勇士的(766)、幻影勇士的(767)、火花勇士的(768)、炼狱勇士的(769)等 14 项；至少 1 条；advanced=false，保存的阶数阈值不作为已启用限制 | 保留原色；S1；M0 |
| 71 | 说明条目/关闭 | These rules guarantee that you don't miss Exalts / Uniques. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 72 | 说明条目/关闭 | Turn these rules off, or their tone their level down, if you want. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 73 | 启用/SHOW | All Uniques - Turns off at 80 | 稀有度：UNIQUE；角色等级 0–79 | 保留原色；S1；M0 |
| 74 | 启用/SHOW | All Exalts - Turns off at 60 | 稀有度：EXALTED；词缀：所有属性(50)、力量(501)、智力(502)、敏捷(503)等 668 项；至少 1 条；advanced=false，保存的阶数阈值不作为已启用限制；角色等级 0–59 | 保留原色；S1；M0 |
| 75 | 启用/SHOW | All Corrupts (SELECT AFFIXES) - Turns Off At 60 | 腐化状态：OnlyCorrupted；词缀：全技能等级与增加魔力(1014)、元素抗性与腐化抗性(1024)、提高生命与每秒获得能量护盾(1010)、物理抗性与虚空抗性(1023)等 18 项；至少 1 条；advanced=false，保存的阶数阈值不作为已启用限制；角色等级 0–59 | 保留原色；S1；M0 |
| 76 | 说明条目/关闭 | Orange Shatter Rules build shards for crafting. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 77 | 说明条目/关闭 | Once have a ton, turn these rules off. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 78 | 说明条目/关闭 | The pink rules allow you to target farm specific Bases / Affixes. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 79 | 说明条目/关闭 | The green rule is for Ascending items. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 80 | 说明条目/关闭 | If you're MG, turn off the COF Requirement on Green. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 81 | 启用/SHOW | Items to Ascend (CHOOSE THE ITEM TYPE) | 物品：空类型（广泛匹配，见说明）；底材不限；稀有度：NORMAL MAGIC RARE EXALTED；物品阵营标记：CircleOfFortune；腐化状态：OnlyUncorrupted | 亮绿；S1；M0；强调 |
| 82 | 启用/SHOW | Item Bases (ADD BASE TYPES TO TARGET) | 物品：空类型（广泛匹配，见说明）；底材不限；稀有度：NORMAL MAGIC RARE EXALTED | 粉；S1；M0；强调 |
| 83 | 启用/SHOW | Highly Needed Affixes (ADD AFFIXES YOU'RE LOW ON) | 词缀：空列表；至少 1 条；advanced=false，保存的阶数阈值不作为已启用限制 | 粉；S1；M0；强调 |
| 84 | 启用/SHOW | Shatter Acolyte Affixes | 词缀：剥皮等级(944)、鬼焰等级(735)、混沌箭等级(734)、冥府裂缝等级(733)等 57 项；至少 1 条；单条 T ≥4；合计 T 不限；稀有度：MAGIC RARE EXALTED | 橙黄；S1；M0 |
| 85 | 启用/SHOW | Shatter Mage Affixes | 词缀：伤害由魔力优先承受而非生命(53)、冻伤冰霜抗性穿透(339)、提高法术暴击几率（最大魔力超过300时翻倍）(381)、引导期间法术伤害(383)等 57 项；至少 1 条；单条 T ≥4；合计 T 不限；稀有度：MAGIC RARE EXALTED | 橙黄；S1；M0 |
| 86 | 启用/SHOW | Shatter Primalist Affixes | 词缀：暴风打击法术伤害(21)、图腾法术伤害(334)、提高变形期间冷却恢复速度(335)、召唤物暴击伤害加成(336)等 57 项；至少 1 条；单条 T ≥4；合计 T 不限；稀有度：MAGIC RARE EXALTED | 橙黄；S1；M0 |
| 87 | 启用/SHOW | Shatter Rogue Affixes | 词缀：生成影子时获得能量护盾(437)、提高影子攻击伤害(439)、伤害偏斜时恢复生命(440)、被击中后使躲避值(442)等 72 项；至少 1 条；单条 T ≥4；合计 T 不限；稀有度：MAGIC RARE EXALTED | 橙黄；S1；M0 |
| 88 | 启用/SHOW | Shatter Sentinel Affixes | 词缀：流血物理抗性穿透(358)、持剑时近战物理伤害(359)、持斧击中时施加流血几率(363)、持锤时近战物理伤害(364)等 53 项；至少 1 条；单条 T ≥4；合计 T 不限；稀有度：MAGIC RARE EXALTED | 橙黄；S1；M0 |
| 89 | 启用/SHOW | Shatter Offensive Affixes (SELECT WHAT YOU NEED) | 词缀：近战攻击速度(2)、暴击率和弓攻击速度(672)、近战物理伤害(63)、近战伤害(89)等 18 项；至少 1 条；单条 T ≥5；合计 T 不限；稀有度：MAGIC RARE EXALTED | 橙黄；S1；M0 |
| 90 | 启用/SHOW | Shatter Defensive Affixes (SELECT WHAT YOU NEED) | 词缀：增加生命(25)、提高生命(52)、复合生命(36)、移动速度(28)等 15 项；至少 1 条；单条 T ≥5；合计 T 不限；稀有度：MAGIC RARE EXALTED | 橙黄；S1；M0 |
| 91 | 说明条目/关闭 | Idol rules below. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 92 | 说明条目/关闭 | 1x1, 2x1 & 1x2 Idols work for all classes - so they have 1 rule each | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 93 | 说明条目/关闭 | Pick your BIS affixes. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 94 | 说明条目/关闭 | For BIS Idols the rules require both Affixes. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 95 | 说明条目/关闭 | This makes them very rare to find. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 96 | 说明条目/关闭 | Change This To 1 Affix Present To Make It Less Strict. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 97 | 说明条目/关闭 | Check The Corrupted Mods You Want. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 98 | 说明条目/关闭 | The Idol Altar Rule Needs SubTypes & Affixes Added. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 99 | 启用/SHOW | All Classes 1x1 Idols (SELECT BEST IDOL AFFIXES) | 物品：小型神像、中型神像；底材不限；词缀：空列表；至少 2 条；advanced=false，保存的阶数阈值不作为已启用限制 | 薄荷绿；S6；M4；强调；光柱 LARGEST/色号19 |
| 100 | 启用/SHOW | All Classes 1x2 Idols (SELECT BEST IDOL AFFIXES) | 物品：厚实神像；底材：厚实拉贡神像(0)、厚实编织者神像(1)；词缀：空列表；至少 2 条；advanced=false，保存的阶数阈值不作为已启用限制 | 薄荷绿；S6；M4；强调；光柱 LARGEST/色号19 |
| 101 | 启用/SHOW | All Classes 2x1 Idols (SELECT BEST IDOL AFFIXES) | 物品：谦卑神像；底材：谦卑伊泰拉神像(0)、谦卑编织者神像(1)；词缀：空列表；至少 2 条；advanced=false，保存的阶数阈值不作为已启用限制 | 薄荷绿；S6；M4；强调；光柱 LARGEST/色号19 |
| 102 | 启用/SHOW | Acolyte 2x2 Idols (SELECT BEST IDOL AFFIXES) | 物品：精装神像；底材：精装不朽神像(3)、异端精装不朽神像(10)；词缀：空列表；至少 2 条；advanced=false，保存的阶数阈值不作为已启用限制 | 薄荷绿；S6；M4；强调；光柱 LARGEST/色号19 |
| 103 | 启用/SHOW | Acolyte 1x3 Idols (SELECT BEST IDOL AFFIXES) | 物品：大型神像；底材：大型不朽神像(3)、异端大型不朽神像(8)、大型幽冥预兆神像(13)；词缀：空列表；至少 2 条；advanced=false，保存的阶数阈值不作为已启用限制 | 薄荷绿；S6；M4；强调；光柱 LARGEST/色号19 |
| 104 | 启用/SHOW | Acolyte 3x1 Idols (SELECT BEST IDOL AFFIXES) | 物品：宏伟神像；底材：宏伟骸骨神像(3)、异端宏伟骸骨神像(8)、宏伟幽冥预兆神像(13)；词缀：空列表；至少 2 条；advanced=false，保存的阶数阈值不作为已启用限制 | 薄荷绿；S6；M4；强调；光柱 LARGEST/色号19 |
| 105 | 启用/SHOW | Acolyte 1x4 Idols (SELECT BEST IDOL AFFIXES) | 物品：巨型神像；底材：巨型不朽神像(3)、异端巨型不朽神像(8)；词缀：空列表；至少 2 条；advanced=false，保存的阶数阈值不作为已启用限制 | 薄荷绿；S6；M4；强调；光柱 LARGEST/色号19 |
| 106 | 启用/SHOW | Acolyte 4x1 Idols (SELECT BEST IDOL AFFIXES) | 物品：华丽神像；底材：华丽骸骨神像(3)、异端华丽骸骨神像(8)；词缀：空列表；至少 2 条；advanced=false，保存的阶数阈值不作为已启用限制 | 薄荷绿；S6；M4；强调；光柱 LARGEST/色号19 |
| 107 | 启用/SHOW | Mage 2x2 Idols (SELECT BEST IDOL AFFIXES) | 物品：精装神像；底材：精装奥术神像(1)、异端精装赫罗特神像(8)；词缀：空列表；至少 2 条；advanced=false，保存的阶数阈值不作为已启用限制 | 薄荷绿；S6；M4；强调；光柱 LARGEST/色号19 |
| 108 | 启用/SHOW | Mage 1x3 Idols (SELECT BEST IDOL AFFIXES) | 物品：大型神像；底材：大型奥术神像(1)、异端大型奥术神像(6)、大型奥术预兆神像(11)；词缀：空列表；至少 2 条；advanced=false，保存的阶数阈值不作为已启用限制 | 薄荷绿；S6；M4；强调；光柱 LARGEST/色号19 |
| 109 | 启用/SHOW | Mage 3x1 Idols (SELECT BEST IDOL AFFIXES) | 物品：宏伟神像；底材：宏伟玻璃神像(1)、异端宏伟玻璃神像(6)、宏伟奥术预兆神像(11)；词缀：空列表；至少 2 条；advanced=false，保存的阶数阈值不作为已启用限制 | 薄荷绿；S6；M4；强调；光柱 LARGEST/色号19 |
| 110 | 启用/SHOW | Mage 1x4 Idols (SELECT BEST IDOL AFFIXES) | 物品：巨型神像；底材：巨型奥术神像(1)、异端巨型奥术神像(6)；词缀：空列表；至少 2 条；advanced=false，保存的阶数阈值不作为已启用限制 | 薄荷绿；S6；M4；强调；光柱 LARGEST/色号19 |
| 111 | 启用/SHOW | Mage 4x1 Idols (SELECT BEST IDOL AFFIXES) | 物品：华丽神像；底材：华丽玻璃神像(1)、异端华丽玻璃神像(6)；词缀：空列表；至少 2 条；advanced=false，保存的阶数阈值不作为已启用限制 | 薄荷绿；S6；M4；强调；光柱 LARGEST/色号19 |
| 112 | 启用/SHOW | Primalist 2x2 Idols (SELECT BEST IDOL AFFIXES) | 物品：精装神像；底材：精装赫罗特神像(0)、异端精装赫罗特神像(7)；词缀：空列表；至少 2 条；advanced=false，保存的阶数阈值不作为已启用限制 | 薄荷绿；S6；M4；强调；光柱 LARGEST/色号19 |
| 113 | 启用/SHOW | Primalist 1x3 Idols (SELECT BEST IDOL AFFIXES) | 物品：大型神像；底材：大型游牧民神像(0)、异端大型游牧民神像(5)、大型原始预兆神像(10)；词缀：空列表；至少 2 条；advanced=false，保存的阶数阈值不作为已启用限制 | 薄荷绿；S6；M4；强调；光柱 LARGEST/色号19 |
| 114 | 启用/SHOW | Primalist 3x1 Idols (SELECT BEST IDOL AFFIXES) | 物品：宏伟神像；底材：宏伟赫罗特神像(0)、异端宏伟赫罗特神像(5)、宏伟原始预兆神像(10)；词缀：空列表；至少 2 条；advanced=false，保存的阶数阈值不作为已启用限制 | 薄荷绿；S6；M4；强调；光柱 LARGEST/色号19 |
| 115 | 启用/SHOW | Primalist 1x4 Idols (SELECT BEST IDOL AFFIXES) | 物品：巨型神像；底材：巨型游牧民神像(0)、异端巨型游牧民神像(5)；词缀：空列表；至少 2 条；advanced=false，保存的阶数阈值不作为已启用限制 | 薄荷绿；S6；M4；强调；光柱 LARGEST/色号19 |
| 116 | 启用/SHOW | Primalist 4x1 Idols (SELECT BEST IDOL AFFIXES) | 物品：华丽神像；底材：华丽赫罗特神像(0)、异端华丽赫罗特神像(5)；词缀：空列表；至少 2 条；advanced=false，保存的阶数阈值不作为已启用限制 | 薄荷绿；S6；M4；强调；光柱 LARGEST/色号19 |
| 117 | 启用/SHOW | Rogue 2x2 Idols (SELECT BEST IDOL AFFIXES) | 物品：精装神像；底材：精装玛加莎神像(4)、异端精装玛加莎神像(11)；词缀：空列表；至少 2 条；advanced=false，保存的阶数阈值不作为已启用限制 | 薄荷绿；S6；M4；强调；光柱 LARGEST/色号19 |
| 118 | 启用/SHOW | Rogue 1x3 Idols (SELECT BEST IDOL AFFIXES) | 物品：大型神像；底材：大型暗影神像(4)、异端大型暗影神像(9)、大型黯影预兆神像(14)；词缀：空列表；至少 2 条；advanced=false，保存的阶数阈值不作为已启用限制 | 薄荷绿；S6；M4；强调；光柱 LARGEST/色号19 |
| 119 | 启用/SHOW | Rogue 3x1 Idols (SELECT BEST IDOL AFFIXES) | 物品：宏伟神像；底材：宏伟玛加莎神像(4)、异端宏伟玛加莎神像(9)、宏伟黯影预兆神像(14)；词缀：空列表；至少 2 条；advanced=false，保存的阶数阈值不作为已启用限制 | 薄荷绿；S6；M4；强调；光柱 LARGEST/色号19 |
| 120 | 启用/SHOW | Rogue 1x4 Idols (SELECT BEST IDOL AFFIXES) | 物品：巨型神像；底材：巨型暗影神像(4)、异端巨型暗影神像(9)；词缀：空列表；至少 2 条；advanced=false，保存的阶数阈值不作为已启用限制 | 薄荷绿；S6；M4；强调；光柱 LARGEST/色号19 |
| 121 | 启用/SHOW | Rogue 4x1 Idols (SELECT BEST IDOL AFFIXES) | 物品：华丽神像；底材：华丽玛加莎神像(4)、异端华丽玛加莎神像(9)；词缀：空列表；至少 2 条；advanced=false，保存的阶数阈值不作为已启用限制 | 薄荷绿；S6；M4；强调；光柱 LARGEST/色号19 |
| 122 | 启用/SHOW | Sentinel 2x2 Idols (SELECT BEST IDOL AFFIXES) | 物品：精装神像；底材：精装瑞耶神像(2)、异端精装瑞耶神像(9)；词缀：空列表；至少 2 条；advanced=false，保存的阶数阈值不作为已启用限制 | 薄荷绿；S6；M4；强调；光柱 LARGEST/色号19 |
| 123 | 启用/SHOW | Sentinel 1x3 Idols (SELECT BEST IDOL AFFIXES) | 物品：大型神像；底材：大型瑞耶神像(2)、异端大型瑞耶神像(7)、大型钢铁预兆神像(12)；词缀：空列表；至少 2 条；advanced=false，保存的阶数阈值不作为已启用限制 | 薄荷绿；S6；M4；强调；光柱 LARGEST/色号19 |
| 124 | 启用/SHOW | Sentinel 3x1 Idols (SELECT BEST IDOL AFFIXES) | 物品：宏伟神像；底材：宏伟太阳神像(2)、异端宏伟太阳神像(7)、宏伟钢铁预兆神像(12)；词缀：空列表；至少 2 条；advanced=false，保存的阶数阈值不作为已启用限制 | 薄荷绿；S6；M4；强调；光柱 LARGEST/色号19 |
| 125 | 启用/SHOW | Sentinel 1x4 Idols (SELECT BEST IDOL AFFIXES) | 物品：巨型神像；底材：巨型瑞耶神像(2)、异端巨型瑞耶神像(7)；词缀：空列表；至少 2 条；advanced=false，保存的阶数阈值不作为已启用限制 | 薄荷绿；S6；M4；强调；光柱 LARGEST/色号19 |
| 126 | 启用/SHOW | Sentinel 4x1 Idols (SELECT BEST IDOL AFFIXES) | 物品：华丽神像；底材：华丽太阳神像(2)、异端华丽太阳神像(7)；词缀：空列表；至少 2 条；advanced=false，保存的阶数阈值不作为已启用限制 | 薄荷绿；S6；M4；强调；光柱 LARGEST/色号19 |
| 127 | 启用/SHOW | Idol Altars (DESELECT UNWANTED SUBTYPES & AFFIXES) | 物品：神像祭坛；底材：扭曲祭坛(0)、天际祭坛(2)、尖塔祭坛(3)、假面祭坛(5)、银月祭坛(6)、侵蚀祭坛(4)、眼之祭坛(7)、远古祭坛(8)、预言祭坛(10)、锯齿祭坛(1)、无懈祭坛(9)、金字塔祭坛(11)、黄金祭坛(12)；词缀：生命自装备的每个预兆神像(1088)、折射栏位神像前缀与后缀效果(1089)、折射栏位神像前缀效果(1093)、折射栏位神像后缀效果(1094)等 20 项；至少 1 条；advanced=false，保存的阶数阈值不作为已启用限制 | 薄荷绿；S6；M4；强调；光柱 LARGEST/色号19 |
| 128 | 启用/SHOW | Godly Idols (ADD CLASS SPECIFIC AFFIXES) - Turns off at 90 | 词缀：火焰抗性(111)、冰霜抗性(112)、虚空抗性(115)、腐化抗性(114)等 143 项；至少 2 条；advanced=false，保存的阶数阈值不作为已启用限制；物品：小型神像、中型神像、谦卑神像、厚实神像、宏伟神像、大型神像、华丽神像、巨型神像、精装神像；底材不限；角色等级 0–89 | 薄荷绿；S1；M0；强调 |
| 129 | 启用/SHOW | Decent Idols (ADD CLASS SPECIFIC AFFIXES) - Turns off at 75 | 词缀：火焰抗性(111)、冰霜抗性(112)、虚空抗性(115)、腐化抗性(114)等 143 项；至少 1 条；advanced=false，保存的阶数阈值不作为已启用限制；物品：小型神像、中型神像、谦卑神像、厚实神像、宏伟神像、大型神像、华丽神像、巨型神像、精装神像；底材不限；角色等级 0–74 | 薄荷绿；S1；M0 |
| 130 | 说明条目/关闭 | Campaign rules below. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 131 | 说明条目/关闭 | Uncheck early game Weapons you won't use. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 132 | 说明条目/关闭 | Add your BIS Weapons and Offhands. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 133 | 说明条目/关闭 | All Campaign Rules Turn Off At Level 60. | 说明用占位条件；保持关闭 | 蓝；S1；M0；强调 |
| 134 | 启用/SHOW | All Exalts or Better - Turns off at 60 | 稀有度：UNIQUE SET LEGENDARY EXALTED；角色等级 0–59 | 保留原色；S1；M0 |
| 135 | 启用/SHOW | Campaign Idols - Turns off at 60 | 物品：小型神像、中型神像、谦卑神像、厚实神像、宏伟神像、大型神像、华丽神像、巨型神像、精装神像；底材不限；词缀：生命(105)、生命(107)、元素抗性(117)、物理抗性(430)等 438 项；至少 1 条；advanced=false，保存的阶数阈值不作为已启用限制；角色等级 0–59 | 薄荷绿；S1；M4；强调；光柱 LARGEST/色号19 |
| 136 | 启用/SHOW | BIS Campaign Wpns (ADD WEAPON & SUBTYPES) | 物品：空类型（广泛匹配，见说明）；底材不限；角色等级 0–59 | 金黄；S6；M8；强调；光柱 LARGEST/色号5 |
| 137 | 启用/SHOW | BIS Campaign Offhands (ADD OH & SUBTYPES) | 物品：空类型（广泛匹配，见说明）；底材不限；角色等级 0–59 | 金黄；S6；M8；强调；光柱 LARGEST/色号5 |
| 138 | 启用/SHOW | BIS Campaign Amulet Bases - Turns off at 60 | 物品：护身符；底材：白骨护身符(7)、金护身符(9)；角色等级 0–59 | 金黄；S6；M8；强调；光柱 LARGEST/色号4 |
| 139 | 启用/SHOW | BIS Campaign Belt Bases - Turns off at 60 | 物品：腰带；底材：蛛丝饰带(7)；角色等级 0–59 | 金黄；S6；M2；强调；光柱 LARGEST/色号4 |
| 140 | 启用/SHOW | BIS Campaign Body Armor Bases - Turns off at 60 | 物品：胸甲；底材：科尔海姆胸甲(29)、银月衣饰(57)、熔炉板甲(60)、贵族板甲(36)、追随者板甲(37)、葬仪板甲(13)、亵渎华服(14)、恶魔长袍(12)、镶片胸甲(47)、蛇鳞克星大衣(66)；角色等级 0–59 | 金黄；S6；M2；强调；光柱 LARGEST/色号0 |
| 141 | 启用/SHOW | BIS Campaign Boot Bases - Turns off at 60 | 物品：靴子；底材：赫伯利亚靴子(5)、太阳之城护胫(6)；角色等级 0–59 | 金黄；S6；M2；强调；光柱 LARGEST/色号0 |
| 142 | 启用/SHOW | BIS Campaign Helmet Bases - Turns off at 60 | 物品：头盔；底材：梅鲁纳头盔(55)、冰狼皮帽(29)、科尔海姆风帽(54)、天神头盔(22)、尖刺头盔(60)、追随者头盔(37)、恶魔风帽(12)、具角头盔(46)、蛇鳞克星恐怖面具(66)、巨龙面罩(68)；角色等级 0–59 | 金黄；S6；M2；强调；光柱 LARGEST/色号0 |
| 143 | 启用/SHOW | BIS Campaign Ring Bases - Turns off at 60 | 物品：戒指；底材：金戒指(4)；角色等级 0–59 | 金黄；S6；M8；强调；光柱 LARGEST/色号4 |
| 144 | 启用/SHOW | BIS Campaign Glove Bases - Turns off at 60 | 物品：手套；底材：太阳之城护腕(6)、圣教军臂铠(7)；角色等级 0–59 | 金黄；S6；M2；强调；光柱 LARGEST/色号0 |
| 145 | 启用/SHOW | BIS Campaign Relic Bases - Turns off at 60 | 物品：遗物；底材：捕灵网(36)、窥视之瞳(25)、符文羽毛笔(27)、银色饰章(44)、腐烂灵魂(19)、古代钱币(55)、红宝石骰子(53)、解毒药剂瓶(54)；角色等级 0–59 | 金黄；S6；M2；强调；光柱 LARGEST/色号0 |
| 146 | 启用/SHOW | Shatter T3+ Phys Res / All Health - Turns off at 50 | 物品：头盔、胸甲、腰带、靴子、手套、护身符、戒指、遗物、小型神像、中型神像、谦卑神像、厚实神像、宏伟神像、大型神像、华丽神像、巨型神像、精装神像；底材不限；词缀：物理抗性(45)、增加生命(25)、提高生命(52)、复合生命(36)等 97 项；至少 1 条；单条 T ≥3；合计 T 不限；角色等级 0–49 | 橙黄；S1；M0；强调 |
| 147 | 启用/SHOW | Shatter T3+ Movespeed & CDR - Turns off at 50 | 物品：靴子；底材不限；词缀：移动速度(28)、提高冷却恢复速度(27)、闪避净化异常状态几率与提高承受的异常状态伤害(991)、提高急速效果与急速期间承受持续伤害总降(992)等 13 项；至少 1 条；单条 T ≥3；合计 T 不限；角色等级 0–49 | 橙黄；S1；M0；强调 |
| 148 | 启用/SHOW | Shatter T3+ Resistances - Turns off at 50 | 物品：头盔、胸甲、腰带、靴子、手套、护身符、戒指、遗物、小型神像、中型神像、谦卑神像、厚实神像、宏伟神像、大型神像、华丽神像、巨型神像、精装神像；底材不限；词缀：冰霜抗性(17)、元素抗性(80)、火焰抗性(13)、闪电抗性(24)等 101 项；至少 1 条；单条 T ≥3；合计 T 不限；角色等级 0–49 | 橙黄；S1；M0；强调 |
| 149 | 启用/SHOW | T2+ Phys Res / All Health - Turns off at 30 | 物品：头盔、胸甲、腰带、靴子、手套、护身符、戒指、遗物、小型神像、中型神像、谦卑神像、厚实神像、宏伟神像、大型神像、华丽神像、巨型神像、精装神像；底材不限；词缀：物理抗性(45)、增加生命(25)、提高生命(52)、复合生命(36)等 97 项；至少 1 条；单条 T ≥2；合计 T 不限；角色等级 0–29 | 橙黄；S1；M0；强调 |
| 150 | 启用/SHOW | T2+ Movespeed & CDR - Turns off at 30 | 物品：靴子；底材不限；词缀：移动速度(28)、提高冷却恢复速度(27)、闪避净化异常状态几率与提高承受的异常状态伤害(991)、提高急速效果与急速期间承受持续伤害总降(992)等 13 项；至少 1 条；单条 T ≥2；合计 T 不限；角色等级 0–29 | 橙黄；S1；M0；强调 |
| 151 | 启用/SHOW | T2+ Resistances - Turns off at 30 | 物品：头盔、胸甲、腰带、靴子、手套、护身符、戒指、遗物、小型神像、中型神像、谦卑神像、厚实神像、宏伟神像、大型神像、华丽神像、巨型神像、精装神像；底材不限；词缀：冰霜抗性(17)、元素抗性(80)、火焰抗性(13)、闪电抗性(24)等 101 项；至少 1 条；单条 T ≥2；合计 T 不限；角色等级 0–29 | 橙黄；S1；M0；强调 |
| 152 | 启用/SHOW | Early Bows - Turns off at 30 | 物品：弓；底材不限；词缀：物理伤害(30)、弓闪电伤害(669)、弓寒冷伤害(670)、弓箭火焰伤害(434)等 23 项；至少 1 条；advanced=false，保存的阶数阈值不作为已启用限制；角色等级 0–29 | 红；S1；M0；强调 |
| 153 | 启用/SHOW | Early Melee Wpns - Turns off at 30 | 物品：单手锤、双手长矛、匕首、魔杖、单手剑、权杖、单手斧、双手剑、双手长杖、双手锤、双手斧；底材不限；词缀：物理伤害(30)、元素伤害(9)、近战冰霜伤害(78)、近战火焰伤害(77)等 58 项；至少 1 条；advanced=false，保存的阶数阈值不作为已启用限制；角色等级 0–29 | 红；S1；M0；强调 |
| 154 | 启用/SHOW | Early Caster Wpns - Turns off at 30 | 物品：魔杖、双手长杖；底材不限；词缀：法术伤害(38)、元素伤害(9)、施法速度(4)、法术暴击几率(84)等 36 项；至少 1 条；advanced=false，保存的阶数阈值不作为已启用限制；角色等级 0–29 | 红；S1；M0；强调 |
| 155 | 启用/SHOW | All Rares - Turns off at 30 | 稀有度：RARE；角色等级 0–29 | 保留原色；S1；M0 |
| 156 | 启用/SHOW | Early Relics - Turns off at 12 | 物品：遗物；底材：黄铜圣杯(3)、白银圣杯(4)、鲜活之种(31)、睿智鹿角(30)、荆刺图腾(70)、灾厄葫芦(65)、捕梦网(29)、符文卷轴(20)、畸变之眼(66)、奥术羽毛笔(21)、三眼遗物(22)、朝霞徽章(38)、天启代码(67)、异端文稿(39)、悲恸旗帜(40)、污损骸骨(11)、先知侏儒(68)、囚禁灵魂(12)、矮人胆汁(13)、象牙骰子(47)、瓶装时间(69)、毒液瓶(48)、风化钱币(49)；角色等级 0–11 | 红；S1；M0；强调 |
| 157 | 启用/SHOW | Early Catalyst - Turns off at 12 | 物品：副手法器；底材：皮革巨著(1)、仪式石(2)、烙印头骨(3)；角色等级 0–11 | 红；S1；M0；强调 |
| 158 | 启用/SHOW | Early Quivers - Turns off at 12 | 物品：箭袋；底材：轻型箭袋(0)、重型箭袋(1)、象牙箭袋(2)；角色等级 0–11 | 红；S1；M0；强调 |
| 159 | 启用/SHOW | Early Shields - Turns off at 12 | 物品：盾牌；底材：团牌(1)、熨斗形盾(2)、骑士盾(4)、木盾(0)；角色等级 0–11 | 红；S1；M0；强调 |
| 160 | 启用/SHOW | Silver Ring - Turns off at 12 | 物品：戒指；底材：银戒指(3)；角色等级 0–11 | 红；S1；M0；强调 |
| 161 | 启用/SHOW | Ruby Amulet - Turns off at 12 | 物品：护身符；底材：红宝石护身符(5)；角色等级 0–11 | 红；S1；M0；强调 |
| 162 | 启用/SHOW | All Items - Turns off at 10 | 物品：单手斧、单手锤、权杖、单手剑、魔杖、匕首、双手斧、双手锤、双手长矛、双手长杖、双手剑、弓、副手法器、盾牌、箭袋、头盔、胸甲、腰带、靴子、手套、护身符、戒指、遗物、小型神像、中型神像、谦卑神像、厚实神像、宏伟神像、大型神像、华丽神像、巨型神像、精装神像；底材不限；角色等级 0–9 | 保留原色；S1；M0 |
| 163 | 启用/HIDE | 最终隐藏全部 | 无条件，匹配全部 | 保留原色；S1；M0 |
