# 可复算构造与实验归档

## R — Reading

D：把已经验证的有限构造、核心分析和S-box计算组合为可追溯科研流程；不是原书定理。

## I — Interpretation

一个实验必须保存生成参数、完整函数表、计算结果、阶段日志、运行环境和程序指纹。manifest哈希一致只证明内部一致；重算匹配另行报告，不代表签名认证。

## A1 — Application Example

Gold n=3,k=1,polynomial=11生成GF(8)立方表，输出NL2、δ2、BCT均匀性2及可核验归档。

## A2 — Future Trigger

完整实验、批次候选记录、构造到指标、reproducible experiment。

## E — Execution

research_workflow.py --input project.json --out-dir 新目录。project的construction={kind,params}，kind支持table,trace,polynomial,gold,mm,quadratic-bent；advanced/sbox/include_sbox_tables是JSON布尔值。生成project/function/analysis、可选sbox、environment、execution.jsonl、summary及最后写入的manifest。用experiment_audit.py --directory 实验目录 --recompute --out 外部新文件，检查哈希、文件关联、阶段日志协议和有限重算；失败时给文件及首个差异JSON指针；用usage.md的审计合同解释状态。

## B — Boundary

拒绝已有输出目录；所有数学计算先完成再创建目录，IO故障仍可能留下部分文件，需检查manifest与哈希。有限计算不是族证明、查新或完整分类；advanced超维项仍可能not_computed。

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
- [resources/experiment_audit.py](../../resources/experiment_audit.py)
- [resources/test_experiment_audit.py](../../resources/test_experiment_audit.py)
