# Boolean Vector Research Skills · 第一版

从MacWilliams与Sloane《The Theory of Error-Correcting Codes》的编码理论基础蒸馏，结合单独标注的现代来源，服务布尔函数与向量值函数设计及科研复现。第一版V1（公开版本1.0.0）冻结开发基线0.2.2。

16张能力卡、8个Python标准库程序：Walsh/RM、二次型、bent/APN、全分量差分、AI与高阶距离、生成码与重量分布、迹/对偶基、EA/给定CCZ证书、BCT/DLCT/SAC/PC、设计/OA、序列相关与实验审计。范围与预算见[使用合同](skills/boolean-vector-research/resources/usage.md)。

## 安装与教程

- [Codex安装版教程PDF](docs/tutorial/Codex-First-Edition.pdf) · [TeX源](docs/tutorial/Codex-First-Edition.tex)
- [DeepSeek Harness安装版教程PDF](docs/tutorial/DeepSeek-First-Edition.pdf) · [TeX源](docs/tutorial/DeepSeek-First-Edition.tex)
- 两份教程都从安装仓颉cangjie-skill开始，覆盖首次计算、完整实验、日志、重算、常见错误和升级。
- Codex：运行python scripts/install_codex.py。新装默认用户.agents/skills；本机已有.codex/skills安装时沿用它。首次不覆盖已有目录；升级明确使用--replace并先备份。
- DeepSeek Harness：按教程安装dsh及仓颉插件，再添加本项目的TGZ插件。普通DeepSeek网页对话不等同于具备本地Python执行能力的Harness；也可手工在本地运行程序。

安装包与校验文件发布在[第一版Release](https://github.com/WEveboy/The-Theory-of-Error-Correcting-Codes-skill/releases/tag/edition-v1.0.0)。如Release尚未显示，以实际发布记录为准；源码下载后也可按教程安装或自行打包。

## 从源码复现

Python3.10+，运行程序无第三方依赖。仓颉作者端另需PyYAML，DSH适配器需Node.js；教程用XeLaTeX。依次运行[上传流程中的检查命令](docs/UPLOAD_WORKFLOW.md)。[版本信息](release-info.json)说明公开版本与内部计算器版本的区别。

原书PDF和整章文本不随仓库分发。精确AI仅n≤6、二阶非线性度仅n≤4；新扩展通常n≤8。完整CCZ分类、未知变换搜索、新族自动证明和系统安全评估未实现。哈希一致不等于身份认证；重算重用现有数学程序，不是独立算法证明。

后续维护必须阅读[上传与发布流程](docs/UPLOAD_WORKFLOW.md)，并更新[日志](CHANGELOG.md)。
