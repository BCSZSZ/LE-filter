# LE-filter：Raxx 基底与双 BD 收集过滤器

当前阶段：**以Raxx原版收集设计为准，Strict只用于提取需要填写的BD情报**。已抽出24组变量，完成提取程序并运行，交付[变量总表](docs/RAXX_VARIABLES.md)与[文字审阅结论](docs/STRICT_VARIABLE_REVIEW.md)。本轮没有生成或修改最终filter，等待审阅变量、候选与未决项。

先读[本轮审阅结论](docs/STRICT_VARIABLE_REVIEW.md)，再查[原版变量及保留门槛](docs/RAXX_VARIABLES.md)与[工作memo](docs/WORKING_MEMO.md)。当前默认Flay为主、Skeleton为副，共享按主，两者同等收集。旧187条XML及其说明保留作历史试制，包含Strict策略移植，**不作为本轮已认可的最终方案**；动态勾选界面尚未实施。

最新神像修正见[Flay神像审阅](docs/FLAY_IDOL_REVIEW.md)：腐化不凑普通目标数量，Flay按用户指定记录1项候选／2项组合毕业四层。普通目标与腐化参考分别输出，原Strict保留供追溯。

[Strict神像自动分类结果](docs/STRICT_IDOL_CLASSIFICATION.md)单独展示12条BD源规则：词缀ID来自Strict，腐化类别由冻结数据库自动查询，不依赖攻略。备用关系另作后续补充。

第一阶段的基底研究也已完成：固定原始过滤器、阅读完整视频英文自动字幕、解析全部163条规则，中文说明和原模板待办保留如下。

建议先读 [中文说明](docs/FILTER_GUIDE.md)和 [玩家待办清单](docs/PLAYER_TODO.md)，再按需要查 [163条完整规则索引](docs/RULE_INDEX.md)。视频讲解与当前文件的差异见 [视频与版本核对](docs/VIDEO_AND_VERSIONS.md)。

这个基底预设由玩家完成待办：蓝字及功能规则名的大写文字说明要选哪些需求。当前文件的第29条默认关闭；第81/82/83条存在空选择，第99–126条也有空词缀列表。它们是待配置入口；填写或明确关闭之前，空选择可能扩大匹配范围。后续生成已配置、可复制的filter时可删除56条蓝色说明，将说明留在文档里。

## 阅读与资料入口

| 文件 | 用途 |
|---|---|
| [PLAN.md](PLAN.md) | 本阶段计划、验收条件与范围 |
| [FILTER_GUIDE.md](docs/FILTER_GUIDE.md) | 用人能读懂的语言解释整套过滤器 |
| [PLAYER_TODO.md](docs/PLAYER_TODO.md) | 蓝字和大写文字要求玩家完成的配置、可选功能与进度调整 |
| [RAXX_VARIABLES.md](docs/RAXX_VARIABLES.md) | 当前24组填空／可选变量、原始默认值和保留门槛 |
| [STRICT_VARIABLE_REVIEW.md](docs/STRICT_VARIABLE_REVIEW.md) | 当前Strict情报与变量匹配的文字结论，供Review |
| [FLAY_IDOL_REVIEW.md](docs/FLAY_IDOL_REVIEW.md) | 神像腐化机制、普通目标分层及必须／可选词缀表达 |
| [STRICT_IDOL_CLASSIFICATION.md](docs/STRICT_IDOL_CLASSIFICATION.md) | 自动提取Strict神像ID并区分非腐化／腐化，附来源 |
| [analysis/raxx-variable-extraction.json](analysis/raxx-variable-extraction.json) | 变量候选、R入口、全部271条Strict条件与未决映射 |
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

- [用户提供的上游文件](https://github.com/raxxanterax/GAMING/blob/main/Raxx%27s%20S5%20Ultimate%20Filter%20v1.0.txt)固定到提交 `57498b0901a7c099efdf931923c65271fdfdb993`。
- 本地原文：[Raxx's S5 Ultimate Filter v1.0.txt](sources/Raxx%27s%20S5%20Ultimate%20Filter%20v1.0.txt)。扩展名为 `.txt`，内容是可导入的 Last Epoch XML。
- 文件内部名称为 `Raxx's S5 Universal Filter`，描述为 `1.5 Circle of Fortune`，格式版本为9。
- 当前文件163条：104条启用、59条关闭；关闭项中56条是蓝色说明，另外3条是职业隐藏、普通实验词缀与冠军词缀规则。
- [讲解视频](https://www.youtube.com/watch?v=l3CRNP95YX8)发布于2026-10-01；研究日期为2026-10-06（日本时间）。

## 复现

安装 Python 3 后，在仓库根目录重建本轮变量和审阅结论：

```powershell
python -X utf8 scripts/extract_raxx_variables.py
```

只使用标准库与已提交资料，不需要网络、.cache或Downloads。检查原版／Strict哈希、56条蓝字覆盖、38份部位池、20种目标及已有XML字节不变；记录全部271条Strict。它不生成filter，不从Strict移植门槛、进度或开关。

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
