---
type: dm2/resource-flow
dm2-layer: Type | Individual
name: null
definition: null
synonyms: []
relationships:
  source: []
  target: []
  carriesResource: []
  viaInterface: []
  hasProtocol: []
pedigree:
  source: ''
  derivedFrom: []
  confidence: high | medium | low
  lastUpdated: ''
keywords:
- 资源流
- 数据流
- 接口
- 连接
- 拓扑
- flow
- interface
- connection
- topology
- 交换
- 传输
- 通信
- 认证流
- 数据交换
- 消息队列
- ETL
- API网关
- 事件流
- 同步
- 认证
- 授权
related_dm2_views:
- SV-4
- DIV-2
- DIV-3
tags:
- dm2/resource-flow
- dm2/type
- dm2/individual
相关分析: '[[ResourceFlow详细分析]]'
---

# {名称}

## 基本信息

| 属性 | 值 |
|------|-----|
| DM2 类型 | ResourceFlow |
| 分层 | {Type | Individual} |

## 定义

{definition}

## 源和目标

| 源 (Source) | 目标 (Target) |
|------------|--------------|
| {Performer/Activity} | {Performer/Activity} |

## 携带资源

| 资源 | 类型 | 方向 |
|------|------|------|
| {Resource-1} | {Material/Information/Data} | {In/Out} |

## 接口

| 接口 | 协议 | 速率 |
|------|------|------|
| {Interface-1} | {Protocol} | {速率} |

## 拓扑关系

```viz
graph LR
    A[Source] -->|ResourceFlow| B[Target]
    B -->|ResourceFlow| C[Next Target]
```

## 备注

{additional notes}

---

**相关数据组**：[[ResourceFlow]] | [[Activity]] | [[Resource]] | [[Information]]
