# 最终验证记录

## 验证基线

- 验证日期：2026-10-27。
- Git HEAD：`926730154ff1532fcfe30d62b8a0288da1d6d4bf`。
- 验证对象：上述 HEAD 加当前未提交工作树差异，包含已跟踪文件修改及本次新增规格、实现和测试文件；未提交、未推送、未归档。
- 差异检查：`git diff --check` 返回码 0，无空白错误。
- 本次评审为按任务顺序进行的实现者自查，不是独立评审。

## 实际命令与结果

### 完整离线测试

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

结果：返回码 0；`Ran 228 tests in 39.974s`，`OK`。228/228 通过。

覆盖普通初始化、索引、关系地图、打包、知识库、旧逆向 v1/v2、设备治理、新自动画像与计划、安装恢复、命名适配器、网页快照及动态 provider 故障矩阵。默认测试使用本地 fixture、假下载器、假执行器和假 provider，不依赖真实网站或公网下载。

### 分发检查

```bash
PYTHONDONTWRITEBYTECODE=1 python3 tools/update-manifest
PYTHONDONTWRITEBYTECODE=1 python3 tools/check-framework
```

结果：清单更新 252 个指纹；分发检查返回码 0，输出 `PASS: 252 inventoried files, 23 skills; hashes, links and script syntax`。

### OpenSpec 严格校验

```bash
openspec validate adaptive-reverse-toolchain --strict
```

结果：返回码 0，输出 `Change 'adaptive-reverse-toolchain' is valid`。

### 只读 doctor

```bash
PYTHONDONTWRITEBYTECODE=1 python3 tools/framework doctor --target .
```

结果：返回码 5，`status=BLOCKED`、`initialization=PARTIAL`、`onboarding=NOT_PREPARED`，`next_actions=["init --target <project>"]`。当前目录是框架分发仓库而不是已初始化目标工程，因此该结果表示缺少目标项目初始化状态，不是本变更测试失败。该命令只读，不执行逆向工具、不联网、不自动修复。普通初始化及目标工程 doctor 行为由完整测试中的初始化、只读状态和兼容性用例覆盖。

## 兼容性与非逆向隔离结论

- 普通初始化、索引、地图、打包和知识库回归通过；无逆向请求时不安装工具、不生成自动计划、不访问网页或设备。
- 旧五字段 scope、`reverse-scope/v2` 和旧 reverse dry-run 输入语义保持兼容。
- dry-run 不创建 `.framework`、不联网、不启动进程。
- 工具 `READY`、观察 `RECORDED` 和运行验证分别报告；安装成功不冒充观察或业务验证成功。
- 网页远程获取、浏览器观察、网络记录和登录态授权相互独立；默认无真实浏览器 provider。

## 未验证项

以下项目没有真实环境证据，均为 `NOT_RUN`：

- 真实 REA、Ghidra、JDK、WABT 安装及适配器运行。
- 真实网站获取、真实浏览器 provider、动态 DOM/网络观察。
- 私有认证、个人登录态、Cookie 或 Authorization 的真实使用。
- 真实设备观察、设备修改、回滚和部署。
- 推送、发布、跨项目全局缓存及生产环境集成。

## 收尾边界

本记录不表示已提交、已同步主规格或已归档。`openspec-sync-specs`、`openspec-archive-change` 和知识库写入均需后续明确授权。
