## Why

dm2 的架构宣言是"CLI 是大脑，AI 是手脚"——dm2 提供 DM2 知识、视图规范、合规规则和结构化指令，AI Agent 用自己的 LLM 执行具体内容生成。但当前代码中 dm2 包含了完整的 LLM 调用能力（ClaudeClient、AnthropicProvider、OpenAIProvider、DoDAFViewGenerator、LLM prompt 模板），这意味着 dm2 自己在扮演"手脚"角色。这些代码不仅与架构哲学冲突，而且实际上 `DoDAFViewGenerator` 从未被任何 CLI 路径调用——它是死代码。需要将 dm2 彻底清理为纯 CLI 工具，把 LLM 能力完全交给 AI Agent。

## What Changes

- **删除** `src/dm2/llm/client.py` — ClaudeClient（**BREAKING**: 任何直接使用此类的代码将失效）
- **删除** `src/dm2/llm/provider.py` — AnthropicProvider, OpenAIProvider, create_provider（**BREAKING**）
- **删除** `src/dm2/llm/prompts.py` — DM2_SYSTEM_PROMPT, VIEW_GENERATION_PROMPTS, PromptTemplate（**BREAKING**）
- **删除** `src/dm2/engine/view_generator.py` 中的 `DoDAFViewGenerator` 类 — dm2 自己生成视图的能力（**BREAKING**）
- **删除** `src/dm2/cli/main.py` 中的 `analyze --llm` 标志和对应代码路径
- **删除** `src/dm2/cognitive/view_recommender.py` 中的 `verify_and_supplement_views()` 及 `_supplement_views_by_llm()` 方法
- **移动** `src/dm2/llm/rag.py` → `src/dm2/kernel/rag.py` — ObsidianRAGEngine 是纯文件检索，不应在 llm 包下
- **移动** `src/dm2/llm/config_manager.py` → `src/dm2/config/manager.py` — 配置系统独立于 LLM，去掉 DEFAULT 中的 `llm:` 段
- **保留** `ViewTemplateFiller` — 纯模板填充，无 LLM 依赖
- **保留** `InstructionBuilder`, `KnowledgeAPI`, `VIEW_RULES`, `STEP_TEMPLATES` — 服务 dm2↔AI Agent 交互

## Capabilities

### New Capabilities

- `dm2-no-llm-dependency`: dm2 CLI has zero LLM code paths — all analysis is rule-based, all generation is template-based, all LLM capability is delegated to external AI Agents
- `dm2-agent-instruction-interface`: dm2 provides a consistent JSON interface (via `instructions` command and `--json` flag) for AI Agents to consume DM2 knowledge, view specifications, compliance rules, and output templates

### Modified Capabilities

- `dm2-generate-no-llm`: scope expanded from just `generate` command to the entire dm2 codebase — no Python file under `src/dm2/` shall import or call any LLM client/provider

## Impact

- `src/dm2/llm/` 目录将只剩 `rag.py`（移至 kernel），最终整个目录可删除
- `src/dm2/engine/view_generator.py` 将只保留 `ViewTemplateFiller` 和相关数据类
- `src/dm2/cli/main.py` 的 `analyze` 命令将移除 `--llm` 选项
- `src/dm2/cognitive/view_recommender.py` 将移除约 130 行 LLM 相关方法
- `src/dm2/config/` 将新增为独立包，承载配置解析
- `.claude/skills/dm2-*.md` AI Agent 技能文件不受影响
- 已有 pip 安装的 `dm2` 入口点不受影响
