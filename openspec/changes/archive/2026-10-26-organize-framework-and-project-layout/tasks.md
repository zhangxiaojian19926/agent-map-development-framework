## 1. 建立基线与文档导航

- [x] 1.1 盘点现行文档、历史资料、运行时资源和相对链接，形成路径迁移对照；运行现有公共检查与完整测试并记录基线，确认没有无关工作区改动。
- [x] 1.2 调整 README 和现行入口，区分使用者与维护者路径；通过 First-time user、Maintainer finds repository-specific guidance 两个场景走查及链接检查验证。
- [x] 1.3 新增 `docs/guide/` 的项目布局、日常开发、模块生命周期、测试交付和框架升级指南；逐项核对每份指南包含输入、目录读写范围、授权边界、验证证据和完成状态。
- [x] 1.4 新增 `docs/maintainer/` 的仓库布局、验证和发布说明；核对维护者命令不再被表述为普通业务项目的初始化前置步骤，所有新增相对链接通过检查。

## 2. 固化业务项目目录所有权

- [x] 2.1 在项目布局指南中建立完整所有权表，覆盖项目声明、生成目录、公共包、本机状态、当前事实、活跃规格、业务模块、验证证据、知识内容和构建产物；用 Contributor classifies a new artifact 场景逐项验证唯一位置、责任方和提交规则。
- [x] 2.2 补充生成文件、人工受管区块、`.framework/`、私有输入、凭据、缓存和 `dist/` 的编辑与提交边界；通过 Generated file is edited 和 Local state is reviewed for commit 场景检查不覆盖人工内容、不共享本机状态。
- [x] 2.3 补充已有源码原位接入、新项目默认模块位置、拟议模块不建空目录及跨模块测试归属规则；用 Existing source tree、Planned module、Cross-module change 三个交付场景验证与现有协议一致。
- [x] 2.4 核对 `AGENTS.md`、项目模板、模块模板、任务交接和验证报告之间的目录指引；通过链接与内容一致性检查消除第二套竞争流程或状态定义。

## 3. 收敛运行时分发白名单

- [x] 3.1 为新目标项目增加运行时必要文件和维护者禁止文件的失败测试；先证明当前生成结果不符合 New project receives only runtime content，再记录有效 RED。
- [x] 3.2 实现显式运行时白名单并保持清单指纹校验，覆盖根入口、法律文件、技能、模板、CLI 和具名现行文档；运行新增测试及既有初始化回归至 GREEN，确认 Runtime payload is incomplete 能给出缺失路径。
- [x] 3.3 为旧目标项目中新版本不再分发的受管残留增加失败测试，覆盖哈希吻合、人工修改、归属不明和目录外同名文件；先验证旧行为会残留或无法安全区分，再实现有限清理规则。
- [x] 3.4 实现旧受管残留的归属与哈希保护，禁止递归清空 `.agent-framework/`；验证仅未修改的旧受管冗余文件被清理，人工修改产生冲突且现场保留。
- [x] 3.5 验证重复初始化、已有项目升级和既有源码原位接入；比较升级前后 `docs/project/` 人工正文、模块规则、业务源码、知识内容和活跃 change 的指纹，确认未被覆盖、移动或归档。

## 4. 整理历史资料与旧状态

- [x] 4.1 建立历史资料索引和统一历史标识，先完成逻辑归档；通过 Historical document is encountered 场景检查历史内容不会被当前入口当作操作步骤或状态来源。
- [x] 4.2 分批将历史计划和历史验收迁入 `docs/archive/`，逐批修正相对链接、文档导航、测试与清单；每批运行大小写敏感链接检查，避免一次性移动现行协议。
- [x] 4.3 为既有未完成 OpenSpec change 建立任务、最终版本、环境和证据对账；核对 Legacy change contains unchecked work，未执行项继续保持未勾或 NOT_RUN，不以本变更的实施结果替代其专属验收。
- [x] 4.4 对证据完整的旧任务只记录可核实结论，并单列仍需外部验证或用户决定的事项；不自动同步、归档旧 change，任何后续 Completed historical change is archived 操作均走独立授权和正常门禁。

## 5. 完善自动检查与最终验收

- [x] 5.1 扩展分发检查或相关测试，覆盖运行时白名单漂移、禁止内容、必要文件缺失、历史标识和文档链接；通过 Distribution validation detects layout drift 验证错误可定位且 CI 会失败。
- [x] 5.2 更新 `CHANGELOG.md` 与 `framework-manifest.json`，运行 `python3 tools/check-framework` 和完整单元测试；核对新增文件全部登记且无无关指纹变化。
- [x] 5.3 运行 `openspec validate --all --strict --no-interactive` 和 `git diff --check`，逐条建立 Requirement/Scenario 到任务、测试和证据的追踪矩阵；不适用验证注明理由，不以文档存在代替场景走查。
- [x] 5.4 完成规格符合性和代码质量评审，处理重要问题并重跑受影响检查；在最终工作树和 Ubuntu/macOS CI 取得新鲜证据后，分别报告实现、验证、旧 change 状态及未执行边界。
- [x] 5.5 按用户选择处理本变更的提交、集成、规格同步和归档，未获授权不推送或发布；交付时一次列明可复用目录治理经验及目标知识库，取得明确授权后才摄入。
