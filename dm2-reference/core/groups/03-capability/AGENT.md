# 03-Capability

## 📌 一句话说明
**能力——能做什么。** 战略层到技术层的分层能力体系，连接愿景与执行。

## 🎯 目录用途
- 存储能力类型和实例（从战略能力到具体功能能力）
- 支持三层模型：TypeType → Type → Individual
- 能力映射到 Activity（使能活动）和 Project（实现载体）

## 📂 结构一览
```
03-Capability/
├── AGENT.md                      ← 本文件
├── Capability-Template.md        ← 操作模板
└── Capability-Type/              ← （待补充）能力层次分类
```

## 🔗 关联目录
| 关联 | 目录 | 关系 |
|------|------|------|
| 使能活动 | `02-Activity` | enablesActivity / mapsActivity |
| 执行者 | `01-Performer` | performedBy |
| 实现项目 | `09-Project` | realizedByProject |
| 子/父能力 | `03-Capability` (自身) | composedOf / contributesTo |
| 度量 | `06-Measure` | measuredBy |
| 分析 | `../详细分析/DM2-Capability详细分析.md` | 深度理论 |

## 🤖 Agent 协作规则
1. **三层模型**：创建实例时明确标注 dm2-layer（TypeType=战略能力 / Type=作战能力 / Individual=具体能力项）
2. **能力分解原则**：父能力 = 子能力的语义聚合（不是简单相加），避免过度拆解

## 📊 当前状态
- 实体数量: 1 个（仅模板）
- 最后更新: 2026-04-18（重构创建 AGENT）
- 覆盖度: ⚠️ 空壳（待补充能力层次示例）
