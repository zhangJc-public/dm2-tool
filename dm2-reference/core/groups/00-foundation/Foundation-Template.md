---
type: dm2/foundation
dm2-layer: Meta
name:
definition:
synonyms: []
relationships:
  beforeAfter: []
  couple: []
  describedBy: []
  descriptionSchemeInstance: []
  measureOfIndividualEndBoundary: []
  measureOfIndividualStartBoundary: []
  measureOfTypeEndBoundaryType: []
  measureOfTypeStartBoundaryType: []
  namedBy: []
  namingSchemeInstance: []
  overlap: []
  powertypeInstance: []
  representationSchemeInstance: []
  representedBy: []
  superSubtype: []
  temporalWholePart: []
  typeInstance: []
  wholePart: []
pedigree:
  source: "IDEAS Group Foundational Ontology"
  derivedFrom: []
  confidence: high
  lastUpdated: ""
keywords:
  - 基础
  - 本体
  - 抽象
  - 关联
  - 时态
  - 边界
  - foundation
  - ontology
  - abstraction
  - relationship
  - temporal
  - pattern
  - 模型
  - 语义
  - 概念
related_dm2_views: []
tags:
  - dm2/foundation
  - dm2/meta
相关分析: "[[DM2-Foundation详细分析]]"
---

## DM2 关联清单（元模型权威）
> 本组权威关联（来自 dm2-metamodel-2.02.yaml 关联目录）：
> - beforeAfter: Individual ─▶ Individual
> - couple: tuple ─▶ Thing
> - describedBy: Thing ─▶ Information
> - descriptionSchemeInstance: DescriptionScheme ─▶ Information
> - measureOfIndividualEndBoundary: Measure ─▶ Individual
> - measureOfIndividualStartBoundary: Measure ─▶ Individual
> - measureOfTypeEndBoundaryType: Measure ─▶ EndBoundaryType
> - measureOfTypeStartBoundaryType: Measure ─▶ StartBoundaryType
> - namedBy: Thing ─▶ Name
> - namingSchemeInstance: NamingScheme ─▶ Name
> - overlap: Individual ─▶ Individual
> - powertypeInstance: Individual ─▶ Type
> - representationSchemeInstance: RepresentationScheme ─▶ Representation
> - representedBy: Thing ─▶ Representation
> - superSubtype: Type ─▶ Type
> - temporalWholePart: Individual ─▶ Individual
> - typeInstance: Individual ─▶ Type
> - wholePart: Individual ─▶ Individual

# Foundation

## 基本定义

DM2 Foundation 是 IDEAS Group 顶层本体的 DM2 实现，定义了所有 DM2 概念的最基本框架：

- **Thing** — 所有 DM2 概念的超类
- **Individual** — 时空中的具体个体
- **Type** — 个体的分类/抽象

## 核心模式

| 模式 | 描述 |
|------|------|
| 4-Dimensionalism | 所有个体在时空扩展（spatio-temporal extent） |
| Supertype-Subtype | 通过 isA 关系的分类层次 |
| Whole-Part | 通过 partOf/hasPart 的组合关系 |
| Temporal Boundary | before/after 时态边界 |

## 对 DoDAF 视图的支撑

Foundation 层为所有 DoDAF 视图提供概念基础，不直接对应特定视图，但确保了：
- AV-2 集成字典中术语间语义一致性
- 跨视图的概念可追溯性
- 类型-实例关系的严格定义

## 备注

此数据组属于 Meta 层级，激活时表示用户关注架构的形式化语义基础或概念建模方法论。

---

**相关数据组**：[[Performer]] | [[Activity]] | [[Capability]] | [[Resource]]
