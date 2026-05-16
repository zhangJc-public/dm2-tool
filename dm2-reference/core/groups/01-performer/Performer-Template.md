---
type: dm2/performer
dm2-layer: Type | Individual
dm2-subtype: System | Service | Organization | PersonRole
name: null
definition: null
synonyms: []
relationships:
  performs: []
  partOf: []
  hasPart: []
  providesService: []
  consumesResource: []
  locatedAt: []
  measuredBy: []
  containsMateriel: []
  hasPort: []
  hasRole: []
  measuredByOrg: []
  hasCapability: []
pedigree:
  source: ''
  derivedFrom: []
  confidence: high | medium | low
  lastUpdated: ''
keywords:
- 角色
- 组织
- 团队
- 人员
- 执行者
- performer
- operator
- system
- service
- person
- 系统
- 服务
- 操作员
- 部门
- 管理员
- 运维
- DevOps
- admin
- 用户
- 角色分配
related_dm2_views:
- OV-4
- PV-1
tags:
- dm2/performer
- dm2/type
- dm2/individual
相关分析: '[[../详细分析/DM2-Performer详细分析]]'
---

# {名称}

## 基本信息

| 属性 | 值 |
|------|-----|
| DM2 类型 | Performer |
| 分层 | {Type | Individual} |
| 子类型 | {System | Service | Organization | PersonRole} |
| 同义词 | {synonyms} |

## 定义

{definition}

## 层级关系

```viz
graph LR
    A[{dm2-subtype}Type] --> B[{dm2-subtype}]
    B --> C[Individual{dm2-subtype}]
```

## 关联关系

### performs（执行）
- [[Activity-1]]
- [[Activity-2]]

### partOf（所属）
- [[Parent-Performer-1]]

### hasPart（包含）
- [[Child-Performer-1]]
- [[Child-Performer-2]]

### providesService（提供服务）
- [[Service-1]]

### locatedAt（位置）
- [[Location-1]]

## 能力映射

| 能力 | 贡献度 |
|------|--------|
| [[Capability-1]] | 高 |
| [[Capability-2]] | 中 |

## 度量指标

| 指标 | 值 | 单位 |
|------|-----|------|
| 可用性 | 99.9 | % |
| 响应时间 | < 200 | ms |

## 备注

{additional notes}

---

**相关数据组**：[[Performer]] | [[Capability]] | [[Activity]] | [[Resource]]
