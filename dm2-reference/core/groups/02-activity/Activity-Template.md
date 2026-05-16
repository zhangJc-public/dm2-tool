---
type: dm2/activity
dm2-layer: Type | Individual
name: null
definition: null
synonyms: []
objective: ''
precondition: ''
postcondition: ''
relationships:
  performedBy: []
  consumes: []
  produces: []
  partOf: []
  hasPart: []
  prerequisite: []
  successor: []
  governedBy: []
  directedBy: []
  underCondition: []
  mapsToCapability: []
  measuredBy: []
pedigree:
  source: ''
  derivedFrom: []
  confidence: high | medium | low
  lastUpdated: ''
keywords:
- 活动
- 流程
- 过程
- 操作
- 步骤
- activity
- process
- operation
- function
- 功能
- 任务
- 业务
- 认证流程
- 认证
- 审批
- 审计跟踪
- audit
- workflow
- 自动化
- 编排
related_dm2_views:
- OV-5a
- OV-5b
tags:
- dm2/activity
- dm2/type
- dm2/individual
相关分析: '[[../详细分析/DM2-Performer详细分析]]（Activity 元模型嵌入其中）'
---

# {名称}

## 基本信息

| 属性 | 值 |
|------|-----|
| DM2 类型 | Activity |
| 分层 | {Type | Individual} |
| 目标 | {objective} |

## 定义

{definition}

## 条件

| 条件类型 | 描述 |
|----------|------|
| 前置 | {precondition} |
| 后置 | {postcondition} |

## 资源流

```viz
graph LR
    subgraph Input
        I1[Resource 1]
        I2[Resource 2]
    end
    A[Activity] --> O[Output Resource]
    I1 --> A
    I2 --> A
```

### 输入（Consumes）
- [[Resource-1]] — {描述}
- [[Information-1]] — {描述}

### 输出（Produces）
- [[Resource-2]] — {描述}
- [[Information-2]] — {描述}

## 执行者

| 执行者 | 角色 | 贡献度 |
|--------|------|--------|
| [[Performer-1]] | 主要 | 高 |
| [[Performer-2]] | 辅助 | 中 |

## 层级关系

- **partOf**：[[Capability-1]]、[[Activity-Parent-1]]
- **hasPart**：[[Sub-Activity-1]]、[[Sub-Activity-2]]

## 时序关系

- **prerequisite**：[[Pre-Activity-1]]
- **successor**：[[Post-Activity-1]]

## 治理规则

- [[Rule-1]]
- [[Guidance-1]]

## 绩效度量

| 指标 | 目标值 | 当前值 |
|------|--------|--------|
| 执行时间 | ≤ 10 min | — |
| 成功率 | ≥ 99% | — |
| 成本 | ≤ ¥5000 | — |

## 备注

{additional notes}

---

**相关数据组**：[[Activity]] | [[Performer]] | [[Capability]] | [[Resource]]
