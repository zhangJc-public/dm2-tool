---
type: dm2/organization-structure
dm2-layer: Type | Individual
name: null
definition: null
synonyms: []
relationships:
  hasLevel: []
  reportsTo: []
  hasStakeholder: []
  hasResponsibility: []
  coordinatesWith: []
pedigree:
  source: ''
  derivedFrom: []
  confidence: high | medium | low
  lastUpdated: ''
keywords:
- 组织结构
- 层级
- 汇报
- 干系人
- 角色
- hierarchy
- stakeholder
- reporting
- 部门
- 职责
- 权限
- 协作
- RBAC
- 职责分离
- separation of duties
- 汇报线
- 矩阵
- 职能
related_dm2_views:
- OV-4
tags:
- dm2/organization-structure
- dm2/type
- dm2/individual
相关分析: '[[OrgStructure详细分析]]'
---

# {名称}

## 基本信息

| 属性 | 值 |
|------|-----|
| DM2 类型 | OrganizationStructure |
| 分层 | {Type | Individual} |

## 定义

{definition}

## 组织层级

```viz
graph TD
    A[Enterprise] --> B[Division A]
    A --> C[Division B]
    B --> D[Department A1]
    B --> E[Department A2]
    C --> F[Department B1]
```

## 汇报关系

| 上级 | 下级 | 关系类型 |
|------|------|----------|
| {Org-1} | {SubOrg-1} | direct-report |
| {Org-1} | {SubOrg-2} | matrix-report |

## 干系人

| 角色 | 人员 | 职责 | 权限 |
|------|------|------|------|
| {Role-1} | {Person-1} | {描述} | {权限级别} |

## 协作关系

| 组织 A | 组织 B | 协作类型 | 频度 |
|--------|--------|----------|------|
| {Org-A} | {Org-B} | {类型} | {频度} |

## 备注

{additional notes}

---

**相关数据组**：[[OrgStructure]] | [[Performer]] | [[Project]]
