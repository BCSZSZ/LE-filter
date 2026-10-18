# LETools角色配装导入

工作台左侧“从角色链接创建模版”接受同一BD的1–12个角色链接，每行一个，重复链接去重。多个角色合并成一个可编辑的个人模版，不直接创建或修改方案。保存后可与其他个人模版、预设模版一起多选，再新建组合方案。预设模版仍由仓库明确维护。

## 读取步骤

1. 粘贴链接，可填写个人BD名称，点击“读取角色并预览并集”。无需书签，也无需转存Planner。
2. 等待读取全部角色，核对暗金、装备、神像、祭坛等数量，点击“保存个人模版”。模版自动选中并打开编辑，练级独立留空。
3. 在两类模版中加选副BD、指定主BD，点击“用所选模版新建方案”，再预览或导出filter。已有方案可通过“添加BD”选择两类模版；也可把当前BD另存为个人模版。导入对话框保留已有角色JSON的读取入口。

旧版通过角色链接创建的方案会自动补入个人模版库，原方案、已编辑目标和主副设置保留。相同BD的不同编辑版本分别保留，升级后不会重复补入。个人模版和方案均随顶部“保存配置”备份。

静态GitHub Pages通过专用后端，从链接提取账号／角色名，调用Maxroll公开角色接口`GET https://planners.maxroll.gg/lastepoch/characters/{account}/{character}`。返回中只保留已装备物品、神像、祭坛的序列化字节和来源更新时间；背包、技能、祝福及其他角色状态不进入工作台。浏览器内的Python适配器解码目标，分类和XML生成继续调用原引擎。任意角色读取失败、身份不符、序列化格式未知或词库缺ID时整批报错，不保存部分模版。链接仅支持具体角色的当前配装，不读取攻略、Planner、账号主页或历史快照。

### 数据来源为何改为Maxroll

LETools Planner的Import确实调用其自身`POST /import_character.php`，参数为`accountName`、`charName`。本机可成功读取，但部署的Cloudflare Workers出口被LETools返回`403 / Attention Required`；具体WAF规则不可见，不能断言只是IP原因。LETools返回的跨域许可也只允许其自身网站，静态Pages不能直接调用。

EHG开发者确认过LETools和Maxroll使用官方Character Data API，但没有找到可直接实施的EHG公开角色接口文档／访问方式，详见[官方API调查](research/LE_OFFICIAL_CHARACTER_API.md)。目前上线的是第三方Maxroll角色接口，不声称LE-filter直接访问了EHG数据库。接口路径可在[LastEpochBuilding的导入源码](https://github.com/uta666XYZ/LastEpochBuilding/blob/main/src/Classes/ImportTab.lua)核对。本次现有云端后端已成功访问四角色，无需Render账户。

读取期间修改链接或关闭对话框，会取消本次读取并丢弃迟到结果；重新读取期间旧预览不能保存。后端对成功的角色响应最多缓存5分钟，重复角色请求共用读取。

## 后端与部署

- 后端地址：`https://le-filter-profile-api.astutestoat4.chatgpt.site/api/profiles/read`；健康检查为`/health`。
- 入口接收`{links: [具体角色URL], name: "可选名称"}`，返回`letools-profile-bundle`。浏览器只接受与本批链接数量、顺序和身份匹配的完整结果，再送入`/api/profiles/import`分类。
- 固定来源主机和接口，输入URL不能指定请求目的地；禁止重定向。每次最多12角色，3个并发，每个来源20秒超时，限制请求体和响应大小。浏览器CORS允许现有工作台及localhost预览，不使用通用公共代理。
- 源码在[services/letools-relay](../services/letools-relay/README.md)。Sites项目身份保存在该目录的`hosting.json`，后端有独立受管理源码仓库；更新沿用同一Site，先验证实际云端读取，再发布前端。现有GitHub Pages发布流程不托管后端。

## 目标边界

- 暗金按实际物品ID收集；暗金神像也按ID收集，暗金自身底材和固有属性不转成普通素材需求。
- 装备词缀按部位取实际普通槽中恰好T6／T7的并集；T5及以下、T8、封印和其他附加槽均不进入装备目标。普通槽上的已知实验词缀也可收集，例如MaadCity腰带713。腐化槽中的普通ID明确排除，不把整件已腐化装备的合法普通槽一起排除。
- 阶数和槽位必须来自实际数据。旧角色JSON若缺少装备普通词缀阶数，明确报错并要求重新读取，不猜T6／T7。每项原始ID、阶数、来源槽及排除原因保存在来源`affix_details`中；真正腐化6、附魔4及固定随机7继续按冻结词库另存参考。
- 普通神像只计0／5类，腐化槽中的普通ID不入普通目标。不同类型、不同底材范围分别保留，同范围取并集，沿用一项／两项规则。神像和祭坛不套装备的T6／T7筛选。
- 祭坛保留实际底材；其普通、腐化和附魔词缀作为实际祭坛目标。
- 普通装备才补入其明确底材，多个底材按替代收集，不猜首选。练级独立留空，技能、天赋和祝福不导入过滤器。

词条顺序保留首次合格来源顺序，后来的新词条追加，供玩家调整。只对本次profile提取应用上述筛选，已有个人方案不自动覆盖。生成仍调用原`tool/engine.py`，保留颜色、提示、阶段、23类装备和超过200条报错的现行规则。

## 本次追心手里剑模版

2026-10-19玩家确认全部需求按以下四个角色重新生成，不再与旧Very Strict模版合并。此为明确授权的预设模版维护；普通用户通过导入功能创建个人模版。

- [MAONG · vsnail](https://www.lastepochtools.com/profile/vsnail/character/MAONG)
- [ShurikenAmhali · Amhali](https://www.lastepochtools.com/profile/Amhali/character/ShurikenAmhali)
- [S5Luciann · chachapieng](https://www.lastepochtools.com/profile/chachapieng/character/S5Luciann)
- [MaadCity · 47x47](https://www.lastepochtools.com/profile/47x47/character/MaadCity)

本次重新读取76件已装备物品，冻结[2026-10-19原始API字节](../sources/builds/shuriken-profile-bundle-2026-10-19.json)。MaadCity的手套、腰带、遗物与旧快照不同。当前13种暗金／10装备组、28项普通槽T6／T7目标／11神像组／1祭坛，无独立05，练级留空，独立生成96条。旧XML独有的毁灭机巧459退出BD目标，通用保护独立保留。完整目标及可直接导入的XML见[追心手里剑审阅](SHURIKEN_MARKSMAN_REVIEW.md)。

此前14暗金／56装备目标／15神像是旧XML与profile合并的历史结果。原[UI摘录](../sources/builds/heartseeker-shuriken-profiles-2026-10-18.json)、两份2026-10-18 API快照、原XML及其他BD保持；旧模板读取函数仅供历史追溯。

已有个人保存保持原样；需要更新时重新应用模版，或导入[同id新版终局需求](../requirements/heartseeker-shuriken-marksman.endgame.json)只更新该阶段。

## 复现与验证

```powershell
python -X utf8 scripts/extract_shuriken_profiles.py
python -X utf8 scripts/build_shuriken_marksman_requirements.py
python -X utf8 scripts/validate_profile_import.py
python -X utf8 scripts/render_shuriken_profile_review.py
python -X utf8 -m unittest discover -s tool -v
python -X utf8 scripts/build_pages.py
node scripts/validate_profile_import_wasm.mjs
```

[当前原生检查](../analysis/profile-tier-validation.json)与[WASM完整输出对照](../analysis/profile-tier-wasm-validation.json)记录profile单独重建、槽位／阶数、组合、保存输入及边界。旧[原生API](../sources/builds/letools-character-api-2026-10-18.json)与[原始字节](../sources/builds/maxroll-character-api-2026-10-18.json)提供76件独立交叉证据，普通／封印／腐化槽的ID与实际阶数逐项一致；旧[导入验证](../analysis/profile-import-validation.json)保留为此前策略记录。

两枚戒指的游戏容器9／10分别对应LETools的ring2／ring1。词缀类别仍按冻结ID核查，但类别普通不再足以入选：还须位置为普通槽、阶数符合装备T6／T7要求。

`tool/character_save.py`解码身份、实际阶数和槽位，不计算属性roll。布局与本机1.5.2.2的`ItemData.RebuildID`（RVA `0x1205E80`）／`setValuesFromSerialisation`（`0x12127E0`）静态指令核对，GameAssembly SHA256为`d5f9fb458f0e9878e697a92b590a586a52fd77e645f8bf87bb4f2b74c6c56567`：v6类型位于字节5，普通词缀数量取字节13低6位；暗金／套装字节22高3位为数量，传奇低3位为数量；每项3字节，首字节低4位＋次字节为ID、首字节高4位＋1为阶数。

普通装备字节13的bit7／bit6分别标记封印／腐化槽，两者先于普通词缀序列；传奇腐化槽为最后一项，须同时检查字节8的bit4（物品已腐化）及字节22的bit7。未腐化编织者传奇的同一高位属于剩余WW，不能误当腐化槽。LP／封印／腐化标志和尾部记忆／馈赠等不能被当作数量或新词缀。版本2、3–5按短身份头的相对偏移处理；未知版本、槽位数量不符、越界和未知ID明确退出。

后端与浏览器协议测试`node --test tool/test_profile_relay.mjs`覆盖链接、CORS、请求大小、来源身份、整批失败、缓存去重和个人保存隔离。此前[API原生验证](../analysis/profile-api-validation.json)、[WASM完整输出对照](../analysis/profile-api-wasm-validation.json)及[网页验证](../analysis/profile-api-browser-validation.json)保留为最初API接入记录；当前目标筛选使用本节上方复现流程。游戏客户端及浏览器Blob下载不作为这些验证的结论。
