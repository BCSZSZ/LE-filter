# Last Epoch 官方角色配装 API：开放范围与接入路线

核查日期：2026-10-18。问题是：LETools 的 Import 只输入 `accountName` 与 `charName`，LE-filter 能否同样直接向 EHG 读取在线角色当前配装，而无需 LETools／Maxroll 等合作方持有的接入资格。本文件只记录研究，不修改导入代码、部署、已有模版或个人保存。

## 结论

**EHG 的角色数据 API 确实存在，LETools／Maxroll 使用它有开发者本人确认；本次没有找到可供一般开发者直接使用、无需合作方资格或凭据的官方角色配装 API 文档与接入入口。** 不能由 LETools 网页只需两个人名字段，推导出其服务器访问 EHG 时也无需授权。[EHG 后端工程师 Muffin，2024-02-14](https://www.reddit.com/r/LastEpoch/comments/1aqs46z/comment/kqewa7d/)、[EHG Mike，2024-07-14](https://www.reddit.com/r/LastEpoch/comments/12p161l/comment/ld34psx/)

截至本次核查，官方支持页仍称 Game Data API 尚未向社区开放，页面标注最后更新为 **2026-07-15**。但该页以技能树静态信息举例，没有专门描述 Character Data API 的当前权限。因此它是较新的官方公开说明，却不足以独自证明所有角色数据接口的当前权限完全相同；页面更新时间也不等于政策首次生效时间。[官方支持页](https://support.lastepoch.com/hc/en-us/articles/1260805256609-The-Game-Data-API-is-not-yet-Available)

**可核实的接洽路线是向官方支持表达接入兴趣，请求转交 API 负责人；没有证据支持“填一份公开申请表即可获得合作方 API”。** EHG Mike 在 2024-02-28 直接建议向支持团队表达兴趣，同时说当时不认为正在接受申请；2024-07-14 被问到申请流程时回答当时没有。本次也未找到更新的官方自助申请、发 Key 或授权协议页面。[2024-02-28 原回复](https://www.reddit.com/r/LastEpoch/comments/12p161l/comment/kskyjky/?context=3)、[2024-07-14 原回复](https://www.reddit.com/r/LastEpoch/comments/12p161l/comment/ld4z2t0/?context=3)、[当前官方支持表单](https://support.lastepoch.com/hc/en-us/requests/new)

这不是“官方确认永远不开放”的结论。历史官方回复多次表达扩展开放范围的意愿；尚缺的是可验证的正式公开上线、最新接入条件和可实施的接口契约。

## 一手证据时间线

下表中的事实仅适用于该条声明的日期。Reddit 的年份来自帖子／评论日期，不能把 2023 年帖子下的 2024 年回复都记成 2023 年。

| 日期 | 一手来源与身份 | 本次核实的内容 | 不能据此推出的内容 |
|---|---|---|---|
| 2023-09-22 | [Dammitt 的 LETools 发布说明](https://www.lastepochtools.com/news/article/site-update-online-character-import-and-character-profiles) | 在线角色导入正式加入 Planner；输入账户名、角色名。角色页显示装备、神像、祝福、技能和被动等信息。作者当时说明角色页按打开触发更新，最多每两小时刷新。 | 这不是 EHG API 文档；当时的两小时网页缓存说明也不能当成今天 EHG API 的限流合同。 |
| 2023-09-22 | [Boards_EHG 原回复](https://www.reddit.com/r/LastEpoch/comments/16p6um4/comment/k1q50df/) | EHG 已把新 API 的 Beta 版交给少数紧密合作方，其中包括 LETools；计划在验证后逐步扩大范围。 | 未来计划不等于 1.0 后已自动向所有人开放。 |
| 2023-10-06 | [EHG Mike／ekimarcher 原回复](https://www.reddit.com/r/LastEpoch/comments/12p161l/comment/k3q13ck/?context=3) | LETools 和 Maxroll 当时正在使用官方 API 试用版；EHG 计划逐渐扩展功能及访问范围。 | 没有给出公开 URL、认证方式、申请流程或开放日期。 |
| 2024-02-14 | [EHG Senior Backend Engineer Muffin 原回复](https://www.reddit.com/r/LastEpoch/comments/1aqs46z/comment/kqewa7d/) | 他参与开发 Character Data API，已被 Maxroll 和 LETools 用于角色页；希望在 1.0 后改进到适于公开使用。 | 证明角色数据上游是官方服务；没有证明一般开发者当时可以直接调用。 |
| 2024-02-28 | [EHG Mike 原回复](https://www.reddit.com/r/LastEpoch/comments/12p161l/comment/kskyjky/?context=3) | 将当时状态称为 closed beta；不认为当时正在接受访问申请，可向支持团队发邮件表达兴趣；无具体扩展时间。 | 不能写成已建立合作方申请制度，更不能承诺提交申请会批准。 |
| 2024-07-14 | [EHG Mike：访问仍有限](https://www.reddit.com/r/LastEpoch/comments/12p161l/comment/ld34psx/)及[申请流程回复](https://www.reddit.com/r/LastEpoch/comments/12p161l/comment/ld4z2t0/?context=3) | API 功能有所增加，但获得访问的人仍受限制；被问申请流程时答当时没有。 | 这是一手且晚于 1.0 的说明，仍不是 2026 年权限政策的完整确认。 |
| 2025-04-22 | [Dammitt 在官方论坛的回复，第20楼](https://forum.lastepoch.com/t/le-planner-import-not-working-after-update/75746) | LE 服务器的 API 维护曾导致 LETools 在线角色导入暂时失效，后来恢复。 | 说明 LETools 仍依赖 LE 上游服务；没有宣布 EHG API 已对外开放。 |
| 2026-07-15，页面标注更新 | [Last Epoch 官方支持页](https://support.lastepoch.com/hc/en-us/articles/1260805256609-The-Game-Data-API-is-not-yet-Available) | Game Data API 仍在开发，尚未向社区开放；描述 JSON、REST，例子为技能专精树数据。 | 不能从静态数据例子推断角色 API 的完整字段、权限、认证类型及开放日期。 |

## LETools 的 Import 实际证明了什么

本次只读核对本地已取得的 LETools 发布前端脚本 `.cache/profile-import/planner.js`，没有执行远程脚本。该文件 SHA-256 为 `a777c87bce28a14ff0900ca63ab5f5d3fe297f4a9391420ed6426434ef67eb4a`。导入函数 `dhtLq` 可见如下调用关系：

```text
LETools Planner 前端
  POST window.getGDHost() + "import_character.php"
  body: accountName, charName
  header: X-Requested-With: XMLHttpRequest
  success: buildInfo.data
```

它证明浏览器把账户／角色名交给 **LETools 自己的 PHP 后端**，并使用该后端返回的 Planner 数据。它没有暴露 PHP 后端向 EHG 请求时使用的地址、凭据或授权安排。结合 EHG 开发者确认，合理架构解释是网页调用 LETools，LETools 作为获准工具从官方数据服务取数；本次没有获得其 PHP 服务端源码，因此不把具体内部流程、Key 类型或认证头写成已知事实。[官方工程师对角色 API 使用方的确认](https://www.reddit.com/r/LastEpoch/comments/1aqs46z/comment/kqewa7d/)

父任务已确认本机直接请求此 LETools 内部接口能读到指定四角色，部署的 Cloudflare Workers 请求则被来源站以 `403 / Attention Required` 拦截。这是**本次项目环境观察**，不是 EHG 的 API 开放政策，也不是四个角色、任意来源或所有云出口均可长期访问的保证。此研究没有重新请求角色数据或尝试规避拦截。

LETools 的 About 明确自己是 Dammitt 维护的 fansite，并非 EHG 官方网站。因此“LETools 有一个浏览器可以调用的接口”和“EHG 向 LE-filter 开放了官方 API”是两个独立判断。[LETools About，2026-10-18 读取](https://www.lastepochtools.com/about/)

## 正式接入可走到哪一步

1. 通过[官方支持表单](https://support.lastepoch.com/hc/en-us/requests/new)提交**接入意向及当前资格咨询**，请求转给 Character Data API／第三方工具负责人。该入口是现在可验证的官方联系渠道；它不是已确认的 API 申请门户。[Mike 曾建议联系支持，2024-02-28](https://www.reddit.com/r/LastEpoch/comments/12p161l/comment/kskyjky/?context=3)
2. 把 LE-filter 的范围写具体：开源个人过滤器工作台、由用户主动提交 1–12 个角色链接、只读当前配装、不请求仓库／市场写操作、预期调用量、缓存周期、项目和域名链接。以上是本项目建议提供的评估资料，**不是已查到的 EHG 强制申请表字段**。
3. 先询问现在是否接受新工具、是否支持非商业个人项目、所需合作条件，以及官方文档／认证／限流／缓存／数据使用条款。得到明确答复后，才能把官方直连作为实现路线；本次没有获得这些答复或凭据。
4. 如果保留 LETools 作为数据提供方，可按其[作者公布的联系页面](https://www.lastepochtools.com/contact/)咨询 Dammitt：是否允许 LE-filter 后端使用角色导入服务、支持何种服务端访问方式和配额。页面当前列出 Discord 私信和作者服务器；该联系路线只适用于 LETools 服务，不能代替 EHG 的官方授权。

本研究未向 EHG、Dammitt 或其他人发送消息。

## 对 LE-filter 的可行路线判断

| 路线 | 本次证据支持程度 | 实施前仍缺什么 |
|---|---|---|
| 直接用无需合作方资格的 EHG 公开角色 API | **未找到可实施的官方公开契约**，不应在当前功能中承诺已可用。 | 官方上线说明、明确适用的端点与字段、访问／认证条件、限流与数据使用规则。 |
| 与 EHG 接洽获得正式访问 | 有历史合作方先例，支持渠道可表达兴趣。 | EHG 对当前申请资格的答复与批准；无法保证个人项目能获准。 |
| 经 LETools 或其他工具提供方的角色服务 | LETools 在线导入是真实存在的一手功能；当前云端 403 是本项目实际约束。第三方服务可达不等于 EHG 官方 API 已公开。 | 提供方允许和支持的集成方式、稳定性、刷新／配额约定；本次不以换出口或规避防护作为结论。 |
| 用户主动导出的角色／Planner JSON | LETools 原生支持把在线角色导入为 Planner；适合把取数结果作为明确输入保存。[作者说明](https://www.lastepochtools.com/news/article/site-update-online-character-import-and-character-profiles) | 会增加用户操作，无法满足“网页一步自动取数”的全部体验；仅是数据输入备选。 |

这里没有建议改变已确认的过滤器条件、整批失败策略、个人保存隔离或已有模版字节约束。接入来源变化需要独立确认，不由研究文档自动触发部署。

## 证据局限与排除的误读

- [2025-02-25 官方论坛讨论](https://forum.lastepoch.com/t/api-for-developers/74843)里关于 Kain“仅合作方可访问”的文字，是普通用户 DJSamhein 转述 Discord；没有附可核对的 Kain 原始消息。本次不把它当成已验证的官方当前声明。论坛域名本身不使普通用户回复变成官方政策。
- [2025-01-27 Reddit](https://www.reddit.com/r/LastEpoch/comments/1ibe9eb/)中“可以申请 partner”也是社区用户的说法。它不能推翻 Mike 在 2024 年关于没有流程的直接答复，也不能建立 2026 年已存在正式审批渠道的事实。
- 使用了开发者追踪站与非官方 Roadmap 寻找历史链接，但关键结论已回到 EHG 本人 Reddit 回复、官方支持页与 Dammitt 作者原文，不以聚合页替代原始证据。
- 2026 年官方支持页的 Game Data API 与开发者所称 Character Data API 名称／范围不同，可能涉及不同服务或开放工作；本次未取得统一架构文档，保留差别。
- 本次没有找到公开的 EHG 角色 API reference、OpenAPI、开发者控制台、自助 Key 或明确宣布面向公众开放的官方页面。**检索未找到不是对所有非公开合作安排的穷尽，也不是永久不开放的证明。**
- 没有猜测官方端点，没有寻找或取得他人凭据，没有绕过认证、来源站防护或改变部署。没有游戏客户端实测。

## 父任务补充：已验证的Maxroll公开角色通路

2026-10-18读到[LastEpochBuilding导入源码](https://github.com/uta666XYZ/LastEpochBuilding/blob/main/src/Classes/ImportTab.lua)的`DownloadFromMaxroll`和`DownloadLEToolsProfileBuild`：将LETools链接中的账号／角色名用于`GET https://planners.maxroll.gg/lastepoch/characters/{account}/{character}`，返回角色保存格式的`savedItems`。本机和同一Sites Cloudflare后端均成功读取用户指定四角色。该接口不是本次发现的EHG官方公开端点，也没有取得其刷新或配额的长期服务合同。

上线实现只保留已装备物品序列化字节并由本地／浏览器Python解码，76件目标身份和各类词缀池逐件对齐LETools独立API；来源标注为Maxroll。路线和验证见[导入说明](../PROFILE_IMPORT.md)。以上补充替代“必须换云平台”的实施判断，不改变前文关于EHG公开访问条件尚未核实的研究结论。
