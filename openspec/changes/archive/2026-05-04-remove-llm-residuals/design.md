## Context

dm2 工具的架构设计原则是「CLI 工具 + AI 协作框架」: CLI 负责结构化数据处理和状态管理，AI Agent（Claude Code）负责内容生成和推理决策。当前代码中存在两处违背该原则的 LLM 残留：

1. `dm2 generate` 内置了 `DoDAFViewGenerator`，直接调用 LLM 生成视图内容。无 API Key 时输出占位内容而非错误提示，掩盖了架构问题。
2. `dm2 cynefin` 只接受结构化参数（`--systems`, `--stakeholders` 等），缺少从自然语言描述自动推导的能力。

问题根因：早期开发直接套用了 LLM 工具链模式，未遵循 CLI-AI 分工。

## Goals / Non-Goals

**Goals:**
- `dm2 cynefin` 支持 `--desc / -d` 参数，从描述文本自动推导 4 个 Cynefin 参数
- `dm2 generate` 移除所有 LLM 依赖，输出结构化指令供 AI Agent 消费
- 保持 CLI 输出中包含所有 AI Agent 所需的结构化数据（6W 分析、数据组激活、视图规则）

**Non-Goals:**
- 不删除 `llm/` 包下的底层基础设施（如 RAG 配置管理），保留未来选项
- 不改变 `dm2 run` 的 Agent 驱动模式（该命令本身就不直接调 LLM）
- 不重构 view_recommender.py 中未使用的遗留方法

## Decisions

### 决策 1：Cynefin 自动推导采用纯关键词计数

**方案**: 对描述文本进行关键词计数，按阈值映射到 4 个维度（systems, stakeholders, uncertainty, rules）的数值。

**替代方案**: 使用 NLP 库或 LLM 进行语义分析。但纯关键词方法无额外依赖、确定性强、对军事/工程领域术语匹配效果好。

**阈值示例**: 
- systems: "系统/模块/节点/api/service" 计数 → ≤2→3, ≤5→5, >5→8
- stakeholders: "组织/部门/科室/机构" 等计数 → ≤1→simple, ≤3→medium, >3→complex

### 决策 2：Generate 输出结构化指令而非视图内容

**方案**: `dm2 generate` 查询索引器获取视图模板信息，运行 6W 分析和数据组激活，将所有结构化数据打包为 JSON/YAML 输出，附带指令文本 "将此指令传递给 AI Agent 以生成视图内容"。

**替代方案**: 保留 `DoDAFViewGenerator` 但标记为可选（需要 API Key 时启用）。此方案虽然兼容旧用法，但模糊了架构边界，且 AI Agent 不需要 CLI 生成的内容——Agent 自己能生成更好的内容。

**关键变化**:
- 移除 `create_provider()`, `DoDAFViewGenerator`, `resolve_config` 调用
- 输出不再是视图内容，而是生成视图所需的元数据 + 指令
- 移除 `--no-rag` 参数（不再需要）

### 决策 3：保持 view_recommender.py 中的遗留方法

**方案**: 保留 `CONCEPT_TO_VIEWS`、`get_minimal_view_set()` 等旧方法，不主动删除。

**理由**: `view_recommender.py` 中部分旧代码可能被其他模块引用（如 `dm2 run` pipeline），删除前需要全面审计。本变更只改动 main.py。

## Risks / Trade-offs

- [风险] generate 命令输出格式变化 → 旧版 AI 技能/skills 中使用 generate 输出作为视图内容的脚本需要更新 → [[SKILL.md]] 已更新为使用新输出模式
- [风险] 删除 `--no-rag` 参数 → 用户可能正在使用该参数 → 该参数在旧版中只是一个布尔标记，移除不会导致运行时错误
- [风险] Cynefin 关键词的覆盖度有限 → 对于非工程领域描述可能不准确 → 用户仍可手动指定 `--systems` 等参数覆盖自动推导值
