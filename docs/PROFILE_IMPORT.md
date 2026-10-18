# LETools角色配装导入

工作台左侧“导入LETools角色（多链接并集）”接受同一BD的1–12个角色链接，每行一个，重复链接去重。多个角色合并成一个可编辑的个人BD，默认新建个人方案，也可加入当前方案。此功能只写“我的保存”，不会修改已有模版。已有模版的更新仍由仓库明确维护。

## 读取步骤

1. 粘贴链接，可填写个人BD名称，点击“读取角色并预览并集”。无需书签，也无需转存Planner。
2. 等待读取全部角色，核对暗金、装备、神像、祭坛等数量，点击“保存个人BD”。
3. 继续调整目标、预览规则，再导出filter；可另存单BD需求JSON或整套配置备份。导入对话框也保留已有角色JSON的读取入口。

静态GitHub Pages通过专用后端，从链接提取账号／角色名，调用Maxroll公开角色接口`GET https://planners.maxroll.gg/lastepoch/characters/{account}/{character}`。返回中只保留已装备物品、神像、祭坛的序列化字节和来源更新时间；背包、技能、祝福及其他角色状态不进入工作台。浏览器内的Python适配器解码目标，分类和XML生成继续调用原引擎。任意角色读取失败、身份不符、序列化格式未知或词库缺ID时整批报错，不创建部分方案。链接仅支持具体角色的当前配装，不读取攻略、Planner、账号主页或历史快照。

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
- 装备普通词缀按类型合并，包含低阶、传奇合成及普通封印词缀；特殊类别按冻结词库ID判定，不能只看来源页签。腐化6、附魔4另存参考，固定随机词缀7存入来源参考。
- 普通神像只计0／5类。不同类型、不同底材范围分别保留，同范围的候选词缀取并集，沿用现有一项／两项规则；不从多个角色锁定精确前后缀配对。
- 祭坛保留实际底材；其普通、腐化和附魔词缀作为实际祭坛目标。
- 普通装备才补入其明确底材，多个底材按替代收集，不猜首选。练级独立留空，技能、天赋和祝福不导入过滤器。

词条顺序保留首次来源顺序，后来的新词条追加，供玩家调整。普通角色配装中的偶然词缀也可能进入并集；导入页明确提示这一点。生成仍调用原`tool/engine.py`，保留颜色、提示、阶段、23类装备和超过200条报错的现行规则。

## 本次追心手里剑模版

玩家明确要求将以下四个角色与原Very Strict模版取并集，因此本次更新了仓库里的追心手里剑终局需求。普通用户通过上述导入功能只创建个人方案。

- [MAONG · vsnail](https://www.lastepochtools.com/profile/vsnail/character/MAONG)
- [ShurikenAmhali · Amhali](https://www.lastepochtools.com/profile/Amhali/character/ShurikenAmhali)
- [S5Luciann · chachapieng](https://www.lastepochtools.com/profile/chachapieng/character/S5Luciann)
- [MaadCity · 47x47](https://www.lastepochtools.com/profile/47x47/character/MaadCity)

2026-10-18从可见Profile→Planner物品编辑器逐件读取76件物品及全部已用词缀页签，冻结[原始UI摘录](../sources/builds/heartseeker-shuriken-profiles-2026-10-18.json)。该摘录不是原生API响应。解码后13种暗金／10装备组／11神像组／1祭坛；再与原模版取并集为14种暗金／10装备组、56项普通部位目标／15神像组／1祭坛，无独立05，练级留空。新增暗金为丛林女王的储物腰带92、埃莱克的创新402、先驱者之针344；原11项完整保留。完整目标见[追心手里剑审阅](SHURIKEN_MARKSMAN_REVIEW.md)。

已有个人保存保持原样；需要更新时重新应用模版，或导入[同id新版终局需求](../requirements/heartseeker-shuriken-marksman.endgame.json)只更新该阶段。

## 复现与验证

```powershell
python -X utf8 scripts/extract_shuriken_profiles.py
python -X utf8 scripts/build_shuriken_marksman_requirements.py
python -X utf8 scripts/validate_profile_import.py
python -X utf8 -m unittest discover -s tool -v
python -X utf8 scripts/build_pages.py
node scripts/validate_profile_import_wasm.mjs
```

[原生检查](../analysis/profile-import-validation.json)与[WASM完整输出对照](../analysis/profile-import-wasm-validation.json)记录组合、保存输入及边界。新增原生API目标字段冻结在[sources/builds/letools-character-api-2026-10-18.json](../sources/builds/letools-character-api-2026-10-18.json)，四角色共76件，与既有UI摘录的目标集合及底材范围一致，顺序可因API字段顺序不同而不同；该夹具不重建或覆盖已有模版。

新通路的最小原始响应冻结在[sources/builds/maxroll-character-api-2026-10-18.json](../sources/builds/maxroll-character-api-2026-10-18.json)。76件物品逐位置比较物品类型、底材、暗金ID及普通／腐化／附魔／固定词缀池，全部等于独立LETools API结果。两枚戒指的游戏容器9／10分别对应LETools的ring2／ring1；普通词缀位于腐化槽时仍按ID保留普通类别。

`tool/character_save.py`只解码目标身份，不计算属性roll或沿用角色装备的来源门槛。布局另与本机1.5.2.2的`ItemData.RebuildID`（RVA `0x1205E80`）／`setValuesFromSerialisation`（`0x12127E0`）静态指令核对，GameAssembly SHA256为`d5f9fb458f0e9878e697a92b590a586a52fd77e645f8bf87bb4f2b74c6c56567`：v6类型位于字节5，普通词缀数量取字节13低6位；暗金／套装字节22高3位为数量，传奇低3位为数量；随后每项3字节，首字节低4位＋次字节为ID、首字节高4位＋1为阶数。LP／封印／腐化等标志和尾部记忆／馈赠／编织信息不能被当成词缀数量或新词缀。版本2、3–5的短身份头按游戏升级拷贝布局处理；未知版本、越界和未知ID明确退出。

```powershell
python -X utf8 scripts/validate_profile_api.py
python -X utf8 scripts/build_pages.py
node scripts/validate_profile_api_wasm.mjs
node --test tool/test_profile_relay.mjs
```

后端与浏览器协议测试覆盖链接、CORS、请求大小、来源身份、整批失败、缓存去重和个人保存隔离。[API原生验证](../analysis/profile-api-validation.json)、[WASM完整输出对照](../analysis/profile-api-wasm-validation.json)及[网页验证](../analysis/profile-api-browser-validation.json)记录实际检查。游戏客户端及浏览器Blob下载不作为这些验证的结论。
