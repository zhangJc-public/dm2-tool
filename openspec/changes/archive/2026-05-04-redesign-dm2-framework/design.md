## Context

当前 dm2-tool 的架构是传统的单体 CLI 设计：
- CLI 命令直接调用 Python 函数，输出人类可读的终端文本
- Pipeline 步骤硬编码在 Python 中，LLM 调用内嵌在函数内部
- 无程序化接口供 AI Agent 查询状态或获取生成指令
- 无制品依赖图，AI 无法知晓"下一步该生成什么"
- DM2 知识库仅内部使用，AI Agent 无法结构化查询

参照 OpenSpec v1.3.1 的架构模式（详见 `OpenSpec-main/docs/summary-design.md`），其核心理念是：
- **CLI 是大脑**：负责状态管理、依赖解析、指令生成、Schema 验证
- **AI 是手脚**：根据结构化指令执行制品生成、分析、验证
- **文件即状态**：所有工作状态持久化到文件系统

dm2-tool 的定位与此高度一致：DoDAF 标准提供系统工程的知识框架，CLI 管理架构变更的生命周期，AI Agent 负责执行具体的视图生成和分析工作。

## Goals / Non-Goals

**Goals:**
- 重新设计 dm2-tool 为四层架构：AI Agent 层 / Agent 接口层 / 核心引擎层 / 知识库层
- 所有 CLI 命令新增 `--json` 标志，输出结构化 JSON 供 AI 程序化解析
- 新增 Artifact Graph 模块：管理 52 个 DoDAF 视图的依赖关系和生成状态
- 新增 Instructions Engine：为每种制品类型生成 AI 指令（context + rules + template）
- 新增 Change Manager：架构变更的完整生命周期管理
- 新增 Knowledge API：DM2 知识库的结构化查询接口
- 重构 Pipeline：从硬编码 Python 函数改为 AI-Agent 驱动的指令-执行-验证循环
- Provider 层保持独立，支持 Anthropic/OpenAI 及未来扩展

**Non-Goals:**
- 不重写 DM2 知识库内容（dm2-reference 保持不变）
- 不改变 DoDAF 标准定义（52 视图、17 数据组、277 术语不变）
- 不引入数据库或外部服务依赖（保持 filesystem-only）
- 不实现 OpenSpec 那样的 27+ 工具适配器（当前仅需支持 Claude Code）
- 不改变 pyproject.toml 的 Python 3.9+ 约束

## Decisions

### Decision 1: 四层架构模型

采用四层架构替代当前的扁平模块结构：

```
Agent Interface Layer (CLI --json)
        │
Core Engine Layer (Artifact Graph / Instructions Engine / Change Manager / Pipeline)
        │
Knowledge Base Layer (Knowledge API / DM2 Indexer)
        │
File System Layer (.dm2/ state, dm2-reference/, output/)
```

**理由**: 与 OpenSpec 的三层架构（CLI / Core / Filesystem）一致，额外拆出 Knowledge Base Layer 是因为 DM2 的知识库比 OpenSpec 的 config.yaml 复杂得多（277 术语、52 视图模板、17 数据组），需要独立的查询接口层。

### Decision 2: `--json` 作为通用输出标志

所有 CLI 命令新增 `--json` flag，输出结构化 JSON。人类可读格式保持为默认。

```bash
# 人类可读（默认）
dm2 status

# AI Agent 程序化接口
dm2 status --json
```

**JSON 响应统一结构**：
```json
{
  "status": "success" | "error",
  "data": { ... },
  "error": { "code": "...", "message": "..." }
}
```

**理由**: 同一命令服务于两种消费者（人类+AI），避免维护两套命令。与 OpenSpec 的 `--json` 模式一致。AI Agent 可通过 grep/jq 解析输出。

### Decision 3: Instructions Engine 作为核心创新

OpenSpec 的成功关键在于 **Instructions Engine**——每个制品类型都有对应的生成指令。这是 dm2-tool 当前最大的缺失。

**Instructions JSON 结构**：
```json
{
  "context": {
    "project": "<项目描述>",
    "dm2_terms": [{"term": "...", "definition": "...", "group": "..."}],
    "dm2_concepts": [{"name": "...", "relationships": [...]}],
    "related_artifacts": [{"id": "OV-1", "status": "done"}]
  },
  "rules": [
    "<DoDAF 合规规则 1>",
    "<DoDAF 合规规则 2>"
  ],
  "template": {
    "sections": ["## 概述", "## 图表", "## 分析"],
    "mermaid": "<template>",
    "required_fields": ["view_id", "view_name", "generated_at"]
  },
  "outputPath": "output/OV-2.md"
}
```

关键原则（与 OpenSpec 一致）：**context 和 rules 是 AI 的约束，不写入制品文件**。

**理由**: 指令引擎解决了 AI Agent 的核心问题——不知道 DM2 标准要求什么。通过在指令中注入 DM2 术语定义、依赖视图内容、DoDAF 合规规则，AI 能够生成符合标准的制品。

### Decision 4: View Dependency Graph (Artifact Graph)

DoDAF 52 个视图间存在复杂的依赖链。当前代码中依赖关系散落在 `view_recommender.py` 的 `VERIFY_CHAINS` 字典中，需要统一为 Artifact Graph。

**Graph 数据来源**：`dm2-reference/views.yaml` 中已定义每个视图的 `dependencies` 和 `downstream` 字段。

**核心算法**：
```python
def get_artifact_status(artifact_id: str, change_dir: Path) -> str:
    if output_exists(artifact_id, change_dir):
        return "done"
    unmet_deps = [d for d in get_dependencies(artifact_id) 
                  if not output_exists(d, change_dir)]
    if unmet_deps:
        return "pending"
    return "ready"
```

**状态机**：
```
pending → ready → in_progress → done
  ↑                    |
  └────────────────────┘ (依赖变化时回退)
```

**理由**: 统一管理视图依赖关系，AI Agent 可通过 `dm2 change status --json` 查询"哪些视图可以生成"。

### Decision 5: Change 作为一等概念

当前 `dm2-changes/` 只是一个自由格式的目录。需要形式化 Change 的生命周期：

```
dm2 change new <name>        → 创建变更（open）
dm2 analyze <desc> --json    → 分析阶段（analyzing）
dm2 generate <view> --json   → 生成阶段（generating）
dm2 verify --json            → 验证阶段（verifying）
dm2 archive <name>           → 归档（archived）
```

每个 change 目录结构（标准化）：
```
dm2-changes/<name>/
├── .change.yaml          ← 变更状态（取代自由格式的 tasks.md）
├── analysis/             ← 分析产物（6W 结果、Cynefin 评估）
├── views/                ← 生成的视图制品
├── delta-specs/          ← 增量规格（类似 OpenSpec delta specs）
└── verification.md       ← 验证结果
```

**理由**: 形式化的 Change 生命周期使 AI Agent 能够追踪工作进度，支持 resume、iterate 等高级流程。

### Decision 6: Knowledge API 替代内部 Indexer

当前 `DM2KnowledgeIndexer` 是一个内部类，被 CLI 命令直接调用，外部无法查询。需要暴露为 Knowledge API：

```bash
dm2 knowledge search "<query>" --json      # 术语全文搜索
dm2 knowledge concept <name> --json        # 概念详情 + 关系
dm2 knowledge views --type OV --json       # 按视点类型列出视图
dm2 knowledge view <id> --json             # 单个视图的模板+依赖+规则
dm2 knowledge stats --json                 # 知识库统计
```

**理由**: AI Agent 需要按需查询 DM2 知识，而不是每次都加载全部 277 个术语。按需检索降低 token 消耗。

### Decision 7: Pipeline 重构为 Agent Loop

当前 6 步 Pipeline 是硬编码的 Python 函数序列。重构为 AI Agent 驱动的循环：

```
while not pipeline_complete:
    status = dm2 run --status --json
    current_step = status["current_step"]
    
    instructions = dm2 instructions $current_step --json
    # AI Agent 根据 instructions 生成步骤产物
    # AI Agent 写入产物到 .dm2/steps/
    
    dm2 run --step $current_step --complete --json
```

Pipeline Orchestrator 的职责从"执行步骤"变为"管理步骤状态和生成指令"。

**理由**: 将"做什么"（AI Agent 的领域知识）与"管理什么"（CLI 的状态管理）分离。CLI 不再需要硬编码分析逻辑。

### Decision 8: 目录结构重组

当前结构：
```
src/dm2/
├── cli/main.py        ← 所有 CLI 命令
├── cognitive/         ← Cynefin + 6W
├── engine/            ← 视图生成 + Pipeline
├── kernel/            ← 知识索引
├── llm/               ← LLM 客户端
├── reasoning/         ← 一致性检查
└── utils/             ← 工具函数
```

新结构：
```
src/dm2/
├── cli/
│   ├── main.py            ← CLI 入口 + --json 格式化
│   └── commands/          ← 各命令实现（拆分 main.py）
├── core/
│   ├── agent/             ← Instructions Engine（指令生成）
│   ├── artifacts/         ← Artifact Graph（制品依赖图）
│   ├── changes/           ← Change Manager（变更管理）
│   ├── knowledge/         ← Knowledge API（知识检索接口）
│   └── pipeline/          ← Pipeline Orchestrator v2
├── engine/                ← 保留：视图生成器、模板填充器
├── cognitive/             ← 保留：Cynefin、6W 分析器
├── llm/                   ← 保留：Provider 接口
├── reasoning/             ← 保留：一致性检查、模式匹配
└── utils/                 ← 保留：工具函数
```

**理由**: 核心新增功能（agent/artifacts/changes/knowledge）是框架的差异化能力，集中在 `core/` 下便于理解和维护。

## Risks / Trade-offs

- **[中] 框架复杂度增加**: 新增 4 个核心模块，代码量预计增加 50-80%。→ 分 phase 实现，每个 phase 产出可用的能力增量，不追求一步到位。
- **[低] --json 输出破坏向后兼容**: 现有脚本如果解析 CLI 输出文本会失败。→ `--json` 是 opt-in flag，默认输出保持人类可读格式，完全向后兼容。
- **[低] Pipeline 重构风险**: 当前 Pipeline 已在生产可用，重构可能引入回归。→ V2 Pipeline 与 V1 并行存在（`dm2 run` vs `dm2 change`），V1 保持可用直到 V2 稳定。
- **[低] 学习成本**: 团队需要理解新的 AI Agent 协作模式。→ 在 README 中补充 AI Agent 工作流文档和示例。

## Migration Plan

分三个 Phase 实施，每个 Phase 产出可独立使用的能力：

**Phase 1: Foundation（Agent Interface + Knowledge API）**
- 所有现有命令添加 `--json` 标志
- 新增 `dm2 knowledge *` 命令组
- 不影响现有功能

**Phase 2: Core Engine（Artifact Graph + Instructions Engine + Change Manager）**
- 新增 `src/dm2/core/artifacts/` 和 `src/dm2/core/agent/`
- 新增 `dm2 change *` 命令组
- 现有的 `dm2-changes/` 目录继续工作

**Phase 3: Pipeline v2（Agent-driven Pipeline）**
- 重写 Pipeline Orchestrator 为 Agent 驱动
- `dm2 run` 变为 Agent-driven 模式
- 旧 Pipeline 代码保留在 `src/dm2/engine/pipeline/v1/`
