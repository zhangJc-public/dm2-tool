# DM2 元模型参考主页

> DoDAF Meta Model 2.02 — 16 个数据组 + 5 个基础模式 · 完整索引  
> 📅 最后更新: **2026-04-18**（重构完成）  
> ✅ **状态**: 全部 18 张类图分析已完成，知识库已重构

---

## 快速导航

### 基础模式层（00-基础模式）
> DM2 的"语法"——所有数据组遵循的元模式

| #   | 模式                                      | 一句话                                     | 详情               |
| --- | --------------------------------------- | --------------------------------------- | ---------------- |
| 1   | [[00-基础模式/IDEAS-TopLevel]]              | 世界由什么构成？Thing→Individual/Type/Tuple 四分法 | 四分类本体公理          |
| 2   | [[00-基础模式/FoundationForAssociations]]   | 事物如何关联？5 种原子关联模式                        | 关联语法速查           |
| 3   | [[00-基础模式/CommonPatterns]]              | Type 和 Instance 怎么对应？双面板映射              | Instance/Type 对照 |
| 4   | [[00-基础模式/NamingAndDescriptionPattern]] | 实体如何被识别和描述？Name/Desc/Rep/Scheme         | 身份系统             |
| 5   | [[00-基础模式/TemporalPartAndBoundaries]]   | 时间如何建模？可重叠！边界即实体                        | 时间建模             |

### 业务数据组（01~10）

#### 核心执行链

| # | 数据组 | 一句话 | 模板 | 分析文档 |
|---|--------|--------|------|---------|
| **01** | [[01-Performer]] | **谁在做** | [[01-Performer/Performer-Template]] | [[详细分析/DM2-Performer详细分析]] |
| **02** | [[02-Activity]] | **做什么** | [[02-Activity/Activity-Template]] | （嵌入 Performer 分析）|
| **03** | [[03-Capability]] | **能做什么** | [[03-Capability/Capability-Template]] | [[详细分析/DM2-Capability详细分析]] |
| **09** | [[09-Project]] | **实现能力的载体** | [[09-Project/Project-Template]] | [[详细分析/DM2-Project详细分析]] |

#### 资源与治理

| # | 数据组 | 一句话 | 模板 | 分析文档 |
|---|--------|--------|------|---------|
| **04** | [[04-Resource]] | **用什么** | [[04-Resource/Resource-Template]] | [[详细分析/DM2-InformationAndData详细分析]] |
| **05** | [[05-Guidance]] | **遵守什么规则** | [[05-Guidance/Guidance-Template]] | [[详细分析/DM2-Rules详细分析]] |
| **08** | [[08-Services]] | **提供的接口** | [[08-Services/Services-Template]] | [[详细分析/DM2-Services详细分析]] |
| **10** | [[10-Rules]] | **条件/约束/逻辑** | [[10-Rules/Rules-Template]] | [[详细分析/DM2-Rules详细分析]] |

#### 度量与位置

| # | 数据组 | 一句话 | 模板 | 分析文档 |
|---|--------|--------|------|---------|
| **06** | [[06-Measure]] | **怎么衡量** | [[06-Measure/Measure-Template]] | [[详细分析/DM2-Measure详细分析]] |
| **07** | [[07-Location]] | **在哪** | [[07-Location/Location-Template]] | [[详细分析/DM2-Location详细分析]] |

### 交叉层面数据组（11~16）

| # | 数据组 | 一句话 | 入口 | 分析文档 |
|---|--------|--------|------|---------|
| **11** | [[11-ResourceFlow]] | 资源如何流转 | [[11-ResourceFlow/README]] | [[详细分析/DM2-ResourceFlow详细分析]] |
| **12** | [[12-Pedigree]] | 万物来源追溯 | [[12-Pedigree/README]] | [[详细分析/DM2-Pedigree详细分析]] |
| **13** | [[13-InformationPedigree]] | 信息资源追溯 | [[13-InformationPedigree/README]] | [[详细分析/DM2-InformationPedigree详细分析]] |
| **14** | [[14-OrganizationalStructure]] | 组织间关系（Overlap） | [[14-OrganizationalStructure/README]] | [[详细分析/DM2-OrgStructure详细分析]] |
| **15** | [[15-ReificationLevels]] | Type↔Individual 转换规则 | [[15-ReificationLevels/README]] | [[详细分析/DM2-Reification详细分析]] |
| **16** | [[16-InformationAndData]] | Sign/Rep/Data 三层表示 | [[16-InformationAndData/README]] | [[详细分析/DM2-InformationAndData详细分析]] |

---

## DM2 核心价值链

```
Vision(愿景) → Capability(能力) → Project(项目) → Activity(活动) → Performer(执行者) → Resource(资源)
     ↓              ↓              ↓            ↓               ↓              ↓
   CV-1           CV-2          PV-1         OV-5b           OV-4          DIV-1/DIV-2
                                                                              ↓
                                                                    Guidance(规则) ← Measure(度量)
                                                                          ↓              ↓
                                                                     Location(位置) ← Services(接口)
```

---

## 创建新实体的快速入口

| 要创建什么？ | 用这个模板 |
|-------------|-----------|
| 组织 / 系统 / 角色 | [[01-Performer/Performer-Template]] |
| 具体组织实例 | [[01-Performer/Organization/Organization-Template]] |
| 活动 | [[02-Activity/Activity-Template]] |
| 能力 | [[03-Capability/Capability-Template]] |
| 资源/信息 | [[04-Resource/Resource-Template]] |
| 法规/标准（通用） | [[05-Guidance/Guidance-Template]] |
| 法律/法规 | [[05-Guidance/Rule/Rule-Template]] |
| 国家/行业标准 | [[05-Guidance/Standard/Standard-Template]] |
| GA 行业标准 | [[05-Guidance/Standard/公共安全行业标准-Template]] |
| 度量指标 | [[06-Measure/Measure-Template]] |
| 位置 | [[07-Location/Location-Template]] |
| 服务 | [[08-Services/Services-Template]] |
| 项目 | [[09-Project/Project-Template]] |
| 业务规则 | [[10-Rules/Rules-Template]] |

---

## 归档区

| 区域 | 内容 | 数量 |
|------|------|------|
| [[详细分析]] | 18 张类图深度分析文档 | 18 |
| [[研究]] | 前瞻性研究报告 + 元模型总报告 | 3 |
| [[总览文档]] | 本页 + 类图总览 + 完整定义 + 治理方案 | 4 |

---

## 知识库架构层次

```
IDEAS TopLevel (本体公理)          ← 00-基础模式/IDEAS-TopLevel
  ↓
Foundation (关联语法)             ← 00-基础模式/FoundationForAssociations
  ↓
Common Patterns (模式对照)        ← 00-基础模式/CommonPatterns
  ↓
Naming / Temporal (身份+时间)      ← 00-基础模式/ Naming & Temporal
  ↓
┌─────────────────────────────────────────────┐
│           10 大业务数据组                      │
│  Performer / Activity / Capability / Resource │
│  / Guidance / Measure / Location             │
│  / Services / Project / Rules                │
└─────────────────────────────────────────────┘
  ↓
交叉层面：Pedigree / InfoPedigree / OrgStructure / Reification / InfoData / ResourceFlow
```

---
*基于 DoDAF 2.02 DM2 规范 + 18 张类图完整分析构建*
