# BCT、DLCT与传播准则

## R — Reading

E：Cid等2018 BCT；Bar-On等2019 DLCT；来源链接和定义见proof_ledger.md。D：直接计数与独立恒等式核验。

## I — Interpretation

经典BCT需要方形置换。DLCT(u,b)=#{x:b·(F(x+u)+F(x))=0}−2^(n−1)=AC_b(u)/2；归一化偏差另除2^n。

## A1 — Application Example

GF(8)立方置换的boomerang uniformity为2；非置换仍可计算DLCT，而经典逆函数BCT应返回not_applicable。

## A2 — Future Trigger

boomerang、BCT、DLCT、差分线性表、SAC、PC传播准则。

## E — Execution

sbox_criteria.py analyze --input function.json --out sbox.json，可加--include-tables。同时给坐标SAC、全部非零分量PC阶数、DLCT最大绝对计数偏差和见证；置换计算经典BCT及最坏输入见证。先确认max-work预算。

## B — Boundary

n≤8,m≤n。SAC只检查单位输入方向与坐标；全分量PC是更强的明确条件。BCT/DLCT不得用作一般CCZ不变量；这些指标不证明系统安全。
