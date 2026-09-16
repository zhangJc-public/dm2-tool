---
type: dm2/project
dm2-layer: Type | Individual
name: ''
definition: ''
synonyms: []
relationships:
  activityConsumesResource: []
  activityPartOfProjectType: []
  activityPerformableUnderCondition: []
  activityPerformedByPerformer: []
  activityProducesResource: []
  desireMeasure: []
  desiredEffect: []
  desiredEffectDirectsActivity: []
  desiredEffectIsRealizedByProjectType: []
  effectMeasure: []
  measureOfTypeActivity: []
  measureOfTypeCondition: []
  measureOfTypeProjectType: []
  measureOfTypeResource: []
  ruleConstrainsActivity: []
  visionIsRealizedByDesiredEffect: []
pedigree:
  source: ''
  derivedFrom: []
  confidence: high | medium | low
  lastUpdated: ''
keywords:
- 项目
- 里程碑
- 阶段
- 计划
- project
- milestone
- phase
- 时间线
- 预算
- 进度
- 项目周期
- sprint
- release
- deploy
- 交付
- 迭代
- 路线图
- 发布
related_dm2_views:
- PV-1
- PV-2
- PV-3
tags:
- dm2/project
- dm2/type
- dm2/individual
相关分析: '[[../详细分析/DM2-Project详细分析]]'
---

## DM2 关联清单（元模型权威）
> 本组权威关联（来自 dm2-metamodel-2.02.yaml 关联目录）：
> - activityConsumesResource: Activity ─▶ Resource
> - activityPartOfProjectType: Activity ─▶ ProjectType
> - activityPerformableUnderCondition: Activity ─▶ Condition
> - activityPerformedByPerformer: Performer ─▶ Activity
> - activityProducesResource: Activity ─▶ Resource
> - desireMeasure: Measure ─▶ MeasureOfDesire
> - desiredEffect: Resource ─▶ Performer
> - desiredEffectDirectsActivity: Resource ─▶ Activity
> - desiredEffectIsRealizedByProjectType: ProjectType ─▶ Resource
> - effectMeasure: MeasureOfEffect ─▶ Resource
> - measureOfTypeActivity: Measure ─▶ Activity
> - measureOfTypeCondition: Measure ─▶ Condition
> - measureOfTypeProjectType: Measure ─▶ ProjectType
> - measureOfTypeResource: Measure ─▶ Resource
> - ruleConstrainsActivity: Activity ─▶ Rule
> - visionIsRealizedByDesiredEffect: Vision ─▶ Resource

# {项目名称}

## 基本信息

| 字段 | 内容 |
|------|------|
| 名称 | |
| 编号 | |
| 状态 | 规划中 / 进行中 / 已完成 / 已暂停 |
| 起止时间 | ~ |
| 预算 | |

## 能力实现映射

> 本项目实现以下能力：

| 能力 | 贡献度 | 验证方式 |
|------|--------|---------|
| | | |

## 项目阶段

| 阶段 | 名称 | 时间 | 交付物 |
|------|------|------|--------|
| 1 | | | |
| 2 | | | |
| 3 | | | |

## 关联实体

| 关系 | 实体 | 说明 |
|------|------|------|
| 实现能力 | | |
| 执行方 | | |
| 度量指标 | | |

## 📖 深入阅读

> 📄 完整类图分析与形式化定义 → [[../详细分析/DM2-Project详细分析]]

### 核心要点
1. Project 是 Capability 从愿景到现实的**实现载体**
2. 项目阶段用 temporalWholePart 或 BeforeAfter 建模
3. 中国适配：Project 可关联等保建设、密评改造等合规项目
