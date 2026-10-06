# LE-filter 工作约束

- 先读 README.md 和 docs/WORKING_MEMO.md；当前原始基底及视频发布前版本在sources中，保持字节不变。
- 研究结论分清XML事实、官方机制、社区格式解释和客户端实测。未经实测不要写成实测通过。
- 规则优先级按Order升序；原始XML物理顺序相反。条件和重复对象不得无声丢弃。
- 后续主玩BD与一起收集的BD具有同等收集优先级；用户未提供BD前不要推断或生成专属filter。
- 用户最新显示约定：主套路粉色8，副套路蓝色12，共享需求按主套路提示，不另设薄荷绿身份。当前默认Flay主、Skeleton副；记录为默认对应，不称为用户已明确指定。来源owners独立于显示身份；通用Raxx样式保留。
- 保持简单、只实现已请求的阶段；原文未配置的空选择和实际默认状态必须显式审查。
- 原filter是待玩家配置的模板。玩家待办见docs/PLAYER_TODO.md；未来可复制成品完成配置后删除56条蓝色说明，说明留在文档。保持功能规则相对次序并重排Order，不把关闭的功能规则一律当作说明删除。
- 自动生成索引用python -X utf8 scripts/analyze_filter.py重建。修改脚本后检查结构验证、输出确定性和文档链接。
- 当前基底是templates/LE-base-v1.xml，来自不变的Raxx原文；规则说明见docs/BASE_TEMPLATE.md，原R／当前B映射见templates/base-manifest.json。当前成品是filters/Flay-Mana-Lich+Skeleton-Necromancer-v2.xml，使用说明与逐条审阅见docs/CURRENT_FILTER_GUIDE.md和CURRENT_RULES_REVIEW.md。用户已明确要求按此基底生成最新版两BD。
- 四类按C1→C2→C3→C4匹配：对应类型BD目标T7；任意双／多T7全量；BD目标不限阶数＋全池T7；一条全量单T7阶段兜底默认开启，由玩家手动关闭，无自动等级退出。C2／C3的T7计数与C4用全部1156冻结ID、原23类装备；不按BD目标缩窄C2／C4。原R60／61合并，阶段规则置于原R62之后。双T6常驻改为双／多T7，原R63／64仍0–84级。
- Maxroll Strict只提供定制变量情报；C1／C3共用按BD／类型绑定的部位目标，C3目标不限阶数，不加FP、未封印计数或未腐化收集门槛。保留不保证可制作。通用模板目标仍为Raxx示例；两BD已填入v2成品。候选来源为docs/RAXX_VARIABLES.md与docs/STRICT_VARIABLE_REVIEW.md。
- 神像最新审阅：按specialAffixType=6分离腐化参考，普通目标计数不含腐化ID，且不限制物品是否已腐化。Flay用户指定843／854与876／886各1项候选、2项组合毕业两层，两层均保留Weaver／Lagon底材，毕业层优先、声音不同；这是明确用户定制，允许有别于原Raxx默认单层。候选只有886不保证点燃，876必须条件与891攻略备用不得静默加入。详见docs/FLAY_IDOL_REVIEW.md。
- Strict的腐化目标ID自动提取，类别通过冻结词库查询，普通／腐化分离不得依赖Guide或人工指定ID名单。备用关系可留作后续补充。独立自动分类见docs/STRICT_IDOL_CLASSIFICATION.md；未知ID报错，不猜普通。
- 当前复现依次运行scripts/build_base_template.py、scripts/verify_base_template.py、scripts/extract_raxx_variables.py；未被上述用户确认改变的原门槛、层级、进度及开关保持。Strict的LP分层、FP52、常驻T6／单词缀神像等不得直接移植；来源通用大池不能误当BD目标。未决信息显式保留。旧187条XML、COMBINED_FILTER_GUIDE和TRANSFER_RULES为历史试制，不能自动作为本轮最终方案；不运行旧生成流程覆盖它。
- 最新成品在提取后依次运行scripts/generate_current_filter.py、scripts/verify_current_filter.py、scripts/render_current_filter.py。旧generate_filter、verify_generated_filter和render_rules_review只复用纯帮助函数，不执行其主程序，不覆盖历史187条输出。当前138条；阶段C4是G57（原R60／基底B61），需按真实生成结果更新编号。
- v2仅使用Strict20种目标暗金，追加原R15形成152项，不重新加入旧5种正文替代品。普通实验目标已填但沿用关闭；升华、紧缺库存入口及未提供的开荒优选底材关闭，五类定向底材启用且保留Raxx宽门槛，侍祭碎片沿用，其他职业碎片关闭。骷髅神像按源BIS底材与至少2个普通目标，不自动导入常驻1项层或精确Planner组合；跨职业Large Omen来源保留，未猜更窄配对。实际待办与默认选择须同步CURRENT_FILTER_GUIDE与memo。
- 历史187条XML、transfer-report和GENERATED_RULE_INDEX原由scripts/generate_filter.py重建；其verify_generated_filter与render_rules_review也仅对应历史流程。当前使用上面的current流程，不手改生成输出、不静默截断超过200条的规则；封印等未知语义保留未确认。
- 当前逐条中文审阅稿与名单附录由scripts/render_current_filter.py从实际XML和冻结名字库重建，标题须对应真实条件；同步CURRENT_FILTER_GUIDE与memo，历史COMBINED_FILTER_GUIDE不冒充当前设计。
