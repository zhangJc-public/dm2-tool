# Naming and Description Pattern（命名与描述模式）

> 📄 **完整分析** → [[../详细分析/DM2-NamingAndDescriptionPattern详细分析]]

## 一句话
DM2 的"身份系统"——每个实体如何被命名、描述、表示和治理。

## 四区域模型

```
┌─────────────────────────────────────────────┐
│              Representation（表示层）         │  ← Sign / 数据格式
│  Sign ← Representation ← Information        │
├─────────────────────────────────────────────┤
│              Description（描述层）             │  ← 定义 + 安全属性
│  Description + SecurityAttributesGroup       │
├─────────────────────────────────────────────┤
│              Name（名称层）                   │  ← 身份标识
│  Name + NamingScheme                         │
└─────────────────────────────────────────────┘
                    ↕
              Scheme（治理层）                  ← 命名规范 / 描述规范 / 表示规范
```

## 三个 "By" 关系（最易混淆！）

| 关系 | 问题回答 | 方向 | 示例 |
|------|---------|------|------|
| **namedBy** | 叫什么名字？ | Entity → Name | "启明星辰" namedBy 中文名称 |
| **describedBy** | 怎么描述？ | Entity → Description | 公司 describedBy 企业简介 |
| **representedBy** | 用什么表示？ | Resource → Data | 标准 PDF representedBy 文件数据 |

**三者不可替代**：名称 ≠ 描述 ≠ 表示。一个实体可以有多种名称（同义词）、多种描述（多语言/多视角）、多种表示（PDF/HTML/数据库）。

## Scheme = 治理

- **NamingScheme**：命名规范（如："设备编号采用 [类别]-[序号]" 格式）
- **DescriptionScheme**：描述规范（如："安全设备必须包含 CVE 编号"）
- **RepresentationScheme**：表示规范（如："法规原文必须保留官方扫描件"）

## SecurityAttributesGroup 内建于描述层

安全标记（机密级/分发控制）不是后加的属性，而是描述层的**内建组成部分**。

---
*基于 DM2-NamingAndDescriptionPattern详细分析.md 提炼 | 2026-04-18*
