# 表示、规格与条件检查

## R — Reading

B：13章 pp.370–375（PDF393–398），平方自由展开与RM单项式基；4章 pp.115–119，迹与对偶基。

## I — Interpretation

先固定n、m、N=2^n及位序，才讨论谱和次数。输入坐标位i对应整数第i位。ANF在F₂中运算，Walsh在整数中求和。域元素的整数编码依赖基；同构不等于列表相同。

## A1 — Application Example

合成演练：n=2,m=1,table=[0,0,0,1]是x₀x₁；ANF次数2。非法长度、bool冒充整数及越界值必须拒绝。

## A2 — Future Trigger

真值表、ANF、域表示转换、位序混淆、specification。只需谱时后续读scalar-spectrum；域表达式尚未生成真值表时先说明模型。

## E — Execution

输入JSON必须提供n,m,table，table恰为2^n个0..2^m−1整数。使用research_core.py analyze，先查看--help取得实际选项。输出保留位序、域元数据、ANF/次数及预算状态。当前工具接受真值表；任意符号式和EPUB/PDF不由脚本解析，需agent依据明示表达式构造并交叉核对。

## B — Boundary

不静默猜基、坐标顺序或补齐缺失表；输出元数据并不证明用户提供的域多项式不可约。正维数bent与平衡不能同时要求。

## 配套资源

路径相对于本文件；脚本需先检查运行条件，不因附带而自动执行。

- [resources/research_core.py](../../resources/research_core.py)
- [resources/test_research_core.py](../../resources/test_research_core.py)
- [resources/usage.md](../../resources/usage.md)
- [resources/research_map.md](../../resources/research_map.md)
- [resources/proof_ledger.md](../../resources/proof_ledger.md)
- [resources/examples.json](../../resources/examples.json)
