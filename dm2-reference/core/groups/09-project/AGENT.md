# 09-Project

## 📌 一句话说明
**项目——实现能力的载体。** 将 Capability 从愿景变为现实的投资组合和执行单元。

## 🎯 目录用途
- 存储项目类型和实例
- 管理项目阶段（ProjectPhase）和里程碑
- 连接 Capability（实现什么能力）和 Performer（谁执行）

## 📂 结构一览
```
09-Project/
├── AGENT.md                  ← 本文件
├── Project-Template.md       ← 操作模板
└── ProjectPhase/             ← （待补充）项目阶段分类
```

## 🔗 关联目录
| 关联 | 目录 | 关系 |
|------|------|------|
| 实现能力 | `03-Capability` | realizedByProject |
| 执行者 | `01-Performer` | performedBy |
| 时间依赖 | `00-基础模式/TemporalPartAndBoundaries` | 项目时间由 temporalWP 建模 |
| 度量 | `06-Measure` | 项目绩效度量 |
| 分析 | `../详细分析/DM2-Project详细分析.md` | 含中国适配性分析 |

## 🤖 Agent 协作规则
1. **Project 是 Individual 层为主**：具体项目通常不涉及 TypeType 层
2. **阶段管理**：使用 temporalWholePart 或 BeforeAfter 建模项目阶段关系

## 📊 当前状态
- 实体数量: 1 个（仅模板，待创建）
- 最后更新: 2026-04-18（重构创建）
- 覆盖度: ⚠️ 新建目录
