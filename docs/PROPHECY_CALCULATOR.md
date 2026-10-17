# 普通掉落与崇高预言概率工具

[在线工具](https://bcszsz.github.io/LE-filter/probability/)切换普通掉落与普通崇高预言。两种模式均以**所选部位／底材职业的最终崇高装备**为分母，分别显示恰好1条和2条T7；没有“全部装备”分母开关。区域固定100且不可修改，命运默认12。网页依次呈现设置与概率、腐化曲线、预言镜片升级规律、基础T级生成规律；普通模式隐藏镜片和仅适用于预言的Excel下载。

[Excel](../outputs/01a135a3-5a09-7e91-83c5-4bd333aeb5ea/普通崇高预言-T7概率.xlsx)仍是区域100、命运12、腐化0的普通崇高预言表，涵盖23类装备的36个底材职业组合，比较无镜片、Lens of Quality、Lens of Origin、Lens of Finality。本轮普通掉落功能没有改写该表。

## 入口与数据边界

游戏版本1.5.2.2，Steam build25816319。数据取自本机实际Unity资源和GameAssembly原生分支，未修改或启动游戏；这些是概率模型计算，不是客户端采样。源文件hash、RVA及调用链分别在[镜片调查](T7_LENS_DATAMINING.md)、[区域／腐化调查](T7_PROPHECY_CORRUPTION.md)和[装备池调查](T7_EQUIPMENT_POOLS.md)。原始游戏二进制和完整资源不上传仓库。

- 普通崇高预言为GenericEquipment、RarityGroup.Exalted、forceExalted=true，不含祭坛、神像、冠军、实验、保证T7或预腐化奖励。23类为真实可掉落普通装备；拳套和弩在本版禁用。
- 入口硬编码奖励ilvl100，区域和巨石腐化不影响此单件概率；腐化图为水平线。区域等级固定显示100，不提供修改。
- **装备职业**指生成底材所属职业。头盔、胸甲各五池；遗物通用加五职业；弓仅游侠；其他19类通用。**玩家职业**是普通随机掉落时的实际角色，另设选择；它会改变类型抽取时的职业亲和及raw2神像分流。预言模式禁用玩家职业选择，按选定底材池条件化。
- 命运0–3未解锁普通崇高预言；4–8使用M1.5、Q1，9–12使用M1.5、Q2。Origin／Finality解锁4、Quality解锁9。命运11的25%不会再作用于已forceExalted的预言；12增加数量，不改单件概率。

普通模式计算100级巨石的普通随机来源，初始forceExalted=false；**额外地图稀有度固定0%、无活动暗金加成**，保留腐化自身的稀有度加成。不混入额外保证稀有、冠军、实验、固定奖励等来源；它不是所有怪物掉落的来源加权结果，也不表示每次击杀的掉落数量。其初始普通／魔法／稀有分支经过自然升阶和命运保底，再只取最终崇高装备。实际UniqueList候选及原生返回路径已核查，该无预先指定类型的100级调用不会从暗金／套装失败回流普通装备，见[范围与输入调查](NATURAL_DROP_CALCULATOR_SCOPE.md)。

腐化会通过稀有度和初始词缀数量，间接改变普通模式最终崇高装备里的T7分布；基础词缀的单条阶数函数本身不读腐化。详见[自然掉落调查](T7_NATURAL_CORRUPTION.md)。放逐法师的实验词缀另有直接读取巨石腐化的阶数公式，见[特殊词缀调查](T7_SPECIAL_CORRUPTION.md)，不套入本工具的普通词缀。

## 模型

[冻结池](../sources/t7-equipment-pools.json)保留每条词缀ID、实际部位权重、前后缀、T6Compatibility、Maximum门槛及可自然升T6判定。初始词缀数1／2／3／4的概率为0.005／0.00995／0.39402／0.59103；按权重无放回生成，每侧最多两条。

`r=clamp(1−weight,0,1)`；自然T5→T6为`a=M(.045+.051r)`，T6→T7为`b=MQ(.066+.054r)`。自然阶数概率对r最高二次。1／2词缀的魔法起点额外以95%阻止自然崇高，即a乘.05；T6不兼容词缀保留低阶生成但不自然升T6。

先生成自然阶数，再以20%触发一条镜片候选，最后执行保证崇高。镜片按原阶数权重选一条，并以2/9、1/3、4/9升1／2／3阶，封顶T7；前／后缀镜片只选对应未封印词缀。

保证崇高阶段以`.3^m`继续抽签，m为镜片之后已有T6／T7数。从全部N槽等概率初抽，初抽已有崇高就停止。初抽低阶不兼容时按原始生成顺序寻找第一条Normal替补；不存在则保留初抽项。替补可能已有T7，仍会被重写T6／T7。必须保留原始顺序及Normal／allowed Maximum／blocked三类身份，不能沿用仅适合全兼容戒指的无序压缩。

[计算器](../scripts/build_prophecy_probability.py)先求有序身份联合矩`E[∏r_i^d_i]`，每轴d=0..3，再枚举全部7^N阶数及镜片状态。保证崇高的输出分布可写成`H0+ΣHi*b_i`，因此最高仅某一轴再加一次，三次矩足够精确积分所有身份相关性。[结果JSON](../analysis/prophecy-probabilities.json)含0–4条T7的完整分布；网页取索引1与2，未把“至少两条”混称2T7。

普通模式额外保存每种初始词缀数N=0..4的`P(K=k)`和`P(E)`；E表示最终至少有一条T6或T7。命运0–3用M1/Q1、4–8用M1.5/Q1、9–12用M1.5/Q2；11级起仅初始raw3/4混入25%的保证崇高分支。没有镜片。自然非崇高概率由有序词缀身份联合积分得到，不能把各槽平均概率相乘。保证崇高会保留事件E，即使Normal替补覆盖已有T7；故混合后`P(E)=1−(1−f)P(自然非崇高)`。

令腐化C，`I=.01×Power(C)`；C≤100时`Power=.6C`，否则为`.002C^1.52+1.055C−47.692955017089844`。初始普通分支下，令`c=(.00156+.0073)(1+.6ln(1+I))`、`n=floor(.36I)`、`u=frac(.36I)`：`F(t)=max(0,(t−c)/(1−c))×[(1−u)t^n+ut^(n+1)]`。在`.13/.35/.84/.93/1`取CDF差分得到raw0..4。

原生代码先抽稀有度、后抽类型；只有raw2允许神像，必须再做Bayes条件化。冻结的[42候选与五职业数据](../sources/t7-natural-type-selection.json)保留拒绝重抽权重和1000次上限尾项，按所选类型乘`P(type|raw2)/P(type|other raw)`后归一化。进一步指定底材职业的因子跨raw共用，故抵消。按此混合各N结果后，对k≥1输出`P(K=k)/P(E)`；k=0需先减去`1−P(E)`，P(E)=0则不输出条件概率。

普通模式的图在0至至少1000腐化取201个点，并包含100、300、600、1000及当前输入；更高输入自动扩展横轴。纵轴标出实际百分比范围，以便看清条件概率的细微变化。因分母也随腐化变化，恰好1T7不保证单调上升。

以理想独立RNG、名义设计小数计算；不宣称精确重放float32 PRNG序列或验证线上服务器热更新。每个结果都对同一指定底材职业池条件化。

## 复现与检查

开发计算依赖NumPy2.3.5：

```powershell
python -X utf8 scripts/build_prophecy_probability.py
python -X utf8 scripts/validate_prophecy_probability.py
python -X utf8 scripts/validate_natural_probability.py
python -X utf8 -m unittest discover -s tool -v
python -X utf8 scripts/build_pages.py
```

前三步在包含NumPy的开发环境运行；已提交结果供发布流程直接使用，GitHub Actions及浏览器不需要NumPy。`freeze_prophecy_pools.py`与`freeze_natural_type_selection.py`只用于从已审查本机调查缓存建立冻结输入，常规重建不运行。

Excel由[build_prophecy_workbook.mjs](../scripts/build_prophecy_workbook.mjs)使用`@oai/artifact-tool`生成，先将脚本放进可解析该包的运行目录，再从仓库根目录运行。导出的288个概率单元格均为数值，带百分比格式，非文本。发布脚本把相同Excel、结果JSON、HTML、CSS和JS复制到`.site/probability/`；保留原工作台根目录。

[预言独立验证](../analysis/prophecy-model-validation.json)：四个4–6词缀小池、639条有序身份路径、1,765,050个身份／阶数状态，两倍率和四镜片共128组完整分布，最大误差1.33×10⁻14。另与上一轮戒指模型交叉核对，并逐格核对原Excel与JSON。

[普通掉落独立验证](../analysis/natural-drop-model-validation.json)：直接枚举有序词缀身份、全部7^N阶数及原生force分支，包含2,647,575个身份／阶数状态；48组原始分布、96组混合条件分布、64个生产组件，最大误差4.92×10⁻13。Node检查两来源、全36池的条件分布归一、五玩家职业、命运0/4/9/11/12及0至100000腐化；实际浏览器检查切换、曲线和响应式排版。发布检查在[prophecy-page-validation.json](../analysis/prophecy-page-validation.json)。
