# LE-filter：Raxx S5 基底研究

已完成第一阶段准备：固定原始过滤器、阅读完整视频英文自动字幕、解析全部163条规则、编写中文说明，并保存后续工作 memo。原始基底未修改。本阶段没有生成 BD 专属 filter，也没有实现勾选工具。

建议先读 [中文说明](docs/FILTER_GUIDE.md)和 [玩家待办清单](docs/PLAYER_TODO.md)，再按需要查 [163条完整规则索引](docs/RULE_INDEX.md)。视频讲解与当前文件的差异见 [视频与版本核对](docs/VIDEO_AND_VERSIONS.md)。

这个基底预设由玩家完成待办：蓝字及功能规则名的大写文字说明要选哪些需求。当前文件的第29条默认关闭；第81/82/83条存在空选择，第99–126条也有空词缀列表。它们是待配置入口；填写或明确关闭之前，空选择可能扩大匹配范围。后续生成已配置、可复制的filter时可删除56条蓝色说明，将说明留在文档里。

## 阅读与资料入口

| 文件 | 用途 |
|---|---|
| [PLAN.md](PLAN.md) | 本阶段计划、验收条件与范围 |
| [FILTER_GUIDE.md](docs/FILTER_GUIDE.md) | 用人能读懂的语言解释整套过滤器 |
| [PLAYER_TODO.md](docs/PLAYER_TODO.md) | 蓝字和大写文字要求玩家完成的配置、可选功能与进度调整 |
| [BUILD_INPUT_ASSESSMENT.md](docs/BUILD_INPUT_ASSESSMENT.md) | 两份BD导出的实际信息量、可生成范围与缺少的过渡／机制资料 |
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

安装 Python 3 后，在仓库根目录执行：

```powershell
python -X utf8 scripts/analyze_filter.py
```

脚本只使用 Python 标准库，离线读取固定资料，生成三个查询文档和三个分析 JSON，并检查来源哈希、规则数量、排序、启用状态、全部条件类型与 ID 引用。重复执行应得到相同文件；不会修改原始 filter。

已完成结构与资料检查；尚未在 Last Epoch 客户端导入或用实际掉落验证。社区数据库用于解释 ID 与格式，不能作为游戏引擎模拟器。三项旧暗金 ID 只能在本地化中找到名字，清单已有标注。

Raxxanterax 是原始过滤器的作者；参考数据来自 Dammitt 的 Last Epoch Tools。仓库保留出处，未替第三方原文声明新的许可证。完整视频字幕仅作为本地研究缓存，不上传。
