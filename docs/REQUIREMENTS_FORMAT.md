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
      {"type": "HELMET", "preferred_bases": [70], "bases": [51, 15, 63]}
    ]
  }
}
```

终局独立底材分组的`preferred_bases`表示首选，最多一个；`bases`表示全部替代。两池不能重复。原文没有明确普通首选时留空，不按列举顺序推断。旧JSON未含`preferred_bases`时，原底材全部作为未排序的替代保留。其他四类目标中的`bases`仍表示原有底材范围；练级仍只用`type`与`bases`，不分首选／替代。

生成时每BD、每装备类型合并底材：首选一条、全部替代一条；空池不生成。两条都要求同BD对应部位至少一条目标恰好T7，常驻。首选在替代前，保持原声音和主副颜色；不会逐个替代品增加规则。

| 字段 | 含义 |
|---|---|
| `id` | BD的稳定标识。同id导入更新该BD；另一个独立BD需要不同id。 |
| `name` | 玩家可读名称，可修改。 |
| `stage` | `endgame`终局或`leveling`独立练级目标；两个阶段不自动复制。 |
| `targets.uniques` | 明确选择的暗金／套装数字ID列表。名字由离线词库显示；生成时引用一个套装部件就补齐整套，补全项不反写此字段。 |
| `targets.equipment` | 每个装备类型独立目标池，`affixes`按需求优先级排列，第一项最高；网页保留顺序并编号。不能跨部位或BD凑目标数量。实验词缀可作为明确目标。 |
| `targets.altars` | 祭坛类型、底材与实际目标词缀池，允许明确指定腐化目标。 |
| `targets.idols` | 神像类型、底材与普通词缀池；附魔／腐化不混入普通池。 |
| `targets.bases` | 独立底材：`type`、替代池`bases`、可选首选池`preferred_bases`。终局05还要求同BD对应部位目标T7，不自动限制其他T7素材的底材。 |
| `source`（可选） | 来源名称、URL、更新日期、范围、哈希与审阅提醒；不参与过滤判断。 |

终局五类`targets`字段必须齐全，没有需求就填`[]`。装备／神像／祭坛分组的`bases: []`表示该类型底材不限；独立底材分组的首选与替代都为空时不生成保留规则。ID必须是整数。`affixes`是候选池，不表示要求物品同时拥有池中全部词缀，也不承诺池中任意组合都是BD最终毕业。

装备词条页面默认填写暗金装备需要的词条，省去底材控件和不限提示；原JSON中的`bases`字段仍随保存与导出保留。装备`affixes`的顺序只记录需求重要程度，过滤门槛仍由基底决定，调序不改变目标集合；神像／祭坛的列表顺序不视作优先级。`uniques`仍为ID列表，网页依据冻结词库按部位分组展示，格式保持version=1。

装备／神像／祭坛分组可带`corrupted`及`enchanted`参考ID列表，分别只接受冻结词库腐化6／附魔4；不会计入普通目标。神像普通池只接受0／5。装备普通池拒绝4／6。未知ID阻止导入／生成，不猜名字或类别。神像还可选填`pair_bases`：限定两项目标层底材；不填表示与`bases`相同，明确`[]`表示两项层底材不限。

祭坛的`affixes`表示实际筛选目标，不受普通神像计数限制。Allie玩家补充为`{"type":"IDOL_ALTAR","bases":[3],"affixes":[1105]}`：尖塔祭坛与“魔力自装备的每个腐化神像”同时匹配。只放在`corrupted`参考列表不会生成这条目标规则。

练级也使用version=1，`stage: "leveling"`的`targets`只包含以下两份列表：

```json
{
  "affixes": [26, 945, 98, 643, 502, 45, 28, 27],
  "bases": [{"type": "RING", "bases": [7]}, {"type": "RELIC", "bases": [15, 18]}]
}
```

练级词缀为平铺普通装备目标池，不按部位人工填写；附魔、腐化、仅神像可用的词缀不能加入。底材必须带类型，因为不同类型可以重复使用同一底材数字ID。基底负责1项／总阶数5／8、单可用目标T5例外及各退出等级。多BD逐个计数、评分，禁止合并成一个总池。练级的暗金／神像／祭坛沿用终局目标，练级列表为空时不推断装备目标。

格式不保存主副身份、勾选状态、声音／地图提示、LP／WW、T7门槛、规则编号或原Strict筛选条件。它们留在工具配置和基底。右上角“保存配置”备份全部组合方案，各方案含独立BD目标及主BD、共通设置；备份version=2，方案内引擎config与单BD需求仍version=1，详见[工具说明](TOOL_GUIDE.md)。左侧“保存本BD需求JSON”只保存正在编辑的BD、当前阶段的目标及来源。

导入范围是当前保存方案。新id加入为启用的可编辑BD；尚无方案时创建导入方案。同id只替换文件`stage`的目标和来源，保留另一个阶段、启用状态和主副身份，同id位于其他保存方案时不受影响。审阅后可在方案内停用BD。两阶段共同导出一份XML。旧五类练级需求仍可读，装备词缀／底材转为两份列表，原五类内容保存在`source.legacy_targets`；旧工具配置的已启用装备R覆盖会转换，原始练级配置另存`legacy_leveling`。不再提供第六个逐R编辑入口。

程序接口：

```python
from requirements import read_document, write_document

data = read_document(document)  # 校验并转成生成器可用的profile
document = write_document(build, "endgame")  # 编辑后的目标保存回同一格式
```

本地HTTP接口为`POST /api/requirements/import`（`{"document": ...}`）及`POST /api/requirements/export`（`{"build": ..., "stage": "endgame"}`）。XML导入仍由`extract(xml)`提取profile；加入BD后使用相同的`write_document`保存，随后JSON与攻略结果走同一转换路径。

真实样本见流血骷髅的[终局需求](../requirements/bleed-skeleton-roamer-guide-835.endgame.json)、[练级需求](../requirements/bleed-skeleton-roamer-guide-835.leveling.json)与[中文审阅表](BLEED_SKELETON_GUIDE_REVIEW.md)。

Allie攻略来源的Flay也使用同一格式：[终局需求](../requirements/flay-lich-allie-guide.endgame.json)、[练级需求](../requirements/flay-lich-allie-guide.leveling.json)。与旧Maxroll Flay使用不同id；同一攻略的两个阶段使用同id。[两篇攻略的完整审阅与网页读回结果](GUIDE_REQUIREMENTS_REVIEW.md)记录了目标、来源冲突及玩家补充的祭坛目标。

冰追心也使用同一格式：[终局需求](../requirements/ice-heartseeker-planner-al0dkyek.endgame.json)、[空练级需求](../requirements/ice-heartseeker-planner-al0dkyek.leveling.json)，稳定id为`ice-heartseeker-planner-al0dkyek`。2026-10-18终局需求改以玩家提供的XML为准，`source.file`及`sha256`记录冻结修订；原构建器证据放在`source.planner_reference`。XML未编码的腐化／附魔参考沿用Planner并明确标注，普通目标完整替换，已删除目标不会在重建时补回。XML不能恢复界面优先级，保留仍选中词条的原顺序并追加新增项；练级不从终局推断。原始数字ID、分类和修订对照见[冰追心审阅](ICE_HEARTSEEKER_PLANNER_REVIEW.md)。
