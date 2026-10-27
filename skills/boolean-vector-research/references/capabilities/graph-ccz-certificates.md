# CCZ图仿射证书与不变量预筛

## R — Reading

E：Carlet作者向量函数章节§3.1.5的图仿射等价。D：对给定矩阵逐点验证及完整图字符谱/差分直方图检查。

## I — Interpretation

用z=x|(F(x)<<n)编码图；给定可逆L与平移c，检验Lz+c的低n位是否一一覆盖输入，再恢复变换后的函数表。

## A1 — Application Example

方形置换交换输入输出得到逆函数；对非置换交换会因投影碰撞而不再是函数图，必须返回碰撞见证。

## A2 — Future Trigger

CCZ certificate、图仿射、逆函数关系、等价预筛。EA证书使用ea-certificate卡。

## E — Execution

graph_equivalence.py certificate输入n,m,table,graph_rows,可选graph_shift和target；矩阵行是位掩码。prefilter输入n,m,left,right。报告verified_graph_affine_certificate、not_function_graph或匹配失败；预筛不变量不同报告proven_not_ccz_equivalent，相同仅inconclusive。

## B — Boundary

n≤8,m≤n，预算明确。不搜索未知变换，不给规范形或完整分类。预筛包含全部非零图字符的绝对Walsh谱及u≠0的完整DDT直方图；不以代数次数或BCT冒充CCZ不变量。

## 配套资源

路径相对于本文件；脚本需先检查运行条件，不因附带而自动执行。

- [resources/research_extensions.py](../../resources/research_extensions.py)
- [resources/test_research_extensions.py](../../resources/test_research_extensions.py)
- [resources/usage.md](../../resources/usage.md)
- [resources/research_map.md](../../resources/research_map.md)
- [resources/proof_ledger.md](../../resources/proof_ledger.md)
- [resources/examples.json](../../resources/examples.json)
- [resources/research_core.py](../../resources/research_core.py)
- [resources/field_functions.py](../../resources/field_functions.py)
- [resources/sbox_criteria.py](../../resources/sbox_criteria.py)
- [resources/graph_equivalence.py](../../resources/graph_equivalence.py)
- [resources/research_workflow.py](../../resources/research_workflow.py)
- [resources/test_field_functions.py](../../resources/test_field_functions.py)
- [resources/test_new_research.py](../../resources/test_new_research.py)
- [resources/test_research_workflow.py](../../resources/test_research_workflow.py)
