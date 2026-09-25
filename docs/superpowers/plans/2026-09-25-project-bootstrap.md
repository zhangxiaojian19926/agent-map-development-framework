# 工程初始化与模块地图 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans for native sequential execution, or superpowers:subagent-driven-development if the user selects it. Steps use checkbox syntax for tracking.

**Goal:** 将现有公共包升级为可执行的工程接入工具，真实跑通已有工程接入与全新需求开发两条路径后上传 main。

**Architecture:** Python 标准库负责计划、受控副作用、状态和文件生成；外部 CLI 由适配器调用。Agent 只产生经验证的分析结果，生成器落盘；设计、代码观察和运行证据分层保存。

**Tech Stack:** Python 3.9+、unittest、Git、OpenSpec、CodeGraph、Codex CLI；首版 macOS/Linux。

**Spec:** [设计](../../../openspec/changes/add-project-bootstrap-and-maps/design.md)、[宏观任务](../../../openspec/changes/add-project-bootstrap-and-maps/tasks.md)，同目录 specs 下五个能力契约。

## Global Constraints

- 首版 macOS/Linux、Python 3.9+；不引入第三方 pip 包。
- 不自动创建远程仓库、公开业务源码、部署或连接设备。
- dry-run 不创建目录、文件、锁、缓存或安装；doctor 默认只读。
- 配置不是授权；当前明确只读要求优先于先前自动化配置。
- 模块、仓库、索引分别标识；同仓模块可共享索引。
- 原有人工文件不覆盖；受管文件应用前重验指纹。
- 不在 Git 钩子调用 LLM，不修改全局 Git/宿主配置。
- 退出码 0/2/3/4/5 对应命令完成/输入错误/待确认或冲突/执行失败/部分完成或等待 Agent。
- CLI 成功、索引存在、模板生成均不等于业务验证通过。
- 首版 CodeGraph 和 Codex 必须有真实合成项目验收，不以 stub 替代。
- 用户已要求完成后上传公共仓库 main；后续明确要求搭建一键流程并在独立目录用真实 Codex CLI 开发小需求，执行范围据此确认。只有验证通过才集成，不把旧的待审阅状态当作重复审批理由。

## Review Focus

1. 在预览之后用符号链接替换输出父目录：应用时拒绝，不能写到工程外（任务 2）。
2. 多 worktree 共用 hook 路径：单工作树授权不能扩大为整个仓库授权（任务 6）。
3. Agent 看到了旧源码后才返回：过期证据不发布，不覆盖较新地图（任务 7）。
4. 初始化被杀死后用户修改了已生成文件：resume 保留人工内容并报告冲突（任务 2）。
5. 包中的第三方工具自动下载或改配置：适配审计检查真实副作用，不靠命令名称推断安全（任务 5）。

## 执行位置和发布范围

继续使用当前公共隔离工作树完成开发，避免在未实施前再引入迁移风险；不改原业务工程。
验收数据使用独立临时根或用户明确选择的验证根，日志不进入业务工程。
如需最终独立本地 clone，在发布完成后从远程 main 创建，再比对已发布文件；原 worktree 保留，不删除未提交资料。
远程目标固定为 https://github.com/zhangxiaojian19926/agent-map-development-framework ，仅推 main，不推原工程历史、其他分支或测试数据。

## 文件与接口划分

| 文件 | 单一职责 |
|---|---|
| tools/framework | 薄 CLI 入口，调用 framework_core.cli.main |
| tools/framework_core/cli.py | 参数、交互、状态序列、输出 |
| tools/framework_core/config.py | 输入 schema、确认范围及计划 |
| tools/framework_core/storage.py | 路径、指纹、事务、互斥与恢复 |
| tools/framework_core/modules.py | 有界发现、目录记录、生命周期 |
| tools/framework_core/process.py | 有界子进程及取消 |
| tools/framework_core/adapters.py | Git/OpenSpec/CodeGraph/Codex 适配 |
| tools/framework_core/hooks.py | hook 归属、事件标记 |
| tools/framework_core/maps.py | 证据校验、地图及入口渲染 |
| tools/framework_core/readiness.py | 只读分层诊断 |
| skill/project-bootstrap/SKILL.md | Agent 分析流程及任务入口/收尾规则 |
| tests/test_bootstrap_*.py | 每个边界对应的回归测试 |
| tests/integration/ | 默认不联网的合成流程及显式真实验收 |
| docs/bootstrap.md | 用户的两条完整使用路径 |

使用 dict/list/string 等 JSON 可序列化结构作为边界，不跨文件共享可变全局状态。
文件时间、随机 run-id、执行器通过参数注入，测试不用真实模型/网络。
所有执行器输入 argv 数组，不接受 shell=True。Plan、Catalog、Map、Report 都带 schema_version。

### Task 1: CLI 输入和只读计划

**关联：** BOOT-01、BOOT-03-CONSENT、READY-01；OpenSpec 2.1–2.2。
**Files:** 创建 tools/framework、tools/framework_core/__init__.py、cli.py、config.py、tests/test_bootstrap_config.py。
**Interfaces:** build_plan(root: Path, config: dict, action: str) -> dict；main(argv=None) -> int。计划含 actions、conflicts、required_capabilities、input_hashes；不写文件。

- [ ] 写失败测试，至少包含以下断言：

```python
with tempfile.TemporaryDirectory() as d:
    root = Path(d) / "中文 project"
    plan = build_plan(root, {"project_id": "demo", "agent": "manual"}, "init")
    self.assertFalse(root.exists())
    self.assertEqual(plan["action"], "init")
    self.assertNotIn("consent", plan)
```

- [ ] 运行 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_bootstrap_config.py -v，确认因目标行为缺失失败。
- [ ] 实现参数树 init/new/module clone/add/sync/doctor/resume；dry-run 只 render plan。交互一次列出全部副作用，非交互缺失目标/宿主/范围返回 2。确认结果放当前调用对象，不从配置读取 trusted=true。
- [ ] 使用固定 JSON 序列化计算计划摘要：

```python
def plan_digest(plan):
    body = json.dumps(plan, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(body.encode("utf-8")).hexdigest()
```

- [ ] 增加下载配置含 authorized=true、--yes 缺少显式能力、非法 project-id、home/root 目标、stdin EOF 和未知选项测试；每项要求明确退出码且无写入。
- [ ] 测试通过并自查 diff 后，按明确文件提交本任务，不推送。

### Task 2: 受管写入、幂等和恢复

**关联：** BOOT-03-CHANGED、BOOT-04-RETRY；OpenSpec 2.3。
**Files:** 创建 storage.py、tests/test_bootstrap_storage.py。
**Interfaces:** safe_path(root, rel) -> Path；fingerprint(path) -> str or None；apply_files(root, changes: list, run_id: str) -> dict；resume_run(root, run_id, consent) -> dict。
change 为 {path, before_sha256, content}；事务只管理该批文件，不递归清理目标目录。

- [ ] 写失败测试：生成 plan 后改动 AGENTS.md；apply_files 必须拒绝且保留内容。

```python
p = root / "AGENTS.md"
p.write_text("before")
expected = fingerprint(p)
p.write_text("user edit")
with self.assertRaises(ValueError):
    apply_files(root, [{"path": "AGENTS.md", "before_sha256": expected,
                        "content": "generated"}], "run-1")
self.assertEqual(p.read_text(), "user edit")
```

- [ ] 运行本文件测试并记录有效失败。
- [ ] 实现写入前逐组件 lstat/边界重验；拒绝符号链接。临时文件同目录创建，flush/fsync 后 os.replace；所有临时文件归属写入事务。
- [ ] 使用独占锁记录拥有者与 run-id；锁冲突不删除对方锁。成功写入逐项记录目标 hash，失败留下已完成/未完成清单。
- [ ] 实现相同内容 no-op、恢复重验和权限 0600 的本地状态；不得只因 journal 声称完成就跳过内容核对。
- [ ] 测试每个写入边界注入失败、锁竞争、取消后恢复、用户改动、链接替换、路径 ../、绝对路径、损坏日志、重复运行。
- [ ] 回归通过后提交。

### Task 3: 工程生成与 new 审批门禁

**关联：** BOOT-01-NEW、BOOT-02-ROOT、MOD-03-EMPTY、MAP-03；OpenSpec 2.4–2.5。
**Files:** 修改 cli.py/config.py；创建 tests/test_bootstrap_generation.py；使用现有 templates/project 和 templates/module-AGENTS.md。
**Interfaces:** generation_changes(root, config, distribution: Path) -> list，输出任务 2 的 changes；approval_check(artifacts: dict, confirmed_hashes: dict) -> list 返回未满足门禁。

- [ ] 写失败测试，确认批准字段不能跳过缺失设计：

```python
missing = approval_check({"design": None, "plan": None}, {})
self.assertIn("design", missing)
self.assertIn("plan", missing)
```

- [ ] 运行测试证明尚未实现门禁。
- [ ] 按发布 manifest 复制公共包并验 hash，保持其内部结构；拒绝 symlink、gitlink、未列入清单文件；排除 .git/本机状态。目标不能是分发源或其父目录。
- [ ] 生成根 AGENTS、project identity、五份项目资料与 local-state 记录；已有不同内容只列冲突。明确重算到 .agent-framework 的引用。
- [ ] new 没有已确认需求/设计/计划时仅展示规划路径及待确认状态；保存规划是独立明确动作。批准 hash 必须与本次展示产物一致。空模块不调用 CodeGraph。
- [ ] 使用 OpenSpec 适配运行 init --tools none 和 context 检查；写 change 使用 CLI scaffold，不手工假造元数据；实际 root 与目标不符即停。
- [ ] 测试上级存在 OpenSpec、现有 config/store 指针、设计修改使批准失效、已有用户 AGENTS、零模块和中文路径。
- [ ] 回归通过后提交。

### Task 4: 模块 clone/add/sync

**关联：** MOD-01/02/03；OpenSpec 3.1–3.3。
**Files:** 创建 modules.py、tests/test_bootstrap_modules.py；修改 cli.py。
**Interfaces:** discover(root, discovery_roots: list, max_depth: int) -> list；catalog_update(previous: dict, declarations: list, observations: list) -> dict。candidate 含 path、git_root、agents、descriptor；catalog 分别含 modules/repos/indexes。

- [ ] 写失败测试：声明两个同仓模块和一个独立仓库，验证三个 module-id、两个 repo-id/index-id，缺失模块仍保留记录：

```python
result = catalog_update({}, declarations, observations)
self.assertEqual(len(result["modules"]), 3)
self.assertEqual(len(result["indexes"]), 2)
after = catalog_update(result, declarations, [])
self.assertTrue(all(m["presence"] == "missing" for m in after["modules"].values()))
```

- [ ] fixture 固定三个 module-id 为 a、b、c；a/b 同仓，c 独立仓。空 observations 模拟三个目录全部消失；另用只少 c 的 observations 验证仅 c 为 missing。
- [ ] 运行失败测试，再实现有界 os.walk；不跟随链接，不执行模块配置。Git root/HEAD/status 使用 subprocess argv，禁止把外层仓库当子仓库。
- [ ] module add 让用户确认无 Git 模块身份，生成项目侧描述；sync 不启动 Agent，只更新观察/过期状态。
- [ ] clone 使用受控 argv，禁用模板 hook、递归子模块和危险协议；默认支持 https/ssh 与明确指定本地 fixture 来源，不允许 ext::。拒绝 URL 密码，日志脱敏；目标存在非空时拒绝。
- [ ] 稳定身份以登记 ID 为准，路径移动只接受显式声明或可靠描述符；冲突返回 3。目录丢失保留 missing；不直接清除关系。
- [ ] 测试 ZIP 目录、模块移动、重复 ID、嵌套仓库、worktree .git 文件、外部链接、clone 中断及凭据 URL。
- [ ] 回归通过后提交。

### Task 5: 受控外部工具和 CodeGraph

**关联：** CG-01、BOOT-03；OpenSpec 4.1–4.2。
**Files:** 创建 process.py/adapters.py、tests/test_bootstrap_adapters.py、tests/integration/test_codegraph_live.py。
**Interfaces:** run(argv: list, cwd: Path, timeout: int, env: dict, stdin: str="") -> dict；ensure_index(index: dict, consent: set, runner) -> dict。run 返回 exit_code/stdout/stderr/timed_out；测试注入 FakeRunner。

- [ ] 写失败测试：同 index-id 不重复 init，超时和缺工具不记 READY。

```python
runner = FakeRunner([{"exit_code": 127, "stdout": "", "stderr": "missing"}])
result = ensure_index({"id": "i1", "root": root}, {"index"}, runner)
self.assertNotEqual(result["status"], "READY")
self.assertFalse(result["verified"])
```

- [ ] 在该测试文件中定义受控执行器；未预期调用直接失败：

```python
class FakeRunner:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def __call__(self, argv, cwd, timeout, env, stdin=""):
        self.calls.append((list(argv), str(cwd), timeout))
        if not self.responses:
            raise AssertionError("Unexpected external command")
        return self.responses.pop(0)
```
- [ ] 实现进程组超时和取消，仅终止自己启动的进程；输出大小上限与日志脱敏，不用 shell=True。
- [ ] 阅读目标版本 CodeGraph init/install/status 实现与 help，列出副作用；在临时 fixture 运行并比较文件/配置/进程变化。不能限制到已授权范围则停止并报告，不编造参数。
- [ ] 将 capability 与调用绑定；明确禁用隐式下载，默认不自动修复全局工具。安装仅在该版本已验证的项目级方式中提供选项，否则报告依赖缺口。
- [ ] 对有支持源码的每个 index-id：状态 → init 或 sync → 状态与代表性 query；记录排除范围、HEAD 与未提交源码 hash。
- [ ] live fixture 写入 Python 函数 alpha 调 beta；真实查询必须包含两者及关系，改代码后验证刷新；无源码记 NOT_APPLICABLE。
- [ ] stub 测试与 live 证据分别保存，全部通过后提交。

### Task 6: 钩子、任务入口与更新状态

**关联：** CG-02/03；OpenSpec 4.3–4.4。
**Files:** 创建 hooks.py、tests/test_bootstrap_hooks.py；修改 cli.py。
**Interfaces:** hook_plan(repo: Path, project: Path, runner) -> dict；mark_dirty(root: Path, worktree_id: str, reason: str) -> None。
hook_plan 只读；受管 hook 通过任务 2 的文件机制安装，但需额外核对 hook 路径授权。

- [ ] 写失败测试：已有任意 hook 不改变，返回冲突：

```python
hook.write_text("#!/bin/sh\nexit 0\n")
before = hook.read_bytes()
plan = hook_plan(repo, project, runner)
self.assertEqual(plan["status"], "HOOK_CONFLICT")
self.assertEqual(hook.read_bytes(), before)
```

- [ ] 运行失败测试，再实现 git rev-parse --git-path hooks、git-common-dir、工作树根检测；外置/共享路径未授权则拒绝安装。
- [ ] 支持不存在的 hook 和框架自身完整拥有的 hook；不向任意脚本末尾追加。hook 只调用固定受管 dispatcher，不接受仓库文本提供的命令。
- [ ] dispatcher 在当前工作树记录 dirty reason 并合并事件；不调用模型、不修改项目 Markdown、不自动提交；故障不阻断 Git，但留下诊断。
- [ ] 任务入口及收尾对源码 hash 和地图证据进行复核；普通 clone 与未提交修改都被发现，已有 watcher 可用则复用。
- [ ] 测试 worktree 共享 hook、不同 cwd、连续事件、PATH 无 Python/框架被移动、索引失败及已有 hook 内容不变。
- [ ] 回归通过后提交。

### Task 7: 真实 Agent、关系证据和文档

**关联：** MAP-01/02/03/04；OpenSpec 5.1–5.5。
**Files:** 修改 adapters.py；创建 maps.py、skill/project-bootstrap/SKILL.md、tests/test_bootstrap_maps.py、tests/integration/test_codex_live.py。
**Interfaces:** analyze(root, modules: list, consent: set, runner) -> dict；validate_map(root, catalog: dict, result: dict) -> list；render_map(result: dict) -> str。
输出 module_summaries、relationships、uncertainties；Agent 不指定任意文件写入路径。

- [ ] 写失败测试：静态输出不能声称运行通过，过期证据不能发布：

```python
errors = validate_map(root, catalog, {
    "relationships": [{"from": "a", "to": "b",
                       "provenance": "STATIC_SUPPORTED",
                       "runtime_validation": "VERIFIED",
                       "evidence": []}]})
self.assertTrue(errors)
```

- [ ] 实现结构与长度限制、闭集关系类型、模块存在检查、相对证据路径和 hash 检查；删除/修改的源码使证据失效。
- [ ] 实现 Codex 能力检查，实际 exec 参数由 help 确认；分析使用 read-only、ephemeral、明确工作目录及输出 schema，不使用 bypass 权限选项。认证失败或损坏入口返回 WAITING_AGENT。
- [ ] 配置禁用无关 MCP/插件自动启动，仅在有源码发送授权时调用；如果不能保证权限/范围，拒绝该适配而非用 prompt 冒充隔离。
- [ ] 在 writing-skills 规则下创建技能：先基线决策测试，覆盖空库、未批准 new、未知连接、恶意 README；再加指引并复测。宿主要求的项目发现方式经验证后才登记为支持。
- [ ] Agent 结果由生成器写项目地图；已有模块 AGENTS 不覆盖，只读第三方模块生成项目侧入口；图表从同一 JSON 渲染。
- [ ] 合成三模块有已知真值连接和一个同名但无关系的符号：真实 Codex 输出应包含有证据连接，不把同名符号当已连接；检查运行状态仍 NOT_RUN。
- [ ] 新设计 A-B 而代码 A-C 时输出 SPEC_MISMATCH，人工 architecture.md 不变。
- [ ] stub 与 live 验证、技能决策复评通过后提交。

### Task 8: 只读 doctor 和流程编排

**关联：** READY-01/02、BOOT-04；OpenSpec 6.1。
**Files:** 创建 readiness.py、tests/test_bootstrap_readiness.py；修改 cli.py。
**Interfaces:** inspect_project(root: Path) -> dict。读取受管状态及当前 hash；不调用有副作用的 CLI，也不更新 checked_at 文件。

- [ ] 写失败测试，未运行 Agent 的工程必须 WAITING_AGENT：

```python
before = snapshot(root)
report = inspect_project(root)
self.assertEqual(report["agent"]["status"], "WAITING_AGENT")
self.assertEqual(snapshot(root), before)
```

- [ ] snapshot 在测试中定义为相对文件名到 SHA256 的映射，拒绝链接；不包含测试进程自己的日志。
- [ ] 实现 capability 独立状态、next_actions、导航/运行分离；无代码只记 scaffold readiness。
- [ ] init/new/module add 串联可执行步骤，失败逐项记录；resume 重新核对权限与输入，不能直接重放序列化命令。
- [ ] 测试索引失败+Agent 成功、地图过期、缺框架、损坏 JSON、无人值守 EOF、用户取消，以及 doctor 不启动网络/守护进程。
- [ ] 回归通过后提交。

### Task 9: 两条完整演练、文档与发布

**关联：** 全部 Req/Scenario、READY-02-RELEASE；OpenSpec 6.2–6.5。
**Files:** 修改 AGENTS.md、docs/framework 四份公共规则、onboarding/integrations/acceptance、templates、README、CHANGELOG、framework-manifest.json、tools/check-framework、.github/workflows/validate.yml；创建 docs/bootstrap.md 和合成端到端测试。

- [ ] 为 init 建立三模块 fixture，为 new 建立批准需求/设计/计划 fixture；默认测试使用 FakeRunner，无网络，不访问用户真实凭据。
- [ ] 编写入口层集成测试代码：

```python
result = subprocess.run([sys.executable, str(cli), "doctor", "--target", str(root)],
                        text=True, capture_output=True, timeout=30)
report = json.loads(result.stdout)
self.assertIn(report["status"], {"READY", "PARTIAL", "WAITING_AGENT", "BLOCKED"})
self.assertEqual(snapshot(root), before)
```

- [ ] 已有工程演练：从干净分发副本 init → clone/add → 真实索引 → 真实 Agent → 地图 → 合成服务请求验证 → 修改接口 → 增量检查。
- [ ] 新需求演练：无目录 → new 先停设计门禁 → 明确确认 fixture 设计/计划 → 骨架 → 有效失败测试 → 最小任务管理功能 → 单测/端到端 → 实际地图与设计对照。
- [ ] 两条演练都运行第二次，检查幂等；再做取消恢复、路径逃逸、hook 冲突、模块 missing 和 CLI 缺失。
- [ ] 文档只描述已实现能力；新增自动化例外不放宽只读、知识摄入、远程发布和设备边界。模板及 skill 所需链接全部可达。
- [ ] 分发检查新增 openspec 规划根支持，技能数量从 manifest 验证实际入口而非硬编码 21；JSON manifest 使用确定性 hash，无业务或本机数据。新增规划文件也纳入发布文件清单。
- [ ] 本地运行：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 tools/check-framework
openspec validate add-project-bootstrap-and-maps --strict
git diff --check
```

- [ ] 独立评审在宿主支持且按技能获授权时执行；否则明确自查，不能冒充。重要问题修复后重跑相关测试。
- [ ] 发布前输出完成矩阵、真实工具证据与未运行项，确认不存在必须通过却缺证据的项；不为通过而修改规格。
- [ ] 明确 stage 公共文件，提交，推 HEAD:refs/heads/main 至已确认公共远程；不 force、不推其他 refs。等 Linux/macOS CI 完成，核对远程 SHA、文件清单和只有 main。
- [ ] CI 失败则修复并重跑；真实环境失败则保持未完成并如实说明，不发布“完整可用”的结论。最终记录工程位置及证据路径。

## 自查与场景覆盖

| 场景 | 计划任务 |
|---|---|
| BOOT-01-INIT | 1、2 |
| BOOT-01-NEW、BOOT-02-ROOT | 3 |
| BOOT-03-CONSENT | 1、5、7 |
| BOOT-03-CHANGED、BOOT-04-RETRY | 2、8 |
| MOD-01-IMPORT、MOD-01-ESCAPE、MOD-02-IDENTITY、MOD-03-MOVE | 4 |
| MOD-03-EMPTY | 3、8 |
| CG-01-INDEX、CG-01-TOOL | 5 |
| CG-02-HOOK、CG-02-EVENT、CG-03-STALE | 6 |
| MAP-01-AGENT、MAP-01-MISSING | 7 |
| MAP-02-RELATION、MAP-02-DESIGN、MAP-03-DOCS、MAP-04-UNTRUSTED | 7 |
| READY-01-REPORT、READY-01-NO_CODE、READY-02-READONLY | 8 |
| READY-02-RELEASE | 9 |

每个测试文件都先证明有效失败，再实现；缺工具/缺环境不计行为 RED。
宏观 tasks 只在其全部规定行为与验证完成后勾选，不因计划存在勾选实现。
执行方式建议 Native：主 Agent 顺序实现各任务，最后独立评审；减少共享接口并行冲突。
