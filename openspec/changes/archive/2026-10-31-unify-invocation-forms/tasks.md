## 1. 补齐形态声明

- [x] 1.1 为 code-review、codebase-design、diagnosing-bugs、tdd、writing-for-agents 放入上游 `agents/openai.yaml`，逐字节核对
- [x] 1.2 to-tickets 改为模型调用型：frontmatter 去掉 `disable-model-invocation`，`agents/openai.yaml` 改为允许隐式调用
- [x] 1.3 在第三方声明里记录 to-tickets 的本地改编

## 2. 一致性校验

- [x] 2.1 `tools/check-framework` 增加形态一致性检查：两侧声明不得只写一侧
- [x] 2.2 增加测试：全量技能一致、负向用例能抓到单侧声明、一致的用户调用型通过

## 3. 规则与文档

- [x] 3.1 `docs/framework/skill-policy.md` 写清两种形态、声明位置、一致性要求与阶段技能的形态约束
- [x] 3.2 `docs/integrations.md` 与 `README.md` 的技能构成说明更新

## 4. 验证

- [x] 4.1 `python3 tools/check-framework` 通过
- [x] 4.2 全量单元测试通过
- [x] 4.3 `openspec validate --all --strict --no-interactive` 通过
- [x] 4.4 规格同步后归档本 change
