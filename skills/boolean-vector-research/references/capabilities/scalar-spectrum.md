# 标量谱、非线性度与RM陪集

## R — Reading

B：14章 pp.413–418，定理1、Parseval及最近一阶RM码字；13章 p.373。

## I — Interpretation

W_f(a)=Σ_x(−1)^(f(x)+a·x)。d(f,a·x+c)=(N−(−1)^cW_f(a))/2；NL=N/2−max|W|/2。陪集重量多重集为全部(N±W)/2。完整谱同时给出最坏线性逼近证书。

## A1 — Application Example

原书例题14章p.415：x₀x₁的谱是2,2,2,−2；NL1。原书p.418及15章p.442的4变量二次bent例，NL6，陪集6/10各16。

## A2 — Future Trigger

Walsh spectrum、非线性度、最近仿射函数、RM coset。高阶NL转advanced-invariants；向量输出转vector-metrics。

## E — Execution

m=1真值表运行research_core.py analyze。检查ΣW²=N²、返回的最近仿射函数直接距离等于NL、陪集计数总数2N。输出完整谱或精确谱直方图、最大幅、见证、重量、次数及平衡状态。需要自相关/韧性时读取advanced-invariants。

## B — Boundary

样本频率不能给精确NL；谱幅约定未归一化。相同谱直方图不证明仿射等价。RM有界译码不是一般最近码字求解器。

## 配套资源

路径相对于本文件；脚本需先检查运行条件，不因附带而自动执行。

- [resources/research_core.py](../../resources/research_core.py)
- [resources/test_research_core.py](../../resources/test_research_core.py)
- [resources/usage.md](../../resources/usage.md)
- [resources/research_map.md](../../resources/research_map.md)
- [resources/proof_ledger.md](../../resources/proof_ledger.md)
- [resources/examples.json](../../resources/examples.json)
