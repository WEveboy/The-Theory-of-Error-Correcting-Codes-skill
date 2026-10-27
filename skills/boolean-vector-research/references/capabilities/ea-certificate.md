# EA变换、等价证书与分类预筛

## R — Reading

B：14章p.417的仿射变换及同分布不保证等价。E：Carlet向量章节的EA/CCZ关系；D：逐点验证给定EA证书。

## I — Interpretation

先选等价关系。工具验证G(x)=B F(Ax+s)+Lx+c，A/B必须可逆。显式变换证明等价；关系所保留的不变量不同可否定等价；相同直方图或未搜到变换都不能证明。

## A1 — Application Example

合成反例：F(x)=x加Lx=x变成零函数，是合法EA操作，但置换性不保留。不要把EA和仅输入/输出可逆仿射复合的性质混淆。

## A2 — Future Trigger

EA-equivalence、equivalence certificate、函数去重、分类预筛、CCZ。仅算谱读vector-metrics；完整CCZ自动分类不在当前工具内。

## E — Execution

research_extensions.py ea：输入n,m,table、input_rows/output_rows/affine_rows及平移常数，可选target。返回变换后的表、逐点匹配结果与可逆矩阵证书。分类报告分别给已证等价、已证不等价、未定；文献比较保留检索范围与日期。

## B — Boundary

工具不自动寻找EA变换；给定CCZ图证书使用graph-ccz-certificates卡，不实现完整分类或群规范形。EA加仿射项不保证置换/次数不变；CCZ保留哪些量须逐项引用，不能默认保留所有指标。

## 配套资源

路径相对于本文件；脚本需先检查运行条件，不因附带而自动执行。

- [resources/research_extensions.py](../../resources/research_extensions.py)
- [resources/test_research_extensions.py](../../resources/test_research_extensions.py)
- [resources/usage.md](../../resources/usage.md)
- [resources/research_map.md](../../resources/research_map.md)
- [resources/proof_ledger.md](../../resources/proof_ledger.md)
- [resources/examples.json](../../resources/examples.json)
