---
type: dm2/pedigree
dm2-layer: Meta
name: null
definition: null
synonyms: []
relationships:
  derivedFrom: []
  hasDerivative: []
  hasConfidence: ''
  verifiedBy: []
  lastModified: ''
pedigree:
  source: ''
  derivedFrom: []
  confidence: high | medium | low
  lastUpdated: ''
keywords:
- 谱系
- 溯源
- 推导
- 置信度
- pedigree
- provenance
- derivation
- confidence
- 来源
- 引用
- 追溯
- 血缘
- 可信度
- 数据血缘
- 可信
- trust
- auditability
- 推导链
- 质量
related_dm2_views: []
tags:
- dm2/pedigree
- dm2/meta
相关分析: '[[Pedigree详细分析]]'
---

# Pedigree

## 基本定义

Pedigree（谱系）提供所有 DM2 概念的元数据溯源机制，包括：

- **推导链** (derivedFrom) — 知识从何处派生
- **置信度** (confidence) — 知识的可信程度
- **时间戳** (lastUpdated) — 知识的时间维度

## 谱系属性

| 属性 | 描述 | 示例 |
|------|------|------|
| source | 知识来源 | DOC-001, Expert-A |
| derivedFrom | 推导来源概念 | [Concept-A] |
| confidence | 置信度 | high / medium / low |
| lastUpdated | 最后更新时间 | 2024-01-15 |

## 推导链示例

```viz
graph LR
    A[Source Document] -->|extracts| B[Fact 1]
    B -->|derives| C[Inference]
    C -->|validates| D[Conclusion]
```

## 对 DoDAF 视图的支撑

Pedigree 为所有视图提供知识可信度追踪，确保：
- AV-2 集成字典中每个术语的来源可追溯
- 跨视图引用具有置信度标注
- 架构决策的推导链清晰

## 备注

此数据组属于 Meta 层级，激活时表示用户关注知识的可信度、溯源或推导链。

---

**相关数据组**：[[Pedigree]] | [[InformationPedigree]] | [[Foundation]]
