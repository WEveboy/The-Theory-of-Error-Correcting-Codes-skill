# GitHub更新与发布流程

沿用用户指定的“密码函数指标分析”项目最新流程，并针对Skill与文档调整验证命令。原流程：https://github.com/WEveboy/Boolean_Function_Analysis/blob/main/docs/UPLOAD_WORKFLOW.md 。本仓库为WEveboy/The-Theory-of-Error-Correcting-Codes-skill。

1. 读取远端main与维护约定，列出本次源码、范例、TeX/PDF、安装器和版本改动；保留远端其他文件。空仓库仅在全部交付准备就绪后初始化。
2. main只收维护所需源文件、两份最终用户教程PDF、TeX源、测试、CI和文档。排除build/dist、缓存、完整原书、私人路径、API密钥、依赖副本和临时实验输出。
3. 运行Python单元测试、安装器迁移测试、DeepSeek适配器契约测试；对两平台的数学资源做SHA256一致性核对。用XeLaTeX编译两份教程并渲染检查；核对文档相对链接和安装命令。
4. 再次读取远端main。使用已确认WEveboy写权限的连接器提交；对已有分支用预期SHA约束更新，禁止强制覆盖他人改动。上传后核对提交、文件清单和关键页面，等待CI完成；失败则修复并重新验证。
5. 发行版采用edition-v1.0.0格式tag；Codex ZIP、DeepSeek TGZ/ZIP、源码ZIP和SHA256SUMS作为Release资产。校验档案完整性、哈希、下载链接和安装烟测。若连接器不支持Release，使用已认证且属于WEveboy的GitHub客户端；不得把未上传的资产描述为已发布。
6. 更新README下载入口、CHANGELOG及发布日志。保存提交SHA、CI结果、资产哈希和未完成事项。后续继续使用本流程。

本仓库第一版采用原生Actions发布：提交信息以`release: first edition`开头时，在双系统验证成功后执行publish任务，使用GitHub提供的临时仓库令牌发布。令牌只通过CI环境传入，不写入源码或日志。发布后逐个下载资产核验SHA256。已存在第一版时不覆盖；后续版本先明确更新tag/版本与流程，再发布。

本项目测试：python -m unittest discover -s skills/boolean-vector-research/resources -p "test_*.py"；python -m unittest discover -s tests；python scripts/make_release.py --prepare-only；node --test tests/test_deepseek.mjs；python scripts/verify_project.py。TeX编译命令见docs/tutorial/BUILD.md。

许可证策略沿用原流程：用户未另行指定前不新增LICENSE；上游依赖按上游许可自行下载安装，不随本项目再分发。
