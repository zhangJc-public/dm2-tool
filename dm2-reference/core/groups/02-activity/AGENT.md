# 02-Activity

## 📌 一句话说明
**活动——做什么。** Performer 执行的动作，是能力（Capability）的具象化。

## 🎯 目录用途
- 存储所有 Activity 类型和实例
- 活动是 OV-5b 作战活动模型的核心实体
- 连接 Performer（谁做）→ Resource（用什么）→ Guidance（遵守什么规则）

## 📂 结构一览
```
02-Activity/
├── AGENT.md                    ← 本文件
├── Activity-Template.md        ← 操作模板
└── Activity-Type/              ← （待补充）活动类型分类
```

## 🔗 关联目录
| 关联 | 目录 | 关系 |
|------|------|------|
| 执行者 | `01-Performer` | performedBy / performs |
| 归属能力 | `03-Capability` | mapsToCapability / enablesActivity |
| 消耗/产生 | `04-Resource` | consumes / produces |
| 治理规则 | `05-Guidance` / `10-Rules` | governedBy |
| 前置/后继 | `02-Activity` (自身) | prerequisite / successor |
| 度量 | `06-Measure` | measuredBy |

## 🤖 Agent 协作规则
1. **⚠️ 无独立类图分析**：Activity 在 DM2 中没有独立的类图，其元模型定义嵌入在 Performer 和 Capability 分析中。查询形式化定义时请跳转到 `DM2-Performer详细分析.md`
2. **活动分类建议**：按 ICOM 分类（输入/控制/输出/机制）或按层级（作战/战术/操作）

## 📊 当前状态
- 实体数量: 1 个（仅模板）
- 最后更新: 2026-04-18（重构创建 AGENT）
- 覆盖度: ⚠️ 空壳（待补充 Activity-Type 分类）
