# 二次型、极化秩与导数核

## R — Reading

B：15章 pp.434–442，定理1、Dickson标准形、定理5。D：由标准形得到非零谱幅与数量。

## I — Interpretation

仅次数≤2时极化B_f(x,y)=f(x+y)+f(x)+f(y)+f(0)是交错双线性型。严格上三角Q给B=Q+Qᵀ，秩r偶数。非零Walsh幅2^(n−r/2)、出现2^r次。向量函数需检查全部非零分量的矩阵和。

## A1 — Application Example

原书15章pp.435–436、442：x₀x₁+x₂x₃，极化秩4，陪集6/10各16。合成反例F=(q,q+x₀)：两个坐标bent而其和线性。

## A2 — Future Trigger

quadratic rank、二次型、根空间、秩分布、二次函数族。一般向量指标读vector-metrics；高次数不套此公式。

## E — Execution

先ANF检查次数，再输出极化矩阵/秩，与实际全谱交叉核对。对全部b≠0记录rank；需要核证书可按矩阵消元重建。研究二次差分时对每u≠0写线性部分与核，只有全部方向核条件已证才给族级APN结论。

## B — Boundary

高次数只能说此公式不适用；仅有限核验不能证明一般参数族。两两秩条件与单个高秩条件不同；Kerdock一般构造尚未作为自动算法实现。

## 配套资源

路径相对于本文件；脚本需先检查运行条件，不因附带而自动执行。

- [resources/research_core.py](../../resources/research_core.py)
- [resources/test_research_core.py](../../resources/test_research_core.py)
- [resources/usage.md](../../resources/usage.md)
- [resources/research_map.md](../../resources/research_map.md)
- [resources/proof_ledger.md](../../resources/proof_ledger.md)
- [resources/examples.json](../../resources/examples.json)
