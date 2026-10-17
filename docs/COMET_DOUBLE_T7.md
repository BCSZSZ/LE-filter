# 双T7彗星判定

2026-10-17更新，作用于目标工作台的共通生成器。原始模板、需求JSON及历史成品XML保留。

## 当前规则

按首次命中，普通装备的多T7依次为：

| 条件 | 档位 |
|---|---|
| 至少三条恰好T7 | 彗星 |
| 至少两条恰好T7，其中至少一条是启用BD在该部位／底材范围内的目标T7 | 彗星 |
| 至少两条恰好T7，且恰好三条未封印词缀，空一个普通栏位 | 彗星 |
| 其余至少两条恰好T7 | 灵感 |

彗星统一名称红7／光柱10、声音12，灵感名称橙5／光柱7、声音9。以上常驻，覆盖23类普通装备；不包括神像、祭坛、资源。T8不参与T7计数，但其占用的普通栏位照常计数。单T7与低阶BD目标、85级退出、两阶段收集及其他共通策略保持。

旧的“同BD两条目标T7”独立层已移除；满足它的物品自然命中新“至少一条目标T7”条件。低阶BD目标加两个非目标T7，只有另行满足三词条空栏或至少三T7等彗星条件才为彗星。

## XML表达与合并

目标双T7规则采用两份AffixCondition并同时成立：全1156词缀池至少2项T=7，对应部位／底材目标池至少1项T=7。不使用T≥7，也不以低阶目标凑数。

“至少一条目标”是存在性条件；同类型、同底材范围内的启用BD目标池可以取并集，结果等于逐BD规则的或关系。只在这个计数为1且显示完全相同的彗星层合并；不同部位或底材范围分别保留。C1、C3、练级评分和保存的BD需求仍独立，未启用BD不进入并集。

游戏原生AffixCountCondition只提供前缀与后缀的独立上下限，没有总数或OR字段。因此空一栏用两条共通规则表示：

- minPrefixes=maxPrefixes=1，minSuffixes=maxSuffixes=2。
- minPrefixes=maxPrefixes=2，minSuffixes=maxSuffixes=1。

每条另有全装备范围与至少两项T=7条件。sealedType=Any；按游戏原生未封印的四个普通栏位计数，已有封印词缀不占普通栏位，不另行排除物品。只有两条词缀、满四条未封印词缀均不命中这一层。

## 本机实现证据

本机1.5.2.2，GameAssembly.dll SHA256为`d5f9fb458f0e9878e697a92b590a586a52fd77e645f8bf87bb4f2b74c6c56567`。

- ItemFiltering.AffixCountCondition字段：minPrefixes `+0x10`、maxPrefixes `+0x18`、minSuffixes `+0x20`、maxSuffixes `+0x28`，均为可空整数；sealedType `+0x30`，Any=0。
- Match RVA `0x19685C0`、长度`0x26A`，先处理封印选项，再在`0x1968692`调用ItemData.GetNonSealedPrefixAndSuffixCount；非空下限按≥、非空上限按≤判断。
- GetNonSealedPrefixAndSuffixCount RVA `0x1201DD0`、长度`0x1B7`，在`0x1201ED8`调用ItemAffix.IsSealed并跳过封印项，再按AffixList中的实际前／后缀类型计数。

Cpp2IL只用于字段、签名和RVA；方法体以实际原生指令核对，未把反编译空方法体当实现。开发核查缓存位于`.cache/t7-filter-conditions/`。以上为静态代码和XML模型验证，没有启动游戏或声光实测。

规则数、边界案例、确定性、重复条件与冻结输入校验记录在[双T7彗星验证](../analysis/comet-double-t7-validation.json)。
