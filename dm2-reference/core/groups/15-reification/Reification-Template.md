---
type: dm2/reification
dm2-layer: Meta
name: null
definition: null
synonyms: []
relationships:
  activityConsumesResource: []
  activityPartOfProjectType: []
  activityPerformedByPerformer: []
  activityProducesResource: []
  describedBy: []
  measureOfTypeActivity: []
  measureOfTypeResource: []
  partiesToAnAgreement: []
  resourceInLocationType: []
  ruleConstrainsActivity: []
pedigree:
  source: ''
  derivedFrom: []
  confidence: high | medium | low
  lastUpdated: ''
keywords:
- 具体化
- 抽象层次
- 类型
- 实例
- 桥接
- reification
- abstraction
- instance
- type
- instanceOf
- 层次
- 泛化
- 特化
- 抽象层
- specialization
- 继承
- 多态
- 分类
related_dm2_views: []
tags:
- dm2/reification
- dm2/meta
相关分析: '[[Reification详细分析]]'
---

## DM2 关联清单（元模型权威）
> 本组权威关联（来自 dm2-metamodel-2.02.yaml 关联目录）：
> - activityConsumesResource: Activity ─▶ Resource
> - activityPartOfProjectType: Activity ─▶ ProjectType
> - activityPerformedByPerformer: Performer ─▶ Activity
> - activityProducesResource: Activity ─▶ Resource
> - describedBy: Thing ─▶ Information
> - measureOfTypeActivity: Measure ─▶ Activity
> - measureOfTypeResource: Measure ─▶ Resource
> - partiesToAnAgreement: Performer ─▶ Agreement
> - resourceInLocationType: Resource ─▶ LocationType
> - ruleConstrainsActivity: Activity ─▶ Rule

# Reification

## 基本定义

Reification（具体化）处理 DM2 中 Type↔Individual 之间的抽象层次桥接关系：

- **Type** — 概念的分类（如 "F-16 战斗机")
- **Individual** — 概念的具体实例（如 "序列号 AF-93-0123 的 F-16")
- **Reification** — 将抽象类型"具体化"为可操作个体

## 抽象层次

```
Individual ──instanceOf──> Type ──subtypeOf──> SuperType
                                                      ↑
                                              Foundation::Thing
```

| 层次 | DM2 位置 | 示例 |
|------|----------|------|
| Foundation | Thing | 存在的事物 |
| SuperType | Performer | 执行者（最抽象） |
| Type | Organization | 组织机构类型 |
| SubType | Agency | 具体机构类型 |
| Individual | NSA | 具体个体 |

## 对 DoDAF 视图的支撑

Reification 确保：
- CV-1/CV-2 中的能力分类层次一致
- OV-4 组织类型与具体组织实例关系清晰
- AV-2 集成字典中类型-实例对应关系正确

## 备注

此数据组属于 Meta 层级，激活时表示用户关注架构概念的分层建模或 Type-Instance 映射关系。

---

**相关数据组**：[[Reification]] | [[Foundation]] | [[Pedigree]]
