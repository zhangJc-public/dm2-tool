---
type: dm2/information-data
dm2-layer: Type | Individual
name: null
definition: null
synonyms: []
relationships:
  structures: []
  dataElementOf: []
  hasDataType: ''
  hasDataFormat: ''
  storedIn: []
pedigree:
  source: ''
  derivedFrom: []
  confidence: high | medium | low
  lastUpdated: ''
keywords:
- 信息
- 数据
- 模型
- 结构
- 元素
- data
- model
- structure
- element
- 定义
- 字段
- 属性
- 类型
- information
- schema
- 元数据
- metadata
- 字段映射
- ER图
- 范式
- 索引
related_dm2_views:
- DIV-1
- DIV-2
- DIV-3
tags:
- dm2/information-data
- dm2/type
- dm2/individual
相关分析: '[[InformationData详细分析]]'
---

# {名称}

## 基本信息

| 属性 | 值 |
|------|-----|
| DM2 类型 | InformationData |
| 分层 | {Type | Individual} |

## 定义

{definition}

## 数据结构

| 数据元素 | 类型 | 格式 | 约束 |
|----------|------|------|------|
| {Element-1} | String | UTF-8 | NOT NULL |
| {Element-2} | Integer | — | 0-9999 |
| {Element-3} | DateTime | ISO 8601 | — |

## 数据模型层级

```viz
graph TD
    DIV1[DIV-1 概念数据模型] --> DIV2[DIV-2 逻辑数据模型]
    DIV2 --> DIV3[DIV-3 物理数据模型]
```

## 信息关联

| 信息对象 | 关联类型 | 关联对象 |
|----------|----------|----------|
| {Info-1} | structures | {Element-1} |
| {Element-1} | references | {Element-2} |

## 存储

| 系统 | 表/集合 | 持久化方式 |
|------|---------|-----------|
| {System-1} | {Table-1} | RDBMS |
| {System-2} | {Collection-1} | NoSQL |

## 备注

{additional notes}

---

**相关数据组**：[[InformationData]] | [[Resource]] | [[InformationPedigree]]
