# 带证明的bent构造

## R — Reading

B：14章 pp.426–430，定理6、10、12。D：可逆置换推广的字符求和证明。p.430习题20的印刷式隔离。

## I — Interpretation

偶维n=2k。标准二次和Σx₂ᵢx₂ᵢ₊₁为bent。h(u,v)=u·π(v)+g(v)，π为k位置换、g任意，对u求和仅留下v=π⁻¹(a)，所以所有Walsh幅2^k；这是真正需要检查的置换条件。

## A1 — Application Example

B例：x₀x₁+x₂x₃。D合成反例：p.430印刷式φ(u)·v+g(v)，k=3,φ交换0/1,g支撑{1}时最大幅16而非8；不直接调用错误推广。

## A2 — Future Trigger

construct bent、MM/Maiorana–McFarland、二次bent、bent对偶、直接和。APN/置换研究读trace-power-search。

## E — Execution

用research_core.py construct的quadratic-bent或mm家族；先查看help，提供明确pi/g与位序。证明求和坍缩，再在预算内全谱核验。输出n,m,table、构造参数、次数、非线性度和证明。直接和由谱乘积证明；需要对偶时由W/2^(n/2)的符号恢复并二次核验。

## B — Boundary

标量bent不平衡；n=2时bent次数上界的例外不能忘。独立选择多个bent作坐标不保证向量bent。

## 配套资源

路径相对于本文件；脚本需先检查运行条件，不因附带而自动执行。

- [resources/research_core.py](../../resources/research_core.py)
- [resources/test_research_core.py](../../resources/test_research_core.py)
- [resources/usage.md](../../resources/usage.md)
- [resources/research_map.md](../../resources/research_map.md)
- [resources/proof_ledger.md](../../resources/proof_ledger.md)
- [resources/examples.json](../../resources/examples.json)
