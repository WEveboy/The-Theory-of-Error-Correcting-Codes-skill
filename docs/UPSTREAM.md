# 上游与适配依据

- 仓颉：https://github.com/kangarooking/cangjie-skill 。本次核验v2.5.0刷新版，DeepSeek包SHA256为b565c693eaf7bc24f09bde5df15e1c7e63fee504773f98288e909e7b3086ddbd；对应上游源提交3adf9e61eec96edf34055432942f2952cfd7cfd9。上游包不随本项目分发。
- Codex技能发现：https://learn.chatgpt.com/docs/build-skills 。新文档使用用户.agents/skills；本机旧安装使用.codex/skills，安装器兼容已有目录以避免重复入口。
- DeepSeek Harness：https://github.com/deepseek-ai/deepseek-harness 。采用官方仓颉适配包所使用的skills服务注册合同；本项目适配器独立编写，固定技能名称与资源目录。
- Harness模型调用需要用户自己的模型配置。本文不复制本机凭据，不测试付费会话；插件契约和数学计算测试与宿主真实模型会话分别报告。

研究来源和原书章节入口见Skill内resources/proof_ledger.md及references/overview.md。原书选定重点证明核读不等同全书逐页逐题核验。
