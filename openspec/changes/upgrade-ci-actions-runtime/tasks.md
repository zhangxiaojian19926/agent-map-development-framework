## 1. 契约测试与最小升级

- [x] 1.1 新增标准库 `unittest` 工作流契约测试，覆盖两个工作流的 Action 版本、Python 3.9、Ubuntu/macOS 矩阵、权限、并发、验证命令和发布关键步骤；先在旧配置上运行，确认测试因旧 Action 版本而失败，形成有效 RED，并记录命令与结果。
- [x] 1.2 仅将 `.github/workflows/validate.yml` 和 `.github/workflows/release.yml` 中两处 `actions/checkout@v4` 改为 `actions/checkout@v7`、两处 `actions/setup-python@v5` 改为 `actions/setup-python@v7`；通过 `git diff` 核对除这四处版本引用外无工作流行为变化。
- [x] 1.3 运行新增契约测试并达到 GREEN；逐项核对 Python 3.9、验证矩阵、权限、并发、验证命令及发布条件均保持原义。

## 2. 清单同步与离线验证

- [x] 2.1 同步 `framework-manifest.json` 中受影响工作流的登记信息，运行 `python3 tools/check-framework`、完整测试套件和 `openspec validate upgrade-ci-actions-runtime --strict`，保存实际命令、退出状态和测试数量。
- [x] 2.2 检查最终 diff 与工作树，记录离线验证范围；在尚无对应线上运行证据时，将升级后实际 CI 和发布实测分别标记为 `NOT_RUN`，不以本地结果代替线上验收。

## 3. 线上 CI 验收与交付

- [ ] 3.1 在获得实施与推送授权后提交并推送本变更，定位目标提交的验证工作流运行，确认 Ubuntu 和 macOS 任务均成功且执行的是目标提交；记录运行 ID、任务结果及提交 SHA。
- [ ] 3.2 读取两个平台任务的检查注解，确认 checkout 和 setup-python 的 Node.js 20 弃用警告消失；单独记录 Ubuntu 镜像迁移、macOS 容量等非本变更目标的平台提示，不主动触发发布工作流，发布实测保持 `NOT_RUN`。
- [ ] 3.3 最终复核工作树、严格规格校验和验证证据，确认 `add-project-bootstrap-and-maps` 与 `agent-led-project-intake` 未被修改；交付时分别说明已完成验证、未验证项和后续归档状态。
