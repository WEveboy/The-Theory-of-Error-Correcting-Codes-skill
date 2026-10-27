# 全分量谱、差分与向量函数设计

## R — Reading

E：Carlet作者章节chap-vectorial-fcts-corr.pdf，分量、非线性度、差分与bent的相关定义。B/D：第3章pp.81、86–88的图像校验和立方差分桥梁。

## I — Interpretation

所有非零b的分量b·F都要检查。NL(F)是它们非线性度最小值；DDT(u,v)计数F(x+u)+F(x)=v，u≠0。差分均匀性与非线性度分别度量不同约束，不能互相替代。

## A1 — Application Example

合成演练：GF(4)上xy是4→2向量bent，NL6、δ4且不平衡。GF(8)上x³是APN置换，NL2、δ2；它不是bent。

## A2 — Future Trigger

S-box、APN、vectorial Boolean function、全分量谱、DDT、置换性。符号族证明先读trace-power-search；只有坐标表现不能验收。

## E — Execution

research_core.py analyze完整计算全部b≠0与u≠0。输出分量NL/次数/谱、最弱分量、DDT最大值及方向/输出差见证、输出计数、置换/平衡判定；按预算标完整计算和未计算项。向量bent必须验证所有分量，n偶且m≤n/2。

## B — Boundary

方形置换不能向量bent。n>m时最佳δ可大于2。低δ和高NL不构成系统安全证明。不能把旧文献所列已知族/开放问题当当前现状。

## 配套资源

路径相对于本文件；脚本需先检查运行条件，不因附带而自动执行。

- [resources/research_core.py](../../resources/research_core.py)
- [resources/test_research_core.py](../../resources/test_research_core.py)
- [resources/usage.md](../../resources/usage.md)
- [resources/research_map.md](../../resources/research_map.md)
- [resources/proof_ledger.md](../../resources/proof_ledger.md)
- [resources/examples.json](../../resources/examples.json)
