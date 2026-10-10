## Why

dm2-tool 目前没有任何机制记录「为什么这个视图被生成」：术语引用、校验结果、Agent 的取舍理由、人工修改都不可追溯。DoDAF V2.02 在 DM2 数据字典中明确定义了 **Pedigree**（血统/出处）数据组——origin、creationDate、author、versionHistory、modificationHistory、source、reliability、confidence——而 dm2 完全没有实现它。工程审计（DoD 采办条例）时无法回答「为什么 5 年前生成的视图是这个样子」。

**为什么是现在、以及为什么改了名字**：本变更原为 `add-llm-reasoning-trace`（2026-06-02），其框架是「把 LLM 推理轨迹接进视图生命周期」。但项目已在 2026-05-04 通过 `remove-llm-from-dm2` 彻底移除 LLM——dm2 不调用任何 LLM，**推理发生在外部 AI Agent 侧**。因此溯源必须拆成两层：dm2 自动记录它**可观测的事实**，并接受 Agent **主动声明的推理**。需求不变，施动者变了。

## What Changes

- **新增视图溯源（Pedigree）系统**：CLI 命令 `dm2 trace record`、`dm2 audit <view>`、`dm2 audit-report`，数据存于 `.dm2/pedigree/`
- **视图 frontmatter 增加 pedigree 字段**：精简版（author/creation_date/source）嵌入视图 MD，完整版外存 `.dm2/pedigree/<view_id>.yaml`，以 `pedigree_id` 关联
- **视图生命周期状态机升级**：`view-state.yaml` 增加 pedigree 状态；缺核心 pedigree 字段的视图**不允许**进入 `verified`
- **双通道写入**：dm2 自动捕获事实层（view 操作、analyze、validate 的元数据），AI Agent 通过技能工作流声明推理层
- **技能模板改造**：propose/apply/verify 三个模板加入溯源要求，**要求 Agent 声明其推理与取舍**（dm2 自身不生成推理）
- **校验器输出增强**：R1–R5 校验结果写入对应视图的 `trace.validation`，并生成结构化修复建议

## Capabilities

### New Capabilities

- `view-provenance`: 视图溯源核心能力。定义 Pedigree 数据模型、双通道捕获机制与 CLI API，覆盖 `dm2 trace record`、`dm2 audit <view>`、`dm2 audit-report`。
- `audit-report`: 工程审计报告生成。基于溯源数据输出人类可读的 why-this-view 报告与项目级审计报告。

### Modified Capabilities

- `view-lifecycle`: 增加 pedigree 状态字段；核心字段缺失时拒绝 `verified` 转换。
- `view-metadata-schema`: 视图 frontmatter 增加 pedigree 精简字段（author/creation_date/source），并定义指向完整记录的引用 ID。
- `view-validation`: R1–R5 校验结果自动写入对应视图的溯源记录。
- `dm2-propose-workflow`: 技能模板增加溯源字段声明要求。
- `dm2-apply-workflow`: 技能模板在 apply 步骤增加溯源更新要求。

## Impact

**Affected code**:
- 新增模块：`src/dm2/core/pedigree/`（数据模型、存储、记录器）
- 新增 CLI：`src/dm2/cli/commands/trace.py`、`src/dm2/cli/commands/audit.py`
- 修改：`src/dm2/core/views/manager.py`（状态机 + 事件钩子）、`view-state.yaml` schema、`src/dm2/reasoning/consistency.py`（写溯源）
- 修改技能模板：`src/dm2/core/templates/workflows/{propose,apply,verify}.py`

**Affected artifacts**:
- 未来生成的视图须包含 pedigree frontmatter
- `dm2 init` 创建 `.dm2/pedigree/`
- `.dm2/view-state.yaml` schema 扩展

**Affected agents**:
- 消费技能模板的 AI Agent 须按新模板声明溯源字段（Claude Code、DeepSeek Harness 等）
- 现有技能副本不会自动迁移；项目升级后首次 propose 起开始强制

**Dependencies**:
- 无新增外部依赖（复用 PyYAML）
- 与 `dm2-data-group-activation` 无冲突；与 `metadata-driven-instructions` 协作（pedigree 进入 instruction context）

**Compatibility**:
- 既有视图无 pedigree 时，`dm2 audit` 报告「溯源缺失」但不失败；新生成视图强制
- 这是面向 AI Agent 工作流的变更，不改变 dm2 已有命令的输出格式

**Invariant check**:
- 本变更**不违反** `dm2-no-llm-dependency`：dm2 仍不导入、不声明、不调用任何 LLM；它只记录自身可观测的事实，并持久化 Agent 主动提交的内容
