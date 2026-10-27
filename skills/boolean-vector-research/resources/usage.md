# 科研工具使用合同（0.2.2）

本入口用16张能力卡组织函数设计与应用。脚本是Python3.10+标准库程序；仓颉仅用于作者端编译，使用本Skill不要求安装仓颉、Sage或NumPy。运行前查看相应 `--help`。

## 对话调用

安装后在新对话使用 `$boolean-vector-research`，例如：

- “分析这个4→2函数的全部分量、差分、二次型秩；给最弱分量和最坏差分的证据。”
- “构造6变量MM bent，给置换参数、证明和全谱核验。”
- “在GF(8)中搜索指数1、3、5，筛选APN置换；不要把候选当新族。”
- “把此函数生成的码列出秩和重量分布，检查能否用码距离推断非线性度。”
- “检查此设计/OA；失败时给具体违反计数的子集。”

Agent先定位安装目录中的resources脚本，再把输入和结果写入当前工作目录。不要把下述相对命令理解成必须切到安装目录；也可对脚本使用绝对路径。

## 真值表合同

```json
{"n":2,"m":1,"table":[0,0,0,1]}
```

n为输入位数，m为输出位数，N=2^n。当前分析器支持1≤m≤n；table[x]是F(x)，低位是x₀、输出低位是F₀。布尔函数的m=1。必须是JSON整数，拒绝true/false、浮点、长度错误和越界值。

ANF以单项式掩码记录：0表示常数1，3表示x₀x₁；空列表是零函数，次数约定−1。非零常数次数0。谱未归一化，都是精确整数；DDT取有序x计数。所有非零输出掩码b都计算；不止m个坐标。

```powershell
python resources/research_core.py analyze --input spec.json --out result.json
python resources/research_core.py analyze --input spec.json --advanced --include-ddt --out detailed.json
```

主要输出：components[mask−1]的ANF、次数、Walsh、NL、最近仿射函数、陪集重量、AC、自相关指标、CI/韧性、线性结构、适用时的极化秩及根空间；顶层的最弱分量、DDT最坏见证、输出分布、置换/平衡/向量bent、二次导数秩、生成码秩及枚举状态。

`--advanced`另外请求每个分量的精确AI（n≤6）与精确二阶非线性度（n≤4），分别给湮灭子和最近RM(2,n)函数。超门限字段为not_computed，不能用0代替未计算。CI采用低重量非零频率判据，常函数CI=n；resiliency_order仅平衡时有值。不把这些极端约定与没有检查条件的界混用。

默认n≤8；可显式 `--max-n` 放宽，最高12，但还有默认25,000,000工作量预算、1,000,000全谱条目硬限。可调 `--max-work`，仍不绕过维数/谱条目硬限。AI、NL2加入工作量估算；总预算不足时整个命令退出2，只有超出各自维数支持范围时返回字段not_computed。生成码只在rank≤16且N≤256时枚举，否则报告原因，满足满秩门时可给经定理推导的距离，须区分“枚举”和“理论桥梁”。

metadata中写域模型不会自动让用户提供的任意表成为该域多项式的值；实际构造必须核对。构造器和幂搜索器会验证它们使用的不可约多项式。

## 构造与演示

```powershell
python resources/research_core.py demo --case scalar-bent --advanced --out scalar.json
python resources/research_core.py demo --case vector-bent --out vector.json
python resources/research_core.py demo --case apn-cube --out apn.json
python resources/research_core.py demo --case identity --out degeneration.json
python resources/research_core.py construct --family quadratic-bent --n 6 --out quadratic.json
python resources/research_core.py construct --family mm --n 6 --params mm.json --out mm-result.json
python resources/research_core.py construct --family gold --n 3 --params gold.json --out gold-result.json
```

MM的mm.json例如 `{"pi":[0,1,2,3,4,5,7,6],"g":[0,1,0,0,0,0,0,0]}`；n=6分为u低3位/v高3位，函数u·pi(v)+g(v)，pi必须置换，g是8项位表。Gold的gold.json为 `{"k":1,"polynomial":11}`，模多项式整数11编码X³+X+1。quadratic-bent/MM要求偶n；Gold的k与n需互素，置换性仍单独核验。

## 有限幂搜索

```json
{"n":3,"polynomial":11,"exponents":[1,3,5],"filters":{"max_delta":2,"require_permutation":true}}
```

```powershell
python resources/search_monomials.py --input search.json --out search-result.json
```

仅2≤n≤6，最多64个明确指数，当前指数范围1..2^n−2。filters还可用min_nonlinearity、min_degree（向量次数），未知字段拒绝。返回所有已测候选及筛选结果，固定n、模多项式、指数列表和表即可复现；没有EA/CCZ去重、自动查新或全函数空间最优结论。

## EA证书

```json
{"n":2,"m":2,"table":[0,1,2,3],"input_rows":[1,2],"output_rows":[1,2],"affine_rows":[1,2],"input_shift":0,"output_constant":0,"target":[0,0,0,0]}
```

```powershell
python resources/research_extensions.py ea --input ea.json --out ea-result.json
```

矩阵行用位掩码，A/B可逆，L不要求可逆；验证G(x)=B F(Ax+s)+Lx+c。此例恒等函数变成零函数，说明EA不保留置换性。输入/输出行、L及平移省略时默认恒等/零，返回证书写明实际使用值。工具只验证给定变换，不搜索分类。

## 枚举器、正交阵、设计、序列

```powershell
python resources/research_extensions.py macwilliams --input weights.json --out dual.json
python resources/research_extensions.py oa --input oa.json --out oa-check.json
python resources/research_extensions.py design --input design.json --out design-check.json
python resources/research_extensions.py sequence --input sequence.json --out correlation.json
```

输入例：

- weights.json：`{"length":3,"distribution":{"0":1,"2":3}}`。二元线性枚举器变换；仅给分布时是必要条件检验，不证明码存在。长度≤512，系数精确有理数。
- oa.json：`{"rows":[[0,0],[0,1],[1,0],[1,1]],"strength":2}`。允许重复行，强度≤4、列≤64、行≤65536，另有限制投影次数的预算。
- design.json：`{"v":4,"k":2,"t":1,"blocks":[[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]]}`。检查简单设计，拒重复块，v≤64、t≤4，另有组合预算。
- sequence.json：`{"sequence":[0,0,0,0,0,0,1,1],"shift_group":"cyclic"}`。长度≤4096，xor作用要求2的幂；可选other做互相关，长度必须相同。shift_group必填。

## 复现与错误处理

脚本输入合法且计算完成时退出0；输入不合法、预算拒绝或文件错误时退出2。比较“成立/不成立”是正常数学结果，不能仅靠退出码当性质成立。使用新输出路径，失败时检查退出码，不读取先前遗留报告当本次结果。

每次报告写：输入/参数、位序/域、数学前提、精确计算/理论推断/未计算的区分、证书、失败见证、未决任务。资源test_research_core.py与test_research_extensions.py可用 `python -m unittest discover -s resources -p "test_*.py" -v` 复算。


## 0.2新增：有限域、S-box与CCZ

下列命令中的resources可替换成安装目录下resources的绝对路径；输入输出保存在工作目录。

有限域多项式/迹输入例子（多项式11为x³+x+1）：
```json
{"n":3,"polynomial":11,"terms":[{"coefficient":1,"exponent":3}]}
```
```powershell
python resources/field_functions.py polynomial --input field.json --out function.json
python resources/field_functions.py trace --input field.json --out trace.json
python resources/research_core.py analyze --input trace.json --out trace-analysis.json
```
对偶基输入为 `{"n":3,"polynomial":11,"basis":[1,2,4]}`：
```powershell
python resources/field_functions.py dual-basis --input basis.json --out dual.json
```
逐项输出Tr(b_i d_j)矩阵以及所有域元素的基坐标，验证坐标重构。n≤8；构造项≤64，指数≤2²⁰；常数项使用0^0=1，不对指数盲目模2^n−1。构造的函数表索引仍为标准多项式基。域运算默认工作预算2,000,000，可用--max-work调整。

```powershell
python resources/sbox_criteria.py analyze --input function.json --out sbox.json --include-tables
```
DLCT是整数计数偏差 `#equal−N/2=AC/2`；将其除N才是概率偏差。最大值排除u=0及输出掩码b=0。经典BCT(a,b)使用输入差a、输出差b，需要n=m且F为置换；否则返回not_applicable。SAC仅检查单位输入方向与坐标，all_component_pc检查所有非零输出分量在指定重量方向是否平衡。n≤8,m≤n，默认工作预算25,000,000。两者不属于本工具承诺的CCZ不变量。

CCZ证书输入：`{"n":2,"m":2,"table":[0,1,2,3],"graph_rows":[4,8,1,2],"graph_shift":0,"target":[0,1,2,3]}`。z=x|(F(x)<<n)，矩阵每行是位掩码，低n位为新输入。target可省略。
```powershell
python resources/graph_equivalence.py certificate --input certificate.json --out certificate-result.json
python resources/graph_equivalence.py prefilter --input pair.json --out prefilter.json
```
pair为 `{"n":2,"m":1,"left":[0,0,0,1],"right":[0,0,0,0]}`。矩阵必须可逆；新输入投影碰撞则not_function_graph并给见证。给定target后必须查看matches_target；证书有效不代表自动匹配所给target。预筛不同即否定CCZ；相同只报告inconclusive。不搜索未知变换，不提供规范形。

## 0.2新增：一次生成完整实验

在工作目录保存project.json：
```json
{"construction":{"kind":"gold","params":{"n":3,"k":1,"polynomial":11}},"advanced":true,"sbox":true}
```
```powershell
python resources/research_workflow.py --input project.json --out-dir experiment-001
```
目录必须不存在。支持kind=table、polynomial、trace、gold、mm、quadratic-bent。table的params为n,m,table；polynomial/trace与上方域构造合同一致；其他家族见既有构造章节。可选advanced、sbox、include_sbox_tables必须是JSON布尔值，max_work与field_max_work控制各阶段预算。

结果含参数、完整函数表、核心指标、可选S-box指标、摘要和manifest.json。先确认manifest.status=complete，再按manifest.files的SHA256核对每个文件；manifest最后写入，IO故障可能留下不完整目录。此流程在n≤8运行，advanced字段超过AI/NL2支持维数时仍会标not_computed。结果只证明当前有限对象，不能宣称全族、新颖性或系统安全。

PowerShell核验单个文件：`(Get-FileHash .\experiment-001\function.json -Algorithm SHA256).Hash`，与manifest中的function.json值比较（忽略大小写）。如需重跑，用新的目录名，保留此前证据。


## 0.2.1：运行日志与实验审计

本版本保持16张卡，增加第8个标准库运行程序experiment_audit.py。research_workflow.py成功实验新增：

- execution.jsonl：实际验证、构造、核心计算、可选S-box计算和文件写入阶段的顺序、UTC时间、耗时和状态。最后事件是manifest准备写入；真正完成仍以随后写出的manifest.status为准。
- environment.json：Python版本、实现、平台、UTC时间和8个运行程序的SHA256。核心数学计算器仍标自身0.2.0，工作流为0.2.1，版本按实际模块区分。
- 两个新增文件同样进入manifest.files哈希清单。计算或输入失败时不会创建实验目录；如需保存失败命令日志，可在PowerShell使用下方Tee-Object命令。本轮优化自身的成功/失败、命令输出、测试和安装记录另保存到发布日志。

### 先检查完整性，再选择重算

```powershell
python resources/experiment_audit.py --directory experiment-001 --out audit-001.json
python resources/experiment_audit.py --directory experiment-001 --recompute --out replay-001.json
```

--out可省略，结果打印到终端。若指定，必须是实验目录外尚不存在的新文件；审计器不修改归档，不覆盖已有报告。支持0.2.0旧实验与0.2.1新实验。0.2.0没有阶段日志和环境指纹，兼容读取不代表补造这些历史信息。

状态：hash_consistent仅表示当前文件与无签名清单一致，不能证明数字真实或文件来自可信作者。recomputed_match表示使用当前程序按原参数重新生成函数及数学结果并逐项匹配。hash_mismatch表示文件哈希变化；content_mismatch表示跨文件输入/结果或重算不一致。输入损坏、文件缺失、路径逃逸、非法清单等以退出码2拒绝；已检测的哈希/内容不一致退出码1；通过退出码0。

重算不是独立算法证明，它重用已测试的计算程序。--recompute默认max-work为25,000,000，不允许存档参数静默提高该预算；需要时显式--max-work。程序只接受安全文件名，不读取清单中的目录路径，最多32项、单文件64MiB、总计128MiB。runtime_fingerprints_match单独报告当前程序与记录是否一致；程序版本变化不自动等于数学结果错误。

### 自己保留命令输出日志

```powershell
python resources/research_workflow.py --input project.json --out-dir experiment-002 2>&1 | Tee-Object -FilePath command-002.log
$LASTEXITCODE
```

成功实验阶段日志和命令失败日志是不同记录。先确认command-002.log不存在，避免人工命令覆盖旧记录。通过Codex可直接请求：“运行完整实验并保存阶段日志、命令输出，再用experiment_audit重算，区分哈希一致和重算一致。”

### 本轮优化日志

工作目录output/logs/boolean-vector-research-0.2.1下保存events.jsonl与每个实际命令的原始输出，中文优化日志.md说明变更、测试和边界。日志中的UTC+08时间和实验内UTC时间都带时区。发布包附打包开始前的日志快照；打包结束、包SHA256和最终安装记录在本地完整日志中，避免把ZIP自己的哈希循环写入自身。


## 0.2.2：日志协议检查与差异定位

本次保持16卡、8个运行程序，补强experiment_audit.py，不增加新的数学定理或分类能力。

- 审计在哈希通过后进一步核对execution.jsonl：序号必须为整数并连续，elapsed_seconds必须为有限、非负且不倒退的数（最大1e12秒），时间必须显式为UTC；阶段必须符合实际是否启用S-box的流程。墙上时钟可能调整，故不以绝对时间先后替代单调耗时检查。
- environment.json检查必要字段、UTC时间、与manifest一致的工作流版本、运行文件名和SHA256格式。程序指纹是否匹配仍单独报告，不能把版本变化直接判成数学错误。
- 审计读取JSON时拒绝重复键、NaN/Infinity及指数溢出为无穷的浮点数；输入与重算结果严格区分整数、浮点和布尔类型。
- 重算差异增加witness.pointer，定位首个不同字段，例如/ nonlinearity（实际值无空格：/nonlinearity）或/components/0/walsh/3。路径中的~和/分别转义为~0和~1；expected/actual是限长JSON预览，reason区分类型、数值、缺键和长度差异。

命令保持兼容：
```powershell
python resources/experiment_audit.py --directory experiment-001 --recompute --out replay-new.json
```

日志语义矛盾或重算不一致：退出码1、content_mismatch及文件/字段见证。JSON损坏、环境格式错误、非法时间等输入合同错误：退出码2。哈希不匹配先报告hash_mismatch，不继续重算。支持0.2.0/0.2.1/0.2.2实验；旧实验原本没有的日志不补造。

以上只能检查记录的内部一致性，不能证明记录者诚实或提供签名认证。重算仍使用同一套已经测试的数学程序。本轮日志位于output/logs/boolean-vector-research-0.2.2，历史0.2.1日志和安装包保留。6页0.2.1基础PDF教程继续适用，本说明补充0.2.2的更严格审计行为。
