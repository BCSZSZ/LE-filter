# Maxroll Strict 完整规则定位索引

由 scripts/analyze_maxroll_filters.py 离线生成。X编号是XML物理位置，不是Raxx的Order编号；两份文件均无Order。完整条件、重复Uniques对象、nil与显示字段保存在analysis/maxroll-strict.json；原始XML保持字节不变。

## Skeleton Necromancer

来源：[原始XML](../sources/builds/maxroll-skeleton-necromancer-strict.xml)。

| X编号 | 状态／动作 | 原始名称 | 条件类型，完整字段见机器索引 |
|---:|---|---|---|
| X1 | 启用/HIDE | All Items | CharacterLevelCondition |
| X2 | 启用/SHOW | Runes | RuneCondition |
| X3 | 启用/SHOW | Important Runes | RuneCondition |
| X4 | 启用/SHOW | Important Glyphs | GlyphCondition |
| X5 | 启用/SHOW | Woven Echoes | WovenEchoesCondition |
| X6 | 启用/SHOW | Keys & Currency | KeysCondition |
| X7 | 启用/SHOW | Crystallized Heart | KeysCondition |
| X8 | 启用/SHOW | Temporal Keystone | KeysCondition |
| X9 | 关闭/SHOW | Movement Speed Rings (10) | SubTypeCondition、CharacterLevelCondition |
| X10 | 关闭/SHOW | Champion Affixes (40) | AffixCondition、CharacterLevelCondition |
| X11 | 关闭/SHOW | Personal Affixes (40) | AffixCondition、CharacterLevelCondition |
| X12 | 关闭/SHOW | Experimental Affixes (40) | AffixCondition、CharacterLevelCondition |
| X13 | 启用/SHOW | Wanted Experimental Affixes | AffixCondition |
| X14 | 关闭/SHOW | All Idols (35) | SubTypeCondition、CharacterLevelCondition |
| X15 | 关闭/SHOW | Generic Resistances & Health Idols (75) | AffixCondition、SubTypeCondition、CharacterLevelCondition |
| X16 | 关闭/SHOW | All Altars | SubTypeCondition |
| X17 | 关闭/SHOW | Corrupted Items | CorruptionCondition |
| X18 | 启用/SHOW | 1 Affix - Minor Idols | SubTypeCondition、AffixCondition |
| X19 | 启用/SHOW | 1 Affix - Humble Idols | SubTypeCondition、AffixCondition |
| X20 | 启用/SHOW | 1 Affix - Large Idols | SubTypeCondition、AffixCondition |
| X21 | 启用/SHOW | 1 Affix - Large Omen Idols | AffixCondition、SubTypeCondition |
| X22 | 启用/SHOW | Strict - Weaver Idols | AffixCondition、SubTypeCondition |
| X23 | 启用/SHOW | Reflect Idols (Alt Leveling) | AffixCondition |
| X24 | 启用/SHOW | Strict - Minor Idols | SubTypeCondition、AffixCondition |
| X25 | 启用/SHOW | Strict - Humble Idols | SubTypeCondition、AffixCondition |
| X26 | 启用/SHOW | Strict - Large Idols | SubTypeCondition、AffixCondition |
| X27 | 启用/SHOW | Strict - Large Omen Idols | AffixCondition、SubTypeCondition |
| X28 | 启用/SHOW | Rare Strict Two-Handed Axe | SubTypeCondition、AffixCondition |
| X29 | 启用/SHOW | Rare Strict Helmet | SubTypeCondition、AffixCondition |
| X30 | 启用/SHOW | Rare Strict Boots | SubTypeCondition、AffixCondition |
| X31 | 启用/SHOW | Rare Strict Gloves | SubTypeCondition、AffixCondition |
| X32 | 启用/SHOW | Rare Strict Ring | SubTypeCondition、AffixCondition |
| X33 | 关闭/SHOW | CoF Rune of Ascendance (Select Item Type) | FactionCondition、SubTypeCondition、PotentialCondition |
| X34 | 启用/SHOW | Shatter / Removal - Increased Health (60) | CharacterLevelCondition、AffixCondition |
| X35 | 启用/SHOW | Shatter / Removal - Increased Health T3+ (80) | AffixCondition、CharacterLevelCondition |
| X36 | 启用/SHOW | Shatter / Removal (Edit Affixes) | AffixCondition |
| X37 | 启用/SHOW | Shatter / Removal (Class Specific Affixes) | AffixCondition |
| X38 | 关闭/SHOW | Any Tier 7 Suffixes (Rune of Redemption) | AffixCondition、SubTypeCondition、CorruptionCondition、RarityCondition |
| X39 | 关闭/SHOW | Any Tier 7 Prefixes (Rune of Redemption) | AffixCondition、SubTypeCondition、CorruptionCondition、RarityCondition |
| X40 | 关闭/SHOW | Open Prefix & Tier 7 (Rune of Havoc) | SubTypeCondition、CorruptionCondition、AffixCondition、AffixCountCondition、PotentialCondition |
| X41 | 关闭/SHOW | Open Suffix & Tier 7 (Rune of Havoc) | SubTypeCondition、CorruptionCondition、AffixCondition、AffixCountCondition、PotentialCondition |
| X42 | 启用/SHOW | Wanted Affix & Tier 7 (Rune of Havoc) | AffixCondition、SubTypeCondition、CorruptionCondition、AffixCondition、PotentialCondition |
| X43 | 启用/SHOW | Wanted Experimental & Tier 7 (Rune of Havoc) | AffixCondition、AffixCondition、SubTypeCondition、CorruptionCondition、PotentialCondition |
| X44 | 启用/SHOW | Tier 7 Highly Craftable Items (52+ FP) | SubTypeCondition、CorruptionCondition、AffixCondition、AffixCountCondition、PotentialCondition |
| X45 | 启用/SHOW | Tier 7 Eternal Gauntlets | AffixCondition、SubTypeCondition、CorruptionCondition、PotentialCondition |
| X46 | 关闭/SHOW | Tier 7 Rings & Amulets | AffixCondition、SubTypeCondition、CorruptionCondition、PotentialCondition |
| X47 | 关闭/SHOW | 无名称 | RarityCondition |
| X48 | 关闭/SHOW | Rare Set Items | UniqueModifiersCondition |
| X49 | 关闭/SHOW | Unique Items | RarityCondition |
| X50 | 启用/SHOW | Cocooned Uniques | UniqueModifiersCondition |
| X51 | 启用/SHOW | Primordial Uniques | UniqueModifiersCondition |
| X52 | 关闭/SHOW | 无名称 | RarityCondition、CorruptionCondition |
| X53 | 启用/SHOW | Unique Idols | UniqueModifiersCondition |
| X54 | 启用/SHOW | Generic Good Altars (Min. Tier 6) | SubTypeCondition、AffixCondition |
| X55 | 启用/SHOW | Suffix Effect Idol Altar (Tier 6 Equivalent) | SubTypeCondition、AffixCondition |
| X56 | 启用/SHOW | Prefix Effect Idol Altar (Tier 6 Equivalent) | SubTypeCondition、AffixCondition |
| X57 | 启用/SHOW | Suffix Effect Idol Altar (Tier 7 Equivalent) | SubTypeCondition、AffixCondition |
| X58 | 启用/SHOW | Prefix Effect Idol Altar (Tier 7 Equivalent) | SubTypeCondition、AffixCondition |
| X59 | 启用/SHOW | Generic Good Altars (Double Exalted) | SubTypeCondition、AffixCondition |
| X60 | 关闭/SHOW | Tier 6 Wanted Affixes (Can Edit Affixes & Item Type) | AffixCondition、SubTypeCondition、CorruptionCondition |
| X61 | 启用/SHOW | Tier 6 - Relic | AffixCondition、CorruptionCondition、SubTypeCondition |
| X62 | 启用/SHOW | Tier 6 - Ring | AffixCondition、CorruptionCondition、SubTypeCondition |
| X63 | 启用/SHOW | Tier 6 - Amulet | AffixCondition、CorruptionCondition、SubTypeCondition |
| X64 | 启用/SHOW | Tier 6 - Gloves | AffixCondition、CorruptionCondition、SubTypeCondition |
| X65 | 启用/SHOW | Tier 6 - Boots | AffixCondition、CorruptionCondition、SubTypeCondition |
| X66 | 启用/SHOW | Tier 6 - Belt | AffixCondition、CorruptionCondition、SubTypeCondition |
| X67 | 启用/SHOW | Tier 6 - Body Armor | AffixCondition、CorruptionCondition、SubTypeCondition |
| X68 | 启用/SHOW | Tier 6 - Helmet | AffixCondition、CorruptionCondition、SubTypeCondition |
| X69 | 启用/SHOW | Tier 6 - Two-Handed Axe | AffixCondition、CorruptionCondition、SubTypeCondition |
| X70 | 启用/SHOW | Tier 6 Strict Idol Altar | SubTypeCondition、AffixCondition |
| X71 | 启用/SHOW | Exalted Bases for Alt Leveling Setup (T7) | CorruptionCondition、AffixCondition、SubTypeCondition |
| X72 | 关闭/SHOW | Wanted Tier 7 (Can Edit Affixes & Item Type) | AffixCondition、SubTypeCondition、CorruptionCondition |
| X73 | 启用/SHOW | Tier 7 - Relic | AffixCondition、CorruptionCondition、SubTypeCondition |
| X74 | 启用/SHOW | Tier 7 - Ring | AffixCondition、CorruptionCondition、SubTypeCondition |
| X75 | 启用/SHOW | Tier 7 - Amulet | AffixCondition、CorruptionCondition、SubTypeCondition |
| X76 | 启用/SHOW | Tier 7 - Gloves | AffixCondition、CorruptionCondition、SubTypeCondition |
| X77 | 启用/SHOW | Tier 7 - Boots | AffixCondition、CorruptionCondition、SubTypeCondition |
| X78 | 启用/SHOW | Tier 7 - Belt | AffixCondition、CorruptionCondition、SubTypeCondition |
| X79 | 启用/SHOW | Tier 7 - Body Armor | AffixCondition、CorruptionCondition、SubTypeCondition |
| X80 | 启用/SHOW | Tier 7 - Helmet | AffixCondition、CorruptionCondition、SubTypeCondition |
| X81 | 启用/SHOW | Tier 7 - Two-Handed Axe | AffixCondition、CorruptionCondition、SubTypeCondition |
| X82 | 启用/SHOW | Tier 7 - Class Specific Affixes | AffixCondition、CorruptionCondition |
| X83 | 启用/SHOW | Tier 7 Strict Idol Altar | SubTypeCondition、AffixCondition |
| X84 | 启用/SHOW | Multi Exalted (Min. Tier 7 & Tier 6) | AffixCondition、AffixCondition、CorruptionCondition |
| X85 | 启用/SHOW | Multi Exalted (Min. 2 Tier 7) | AffixCondition、CorruptionCondition |
| X86 | 启用/SHOW | Triple+ Exalted (Min. 1 Tier 7) | AffixCondition、AffixCondition、CorruptionCondition |
| X87 | 启用/SHOW | Corrupted Multi Exalted (Min. Tier 7 & Tier 6) | AffixCondition、AffixCondition、RarityCondition、CorruptionCondition |
| X88 | 关闭/SHOW | Uniques with 1 LP (All) | RarityCondition、UniqueModifiersCondition、PotentialCondition |
| X89 | 启用/SHOW | Dungeons / Arena Uniques | UniqueModifiersCondition |
| X90 | 启用/SHOW | Rare Dungeon Drops | UniqueModifiersCondition |
| X91 | 启用/SHOW | Rare Monolith Timeline Boss Drops | UniqueModifiersCondition |
| X92 | 启用/SHOW | Harbinger Uniques | UniqueModifiersCondition |
| X93 | 启用/SHOW | Very Rare Uniques (80% Reroll Chance) | UniqueModifiersCondition |
| X94 | 启用/SHOW | Very Rare Uniques (85% Reroll Chance) | UniqueModifiersCondition |
| X95 | 启用/SHOW | Very Rare Uniques (90% Reroll Chance) | UniqueModifiersCondition |
| X96 | 启用/SHOW | Woven Echoes Uniques | UniqueModifiersCondition |
| X97 | 启用/SHOW | Exiled Mage Uniques | UniqueModifiersCondition |
| X98 | 启用/SHOW | Shade of Orobyss Uniques | UniqueModifiersCondition |
| X99 | 启用/SHOW | Aberroth Uniques | UniqueModifiersCondition |
| X100 | 启用/SHOW | Vision of the Observer Uniques | UniqueModifiersCondition |
| X101 | 启用/SHOW | Morditas Uniques | UniqueModifiersCondition |
| X102 | 启用/SHOW | Final Rift Beast - Evolution's End | UniqueModifiersCondition |
| X103 | 启用/SHOW | Dungeons / Arena Uniques - 1 LP+ | UniqueModifiersCondition、PotentialCondition |
| X104 | 启用/SHOW | Rare Dungeon Drops - 1 LP+ | UniqueModifiersCondition、PotentialCondition |
| X105 | 启用/SHOW | Rare Monolith Timeline Boss Drops - 1 LP+ | UniqueModifiersCondition、PotentialCondition |
| X106 | 启用/SHOW | Harbinger Uniques - 1 LP+ | UniqueModifiersCondition、PotentialCondition |
| X107 | 启用/SHOW | Very Rare Uniques With 1 LP (80% Reroll Chance) | UniqueModifiersCondition、PotentialCondition |
| X108 | 启用/SHOW | Very Rare Uniques With 1 LP(85% Reroll Chance) | UniqueModifiersCondition、PotentialCondition |
| X109 | 启用/SHOW | Very Rare Uniques With 1 LP (90% Reroll Chance) | UniqueModifiersCondition、PotentialCondition |
| X110 | 启用/SHOW | Woven Echoes Uniques - 1 LP+ | UniqueModifiersCondition、PotentialCondition |
| X111 | 启用/SHOW | Exiled Mage Uniques - 1 LP+ | UniqueModifiersCondition、PotentialCondition |
| X112 | 启用/SHOW | Shade of Orobyss Uniques - 1 LP+ | UniqueModifiersCondition、PotentialCondition |
| X113 | 启用/SHOW | Aberroth Uniques - 1 LP+ | UniqueModifiersCondition、PotentialCondition |
| X114 | 启用/SHOW | Morditas Uniques - 1 LP+ | UniqueModifiersCondition、PotentialCondition |
| X115 | 启用/SHOW | Final Rift Beast - Evolution's End - 1 LP+ | UniqueModifiersCondition |
| X116 | 启用/SHOW | Any Class Alt Leveling Uniques - Campaign | UniqueModifiersCondition、PotentialCondition、CorruptionCondition |
| X117 | 启用/SHOW | Any Class Alt Leveling Uniques - Reflect  lvl 35 | UniqueModifiersCondition、PotentialCondition、CorruptionCondition |
| X118 | 关闭/SHOW | Weaver's Will Items | PotentialCondition |
| X119 | 启用/SHOW | Uniques With 21+ Weaver's Will (≤1% - 30+ LPL) | PotentialCondition、UniqueModifiersCondition |
| X120 | 启用/SHOW | Uniques With 20+ Weaver's Will (≤1% - 40+ LPL) | PotentialCondition、UniqueModifiersCondition |
| X121 | 启用/SHOW | Uniques With 19+ Weaver's Will (≤1% - 50+ LPL) | PotentialCondition、UniqueModifiersCondition |
| X122 | 启用/SHOW | Uniques With 18+ Weaver's Will (≤1% - 68+ LPL) | PotentialCondition、UniqueModifiersCondition |
| X123 | 关闭/SHOW | Uniques With 2 LP (All) | RarityCondition、UniqueModifiersCondition、PotentialCondition |
| X124 | 启用/SHOW | Uniques With 2 LP (≤4% - 48+ LPL) | RarityCondition、UniqueModifiersCondition、PotentialCondition |
| X125 | 启用/SHOW | Uniques With 2 LP (≤1% - 70+ LPL) | RarityCondition、UniqueModifiersCondition、PotentialCondition |
| X126 | 启用/SHOW | Uniques With 2 LP (80% Reroll Chance) | UniqueModifiersCondition、PotentialCondition |
| X127 | 启用/SHOW | Uniques With 2 LP (85% Reroll Chance) | UniqueModifiersCondition、PotentialCondition |
| X128 | 启用/SHOW | Uniques With 2 LP (90% Reroll Chance) | UniqueModifiersCondition、PotentialCondition |
| X129 | 启用/SHOW | Uniques With 3 LP (All) | RarityCondition、UniqueModifiersCondition、PotentialCondition |
| X130 | 启用/SHOW | Uniques With 3 LP (≤1% - 27+ LPL) | RarityCondition、UniqueModifiersCondition、PotentialCondition |
| X131 | 启用/SHOW | Legendary Uniques From Planner (Fail Safe Rule) | UniqueModifiersCondition、RarityCondition |
| X132 | 启用/SHOW | Uniques & Sets From Planner (Optional: Add More) | UniqueModifiersCondition、RarityCondition |
| X133 | 启用/SHOW | Corrupted Uniques & Sets From Planner (Optional: Add More) | UniqueModifiersCondition、RarityCondition、CorruptionCondition |
| X134 | 启用/SHOW | Uniques From Planner 1 LP - Turtle Rule (Optional: Add More) | RarityCondition、UniqueModifiersCondition、PotentialCondition |
| X135 | 启用/SHOW | Uniques From Planner 2 LP (Optional: Add More) | RarityCondition、UniqueModifiersCondition、PotentialCondition |
| X136 | 启用/SHOW | Uniques From Planner 3 LP (Optional: Add More) | RarityCondition、UniqueModifiersCondition、PotentialCondition |
| X137 | 启用/SHOW | Uniques With 2 LP (≤0.1% - 100+ LPL) | RarityCondition、UniqueModifiersCondition、PotentialCondition |
| X138 | 启用/SHOW | Uniques With 3 LP (≤0.1% - 58+ LPL) | RarityCondition、UniqueModifiersCondition、PotentialCondition |
| X139 | 启用/SHOW | Uniques With 22+ Weaver's Will (≤0.6% - All) | PotentialCondition |
| X140 | 启用/SHOW | Uniques With 4 LP (All) | RarityCondition、UniqueModifiersCondition、PotentialCondition |
| X141 | 启用/SHOW | S Tier & Extremely Rare Uniques | UniqueModifiersCondition |

## Flay Mana Lich

来源：[原始XML](../sources/builds/maxroll-flay-mana-lich-strict.xml)。

| X编号 | 状态／动作 | 原始名称 | 条件类型，完整字段见机器索引 |
|---:|---|---|---|
| X1 | 启用/HIDE | All Items | CharacterLevelCondition |
| X2 | 启用/SHOW | Runes | RuneCondition |
| X3 | 启用/SHOW | Important Runes | RuneCondition |
| X4 | 启用/SHOW | Important Glyphs | GlyphCondition |
| X5 | 启用/SHOW | Woven Echoes | WovenEchoesCondition |
| X6 | 启用/SHOW | Keys & Currency | KeysCondition |
| X7 | 启用/SHOW | Crystallized Heart | KeysCondition |
| X8 | 启用/SHOW | Temporal Keystone | KeysCondition |
| X9 | 关闭/SHOW | Movement Speed Rings (10) | SubTypeCondition、CharacterLevelCondition |
| X10 | 关闭/SHOW | Champion Affixes (40) | AffixCondition、CharacterLevelCondition |
| X11 | 关闭/SHOW | Personal Affixes (40) | AffixCondition、CharacterLevelCondition |
| X12 | 关闭/SHOW | Experimental Affixes (40) | AffixCondition、CharacterLevelCondition |
| X13 | 关闭/SHOW | All Idols (35) | SubTypeCondition、CharacterLevelCondition |
| X14 | 关闭/SHOW | Generic Resistances & Health Idols (75) | AffixCondition、SubTypeCondition、CharacterLevelCondition |
| X15 | 关闭/SHOW | All Altars | SubTypeCondition |
| X16 | 关闭/SHOW | Corrupted Items | CorruptionCondition |
| X17 | 启用/SHOW | 1 Affix - Minor Idols | SubTypeCondition、AffixCondition |
| X18 | 启用/SHOW | 1 Affix - Stout Idols | SubTypeCondition、AffixCondition |
| X19 | 启用/SHOW | Strict - Weaver Idols | AffixCondition、SubTypeCondition |
| X20 | 启用/SHOW | Reflect Idols (Alt Leveling) | AffixCondition |
| X21 | 启用/SHOW | Strict - Minor Idols | SubTypeCondition、AffixCondition |
| X22 | 启用/SHOW | Strict - Stout Idols | SubTypeCondition、AffixCondition |
| X23 | 关闭/SHOW | CoF Rune of Ascendance (Select Item Type) | FactionCondition、SubTypeCondition、PotentialCondition |
| X24 | 启用/SHOW | Shatter / Removal - Increased Health (60) | CharacterLevelCondition、AffixCondition |
| X25 | 启用/SHOW | Shatter / Removal - Increased Health T3+ (80) | AffixCondition、CharacterLevelCondition |
| X26 | 启用/SHOW | Shatter / Removal (Edit Affixes) | AffixCondition |
| X27 | 关闭/SHOW | Any Tier 7 Suffixes (Rune of Redemption) | AffixCondition、SubTypeCondition、CorruptionCondition、RarityCondition |
| X28 | 关闭/SHOW | Any Tier 7 Prefixes (Rune of Redemption) | AffixCondition、SubTypeCondition、CorruptionCondition、RarityCondition |
| X29 | 关闭/SHOW | Open Prefix & Tier 7 (Rune of Havoc) | SubTypeCondition、CorruptionCondition、AffixCondition、AffixCountCondition、PotentialCondition |
| X30 | 关闭/SHOW | Open Suffix & Tier 7 (Rune of Havoc) | SubTypeCondition、CorruptionCondition、AffixCondition、AffixCountCondition、PotentialCondition |
| X31 | 启用/SHOW | Wanted Affix & Tier 7 (Rune of Havoc) | AffixCondition、SubTypeCondition、CorruptionCondition、AffixCondition、PotentialCondition |
| X32 | 启用/SHOW | Tier 7 Highly Craftable Items (52+ FP) | SubTypeCondition、CorruptionCondition、AffixCondition、AffixCountCondition、PotentialCondition |
| X33 | 启用/SHOW | Tier 7 Eternal Gauntlets | AffixCondition、SubTypeCondition、CorruptionCondition、PotentialCondition |
| X34 | 关闭/SHOW | Tier 7 Rings & Amulets | AffixCondition、SubTypeCondition、CorruptionCondition、PotentialCondition |
| X35 | 关闭/SHOW | 无名称 | RarityCondition |
| X36 | 关闭/SHOW | Rare Set Items | UniqueModifiersCondition |
| X37 | 关闭/SHOW | Unique Items | RarityCondition |
| X38 | 启用/SHOW | Cocooned Uniques | UniqueModifiersCondition |
| X39 | 启用/SHOW | Primordial Uniques | UniqueModifiersCondition |
| X40 | 关闭/SHOW | 无名称 | RarityCondition、CorruptionCondition |
| X41 | 启用/SHOW | Unique Idols | UniqueModifiersCondition |
| X42 | 启用/SHOW | Generic Good Altars (Min. Tier 6) | SubTypeCondition、AffixCondition |
| X43 | 启用/SHOW | Suffix Effect Idol Altar (Tier 6 Equivalent) | SubTypeCondition、AffixCondition |
| X44 | 启用/SHOW | Prefix Effect Idol Altar (Tier 6 Equivalent) | SubTypeCondition、AffixCondition |
| X45 | 启用/SHOW | Suffix Effect Idol Altar (Tier 7 Equivalent) | SubTypeCondition、AffixCondition |
| X46 | 启用/SHOW | Prefix Effect Idol Altar (Tier 7 Equivalent) | SubTypeCondition、AffixCondition |
| X47 | 启用/SHOW | Generic Good Altars (Double Exalted) | SubTypeCondition、AffixCondition |
| X48 | 关闭/SHOW | Tier 6 Wanted Affixes (Can Edit Affixes & Item Type) | AffixCondition、SubTypeCondition、CorruptionCondition |
| X49 | 启用/SHOW | Tier 6 - Relic | AffixCondition、CorruptionCondition、SubTypeCondition |
| X50 | 启用/SHOW | Tier 6 - Ring | AffixCondition、CorruptionCondition、SubTypeCondition |
| X51 | 启用/SHOW | Tier 6 - Amulet | AffixCondition、CorruptionCondition、SubTypeCondition |
| X52 | 启用/SHOW | Tier 6 - Gloves | AffixCondition、CorruptionCondition、SubTypeCondition |
| X53 | 启用/SHOW | Tier 6 - Boots | AffixCondition、CorruptionCondition、SubTypeCondition |
| X54 | 启用/SHOW | Tier 6 - Belt | AffixCondition、CorruptionCondition、SubTypeCondition |
| X55 | 启用/SHOW | Tier 6 - Body Armor | AffixCondition、CorruptionCondition、SubTypeCondition |
| X56 | 启用/SHOW | Tier 6 - Helmet | AffixCondition、CorruptionCondition、SubTypeCondition |
| X57 | 启用/SHOW | Tier 6 - Dagger | AffixCondition、CorruptionCondition、SubTypeCondition |
| X58 | 启用/SHOW | Tier 6 - One-Handed Axe | AffixCondition、CorruptionCondition、SubTypeCondition |
| X59 | 启用/SHOW | Tier 6 Strict Idol Altar | SubTypeCondition、AffixCondition |
| X60 | 启用/SHOW | Exalted Bases for Alt Leveling Setup (T7) | CorruptionCondition、AffixCondition、SubTypeCondition |
| X61 | 关闭/SHOW | Wanted Tier 7 (Can Edit Affixes & Item Type) | AffixCondition、SubTypeCondition、CorruptionCondition |
| X62 | 启用/SHOW | Tier 7 - Relic | AffixCondition、CorruptionCondition、SubTypeCondition |
| X63 | 启用/SHOW | Tier 7 - Ring | AffixCondition、CorruptionCondition、SubTypeCondition |
| X64 | 启用/SHOW | Tier 7 - Amulet | AffixCondition、CorruptionCondition、SubTypeCondition |
| X65 | 启用/SHOW | Tier 7 - Gloves | AffixCondition、CorruptionCondition、SubTypeCondition |
| X66 | 启用/SHOW | Tier 7 - Boots | AffixCondition、CorruptionCondition、SubTypeCondition |
| X67 | 启用/SHOW | Tier 7 - Belt | AffixCondition、CorruptionCondition、SubTypeCondition |
| X68 | 启用/SHOW | Tier 7 - Body Armor | AffixCondition、CorruptionCondition、SubTypeCondition |
| X69 | 启用/SHOW | Tier 7 - Helmet | AffixCondition、CorruptionCondition、SubTypeCondition |
| X70 | 启用/SHOW | Tier 7 - Dagger | AffixCondition、CorruptionCondition、SubTypeCondition |
| X71 | 启用/SHOW | Tier 7 - One-Handed Axe | AffixCondition、CorruptionCondition、SubTypeCondition |
| X72 | 启用/SHOW | Tier 7 Strict Idol Altar | SubTypeCondition、AffixCondition |
| X73 | 启用/SHOW | Multi Exalted (Min. Tier 7 & Tier 6) | AffixCondition、AffixCondition、CorruptionCondition |
| X74 | 启用/SHOW | Multi Exalted (Min. 2 Tier 7) | AffixCondition、CorruptionCondition |
| X75 | 启用/SHOW | Triple+ Exalted (Min. 1 Tier 7) | AffixCondition、AffixCondition、CorruptionCondition |
| X76 | 启用/SHOW | Corrupted Multi Exalted (Min. Tier 7 & Tier 6) | AffixCondition、AffixCondition、RarityCondition、CorruptionCondition |
| X77 | 关闭/SHOW | Uniques with 1 LP (All) | RarityCondition、UniqueModifiersCondition、PotentialCondition |
| X78 | 启用/SHOW | Dungeons / Arena Uniques | UniqueModifiersCondition |
| X79 | 启用/SHOW | Rare Dungeon Drops | UniqueModifiersCondition |
| X80 | 启用/SHOW | Rare Monolith Timeline Boss Drops | UniqueModifiersCondition |
| X81 | 启用/SHOW | Harbinger Uniques | UniqueModifiersCondition |
| X82 | 启用/SHOW | Very Rare Uniques (80% Reroll Chance) | UniqueModifiersCondition |
| X83 | 启用/SHOW | Very Rare Uniques (85% Reroll Chance) | UniqueModifiersCondition |
| X84 | 启用/SHOW | Very Rare Uniques (90% Reroll Chance) | UniqueModifiersCondition |
| X85 | 启用/SHOW | Woven Echoes Uniques | UniqueModifiersCondition |
| X86 | 启用/SHOW | Exiled Mage Uniques | UniqueModifiersCondition |
| X87 | 启用/SHOW | Shade of Orobyss Uniques | UniqueModifiersCondition |
| X88 | 启用/SHOW | Aberroth Uniques | UniqueModifiersCondition |
| X89 | 启用/SHOW | Vision of the Observer Uniques | UniqueModifiersCondition |
| X90 | 启用/SHOW | Morditas Uniques | UniqueModifiersCondition |
| X91 | 启用/SHOW | Final Rift Beast - Evolution's End | UniqueModifiersCondition |
| X92 | 启用/SHOW | Dungeons / Arena Uniques - 1 LP+ | UniqueModifiersCondition、PotentialCondition |
| X93 | 启用/SHOW | Rare Dungeon Drops - 1 LP+ | UniqueModifiersCondition、PotentialCondition |
| X94 | 启用/SHOW | Rare Monolith Timeline Boss Drops - 1 LP+ | UniqueModifiersCondition、PotentialCondition |
| X95 | 启用/SHOW | Harbinger Uniques - 1 LP+ | UniqueModifiersCondition、PotentialCondition |
| X96 | 启用/SHOW | Very Rare Uniques With 1 LP (80% Reroll Chance) | UniqueModifiersCondition、PotentialCondition |
| X97 | 启用/SHOW | Very Rare Uniques With 1 LP(85% Reroll Chance) | UniqueModifiersCondition、PotentialCondition |
| X98 | 启用/SHOW | Very Rare Uniques With 1 LP (90% Reroll Chance) | UniqueModifiersCondition、PotentialCondition |
| X99 | 启用/SHOW | Woven Echoes Uniques - 1 LP+ | UniqueModifiersCondition、PotentialCondition |
| X100 | 启用/SHOW | Exiled Mage Uniques - 1 LP+ | UniqueModifiersCondition、PotentialCondition |
| X101 | 启用/SHOW | Shade of Orobyss Uniques - 1 LP+ | UniqueModifiersCondition、PotentialCondition |
| X102 | 启用/SHOW | Aberroth Uniques - 1 LP+ | UniqueModifiersCondition、PotentialCondition |
| X103 | 启用/SHOW | Morditas Uniques - 1 LP+ | UniqueModifiersCondition、PotentialCondition |
| X104 | 启用/SHOW | Final Rift Beast - Evolution's End - 1 LP+ | UniqueModifiersCondition |
| X105 | 启用/SHOW | Any Class Alt Leveling Uniques - Campaign | UniqueModifiersCondition、PotentialCondition、CorruptionCondition |
| X106 | 启用/SHOW | Any Class Alt Leveling Uniques - Reflect  lvl 35 | UniqueModifiersCondition、PotentialCondition、CorruptionCondition |
| X107 | 关闭/SHOW | Weaver's Will Items | PotentialCondition |
| X108 | 启用/SHOW | Uniques With 21+ Weaver's Will (≤1% - 30+ LPL) | PotentialCondition、UniqueModifiersCondition |
| X109 | 启用/SHOW | Uniques With 20+ Weaver's Will (≤1% - 40+ LPL) | PotentialCondition、UniqueModifiersCondition |
| X110 | 启用/SHOW | Uniques With 19+ Weaver's Will (≤1% - 50+ LPL) | PotentialCondition、UniqueModifiersCondition |
| X111 | 启用/SHOW | Uniques With 18+ Weaver's Will (≤1% - 68+ LPL) | PotentialCondition、UniqueModifiersCondition |
| X112 | 关闭/SHOW | Uniques With 2 LP (All) | RarityCondition、UniqueModifiersCondition、PotentialCondition |
| X113 | 启用/SHOW | Uniques With 2 LP (≤4% - 48+ LPL) | RarityCondition、UniqueModifiersCondition、PotentialCondition |
| X114 | 启用/SHOW | Uniques With 2 LP (≤1% - 70+ LPL) | RarityCondition、UniqueModifiersCondition、PotentialCondition |
| X115 | 启用/SHOW | Uniques With 2 LP (80% Reroll Chance) | UniqueModifiersCondition、PotentialCondition |
| X116 | 启用/SHOW | Uniques With 2 LP (85% Reroll Chance) | UniqueModifiersCondition、PotentialCondition |
| X117 | 启用/SHOW | Uniques With 2 LP (90% Reroll Chance) | UniqueModifiersCondition、PotentialCondition |
| X118 | 启用/SHOW | Uniques With 3 LP (All) | RarityCondition、UniqueModifiersCondition、PotentialCondition |
| X119 | 启用/SHOW | Uniques With 3 LP (≤1% - 27+ LPL) | RarityCondition、UniqueModifiersCondition、PotentialCondition |
| X120 | 启用/SHOW | Legendary Uniques From Planner (Fail Safe Rule) | UniqueModifiersCondition、RarityCondition |
| X121 | 启用/SHOW | Uniques & Sets From Planner (Optional: Add More) | UniqueModifiersCondition、RarityCondition |
| X122 | 启用/SHOW | Corrupted Uniques & Sets From Planner (Optional: Add More) | UniqueModifiersCondition、RarityCondition、CorruptionCondition |
| X123 | 启用/SHOW | Uniques From Planner 1 LP - Turtle Rule (Optional: Add More) | RarityCondition、UniqueModifiersCondition、PotentialCondition |
| X124 | 启用/SHOW | Uniques From Planner 2 LP (Optional: Add More) | RarityCondition、UniqueModifiersCondition、PotentialCondition |
| X125 | 启用/SHOW | Uniques From Planner 3 LP (Optional: Add More) | RarityCondition、UniqueModifiersCondition、PotentialCondition |
| X126 | 启用/SHOW | Uniques With 2 LP (≤0.1% - 100+ LPL) | RarityCondition、UniqueModifiersCondition、PotentialCondition |
| X127 | 启用/SHOW | Uniques With 3 LP (≤0.1% - 58+ LPL) | RarityCondition、UniqueModifiersCondition、PotentialCondition |
| X128 | 启用/SHOW | Uniques With 22+ Weaver's Will (≤0.6% - All) | PotentialCondition |
| X129 | 启用/SHOW | Uniques With 4 LP (All) | RarityCondition、UniqueModifiersCondition、PotentialCondition |
| X130 | 启用/SHOW | S Tier & Extremely Rare Uniques | UniqueModifiersCondition |
