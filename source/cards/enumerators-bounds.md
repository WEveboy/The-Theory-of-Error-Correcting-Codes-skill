# 重量枚举器、对偶变换与界的研究入口

## R — Reading

B：5章pp.126–129的MacWilliams恒等式；17章pp.535–539及21章pp.666–668的非负变换与界机制。

## I — Interpretation

二元线性码A_j的对偶候选系数为|C|⁻¹Σ_i A_i K_j(i)。原始系数非负、A0=1、总数为2的幂是必要检查。精确整数/有理数比浮点近似更适合证明。

## A1 — Application Example

原书5章例：偶重量3码1+3Y²变为重复码1+Y³。合成反例分布{0:1,1:3}长度3给非整数/负变换系数，必要条件失败。

## A2 — Future Trigger

MacWilliams、weight enumerator、few-weight codes、Krawtchouk、LP bounds。实际生成码先读function-code；LP求解需另外准备正确模型。

## E — Execution

research_extensions.py macwilliams输入length与distribution，输出精确变换与nonnegative_integers。给定已证线性码时解释为对偶枚举器；仅给分布时只报告necessary_conditions_only。研究界可构建距离分布非负约束和对偶证书，但当前没有通用LP求解器。

## B — Boundary

分布可行不等于码存在，浮点求解状态不是证明。未核清第21章参数的界不输出闭式数值；本卡自动能力限于精确枚举器检查。
