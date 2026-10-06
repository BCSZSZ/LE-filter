# LE-filter 工作约束

- 先读 README.md 和 docs/WORKING_MEMO.md；当前原始基底及视频发布前版本在sources中，保持字节不变。
- 研究结论分清XML事实、官方机制、社区格式解释和客户端实测。未经实测不要写成实测通过。
- 规则优先级按Order升序；原始XML物理顺序相反。条件和重复对象不得无声丢弃。
- 后续主玩BD与一起收集的BD具有同等收集优先级；用户未提供BD前不要推断或生成专属filter。
- 用户最新显示约定：主套路粉色8，副套路蓝色12，共享需求按主套路提示，不另设薄荷绿身份。当前默认Flay主、Skeleton副；记录为默认对应，不称为用户已明确指定。来源owners独立于显示身份；通用Raxx样式保留。
- 保持简单、只实现已请求的阶段；原文未配置的空选择和实际默认状态必须显式审查。
- 原filter是待玩家配置的模板。玩家待办见docs/PLAYER_TODO.md；未来可复制成品完成配置后删除56条蓝色说明，说明留在文档。保持功能规则相对次序并重排Order，不把关闭的功能规则一律当作说明删除。
- 自动生成索引用python -X utf8 scripts/analyze_filter.py重建。修改脚本后检查结构验证、输出确定性和文档链接。
- 当前基底是templates/LE-base-v1.xml，来自不变的Raxx原文；规则说明见docs/BASE_TEMPLATE.md，原R／当前B映射与策略见templates/base-manifest.json。用户已要求把四类T7收集落实为后续使用的新模板，尚未要求生成两个BD最终filter。
- 四类按C1→C2→C3→C4匹配：对应类型BD目标T7；任意双／多T7全量；BD目标不限阶数＋全池T7；一条全量单T7阶段兜底默认开启，由玩家手动关闭，无自动等级退出。C2／C3的T7计数与C4用全部1156冻结ID、原23类装备；不按BD目标缩窄C2／C4。原R60／61合并，阶段规则置于原R62之后。双T6常驻改为双／多T7，原R63／64仍0–84级。
- Maxroll Strict只提供定制变量情报；C1／C3共用按BD／类型绑定的部位目标，C3目标不限阶数，不加FP、未封印计数或未腐化收集门槛。保留不保证可制作。模板目标仍为Raxx示例，不冒充已填两BD。当前入口为docs/RAXX_VARIABLES.md与docs/STRICT_VARIABLE_REVIEW.md。
- 神像最新审阅：按specialAffixType=6分离腐化参考，普通目标计数不含腐化ID，且不限制物品是否已腐化。Flay用户指定843／854与876／886各1项候选、2项组合毕业两层，两层均保留Weaver／Lagon底材，毕业层优先、声音不同；这是明确用户定制，允许有别于原Raxx默认单层。候选只有886不保证点燃，876必须条件与891攻略备用不得静默加入。详见docs/FLAY_IDOL_REVIEW.md。
- Strict的腐化目标ID自动提取，类别通过冻结词库查询，普通／腐化分离不得依赖Guide或人工指定ID名单。备用关系可留作后续补充。独立自动分类见docs/STRICT_IDOL_CLASSIFICATION.md；未知ID报错，不猜普通。
- 当前复现依次运行scripts/build_base_template.py、scripts/verify_base_template.py、scripts/extract_raxx_variables.py；未被上述用户确认改变的原门槛、层级、进度及开关保持。Strict的LP分层、FP52、常驻T6／单词缀神像等不得直接移植；来源通用大池不能误当BD目标。未决信息显式保留。旧187条XML、COMBINED_FILTER_GUIDE和TRANSFER_RULES为历史试制，不能自动作为本轮最终方案；不运行旧生成流程覆盖它。
- 成品XML、transfer-report和GENERATED_RULE_INDEX由scripts/generate_filter.py重建，不仅手改输出。修改生成器后运行scripts/verify_generated_filter.py；超200条或转移不等价不能静默降级。封印等未知语义返回未确认，不充当游戏实测。
- 逐条中文审阅稿与名单附录由scripts/render_rules_review.py从实际成品和冻结名字库重建，标题须对应真实条件，不能只复述含糊规则名。同步COMBINED_FILTER_GUIDE与本memo中的现行显示约定。
