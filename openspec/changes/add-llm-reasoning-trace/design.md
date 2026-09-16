## Context

dm2-tool 当前的视图生命周期只跟踪"状态"（pending/in_progress/generated/verified），不跟踪"为什么"。LLM 通过 SKILL.md 工作流生成视图时，所有决策依据都丢失。ontology-main 已经在 `dm2-metamodel.ts:357-411` 把 DM2 V2.02 Pedigree 数据组的属性结构化列出（origin, creationDate, author, versionHistory, modificationHistory, source, reliability, confidence），但该元模型没有工程化集成到任何 CLI 工作流。

本设计将 Pedigree 实现为 dm2 项目的 first-class artifact，由 CLI 自动捕获客观事实（事实层）+ LLM 主动调用 CLI 记录主观理由（理由层）双通道写入，存储于嵌入 frontmatter + 外存 YAML 双位置。这与 `metadata-driven-instructions` 规范协作（pedigree 字段进入 InstructionBuilder 的 context），与 `view-lifecycle`/`view-validation` 规范修改深度集成（验证结果回写 + 状态门控）。

约束：用户已确认不重构 CLI 架构（不引入多进程/RPC），不实现 SHACL/OWL 语义层。pyyaml 已是 dm2 唯一需要的外部依赖。

## Goals / Non-Goals

**Goals:**

- 让每个视图的"为什么"在交付 5 年后仍可追溯
- Pedigree 数据自动捕获与 LLM 主动声明双通道，事实与理由分离
- 视图 `verified` 状态被 pedigree 完整性门控，确保工程严肃性
- 提供 `dm2 audit <view>` 和 `dm2 audit-report` 命令输出人类可读审计报告
- 跨变更追溯（capability/term lineage）支持

**Non-Goals:**

- 不引入 SHACL/OWL 语义层（保持 --json 路线）
- 不把 views.yaml 替换为 XLS 数据源（另议）
- 不重构现有 CLI 架构为多进程/RPC
- 不修改 R1-R5 一致性规则本身（仅修改其输出落点）
- 不为既有视图自动补 pedigree（视为"trace 缺失"，审计时报告）

## Decisions

### Decision 1: 双层存储 — 嵌入 frontmatter + 外存完整 YAML

**选择**: 每个视图 frontmatter 包含精简 pedigree 块（pedigree_id / author / creation_date / source 子集），完整记录在 `.dm2/pedigree/<view_id>.yaml`，用 pedigree_id 关联。

**Rationale**:
- 嵌入 frontmatter 让视图可独立移动/共享时仍带血缘
- 外存完整 YAML 避免视图文件膨胀，详细决策历史不影响阅读
- pedigree_id 作为统一引用键，让 audit 报告能从一个 ID 跳到完整记录

**Alternatives considered**:
- A. 全部嵌入 frontmatter — 拒绝：视图文件会很大，frontmatter 解析变慢
- B. 全部外存 — 拒绝：移动视图时血缘丢失，工程实用上不可接受
- C. 双层（采用）— 平衡可读性与完整性

### Decision 2: 双通道写入 — CLI 自动捕获 + LLM 主动声明

**选择**:
- 事实层（CLI 自动）：view 注册、状态转换、validate 调用的元数据 → `modification_history`、`validation` 字段
- 理由层（LLM 主动）：通过 `dm2 trace record` 命令 LLM 写 `reasoning.summary`、`decision_factors`、`alternatives_considered`、`known_limitations`

**Rationale**:
- 事实不可被 LLM "事后合理化"伪造，理由是 LLM 的真实思考过程
- 理由层不强制每次都写（避免 LLM 负担过重），但 verify 状态要求核心字段必须存在
- 强制等级 = 必填 author/creation_date/source（核心），推荐 alternatives_considered/known_limitations（增强）

**Alternatives considered**:
- A. LLM 全部手写 — 拒绝：LLM 可能编造"事实"（如冒充 validate 结果）
- B. CLI 全部自动 — 拒绝：记不到"为什么"，审计时无意义
- C. 双通道（采用）— 事实与理由天然分离

### Decision 3: Pedigree 数据模型用 dataclass + 显式 schema 文件

**选择**: `src/dm2/core/pedigree/model.py` 使用 Python dataclass 配合手工 schema 文件 `src/dm2/core/pedigree/schema.yaml`，序列化/反序列化用 `yaml.safe_dump` / `yaml.safe_load`。

**Rationale**:
- 与 dm2 现有风格一致（kernel/indexer.py 用 dataclass，utils/frontmatter.py 用手工 YAML）
- 不引入 pydantic 减少依赖（虽然 pydantic 已是 transitive dep，但项目其他模块没用）
- schema.yaml 同时作为审计文档和 OpenSpec 规范的"机器可读版本"

**Alternatives considered**:
- A. Pydantic models — 拒绝：引入新依赖风格，破坏现有 minimal 依赖原则
- B. attrs — 拒绝：项目其他模块不引入
- C. dataclass + 手工 schema（采用）— 保持一致

### Decision 4: ViewManager 修改采用"装饰器式事件钩子"

**选择**: 在 `ViewManager` 状态转换处加事件钩子（`on_state_change`, `on_register`），由 `PedigreeRecorder` 订阅这些事件并自动写 pedigree。不改 ViewManager 内部逻辑，只在转换点发事件。

**Rationale**:
- 解耦：ViewManager 不需要"知道" pedigree
- 可测试：事件可独立 mock
- 可扩展：未来加新事件源（pipeline、外部工具）不用改 ViewManager
- 符合"开闭原则"——ViewManager 对扩展开放，对修改关闭

**Alternatives considered**:
- A. 直接在 ViewManager 方法里写 pedigree — 拒绝：耦合严重，难测试
- B. 装饰器包 ViewManager 方法 — 拒绝：复杂，元数据丢失
- C. 事件钩子（采用）— 解耦，简洁

### Decision 5: `dm2 audit` 和 `dm2 audit-report` 作为新 CLI group

**选择**: 新增 `src/dm2/cli/commands/audit.py`，注册为 `audit_app` Typer 子命令组。命令包括 `dm2 audit <view_id>` 和 `dm2 audit-report`。输出支持 `--json`、`--output`、`--min-confidence`。

**Rationale**:
- 与现有 `dm2 view` / `dm2 validate` / `dm2 knowledge` 命令组织一致
- 独立 group 让 audit 逻辑自治，未来可加 `dm2 audit-lineage` 等
- 输出可选 Markdown/JSON，覆盖人类阅读与机器消费

**Alternatives considered**:
- A. 把 audit 塞进 `dm2 view` — 拒绝：view 是状态管理，audit 是查询，关注点不同
- B. 把 audit 塞进 `dm2 validate` — 拒绝：validate 是规则检查，audit 是溯源
- C. 独立 group（采用）— 职责单一

### Decision 6: SKILL.md 模板改造采用"内联 trace 指令"而非"独立 trace skill"

**选择**: 修改现有的 `propose.py` / `apply.py` Python 模板（生成 SKILL.md 文本），在合适位置插入"调用 `dm2 trace record`"的指令。**不**新增独立 `dm2-trace-workflow` skill。

**Rationale**:
- 现有 propose/apply workflow 已经覆盖视图生命周期
- trace 是这些 workflow 的"内嵌要求"，不是独立 phase
- 新增 skill 会让用户多一步操作（先 propose，再 trace，再 apply），破坏工作流连贯性
- 工程实用性：审计时看 propose/apply 的 SKILL.md 就能看到 trace 要求

**Alternatives considered**:
- A. 独立 `dm2:trace` skill — 拒绝：破坏 LLM 工作流连贯性
- B. 内联指令（采用）— 维护工作流单一来源
- C. 用 SKILL.md frontmatter 元数据声明 trace 要求 — 复杂，且 LLM 不一定会遵循

## Risks / Trade-offs

**[Risk] LLM 跳过 trace record 调用，写出"假合规"** → Mitigation: verify 状态门控 + SKILL.md 强提示 + audit 命令检测"trace 缺失"显式报告

**[Risk] 双层存储数据漂移（frontmatter 与外存不一致）** → Mitigation: 每次写外存时同步刷新 frontmatter；audit 命令运行时校验一致性，发现漂移报警

**[Risk] Pedigree YAML 文件膨胀（项目用 3 年后每个视图都有 50+ 行 history）** → Mitigation: 提供 `dm2 trace compact` 命令归档老条目到 `.dm2/pedigree/archive/`；modification_history 默认保留最近 20 条

**[Risk] LLM 写入的"理由"是事后合理化而非真实推理** → Mitigation: 文档明确说明 pedigree 的 LLM 部分"is the LLM's stated reasoning, not validated ground truth"；CLI 自动捕获的 fact 部分是不可篡改的"硬证据"

**[Risk] 跨变更追溯（lineage）性能问题——项目有 50+ 视图时全量扫描慢** → Mitigation: 初次实现可接受全量扫描（<100 视图 <1s）；未来加 `.dm2/pedigree/index.yaml` 索引

**[Risk] 现有 SKILL.md 已在使用，修改可能让 Claude 行为变化不可控** → Mitigation: 模板生成逻辑保留可选项（`config.yaml` 加 `trace.enabled: true|false`），老项目可关闭

**[Trade-off] 引入 `dm2 trace record` 增加 LLM 调用次数（每个视图多 1-2 次 CLI 调用）** → Mitigation: SKILL.md 允许批量模式（一次 record 多个 view_id）；trace 失败不阻塞主流程

## Migration Plan

**部署步骤**:

1. **Phase 1（内部测试）**: 在 dm2 自己的 .dm2/ 项目里跑一遍新流程，验证 pedigree 写入和 audit 报告
2. **Phase 2（opt-in）**: 通过 `config.yaml` 的 `trace.enabled: false` 默认关闭，新项目引导时询问是否启用
3. **Phase 3（默认开启）**: 在 0.2.0 版本默认启用；老项目升级时跑一次性迁移脚本补"trace 缺失"标记

**回滚策略**:

- `config.yaml` 关闭 `trace.enabled` 立即禁用所有 pedigree 写入
- 现有视图不受影响（`verified` 状态不被打回）
- `.dm2/pedigree/` 目录可手动删除，不影响其他状态

**兼容性**:

- 现有视图无 pedigree 时：`dm2 audit` 报告"trace 缺失"但不阻塞
- 现有 `dm2 validate` 输出格式保持（仅增加 `--json` 输出的 `pedigree_updated` 字段，向后兼容）
- 现有 `dm2 view list` 输出增加 `pedigree_status` 字段，老 consumer 忽略未知字段

## Open Questions

1. **Pedigree 中 `confidence` 字段如何由 LLM 自评？** 是否需要 LLM 跑一个 self-check 子流程（与 validate 区分）？**当前默认**: LLM 自由填 0-1，未来可加 self-check 工具。
2. **跨变更追溯（lineage）的 UI 形态？** 当前 `dm2 trace lineage` 输出 JSON，未来是否需要 Mermaid 图？**当前默认**: 仅 JSON，留扩展点。
3. **Pedigree 是否需要加密/签名？** 工程交付物可能被审查，是否要保证 pedigree 没被事后篡改？**当前默认**: 不加密，依赖 git log；若需更强保证可加 GPG 签名（远期）。
4. **`dm2 trace compact` 的归档策略？** 修改历史超过多少条触发？默认 20 条是否合理？**待用户决策**。
