# 视频与版本核对

来源：[主播视频](https://www.youtube.com/watch?v=l3CRNP95YX8)，2026-10-01发布，页面元数据时长1271秒。完整英文自动字幕已阅读，覆盖00:00–21:09；另检查了15:45的规则29讲解画面。没有声称完整逐帧或听音核验。字幕中的人名、BIS、Idol、Havoc等术语存在识别误差，因此具体条件以固定XML为准。

## 视频定位

以下为简短主题定位，不是逐字稿。细节解释依据XML写在 [中文说明](FILTER_GUIDE.md)。

| 时间入口 | 主题 |
|---|---|
| [00:00](https://www.youtube.com/watch?v=l3CRNP95YX8&t=0s) | 开场、广告及个人开荒计划 |
| [03:45](https://www.youtube.com/watch?v=l3CRNP95YX8&t=225s) | 介绍本季模板调整 |
| [05:05](https://www.youtube.com/watch?v=l3CRNP95YX8&t=305s) | 导入和从底部阅读说明 |
| [05:30](https://www.youtube.com/watch?v=l3CRNP95YX8&t=330s) | 开荒底材与武器配置 |
| [07:30](https://www.youtube.com/watch?v=l3CRNP95YX8&t=450s) | 神像组合与放宽条件 |
| [08:38](https://www.youtube.com/watch?v=l3CRNP95YX8&t=518s) | 碎片、定向底材、升华用途 |
| [10:29](https://www.youtube.com/watch?v=l3CRNP95YX8&t=629s) | 早期崇高及腐化兜底 |
| [11:05](https://www.youtube.com/watch?v=l3CRNP95YX8&t=665s) | 发布前尚未加入的物品 |
| [12:57](https://www.youtube.com/watch?v=l3CRNP95YX8&t=777s) | 实验词缀与制作候选 |
| [14:19](https://www.youtube.com/watch?v=l3CRNP95YX8&t=859s) | 双崇高与BIS收集 |
| [15:41](https://www.youtube.com/watch?v=l3CRNP95YX8&t=941s) | 职业隐藏的放置位置 |
| [16:45](https://www.youtube.com/watch?v=l3CRNP95YX8&t=1005s) | 高优先级物品保护 |
| [18:12](https://www.youtube.com/watch?v=l3CRNP95YX8&t=1092s) | 复述配置顺序与角色切换 |

视频开头和结尾的个人BD计划不代表用户的需求，本阶段未把主播玩的BD写入任何新filter。

## 三个版本标识不能混用

| 标识 | 当前事实 |
|---|---|
| GitHub文件名 | `Raxx's S5 Ultimate Filter v1.0.txt` |
| 上游最新提交标题 | `Update Raxx's S5 Ultimate Filter v1.1.txt` |
| XML内部元数据 | 名称Universal Filter；描述1.5 Circle of Fortune；lastModifiedInVersion=1.4.7；lootFilterVersion=9 |

视频发布前的文件来自 [3525e167](https://github.com/raxxanterax/GAMING/commit/3525e1672784a78a868e189fd278cce55c0eaf84)，提交时间2026-10-01 00:26:01 UTC。研究基底来自其后 [57498b09](https://github.com/raxxanterax/GAMING/commit/57498b0901a7c099efdf931923c65271fdfdb993)，提交时间2026-10-01 23:22:12 UTC（日本时间10月2日08:22:12）。两个原文均已保留，便于复核。

视频说明中的“发布后再补新物品”需要放在当时的时间背景下理解。本次固定的当前文件已经有补充；不能重复把它说成完全未补。

## 两份原文的全部语义差异

由脚本比较规则字段和条件，发现七条改变；完整前后值在 [version-diff.json](../analysis/version-diff.json)。

| 第几条 | 视频发布前文件 | 当前研究基底 | 含义 |
|---:|---|---|---|
| 15 | 指定128项 | 指定143项，新增15个物品ID | 新增物品进入不要求LP的保留清单 |
| 20 | 资源flag为None | 改为AllKeys | 修复资源选择 |
| 29 | 空职业配置，但启用 | 改为关闭 | 避免未配置时广泛隐藏 |
| 61 | 341个词缀ID | 增加36与52，变为343项 | 加入复合生命与提高生命 |
| 82 | 空类型/底材，关闭 | 空选择仍在，改为启用 | 可能扩大显示并遮住下方规则 |
| 83 | 空词缀，关闭 | 空选择仍在，改为启用 | 官方空词缀语义下需要审查 |
| 91 | 神像说明要求启用对应职业BIS条目 | 改为较短说明 | 说明文字改变；第99–126条的状态没有随之改变 |

第15条新增的ID为471、472、473、474、475、476、478、479、480、483、484、485、486、487、488；名称可查 [选择清单](SELECTED_UNIQUES.md)。第13/14条的白名单并未在这次提交里同步增加，第16条也没有增加。上游提交摘要只列了两项，完整差异比摘要多，必须以原文比较为准。

## 研究中纠正的阅读陷阱

- 规则名称“all”“BIS”“LP0”表达用途，不能替代检查条件。
- 视频概括、蓝色说明和最新XML可能不同；例如最新一般T6/T7区使用淡紫色。
- 官方支持页面仍写75条上限，但 [1.4正式补丁](https://forum.lastepoch.com/t/last-epoch-shattered-omens-patch-notes/80571)明确提升到200条。本文件163条与视频中的数量吻合；未来仍须以实际客户端版本确认。
- S5补丁页面的“# of T6/T7”“忽略sealed”“affix分组”一段属于Bazaar搜索更新，不能直接移植成loot filter行为。基底本身没有AffixCountCondition。
- Last Epoch Tools的部分`match()`实现是占位或简化逻辑，尤其潜能条件；它适合查ID和格式，不能拿其模拟结果冒充客户端实测。

完整字幕保存在忽略的本地缓存中，不随仓库发布；这里只保留简短定位和自主分析。
