# 双 BD 成品规则索引

由 scripts/generate_filter.py 生成。G=成品 Order+1，R=原基底编号，X=Strict 原XML物理位置。按G升序匹配；完整条件在成品XML，全部原规则处置见 analysis/transfer-report.json。

| G | 状态 | R槽位 | 名称 | 依据 |
|---:|---|---:|---|---|
| 1 | 启用 | 8 | MAIN - Build uniques: Uniques From Planner 3 LP | FLAY X125; NECRO X136 |
| 2 | 启用 | 8 | MAIN - Build uniques: Uniques From Planner 2 LP | FLAY X124; NECRO X135 |
| 3 | 启用 | 8 | MAIN - Build uniques: Uniques From Planner 1 LP - Turtle Rule | FLAY X123; NECRO X134 |
| 4 | 启用 | 8 | MAIN - Build uniques: Uniques & Sets From Planner | FLAY X121; NECRO X132 |
| 5 | 启用 | 8 | MAIN - Build uniques: Uniques From Planner 3 LP | FLAY X125 |
| 6 | 启用 | 8 | MAIN - Build uniques: Uniques From Planner 2 LP | FLAY X124 |
| 7 | 启用 | 8 | MAIN - Build uniques: Uniques From Planner 1 LP - Turtle Rule | FLAY X123 |
| 8 | 启用 | 8 | MAIN - Build uniques: Uniques & Sets From Planner | FLAY X121 |
| 9 | 启用 | 8 | SECONDARY - Build uniques: Uniques From Planner 3 LP | NECRO X136 |
| 10 | 启用 | 8 | SECONDARY - Build uniques: Uniques From Planner 2 LP | NECRO X135 |
| 11 | 启用 | 8 | SECONDARY - Build uniques: Uniques From Planner 1 LP - Turtle Rule | NECRO X134 |
| 12 | 启用 | 8 | SECONDARY - Build uniques: Uniques & Sets From Planner | NECRO X132 |
| 13 | 启用 | 8 |  | raxx |
| 14 | 启用 | 12 | all Uniques with 3LP or 20 WW | raxx |
| 15 | 启用 | 13 | all Uniques with 2LP / 17 WW (UNCHECK UNWANTED) | raxx |
| 16 | 启用 | 14 | all Uniques with 1LP / 14 WW (UNCHECK UNWANTED) | raxx |
| 17 | 启用 | 15 | Raxx rare unique protection | raxx |
| 18 | 启用 | 16 | MAIN - Unique Idols | FLAY X41; NECRO X53 |
| 19 | 启用 | 16 | Raxx selected sets | raxx |
| 20 | 启用 | 19 | Glyphs | raxx |
| 21 | 启用 | 20 | Keys & Resources | raxx |
| 22 | 启用 | 21 | Resonances | raxx |
| 23 | 启用 | 22 | Runes | raxx |
| 24 | 启用 | 23 | Shards | raxx |
| 25 | 启用 | 24 | Woven Echoes | raxx |
| 26 | 关闭 | 29 | OFF - Class hide not requested | raxx |
| 27 | 启用 | 37 | All Tier 8 Items | raxx |
| 28 | 启用 | 38 | MAIN - Tier 7 - One-Handed Axe | FLAY X71 |
| 29 | 启用 | 38 | SECONDARY - Tier 7 - Two-Handed Axe | NECRO X81 |
| 30 | 启用 | 39 | MAIN - Tier 7 - Dagger | FLAY X70 |
| 31 | 启用 | 40 | MAIN - Tier 7 - Helmet | FLAY X69 |
| 32 | 启用 | 40 | SECONDARY - Tier 7 - Helmet | NECRO X80 |
| 33 | 启用 | 41 | MAIN - Tier 7 - Body Armor | FLAY X68 |
| 34 | 启用 | 41 | SECONDARY - Tier 7 - Body Armor | NECRO X79 |
| 35 | 启用 | 42 | MAIN - Tier 7 - Belt | FLAY X67; NECRO X78 |
| 36 | 启用 | 42 | MAIN - Tier 7 - Belt | FLAY X67 |
| 37 | 启用 | 42 | SECONDARY - Tier 7 - Belt | NECRO X78 |
| 38 | 启用 | 43 | MAIN - Tier 7 - Boots | FLAY X66; NECRO X77 |
| 39 | 启用 | 43 | MAIN - Tier 7 - Boots | FLAY X66 |
| 40 | 启用 | 43 | SECONDARY - Tier 7 - Boots | NECRO X77 |
| 41 | 启用 | 44 | MAIN - Tier 7 - Gloves | FLAY X65 |
| 42 | 启用 | 44 | SECONDARY - Tier 7 - Gloves | NECRO X76 |
| 43 | 启用 | 45 | MAIN - Tier 7 - Amulet | FLAY X64 |
| 44 | 启用 | 45 | SECONDARY - Tier 7 - Amulet | NECRO X75 |
| 45 | 启用 | 46 | MAIN - Tier 7 - Ring | FLAY X63; NECRO X74 |
| 46 | 启用 | 46 | MAIN - Tier 7 - Ring | FLAY X63 |
| 47 | 启用 | 46 | SECONDARY - Tier 7 - Ring | NECRO X74 |
| 48 | 启用 | 47 | MAIN - Tier 7 - Relic | FLAY X62; NECRO X73 |
| 49 | 启用 | 47 | MAIN - Tier 7 - Relic | FLAY X62 |
| 50 | 启用 | 47 | SECONDARY - Tier 7 - Relic | NECRO X73 |
| 51 | 启用 | 48 | Double exalts on either build's equipment types | raxx |
| 52 | 关闭 | 60 | OFF - T7 weapon pools mapped above | raxx |
| 53 | 启用 | 61 | SECONDARY - Tier 7 - Class Specific Affixes | NECRO X82 |
| 54 | 启用 | 62 | MAIN - Wanted Affix & Tier 7 (Rune of Havoc) | FLAY X31 |
| 55 | 启用 | 62 | MAIN - Tier 7 Highly Craftable Items (52+ FP) | FLAY X32 |
| 56 | 启用 | 62 | MAIN - Tier 7 Eternal Gauntlets | FLAY X33; NECRO X45 |
| 57 | 启用 | 62 | SECONDARY - Wanted Affix & Tier 7 (Rune of Havoc) | NECRO X42 |
| 58 | 启用 | 62 | SECONDARY - Wanted Experimental & Tier 7 (Rune of Havoc) | NECRO X43 |
| 59 | 启用 | 62 | SECONDARY - Tier 7 Highly Craftable Items (52+ FP) | NECRO X44 |
| 60 | 启用 | 63 | MAIN - Tier 6 - Dagger | FLAY X57 |
| 61 | 启用 | 63 | MAIN - Tier 6 - One-Handed Axe | FLAY X58 |
| 62 | 启用 | 63 | SECONDARY - Tier 6 - Two-Handed Axe | NECRO X69 |
| 63 | 启用 | 64 | MAIN - Tier 6 - Relic | FLAY X49; NECRO X61 |
| 64 | 启用 | 64 | MAIN - Tier 6 - Relic | FLAY X49 |
| 65 | 启用 | 64 | SECONDARY - Tier 6 - Relic | NECRO X61 |
| 66 | 启用 | 64 | MAIN - Tier 6 - Ring | FLAY X50; NECRO X62 |
| 67 | 启用 | 64 | MAIN - Tier 6 - Ring | FLAY X50 |
| 68 | 启用 | 64 | SECONDARY - Tier 6 - Ring | NECRO X62 |
| 69 | 启用 | 64 | MAIN - Tier 6 - Amulet | FLAY X51 |
| 70 | 启用 | 64 | SECONDARY - Tier 6 - Amulet | NECRO X63 |
| 71 | 启用 | 64 | MAIN - Tier 6 - Gloves | FLAY X52 |
| 72 | 启用 | 64 | SECONDARY - Tier 6 - Gloves | NECRO X64 |
| 73 | 启用 | 64 | MAIN - Tier 6 - Boots | FLAY X53; NECRO X65 |
| 74 | 启用 | 64 | MAIN - Tier 6 - Boots | FLAY X53 |
| 75 | 启用 | 64 | SECONDARY - Tier 6 - Boots | NECRO X65 |
| 76 | 启用 | 64 | MAIN - Tier 6 - Belt | FLAY X54; NECRO X66 |
| 77 | 启用 | 64 | MAIN - Tier 6 - Belt | FLAY X54 |
| 78 | 启用 | 64 | SECONDARY - Tier 6 - Belt | NECRO X66 |
| 79 | 启用 | 64 | MAIN - Tier 6 - Body Armor | FLAY X55 |
| 80 | 启用 | 64 | SECONDARY - Tier 6 - Body Armor | NECRO X67 |
| 81 | 启用 | 64 | MAIN - Tier 6 - Helmet | FLAY X56 |
| 82 | 启用 | 64 | SECONDARY - Tier 6 - Helmet | NECRO X68 |
| 83 | 启用 | 68 | SECONDARY - Exalted items with wanted experimentals | experimental_exalted |
| 84 | 启用 | 69 | SECONDARY - Wanted Experimental Affixes | NECRO X13 |
| 85 | 关闭 | 70 | OFF - Champion affixes not requested | raxx |
| 86 | 启用 | 73 | All Uniques - Turns off at 80 | raxx |
| 87 | 启用 | 74 | All Exalts - Turns off at 60 | raxx |
| 88 | 启用 | 75 | MAIN - Wanted corrupted affix (any tier) | FLAY X49 |
| 89 | 启用 | 75 | MAIN - Wanted corrupted affix (any tier) | FLAY X50 |
| 90 | 启用 | 75 | MAIN - Wanted corrupted affix (any tier) | FLAY X51 |
| 91 | 启用 | 75 | MAIN - Wanted corrupted affix (any tier) | FLAY X52 |
| 92 | 启用 | 75 | MAIN - Wanted corrupted affix (any tier) | FLAY X53 |
| 93 | 启用 | 75 | MAIN - Wanted corrupted affix (any tier) | FLAY X54 |
| 94 | 启用 | 75 | MAIN - Wanted corrupted affix (any tier) | FLAY X55 |
| 95 | 启用 | 75 | MAIN - Wanted corrupted affix (any tier) | FLAY X56 |
| 96 | 启用 | 75 | SECONDARY - Wanted corrupted affix (any tier) | NECRO X61 |
| 97 | 启用 | 75 | SECONDARY - Wanted corrupted affix (any tier) | NECRO X62 |
| 98 | 启用 | 75 | SECONDARY - Wanted corrupted affix (any tier) | NECRO X63 |
| 99 | 启用 | 75 | SECONDARY - Wanted corrupted affix (any tier) | NECRO X64 |
| 100 | 启用 | 75 | SECONDARY - Wanted corrupted affix (any tier) | NECRO X66 |
| 101 | 启用 | 75 | SECONDARY - Wanted corrupted affix (any tier) | NECRO X67 |
| 102 | 启用 | 75 | SECONDARY - Wanted corrupted affix (any tier) | NECRO X68 |
| 103 | 关闭 | 81 | OFF - Ascend target not requested | raxx |
| 104 | 启用 | 82 | SECONDARY - Rare Strict Two-Handed Axe | NECRO X28 |
| 105 | 启用 | 82 | SECONDARY - Rare Strict Helmet | NECRO X29 |
| 106 | 启用 | 82 | SECONDARY - Rare Strict Boots | NECRO X30 |
| 107 | 启用 | 82 | SECONDARY - Rare Strict Gloves | NECRO X31 |
| 108 | 启用 | 82 | SECONDARY - Rare Strict Ring | NECRO X32 |
| 109 | 启用 | 83 | MAIN - Shatter / Removal (Edit Affixes) | FLAY X26 |
| 110 | 启用 | 83 | SECONDARY - Shatter / Removal (Edit Affixes) | NECRO X36 |
| 111 | 启用 | 84 | SECONDARY - Shatter / Removal (Class Specific Affixes) | NECRO X37 |
| 112 | 关闭 | 85 | OFF - Mage shards not requested | raxx |
| 113 | 关闭 | 86 | OFF - Primalist shards not requested | raxx |
| 114 | 关闭 | 87 | OFF - Rogue shards not requested | raxx |
| 115 | 关闭 | 88 | OFF - Sentinel shards not requested | raxx |
| 116 | 关闭 | 89 | OFF - Extra offensive shard inventory not supplied | raxx |
| 117 | 启用 | 90 | MAIN - Shatter / Removal - Increased Health (60) | FLAY X24; NECRO X34 |
| 118 | 启用 | 90 | MAIN - Shatter / Removal - Increased Health T3+ (80) | FLAY X25; NECRO X35 |
| 119 | 启用 | 99 | MAIN - Planner idol combination | Planner JSON [26, 1, [843, 854]] |
| 120 | 启用 | 99 | MAIN - Planner idol combination | Planner JSON [28, 1, [876, 886]] |
| 121 | 启用 | 99 | SECONDARY - Planner idol combination | Planner JSON [30, 8, [287, 897, 941]] |
| 122 | 启用 | 99 | SECONDARY - Planner idol combination | Planner JSON [27, 1, [319, 862]] |
| 123 | 启用 | 99 | SECONDARY - Planner idol combination | Planner JSON [26, 1, [846, 851]] |
| 124 | 启用 | 99 | SECONDARY - Planner idol combination | Planner JSON [26, 1, [846, 852]] |
| 125 | 启用 | 99 | SECONDARY - Planner idol combination | Planner JSON [27, 1, [862, 870]] |
| 126 | 启用 | 99 | SECONDARY - Planner idol combination | Planner JSON [26, 1, [846, 855]] |
| 127 | 启用 | 99 | MAIN - Ignite + Frailty fallback | guide_idol |
| 128 | 启用 | 99 | MAIN - Strict - Minor Idols | FLAY X21 |
| 129 | 启用 | 99 | MAIN - Strict - Stout Idols | FLAY X22 |
| 130 | 启用 | 99 | SECONDARY - Strict - Minor Idols | NECRO X24 |
| 131 | 启用 | 99 | SECONDARY - Strict - Humble Idols | NECRO X25 |
| 132 | 启用 | 99 | SECONDARY - Strict - Large Idols | NECRO X26 |
| 133 | 启用 | 99 | SECONDARY - Strict - Large Omen Idols | NECRO X27 |
| 134 | 启用 | 127 | MAIN - Suffix Effect Idol Altar (Tier 7 Equivalent) | FLAY X45 |
| 135 | 启用 | 127 | MAIN - Prefix Effect Idol Altar (Tier 7 Equivalent) | FLAY X46 |
| 136 | 启用 | 127 | MAIN - Generic Good Altars (Double Exalted) | FLAY X47; NECRO X59 |
| 137 | 启用 | 127 | MAIN - Tier 7 Strict Idol Altar | FLAY X72 |
| 138 | 启用 | 127 | SECONDARY - Suffix Effect Idol Altar (Tier 7 Equivalent) | NECRO X57 |
| 139 | 启用 | 127 | SECONDARY - Prefix Effect Idol Altar (Tier 7 Equivalent) | NECRO X58 |
| 140 | 启用 | 127 | SECONDARY - Tier 7 Strict Idol Altar | NECRO X83 |
| 141 | 启用 | 127 | MAIN - Generic Good Altars (Min. Tier 6) | FLAY X42; NECRO X54 |
| 142 | 启用 | 127 | MAIN - Suffix Effect Idol Altar (Tier 6 Equivalent) | FLAY X43 |
| 143 | 启用 | 127 | MAIN - Prefix Effect Idol Altar (Tier 6 Equivalent) | FLAY X44 |
| 144 | 启用 | 127 | MAIN - Tier 6 Strict Idol Altar | FLAY X59 |
| 145 | 启用 | 127 | SECONDARY - Suffix Effect Idol Altar (Tier 6 Equivalent) | NECRO X55 |
| 146 | 启用 | 127 | SECONDARY - Prefix Effect Idol Altar (Tier 6 Equivalent) | NECRO X56 |
| 147 | 启用 | 127 | SECONDARY - Tier 6 Strict Idol Altar | NECRO X70 |
| 148 | 启用 | 127 | MAIN - Guide armor altar base (inspect manually) | guide_altar |
| 149 | 启用 | 128 | MAIN - 1 Affix - Minor Idols | FLAY X17 |
| 150 | 启用 | 128 | MAIN - 1 Affix - Stout Idols | FLAY X18 |
| 151 | 启用 | 128 | SECONDARY - 1 Affix - Minor Idols | NECRO X18 |
| 152 | 启用 | 128 | SECONDARY - 1 Affix - Humble Idols | NECRO X19 |
| 153 | 启用 | 128 | SECONDARY - 1 Affix - Large Idols | NECRO X20 |
| 154 | 启用 | 128 | SECONDARY - 1 Affix - Large Omen Idols | NECRO X21 |
| 155 | 启用 | 128 | MAIN - Optional critical avoidance corruption | guide_idol |
| 156 | 启用 | 129 | MAIN - Strict - Weaver Idols | FLAY X19; NECRO X22 |
| 157 | 启用 | 129 | MAIN - Reflect Idols (Alt Leveling) | FLAY X20; NECRO X23 |
| 158 | 启用 | 134 | All Exalts or Better - Turns off at 60 | raxx |
| 159 | 启用 | 135 | Campaign Idols - Turns off at 60 | raxx |
| 160 | 关闭 | 136 | OFF - Campaign weapon bases not supplied | raxx |
| 161 | 关闭 | 137 | OFF - Campaign offhand bases not supplied | raxx |
| 162 | 启用 | 138 | BIS Campaign Amulet Bases - Turns off at 60 | raxx |
| 163 | 启用 | 139 | BIS Campaign Belt Bases - Turns off at 60 | raxx |
| 164 | 启用 | 140 | BIS Campaign Body Armor Bases - Turns off at 60 | raxx |
| 165 | 启用 | 141 | BIS Campaign Boot Bases - Turns off at 60 | raxx |
| 166 | 启用 | 142 | BIS Campaign Helmet Bases - Turns off at 60 | raxx |
| 167 | 启用 | 143 | BIS Campaign Ring Bases - Turns off at 60 | raxx |
| 168 | 启用 | 144 | BIS Campaign Glove Bases - Turns off at 60 | raxx |
| 169 | 启用 | 145 | BIS Campaign Relic Bases - Turns off at 60 | raxx |
| 170 | 启用 | 146 | Shatter T3+ Phys Res / All Health - Turns off at 50 | raxx |
| 171 | 启用 | 147 | Shatter T3+ Movespeed & CDR - Turns off at 50 | raxx |
| 172 | 启用 | 148 | Shatter T3+ Resistances - Turns off at 50 | raxx |
| 173 | 启用 | 149 | T2+ Phys Res / All Health - Turns off at 30 | raxx |
| 174 | 启用 | 150 | T2+ Movespeed & CDR - Turns off at 30 | raxx |
| 175 | 启用 | 151 | T2+ Resistances - Turns off at 30 | raxx |
| 176 | 关闭 | 152 | OFF - Bow not used | raxx |
| 177 | 启用 | 153 | Early Melee Wpns - Turns off at 30 | raxx |
| 178 | 关闭 | 154 | OFF - Wand/staff not used | raxx |
| 179 | 启用 | 155 | All Rares - Turns off at 30 | raxx |
| 180 | 启用 | 156 | Early Relics - Turns off at 12 | raxx |
| 181 | 关闭 | 157 | OFF - Catalyst not used | raxx |
| 182 | 关闭 | 158 | OFF - Quiver not used | raxx |
| 183 | 关闭 | 159 | OFF - Shield not used | raxx |
| 184 | 启用 | 160 | Silver Ring - Turns off at 12 | raxx |
| 185 | 启用 | 161 | Ruby Amulet - Turns off at 12 | raxx |
| 186 | 启用 | 162 | All Items - Turns off at 10 | raxx |
| 187 | 启用 | 163 |  | raxx |
