# 函数生成码、秩门与重量分布

## R — Reading

B：1章线性码/对偶、5章pp.125–129；D/E：在RM(1,n)上添加输出分量的完整长度码。

## I — Interpretation

C_F由1、输入坐标和输出坐标生成，长度N。只有rank=n+m+1时最小非零重量才等于NL(F)；否则某非零分量仿射，NL0而码最小正重量仍可为正。

## A1 — Application Example

合成演练：F(x)=x于3位，rank4而非7，NL0，C_F最小正重量4。原书二次bent例生成码的重量0:1/6:16/8:30/10:16/16:1。

## A2 — Future Trigger

function-code bridge、少重量码、生成矩阵、rank degeneracy。由分布求对偶读enumerators-bounds；设计应用读design-oa。

## E — Execution

先输出rank和桥梁前提是否满足，再按脚本预算枚举码字及重量；超预算明确未枚举。对全谱得到的重量分布与独立枚举交叉检查。严禁将输入行数代替rank。

## B — Boundary

当前码包含原点及常数行，穿孔长度N−1必须另证。非线性Kerdock的形式关系不等于普通线性对偶。

## 配套资源

路径相对于本文件；脚本需先检查运行条件，不因附带而自动执行。

- [resources/research_core.py](../../resources/research_core.py)
- [resources/test_research_core.py](../../resources/test_research_core.py)
- [resources/usage.md](../../resources/usage.md)
- [resources/research_map.md](../../resources/research_map.md)
- [resources/proof_ledger.md](../../resources/proof_ledger.md)
- [resources/examples.json](../../resources/examples.json)
