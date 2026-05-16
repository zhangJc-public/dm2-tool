---
type: dm2/capability
dm2-layer: TypeType | Type | Individual
name: null
definition: null
synonyms: []
level: TypeType | Type | Capability | IndividualCapability
relationships:
  composedOf: []
  contributesTo: []
  requiredBy: []
  enablesActivity: []
  performedBy: []
  measuredBy: []
  governedBy: []
  desiredEffect: []
  realizedByProject: []
  mapsActivity: []
  conditions: []
pedigree:
  source: ''
  derivedFrom: []
  confidence: high | medium | low
  lastUpdated: ''
keywords:
- 能力
- 功能
- 本领
- capability
- capacity
- 能力需求
- 能力映射
- 能力差距
- 能力视图
- 能力演进
- 战略
- 规划
- roadmap
- 成熟度
- maturity
- 差距分析
related_dm2_views:
- CV-1
- CV-2
- CV-3
- CV-4
- CV-5
- CV-6
- CV-7
tags:
- dm2/capability
- dm2/typetype
- dm2/type
- dm2/individual
相关分析: '[[../详细分析/DM2-Capability详细分析]]'
---

# {名称}

## 基本信息

| 属性 | 值 |
|------|-----|
| DM2 类型 | Capability |
| 分层级别 | {TypeType | Type | Capability | IndividualCapability} |
| 同义词 | {synonyms} |

## 定义

{definition}

## 四层层级

```viz
graph TB
    A[CapabilityTypeType] --> B[CapabilityType]
    B --> C[Capability]
    C --> D[IndividualCapability]
    
    A1[能力类型类型] --> B1[能力类型]
    B1 --> C1[能力]
    C1 --> D1[具体能力实例]
```

## 能力组成

### composedOf（组成）
- [[Sub-Capability-1]] — 贡献度：高
- [[Sub-Capability-2]] — 贡献度：中

### contributesTo（归属）
- [[Parent-Capability-1]]

## 三角关系

> Performer ──performs──→ Activity ──partOf──→ Capability

| 关系                     | 节点                                      |
| ---------------------- | --------------------------------------- |
| Capability → Performer | [[Performer-1]] performs [[Activity-1]] |
| Capability → Activity  | [[Activity-1]] partOf [[Capability]]    |

## 效果与度量

### desiredEffect（期望效果）
- [[Effect-1]]
- [[Effect-2]]

### measuredBy（度量）
- [[Measure-1]] — 目标：95%
- [[Measure-2]] — 目标：< 100ms

## 治理

- [[Rule-1]] — 能力准入标准
- [[Guidance-1]] — 能力评估规范

## 备注

{additional notes}

---

**相关数据组**：[[Capability]] | [[Performer]] | [[Activity]] | [[Measure]]
