# 周期序列与异或相关分析

## R — Reading

B：3章pp.88–89移位寄存器，7章循环作用；14章Hadamard和导数。D：按明确群作用的有限相关求和。

## I — Interpretation

周期相关用索引x+τ modN，布尔加法相关用x XOR u。前者是Z_N，后者需要N为2的幂且表示F₂ⁿ。给定迹序列可分析，但不能把两种移位公式互换。

## A1 — Application Example

合成反例：[0,0,0,0,0,0,1,1]在循环和xor移位下相关向量不同。相同输入可用于测试群作用是否被混淆。

## A2 — Future Trigger

sequence correlation、迹序列、低相关序列族、periodic autocorrelation、XOR相关。函数导数读advanced-invariants。

## E — Execution

research_extensions.py sequence输入sequence、可选other、必需shift_group=cyclic或xor。返回全部相关值、非零移位最大幅和计数约定。需要族相关时逐对分析并保留最坏对；当前工具不自动搜索全部序列族。

## B — Boundary

N≤4096，精确计算有预算；xor要求2幂长度。不能把一个序列自相关好推广成族的互相关好。

## 配套资源

路径相对于本文件；脚本需先检查运行条件，不因附带而自动执行。

- [resources/research_extensions.py](../../resources/research_extensions.py)
- [resources/test_research_extensions.py](../../resources/test_research_extensions.py)
- [resources/usage.md](../../resources/usage.md)
- [resources/research_map.md](../../resources/research_map.md)
- [resources/proof_ledger.md](../../resources/proof_ledger.md)
- [resources/examples.json](../../resources/examples.json)
