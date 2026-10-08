# LE-filter：Raxx 基底与双 BD 收集过滤器

[在线工作台](https://bcszsz.github.io/LE-filter/)由GitHub Pages托管。支持导入Maxroll filter XML／TXT、导入需求JSON、列表搜索编辑、多个BD选择及JSON／XML导出；不支持从网址提取攻略。首次打开需要加载运行环境，导入内容与生成过程在浏览器内处理。在线示例包含旧Maxroll Flay／Skeleton，以及独立的Allie Flay攻略／中文骷髅835攻略；两个攻略方案默认未勾选，两份Flay不合并。使用Chrome或Edge进行文件下载；Codex内置浏览器目前不能正常接收浏览器生成的下载文件。

**目标工作台已可使用**：双击[start-tool.cmd](start-tool.cmd)，打开本地 <http://127.0.0.1:8765>。支持导入filter提取目标、中文／英文／ID搜索多选、多个BD勾选合并、主副套路、JSON保存和XML预览导出。终局五类目标、练级只填词缀与底材两份列表，共同导出一份filter。见[工具使用说明](docs/TOOL_GUIDE.md)。内置两BD示例133条（127启用，练级目标留空）。05要求指定底材＋同BD对应部位目标T7常驻；删除专门T6层，练级品质80退出、底材60退出、普通拆解50退出、原常驻拆解60退出。897附魔及腐化不计普通神像目标。

[赛季暗金通用保护](docs/SEASONAL_UNIQUE_PROTECTION.md)涵盖1.3／1.4／1.5新增的55种暗金，含25种先古和4种暗金神像；0LP也留。与原珍贵暗金／套装合并为170种通用名单，独立于BD选择。预览可按名字／ID搜索并展开完整名单。

新增[共通BD需求JSON格式](docs/REQUIREMENTS_FORMAT.md)：filter与攻略先提供一个BD／一个阶段的目标，网页可导入、修改并保存回该格式，再由基底生成filter。攻略835的[流血骷髅终局需求](requirements/bleed-skeleton-roamer-guide-835.endgame.json)含25暗金／套装、13装备组、3神像组、1祭坛、3独立底材；另有[练级需求](requirements/bleed-skeleton-roamer-guide-835.leveling.json)，8词缀、5底材。练级按1项目标→总阶数5→8收紧，单可用目标T5兜底，跨BD不能合计。见[中文审阅表](docs/BLEED_SKELETON_GUIDE_REVIEW.md)。旧Strict与历史XML保留。

Allie攻略来源的Flay已按2026-10-07正文更新[终局需求](requirements/flay-lich-allie-guide.endgame.json)与[练级需求](requirements/flay-lich-allie-guide.leveling.json)：17暗金、10装备组、4神像组、28种终局底材；练级19词缀与3种底材，祭坛未提供目标。补入短暂休息132、红戒277、虚无353、破碎世界413、流亡469、不息狂怒477，保留山之麓替代品。新Flay＋835当前转换179条（173启用），30项测试通过。完整目标、部位链接冲突与来源提取时的验证边界见[双攻略需求审阅](docs/GUIDE_REQUIREMENTS_REVIEW.md)。已有浏览器配置需导入新版同id终局JSON更新，不覆盖练级或主副设置。

基底常驻显示带普通抗性后缀的1×2／2×1神像：全部16条普通抗性后缀，至少一项、阶数不限、所有底材、不随等级关闭。此规则独立于BD需求JSON，静音且无地图标记／光柱；命中BD目标时优先使用BD提示。

已归档固定成品：**[Flay＋Skeleton Necromancer v3](filters/Flay-Mana-Lich+Skeleton-Necromancer-v3.xml)**，162条（151启用／11关闭），采用铁匠／开始／灵感／彗星四档，静音项无图标和光柱，沿用原颜色。旧v2保留不动。[四档分类与能力审阅](docs/SOUND_STYLE_REVIEW.md)、[全部提示索引](docs/CURRENT_ALERT_INDEX.md)、[使用说明](docs/CURRENT_FILTER_GUIDE.md)和[逐条条件](docs/CURRENT_RULES_REVIEW.md)对应这个历史快照。

2026-10-07修正：至少3条T7彗星；双T7含对应部位BD目标T7灵感；其余任意双T7开始。静音不额外改色。T8为铁匠兜底（G84）；T7只计恰好7阶，T8不凑双／多T7，也不冒充BD目标单T7。

当前基底仍为[LE Base Template v1](templates/LE-base-v1.xml)，落实用户确认的T7四类，供后续定制。Strict提供目标情报，成品采用基底门槛；原Raxx与旧187条试制保留不动。

先读[工具使用说明](docs/TOOL_GUIDE.md)，历史v3快照查[当前使用说明](docs/CURRENT_FILTER_GUIDE.md)，基底与来源查[新基底说明](docs/BASE_TEMPLATE.md)、[BD情报来源](docs/STRICT_VARIABLE_REVIEW.md)及[工作memo](docs/WORKING_MEMO.md)。Flay主套路粉色、Skeleton副套路蓝色，共享按主；两者同等收集。旧187条XML及其说明包含Strict策略移植，仅作历史。

[V05–V10的用途与过渡范围](docs/STRICT_VARIABLE_REVIEW.md#equipment-purpose)保留基底四类情报。v3按三T7→目标双T7→任意双T7→目标单T7分档；目标双T7、C1与C3各自主一组、副一组。C4仍只有一条，当前G85，默认开启、手动关闭；T6等价压成18条，85级退出。详见[提示审阅](docs/SOUND_STYLE_REVIEW.md)。

[原版宽池完整名单](docs/RAXX_DEFAULT_EQUIPMENT_POOLS.md)保留623／42／343项作为历史对照。新基底的全量池使用冻结词库全部1156个ID，装备范围保留原23类普通装备；双／多T7和额外单T7阶段池不再按BD裁剪。C1／C3的目标仍按BD与部位填写。

最新神像修正见[Flay神像审阅](docs/FLAY_IDOL_REVIEW.md)：腐化不凑普通目标数量，Flay按用户指定记录1项候选／2项组合毕业四层。普通目标与腐化参考分别输出，原Strict保留供追溯。

[Strict神像自动分类结果](docs/STRICT_IDOL_CLASSIFICATION.md)单独展示12条BD源规则：词缀ID来自Strict，腐化类别由冻结数据库自动查询，不依赖攻略。备用关系另作后续补充。

2026-10-07新增[骷髅Strict／Very Strict两轮调查](docs/SKELETON_STRICT_INVESTIGATION.md)：9组部位T7与8条神像来源的条件、目标一致；缺少常驻一项层是当前生成策略所致。装备只按filter的每部位目标池；池有至少2项目标时只增加一条“至少2项目标为T7”，不枚举配对，不从攻略补缺或排序。程序已输出两个BD全部19组情报。神像只数源普通目标，897附魔与腐化均不凑数，一项／两项各用一条池条件，不强制攻略配对。本轮归档提取规则，成品未改。

第一阶段的基底研究也已完成：固定原始过滤器、阅读完整视频英文自动字幕、解析全部163条规则，中文说明和原模板待办保留如下。

建议先读 [中文说明](docs/FILTER_GUIDE.md)和 [玩家待办清单](docs/PLAYER_TODO.md)，再按需要查 [163条完整规则索引](docs/RULE_INDEX.md)。视频讲解与当前文件的差异见 [视频与版本核对](docs/VIDEO_AND_VERSIONS.md)。

这个基底预设由玩家完成待办：C1／C3当前仍是Raxx目标示例，要用Strict部位目标替换。原R29职业隐藏保持关闭；原R81/82/83和R99–126等仍有未填入口，填写或明确关闭之前，空选择可能扩大匹配范围。R指冻结原版，B指新基底Order+1；原R61已并入阶段规则，后续编号发生变化。生成已配置、可复制filter时可删除56条蓝色说明，将说明留在文档里。

## 阅读与资料入口

| 文件 | 用途 |
|---|---|
| [start-tool.cmd](start-tool.cmd) | Windows双击启动目标工作台 |
| [TOOL_GUIDE.md](docs/TOOL_GUIDE.md) | 五类终局／两类练级目标、最新门槛、导入保存和XML导出 |
| [tool/engine.py](tool/engine.py) | 从filter提取目标并填入Raxx基底，运行期离线 |
| [tool/test_engine.py](tool/test_engine.py) | 提取与已审阅收集策略的有限自动测试 |
| [PLAN.md](PLAN.md) | 本阶段计划、验收条件与范围 |
| [Flay＋Skeleton v3](filters/Flay-Mana-Lich+Skeleton-Necromancer-v3.xml) | 当前可导入成品，四档声音与一条手动退出C4 |
| [SOUND_STYLE_REVIEW.md](docs/SOUND_STYLE_REVIEW.md) | 全部旧v2情况的档位、区分能力、修改与未完成语义 |
| [CURRENT_ALERT_INDEX.md](docs/CURRENT_ALERT_INDEX.md) | 实际162条声音、图标、光柱及启用状态 |
| [CURRENT_FILTER_GUIDE.md](docs/CURRENT_FILTER_GUIDE.md) | 当前策略、默认开关和玩家仍需完成的事项 |
| [CURRENT_RULES_REVIEW.md](docs/CURRENT_RULES_REVIEW.md) | 实际162条XML规则的类型、目标、门槛、颜色与声音 |
| [CURRENT_RULE_POOLS.md](docs/CURRENT_RULE_POOLS.md) | 当前大名单与原364项roll边界，低WW层另引用一份 |
| [current-filter-report.json](analysis/current-filter-report.json) | 成品哈希、G／B／R／X映射、来源与默认配置 |
| [current-filter-validation.json](analysis/current-filter-validation.json) | 条件、声音／图标约束、T6等价合并与有限案例 |
| [filter-style-reference.json](sources/filter-style-reference.json) | 冻结音效／图标／光柱／颜色ID及代码来源哈希 |
| [Flay＋Skeleton v2](filters/Flay-Mana-Lich+Skeleton-Necromancer-v2.xml) | 上一版138条快照；复现脚本见Git提交82e557d |
| [BASE_TEMPLATE.md](docs/BASE_TEMPLATE.md) | 当前四类收集规则、范围、退出方式和玩家待办 |
| [LE-base-v1.xml](templates/LE-base-v1.xml) | 后续填写BD使用的162条可复现基底模板 |
| [base-manifest.json](templates/base-manifest.json) | 模板哈希、原R／当前B映射、四类规则和全池范围 |
| [scripts/build_base_template.py](scripts/build_base_template.py) | 从不变的原版重建用户确认的新基底 |
| [scripts/verify_base_template.py](scripts/verify_base_template.py) | 核对变更边界、四类匹配和阶段关闭后的保护 |
| [analysis/base-template-validation.json](analysis/base-template-validation.json) | 结构、全池与15个有限T7匹配案例的检查结果 |
| [FILTER_GUIDE.md](docs/FILTER_GUIDE.md) | 用人能读懂的语言解释整套过滤器 |
| [PLAYER_TODO.md](docs/PLAYER_TODO.md) | 蓝字和大写文字要求玩家完成的配置、可选功能与进度调整 |
| [RAXX_VARIABLES.md](docs/RAXX_VARIABLES.md) | 当前24组变量、实际模板默认值及原R／当前B入口 |
| [STRICT_VARIABLE_REVIEW.md](docs/STRICT_VARIABLE_REVIEW.md) | 当前Strict情报与变量匹配的文字结论，供Review |
| [FLAY_IDOL_REVIEW.md](docs/FLAY_IDOL_REVIEW.md) | 神像腐化机制、普通目标分层及必须／可选词缀表达 |
| [STRICT_IDOL_CLASSIFICATION.md](docs/STRICT_IDOL_CLASSIFICATION.md) | 自动提取Strict神像ID并区分非腐化／腐化，附来源 |
| [SKELETON_STRICT_INVESTIGATION.md](docs/SKELETON_STRICT_INVESTIGATION.md) | 骷髅双目标T7、单目标神像缺口、截图配对与附魔分列调查 |
| [skeleton-strict-investigation.json](analysis/skeleton-strict-investigation.json) | 两份骷髅导出逐规则对比、17条相同目标、截图覆盖与成品快照 |
| [analysis/raxx-variable-extraction.json](analysis/raxx-variable-extraction.json) | 当前模板、变量候选、R／B入口、全部271条Strict条件与未决映射 |
| [scripts/extract_raxx_variables.py](scripts/extract_raxx_variables.py) | 本轮离线提取程序，只输出数据和文档 |
| [COMBINED_FILTER_GUIDE.md](docs/COMBINED_FILTER_GUIDE.md) | 历史试制的颜色、用途与待办 |
| [RULES_REVIEW.md](docs/RULES_REVIEW.md) | 历史试制187条规则的中文条件、门槛、启用状态和提示 |
| [RULES_REVIEW_POOLS.md](docs/RULES_REVIEW_POOLS.md) | 历史审阅稿的完整大名单及原XML唯一属性roll编码边界 |
| [TRANSFER_RULES.md](docs/TRANSFER_RULES.md) | Strict输入族如何填入基底、共享池拆分、补充与明确差异 |
| [GENERATED_RULE_INDEX.md](docs/GENERATED_RULE_INDEX.md) | 187条成品编号G与基底槽位R、Strict来源X的定位 |
| [analysis/transfer-report.json](analysis/transfer-report.json) | 原163条与Strict全部271条的处置，以及每条成品的来源 |
| [analysis/generated-validation.json](analysis/generated-validation.json) | 条件转移、无潜能门槛暗金保护与20个有限离线案例 |
| [BUILD_INPUT_ASSESSMENT.md](docs/BUILD_INPUT_ASSESSMENT.md) | 两份BD导出的实际信息量、可生成范围与缺少的过渡／机制资料 |
| [SAVED_GUIDE_ASSESSMENT.md](docs/SAVED_GUIDE_ASSESSMENT.md) | 本地保存巫妖网页补充的门槛、6种替代／升级暗金、神像依赖与来源矛盾 |
| [MAXROLL_STRICT_ASSESSMENT.md](docs/MAXROLL_STRICT_ASSESSMENT.md) | 两份Strict XML的参考价值、具体拾取门槛、覆盖缺口和合并前配置 |
| [MAXROLL_RULE_INDEX.md](docs/MAXROLL_RULE_INDEX.md) | 两份Strict的全部271条规则定位；完整字段见analysis/maxroll-strict.json |
| [RULE_INDEX.md](docs/RULE_INDEX.md) | 按游戏优先级列出全部163条，含条件与提示设置 |
| [VIDEO_AND_VERSIONS.md](docs/VIDEO_AND_VERSIONS.md) | 视频定位、发布时版本与当前基底的七条差异 |
| [BEHAVIOR_CASES.md](docs/BEHAVIOR_CASES.md) | 容易混淆的条件示例及游戏内验证清单 |
| [ID_REFERENCE.md](docs/ID_REFERENCE.md) | 1,112个词缀 ID 与149个底材映射的中英文对照 |
| [SELECTED_UNIQUES.md](docs/SELECTED_UNIQUES.md) | 448个暗金／套装 ID 在各规则中的选择情况 |
| [WORKING_MEMO.md](docs/WORKING_MEMO.md) | 给未来工作的约束、关键结论、复现命令与待确认项 |
| [sources/manifest.json](sources/manifest.json) | 上游提交、哈希、证据来源及研究边界 |
| [analysis/rules.json](analysis/rules.json) | 保留所有规则字段、完整选择列表和源文件行号 |
| [analysis/validation.json](analysis/validation.json) | 全量解析与映射的检查结果 |

## 基底版本

- 当前使用[LE Base Template v1](templates/LE-base-v1.xml)：162条，103启用、59关闭，仍含56条蓝色说明；原目标预填仅作示例，尚未配置为BD成品。
- 下列163条事实描述冻结的Raxx原文；原文件保持字节不变。
- [用户提供的上游文件](https://github.com/raxxanterax/GAMING/blob/main/Raxx%27s%20S5%20Ultimate%20Filter%20v1.0.txt)固定到提交 `57498b0901a7c099efdf931923c65271fdfdb993`。
- 本地原文：[Raxx's S5 Ultimate Filter v1.0.txt](sources/Raxx%27s%20S5%20Ultimate%20Filter%20v1.0.txt)。扩展名为 `.txt`，内容是可导入的 Last Epoch XML。
- 文件内部名称为 `Raxx's S5 Universal Filter`，描述为 `1.5 Circle of Fortune`，格式版本为9。
- 当前文件163条：104条启用、59条关闭；关闭项中56条是蓝色说明，另外3条是职业隐藏、普通实验词缀与冠军词缀规则。
- [讲解视频](https://www.youtube.com/watch?v=l3CRNP95YX8)发布于2026-10-01；研究日期为2026-10-06（日本时间）。

## 复现

安装 Python 3 后，在仓库根目录重建基底、提取情报并生成当前成品：

```powershell
python -X utf8 scripts/build_base_template.py
python -X utf8 scripts/verify_base_template.py
python -X utf8 scripts/extract_raxx_variables.py
python -X utf8 scripts/generate_current_filter.py
python -X utf8 scripts/verify_current_filter.py
python -X utf8 scripts/render_current_filter.py
```

只使用标准库与已提交资料，不需要网络、.cache或Downloads。模板验证162条结构与15个有限案例；提取核对源哈希、56蓝字覆盖、全部271条Strict与19份目标一致。成品验证162条结构、1156全池、20种暗金0／1LP路径、提示字段、排序、T6压缩等价及107个有限案例，包含目标双T7的部位／阶数绑定、主副及共享提示、T8不凑数；静音基底颜色／强调保留，42条其他规则的条件和开关保持，原364项roll边界保留。客户端导入、封印计数与实际听音尚未实测。完整分类与本轮收集范围变化见SOUND_STYLE_REVIEW。

以下命令用于**历史试制**，本轮不要执行：

```powershell
python -X utf8 scripts/generate_filter.py
python -X utf8 scripts/verify_generated_filter.py
python -X utf8 scripts/render_rules_review.py
```

只使用标准库，无需网络或.cache。当前固定两份导出；38条源T6/T7条件被集合等价地拆成46条，另55条Strict谓词保持原样，25种目标暗金及20个有限离线案例已通过检查。未建模的封印计数会返回未确认；客户端导入和实际掉落待验证。

重建原始基底研究索引：

```powershell
python -X utf8 scripts/analyze_filter.py
```

脚本只使用 Python 标准库，离线读取固定资料，生成三个查询文档和三个分析 JSON，并检查来源哈希、规则数量、排序、启用状态、全部条件类型与 ID 引用。重复执行应得到相同文件；不会修改原始 filter。

社区数据库用于解释 ID 与格式，不能作为游戏引擎模拟器。三项旧暗金 ID 只能在本地化中找到名字，清单已有标注。

Raxxanterax 是原始过滤器的作者；参考数据来自 Dammitt 的 Last Epoch Tools。仓库保留出处，未替第三方原文声明新的许可证。完整视频字幕仅作为本地研究缓存，不上传。
