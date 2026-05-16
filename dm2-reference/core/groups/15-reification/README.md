# Reification Levels（具象化层级）

> 📄 **完整分析** → [[../详细分析/DM2-Reification详细分析]]

Reification 解决的是 **"这个实体应该在哪一层？"** 的根本问题。

## 四层体系

| 层级 | 名称 | 谁关心 | 类比 |
|------|------|--------|------|
| **L0: TypeType** | 元类型 | 架构总师 | "能力"这个概念本身 |
| **L1: Type** | 类型 | 架构师 | "网络防御能力" |
| **L2: Individual** | 实例 | 设计师 | "某 SOC 的入侵检测能力" |
| **L3: IndividualIndividual** | 出现 | 运维 | "2026Q1 的入侵检测运行实例" |

## 快速决策树

```
新实体是？
├─ 一个概念/类别？         → Type (L1)
│  └─ 概念的概念？         → TypeType (L0)
├─ 一个具体的东西？        → Individual (L2)
│  └─ 需要记录特定时刻状态？→ IndividualIndividual (L3)
└─ 不确定？                → 查阅本文档或咨询 00-基础模式/IDEAS-TopLevel
```

## IDEAS 公理支撑

- **Individual IS-A Type**: L2 实体同时也是某个 L1 类型的实例
- **typeinstance**: Type 本身可以被实例化（L0 → L1）

---
*基于 DM2-Reification详细分析.md | 2026-04-18*
