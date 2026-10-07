# 赛季暗金通用保护名单

范围：1.3、1.4、1.5新增的全部暗金，含先古暗金与暗金神像。按版本新增名单收集，不局限于赛季机制限定掉落。共55种，其中先古25种、暗金神像4种。

## 生成规则

- 一条“通用暗金／套装0LP保护”：原R15珍贵暗金＋原R16套装＋本名单，共170种；默认启用，不受角色等级或BD勾选影响。
- 本名单只检查物品ID，不要求LP、WW、词缀或属性数值。原珍贵名单中已收录的赛季暗金解除其Rolls条件；其他旧暗金／套装的原条件保留。
- 非BD的0LP赛季暗金使用铁匠档；BD目标仍先命中主粉／副蓝规则。更高LP／WW层在前，沿用四档提示。
- 原珍贵名单低WW静音子层保留；它有独立提示用途。原R12／13／14的LP与WW混合兜底被拆分规则覆盖，不再重复生成。
- 保护范围属于生成器基底政策，不写入各BD需求JSON。冻结Raxx原文、Base v1和历史XML不改；新网页导出使用更新后的策略。

## 来源与维护

名单取自Last Epoch Tools各版本“New items”实际物品链接。链接key用lz-string 1.5.0解码，末三位为Unique ID，并逐项与冻结version150词库的名字及类型交叉核对。先古标记从已验证SHA256的数据库脚本`isPrimordialItem`读取；25种先古全部在名单中。运行期只读取冻结JSON，不联网提取。

- [官方1.3先古机制说明](https://forum.lastepoch.com/t/primal-hunt-coming-to-last-epoch-august-21st/78569)
- [官方1.5新增暗金说明](https://forum.lastepoch.com/t/new-uniques-coming-to-last-epoch-october-1/81777)
- 冻结名单与来源：[seasonal-unique-protection.json](../sources/seasonal-unique-protection.json)

后续版本需先核对新版本的新增暗金页、数字ID、是否仍可掉落，再向冻结名单追加该版本。不得以ID区间猜新增物品，也不得从任何BD清单推断赛季通用保护。

## 1.3：30种

[版本新增物品来源](https://www.lastepochtools.com/db/version/version130/new/items)

| ID | 中文名 | 英文名 | 类别 |
|---|---|---|---|
| 420 | 处刑者的献祭 | Executioner's Tithe | 暗金装备 |
| 421 | 亘古之壤 | The Land Before | 暗金神像 |
| 422 | 瓶中闪电 | Lightning in a Bottle | 暗金装备 |
| 423 | 传奇交织 | Legends Entwined | 先古暗金 |
| 424 | 暴君颅骨 | Tyrant's Skull | 先古暗金 |
| 425 | 野火余烬 | Wildfire Embers | 先古暗金 |
| 426 | 眩光棘林 | Thicket of Blinding Light | 先古暗金 |
| 427 | 原初谐律 | Harmony of the First | 先古暗金 |
| 428 | 棘影猛攻 | Onslaught of Cerata | 先古暗金 |
| 429 | 不朽石之花 | Blossom of Immortal Stone | 先古暗金 |
| 430 | 阿努洛克的合唱 | Chorus of the Anurok | 先古暗金 |
| 431 | 创世残骸 | Carrion of Creation | 先古暗金 |
| 432 | 骨火之角 | Horn of the Bone Wisp | 先古暗金 |
| 433 | 神圣巢穴 | Reliquary Nest | 先古暗金 |
| 434 | 冷漠面具 | Mask of Indifference | 先古暗金 |
| 435 | 原识永存 | Permanence of Primal Knowledge | 先古暗金 |
| 436 | 纷争之翼 | Wings of Discord | 先古暗金 |
| 437 | 原始节奏 | Primal Cadence | 先古暗金 |
| 438 | 磨石木槌 | Whetstone Gavel | 先古暗金 |
| 439 | 真视玻璃 | Truesight Glass | 先古暗金 |
| 440 | 蓝羽绑带 | Bluefeather Band | 先古暗金 |
| 441 | 多头蛇弧光 | Hydra Arc | 先古暗金 |
| 442 | 维洛西恩之颌 | Velocyn's Jaw | 先古暗金 |
| 443 | 肌肤大军 | Army of Skin | 暗金装备 |
| 444 | 进化终焉 | Evolution's End | 暗金装备 |
| 445 | 灵体木质部 | Spirit Xylem | 先古暗金 |
| 446 | 狂战士之牙 | Fangs of the Berserker | 先古暗金 |
| 447 | 先祖集群之骨 | Bones of the Ancestral Pack | 先古暗金 |
| 448 | 星血筑师 | Architects of Astral Blood | 先古暗金 |
| 449 | 屠夫冠冕 | The Butcher's Crown | 先古暗金 |

## 1.4：9种

[版本新增物品来源](https://www.lastepochtools.com/db/version/version140/new/items)

| ID | 中文名 | 英文名 | 类别 |
|---|---|---|---|
| 450 | 不屈冲锋 | Unbroken Charge | 暗金装备 |
| 458 | 朝暮足袋 | Tabi of Dusk and Dawn | 暗金装备 |
| 459 | 毁灭机巧 | Artifice of Devastation | 暗金装备 |
| 460 | 劳普的足迹 | Laup's Path | 暗金装备 |
| 461 | 灰烬觉醒 | Ash Wake | 暗金装备 |
| 462 | 自然之怒 | Natural Wrath | 暗金神像 |
| 463 | 瑞耶之拥 | Rahyeh's Embrace | 暗金装备 |
| 469 | 流亡 | Exulis | 暗金装备 |
| 470 | 毁灭之眼 | Oculus of Ruin | 暗金装备 |

## 1.5：16种

[版本新增物品来源](https://www.lastepochtools.com/db/version/version150/new/items)

| ID | 中文名 | 英文名 | 类别 |
|---|---|---|---|
| 471 | 不屈军团 | Unbroken Legion | 暗金装备 |
| 472 | 赫罗特的憩息 | Heorot's Repose | 暗金装备 |
| 473 | 永恒之池 | Eternal Font | 暗金装备 |
| 474 | 融合元素 | Fused Elements | 暗金装备 |
| 475 | 吞噬知识 | Devoured Knowledge | 暗金装备 |
| 476 | 死亡之舞 | Death Dance | 暗金装备 |
| 477 | 不息狂怒 | Unsated Rage | 暗金装备 |
| 478 | 幻灵赠礼 | Gift of the Eidolon | 暗金装备 |
| 479 | 抵御元素 | Withstand the Elements | 暗金装备 |
| 480 | 险境映像 | Perilous Reflection | 暗金装备 |
| 483 | 牧人的纪念品 | Wrangler's Keepsake | 暗金装备 |
| 484 | 奔放誓言 | Effusive Oath | 暗金装备 |
| 485 | 焦土 | Scorched Earth | 暗金神像 |
| 486 | 霜生孤寂 | Frostborn Solitude | 暗金神像 |
| 487 | 囚禁之迹 | Vestige of Imprisonment | 暗金装备 |
| 488 | 莫迪塔斯的复仇 | Morditas' Vengeance | 暗金装备 |
