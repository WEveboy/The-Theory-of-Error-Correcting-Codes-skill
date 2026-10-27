# 有限域多项式、绝对迹与对偶基

## R — Reading

B：第4章pp.115–119的迹配对和对偶基。D：固定多项式基的逐点计算；不是原书自动生成的算法。

## I — Interpretation

先验证模多项式不可约。绝对迹Tr(z)=Σz^(2^i)取F₂值；对偶基满足Tr(b_i d_j)=δ_ij，坐标由迹配对恢复。

## A1 — Application Example

GF(8)用模多项式11构造Tr(x³)，再将完整真值表交给全谱工具；常数项采用0^0=1约定。

## A2 — Future Trigger

trace polynomial、绝对迹、多项式构造、dual basis、有限域表示。

## E — Execution

field_functions.py polynomial|trace|dual-basis --input spec.json --out result.json。构造输入n,polynomial,terms=[{coefficient,exponent}]；对偶基输入n,polynomial及可选basis。运行前读usage.md；构造输出可直接交research_core.py analyze。输出域模型、完整表、迹前值或配对矩阵和坐标恢复表。

## B — Boundary

n≤8，terms≤64且受预算限制。构造的索引始终是标准多项式基；对偶基坐标表不会偷偷改变函数表的索引。有限表不证明全参数族。
