---
type: dm2/rule
dm2-layer: Type | Individual
dm2-subtype: Condition | Constraint | Requirement | Guideline
name: ''
definition: ''
synonyms: []
sourceDocument: ''
ruleCategory: ''
triggerCondition: ''
actionOrConstraint: ''
severity: mandatory | recommended | optional
relationships:
  appliesTo: []
  derivedFromGuidance: []
  relatedRule: []
  measuredBy: []
pedigree:
  source: ''
  derivedFrom: []
  confidence: high | medium | low
  lastUpdated: ''
keywords:
- 规则
- 约束
- 条件
- 需求
- 策略
- rule
- constraint
- condition
- requirement
- 加密
- 密码
- 合规
- 安全策略
- 访问控制
- RBAC
- ABAC
- ACL
- 防火墙
- firewall
- 认证
- 授权
related_dm2_views:
- SV-10a
- SvcV-10a
tags:
- dm2/rule
- dm2/type
- dm2/individual
相关分析: '[[../详细分析/DM2-Rules详细分析]]'
---

# {规则名称/编号}

## 基本信息

| 字段 | 内容 |
|------|------|
| 名称 | |
| 来源文档 | [[来源Guidance]] |
| 规则类型 | Condition / Constraint / Requirement / Guideline |
| 严重程度 | mandatory / recommended / optional |

## 规则定义

### 触发条件
{何时适用此规则}

### 动作/约束
{具体要求}

## 适用范围

| 对象类型 | 具体实体 | 说明 |
|---------|---------|------|
| | | |

## 合规检查

| 度量项 | 目标值 | 当前值 | 状态 |
|--------|--------|--------|------|
| | | | |

## 📖 深入阅读

> 📄 完整类图分析与形式化定义 → [[../详细分析/DM2-Rules详细分析]]

### 核心要点
1. **⚠️ vs Guidance 的区别**：Guidance = 法规原文；Rules = 提取的可执行逻辑条目
2. 四种子类型：Condition(条件) / Constraint(约束) / Requirement(需求) / Guideline(指南)
3. DesiredEffect（期望效果）是 Rules 连接到 Activity 的桥梁
