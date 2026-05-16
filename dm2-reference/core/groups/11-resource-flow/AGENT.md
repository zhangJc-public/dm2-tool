# 11-ResourceFlow

## 📌 一句话说明
**资源流动——资源如何流转。** 纯关系视角，描述资源在 Performer 之间的流动。

## 🎯 目录用途
- ResourceFlow 不是独立实体类型，而是**资源流动关系的建模规范**
- 描述：谁 → 什么资源 → 给谁 → 在什么条件下
- SV-4 系统功能描述和 DIV-2/3 数据视图的基础

## 📂 结构一览
```
11-ResourceFlow/
├── AGENT.md          ← 本文件
└── README.md         → 链接到 [[../详细分析/DM2-ResourceFlow详细分析]]
```

## 🔗 关联目录
| 关联 | 目录 | 关系 |
|------|------|------|
| 流动资源 | `04-Resource` | 流动的对象 |
| 生产者/消费者 | `01-Performer` | producedBy / consumedBy |
| 经过的系统 | `01-Performer` | flowsThrough |
| 分析 | `../详细分析/DM2-ResourceFlow详细分析.md` | 深度理论 |

## 🤖 Agent 协作规则
1. **本目录不放实例**：ResourceFlow 是关系模式，不是实体类型。具体的流动记录应在相关 Activity 或 Performer 实例中描述
2. **参考价值**：主要用于设计 SV-4 和数据流视图时的建模参考

## 📊 当前状态
- 实体数量: 0 个（纯参考目录）
- 最后更新: 2026-04-18（重构创建）
- 覆盖度: ✅ 完整（README 链接到详细分析）
