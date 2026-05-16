# ResourceFlow（资源流动）

> 📄 **完整分析** → [[../详细分析/DM2-ResourceFlow详细分析]]

ResourceFlow 描述资源在 Performer 之间的**流动关系**。它不是独立实体类型，而是一种关系建模视角，主要服务于：
- **SV-4 系统功能描述**：数据和资源如何在系统间流转
- **DIV-2/3 数据视图**：信息交换需求

## 核心模型

```
生产者(Performer) --produces--> 资源(Resource) --flowsThrough--> 经过的系统(Performer) --consumesBy--> 消费者(Performer)
                              ↑
                         governedBy 规则
                         locatedIn 位置
```

## 关键概念

| 概念 | 说明 |
|------|------|
| **ResourceFlow** | 资源从一方向另一方的有向移动 |
| **resourceFlowType** | 流动的类型分类 |
| **与 Pedigree 的关系** | ResourceFlow + Pedigree = 完整的资源生命周期追踪 |

## 建模建议

1. 先在 `04-Resource` 中定义资源实体
2. 再在此处描述资源如何在不同 Performer 间流转
3. 用 `12-Pedigree` 追溯资源的生产和消费历史

---
*基于 DM2-ResourceFlow详细分析.md | 2026-04-18*
