---
type: dm2/guidance
dm2-layer: Type | Individual
dm2-subtype: Rule | Standard | Regulation
name: null
definition: null
synonyms: []
source: ''
effectiveDate: ''
appliesTo: []
relationships:
  constrains: []
  derivedFrom: []
  relatedTo: []
  measuredBy: []
pedigree:
  source: ''
  derivedFrom: []
  confidence: high | medium | low
  lastUpdated: ''
keywords:
- 指导
- 法规
- 标准
- 规范
- guidance
- regulation
- standard
- policy
- 合规
- 等保
- 制度
- NIST
- GDPR
- ISO27001
- SOC2
- compliance
- 审计
- 认证
- 授权
related_dm2_views:
- StdV-1
- OV-6a
tags:
- dm2/guidance
- dm2/rule
- dm2/standard
- dm2/regulation
相关分析: '[[../详细分析/DM2-Rules详细分析]]'
---

# {名称}

## 基本信息

| 属性 | 值 |
|------|-----|
| DM2 类型 | Guidance |
| 子类型 | {Rule | Standard | Regulation} |
| 来源 | {source} |
| 生效日期 | {effectiveDate} |
| 同义词 | {synonyms} |

## 定义

{definition}

## 适用范围

- [[Performer-1]]
- [[Activity-1]]
- [[Resource-1]]

## 核心要求

### 主要条款

1. **{条款1}**
   - 要求：{具体要求}
   - 验证方式：{验证方法}

2. **{条款2}**
   - 要求：{具体要求}
   - 验证方式：{验证方法}

### 合规检查点

| 检查点 | 状态 | 备注 |
|--------|------|------|
| 检查项1 | ✅符合 / ⚠️部分 / ❌不符合 | |
| 检查项2 | ✅符合 / ⚠️部分 / ❌不符合 | |

## 层级关系

### derivedFrom（来源于）
- [[Parent-Standard-1]]
- [[Regulation-1]]

### relatedTo（相关）
- [[Related-Rule-1]]
- [[Related-Standard-1]]

## 合规度量

| 度量指标 | 目标值 | 当前值 | 状态 |
|----------|--------|--------|------|
| 合规率 | 100% | — | — |
| 审计通过率 | 100% | — | — |

## 与其他规则的关系

```viz
graph TB
    R1[Regulation: 上位法] -->|derivedFrom| S1[Standard: 标准]
    S1 -->|derivedFrom| R2[Rule: 内部规则]
    
    R2 -->|constrains| P1[Performer/Activity]
```

## 备注

{additional notes}

---

## 子分类

| 目录 | 用途 | 示例 |
|------|------|------|
| **Rule/** | 规定性文件：法律、行政法规、部门规章、规范性文件、通知等 | 《网络安全法》、《数据安全法》、《个人信息保护法》、等保2.0、密评办法 |
| **Standard/** | 标准性文件：国际标准、国家标准、行业标准、企业标准、项目标准 | ISO 27001、GB/T 22239、GA/T 1389、行业安全规范 |

> [!tip] 使用说明
> - 法规类文档优先使用 [[Rule-Template]]
> - 标准类文档优先使用 [[Standard-Template]]

---

**相关数据组**：[[Guidance]] | [[Performer]] | [[Activity]] | [[Resource]]
