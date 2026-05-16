# Pedigree（通用血缘）

> 📄 **完整分析** → [[../详细分析/DM2-Pedigree详细分析]]

Pedigree 是 DM2 的**通用血缘模型**——适用于所有数据组的实体来源追溯。

## 核心问题

> 这个实体从哪来？基于什么？可信度多高？

## 生产流程网络

```
        ┌─── Consumes（消耗）
        │      ↓
Performer ──→ Activity ──→ Produces（产生）
                 │              ↓
            Rules（规则）   Resource
                 │              ↓
            Measures（度量）  Location
```

6 种节点通过有向边连接，形成完整的生产-消费追溯链。

## 每个 Template 都有的 Pedigree 字段

```yaml
pedigree:
  source: ""           # 来源（如：官方文档/专家访谈/估算）
  derivedFrom: []      # 派生自哪些其他实体
  confidence: high | medium | low  # 置信度
  lastUpdated: ""      # 最后更新时间
```

---
*基于 DM2-Pedigree详细分析.md | 2026-04-18*
