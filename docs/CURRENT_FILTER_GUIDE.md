# 最新版：Flay Mana Lich＋Skeleton Necromancer v2

[可导入XML](../filters/Flay-Mana-Lich+Skeleton-Necromancer-v2.xml)｜[138条可审阅规则](CURRENT_RULES_REVIEW.md)｜[完整名单](CURRENT_RULE_POOLS.md)。

基于[LE Base Template v1](BASE_TEMPLATE.md)，Flay为主套路／粉色，骷髅Nec为副套路／蓝色，共享按主处理。两者同等收集；原187条试制保留为历史。

## 当前收集策略

- 暗金：20种Strict目标均有0LP保护；目标补入原143项珍贵名单，合并152项。保留原通用高潜能层，不另建BD的1／2／3LP分层。本次不添加5种旧正文替代品。
- 装备：19份目标按BD／装备类型分别绑定，C1收目标T7，C3收目标任意阶＋任意T7；C2保护任意双／多T7。C2／C3的T7计数及C4覆盖全部1156冻结ID，C2／C4保留原23类装备。
- 额外单T7阶段：G57默认开启，名称含[4 ALL T7 PHASE]，没有等级退出。阶段结束后只关闭这一条，前三类继续保留。其他实验／碎片／底材规则仍可能显示单T7。
- T6：按两BD目标补收，保持角色0–84级；双T6没有常驻双／多T7保护。目标候选不保证整件装备毕业或可制作。
- Flay神像：中型843／854、厚实876／886，各有两项齐全和至少一项两层；Weaver与Lagon均保留。两项层Begin声音，一项层静音；腐化不凑数，不要求腐化。厚实只有886仍属候选，876必需条件与891备用没有静默加入。
- 骷髅神像：使用Strict两项目标入口，剥离腐化词缀，普通目标至少2项、阶数不限。原来源底材保留，包括Large Omen的多个职业底材；本轮没有根据类名猜测更窄配对。通用过渡两项／一项层仍在90／75级退出。
- 祭坛：按BD绑定底材与目标池，采用Raxx至少一项、阶数不限；不移植Strict合计T8／T10或双崇高门槛。祭坛的腐化目标保留在其目标池，神像普通池另行剥离腐化。
- 定向底材：五类Strict底材已填入Raxx入口并启用，不附加Strict词缀／FP门槛。永恒臂铠为共享制作底材，属于宽收集。
- 可选项：职业隐藏、冠军词缀、升华、紧缺碎片、普通实验词缀与未给出的开荒优选底材关闭。普通实验目标676／679和紧缺碎片候选36／825／945已填入，按需要手动开启；崇高实验装备及通用进攻／防御碎片沿用基底。仅保留侍祭职业碎片，其他四职业碎片关闭。

## 玩家待办

1. 单T7储备足够后，手动关闭G57 [4 ALL T7 PHASE]；它不会随等级关闭。
2. 没有定向底材需求时关闭Target base五条；其Raxx门槛较宽，会保留指定底材的普通／魔法／稀有／崇高物品。
3. 对照库存调整碎片收集。紧缺入口默认关闭；魔力34、暴击避免97未冒充库存缺口，可按实际需要补入。
4. 需要普通实验目标时开启Optional wanted experimentals；需要升华或冠军词缀时先填写对应目标。
5. Flay没有腐化虚弱1069时，攻略891备用组合可后续补充；Skeleton的必须／可选前后缀配对及跨职业Omen取舍也可以继续细化。
6. 导入后核对138条规则、排序、颜色与声音。封印／特殊词缀计数、LP／WW组合和客户端兼容性尚未实测。开荒专属优选底材未提供，不能把终局配装当开荒路线。

## 复现与证据

```powershell
python -X utf8 scripts/extract_raxx_variables.py
python -X utf8 scripts/generate_current_filter.py
python -X utf8 scripts/verify_current_filter.py
python -X utf8 scripts/render_current_filter.py
```

离线使用已提交的模板、Strict、词库与审阅结果，无需Downloads或缓存。来源与G／B／R／X对应见[生成报告](../analysis/current-filter-report.json)，结构和有限案例见[验证报告](../analysis/current-filter-validation.json)。验证不充当游戏客户端实测。
