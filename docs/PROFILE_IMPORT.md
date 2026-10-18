# LETools角色配装导入

工作台左侧“导入LETools角色（多链接并集）”接受同一BD的1–12个角色链接，每行一个，重复链接去重。多个角色合并成一个可编辑的个人BD，默认新建个人方案，也可加入当前方案。此功能只写“我的保存”，不会修改已有模版。已有模版的更新仍由仓库明确维护。

## 读取步骤

1. 粘贴链接，可填写个人BD名称，点击“生成读取书签”。
2. 将“读取LETools角色”拖到Chrome／Edge收藏栏，然后打开第一个角色页面。
3. 页面加载完成后，点击收藏栏中的读取书签。它在LETools页面读取全部链接；完成后点击“返回工作台，预览并集”。也可下载角色JSON，再在导入对话框选择该文件。
4. 核对暗金、装备、神像、祭坛等数量，点击“保存个人BD”。继续调整目标、预览规则，再导出filter；可另存单BD需求JSON或整套配置备份。

静态GitHub Pages不能直接跨站读取LETools；来源站也会对服务器请求返回访问验证。书签通过用户已打开的LETools页面发起同源读取，不使用公共代理、登录凭据上传或关闭浏览器保护。遇到来源站验证、私有角色、失效链接或未知ID时显示错误；任意链接失败都不返回部分并集。链接仅支持具体角色的当前配装，不读取攻略、Planner、账号主页或历史快照。

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

[原生检查](../analysis/profile-import-validation.json)与[WASM完整输出对照](../analysis/profile-import-wasm-validation.json)记录组合、保存输入及边界。读取书签的同源请求顺序使用来源字段结构夹具验证，真实角色目标由可见UI交叉核对；这不等于已经在真实浏览器执行收藏栏书签、下载Blob或进行游戏客户端实测。
