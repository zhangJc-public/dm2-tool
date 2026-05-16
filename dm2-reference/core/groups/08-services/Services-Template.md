---
type: dm2/service
dm2-layer: Type | Individual
name: ''
definition: ''
synonyms: []
relationships:
  providedBy: []
  accessedBy: []
  operatesOn: []
  hasPort: []
  governedBy: []
pedigree:
  source: ''
  derivedFrom: []
  confidence: high | medium | low
  lastUpdated: ''
keywords:
- 服务
- 接口
- API
- 微服务
- service
- port
- interface
- 服务端口
- 服务接口
- 服务编排
- SSO
- MFA
- OAuth
- LDAP
- 认证
- 授权
- auth
- 登录
- API网关
related_dm2_views:
- SvcV-1
- SvcV-2
- SvcV-3
- SvcV-4
- SvcV-5
- SvcV-6
- SvcV-7
- SvcV-8
- SvcV-9
- SvcV-10a
- SvcV-10b
- SvcV-10c
tags:
- dm2/service
- dm2/type
- dm2/individual
相关分析: '[[../详细分析/DM2-Services详细分析]]'
---

# {服务名称}

## 基本信息

| 字段 | 内容 |
|------|------|
| 名称 | |
| 英文名 | |
| 类型 | [[Service-Type]] |
| 层级 | Type / Individual |

## 服务描述

{服务功能描述}

## 服务端口（ServicePort）

| 端口名 | 方向 | 描述 |
|--------|------|------|
| | 输入 | |
| | 输出 | |
| | 异常 | |

## 关联实体

| 关系 | 实体 | 说明 |
|------|------|------|
| 提供者 | | |
| 访问者 | | |
| 操作资源 | | |

## 📖 深入阅读

> 📄 完整类图分析与形式化定义 → [[../详细分析/DM2-Services详细分析]]

### 核心要点
1. Service 是 Performer 向外部暴露的**接口**，不是执行者本身
2. 一个 Performer 可以提供多个 Service
3. ServicePort 是服务的组成单元，每个 Port 有方向性（输入/输出/异常）
