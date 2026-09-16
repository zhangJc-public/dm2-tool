## Why

dm2-tool 当前没有任何机制记录"为什么这个视图被生成"——LLM 决策、术语引用、校验结果、人工修改都不可追溯。DoDAF V2.02 在 DM2 数据字典中明确定义了 **Pedigree**（血统/出处）数据组，用于记录"origin, creationDate, author, versionHistory, modificationHistory, source, reliability, confidence"，但 dm2-tool 完全没有实现。工程审计时（DoD 采办条例要求），无法回答"为什么 5 年前生成的视图是这个样子的"。ontology-main 的 `dm2-metamodel.ts` 已经列出了 Pedigree 的属性，但既未工程化也未集成。必须把 LLM reasoning trace 接进视图生命周期，让每个视图自带"为什么"。

## What Changes

- **新增 LLM 推理追溯系统**：CLI 命令 `dm2 trace record`、`dm2 audit <view>`、`dm2 audit-report`，存储于 `.dm2/pedigree/`
- **视图 frontmatter 增加 pedigree 字段**：精简版（author/creation_date/source）嵌入视图 MD 文件，完整版外存于 `.dm2/pedigree/<view_id>.yaml`
- **视图生命周期状态机升级**：view-state.yaml 增 pedigree 状态字段；缺核心 pedigree 字段的视图不允许进入 `verified`
- **CLI 自动捕获事实层**：每次 view 操作、analyze 调用、validate 调用的元数据自动记录为 trace 事实
- **SKILL.md 模板改造**：propose/apply/verify 三个 skill 模板加入 trace 要求，强制 LLM 填 reasoning 字段
- **校验器输出增强**：R1-R5 校验结果自动写入对应视图的 `trace.validation`，并生成结构化修复建议

## Capabilities

### New Capabilities

- `llm-reasoning-trace`: 推理追溯核心能力。定义 Pedigree 数据模型、自动捕获机制、CLI API。覆盖 `dm2 trace record`、`dm2 audit <view>`、`dm2 audit-report` 命令。
- `audit-report`: 工程审计报告生成。基于 trace 数据输出人类可读的 why-this-view 报告和项目级审计报告。

### Modified Capabilities

- `view-lifecycle`: 增加 pedigree 状态字段；核心 pedigree 字段缺失时 `verified` 转换被拒绝。
- `view-metadata-schema`: 视图 frontmatter 增加 pedigree 精简字段（author/creation_date/source），并定义指向完整 trace 的引用 ID。
- `view-validation`: R1-R5 校验结果自动写入对应视图的 trace 记录。
- `dm2-propose-workflow`: SKILL.md 模板增加 trace 字段填写要求。
- `dm2-apply-workflow`: SKILL.md 模板在 apply 步骤增加 trace 更新要求。

## Impact

**Affected code**:
- 新增模块：`src/dm2/core/pedigree/` (data model, store, recorder)
- 新增 CLI 命令：`src/dm2/cli/commands/trace.py`、`src/dm2/cli/commands/audit.py`
- 修改模块：`src/dm2/core/views/manager.py`（状态机）、`src/dm2/core/views/state.yaml` schema、`src/dm2/reasoning/consistency.py`（写 trace）
- 修改 SKILL 模板：`src/dm2/core/templates/workflows/{propose,apply,verify}.py`

**Affected artifacts**:
- 所有未来生成的视图必须包含 pedigree frontmatter
- `.dm2/pedigree/` 目录在 `dm2 init` 时创建
- `.dm2/view-state.yaml` schema 扩展

**Affected agents**:
- 消费 SKILL.md 的 Claude Code / 其他 LLM Agent 必须按新模板填 trace 字段
- 现有 SKILL.md 不会自动迁移；项目升级后第一次 dm2:propose 时开始强制

**Dependencies**:
- 无新增外部依赖（用 PyYAML 已有）
- 与 `dm2-data-group-activation` 无冲突
- 与 `metadata-driven-instructions` 协作（pedigree 字段进入 instruction context）

**Compatibility**:
- 现有视图文件无 pedigree frontmatter 时，`dm2 audit` 报告"trace 缺失"但不会失败；新生成视图强制
- 这是面向 LLM 输出的工作流变更，不影响 dm2 CLI 已有命令的输出格式
