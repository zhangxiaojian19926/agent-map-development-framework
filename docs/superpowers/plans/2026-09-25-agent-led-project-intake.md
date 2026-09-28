# Agent 主导的命名模块初始化 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans for native execution, or superpowers:subagent-driven-development if the user selects it. Steps use checkbox (`- [ ]`) syntax for tracking. 本计划需要用户审阅并选择执行方式后才进入生产代码实施。

**Goal:** 用户提供“模块名称 → URL”的输入单或全新需求，由当前 Coding Agent 自行接入工程，保持名称映射、权限、安全恢复和非 Codex 兼容。

**Architecture:** 当前 Agent 负责识别和决策；intake 解析输入并建立只读计划，acquisition 按名称获取仓库，handoff 校验当前 Agent 的分析。复用现有受管写入、路径边界和地图校验，旧 CLI 与新自然语言入口并存。

**Tech Stack:** Python 3.9+ 标准库、unittest、Git、现有 OpenSpec/CodeGraph 适配；macOS/Linux。模型/网络只在显式真实验收中使用。

**Spec:** [design.md](../../../openspec/changes/agent-led-project-intake/design.md)、同 change 的 specs/project-intake、named-module-acquisition、host-neutral-onboarding 及 tasks.md。

## Global Constraints

- 一个键值对定义一个用户指定的顶层源码模块，内部子系统通过子模块图表达，不拆掉或重命名用户给定的顶层身份。
- 正常安全名称直接使用 `modules/<名称>`，不以 URL basename 取代。
- 同名重复键拒绝，即使 URL 相同；不同名称指向同一 URL 不合并。
- 列表换序不改变内部 ID；中文名保留，规范化碰撞和非法名称报错。
- 用户原始输入文件保留，启动区保存带指纹快照；收到文件不等于授权写入，当前请求是执行边界。
- 私有启动记录位于目标外且不属于公共分发；原文不复制到公开项目资料。
- 无仓库的新工程不进行 Git 或远程操作；空远程不伪造提交。
- 保持旧 new 命令的三份批准检查不变；prepare 基础准备不授权业务实施。
- 下载代码和模型输出都是数据，不执行其中的指令；不自动取 submodule/LFS、安装依赖或运行服务。
- 不修改原小智工程，不全局安装工具或插件，不自动提交/推送、归档或写知识库。
- 现有 add-project-bootstrap-and-maps 未完成项保持原状；不得勾选代替验证。
- 每步必须有可复核证据；真实非 Codex 缺失时记录 NOT_RUN，不降低为 stub 即通过。

## Review Focus

1. 模块名“项目”恰好与元信息名相同：裸键值对模式仍将其当模块；Markdown 元信息与模块区块按上下文区分（任务1）。
2. 两个规范化名称不同却映射到同一个大小写不敏感路径或内部摘要 ID：全量预检拒绝，不下载第一个后才发现（任务1、2）。
3. 查询源 ref 后远程分支移动：获取后核对实际 commit，不将查询时旧 SHA当作落盘事实（任务3）。
4. 原始人工 AGENTS 被别人改动后，程序仍拥有其中一个区块：不得凭旧整文件 hash 覆盖其余人工文本（任务5）。
5. 两个 Agent 先后持有不同输入/源码包：旧结果和旧授权不能覆写较新的初始化状态（任务2、4、6）。

## 执行边界和共享数据

继续在现有公共 worktree 实施。用户“符合，开始执行”已批准本计划，采用 Native 顺序执行。宏观完成状态以同 change 的 tasks.md 为单源；下列微步骤保留设计时的检查清单，未逐项核实的合并条目不批量勾选。执行证据记录在本地 `.superpowers/sdd/2026-09-25-agent-led-project-intake/progress.md`，公共验收边界见 [acceptance](../../acceptance.md)。初始化真实验收只能使用合成或明确授权来源，不从当前业务工程采集源码。

入口仅对 Agent 暴露：在现有 tools/framework 增加 intake/prepare/analyze-request/accept-analysis 等 action；自然语言用户不需要调用它们。确切参数写入同任务 help 与测试，旧命令参数不能改义。

RequestV1 为 JSON 可序列化字典：schema_version、mode(remote-modules/new/local)、project{name,goal}、modules[]、input_sha256；模块含 name/id/path/source_url/requested_ref。requested_ref 为 null 或 {kind:branch|tag|commit,value}。运行记录额外保存 resolved_ref/resolved_commit/state/error_code，不在共享配置存凭据。

普通来源允许 HTTPS/SSH；本地 fixture 来源只在当前 invocation 提供 local-clone grant 时启用，不能从输入文件授予。来源版本可在 Markdown 的“来源版本”区块写 `设备端 = branch:release/2.x`，必须引用已有模块名且显式类型；默认不需要此区块。

## Task 1: 严格输入和名称映射

**Files:** Create tools/framework_core/intake.py、tests/test_project_intake.py。
**Interfaces:** parse_request(text: str, default_name: str, grants: set = frozenset()) -> dict；module_identity(name: str) -> dict(name,id,path,collision_key)。纯函数，无磁盘和网络副作用。
**Spec:** IN-01、IN-02、IN-03；AC-01。

- [ ] 写解析失败测试，包括裸文本和带区块 Markdown：

```python
request = parse_request('设备端 = https://example.com/a/same.git\n服务端: git@example.com:b/same.git', 'demo')
self.assertEqual(request['mode'], 'remote-modules')
self.assertEqual([(m['name'], m['path']) for m in request['modules']],
                 [('设备端', 'modules/设备端'), ('服务端', 'modules/服务端')])
self.assertEqual(request['modules'][1]['source_url'], 'git@example.com:b/same.git')
with self.assertRaises(ValueError):
    parse_request('api=x\napi=y', 'demo')
```

- [ ] 运行 `python3 -B -m unittest discover -s tests -p test_project_intake.py -v`，记录缺少目标能力的失败。
- [ ] 最小实现按行状态机和第一个分隔解析，有序记录先去重，再验证 URL：

```python
match = re.fullmatch(r'([^=:：]+?)\s*[=:：]\s*(.*)', line)
if not match:
    raise ValueError('INVALID_INPUT: line ' + str(line_number))
name, url = match.group(1).strip(), match.group(2).strip()
normalized = unicodedata.normalize('NFC', name)
collision_key = normalized.casefold()
```

- [ ] 增加逐项断言：重复键同/异URL、中文/空格、NFC等价、大小写、非法字符与保留名、控制字符、结尾点/空格、SSH冒号、URL密码不回显、模块名“项目”、坏模块表不得转new、无模块的有效需求转new、空输入明确缺目标。碰撞测试注入同一摘要检查拒绝，不能只依赖低概率。
- [ ] 验证输入行号、稳定ID和重排不变；解析错误不得先产生输出文件或runner调用。自查后只登记任务2.1/2.2/2.4适用结果，提交按当前授权另行处理。

## Task 2: 私有启动计划、指纹与恢复绑定

**Files:** Modify intake.py、cli.py、config.py；Test tests/test_project_intake.py、tests/test_bootstrap_config.py。
**Interfaces:** plan_intake(request: dict, target: Path, staging: Path, distribution: Path) -> dict；save_intake(plan: dict, original_text: str, grants: set) -> dict。调用现有 safe_path/project_lock/atomic，计划阶段不得写锁。
**Spec:** IN-04；AC-03-CONFLICT；HN-04-RESUME。

- [ ] 写失败测试：

```python
with tempfile.TemporaryDirectory() as d:
    base = Path(d).resolve()
    before = sorted(base.rglob('*'))
    plan = plan_intake(parse_request('项目 = https://example.com/a.git', 'demo'),
                       base / 'project', base / 'launch', distribution)
    self.assertEqual(sorted(base.rglob('*')), before)
    with self.assertRaises(ValueError):
        save_intake(plan, '项目 = https://example.com/a.git', set())
    self.assertFalse((base / 'launch').exists())
```

- [ ] 运行两个关联测试文件，确认缺少计划/授权边界失败；不用真实网络。
- [ ] 实现目标/启动区/分发根的规范路径互斥、原文SHA和计划指纹；拒绝工作区外目标、符号链接、启动区在clone目标内、分发源覆盖。所有模块静态冲突一次预检。保存原文前必须完成秘密URL拒绝：

```python
if 'write' not in grants:
    raise ValueError('CONSENT_REQUIRED: write')
if hashlib.sha256(original_text.encode('utf-8')).hexdigest() != plan['input_sha256']:
    raise ValueError('STALE_INPUT')
with project_lock(staging):
    atomic(staging, 'request.json', encoded(plan['request']))
    atomic(staging, 'PROJECT-START.md', original_text)
```

- [ ] 在保存前后插入故障验证原子文件与已完成状态；两个会话不同输入的指纹必须冲突；恢复不能从saved approved/grants恢复权限。恢复前读取绑定目标，不要求用户记run-id。
- [ ] 加入 Agent 内部 intake --request/--staging/--target/--dry-run 参数与json结果。预览、缺权限、输入坏行分别验证零写和明确退出结果；按任务2.3/3.4核对，保留原始输入不移动不删除。

## Task 3: 命名仓库获取、源版本和模块级恢复

**Files:** Create tools/framework_core/acquisition.py、tests/test_module_acquisition.py；Modify adapters.py、modules.py。
**Interfaces:** resolve_source(module: dict, grants: set, runner=run, auth=None) -> dict；acquire_modules(plan: dict, grants: set, runner=run, auth=None) -> dict。auth 仅来自当前宿主调用，不能从启动单/README读取；无安全适配时AUTH_REQUIRED。
**Spec:** AC-01、AC-02、AC-03、AC-04。

- [ ] 建两个独立临时Git fixture，分别在不同父目录使用相同basename；写测试校验中文模块目录、remote、实际HEAD，并用故障runner让第二模块失败：

```python
report = acquire_modules(plan, {'write', 'clone', 'local-clone'}, runner)
self.assertEqual(report['status'], 'PARTIAL')
self.assertEqual(report['modules'][first_id]['state'], 'REGISTERED')
self.assertEqual(report['modules'][second_id]['state'], 'FAILED')
before = recovered_runner.clone_count.get(first_id, 0)
resumed = acquire_modules(plan, {'write', 'clone', 'local-clone'}, recovered_runner)
self.assertEqual(resumed['status'], 'COMPLETE')
self.assertEqual(recovered_runner.clone_count.get(first_id, 0), before)
self.assertEqual(resumed['modules'][second_id]['state'], 'REGISTERED')
```

测试runner必须记录所有argv，成功路径另以真实本地Git验收；不得仅让fake固定返回成功就算下载验证。

- [ ] 运行 `python3 -B -m unittest discover -s tests -p test_module_acquisition.py -v`，先确认有效失败。
- [ ] 最小实现先记录PENDING/FETCHING，调用隔离Git查询再获取；命令只用argv：

```python
result = runner(['git', 'ls-remote', '--symref', '--', source_url, 'HEAD'],
                staging, 30, safe_git_env)
if result['exit_code'] != 0:
    return {'state': 'FAILED', 'error_code': 'SOURCE_UNAVAILABLE'}
```

上述输出为空不足以证明空仓库：需再查询完整refs。查询失败与无refs分开；查询有refs但HEAD无效为REF_UNRESOLVED。branch/tag/commit分别解析；显式commit按可获取性校验。获取后再次读取实际HEAD，与请求约束及源快照比较，分支移动记录SOURCE_MOVED，不发布错误SHA。

- [ ] 保留现有禁hooks/template/ext协议原则，设置LFS不自动下载；获取新目标与已有目标检查分开。已有记录匹配且文件未被破坏才跳过，来源改动、人工目录、缺Git根、未完成clone状态不得覆盖。继续其他独立模块，汇总全部结果；不自动删除任何失败目录。
- [ ] 认证测试：不从仓库/全局配置加载任意helper；对宿主明确选择、路径已验证的认证适配单独允许，不使用含秘密URL，不回显凭据。测试无适配为AUTH_REQUIRED；有受控helper或SSH-agent适配时，仅授予该链路，不恢复任意配置。不支持的认证方式报告而非自行安装。
- [ ] 加真实测试：非main默认、branch/tag/commit、缺ref、空仓库、远程移动、同URL不同名、source改变、用户改动、恶意安装脚本/submodule未执行、第二模块失败恢复。重新运行原adapter/module测试，按任务3.1–3.4与全部AC场景核对。

## Task 4: 当前 Agent 分析与跨宿主结果接收

**Files:** Create tools/framework_core/handoff.py、tests/test_agent_handoff.py；Modify cli.py、workflow.py、readiness.py、config.py。
**Interfaces:** make_analysis_request(root: Path, catalog: dict, grants: set) -> dict；accept_analysis(root: Path, envelope: dict, grants: set) -> dict。envelope={request_id,source_digest,result}；result复用现有地图schema。生成/接收阶段使用当前写入授权及源码访问范围，不从envelope获取授权。
**Spec:** HN-01、HN-02、HN-04-RESUME。

- [ ] 写缺codex PATH测试，runner在任何argv包含codex时失败；以真实源码生成证据：

```python
packet = make_analysis_request(root, catalog, {'write', 'agent'})
envelope = {'request_id': packet['request_id'],
            'source_digest': packet['source_digest'], 'result': valid_result}
report = accept_analysis(root, envelope, {'write', 'agent'})
self.assertEqual(report['agent']['execution'], 'current-session')
self.assertEqual(report['runtime'], 'NOT_RUN')
```

- [ ] 运行 `python3 -B -m unittest discover -s tests -p test_agent_handoff.py -v`，记录失败。
- [ ] 实现只读取授权模块的有界观察包；绑定request/source hash，结果发布前重验源码和请求有效性，再复用validate_map/map_outputs/owned_changes：

```python
if envelope['request_id'] != current_request['request_id']:
    raise ValueError('STALE_REQUEST')
if envelope['source_digest'] != digest(current_sources):
    raise ValueError('STALE_SOURCE')
errors = validate_map(root, catalog, envelope['result'])
if errors:
    raise ValueError('INVALID_EVIDENCE: ' + ','.join(errors))
```

- [ ] 验证空模块摘要、未知模块、越界证据、错误anchor/hash、runtime=VERIFIED、伪造approved、超预算、源码修改、旧请求和撤销权限均不覆盖旧地图。文档说明host标签不是认证证明，current-session不能生成假Codex版本记录。
- [ ] 新增内部analyze-request与accept-analysis参数，返回宿主下一步提示；外部Codex路径保持独立。换宿主只读检查状态后重新授予当前所需范围，任务4.1通过后再集成任务6。

## Task 5: 基础 prepare、已有规则接入与分层诊断

**Files:** Modify generation.py、config.py、cli.py、workflow.py、readiness.py；Test tests/test_bootstrap_generation.py、tests/test_bootstrap_config.py、tests/test_bootstrap_readiness.py。
**Interfaces:** generation_changes(root, config, distribution, prepare=False) -> list；inspect_project(root) -> dict保留旧字段并新增onboarding/development层，不使旧调用成功含义变更。
**Spec:** IN-03、HN-03。

- [ ] 写subprocess失败测试：

```python
result = invoke('prepare', '--target', root, '--project-id', 'demo',
                '--agent', 'current', '--yes', '--allow', 'write')
self.assertEqual(result.returncode, 0, result.stdout)
self.assertEqual(json.loads(result.stdout)['onboarding'], 'PREPARED')
self.assertFalse((root / '.git').exists())
self.assertFalse((root / 'taskcli').exists())
old = invoke('new', '--target', other, '--project-id', 'demo',
             '--agent', 'manual', '--yes', '--allow', 'write')
self.assertEqual(old.returncode, 3)
```

- [ ] 运行这三个文件对应测试，确认prepare能力缺失的失败，旧new门禁先保持通过。
- [ ] prepare只生成规则入口、项目身份和资料，不要求已批准设计；配置未有设计时architecture标题不能声称Approved。新增agent=current不触发codex分析；只有用户授权OpenSpec时建立本地根，未配置不伪造change。
- [ ] 人工AGENTS采用明确受管边界，写入前核对整文件指纹；默认仅追加无冲突块并保留原字节：

```python
begin, end = '<!-- FRAMEWORK_ENTRY_START -->', '<!-- FRAMEWORK_ENTRY_END -->'
if begin in text or end in text:
    raise ValueError('RULE_CONFLICT: inspect existing managed block')
updated = text + '\n\n' + begin + '\n' + entry + '\n' + end + '\n'
```

已有受管块更新必须验证其归属和完整边界；人工改动区块、嵌套/重复标记都保留原文并冲突。不根据“有标记”推断拥有整文件。语义冲突由当前Agent报告，程序不自动融合规则。

- [ ] 测试人工正文与未提交源码字节不变、并发修改拒绝、损坏标记、相对链接到真实docs/project而非模板、空工程无索引N/A、缺增强工具不伪造全READY、业务runtime始终独立。
- [ ] 重跑旧生成/配置/诊断回归，任务4.2–4.4和HN-03三个场景分别登记证据，不将prepare成功解释为业务实施批准。

## Task 6: 统一 Agent 编排与两条确定性全流程

**Files:** Modify intake.py、cli.py、workflow.py、modules.py、tests/test_bootstrap_end_to_end.py。
**Interfaces:** execute_intake(plan: dict, grants: set, runner=run) -> dict；输入任务2的计划，调用任务3获取及任务5准备，需要分析时返回任务4交接提示。
**Spec:** 所有IN/AC，HN-01-NONCODEX、HN-03-EMPTY/HUMAN、HN-04-RESUME。

- [ ] 写远程模块fixture与无URL需求两条失败测试；输入不附带执行JSON或审批hash，只有启动单和当前授权。验证keys对应Git根、目标内不混入启动单，且缺第三方工具能报告降级。
- [ ] 运行 `python3 -B -m unittest discover -s tests -p test_bootstrap_end_to_end.py -v` 记录失败。
- [ ] 最小编排顺序：

```python
if plan['request']['mode'] == 'remote-modules':
    acquisition = acquire_modules(plan, grants, runner)
    if acquisition['status'] != 'COMPLETE':
        return acquisition
return {'status': 'PREPARED', 'next_action': 'analyze-request'}
```

实际prepare在已验证目标作用域内调用generation_changes并应用；部分模块失败可以保存明确部分目录，但不能注册为全体成功。已有本地工程分支不clone、不移动源码，读取目标Git边界及已有声明。

- [ ] 全操作计划锁/指纹交接保留；长分析过程返回当前Agent后释放执行锁，接收时重新核对，不能只靠初始锁。测试两个不同输入会话交错、取消恢复、普通clone新候选不得自动启用。
- [ ] 运行全部测试并逐项核对用户步骤为零；明确哪些是机器内部授权参数、哪些是用户真正提供的业务决定，不通过测试脚本偷偷替用户选择全部模块/起点。

## Task 7: 通用入口、模板、技能和用户文档

**Files:** Create BOOTSTRAP.md、templates/PROJECT-START.md、docs/project-intake.md、tests/integration/intake-prompts.md；Modify AGENTS.md、README.md、docs/bootstrap.md、docs/onboarding.md、docs/integrations.md、docs/framework/development-workflow.md、docs/framework/collaboration-policy.md、docs/framework/skill-policy.md、skill/project-bootstrap/SKILL.md、docs/acceptance.md、tools/check-framework。
**Interfaces:** BOOTSTRAP为跨宿主单一流程；宿主快捷入口只引用它，不复制第二套流程；技能说明与CLI help一致。
**Spec:** HN-01、HN-03、HN-04；全部输入使用契约。

- [ ] 在check-framework相关测试中先加入入口/模板存在、必要相对引用、分发排除私有输入的失败断言；技能修改前完整读取writing-skills及所需测试指导，按其允许方式测试，而非直接编辑后宣称有效。
- [ ] 模板直接提供如下二选一内容，未知值不能作为真实项目输入自动执行：

```text
# 工程启动单
## 模块仓库
设备端 = https://example.com/team/device.git
服务端 = https://example.com/team/service.git

# 新工程使用另一份独立输入，不混用上面的示例模块
项目：家庭任务助手
目标：提供本地任务新增、列表和完成。
仓库：暂无
```

正式模板用清楚的分隔说明要求选一段，不将两种示例同时解析成一个可执行请求。BOOTSTRAP先明确框架源/输入/目标三者，再读请求、预览计划、按当前授权执行、处理返回的分析交接、验证和总结。能力不足返回具体缺口，不让纯聊天宿主假报完成。

- [ ] 文档自查逐文件：正常用户路径没有“请运行”、必填JSON、hash或init/new选择；高级CLI附录保留维护用途。非Codex不要求安装Codex；缺认证/写权限时只询问必要操作。
- [ ] 技能做无技能对照和正向任务，输入只含启动单与初始化意图；记录改善的实际行为，不把默认安全能力归功于技能。所有结果与权限边界按知识和开发公共规则处理。
- [ ] 相对链接与分发检查通过后记录任务5.1/5.2；按当前授权决定本地提交，不自动push。

## Task 8: 真实跨宿主验收、最终审查与分发

**Files:** Modify tools/verify-live、docs/acceptance.md、CHANGELOG.md、framework-manifest.json；使用tests/integration/intake-prompts.md。
**Interfaces:** verify-live保留现有调用，新验收显式选择宿主/场景；仅在allow-live下模型调用与合成代码执行，默认CI只运行离线测试。
**Spec:** HN-04-LIVE/RESUME；初版27 Scenario；本轮补充的8个Scenario另见Task 9–12。

- [ ] 写测试验证未授权真实验收不建目录、不调模型；非Codex适配缺失返回NOT_RUN，不回退为Codex或stub。执行测试观察失败，再加宿主选择与结果归档逻辑。
- [ ] 真实Codex接收以下原始提示，不预先生成执行配置/模块ID/hash：

```text
按指定公共框架的 BOOTSTRAP.md 初始化目标工程，输入在 PROJECT-START.md。
当前仅授权在指定验证工作区生成工程、从列出的合成来源获取源码、分析和检查。
不要安装全局工具、创建远程、推送、执行下载项目脚本或写知识库。
你需要自行识别路线、生成机器参数，最后给出逐模块结果和未验证项。
```

- [ ] 独立检查每个目标模块的实际Git根/remote/HEAD、原名映射、人工文件hash、输出图schema、退出/错误状态及全部进程调用。分别运行三模块来源和无URL新需求，失败不得仅通过修改测试预期变绿。
- [ ] 检查可用的真实非Codex宿主，不安装或伪造；使用同样输入和界限跑两条路线，再切换宿主恢复一次。无凭据/能力时保存具体阻塞与NOT_RUN，不标跨宿主通过。
- [ ] 全部原58回归及新增测试在macOS/Linux通过后，执行 `python3 -B tools/update-manifest`、`python3 -B tools/check-framework`、`openspec validate agent-led-project-intake --strict`、`git diff --check`；新增文档/规划纳入清单，私有输入和原始真实模型日志不入清单。
- [ ] 根据最终diff、文件清单与Scenario矩阵做新鲜审查。选择Native时由独立评审检查整批；选择Subagent-driven时逐任务独立审查再整批复核。核实评审实际可用/获准；只有自查则明确报告，不能冒充独立评审。
- [ ] 提交/推送/远程CI按当时用户明确授权执行；没有发布授权不沿用上轮上传意图。缺任何必要实测项保留宏观任务未完成，不归档成全通过。

## Scenario 覆盖矩阵

| 场景 | 实施任务 | 核心证据 |
|---|---|---|
| IN-01-PAIRS、IN-01-BARE | 1、6、8 | 精确name/URL/目录与零人工参数 |
| IN-02-DUP、IN-02-PATH | 1、2 | 全量拒绝、零网络/目标写入 |
| IN-03-NEW、IN-03-BROKEN | 1、5、6 | 新需求准备、坏表不降级 |
| IN-04-PERSIST、IN-04-READONLY | 2、6 | 外部启动区、输入指纹、当前权限 |
| AC-01-NAMES、AC-01-REORDER | 1、3 | 实际Git来源、稳定ID与命名目录 |
| AC-02-DEFAULT、AC-02-MISSING | 3 | 真实refs、缺ref不回退 |
| AC-02-EMPTY、AC-02-AUTH | 3 | 查询证据、错误分类与脱敏 |
| AC-03-PARTIAL、AC-03-CONFLICT | 2、3、6 | 模块级结果、恢复调用计数与人工文件保留 |
| AC-04-UNTRUSTED、AC-04-CREDENTIALS | 3、8 | Git隔离、执行审计与认证测试 |
| HN-01-NONCODEX、HN-01-CHATONLY | 4、7、8 | 能力报告、真实非Codex轨迹 |
| HN-02-RESULT、HN-02-STALE | 4、6 | 结构/源码证据校验、拒绝旧结果 |
| HN-03-EMPTY、HN-03-LEGACY、HN-03-HUMAN | 5 | 分层结果、旧new门禁、人工文件保护 |
| HN-04-LIVE、HN-04-RESUME | 6、8 | 两种真实宿主、两种工程、跨宿主恢复 |

## 计划自查记录

初版12条Requirement、27个Scenario均已映射；本轮另增HN-05至HN-08共8个Scenario，映射见下文。三个初版组件的函数名和调用边界一致。微步骤未逐项核对时保留未勾选，宏观完成状态以change tasks.md为准，不将代码片段、既往测试或宿主名称当成本次验证结果。

现有详细文件清单仍以design D9为范围约束；本计划新增本文件与审批记录，不创建运行代码。推荐Native顺序执行，因为intake/acquisition/handoff共享同一输入与证据协议，先锁定接口可减少并行修改冲突；最后做独立审查。用户可选择Subagent-driven逐任务实现与审查。

## 2026-09-26 增量：从骨架到完整初始化

用户已确认四项方向；本轮补充以下实施细节供审阅，尚未执行。继续Native顺序执行，不重选宿主、不要求用户手工参数。旧94项通过只是9359ceb基线证据，不能勾选新增项。提交、推送、真实模型调用与业务执行仍按届时授权处理。

**新增约束：** 200000字节是每个v2序列化包预算；PREPARED不是COMPLETE；资料必须完整但不得伪造命令成功；人工内容不覆盖；只读模块使用等价项目侧入口；无源码用设计而非实际地图；KB未配置不建库。不能简单把业务审批标志保存在文件中就视为当前授权。

**增量Review Focus：** 单文件大于预算/单行过大；批间调用双方；分析中源码及框架版本变化；生成后人工修改；新增或消失模块留下旧COMPLETE。分别由Task 9、9、9、10、11覆盖。

### Task 9: 可恢复的v2分批协议（宏观7.1）

**Files:** Create tools/framework_core/analysis_batches.py、tests/test_analysis_batches.py；Modify handoff.py、cli.py、modules.py及tests/test_agent_handoff.py。路径均在tools/framework_core或tests下，不改全局工具。
**Interfaces:** `split_sources(sources: list[dict], max_bytes: int = 200000) -> list[dict]`，输入项为path/sha256/content，输出包含batch_id/slices，slice含path/file_sha256/start_line/end_line/content；`begin_analysis(root, catalog, grants) -> dict`产生会话清单；`read_batch(root, session_id, batch_id, grants) -> dict`；`accept_batch(root, session_id, batch_id, result, grants) -> dict`；`finalize_analysis(root, session_id, result, grants) -> dict`。均不启动模型。会话存本地状态，源码不重复持久化。

- [ ] 写首个预算/覆盖失败测试；fixture两模块分别为重复完整行，总量超过600KB，不依赖网络：

```python
sources = [dict(path='a/api.py', sha256='a'*64, content='x = 1\n'*60000),
           dict(path='b/client.py', sha256='b'*64, content='y = 2\n'*60000)]
batches = split_sources(sources)
self.assertGreater(len(batches), 3)
for batch in batches:
    self.assertLessEqual(len(json.dumps(batch, ensure_ascii=False).encode()), 200000)
for source in sources:
    slices = [s for b in batches for s in b['slices'] if s['path'] == source['path']]
    self.assertEqual(''.join(s['content'] for s in slices), source['content'])
```

- [ ] 运行 `python3 -B -m unittest discover -s tests -p test_analysis_batches.py -v`，确认缺分批能力的RED；实现稳定排序、完整行分片及实际JSON开销核算，单行过大抛FILE_SLICE_TOO_LARGE。使用真实文件hash构造后续会话fixture，上例假hash只用于无IO分片测试。
- [ ] 分别先写失败测试再实现会话状态：清单绑定catalog/source/framework；每个包由会话派生不能扩大路径；相同重传幂等、不同结果BATCH_CONFLICT；缺批finalize报INCOMPLETE_COVERAGE；新文件、删除、改动或manifest变化拒绝旧会话。授权缺失不得写状态或读取新包。
- [ ] 最终汇总复用validate_map两端证据检查，跨批关系指向原文件准确anchor/hash；全部批次通过后才一次调用map_outputs/受管事务。测试批次失败时旧地图字节不变，最终写入中断保留可恢复事务，不谎报成功。
- [ ] CLI增加仅供Agent使用的v2会话/批次参数，保留v1原行为。逐场景跑HN-06-LARGE/RESUME及旧handoff测试，记录GREEN。不要在每批完成后生成不完整正式地图。

### Task 10: 项目资料与完整模块入口（宏观7.2）

**Files:** Create tools/framework_core/project_docs.py、tests/test_project_docs.py；Modify generation.py、maps.py、handoff.py、analysis_batches.py及对应生成测试。
**Interfaces:** `validate_project_docs(root, catalog, dossier) -> list[str]`、`project_doc_outputs(root, catalog, dossier) -> dict[str,str]`。dossier包含project、modules；project必需goal/non_goals/architecture/interfaces/integration_order/constraints/resources，module必需id/purpose/non_responsibilities/entrypoints/inputs/outputs/dependencies/internal_roles/commands/limitations/knowledge。每项为value/provenance/evidence/status，status限KNOWN/NOT_VERIFIED/NOT_CONFIGURED/NOT_APPLICABLE，N/A须reason；引用复用path/anchor/sha256，设计引用批准规格且标DECLARED。未知阻塞项单列，不用编造内容凑字段。

- [ ] 用三个真实临时模块建立失败fixture：人工AGENTS内容含CRLF、只读模块缺AGENTS、可写模块缺AGENTS。逐字段删除dossier数据、填空白/模板占位、提供过期来源，验证拒绝且旧文件不变。最小否定断言：

```python
errors = validate_project_docs(root, catalog, {'project': {}, 'modules': []})
self.assertIn('INCOMPLETE_DOCUMENTATION', errors)
```

- [ ] 运行 `python3 -B -m unittest discover -s tests -p test_project_docs.py -v` 观察RED。实现schema及来源校验，再实现完整项目/模块正文；command记录工作目录、前提、来源、执行状态，不执行命令获取“通过”。保留原始启动输入私密性，只从明确允许公开的事实生成资料。
- [ ] 对人工AGENTS只添加获准且无冲突的受管局部区块；写前核对当前字节hash，人工正文不变。只读模块生成完整项目侧入口及原因；语义冲突生成交接缺项，不写模块，状态PARTIAL。已有人工项目文档不全文覆盖。
- [ ] 以真实输出校验段落内容、导航和引用，不以源码包含某字符串作为测试。将生成后人工修改再刷新、重复/损坏标记、旧生成物与新事实冲突纳入RED/GREEN。HN-05两场景及旧generation/maps测试通过后再交给Task 11。

### Task 11: 完成标准、设计交接和模块变化（宏观7.3）

**Files:** Create tests/test_onboarding_completion.py；Modify readiness.py、workflow.py、intake.py、cli.py、project_docs.py、tests/test_bootstrap_end_to_end.py。
**Interfaces:** `inspect_project(root)`追加documentation/coverage/handoff/initialization，保留旧字段和旧命令退出语义；`build_handoff(config, catalog, dossier, checks) -> dict`在project_docs.py中生成目标、版本、规格/计划引用、阻塞项、next_action及needed_permissions，不执行下一动作。受管输出docs/project/handoff.md及.framework/local-state/handoff.json，不保存凭据或永久授权。

- [ ] 写基础prepare的否定验收，防止骨架被误报完成：

```python
result = invoke('prepare', '--target', root, '--project-id', 'demo', '--yes', '--allow', 'write')
self.assertEqual(result.returncode, 0)
report = json.loads(invoke('doctor', '--target', root).stdout)
self.assertEqual(report['onboarding'], 'PREPARED')
self.assertEqual(report['initialization'], 'PARTIAL')
self.assertEqual(report['handoff']['status'], 'NEEDS_DESIGN_APPROVAL')
```

- [ ] 运行 `python3 -B -m unittest discover -s tests -p test_onboarding_completion.py -v` 观察RED。实现组合检查：必要获取/文档/覆盖/交接全通过才COMPLETE；未配置的可选索引或KB不自动变成失败；明确要求的增强能力未完成则PARTIAL；业务runtime不改变。
- [ ] 新工程fixture分两步：未批准设计时实际地图N/A、交接需设计确认；明确批准设计后记录拟建模块及DECLARED关系，仍不隐式创建Git或业务源码。继续开发读取实际OpenSpec上下文；文件中的批准字段不能替代本次执行权限，旧new门禁保持。
- [ ] 新增第四模块fixture先发现候选再授权登记；检查旧完成状态失效、前三模块ID不变、第四模块资料/关系需补齐。移动/缺失fixture保留历史及文档且报告PARTIAL，不自动删除。每个失败先观察RED，再最小修复到GREEN。
- [ ] 验证缺资料、缺批、来源变动、关键未知项分别给可操作next_action。执行HN-07/08四场景及旧端到端/doctor回归，跨模块局部通过不能替代集成证据。

### Task 12: 入口更新与真实交接验收（宏观7.4–7.5）

**Files:** Modify BOOTSTRAP.md、AGENTS.md、README.md、docs/project-intake.md、docs/framework/development-workflow.md、docs/framework/collaboration-policy.md、skill/project-bootstrap/SKILL.md、templates/module-AGENTS.md、templates/project/*.md、tests/integration/intake-prompts.md、tools/verify-live、docs/acceptance.md、CHANGELOG.md、framework-manifest.json。
**Interfaces:** 用户输入仍只是一份启动输入及意图；内部v2参数和dossier由Agent生成。真实探针复用verify-live，报告绑定当前manifest/工作树和宿主版本，输出机器测试结果与语义人工/Agent复核分别列示。

- [ ] 修改自有skill前读取writing-skills，做基线与正向消费测试：初始化结束不能只报PREPARED，必须完成文档与交接或清楚列出阻塞。公共规则/项目事实/模块局部说明三层不复制，旧高级CLI保留。
- [ ] 为verify-live独立探针写RED：remote正确但HEAD错误、内容不同、项目只有占位文档、关系缺调用端，均不得PASS。再补实际git HEAD/源码hash和文档schema校验，不能相信宿主自述。
- [ ] 真实宿主输入只含BOOTSTRAP、启动单、目标和当前范围授权；已有三模块及全新需求各跑一次。分开记录Codex和非Codex结果，后者PATH禁codex；缺认证保留NOT_RUN，不放开全局配置。不使用真实私有业务源码。
- [ ] 在第二模块获取失败、已接收部分分析批次两个断点换宿主继续；固定源码时成功模块不重clone，已接收批次不重算，当前权限重新核对。所有等待用户设计决策的状态都保持可恢复而非自动跳过。
- [ ] 运行全部离线回归、macOS/Linux验证和最终独立评审；重跑check-framework、OpenSpec严格校验和diff检查。覆盖矩阵逐项归档证据，但有未完成实测不能归档整个change为完成。未收到新的提交/推送授权时只交付本地修改。

### 增量覆盖与自查

| Scenario | Task | 主要断言 |
|---|---|---|
| HN-05-DOCS/PRESERVE | 10、11、12 | 完整内容/来源、人工保护、只读替代、冲突阻塞 |
| HN-06-LARGE/RESUME | 9、12 | 包预算、行覆盖、跨批关系、版本绑定、可恢复 |
| HN-07-NEW/CONTINUE | 11、12 | 新工程设计边界、明确交接、旧审批不重复 |
| HN-08-ADD/REMOVED | 11、12 | 变化使旧完成状态失效，稳定身份和历史保留 |
| HN-04-LIVE/RESUME | 12 | 真实双宿主和两种中断交接，不用离线stub代替 |

自查：增量8个Scenario全部有任务；4个单元按“协议→资料→诊断→真实入口”交接，公共底层storage复用；原业务工程和第三方技能不在修改范围。机器完整性校验不能代替语义审查，认证/实际宿主不可用时不能宣称通用兼容已验证。
