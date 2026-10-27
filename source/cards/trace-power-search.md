# 迹、幂函数与可证候选搜索

## R — Reading

B：3章p.86、4章pp.115–119、8章pp.239–240。D：Gold差分线性化与有限枚举工作流。

## I — Interpretation

固定域模型再生成x^(2^k+1)，差分的线性部分可归约为a x^(2^k)+a^(2^k)x。gcd(k,n)=1时核为{0,a}，给APN；置换性另查gcd(2^k+1,2^n−1)。迹/指数支撑是构造参数而不是结论。

## A1 — Application Example

B桥梁：原书x³校验。D例GF(8)立方APN且置换；GF(16)立方APN但不是置换。任意二项扰动的APN不能沿用该证明。

## A2 — Future Trigger

Gold functions、trace polynomial、幂函数、构造搜索、APN设计。全指标读vector-metrics，分类证书读ea-certificate。

## E — Execution

使用core的gold构造或search_monomials.py显式指数列表。记录域模多项式、指数、参数条件、预算及全部候选结果，排序只依据用户指标。域模型验证应检查不可约；给出的元数据不替代该验证。一般有限域多项式/迹构造使用field_functions.py，读取finite-field-functions卡，再用核心分析。

## B — Boundary

最优仅指已枚举集合；不宣布新族或当前最好。MS有限域变换不是Walsh实变换。一般指数/迹/扰动族尚无自动定理证明。
