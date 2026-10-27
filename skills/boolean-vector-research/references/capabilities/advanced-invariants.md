# 自相关、韧性、代数免疫与高阶距离

## R — Reading

B：14章字符变换与导数；13章RM阶数。E：Carlet chap-fcts-Bool-corr.pdf，§4.1.3的CI/韧性及代数免疫章节。

## I — Interpretation

自相关AC(u)=Σ_x(−1)^(f(x)+f(x+u))是W²的逆变换。CI要求低重量非零频率Walsh为0，韧性另加平衡。AI寻找非零低次数g使fg=0或(f+1)g=0。第r阶NL是到RM(r,n)的距离。

## A1 — Application Example

合成演练：f=x₀在多变量中平衡却存在低重量谱峰；二次bent导数平衡而f自身不平衡。AI、次数、NL不可作为同一个数输出。

## A2 — Future Trigger

autocorrelation、相关免疫、resilience、algebraic immunity、higher-order nonlinearity。仅请求一般NL读scalar-spectrum。

## E — Execution

research_core.py analyze --advanced，先读help与资源API文档确认门限。自相关检查AC(0)=N；线性结构要排除零方向。AI仅在支持维数内进行GF2零空间搜索并给非零annihilator见证，逐点验证乘积为0。NL2仅支持小维完整RM2枚举时标exact，否则not_computed。

## B — Boundary

不能把采样当精确AI/高阶NL；常函数的degree约定、CI极端值应解释。Siegenthaler类型界需要完整参数/例外，本卡不硬套无条件公式。

## 配套资源

路径相对于本文件；脚本需先检查运行条件，不因附带而自动执行。

- [resources/research_core.py](../../resources/research_core.py)
- [resources/test_research_core.py](../../resources/test_research_core.py)
- [resources/usage.md](../../resources/usage.md)
- [resources/research_map.md](../../resources/research_map.md)
- [resources/proof_ledger.md](../../resources/proof_ledger.md)
- [resources/examples.json](../../resources/examples.json)
