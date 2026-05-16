## Context

dm2-tool 的架构哲学是 "CLI 是大脑，AI 是手脚"。实际工作流中：

```
dm2 CLI (大脑)                      AI Agent (手脚, Claude Code)
─────────────                       ─────────────────────────────
dm2 instructions view/OV-1 --json → 接收: DM2术语 + 规则 + 模板
dm2 knowledge search "capability" → 接收: 结构化知识
dm2 analyze -d "desc" --json      → 接收: 6W分析 + 视图推荐
dm2 validate OV-1                  ← AI Agent 生成内容后回调验证
dm2 run --complete-step <step>     ← AI Agent 完成步骤后更新状态
```

当前的 LLM 代码（`llm/client.py`, `llm/provider.py`, `llm/prompts.py`, `DoDAFViewGenerator`）是 dm2 试图自己扮演"手脚"角色——dm2 直接调用 Claude/OpenAI API 生成内容。这违反了角色分离，且 `DoDAFViewGenerator` 从未被任何 CLI 路径实际调用。

## Goals / Non-Goals

**Goals:**
- 删除 dm2 中所有直接调用 LLM 的代码
- 将放错位置的非 LLM 代码移到正确的包
- 保持 `.claude/skills/` 中 AI Agent 交互协议完全不受影响
- 保持所有 `--json` API 和 `instructions` 命令正常工作

**Non-Goals:**
- 修改 `.claude/skills/dm2-*.md` 技能文件
- 修改 `dm2 generate`, `dm2 instructions`, `dm2 analyze` 的输出格式
- 改变 pipeline 的行为（pipeline step 已经用 ViewTemplateFiller，不依赖 LLM）
- 改动 `views.yaml` 或其他 DM2 参考数据

## Decisions

### Decision 1: 删除而非重构

**选择**: 直接删除 `llm/client.py`, `llm/provider.py`, `llm/prompts.py`, `DoDAFViewGenerator` 类。

**理由**: 这些代码在 dm2 中没有合法角色。`DoDAFViewGenerator` 从未被 CLI 调用。providers 和 client 只在 `analyze --llm` 和 `_supplement_views_by_llm` 中使用——这两个使用点也在本次删除范围。

**替代方案考虑**: 保留并标为 deprecated → 不选，因为会导致持续维护负担且与架构哲学冲突。

### Decision 2: 移动 rag.py 到 kernel 包

**选择**: `src/dm2/llm/rag.py` → `src/dm2/kernel/rag.py`，更新所有 import。

**理由**: `ObsidianRAGEngine` 执行纯文件检索（关键词匹配 MD 文件），不调任何 LLM API。它在 `dm2.llm` 包下是因为"RAG 的 R 指 retrieval（检索），但命名暗示了整个 RAG pipeline"。移到 `kernel` 包更准确反映它在知识库层的角色。

### Decision 3: 移动 config_manager.py 到 config 包

**选择**: `src/dm2/llm/config_manager.py` → `src/dm2/config/manager.py`，新建 `src/dm2/config/` 包。

**理由**: 配置解析系统（三层覆盖、YAML 加载、dot notation 存取）是通用基础设施，不依赖 LLM。DEFAULT 中需移除 `llm:` 段（provider/model/api_key/base_url/max_tokens），保留 `views:`, `consistency:`, `dm2:` 段。

### Decision 4: 保留 ViewTemplateFiller

**选择**: `ViewTemplateFiller` 类保留在 `engine/view_generator.py`。

**理由**: 它执行纯 Markdown 模板填充（加载 MD 文件 → `{placeholder}` 替换 → 输出），不调任何 LLM。它是 "dm2 大脑" 的一部分——提供草稿骨架让 AI Agent 在此基础上丰富。

### Decision 5: CLI `config` 子命令处理

**选择**: `dm2 config` 命令不再显示或设置 `llm.*` 配置项。如果用户尝试 `dm2 config -s llm.model=xxx`，提示 "llm 配置已移除，请直接在 AI Agent 中配置"。

**理由**: AI Agent（Claude Code）自带 LLM 配置，不需要 dm2 管理。

## Risks / Trade-offs

- **Risk**: 有外部脚本直接使用 `from dm2.llm.client import ClaudeClient` → **Mitigation**: 本次是 **BREAKING** 变更，在 README 中注明。同时 `ClaudeClient` 从未在 `.claude/skills/` 中被引用——所有 dm2 skill 都通过 CLI `--json` 接口使用，不受影响。
- **Risk**: `config_manager` 移动后 `dm2 config` 命令无法设置 llm 配置 → **Mitigation**: 这是预期行为。llm 配置属于 AI Agent 层。
- **Trade-off**: 删除 `analyze --llm` 后，LLM 增强的分析只能由 AI Agent 完成 → 这符合架构哲学。

## Open Questions

- `pyproject.toml` 中的 `[project.optional-dependencies]` 的 `openai` extra — 是否也删除？
