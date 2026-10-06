# 后续工作 memo

更新时间：2026-10-07，日本时间。当前阅读顺序：README → SOUND_STYLE_REVIEW → CURRENT_FILTER_GUIDE → CURRENT_RULES_REVIEW → BASE_TEMPLATE → 本memo；填空来源查STRICT_VARIABLE_REVIEW和RAXX_VARIABLES，原始Raxx查FILTER_GUIDE、analysis/rules.json和sources/manifest.json。

## 最新成品：v3四档提示

- 用户本轮要求清晰名称、全部情况四档归类、无声无地图图标、主副分组、合并同条件与审查T6压缩。成品v3共144条（133启用／11关闭）；原138条v2保持不动，其复现脚本在82e557d。当前current三脚本改为生成／验证／渲染v3，报告路径沿用current-filter-report与current-filter-validation。
- 声音ID：静音1、铁匠14、开始6、灵感9、彗星12。图标：None=1，Default=0；静音不能用0。所有规则明确BeamOverride=true，静音NONE；四档SMALL／MEDIUM／LARGE／LARGEST，图标2／7／8／5。普通静音灰色；BD文字粉8／蓝12，光柱对应粉11／蓝15，不是同一ID表。格式参考sources/filter-style-reference.json是从已校验哈希的Tools代码和中文词库提取，不依赖.cache，不冒充游戏引擎。
- 用户已确认WW按14／17／20分开始／灵感／彗星，低于14的BD目标铁匠，非BD名单WW1–13静音。LP和WW拆为独立规则，避免假定同一PotentialCondition的组合语义。LP=1／2按用户“任意暗金”扩大到无名字限制；BD LP=1有主／副灵感层。WW17–19、14–16沿用原412项名单并补缺少3种BD目标，WW≥20不限名字。
- 0LP BD主名单把原共享2项与主专属9项合成11，副专属9项；shared_unique_ids保留来源，不把整条11项声称为全部共享。珍贵名单152及原364项roll边界保持，低WW静音子层另引用同一份（成品728次边界引用）。
- 2026-10-07用户纠正T8通常不值得高提示，最多铁匠或可静音。当前取铁匠保留兜底，撤回初版置顶彗星。原Raxx R37音效是Begin=6，彗星和置顶是我们的误判。全1156池保持，当前G66在C1／C2／C3与实验／冠军后、C4前。C1／C2／C3／C4的T7门槛改为EQUAL 7；T8不冒充BD单T7，不凑双／三／四T7。冻结Base v1仍有≥7历史条件，成品覆盖必须保留，未来生成不得重新混计。
- 任意4+真正T7彗星、3T7灵感、2T7铁匠，均完整1156池与23装备类型；只有4+T7置顶。一般传奇灵感，不反推合成前LP，T8本身不再升档。双／三T7先于C1目标单T7开始；C3非目标单T7＋BD目标不限阶铁匠；实验／可选冠军入口先于T8兜底、静音C4及T6。通用强规则先匹配时用通用档色，不判主副。
- C1主G25–34、副G35–43；C3主G44–53、副G54–62。C4当前G67，一条默认开启、手动关闭、无等级退出，名称[C4 额外单T7阶段：手动关闭]。C3名称[C3 非目标单T7＋BD目标词缀]里的C3是分类，目标仅至少1条，阶数不限。
- T6只合并同主BD且同条件／同目标池的匕首与单手斧（2／718／943），19→18，展开类型后的条件集合与v2完全相等。当前主G68–76、副G77–85；0–84级、85自动不匹配，静音无图标，其他部位目标池不混。实验属性优先铁匠；C3、实验、碎片和底材仍可保留T6。
- 神像两项灵感、一项开始，普通池不含腐化；骷髅仍保留四条BIS入口，没有新增常驻一项收集。通用过渡神像广池静音；BD祭坛至少1目标开始，不增造两项毕业判断。精确前后缀、891备用和祭坛腐化重要性仍可单独审阅。
- SOUND_STYLE_REVIEW覆盖全部旧G1–138且列能力缺口；CURRENT_ALERT_INDEX逐条来自真实144条XML。验证包括100个有限全过滤器案例、T8独立铁匠及不混入T7数量、T6展开等价、42条其他规则条件／开关保持、20目标0／1LP及LP／WW边界、无声无图标与颜色对应。未模拟唯一属性roll、封印／特殊词缀计数或游戏听音；没有逐条音量字段，不承诺四种声音客观响度递增。

## 上一版快照：Flay＋Skeleton v2


- 用户已明确要求按新基底生成最新版。成品filters/Flay-Mana-Lich+Skeleton-Necromancer-v2.xml，138条（127启用／11关闭），原187条XML、原Raxx、Strict、通用Base v1保持字节不变。Flay主粉8、Skeleton副蓝12；同层主先匹配，共享按主，收集条件是两者并集。
- 19份目标分别绑定C1／C3／T6，C3目标不限阶数且全池T7，不加FP／未腐化门槛。C2／C4全1156ID、23类装备不缩窄。C4在当前G57，原R60、基底B61；默认开启、手动关闭。T6仍0–84级，无常驻双T6保护。其他实验／碎片／底材路径仍可能保留非目标单T7。
- 暗金仅20种Strict目标，三条身份提示加原R15合并152项；全部目标有无潜能门槛路径，不另建BD的1／2／3LP规则，不加旧正文5种替代品。原143项对象及364条唯一属性roll边界完整保留，高LP通用层原样保持，可能先于BD颜色提示。
- Flay四条神像层已实际填入，两项普通目标优先Begin=6声音，一项静音=1；Weaver／Lagon都收。骷髅4条源BIS入口剥离腐化、至少2项普通目标、阶数不限，保留源底材，包括多职业Large Omen；未知更窄配对不按名字推断。普通目标池可能含特殊附加属性，不将任意两项称为精确前后缀毕业。通用过渡普通池补入两BD目标，保留90／75级退出。
- 祭坛按BD类型／底材和目标池绑定，至少1项、阶数不限，保留其腐化目标；不移植Strict合计T8／T10及双崇高门槛。神像腐化不参与普通池计数，与祭坛目标不是同一决策。
- 原R81升华、R83紧缺碎片和R136／137开荒优选底材因没有确定用途／库存／开荒路线而关闭；R83已填36／825／945候选，不能称为玩家库存紧缺。原R69普通实验目标676／679已填，仍关闭；R68广泛崇高实验保持。原R82按Strict五类底材填入并启用，保留原稀有度、不带Strict词缀／FP条件，永恒臂铠共享。原侍祭碎片R84和通用进攻／防御碎片R89／90保留，其他四职业碎片关闭。原早期通用分支保留，未用终局武器倒推开荒路线。
- 当前只运行generate_current_filter、verify_current_filter、render_current_filter；只复用旧脚本的纯帮助函数，旧主程序及历史输出不重建。来源、G／B／R／X映射和哈希在current-filter-report.json；结构、原规则保持、类型绑定、阶段关闭和35个有限案例在current-filter-validation.json。不是客户端／封印计数实测。
- 模板情报提取仍只读XML，随后生成具体成品；CURRENT_FILTER_GUIDE列当前默认和玩家待办，CURRENT_RULES_REVIEW逐条从XML翻译，CURRENT_RULE_POOLS保存全部大名单与roll边界。后续更新成品须运行生成、验证与文档渲染，并检查确定性和提交后哈希。

## 当前交付：用户确认的新基底与BD填空情报

- 当前后续使用templates/LE-base-v1.xml：162条（103启用／59关闭），仍含56条蓝色说明。scripts/build_base_template.py从原版重建，base-manifest.json记录原R／当前B映射、完整1156词缀ID及哈希；源Raxx、两份Strict、视频发布前原文和旧187条XML不改。模板尚未填两BD目标，不是最终成品。
- 用户确认四类依次匹配：C1／V05对应类型BD目标T7；C2／V06任意双／多T7全量保护；C3／V09对应类型BD目标不限阶数＋全池T7；C4／V07额外单T7阶段全量兜底。C1／C2／C3常驻，C4默认开启，由玩家阶段结束后手动关闭，没有自动等级退出。
- C2／C3的T7计数与C4用冻结version150全部1156个ID，C2／C4保留原23类普通装备（15类武器／副手＋8类其他），排除神像／祭坛，不按BD裁剪。原623／42／343项名单保留在RAXX_DEFAULT_EQUIPMENT_POOLS，仅作历史对照，不再是当前宽池待决项。未来版本新增ID需更新冻结资料并重建。
- 原R60／61合为一条R60来源的阶段规则，移到R62之后；原R61删除。当前位置C1=B38–47、C2=B48、C3=B60、C4=B61，T6=B62／63（原R63／64）。之后原R编号比B大1。V08只保留历史入口，不再单独配置。其他功能规则相对次序不变；原R29职业隐藏保持关闭，后续不能让它抢先破坏全量保护。
- C4用至少1条T≥7的有效XML条件，经C1／C2／C3先匹配后兜底剩余单T7，不伪造最多1条条件。关闭C4保留前三类，但其他实验／碎片规则仍可能显示非目标T7，不能承诺全部隐藏。
- 原双T6／T7＋T6常驻R48改为至少2条T≥7。V10仍至少1条所选T≥6、角色0–84级，85级退出；C4手动退出与此无关。T6仍可由实验／碎片等其他路径保留；85级是收集策略，不要求丢弃身上T6。
- C1与C3使用相同19份Strict部位目标，必须按BD／装备类型绑定。C3只移用目标名单，忽略Strict来源T7门槛，目标阶数不限；全池另至少1条T≥7。原R62的10项预填仍是模板示例，不能冒充两BD真实目标。Wanted/Havoc全局混池仍完整记录作证据，不取代部位绑定。
- C3不加FP、未封印计数或未腐化收集限制，符合用户第三类就留；保留不保证可以制作。Havoc实际要求未腐化且4条未封印词缀；不能把规则显示写成制作可行或成功保证。T7在目标上时C1先匹配，多T7由C2先匹配。
- 用户确认备用关系可作为后续补充，至少普通／腐化区分要自动化。Strict给ID但不给逐词缀腐化标签；split_affixes统一按冻结specialAffixType=6分类，供V13／V19／V21使用，不按名称或固定腐化ID名单猜测。未知ID查表报错，不默认普通。新增自动输出strict-idol-affix-classification.json与STRICT_IDOL_CLASSIFICATION.md，覆盖12条两BD神像源规则，保留源ID、底材、启用状态与出处，不依赖Guide／Planner。
- 神像本轮修正：以前把普通与腐化ID混在同一个计数池，会让843＋1070误充双目标毕业。V19／V21按specialAffixType=6剥离腐化参考；affix_ids只含普通目标，corrupted_affix_ids独立，原affix_pools仍保留全部源ID。V13的早期腐化参考不删除。
- 用户明确Flay：中型843＋854、厚实876＋886，各记录1项候选／2项组合毕业两层；都保留Weaver与Lagon，腐化状态不限、阶数不限，两项优先，声音不同。user_reviewed_flay_idol_layers记录4层，标明来源是用户审阅而非Strict等价复制。“毕业”只是普通组合齐全，不指满roll；其他BD配对仍待审阅。
- 必须／选择条件可用多份AffixCondition共同满足，官方1.1已支持、原R62也有两份。照用户目前候选池，厚实只有886仍被保留；若要求876必有要明确采用必选条件，不静默收紧。891备用与最终祭坛1105需要腐化神像来自正文，不假称为Strict导出，也不自动加进这4层。机制及来源见FLAY_IDOL_REVIEW.md。
- 用户已纠正方向：按Raxx设计，Strict仅填定制变量；先确认四类T7政策并建立通用模板，再明确要求生成两BD最新版。当前成品按本文开头的v2流程生成，不直接移植Strict策略。
- scripts/extract_raxx_variables.py读取实际新模板及冻结原版，提取24组变量；蓝字56条全部归入填空说明或固定说明。机器结果template_slots映射原R到当前B，template_default_overrides仅存有变化的B默认值，无变化入口继承baseline_defaults，避免重复巨大的原暗金roll字段；文档直接读实际模板展开全部当前门槛。数据与文档为RAXX_VARIABLES、STRICT_VARIABLE_REVIEW、raxx-variables.json、raxx-variable-extraction.json和variable-extraction-validation.json；不读Planner JSON或攻略正文，不依赖.cache。
- 已提取两BD各11种暗金，共20种、无套装目标；R15原143项已有11种，追加缺少的9种可形成152项候选。原珍贵名单保持，所有BD目标0LP也留，不增加BD独立LP分层。旧25种目标包含额外5种正文替代，不能冒充Strict本身导出。
- 38份部位T6／T7池两层逐部位相同，C1／C3使用其中19份目标、V10复用对应T6名单；新C2／C4不能被它们缩窄。保留原R63／64在85级退出、R128／129在90／75级退出。原R127实际数量1、advanced=false，阶数不限，不能误写为T6门槛。R68原广池默认不缩到两个BD实验目标，R69是否采用另审。
- Source family明确区分BD目标、generic_idol／generic_altar及maxroll_only_crafting；通用Weaver／反伤、通用祭坛与FP52不当作BD填空目标。原Strict Havoc第一份是全局Wanted池、另一份1156项是通用T7池；新C3按部位提目标，不以全局Wanted混池替代。
- 底材／词缀／尺寸／BD绑定保留。Large Omen来源包含五职业底材，单职业入口映射标为待判别，不能因此声称五职业都要收集。开荒路线、排除职业、升华用途、真实紧缺库存不能从终局Strict自动确定。
- sources/builds/strict-variable-reference.json固定20个目标的isSetItem和1156项specialAffixType，来自此前已验证哈希的version150缓存；运行期不读取缓存。名字来源沿用game-reference、maxroll-reference-supplement与7底材review-reference。
- 新模板验证检查162条排序、1156全池、141条无关源规则字段保持、15个有限T7模块案例（含关闭阶段后前三类仍留）；不声称整个未配置模板或客户端掉落实测通过。提取另检查来源／模板哈希、271条Strict、56说明覆盖、C1／C3目标一致；提取前后原版、Strict、模板、旧filter字节不变。
- 基底与情报复现依次python -X utf8 scripts/build_base_template.py、scripts/verify_base_template.py、scripts/extract_raxx_variables.py，随后使用本文开头的current流程填入具体BD。旧generate_filter／verify_generated_filter／render_rules_review主程序不执行，帮助函数可只读复用。

## 上一轮历史试制：曾直接移植Strict条件

- 上一轮采用Strict部分拾取门槛的双BD试制已完成；下列条目记录当时方法，已被本memo开头的Raxx变量流程取代，不代表当前最终设计。
- filters/Flay-Mana-Lich+Skeleton-Necromancer.xml：187条、171启用、16明确关闭；25种目标暗金。最新约定MAIN主套路粉8／SECONDARY副套路蓝12，共享显示MAIN粉8；本次默认Flay主、Skeleton副（按给出顺序的假定，非用户明确指定）。唯一启用HIDE为G187；不启用职业隐藏，收集是显示条件并集。
- 运行python -X utf8 scripts/generate_filter.py，再运行scripts/verify_generated_filter.py和scripts/render_rules_review.py。依赖标准库与已提交资料，不需要.cache、网络或用户Downloads。成品XML、transfer-report、GENERATED_RULE_INDEX、RULES_REVIEW及RULES_REVIEW_POOLS自动生成，禁止只手改输出。
- PRIMARY_BUILD是当前固定两输入生成器的主套路身份；颜色跟随身份，来源owners仍用FLAY/NECRO，display_role单独记录MAIN/SECONDARY/COMMON。没有新增勾选UI。显式共享交集／相同谓词按主套路显示；物品用不同词缀分别命中两个套路时仍保留原层级先匹配样式。
- 审阅稿覆盖全部187条和成品实际使用的16种条件（含封印／腐化条件），明确计数、advanced、EQUAL与等级上限。超22项大名单放附录，共15份名单；364项唯一属性roll边界保留原编码。sources/builds/review-reference.json只补原冻结本地化中7个所用底材名，不覆盖原基底参考。
- 先读TRANSFER_RULES与COMBINED_FILTER_GUIDE。transfer-report记录原163条、Strict全部271条的处置，以及成品→基底槽位／Strict物理X编号。93条源BD条件已转移：38条T6/T7按同类型交集＋各自差集拆成46条，55条其他谓词保持；12条Planner规则重建潜能分层／无门槛兜底。46关闭项不启用，120通用项采用Raxx策略。
- 主输入是启用的Strict部位、Rare Strict、实验、制作、神像、祭坛、拆解与暗金名单。复制整组conditions，不丢第二AffixCondition、nil、重复Uniques、advanced=false或AffixCountCondition。原JSON只补精确神像组合，正文补5种替代暗金、876/891备用、1067可选神像和41:4祭坛底材；不从roll=1或目标T7创造最低门槛。
- 原38/39已填真实武器，47取消旧遗物底材限制。原99–126的28个空神像模板由配置好的规则组替代，后27个重复槽位移出；56蓝字另行删除。29保留关闭、69按死灵需求启用、70保留关闭。81和未提供的开荒专属空模板明确关闭。保留功能按槽位保持相对次序。
- T6与Strict一项神像规则没有原基底85／75／90退出限制，100级仍启用。Raxx通用开荒兜底保持自己的上限。Strict混合池≥2不是精确前后缀；精确JSON组合另置上层，死灵三条affixes保持数量3。
- 腰带等共享拆分仅适用min=1且combined=ANY、其他条件相同的单词缀池；不能用于数量2或合计限制。其他重叠先命中的样式不表示BD优先级更高。新BD或变化的导出族要审核后接入，当前代码固定两输入，未实现勾选UI。
- sources/builds/transfer-reference.json固定35个部位目标ID的specialAffixType，1156全池直接从Strict汇总；特殊类型6仅用于15条腐化补充分支，保持原Strict OnlyUncorrupted规则另加同装备类型、目标腐化词缀任意阶候选。R37/R48扩大全池，R48类型缩到11种实际装备类。该宽松补充不是普通传奇素材的自动判定。
- 玩家剩余任务主要是进度／库存收紧、代表物品导入核对、选择可选方案；细表按G编号在COMBINED_FILTER_GUIDE。不得说每个原始空模板还待用户填写才可用。魔力34／暴击避免97碎片不在Strict默认拆解，库存需要时再加明确条件。
- 验证输出generated-validation.json：结构、25暗金保护、38源池等价、55源谓词、20离线案例通过。LP/WW组合、封印计数及神像特殊／腐化计数仍未经游戏实测；FP52/NotSealed预测必须返回unknown。生成超200条就失败，不静默截断；动态工具扩展时重新验收。
- 以下输入评估小节保留收集资料时的历史判断；其中“未生成”和直接移植Strict门槛的记录描述当时阶段。当前以本文开头的v2与Base v1流程为准。

## 用户已确定的范围与偏好

- 最初的基底研究、中文说明、memo和远程仓库已完成。两个BD先有历史合并试版，再按用户确认建立Base v1并生成当前v2；填空和生成已程序化。动态勾选工具仍未启动，没有选择工具框架。
- 用户会提供多个BD：正在玩的与一起刷装备的其他BD具有同等收集优先级，可以用颜色、声音区分。
- 用户最新要求主套路粉色、副套路蓝色，共享按主套路处理；不继续使用第三种薄荷绿BD身份。原FILTER_GUIDE／RULE_INDEX描述的Raxx颜色事实保留，不改为成品约定。
- 用户已提供Flay Mana Lich与Skeleton Necromancer两篇Maxroll攻略，链接及试制计划见PLAN.md第二阶段。不要把视频中主播的个人计划或原文预填属性当成这两个BD的真实需求。
- 用户已明确：蓝字是给玩家看的说明，基底预设有玩家待办；后续已配置、可复制filter可以删去蓝字。待办见PLAYER_TODO.md，覆盖全部56条蓝字及功能名大写指令。空模板要先填写或明确关闭，不把未配置状态直接判为作者错误。
- 保留原始基底字节；未来生成的版本另存，修改都必须对应明确需求。
- GitHub目标为个人账号BCSZSZ，LE-filter，private。用户已明确选择private。
- 远程Maxroll浏览器访问受站点安全策略阻止，不绕过。用户已提供两个Planner链接、两份JSON和本地保存的巫妖网页；可以静态分析这些用户提供的文档。JSON固定于sources/builds；巫妖正文已读取，死灵正文尚未收到。暂按基底CoF场景准备。

## 双BD输入评估（2026-10-06）

- 巫妖：11件装备、1祭坛、18个非空神像对象、10种暗金、24种词缀ID；死灵：10件装备、1祭坛、11个神像对象、9种暗金、31种词缀ID。词缀计数包含神像、祭坛和腐化属性。合并17种暗金、48种词缀ID，全部能对上当前冻结参考资料。
- 两份都是所有常规装备带uniqueID的目标配装，所有记录roll为1；不能把成品目标T7或roll当最低拾取门槛，也没有LP/WW收集门槛。导出没有攻略版本、装备阶段标签或角色等级。
- 巫妖offhand槽实际是ONE_HANDED_DAGGER，不是CATALYST；主手ONE_HANDED_AXE。死灵使用TWO_HANDED_AXE，无副手。
- 目标暗金本体、普通素材、实验词缀、腐化词缀、神像特殊附加属性要分清。Exulis469的社区元数据有传奇直接掉落与预腐化标志，摘录已冻结；不一律宣称暗金上的所有附加词缀都来自同种传奇制作。
- 暗金subType不直接限定素材底材。神像保留原组合；死灵有一枚神像的affixes数组含3条，不能一律压成2条。
- 当前最有价值的补充是攻略装备进阶／过渡配装、核心装备与属性门槛说明。仅靠最终快照不足以可靠生成完整BD成长路线。
- 复现输入清点：python -X utf8 scripts/analyze_build_inputs.py。结果analysis/build-inputs.json；来源、哈希、技能名与特殊元数据在sources/builds/manifest.json。本轮先完成用户要求的输入充分性评估，未生成个人filter。

## 本地巫妖网页补充（2026-10-06）

- 详见SAVED_GUIDE_ASSESSMENT.md和sources/builds/flay-mana-lich-guide.json。原HTML位于用户Downloads，字节副本在忽略的.cache/saved-flay-guide.html，SHA-256为dd7d6c8d372422681b30c21940cfe83bd12d0a59dffbb4fcda163c98e7c2e8dc。未执行脚本或请求远程资源。仓库只保存整理事实。
- 作者Volca，Season 5；结构化修改时间2026-09-26，Changelog更新日期2026-09-27，两者均记录。攻略以80级角色为前提，明确没有Starter Planner。保存时Endgame为active、Aspirational与Stat Priority未选，不能宣称已经拿到这两种变体的完整数据，也不按URL #2猜阶段。
- 成型门槛600+总魔力，核心暗金420/372/342；不要转成单件装备600魔力条件。原JSON巫妖10种暗金之外，补收415手套升级、353项链替代及348/294/125/366戒指替代，共16种候选。443是攻略不推荐的鞋，258是需改技能转换的条件选项，不因提及而加入默认清单。
- 876提供点燃触发Exult in Misery，1069腐化神像提供虚弱；没有1069时，用类型28神像的891替代另一条词缀，不能与876混成任意命中。843+854仍是主要魔力组合；886不是正文确认不可替代的条件。1067腐化神像可补暴击避免。祭坛除41:3外，正文还推荐41:4护甲方案，目标腐化1105需要装备腐化神像来成长。
- Exulis优先1084、避免1083；有狂热时1087是次选。正文确认预腐化、两条属性转换加随机传奇属性，坏传奇属性仍有用。换415后攻略计算暴击率94.6%，推荐1075补足；按玩家实际配装重算。
- 必须保留两处源矛盾：页面标题/正文/所示技能为Flay，但嵌入data-le-profile和Planner链接为死灵2ai4s0qh#1；FAQ多写two Traitor's Tongue，开头与配装是斧主手＋一把匕首副手。不要据嵌入链接替换已有巫妖JSON，也不创造双匕首需求。Loot Filter按钮没有可用XML内容，不能当作已取得Maxroll过滤器。
- 先前“缺门槛/替代/876用途”对巫妖已解决；仍缺死灵正文、每部位拾取最低阶数、LP/WW及玩家进度/库存偏好。本轮只完成保存网页的充分性核对，不跳到动态工具实现。

## Maxroll Strict参考（2026-10-06）

- 用户提供两份Strict XML，字节固定于sources/builds/maxroll-skeleton-necromancer-strict.xml和maxroll-flay-mana-lich-strict.xml。来源、附件、哈希和边界在maxroll-strict-manifest.json。死灵141条（118启用/23关闭），巫妖130条（107/23）；没有生成合并成品。
- 阅读MAXROLL_STRICT_ASSESSMENT.md和MAXROLL_RULE_INDEX.md；完整条件、重复Uniques、nil和提示在analysis/maxroll-strict.json。复现python -X utf8 scripts/analyze_maxroll_filters.py。这里X编号是XML物理位置，两文件没有Order，不能拿Raxx编号套用；社区导入反向只作辅助证据，实机次序待核对。
- 两份Planner名单均11种，完整覆盖原JSON暗金。巫妖额外415；死灵额外300（遗物Ambitions of an Erased Acolyte）及477（戒指Unsated Rage），后两者没有机制说明，标为生成器候选。核心名单兜底本身没有LP/WW限制；1/2/3LP与WW1/15/19是其他分层规则，不是所有核心的统一门槛。
- 分部位T6/T7均数量1、advanced=true、单条阶数>=6/7、合计ANY、OnlyUncorrupted，通常底材不限。素材类型与暗金底材分开。巫妖10个类型，死灵9个；神像和祭坛另有规则。死灵5条Rare Strict有底材、数量2、合计T>=4，但没有RarityCondition，不能当作只适用稀有度RARE。
- 巫妖正文的5种替代暗金未进入专属名单，通用路径不一：353/125/366有无LP路径，348普通潜能路径从LP2起，294只有LP3/4；低LP过渡戒指应明确保护。876+891的备用神像没有独立用途提示，但891在通用Weaver池，不能说一定被隐藏。41:4祭坛正文选项也要补到BD分支。
- 神像Strict规则是混合池数量2，并非严格前后缀配对；一条目标词缀与宽泛66词缀Weaver规则都启用。普通/腐化计数待客户端验证。分部位OnlyUncorrupted规则混入1084/951/1009/1022等腐化属性，不证明腐化成品可通过；不要当成普通可制作词缀。
- Wanted Affix & Tier 7同时有两份AffixCondition：一份目标池advanced=false，一份全池T>=7；FP>=1、未腐化。同一条词缀可参与两者；目标不必T7。高制作潜能规则有FP>=52及AffixCountCondition NotSealed，此条件类型未出现在Raxx原文，不能忽略。
- Strict关闭项全部按功能规则研究，不按Raxx56蓝字删除策略处理。巫妖Shatter/Edit池仅36；魔力34、暴击避免97碎片需结合库存另配。普通生命碎片0–60、T3+生命0–80；等级含上限。CoF升华规则关闭且类型未选，开启前先配置。
- 全文件各涉及1156词缀、482暗金ID；Raxx未涉及的44词缀/41暗金从原有完整1.5.0缓存补齐在maxroll-reference-supplement.json，不改冻结基底参考。名字与旧数据库标志不能证明当前掉落状态。Maxroll保存脚本将lastModifiedInVersion默认设1.0.0.4，不据此判定旧赛季。
- 用户已明确Strict由攻略导出。生成版采用其BD条件门槛，通用收集保留Raxx，另有逐项记录的JSON／正文／腐化补充。两个Strict直接271条加基底107条会是378条；已通过映射与替换生成187条，方法见TRANSFER_RULES。

## 已确认的固定事实

1. 当前上游文件固定于57498b0901a7c099efdf931923c65271fdfdb993，文件名仍为v1.0，提交标题写v1.1。SHA-256：146465750ab794175676f73b7251ddba610c42c4508bb16b614b6d4982036288。
2. 内部名称Universal Filter，description=1.5 Circle of Fortune，lastModifiedInVersion=1.4.7，lootFilterVersion=9。不要据最后修改字段断言它不适用于S5；导入兼容性仍待客户端验证。
3. 163条，104启用、59关闭；56条是蓝色说明。真正关闭的功能条目是29、69、70。
4. Order为0–162；优先级取Order升序，编号Order+1；XML元素的物理顺序完全相反。rules.json同时保留number、xml_position、source_lines。
5. 15种条件全部解析，不能丢弃新材料条件、潜能条件或第二个AffixCondition。递归转换保留重复Uniques对象与nil/空字符串区别。
6. 当前与视频发布前的差异在15、20、29、61、82、83、91条。上游摘要并不完整；要查看version-diff.json。
7. 英文自动字幕已完整阅读，15:45画面抽查；没有完整听音/逐帧检查。字幕术语容易错，具体筛选以XML为准。
8. ID解释资料来自Last Epoch Tools version150及其游戏本地化，冻结摘录在game-reference.json。1112词缀、448暗金/套装、149底材组合。旧暗金46/69/248仅有本地化名称，不断言当前可掉落。

## 未来定制必须先解决的点

下面R编号指未改动的原始Raxx；新基底的四类变更以本文开头为准。旧双BD成品处理仅是历史，当前通用模板仍需填入具体BD。

- 29：关闭且req=None，选择“不会收集的职业”之后才考虑启用。主玩和备刷BD的职业都属于保留范围。无职业限制装备不能靠它按BD筛选。
- 37/38/39/81/82/136/137：类型列表为空。37的空类型是广泛收集T8的意图；其余条目不能仅按名字当成武器、副手或指定底材。
- 83及99–126：词缀列表为空但启用。1.4官方已明确空词缀匹配任意；空列表不是禁用信号，计数边界待游戏核对。
- 81/82/83在碎片、神像、开荒区之前。82按空类型广泛匹配的解释会覆盖普通至崇高装备的下层规则；需要先决定填充/关闭，才有意义讨论终局严格度。
- 47已限制RELIC:3/4/5，不能原样当成通用遗物／所有职业的制作素材规则。
- 13/14各412个指定物品，清单相同；12无名字白名单；15的143项不要求LP=0；16选21项。新增物品只进入此次提交的15，不自动进入13/14。
- Unique roll非空边界集中在15，364个0–255区间。不得把它们当面板实数门槛，也不得无理由删字段。
- 38–47数量1且T≥7；不是全部BIS词缀齐全。48要求至少2个所选T≥6，合计比较ANY，保存的14不是限制。
- 62两份词缀列表有重叠，第二份10项全部在第一份491项中。可由同一条T7满足两份条件；无未封印词缀或两条不同词缀的显式保证。
- 68要求EXALTED物品加实验词缀，并不单独要求实验词缀阶数T6/T7。
- 135存了T3阈值却advanced=false；别在翻译或生成时把保存值悄悄激活。
- 等级条件是角色等级，包含上限；85退出对应max84，60退出对应max59。复用到低等级角色可能重新适用，不会自动切换isEnabled。
- 颜色、声音、光柱、地图图标分别定义。声音1映射None，6映射Begin；recolor=false保留原色。不要把声音1写成Default或把未启用光柱当作已生效。
- 同一物品只取最先匹配的提示。多个BD的收集可做逻辑并集，但多个BD的底材/词缀配对、神像前后缀组合不能直接混池；收集等优先级与显示顺序需要分开确认。
- 1.4规则上限为200，原文占163。后续成品删除56条蓝色说明后，仅做这项删除会剩107条功能规则（104启用、3关闭），相对200条上限有93条空间；实际数量随BD拆分和取舍改变。保持功能规则相对次序并重排Order，不能顺手删除29/69/70等关闭的功能规则。将来实际扩充要重新检查客户端限制，不提前实现拆分或压缩工具。

## 证据边界

官方1.4补丁确认200条、空词缀与新资源条件。官方支持页仍写75条，是版本资料冲突，不采用其旧上限。

S5补丁里的T6/T7数量、sealed与affix分组更新位于Bazaar段落；不要当作本XML条件的引擎保证。社区filters.js的部分match实现简化甚至直接返回true；只能用于格式/名字辅助，不能拿它的结果当游戏实测。

游戏客户端导入、空类型范围、空词缀计数、sealed计数、潜能组合、声音与图标尚未实测。具体用例在BEHAVIOR_CASES.md。后续有游戏证据时，记录版本、物品字段、命中编号与实际显示，再修改结论。

## 复现与继续工作

```powershell
python -X utf8 scripts/analyze_filter.py
git status --short --branch
git log -1 --format='%h %s'
git remote -v
```

脚本只读固定资料，标准库、无需网络；生成rules.json、version-diff.json、validation.json及三份索引文档。修改自动生成文档要先改脚本或输入资料，再运行；手写说明在其余docs文件。

更新上游时先检查新提交与文件哈希，再逐项比较条件；不能直接覆盖基底后沿用旧结论。重新获取参考ID时记录其游戏版本与来源哈希，当前摘录不覆盖完整游戏数据库。

Windows命令使用PowerShell；Python加-X utf8以避免本机默认cp932导致输出失败。这里不依赖PowerPoint、游戏安装目录或其他项目机器配置。

远程使用SSH别名github.com-personal；已用Git自带OpenSSH确认认证身份是BCSZSZ。GitHub CLI默认活跃身份当时是另一个账号，因此创建仓库时仅在该进程选择BCSZSZ凭据，不改变全局账号设置。SSH私钥、令牌和完整字幕均不加入仓库。

任务完成后的最终仓库URL和提交以实际git remote、HEAD及远程核对为准，不在此预写未验证结果。
