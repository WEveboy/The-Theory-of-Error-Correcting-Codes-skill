# 支持集设计与正交阵的精确检查

## R — Reading

B：6章设计条件框架；21章pp.670–671定理15/16。D：直接枚举子集/投影检查给定有限对象。

## I — Interpretation

t-(v,k,λ)简单设计要求所有块大小k且每个t子集恰出现λ次。二元OA强度t要求任意t列全部模式均出现M/2^t次。它们使用不同空间和计数，必须先明确对象。

## A1 — Application Example

合成演练：4点全部6个2子集是1-(4,2,3)设计；全部3位向量是强度3的OA。少数重量本身不能替代这两个条件。

## A2 — Future Trigger

t-design、orthogonal array、支持集、均匀投影、码与秘密共享。由码推出设计的定理条件需单独读；具体密码方案不自动推定。

## E — Execution

research_extensions.py design输入v,k,t,blocks，或oa输入rows,strength；计数精确并在失败时给子集/列模式见证。当前简单设计拒重复块，OA允许重复行并标明多重集。输出核验级别、λ/index和预算状态。

## B — Boundary

t上限及组合预算见CLI/API，超限拒绝不冒充已核验。给定对象检验不等于构造全族或证明系统安全。

## 配套资源

路径相对于本文件；脚本需先检查运行条件，不因附带而自动执行。

- [resources/research_extensions.py](../../resources/research_extensions.py)
- [resources/test_research_extensions.py](../../resources/test_research_extensions.py)
- [resources/usage.md](../../resources/usage.md)
- [resources/research_map.md](../../resources/research_map.md)
- [resources/proof_ledger.md](../../resources/proof_ledger.md)
- [resources/examples.json](../../resources/examples.json)
