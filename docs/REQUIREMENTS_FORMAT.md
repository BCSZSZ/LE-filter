# 共通BD需求JSON v1

一份文件表示一个BD、一个阶段的收集目标。filter提取结果与攻略提取结果使用同一格式；网页导入、列表编辑、保存回读，再由`tool/engine.py`填入基底生成XML。来源只提供目标，基底决定收集层级、声音、颜色与顺序。

```json
{
  "format": "le-filter-requirements",
  "version": 1,
  "id": "example-bd",
  "name": "示例BD",
  "stage": "endgame",
  "targets": {
    "uniques": [253, 416],
    "equipment": [
      {"type": "BODY_ARMOR", "bases": [], "affixes": [406, 192]}
    ],
    "altars": [
      {"type": "IDOL_ALTAR", "bases": [12], "affixes": [1094, 1089, 1102, 1100]}
    ],
    "idols": [
      {"type": "IDOL_1x3", "bases": [13], "affixes": [266, 287]}
    ],
    "bases": [
      {"type": "RELIC", "bases": [18]}
    ]
  }
}
```

| 字段 | 含义 |
|---|---|
| `id` | BD的稳定标识。同id导入更新该BD；另一个独立BD需要不同id。 |
| `name` | 玩家可读名称，可修改。 |
| `stage` | `endgame`终局或`leveling`独立练级目标；两个阶段不自动复制。 |
| `targets.uniques` | 暗金／套装数字ID列表。名字由离线词库显示。 |
| `targets.equipment` | 每个装备类型独立目标池，不能跨部位或BD凑目标数量。实验词缀可作为明确目标。 |
| `targets.altars` | 祭坛类型、底材与普通词缀池。 |
| `targets.idols` | 神像类型、底材与普通词缀池；附魔／腐化不混入普通池。 |
| `targets.bases` | 独立制作底材，只填`type`与`bases`。不自动限制装备T7素材的底材。 |
| `source`（可选） | 来源名称、URL、更新日期、范围、哈希与审阅提醒；不参与过滤判断。 |

五类`targets`字段必须齐全，没有需求就填`[]`。分组的`bases: []`表示该类型底材不限；ID必须是整数。`affixes`是候选池，不表示要求物品同时拥有池中全部词缀，也不承诺池中任意组合都是BD最终毕业。

装备／神像／祭坛分组可带`corrupted`及`enchanted`参考ID列表，分别只接受冻结词库腐化6／附魔4；不会计入普通目标。神像普通池只接受0／5。装备普通池拒绝4／6。未知ID阻止导入／生成，不猜名字或类别。神像还可选填`pair_bases`：限定两项目标层底材；不填表示与`bases`相同，明确`[]`表示两项层底材不限。

格式不保存主副身份、勾选状态、声音／地图提示、LP／WW、T7门槛、规则编号、练级R分段覆盖或原Strict筛选条件。它们留在工具配置和基底。右上角“保存配置”备份全部BD与这些设置；左侧“保存本BD需求JSON”只保存正在编辑的BD、当前阶段的五类目标及来源。

新id导入为未勾选的可编辑BD，审阅后再决定是否收集。导入同id时替换当前文件`stage`的五类目标和来源，保留另一个阶段、勾选状态、主副身份及已填写的`leveling_slots`。练级阶段的独立需求可以另存一份`stage: "leveling"`文件；原Raxx等级分段和具体分段目标覆盖仍在工具第六入口填写。

程序接口：

```python
from requirements import read_document, write_document

data = read_document(document)  # 校验并转成生成器可用的profile
document = write_document(build, "endgame")  # 编辑后的目标保存回同一格式
```

本地HTTP接口为`POST /api/requirements/import`（`{"document": ...}`）及`POST /api/requirements/export`（`{"build": ..., "stage": "endgame"}`）。XML导入仍由`extract(xml)`提取profile；加入BD后使用相同的`write_document`保存，随后JSON与攻略结果走同一转换路径。

本次真实样本见[流血骷髅需求](../requirements/bleed-skeleton-roamer-guide-835.endgame.json)与[中文审阅表](BLEED_SKELETON_GUIDE_REVIEW.md)。
