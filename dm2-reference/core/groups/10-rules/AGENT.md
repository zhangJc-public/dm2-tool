# 10-Rules

## 📌 一句话说明
**规则——条件/约束/逻辑。** ⚠️ 从 Guidance 中拆出的独立数据组，侧重形式化业务规则。

## 🎯 目录用途
- 存储 Rule 的形式化定义（条件→动作/约束）
- 与 05-Guidance 的区别：Guidance = 法规文档本身；Rules = 从法规中提取的可执行逻辑
- 支持 Condition（条件）、Constraint（约束）、Requirement（需求）三类

## 📂 结构一览
```
10-Rules/
├── AGENT.md                  ← 本文件
├── Rules-Template.md         ← 操作模板
└── README.md                 → 链接到 [[../详细分析/DM2-Rules详细分析]]
```

## 🔗 关联目录
| 关联 | 目录 | 关系 |
|------|------|------|
| 来源 | `05-Guidance` | Rules 从 Guidance 文档中提取 |
| 约束对象 | 所有数据组 | appliesTo |
| 效果导向 | `02-Activity` | DesiredEffect（期望效果） |
| 分析 | `../详细分析/DM2-Rules详细分析.md` | 最详细的分析之一（36KB） |

## 🤖 Agent 协作规则
1. **⚠️ vs Guidance 的定位差异**：Guidance 放原文（如等保2.0全文），Rules 放提取的规则条目（如："三级系统必须具备XXX")
2. **新建时先查 Guidance**：创建 Rule 实例前，确认对应的 Guidance 文档已存在

## 📊 当前状态
- 实体数量: 0 个（待创建模板）
- 最后更新: 2026-04-18（重构创建）
- 覆盖度: ⚠️ 新建目录
