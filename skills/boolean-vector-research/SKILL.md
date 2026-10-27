---
name: boolean-vector-research
description: |
  布尔函数与向量值函数科研：Walsh/RM、bent/APN、有限域迹构造、DDT/BCT/DLCT、AI、函数生成码、EA/CCZ给定证书、设计与序列，以及带哈希的可复算实验。用于设计和分析有限候选及核对证明条件；不替代完整分类、通用译码或系统安全评估。
metadata:
  cangjie.generated-by: cangjie-tools v2.5.0
  cangjie.variant: single
  cangjie.bundle-id: bundle.boolean-vector-research
  cangjie.capability-count: 16
  cangjie.entrypoint-count: 1
---
# 布尔函数与向量值函数科研工具（MacWilliams基础与独立扩展） — 全书能力入口

## 触发与不触发

**适用**：与本书能力域相关的咨询与任务（见下方路由表的意图列）。
**不适用**：
- 通用BCH/RS译码工程、任意PDF自动蒸馏和与函数科研无关的请求。
- 自动证明新颖性、无条件宣称安全或实现完整CCZ分类。

## 核心原则（常驻速览，概览类问题读到这里即可回答）

1. 先读resources/usage.md确认当前命令与限制；所有计算记录n,m、位序、域模型和预算。
2. 分离B原书、D独立推导、E外部理论、H研究假设；证明、有限全算、采样和未定分别报告。
3. 向量性质检查全部非零分量；函数与码的距离关系先过满秩门；bent、平衡和置换的条件分别核对。
4. 执行前读取能力卡；跨域任务按阶段依次加载所需卡，每阶段最多两张，逐项输出证书与失败见证。
5. 扩展研究优先查resources/research_map.md；完整CCZ分类、一般高阶精确距离、LP界和新族证明不得伪报已完成。
6. 使用Python3.10+标准库工具；资源相对SKILL目录定位。结果写用户工作目录，不写已安装技能目录。

## 能力路由（先读本表，按意图加载 1 张能力卡）

| 用户意图 | 先读 | 补读/备注 |
|---|---|---|
| 表示、规格与条件检查；真值表、ANF、域表示转换、位序混淆、specification | references/capabilities/representation.md | — |
| 标量谱、非线性度与RM陪集；Walsh spectrum、非线性度、最近仿射函数、RM coset | references/capabilities/scalar-spectrum.md | references/capabilities/representation.md |
| 二次型、极化秩与导数核；quadratic rank、二次型、根空间、秩分布、二次函数族 | references/capabilities/quadratic-rank.md | references/capabilities/representation.md |
| 带证明的bent构造；construct bent、MM/Maiorana–McFarland、二次bent、bent对偶、直接和 | references/capabilities/bent-construction.md | references/capabilities/representation.md |
| 全分量谱、差分与向量函数设计；S-box、APN、vectorial Boolean function、全分量谱、DDT、置换性 | references/capabilities/vector-metrics.md | references/capabilities/representation.md |
| 函数生成码、秩门与重量分布；function-code bridge、少重量码、生成矩阵、rank degeneracy | references/capabilities/function-code.md | references/capabilities/representation.md |
| 自相关、韧性、代数免疫与高阶距离；autocorrelation、相关免疫、resilience、algebraic immunity、higher-order nonlinearity | references/capabilities/advanced-invariants.md | references/capabilities/representation.md |
| 迹、幂函数与可证候选搜索；Gold functions、trace polynomial、幂函数、构造搜索、APN设计 | references/capabilities/trace-power-search.md | references/capabilities/representation.md |
| EA变换、等价证书与分类预筛；EA-equivalence、equivalence certificate、函数去重、分类预筛、CCZ | references/capabilities/ea-certificate.md | references/capabilities/representation.md |
| 重量枚举器、对偶变换与界的研究入口；MacWilliams、weight enumerator、few-weight codes、Krawtchouk、LP bounds | references/capabilities/enumerators-bounds.md | references/capabilities/representation.md |
| 支持集设计与正交阵的精确检查；t-design、orthogonal array、支持集、均匀投影、码与秘密共享 | references/capabilities/design-oa.md | references/capabilities/representation.md |
| 周期序列与异或相关分析；sequence correlation、迹序列、低相关序列族、periodic autocorrelation、XOR相关 | references/capabilities/sequence-correlation.md | references/capabilities/representation.md |
| 有限域多项式、绝对迹与对偶基；trace polynomial、绝对迹、多项式构造、dual basis、有限域表示 | references/capabilities/finite-field-functions.md | references/capabilities/representation.md |
| BCT、DLCT与传播准则；boomerang、BCT、DLCT、差分线性表、SAC、PC传播准则 | references/capabilities/sbox-criteria.md | references/capabilities/representation.md |
| CCZ图仿射证书与不变量预筛；CCZ certificate、图仿射、逆函数关系、等价预筛 | references/capabilities/graph-ccz-certificates.md | references/capabilities/representation.md |
| 可复算构造与实验归档；完整实验、批次候选记录、构造到指标、reproducible experiment | references/capabilities/research-workflow.md | references/capabilities/representation.md |

**非能力类查询**：
- 书名/作者/章节/整书概览 → references/overview.md
- 术语解释 → references/glossary.md
- 决策规则速查（不需要原文依据时） → references/cheatsheet.md
- 完整意图与关键词索引（本表未覆盖的意图先查这里） → references/capability-index.md

## 加载规则

- 每次任务先读本文件，再按路由表加载 **1** 张能力卡；任务明确跨域时最多加载 2 张。
- 概览/书名类问题不加载能力卡，用「核心原则」与 overview.md 回答。
- 路由表与 capability-index.md 都无法命中的意图，明确告知超出本书范围，不要硬套。

## 边界与判停

- 缺n/m/位序/域模型时询问或明确仅用已有真值表，不能猜关键条件。
- 超预算、来源不足或定理前提不满足时说明未算/未证；继续可执行的独立部分。
- 禁止将p.430习题20印刷推广式当有效构造；使用卡内有证明的同侧变量版本。
