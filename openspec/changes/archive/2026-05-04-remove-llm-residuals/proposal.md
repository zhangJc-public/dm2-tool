## Why

dm2 工具的架构原则是「CLI 工具 + AI 协作框架」，CLI 不应直接调用 LLM。当前代码中存在两处 LLM 残留：`dm2 generate` 直接依赖 LLM 生成视图内容（无 API Key 时产出占位内容），`dm2 cynefin` 缺少纯文本参数推导功能。这些问题使工具在无 LLM 环境中无法正常工作，且违背了 CLI 只做结构化数据处理、AI Agent 负责内容生成的分工原则。

## What Changes

- `dm2 cynefin` 新增 `--desc` / `-d` 参数，支持从描述文本自动推导 4 个复杂度参数（systems、stakeholders、uncertainty、rules）
- `dm2 generate` 移除所有 LLM 依赖，不再调用 `create_provider`、`DoDAFViewGenerator` 等组件，改为输出结构化 JSON/YAML 指令供 AI Agent 使用
- `dm2 generate` 移除 `--no-rag` 参数（已不再需要）

## Capabilities

### New Capabilities

- (none)

### Modified Capabilities

- `dm2-cynefin-auto-derive`: `dm2 cynefin` 命令新增文本自动推导能力，cynefin CLI 能力增强
- `dm2-generate-no-llm`: `dm2 generate` 命令移除 LLM 依赖，改为结构化指令输出模式
- `dm2-data-group-activation`: 数据组激活机制的 keywords 和 group-to-views 外部化已实现，generate 命令利用该数据

## Impact

- `src/dm2/cli/main.py`: `cynefin` 命令新增 `--desc` 选项和 `_derive_cynefin_from_description()` 函数；`generate` 命令完全重写
- `src/dm2/cognitive/view_recommender.py`: `recommend()` 新增 `raw_description` 参数，新增 `recommend_from_description()` 方法
- `.claude/skills/dm2-propose-workflow/SKILL.md`: 已更新为使用新的 generate 输出模式
- `dm2-reference/group-to-views.yaml`: 新增的外部映射文件（已被 generate 命令使用）
- `dm2-reference/core/groups/*/*-Template.md`: 11 个模板已添加 keywords 和 related_dm2_views 元数据
