---
type: dm2/resource
dm2-layer: Type | Individual
dm2-subtype: Resource | Information | DataType
name: null
definition: null
synonyms: []
format: ''
sensitivity: public | internal | confidential | restricted
relationships:
  representedBy: []
  consumedBy: []
  producedBy: []
  storedAt: []
  flowsThrough: []
  governedBy: []
  accessedVia: []
  locatedIn: []
pedigree:
  source: ''
  derivedFrom: []
  confidence: high | medium | low
  lastUpdated: ''
keywords:
- 资源
- 数据
- 信息
- 资产
- resource
- data
- information
- asset
- 数据流
- 数据交换
- 资源流
- 数据分类
- 令牌
- 凭证
- 密钥
- 证书
- token
- credential
- secret
- 加密
related_dm2_views:
- OV-2
- OV-3
- SV-2
- SV-6
- DIV-1
- DIV-2
- DIV-3
tags:
- dm2/resource
- dm2/type
- dm2/individual
- dm2/information
相关分析: '[[../详细分析/DM2-InformationAndData详细分析]]'
---

# {名称}

## 基本信息

| 属性 | 值 |
|------|-----|
| DM2 类型 | Resource / Information / DataType |
| 分层 | {Type | Individual} |
| 格式 | {format} |
| 敏感度 | {sensitivity} |
| 同义词 | {synonyms} |

## 定义

{definition}

## 数据分类

> 参考：数据安全法、个人信息保护法

| 维度 | 分类 |
|------|------|
| 重要程度 | 核心 / 重要 / 一般 |
| 个人信息 | 是 / 否 |
| 敏感个人信息 | 是 / 否 |

## 信息结构

```viz
graph LR
    A[Resource/Information] -->|representedBy| B[Data Type]
    B -->|has| C[Data Element 1]
    B -->|has| D[Data Element 2]
```

## 资源流

```viz
graph LR
    P1[Producer: Performer/Activity] -->|produces| R[Resource]
    R -->|consumedBy| C1[Consumer: Performer/Activity]
    R -->|storedAt| L[Location]
```

### 生产者（producedBy）
- [[Activity-1]] — 频率：实时
- [[Performer-1]]

### 消费者（consumedBy）
- [[Activity-2]]
- [[Performer-2]]

### 存储位置（storedAt）
- [[Location-1]]

## 数据血缘（Pedigree）

| 节点 | 类型 | 说明 |
|------|------|------|
| [[Source-1]] | Source | 原始数据 |
| [[Process-1]] | Derivation | 数据处理 |
| [[Aggregate-1]] | Aggregation | 数据聚合 |

## 治理要求

- [[Rule-1]] — 访问控制
- [[Guidance-1]] — 数据分类分级
- [[Regulation-1]] — 个人信息保护

## 安全措施

| 威胁 | 措施 | 级别 |
|------|------|------|
| 未授权访问 | 加密存储 + 访问控制 | 核心 |
| 数据泄露 | DLP + 审计 | 重要 |

## 备注

{additional notes}

---

**相关数据组**：[[Resource]] | [[Activity]] | [[Performer]] | [[Guidance]]
