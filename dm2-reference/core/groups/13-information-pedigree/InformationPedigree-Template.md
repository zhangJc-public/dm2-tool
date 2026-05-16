---
type: dm2/information-pedigree
dm2-layer: Type | Individual
name: null
definition: null
synonyms: []
relationships:
  derivedFromInfo: []
  aggregatedFrom: []
  transformedBy: []
  hasLineageDepth: 0
  qualityScore: 0.0
pedigree:
  source: ''
  derivedFrom: []
  confidence: high | medium | low
  lastUpdated: ''
keywords:
- 信息谱系
- 衍生
- 聚合
- 变换
- 血缘
- lineage
- aggregation
- transformation
- 数据源
- 派生
- 融合
- 加工
- 数据治理
- governance
- aggregate
- 转换
- ETL
related_dm2_views:
- DIV-1
- DIV-2
tags:
- dm2/information-pedigree
- dm2/type
- dm2/individual
相关分析: '[[InformationPedigree详细分析]]'
---

# {名称}

## 基本信息

| 属性 | 值 |
|------|-----|
| DM2 类型 | InformationPedigree |
| 分层 | {Type | Individual} |

## 定义

{definition}

## 信息血缘图

```viz
graph TD
    A[Raw Data Source] -->|extract| B[Data Element 1]
    B -->|aggregate| C[Derived Metric]
    C -->|transform| D[Output Report]
    D -->|validate| E[Final Result]
```

## 血缘关系

| 源信息 | 操作 | 目标信息 | 变换描述 |
|--------|------|----------|----------|
| {Info-1} | extract | {Element-1} | {描述} |
| {Element-1} | aggregate | {Metric-1} | {描述} |

## 数据质量

| 指标 | 值 | 评估 |
|------|-----|------|
| 完整性 | {0-100}% | {高/中/低} |
| 准确性 | {0-100}% | {高/中/低} |
| 时效性 | {时间} | {描述} |

## 备注

{additional notes}

---

**相关数据组**：[[InformationPedigree]] | [[Pedigree]] | [[InformationData]]
