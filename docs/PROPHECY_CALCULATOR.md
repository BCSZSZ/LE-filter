# 普通崇高预言概率工具

[在线工具](https://bcszsz.github.io/LE-filter/probability/)与[Excel](../outputs/01a135a3-5a09-7e91-83c5-4bd333aeb5ea/普通崇高预言-T7概率.xlsx)对比无镜片、Lens of Quality、Lens of Origin、Lens of Finality下，单件装备**恰好**1T7和2T7的概率。Excel采用区域100、命运12、腐化0，含23类装备的36个底材职业组合。网页布局依次为设置与概率、腐化曲线、镜片升阶规律、基础T级生成规律。

## 入口与数据边界

游戏版本1.5.2.2，Steam build25816319。数据取自本机实际Unity资源和GameAssembly原生分支，未修改或启动游戏；这些是概率模型计算，不是客户端采样。源文件hash、RVA及调用链分别在[镜片调查](T7_LENS_DATAMINING.md)、[区域／腐化调查](T7_PROPHECY_CORRUPTION.md)和[装备池调查](T7_EQUIPMENT_POOLS.md)。原始游戏二进制和完整资源不上传仓库。

- 普通崇高预言为GenericEquipment、RarityGroup.Exalted、forceExalted=true，不含祭坛、神像、冠军、实验、保证T7或预腐化奖励。23类为真实可掉落普通装备；拳套和弩在本版禁用。
- 入口硬编码奖励ilvl100，区域和巨石腐化不影响此单件概率；腐化图为水平线。区域输入默认100，保留设置但不伪造概率变化。
- 职业指**生成装备底材所属职业**。头盔、胸甲各五池；遗物通用加五职业；弓仅游侠；其他19类通用。普通预言并不保证只掉玩家本职业，这里没有伪造“玩家职业所有预言结果”的混合比例。
- 命运0–3未解锁普通崇高预言；4–8使用M1.5、Q1，9–12使用M1.5、Q2。Origin／Finality解锁4、Quality解锁9。命运11的25%不会再作用于已forceExalted的预言；12增加数量，不改单件概率。

## 模型

[冻结池](../sources/t7-equipment-pools.json)保留每条词缀ID、实际部位权重、前后缀、T6Compatibility、Maximum门槛及可自然升T6判定。初始词缀数1／2／3／4的概率为0.005／0.00995／0.39402／0.59103；按权重无放回生成，每侧最多两条。

`r=clamp(1−weight,0,1)`；自然T5→T6为`a=M(.045+.051r)`，T6→T7为`b=MQ(.066+.054r)`。自然阶数概率对r最高二次。1／2词缀的魔法起点额外以95%阻止自然崇高，即a乘.05；T6不兼容词缀保留低阶生成但不自然升T6。

先生成自然阶数，再以20%触发一条镜片候选，最后执行保证崇高。镜片按原阶数权重选一条，并以2/9、1/3、4/9升1／2／3阶，封顶T7；前／后缀镜片只选对应未封印词缀。

保证崇高阶段以`.3^m`继续抽签，m为镜片之后已有T6／T7数。从全部N槽等概率初抽，初抽已有崇高就停止。初抽低阶不兼容时按原始生成顺序寻找第一条Normal替补；不存在则保留初抽项。替补可能已有T7，仍会被重写T6／T7。必须保留原始顺序及Normal／allowed Maximum／blocked三类身份，不能沿用仅适合全兼容戒指的无序压缩。

[计算器](../scripts/build_prophecy_probability.py)先求有序身份联合矩`E[∏r_i^d_i]`，每轴d=0..3，再枚举全部7^N阶数及镜片状态。保证崇高的输出分布可写成`H0+ΣHi*b_i`，因此最高仅某一轴再加一次，三次矩足够精确积分所有身份相关性。[结果JSON](../analysis/prophecy-probabilities.json)含0–4条T7的完整分布；网页取索引1与2，未把“至少两条”混称2T7。

以理想独立RNG、名义设计小数计算；不宣称精确重放float32 PRNG序列或验证线上服务器热更新。每个结果都对同一指定底材职业池条件化。

## 复现与检查

开发计算依赖NumPy2.3.5：

```powershell
python -X utf8 scripts/build_prophecy_probability.py
python -X utf8 scripts/validate_prophecy_probability.py
python -X utf8 -m unittest discover -s tool -v
python -X utf8 scripts/build_pages.py
```

前两步在包含NumPy的开发环境运行；已提交结果供发布流程直接使用，GitHub Actions及浏览器不需要NumPy。`freeze_prophecy_pools.py`只用于从本机复读调查缓存建立新冻结池，常规重建不运行它。

Excel由[build_prophecy_workbook.mjs](../scripts/build_prophecy_workbook.mjs)使用`@oai/artifact-tool`生成，先将脚本放进可解析该包的运行目录，再从仓库根目录运行。导出的288个概率单元格均为数值，带百分比格式，非文本。发布脚本把相同Excel、结果JSON、HTML、CSS和JS复制到`.site/probability/`；保留原工作台根目录。

[独立验证](../analysis/prophecy-model-validation.json)：四个4–6词缀小池、639条有序身份路径、1,765,050个身份／阶数状态、两倍率和四镜片共128组完整分布，最大误差1.33×10⁻14。另与上一轮戒指模型交叉核对，逐格核对Excel与JSON；浏览器检查职业切换、未解锁镜片、区域／腐化不改数值及响应式排版。发布检查在[prophecy-page-validation.json](../analysis/prophecy-page-validation.json)。
