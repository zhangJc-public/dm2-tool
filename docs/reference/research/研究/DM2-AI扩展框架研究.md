# DM2-AI 扩展框架研究报告

> ⚠️ **本文档为前瞻性研究，非 DoDAF 2.02 标准内容**。包含对 AI/LLM/Agent 架构描述的扩展思考，仅供探索参考。
>
> **研究目标**：扩展 DoDAF Meta-Model 2.0 以支持 AI/LLM/Agent 系统架构描述
> 
> **研究日期**：2026-04-16
> 
> **参考来源**：
> - AI Agent Orchestration Patterns (Microsoft Azure Architecture Center, 2025-02)
> - The Orchestration of Multi-Agent Systems (arXiv:2601.13671, 2026-01)
> - Enterprise AI Knowledge Base with RAG (Xenoss, 2025-07)
> - DoDAF Architecture Framework Version 2.02 (2010-08)
> - 文学/领域知识/DM2/DM2数据组完整定义.md
> - 文学/领域知识/DM2/DM2类图分析.md

---

## 一、问题分析

### 1.1 DM2 发布背景

DoDAF v2.02 发布于 **2010年8月**，彼时：
- AI 主要是规则引擎和专家系统
- 大模型（LLM）尚未出现
- 智能体（Agent）概念停留在学术研究阶段
- 云计算正在兴起，SaaS 模式刚刚起步

### 1.2 当前 AI 系统的架构特征

基于 2025-2026 年最新研究，现代 AI 系统呈现以下架构特征：

#### 核心组件

| 组件类别 | 核心组件 | DM2 缺失 |
|---------|---------|---------|
| **LLM 引擎** | 大语言模型、推理引擎、提示管理器 | ❌ 无对应概念 |
| **知识系统** | 向量数据库、Embedding 模型、RAG Pipeline | ❌ 无对应概念 |
| **Agent 框架** | 多 Agent 编排器、状态管理、规划引擎 | ❌ 无对应概念 |
| **通信协议** | MCP (Model Context Protocol)、A2A (Agent-to-Agent) | ❌ 无对应概念 |
| **工具系统** | API 网关、函数调用、工具注册中心 | ⚠️ 部分覆盖 |

#### AI Agent 编排模式

| 模式             | 描述        | DM2 如何表达                 |
| -------------- | --------- | ------------------------ |
| **Sequential** | 线性管道，串联处理 | Activity + Resource Flow |
| **Concurrent** | 并行执行，结果聚合 | Activity (parallel) + ?  |
| **Group Chat** | 群聊协作，共识构建 | Activity + ?             |
| **Handoff**    | 动态移交，委托执行 | Activity + ?             |
| **Magentic**   | 计划构建，任务账本 | Activity + Project?      |

#### 多智能体系统架构

```
┌─────────────────────────────────────────────────────────────┐
│          多智能体系统架构 (arXiv:2601.13671)                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │              专业化智能体层                              │ │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐                │ │
│  │  │ Worker  │  │ Service │  │ Support │                │ │
│  │  │ Agents  │  │ Agents  │  │ Agents  │                │ │
│  │  └─────────┘  └─────────┘  └─────────┘                │ │
│  └───────────────────────────────────────────────────────┘ │
│                           ↑                                 │
│  ┌───────────────────────────────────────────────────────┐ │
│  │              编排层（Orchestration Layer）              │ │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐ │ │
│  │  │ 规划与   │  │ 执行与   │  │ 状态与   │  │ 质量与   │ │ │
│  │  │ 策略     │  │ 控制     │  │ 知识     │  │ 运维     │ │ │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘ │ │
│  └───────────────────────────────────────────────────────┘ │
│                           ↑                                 │
│  ┌───────────────────────────────────────────────────────┐ │
│  │              通信协议层                                  │ │
│  │  ┌─────────────────┐  ┌─────────────────┐              │ │
│  │  │      MCP        │  │      A2A        │              │ │
│  │  │ (工具/数据访问)  │  │ (智能体间协作)  │              │ │
│  │  └─────────────────┘  └─────────────────┘              │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 扩展需求总结

| 扩展维度         | 当前 DM2 能力          | 扩展需求                                    |
| ------------ | ------------------ | --------------------------------------- |
| **AI 实体建模**  | 仅支持 System/Service | 需要新增 AIPerformer、AIResource、AIKnowledge |
| **Agent 编排** | 无编排概念              | 需要 Agent、Orchestrator、Protocol          |
| **知识系统**     | 仅 Information/Data | 需要 VectorStore、Embedding、RAG            |
| **工具调用**     | 有限的 Service        | 需要 ToolRegistry、FunctionCall            |
| **交互协议**     | 无                  | 需要 MCP、A2A 等协议建模                        |
| **动态行为**     | 静态建模               | 需要 StateMachine、Plan、Memory             |
| **度量指标**     | MOE/MOP            | 需要 HallucinationRate、ContextPrecision 等 |

---

## 二、DM2-AI 扩展框架设计

### 2.1 总体架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     DM2-AI 扩展框架 (DM2-AI Extension)                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    DM2 Core (v2.02 保留)                           │   │
│  │                                                                   │   │
│  │  Activity │ Resource │ Performer │ Capability │ Measure │ ...   │   │
│  │                                                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    AI Extension Layer                             │   │
│  │                                                                   │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │   │
│  │  │   AI Entity      │  │  AI Knowledge   │  │  AI Interaction │   │   │
│  │  │   Extension     │  │   Extension     │  │   Extension     │   │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘   │   │
│  │                                                                   │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │   │
│  │  │  AI Behavior    │  │  AI Orchestration│  │  AI Governance  │   │   │
│  │  │   Extension     │  │   Extension     │  │   Extension     │   │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘   │   │
│  │                                                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 六大扩展模块

```
DM2-AI Extension
│
├── AI Entity Extension（AI 实体扩展）
│   ├── AI Model（AI 模型）
│   ├── AI Agent（智能体）
│   ├── AI Knowledge（AI 知识资源）
│   └── AI Tool（AI 工具）
│
├── AI Knowledge Extension（AI 知识扩展）
│   ├── Vector Store（向量存储）
│   ├── Embedding Model（嵌入模型）
│   ├── Knowledge Graph（知识图谱）
│   └── RAG Pipeline（RAG 流水线）
│
├── AI Interaction Extension（AI 交互扩展）
│   ├── Protocol（协议）
│   ├── MCP Protocol（MCP 协议）
│   ├── A2A Protocol（A2A 协议）
│   └── Message（消息）
│
├── AI Behavior Extension（AI 行为扩展）
│   ├── Plan（规划）
│   ├── State（状态）
│   ├── Memory（记忆）
│   └── Reflection（反思）
│
├── AI Orchestration Extension（AI 编排扩展）
│   ├── Orchestrator（编排器）
│   ├── Orchestration Pattern（编排模式）
│   ├── Task Ledger（任务账本）
│   └── Result Aggregator（结果聚合器）
│
└── AI Governance Extension（AI 治理扩展）
    ├── Hallucination Metric（幻觉度量）
    ├── Safety Guardrail（安全护栏）
    ├── Compliance Rule（合规规则）
    └── Audit Trail（审计追踪）
```

---

## 三、核心概念扩展

### 3.1 AI Entity Extension（AI 实体扩展）

#### 3.1.1 AI Model（AI 模型）

**定义**：A computational system that processes inputs to generate outputs, typically through learned parameters from training data.

**继承**：Resource 的特殊类型

```yaml
AI Model Type
├── <<Type>> AIBaseModelType
│   ├── <<Type>> LLMType  # 大语言模型
│   │   ├── GPTModel
│   │   ├── ClaudeModel
│   │   └── LlamaModel
│   ├── <<Type>> EmbeddingModelType  # 嵌入模型
│   │   ├── OpenAIEmbedding
│   │   └── BGEEmbedding
│   ├── <<Type>> VisionModelType  # 视觉模型
│   └── <<Type>> MultimodalModelType  # 多模态模型
│
└── <<Individual>> AIBaseModel
    └── AI Model 实例
```

**核心属性**：

| 属性 | 类型 | 说明 |
|------|------|------|
| modelName | String | 模型名称 |
| modelVersion | String | 模型版本 |
| contextWindow | Integer | 上下文窗口大小 |
| parameters | Integer | 参数数量（10B、70B 等） |
| capabilities | List<String> | 能力列表 |
| limitations | List<String> | 限制条件 |
| deploymentType | Enum | cloud/on-premise/edge |

**核心关系**：

| 关系 | 说明 |
|------|------|
| aiModelProvidesCapability | AI 模型提供能力 |
| aiModelRequiresCompute | AI 模型需要计算资源 |
| aiModelConsumesToken | AI 模型消耗 Token |

#### 3.1.2 AI Agent（智能体）

**定义**：An autonomous or semi-autonomous entity that perceives environment, makes decisions, and takes actions to achieve goals.

**继承**：Performer 的特殊类型

```yaml
AI Agent Type
├── <<Type>> AIAgentType
│   ├── <<Type>> WorkerAgentType  # 执行智能体
│   │   ├── StatelessWorkerAgent
│   │   └── StatefulWorkerAgent
│   ├── <<Type>> ServiceAgentType  # 服务智能体
│   │   ├── QA Agent
│   │   ├── DiagnosticAgent
│   │   └── HealingAgent
│   ├── <<Type>> SupportAgentType  # 支持智能体
│   │   ├── MonitoringAgent
│   │   └── AnalyticsAgent
│   └── <<Type>> OrchestratorAgentType  # 编排智能体
│       ├── SequentialOrchestrator
│       ├── ConcurrentOrchestrator
│       ├── GroupChatManager
│       └── MagenticManager
│
└── <<Individual>> AIAgent
    └── AI Agent 实例
```

**核心属性**：

| 属性 | 类型 | 说明 |
|------|------|------|
| agentName | String | 智能体名称 |
| agentRole | String | 智能体角色描述 |
| autonomyLevel | Enum | autonomy/semi-autonomy/guided |
| specialization | String | 专业领域 |
| llmConfig | LLMConfig | 使用的 LLM 配置 |
| toolSet | List<Tool> | 可用工具集 |
| memoryCapacity | Integer | 记忆容量 |

**核心关系**：

| 关系 | 说明 |
|------|------|
| agentUsesModel | 智能体使用 AI 模型 |
| agentHasTool | 智能体拥有工具 |
| agentFollowsProtocol | 智能体遵循协议 |
| agentCommunicatesWith | 智能体与其他智能体通信 |
| agentMaintainsState | 智能体维护状态 |
| agentReceivesTask | 智能体接收任务 |

#### 3.1.3 AI Knowledge（AI 知识资源）

**定义**：Structured or unstructured information used by AI systems for reasoning, retrieval, or training.

**继承**：Resource 的特殊类型

```yaml
AI Knowledge Type
├── <<Type>> AIKnowledgeType
│   ├── <<Type>> VectorStoreType  # 向量存储
│   │   ├── PineconeStore
│   │   ├── WeaviateStore
│   │   └── Neo4jVectorStore
│   ├── <<Type>> KnowledgeGraphType  # 知识图谱
│   │   └── Neo4jGraph
│   ├── <<Type>> DocumentCorpusType  # 文档语料库
│   │   ├── MarkdownCorpus
│   │   └── PDFCorpus
│   └── <<Type>> TrainingDataType  # 训练数据
│       ├── StructuredTrainingData
│       └── UnstructuredTrainingData
│
└── <<Individual>> AIKnowledge
    └── AI Knowledge 实例
```

**核心属性**：

| 属性 | 类型 | 说明 |
|------|------|------|
| knowledgeType | Enum | vector/graph/document/training |
| sourceSystem | String | 来源系统 |
| lastUpdated | DateTime | 最后更新时间 |
| embeddingModel | String | 使用的嵌入模型 |
| indexMethod | String | 索引方法 |
| accessControl | ACL | 访问控制 |

**核心关系**：

| 关系                         | 说明              |
| -------------------------- | --------------- |
| knowledgeIndexedByModel    | 知识被嵌入模型索引       |
| knowledgeQueriedByAgent    | 知识被智能体查询        |
| knowledgeStoredInVectorDB  | 知识存储在向量数据库      |
| knowledgePartOfRAGPipeline | 知识是 RAG 流水线的一部分 |

#### 3.1.4 AI Tool（AI 工具）

**定义**：A callable function or service that an AI Agent uses to interact with external systems or perform specific actions.

```yaml
AI Tool Type
├── <<Type>> AIToolType
│   ├── <<Type>> FunctionCallType  # 函数调用
│   ├── <<Type>> APIGatewayType  # API 网关
│   ├── <<Type>> WebSearchToolType  # 网页搜索
│   ├── <<Type>> DatabaseToolType  # 数据库查询
│   ├── <<Type>> CodeInterpreterType  # 代码解释器
│   └── <<Type>> FileSystemToolType  # 文件系统
│
└── <<Individual>> AITool
    └── AI Tool 实例
```

**核心属性**：

| 属性 | 类型 | 说明 |
|------|------|------|
| toolName | String | 工具名称 |
| toolDescription | String | 工具描述 |
| inputSchema | JSONSchema | 输入模式 |
| outputSchema | JSONSchema | 输出模式 |
| requiresAuth | Boolean | 是否需要认证 |
| rateLimit | RateLimit | 速率限制 |

---

### 3.2 AI Interaction Extension（AI 交互扩展）

#### 3.2.1 Protocol（协议）

**定义**：A set of rules governing communication and interaction between AI entities.

```yaml
Protocol Type
├── <<Type>> ProtocolType
│   ├── <<Type>> MCPProtocolType  # Model Context Protocol
│   │   ├── ToolInvocation
│   │   ├── ResourceAccess
│   │   └── PromptTemplate
│   ├── <<Type>> A2AProtocolType  # Agent-to-Agent
│   │   ├── TaskDelegation
│   │   ├── ResultSharing
│   │   └── StatusUpdate
│   └── <<Type>> CustomProtocolType
│
└── <<Individual>> Protocol
    └── Protocol 实例
```

**核心属性**：

| 属性 | 类型 | 说明 |
|------|------|------|
| protocolName | String | 协议名称 |
| protocolVersion | String | 协议版本 |
| transportLayer | Enum | http/grpc/websocket |
| securityMechanism | String | 安全机制 |
| messageFormat | Enum | json/protobuf |

**核心关系**：

| 关系 | 说明 |
|------|------|
| protocolGovernsAgentInteraction | 协议约束智能体交互 |
| protocolImplementsMCP | 协议实现 MCP |
| protocolImplementsA2A | 协议实现 A2A |

#### 3.2.2 Message（消息）

**定义**：A structured unit of communication exchanged between AI entities.

```yaml
Message Type
├── <<Type>> MessageType
│   ├── <<Type>> TaskMessage  # 任务消息
│   ├── <<Type>> ResultMessage  # 结果消息
│   ├── <<Type>> StatusMessage  # 状态消息
│   ├── <<Type>> ErrorMessage  # 错误消息
│   └── <<Type>> HeartbeatMessage  # 心跳消息
│
└── <<Individual>> Message
    └── Message 实例
```

**核心属性**：

| 属性 | 类型 | 说明 |
|------|------|------|
| messageId | UUID | 消息 ID |
| messageType | Enum | task/result/status/error |
| sender | Agent | 发送方 |
| receiver | Agent | 接收方 |
| payload | Any | 消息内容 |
| timestamp | DateTime | 时间戳 |
| correlationId | UUID | 关联 ID |

---

### 3.3 AI Behavior Extension（AI 行为扩展）

#### 3.3.1 Plan（规划）

**定义**：A structured representation of steps or actions to achieve a goal.

```yaml
Plan Type
├── <<Type>> PlanType
│   ├── <<Type>> GoalDecompositionPlan  # 目标分解计划
│   ├── <<Type>> TaskSequencePlan  # 任务序列计划
│   └── <<Type>> ContingencyPlan  # 应急计划
│
└── <<Individual>> Plan
    └── Plan 实例
```

**核心属性**：

| 属性 | 类型 | 说明 |
|------|------|------|
| planId | UUID | 计划 ID |
| goal | String | 目标描述 |
| steps | List<Step> | 步骤列表 |
| dependencies | DAG | 依赖关系图 |
| estimatedCost | Cost | 预估成本 |
| createdBy | Agent | 创建者 |
| creationTime | DateTime | 创建时间 |

**核心关系**：

| 关系 | 说明 |
|------|------|
| planCreatedByAgent | 计划由智能体创建 |
| planDecomposedFromGoal | 计划分解自目标 |
| planExecutedByAgent | 计划由智能体执行 |
| planContainsTask | 计划包含任务 |

#### 3.3.2 State（状态）

**定义**：The current condition or context of an AI Agent during execution.

```yaml
State Type
├── <<Type>> AIStateType
│   ├── <<Type>> WorkingMemory  # 工作记忆
│   ├── <<Type>> LongTermMemory  # 长期记忆
│   ├── <<Type>> ConversationHistory  # 对话历史
│   └── <<Type>> ExecutionContext  # 执行上下文
│
└── <<Individual>> State
    └── State 实例
```

**核心属性**：

| 属性 | 类型 | 说明 |
|------|------|------|
| stateId | UUID | 状态 ID |
| stateType | Enum | working/longterm/conversation |
| content | Any | 状态内容 |
| lastUpdated | DateTime | 最后更新时间 |
| ttl | Duration | 生存时间 |

**核心关系**：

| 关系 | 说明 |
|------|------|
| agentMaintainsState | 智能体维护状态 |
| stateAssociatedWithTask | 状态与任务关联 |
| statePersistedToMemory | 状态持久化到记忆 |

#### 3.3.3 Memory（记忆）

**定义**：Persistent storage of information that enables AI Agents to retain and recall past experiences.

```yaml
Memory Type
├── <<Type>> MemoryType
│   ├── <<Type>> EpisodicMemory  # 情景记忆
│   ├── <<Type>> SemanticMemory  # 语义记忆
│   ├── <<Type>> ProceduralMemory  # 程序性记忆
│   └── <<Type>> VectorMemory  # 向量记忆
│
└── <<Individual>> Memory
    └── Memory 实例
```

**核心属性**：

| 属性 | 类型 | 说明 |
|------|------|------|
| memoryType | Enum | episodic/semantic/procedural/vector |
| capacity | Integer | 容量限制 |
| retentionPeriod | Duration | 保留期限 |
| embeddingModel | String | 嵌入模型 |

---

### 3.4 AI Orchestration Extension（AI 编排扩展）

#### 3.4.1 Orchestrator（编排器）

**定义**：A component that coordinates multiple AI Agents to accomplish complex tasks.

```yaml
Orchestrator Type
├── <<Type>> OrchestratorType
│   ├── <<Type>> SequentialOrchestrator  # 顺序编排
│   ├── <<Type>> ConcurrentOrchestrator  # 并发编排
│   ├── <<Type>> GroupChatOrchestrator  # 群聊编排
│   ├── <<Type>> HandoffOrchestrator  # 移交编排
│   └── <<Type>> MagenticOrchestrator  # 磁力编排
│
└── <<Individual>> Orchestrator
    └── Orchestrator 实例
```

**核心属性**：

| 属性 | 类型 | 说明 |
|------|------|------|
| orchestratorType | Enum | sequential/concurrent/... |
| managedAgents | List<Agent> | 管理的智能体 |
| coordinationStrategy | String | 协调策略 |
| failureHandling | Enum | retry/rollback/fallback |

**核心关系**：

| 关系 | 说明 |
|------|------|
| orchestratorManagesAgent | 编排器管理智能体 |
| orchestratorCreatesTaskLedger | 编排器创建任务账本 |
| orchestratorAggregatesResults | 编排器聚合结果 |

#### 3.4.2 Orchestration Pattern（编排模式）

**定义**：A reusable pattern describing how multiple AI Agents collaborate.

| 模式 | 描述 | DM2-AI 表达 |
|------|------|-------------|
| **Sequential** | 串联处理，预定义顺序 | Activity Pipeline + Control Flow |
| **Concurrent** | 并行执行，结果聚合 | Parallel Activities + Fan-out/Fan-in |
| **Group Chat** | 群聊协作，共识构建 | Group Activity + Shared Context |
| **Handoff** | 动态移交，专业委托 | Dynamic Routing + Task Transfer |
| **Magentic** | 计划构建，任务账本 | Planning + Task Ledger |

#### 3.4.3 Task Ledger（任务账本）

**定义**：A dynamic record of tasks, their status, and dependencies in an orchestration.

```yaml
Task Ledger Type
├── <<Type>> TaskLedgerType
│   └── <<Type>> TaskEntryType
│       ├── TaskId
│       ├── TaskStatus  # pending/in_progress/completed/failed
│       ├── TaskAssignee
│       ├── TaskDependencies
│       └── TaskResult
│
└── <<Individual>> TaskLedger
    └── Task Ledger 实例
```

---

### 3.5 AI Knowledge Extension（AI 知识扩展）

#### 3.5.1 RAG Pipeline（RAG 流水线）

**定义**：A workflow that combines retrieval and generation for AI-powered knowledge问答.

```yaml
RAG Pipeline Type
├── <<Type>> RAGPipelineType
│   ├── <<Type>> IngestionStage  # 摄入阶段
│   │   ├── DocumentLoader
│   │   ├── TextSplitter
│   │   └── EmbeddingGenerator
│   ├── <<Type>> RetrievalStage  # 检索阶段
│   │   ├── QueryEncoder
│   │   ├── VectorSearcher
│   │   └── Reranker
│   └── <<Type>> GenerationStage  # 生成阶段
│       ├── ContextAssembler
│       └── LLMGenerator
│
└── <<Individual>> RAGPipeline
    └── RAG Pipeline 实例
```

**核心属性**：

| 属性 | 类型 | 说明 |
|------|------|------|
| pipelineType | Enum | vanilla/hybrid/graph/agentic |
| chunkSize | Integer | 分块大小 |
| chunkOverlap | Integer | 分块重叠 |
| embeddingModel | String | 嵌入模型 |
| retrievalTopK | Integer | 检索数量 |

**核心关系**：

| 关系 | 说明 |
|------|------|
| pipelineIngestDocument | 流水线摄入文档 |
| pipelineQueriesVectorStore | 流水线查询向量存储 |
| pipelineGeneratesWithLLM | 流水线使用 LLM 生成 |

#### 3.5.2 Vector Store（向量存储）

**定义**：A specialized database for storing and retrieving high-dimensional vectors.

```yaml
Vector Store Type
├── <<Type>> VectorStoreType
│   ├── Pinecone
│   ├── Weaviate
│   ├── Milvus
│   ├── ChromaDB
│   └── Neo4j (with vector)
│
└── <<Individual>> VectorStore
    └── Vector Store 实例
```

**核心属性**：

| 属性 | 类型 | 说明 |
|------|------|------|
| storeType | String | 存储类型 |
| indexType | String | 索引类型 (HNSW/IVF) |
| dimension | Integer | 向量维度 |
| metric | Enum | cosine/euclidean/dot |

---

### 3.6 AI Governance Extension（AI 治理扩展）

#### 3.6.1 Safety Guardrail（安全护栏）

**定义**：Constraints and validations that ensure AI system behavior remains within acceptable bounds.

```yaml
Safety Guardrail Type
├── <<Type>> SafetyGuardrailType
│   ├── <<Type>> InputValidation  # 输入验证
│   ├── <<Type>> OutputFilter  # 输出过滤
│   ├── <<Type>> RateLimiter  # 速率限制
│   ├── <<Type>> ContentModeration  # 内容审核
│   └── <<Type>> AccessControl  # 访问控制
│
└── <<Individual>> SafetyGuardrail
    └── Safety Guardrail 实例
```

**核心关系**：

| 关系 | 说明 |
|------|------|
| guardrailValidatesInput | 护栏验证输入 |
| guardrailFiltersOutput | 护栏过滤输出 |
| guardrailEnforcesPolicy | 护栏强制策略 |

#### 3.6.2 AI Metric（AI 度量）

**定义**：Metrics specific to AI system performance and quality.

```yaml
AI Metric Type
├── <<Type>> AIMetricType
│   ├── <<Type>> QualityMetric
│   │   ├── HallucinationRate  # 幻觉率
│   │   ├── ContextPrecision  # 上下文精度
│   │   ├── AnswerRelevance  # 答案相关性
│   │   └── Faithfulness  # 忠实度
│   ├── <<Type>> PerformanceMetric
│   │   ├── Latency
│   │   ├── Throughput
│   │   └── TokenUsage
│   └── <<Type>> SafetyMetric
│       ├── ToxicityScore
│       └── PIILeakageRate
```

---

## 四、核心设计原则：继承而非独立

### 4.1 错误的做法 vs 正确的做法

#### ❌ 错误：创建独立数据组

```
DM2 Core
├── Performer, Resource, Activity, ...
└── AIExtension（独立数据组）  ❌ 破坏 DM2 原有结构
```

**问题**：
- DM2 官方定义只有 **14 个 Data Groups**，不能随意增加
- 独立数据组会破坏 DM2 的语义完整性
- 与 DoDAF v2.02 标准不兼容

#### ✅ 正确：通过类型继承扩展

```
DM2 Core
├── Performer
│   ├── System / Service
│   │   └── AIAgent（作为 System/Service 的特殊类型）
│   └── ...
│
├── Resource
│   ├── Information / Materiel
│   │   ├── AI Model（作为 Materiel 的特殊类型）
│   │   └── Vector Store（作为 Information 的特殊类型）
│   └── ...
│
├── Activity
│   └── RAGActivity（RAG 处理活动）
│
├── Agreement / Rule
│   ├── MCPProtocol（MCP 协议）
│   └── SafetyGuardrail（安全护栏）
│
└── Measure
    └── AIMeasureType（AI 度量类型）
```

### 4.2 DM2 的扩展机制

DM2 基于 **IDEAS 本体**，支持以下扩展方式：

| 扩展方式 | DM2 语法 | AI 扩展应用 |
|---------|---------|-----------|
| **Super-Subtype** | `<<Type>>` 继承 | `System → AIAgent` |
| **IndividualType** | `<<IndividualType>>` | `LLMType → GPT4-Instance` |
| **Composition** | 整体-部分关系 | `Orchestrator → Agent[]` |
| **Association** | 关联关系 | `Agent ↔ VectorStore` |

### 4.3 AI 概念到 DM2 的映射表

| AI 概念 | DM2 归属 | 扩展类型 | 继承关系 |
|---------|---------|---------|---------|
| **AI Agent** | Performer | <<Type>> | `System → AISystem → AIAgent` |
| **LLM / AI Model** | Resource | <<Type>> | `Materiel → AIModel → LLMType` |
| **Vector Store** | Resource | <<Type>> | `Information → AIKnowledge → VectorStore` |
| **RAG Pipeline** | Activity | <<Type>> | `Activity → AIProcessingActivity → RAGActivity` |
| **MCP / A2A 协议** | Agreement | <<Type>> | `Agreement → AIProtocol → MCPProtocol` |
| **Tool / Function** | Service | <<Type>> | `Service → AIService → ToolService` |
| **Orchestrator** | Performer | <<Type>> | `System → AISystem → AIOrchestrator` |
| **Safety Guardrail** | Rule | <<Type>> | `Rule → AISafetyRule → GuardrailRule` |
| **AI 行为度量** | Measure | <<Type>> | `Measure → AIMeasure → HallucinationRate` |
| **Plan / 规划** | Activity | 组合关系 | `Agent creates Plan` |
| **State / 状态** | Condition | 扩展属性 | `Agent maintains State` |
| **Memory / 记忆** | Resource | <<Type>> | `Information → AIMemory → VectorMemory` |

---

## 五、扩展类型层级定义

### 5.1 Performer 扩展：AI Agent

```yaml
# DM2 Performer 扩展
Performer
  ↑
System (DM2 Core)
  ↑
AISystem (AI Extension)
  ├── ↑
  │   AIAgent (AI 智能体)
  │   │   ├── ↑
  │   │   │   WorkerAgentType
  │   │   │   ├── StatelessWorkerAgent
  │   │   │   └── StatefulWorkerAgent
  │   │   │
  │   │   ├── ↑
  │   │   │   ServiceAgentType
  │   │   │   ├── QAAgent
  │   │   │   ├── DiagnosticAgent
  │   │   │   └── HealingAgent
  │   │   │
  │   │   └── ↑
  │   │       OrchestratorAgentType
  │   │           ├── SequentialOrchestrator
  │   │           ├── ConcurrentOrchestrator
  │   │           ├── GroupChatManager
  │   │           └── MagenticManager
  │   │
  │   └── ↑
  │       AIOrchestrator (编排器)
  │
  └── ↑
      AIService (AI 服务)
          ├── LLMWrapper
          ├── ToolService
          └── RAGService
```

### 5.2 Resource 扩展：AI Model 与 Knowledge

```yaml
# DM2 Resource 扩展
Resource
  ├── ↑
  │   Materiel (DM2 Core)
  │   └── ↑
  │       AIModel (AI 模型)
  │           ├── ↑
  │           │   LLMType (大语言模型)
  │           │   ├── GPTModel
  │           │   ├── ClaudeModel
  │           │   └── LlamaModel
  │           │
  │           ├── ↑
  │           │   EmbeddingModelType (嵌入模型)
  │           │   ├── OpenAIEmbedding
  │           │   └── BGEEmbedding
  │           │
  │           └── ↑
  │               MultimodalModelType (多模态模型)
  │
  ├── ↑
  │   Information (DM2 Core)
  │   └── ↑
  │       AIKnowledge (AI 知识资源)
  │           ├── ↑
  │           │   VectorStoreType (向量存储)
  │           │   ├── PineconeStore
  │           │   ├── WeaviateStore
  │           │   └── MilvusStore
  │           │
  │           ├── ↑
  │           │   KnowledgeGraphType (知识图谱)
  │           │
  │           └── ↑
  │               DocumentCorpusType (文档语料库)
  │
  └── ↑
      AIMemory (AI 记忆)
          ├── EpisodicMemory
          ├── SemanticMemory
          └── VectorMemory
```

### 5.3 Activity 扩展：AI 行为与 RAG

```yaml
# DM2 Activity 扩展
Activity (DM2 Core)
  ↑
AIProcessingActivity (AI 处理活动)
  ├── ↑
  │   InferenceActivity (推理活动)
  ├── ↑
  │   RAGActivity (RAG 处理)
  │       ├── IngestionStage
  │       │   ├── DocumentLoader
  │       │   ├── TextSplitter
  │       │   └── EmbeddingGenerator
  │       ├── RetrievalStage
  │       │   ├── QueryEncoder
  │       │   ├── VectorSearcher
  │       │   └── Reranker
  │       └── GenerationStage
  │           ├── ContextAssembler
  │           └── LLMGenerator
  │
  └── ↑
      OrchestrationActivity (编排活动)
```

### 5.4 Agreement/Rule 扩展：协议与治理

```yaml
# DM2 Agreement / Rule 扩展
Agreement (DM2 Core)
  ↑
AIProtocol (AI 协议)
  ├── ↑
  │   MCPProtocolType (MCP 协议)
  │       ├── ToolInvocation
  │       ├── ResourceAccess
  │       └── PromptTemplate
  │
  └── ↑
      A2AProtocolType (A2A 协议)
          ├── TaskDelegation
          ├── ResultSharing
          └── StatusUpdate

Rule (DM2 Core)
  ↑
AISafetyRule (AI 安全规则)
  ├── InputValidation
  ├── OutputFilter
  ├── ContentModeration
  └── RateLimiter
```

### 5.5 Measure 扩展：AI 度量

```yaml
# DM2 Measure 扩展
Measure (DM2 Core)
  ↑
AIMeasureType (AI 度量类型)
  ├── ↑
  │   QualityMetric (质量度量)
  │       ├── HallucinationRate (幻觉率)
  │       ├── ContextPrecision (上下文精度)
  │       ├── AnswerRelevance (答案相关性)
  │       └── Faithfulness (忠实度)
  │
  ├── ↑
  │   PerformanceMetric (性能度量)
  │       ├── ResponseLatency
  │       ├── Throughput
  │       └── TokenUsage
  │
  └── ↑
      SafetyMetric (安全度量)
          ├── ToxicityScore
          └── PIILeakageRate
```

---

## 六、扩展关系模式

### 6.1 核心关系定义

```yaml
# AI Agent 相关关系
agentUsesModel: AIAgent → AIModel
agentHasTool: AIAgent → AIService (ToolService)
agentFollowsProtocol: AIAgent → AIProtocol
agentCommunicatesVia: AIAgent ↔ AIAgent (A2A)
agentDelegatesTo: AIAgent → AIAgent (Handoff)
agentCreatesPlan: AIAgent → Activity (Plan)
agentMaintainsState: AIAgent → Condition (AIState)
agentRetrievesFrom: AIAgent → VectorStore

# 编排关系
orchestratorCoordinates: AIOrchestrator → AIAgent
orchestratorCreatesLedger: AIOrchestrator → Project (TaskLedger)
orchestratorUsesPattern: AIOrchestrator → Capability (Pattern)

# RAG Pipeline 关系
pipelineIngestDocument: RAGActivity → AIKnowledge (Document)
pipelineStoreVector: RAGActivity → VectorStore
pipelineQueryLLM: RAGActivity → AIModel
```

---

## 六、实施建议

> **设计原则更新（2026-04-17）**：AI 扩展应通过 **Subtype 继承** 而非独立数据组实现。

### 6.1 扩展策略

| 阶段 | 内容 | 优先级 |
|------|------|-------|
| **Phase 1** | 核心扩展：Performer/Resource/Activity Subtype | P0 |
| **Phase 2** | 编排扩展：Orchestration Pattern、Task Ledger | P1 |
| **Phase 3** | 治理扩展：Safety Guardrail、AI Metric | P2 |
| **Phase 4** | 视图扩展：AI-specific 视图定义 | P3 |

### 6.2 与现有 DM2 的兼容性

**向后兼容原则**：
- 保留所有 DM2 Core 概念和关系
- AI Extension 通过类型扩展（Subtype）实现
- 现有视图和工具无需修改
- 新视图可选择性采用

### 6.3 下一步研究课题

1. **DM2-AI Schema 形式化定义**：使用 OWL/RDFS 形式化定义扩展
2. **视图模板设计**：为每个 AI-specific 视图设计模板
3. **工具支持评估**：评估现有 DoDAF 工具对 AI Extension 的支持
4. **案例研究**：使用 DM2-AI 描述实际 AI 系统

---

## 七、与 DM2 Core 的集成

### 7.1 概念映射原则

**核心原则**：不创建新数据组，通过现有 DM2 概念的 **Subtype（子类型）** 实现扩展。

| DM2 Core 概念 | AI 扩展方式 | 继承关系 | 示例 |
:|--------------|----------|---------|------|
| **Activity** | Subtype | `Activity → AIProcessingActivity` | `RAGActivity`, `InferenceActivity` |
| **Performer** | Subtype | `System → AISystem → AIAgent` | `WorkerAgent`, `Orchestrator` |
| **Resource** | Subtype | `Materiel → AIModel` | `LLMType`, `EmbeddingModelType` |
| **Resource** | Subtype | `Information → AIKnowledge` | `VectorStore`, `KnowledgeGraph` |
| **Agreement** | Subtype | `Agreement → AIProtocol` | `MCPProtocol`, `A2AProtocol` |
| **Rule** | Subtype | `Rule → AISafetyRule` | `SafetyGuardrail`, `AlignmentRule` |
| **Measure** | Subtype | `Measure → AIMeasureType` | `HallucinationRate`, `Latency` |
| **Capability** | 组合扩展 | `Capability → AI Capability` | `LLMCapability`, `ReasoningCapability` |

### 7.2 视图扩展

| 扩展视图          | 对应 DM2 视图 | 描述        |
| ------------- | --------- | --------- |
| **AV-AI-1**   | AV-1      | AI 架构概览   |
| **OV-AI-2**   | OV-2      | AI 资源流图   |
| **SV-AI-1**   | SV-1      | AI 系统界面描述 |
| **SvcV-AI-1** | SvcV-1    | AI 服务描述   |
| **CV-AI-1**   | CV-1      | AI 能力愿景   |
| **CV-AI-2**   | CV-2      | AI 能力分类   |

**重要**：扩展视图仍然映射到标准 DoDAF 视图编号，只是内容聚焦于 AI 实体。

### 7.3 集成架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DM2-AI 完整架构集成图                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                           Vision / Goal                                 │
│                                 ↑                                       │
│                           Capability                                    │
│                                 ↑                                       │
│         ┌───────────────────────┼───────────────────────┐              │
│         │                       │                       │              │
│    Activity              AI Behavior              Project               │
│    (DM2 Core)           (Extension)              (DM2 Core)             │
│         │                       │                       │              │
│         │              ┌────────┴────────┐             │              │
│         │              │                 │             │              │
│    ┌────┴────┐    Plan              State         Task Ledger        │
│    │         │              ┌────────┐             │              │
│    │         │              │ Memory │             │              │
│    │         └──────────────┤        ├─────────────┘              │
│    │                         └────────┘                             │
│    │                                                                   │
│    ↓                              ↓                                    │
│ Resource                      AI Knowledge                            │
│ (DM2 Core)                    (Extension)                              │
│    │                              │                                    │
│    ├── Information                  ├── Vector Store                   │
│    ├── Materiel                     ├── Knowledge Graph                │
│    └── **AI Model** ←───────────────└── RAG Pipeline                  │
│                                    AI Tool                             │
│                                    AI Knowledge                         │
│                                                                         │
│                           Performer                                     │
│                        (DM2 Core + Extension)                          │
│    ┌─────────────────┬─────────────────┬─────────────────┐            │
│    │                 │                 │                 │            │
│ System          Organization       **AI Agent**      Service         │
│                                     ├── Worker Agent                   │
│                                     ├── Service Agent                  │
│                                     └── Support Agent                   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                     AI Interaction Layer                          │  │
│  │                                                                   │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │  │
│  │  │    MCP      │  │    A2A      │  │   Message   │             │  │
│  │  │  Protocol   │  │  Protocol   │  │             │             │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘             │  │
│  │                                                                   │  │
│  │  ┌─────────────────────────────────────────────────────┐        │  │
│  │  │               Orchestrator                           │        │  │
│  │  │  Sequential │ Concurrent │ Group │ Handoff │ Magentic    │   │  │
│  │  └─────────────────────────────────────────────────────┘        │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                     AI Governance Layer                          │  │
│  │                                                                   │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │  │
│  │  │   Safety    │  │   AI        │  │   Audit     │             │  │
│  │  │  Guardrail  │  │   Metric    │  │   Trail     │             │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘             │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 六、应用场景示例

### 6.1 场景：企业 AI 客服系统

#### 6.1.1 架构描述

一个基于多智能体的企业客服系统，包含：
- **分诊智能体**：接收用户请求，判断类型
- **技术智能体**：处理技术问题
- **业务智能体**：处理业务咨询
- **编排器**：协调智能体工作

#### 6.1.2 DM2-AI 建模

```yaml
# AI Entity 建模
IndividualPerformer:
  - id: "triage-agent"
    type: AIAgent
    specialization: "customer-intake"
    llmConfig:
      model: "gpt-4"
      temperature: 0.3
    
  - id: "tech-agent"
    type: AIAgent
    specialization: "technical-support"
    llmConfig:
      model: "gpt-4"
      temperature: 0.7
      
  - id: "business-agent"
    type: AIAgent
    specialization: "business-consultation"
    llmConfig:
      model: "gpt-4"
      temperature: 0.5

# AI Knowledge 建模
AIKnowledge:
  - id: "product-knowledge-base"
    type: VectorStore
    embeddingModel: "text-embedding-3-large"
    storeType: "Pinecone"
    
# Orchestration 建模
Orchestrator:
  - id: "customer-service-orchestrator"
    type: HandoffOrchestrator
    managedAgents:
      - triage-agent
      - tech-agent
      - business-agent
    coordinationStrategy: "dynamic-handoff"

# Protocol 建模
Protocol:
  - id: "agent-communication"
    type: A2AProtocol
    messageFormat: "json"
    
# Governance 建模
SafetyGuardrail:
  - id: "pii-filter"
    type: ContentModeration
    action: "redact"
    
  - id: "response-validator"
    type: OutputFilter
    rules:
      - "no-personal-advice"
      - "escalate-sensitive-topics"
```

#### 6.1.3 视图映射

| 视图 | 描述 |
|------|------|
| **AV-AI-1** | AI 客服架构概览 |
| **OV-AI-2** | 用户请求 → 分诊 → 专家智能体 → 响应 |
| **SV-AI-1** | 智能体接口定义 |
| **SvcV-AI-1** | RAG 知识服务描述 |
| **CV-AI-2** | 能力分类（问答、问题诊断、升级处理） |

---

### 6.2 场景：AI 驱动的网络安全态势感知

#### 6.2.1 架构描述

- **监控智能体**：持续监控网络流量
- **分析智能体**：分析告警，识别威胁模式
- **响应智能体**：生成响应建议或自动处置
- **报告智能体**：生成安全报告

#### 6.2.2 DM2-AI 建模

```yaml
# Orchestration Pattern: Concurrent + Sequential
Orchestrator:
  - id: "security-orchestrator"
    type: ConcurrentOrchestrator
    pattern: "fan-out-fan-in"
    
# AI Knowledge: 安全知识图谱
AIKnowledge:
  - id: "threat-intel-graph"
    type: KnowledgeGraph
    content: "MITRE ATT&CK"
    
# AI Metric: 安全特定度量
AIMetric:
  - name: "threat-detection-rate"
    type: QualityMetric
  - name: "false-positive-rate"
    type: QualityMetric
  - name: "response-time"
    type: PerformanceMetric
```

---

## 八、总结

> **2026-04-17 修订说明**：本报告已更新核心设计原则。AI 扩展不再作为独立数据组（AIExtension），而是**通过 DM2 现有概念的 Subtype 继承机制扩展**，确保与 DoDAF v2.02 标准的 14 个 Data Groups 保持兼容。

### 8.1 核心扩展要点

1. **AI Entity Extension**：通过 Performer/Resource Subtype 扩展 AI 实体
2. **AI Knowledge Extension**：Vector Store、RAG Pipeline 作为 Information Subtype
3. **AI Interaction Extension**：MCP/A2A Protocol 作为 Agreement Subtype
4. **AI Behavior Extension**：Plan、State、Memory 作为 Activity 扩展
5. **AI Orchestration Extension**：Orchestrator 作为 Performer Subtype
6. **AI Governance Extension**：Safety Guardrail 作为 Rule Subtype，AI Metric 作为 Measure Subtype

### 8.2 关键设计原则

1. **向后兼容**：不破坏现有 DM2 结构
2. **类型扩展**：通过 Type 继承（Subtype）实现扩展
3. **关系复用**：尽量复用 DM2 已有关系模式
4. **视图可扩展**：支持新增 AI-specific 视图

### 8.3 与智能驱动转化的关联

DM2-AI 扩展为 DM2 智能驱动转化提供了**语义基础**：

```
DM2-AI Extension (元模型层)
        ↓
AI-aware DM2 Knowledge Graph (知识层)
        ↓
DM2-Constrained LLM Reasoning (推理层)
        ↓
Intelligent Architecture Assistant (应用层)
```

---

## 参考来源

1. **AI Agent Orchestration Patterns**
   - Microsoft Azure Architecture Center
   - https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns

2. **The Orchestration of Multi-Agent Systems**
   - arXiv:2601.13671
   - 2026-01-20

3. **Enterprise AI Knowledge Base with RAG**
   - Xenoss Blog
   - 2025-07-03

4. **DoDAF Architecture Framework Version 2.02**
   - U.S. Department of Defense
   - 2010-08

---

*本文档为 DM2-AI 扩展框架的初步研究，旨在为 AI/LLM/Agent 系统架构提供标准化的描述框架。后续需要针对具体实施课题进行深入设计。*
