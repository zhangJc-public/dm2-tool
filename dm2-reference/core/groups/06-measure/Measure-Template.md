---
type: dm2/measure
dm2-layer: Type | Individual
dm2-subtype: '# 质量度量 (Quality Measures)

  AdaptabilityMeasure |     # 适应性：满足不同约束的难易程度

  MaintainabilityMeasure | # 可维护性：执行者在一段时间内执行活动的能力

  NeedsSatisfactionMeasure | # 需求满意度：满足用户需求的程度

  PerformanceMeasure |     # 性能：满足能力需求的程度

  OrganizationalMeasure |   # 组织运营成本度量

  # 物理度量 (Physical Measures)

  PhysicalMeasure |         # 时空范围度量（长度、质量、能量等）

  SpatialMeasure |          # 时空位置度量

  TemporalMeasure |         # 时间度量

  # 技能度量 (Skill Measures)

  MeasureableSkill |        # 可数字度量的技能

  # 效果度量 (Effect Measures)

  MeasureOfDesire |         # 期望度量

  MeasureOfEffect |         # 效果度量

  '
name: null
definition: null
synonyms: []
unit: ''
direction: higher-is-better | lower-is-better | target-is-best
targetValue: ''
threshold: ''
relationships:
  measures: []
  partOf: []
  contributesTo: []
  governedBy: []
pedigree:
  source: ''
  derivedFrom: []
  confidence: high | medium | low
  lastUpdated: ''
keywords:
- 度量
- 指标
- 测量
- measure
- metric
- KPI
- 性能
- 质量
- 效率
- 绩效
- SLA
- 延迟
- 吞吐量
- latency
- throughput
- 可用性
- 监控
related_dm2_views:
- SV-7
- SvcV-7
tags:
- dm2/measure
- dm2/metric
- dm2/performance
相关分析: '[[../详细分析/DM2-Measure详细分析]]'
---

# {名称}

## 基本信息

| 属性 | 值 |
|------|-----|
| DM2 类型 | Measure |
| 子类型 | {Measure | Metric | PerformanceIndicator} |
| 单位 | {unit} |
| 方向 | {direction} |
| 目标值 | {targetValue} |
| 阈值 | {threshold} |
| 同义词 | {synonyms} |

## 定义

{definition}

## 度量结构

```viz
graph LR
    M[Measure] -->|measures| T1[Target 1]
    M -->|measures| T2[Target 2]
    
    M -->|contributesTo| A[Aggregate Metric]
```

## 被度量对象

| 对象 | 类型 | 当前值 |
|------|------|--------|
| [[Performer-1]] | 可用性 | — |
| [[Activity-1]] | 执行时间 | — |
| [[Capability-1]] | 能力水平 | — |

## 采集方法

- **数据源**：{数据来源}
- **采集频率**：{实时/定期}
- **采集方式**：{自动/手动}

## 当前状态

```viz
gauge
  title "{名称}"
  0 "{threshold}" 100 "{targetValue}"
  75 当前值
```

| 状态 | 描述 |
|------|------|
| 🟢 达标 | ≥ {targetValue} |
| 🟡 预警 | ≥ {threshold} 且 < {targetValue} |
| 🔴 不达标 | < {threshold} |

## 层级关系

- **partOf**：[[Metric-System-1]]
- **contributesTo**：[[KPI-1]]

## 备注

{additional notes}

---

**相关数据组**：[[Measure]] | [[Performer]] | [[Capability]] | [[Activity]]
