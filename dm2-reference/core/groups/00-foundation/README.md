# DM2 基础模式 · 导航

> DM2 元模型的"语法层"——在深入任何数据组之前，先理解这些底层模式。

## 五大基础模式

| # | 模式 | 核心问题 | 一句话 | 详情 |
|---|------|---------|--------|------|
| 1 | **IDEAS TopLevel** | 世界由什么构成？ | Thing → Individual / Type / Tuple 四分法 | [[IDEAS-TopLevel]] |
| 2 | **Foundation for Associations** | 事物如何关联？ | 5 种核心关联：WholePart / BeforeAfter / Overlap / Couple / TemporalWP | [[FoundationForAssociations]] |
| 3 | **Common Patterns** | Type 和 Instance 怎么对应？ | Instance 层（绿色）↔ Type 层（紫色）完整映射 | [[CommonPatterns]] |
| 4 | **Naming & Description** | 实体如何被识别和描述？ | Name(名) / Description(述) / Representation(示) / Scheme(案) 四区域 | [[NamingAndDescriptionPattern]] |
| 5 | **Temporal Part & Boundaries** | 时间如何建模？ | 时间可重叠！边界是一等实体，双层设计（具体+统计约束） | [[TemporalPartAndBoundaries]] |

## 学习路径

```
新手入门:   IDEAS TopLevel → Common Patterns → Naming & Description
深度理解:   Foundation for Associations → Temporal Part & Boundaries
日常参考:   直接查对应模式的文档即可
```

## 与详细分析文档的关系

每个模式文档都是 `../详细分析/` 中对应深度分析的**精华提炼版**。需要完整类图、形式化定义、IDEAS 公理推导时，请跳转到详细分析。

---
*最后更新: 2026-04-18 | 状态: 重构完成*
