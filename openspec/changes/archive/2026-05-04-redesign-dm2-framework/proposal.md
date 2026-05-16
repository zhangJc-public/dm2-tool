## Why

当前 dm2-tool 是一个面向人类用户的独立 CLI 工具，所有命令输出人类可读文本，内部硬编码 LLM 调用逻辑，缺乏面向 AI Agent 的程序化接口。这导致 AI 无法有效利用 DM2 知识库驱动系统工程流程——每次交互都需要重新在 prompt 中注入知识，无法追踪工作状态，也无法管理架构变更生命周期。参照 OpenSpec "CLI 是大脑，AI 是手脚"的架构模式，需要将 dm2-tool 重新设计为 **CLI 工具 + AI 协作框架**，由 DoDAF 标准驱动，AI Agent 通过结构化接口查询状态、获取指令、执行生成、同步知识。

## What Changes

- **BREAKING**: 重新设计 CLI 架构，引入三层模型（Agent 接口层 / 核心引擎层 / 知识库层）
- **BREAKING**: 所有 CLI 命令新增 `--json` 标志，输出结构化 JSON 供 AI 解析
- 新增 Artifact Graph 模块：管理 DoDAF 视图/制品依赖关系和生成状态
- 新增 Instructions Engine 模块：为每个 DoDAF 制品类型生成 AI 执行指令（context + rules + template）
- 新增 Change Manager 模块：架构变更生命周期管理（create → analyze → generate → verify → archive）
- 新增 Knowledge API 模块：结构化查询接口（DM2 术语检索、概念关系查询、视图依赖查询）
- 重构 Pipeline：从硬编码 Python 函数改为 AI-Agent 驱动的指令执行循环
- Provider 层保持独立，支持 Anthropic/OpenAI 双 provider

## Capabilities

### New Capabilities

- `agent-interface`: CLI 的 JSON 化接口层，所有命令支持 --json 输出，AI Agent 可程序化调用
- `artifact-graph`: DoDAF 制品依赖图管理，视图间依赖关系定义和状态追踪
- `instructions-engine`: AI 指令生成引擎，根据制品类型、DM2 上下文、项目约束生成结构化指令
- `change-manager`: 架构变更生命周期管理，涵盖变更创建、分析、生成、验证、归档全流程
- `knowledge-api`: DM2 知识库的结构化查询 API，术语检索、概念关系、视图模板查询
- `pipeline-v2`: 重构的 6 步融合流程，以 AI Agent 为执行主体，CLI 负责调度和状态管理

### Modified Capabilities

- `pipeline-orchestrator`: 将硬编码的步骤执行改为 AI-Agent 驱动的指令-执行-验证循环
- `step1-intent-scope`: 添加 JSON 输出格式和指令生成能力
- `step3-data-requirements`: 添加 RAG 检索的结构化查询接口
- `step5-analysis`: 添加分析结果的 JSON Schema 定义
- `step6-documentation`: 添加视图生成的指令模板和验证规则

## Impact

- `src/dm2/cli/main.py` — 完全重构，所有命令新增 --json 输出
- `src/dm2/engine/pipeline/*` — 重构为 AI-Agent 驱动模式
- `src/dm2/kernel/indexer.py` — 扩展为 Knowledge API
- `src/dm2/llm/*` — provider 抽离为独立接口
- 新增 `src/dm2/core/agent/` — Agent 指令生成和状态管理
- 新增 `src/dm2/core/artifacts/` — 制品依赖图
- 新增 `src/dm2/core/changes/` — 变更管理
