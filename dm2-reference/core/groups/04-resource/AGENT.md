# 04-Resource

## 📌 一句话说明
**资源——用什么。** 信息、数据、物资的总称，是活动和服务的操作对象。

## 🎯 目录用途
- 存储资源类型和实例（文档、数据、API、设备物资等）
- 区分 Resource / Information / DataType 三种子类型
- 管理资源的表示关系（representedBy）、敏感度、访问方式

## 📂 结构一览
```
04-Resource/
├── AGENT.md                    ← 本文件
├── Resource-Template.md        ← 操作模板（已修复 YAML 断裂 ✅）
├── Information/                ← （待补充）信息特化子类型
│   ├── Sign/                   ← 符号/标记
│   ├── Representation/         ← 表示形式
│   └── Data/                   ← 数据内容
└── DataType/                   ← （待补充）数据类型定义
```

## 🔗 关联目录
| 关联 | 目录 | 关系 |
|------|------|------|
| 表示为 | `16-InfoData` | representedBy (Sign/Rep/Data 三层) |
| 消费/生产 | `01-Performer`, `02-Activity` | consumedBy / producedBy |
| 存储/位于 | `07-Location` | storedAt / locatedIn |
| 访问方式 | `08-Services` | accessedVia |
| 流经 | `11-ResourceFlow` | flowsThrough |
| 血缘 | `12-Pedigree`, `13-InfoPedigree` | 生产追溯 |
| 分析 | `../详细分析/DM2-InformationAndData详细分析.md` | 深度理论 |

## 🤖 Agent 协作规则
1. **与 16-InfoData 的边界**：04-Resource 侧重**资源管理视角**（谁用/存哪/敏感度）；16-InfoData 侧重**抽象表示视角**（Sign→Rep→Data 三层本体）。同一实体可能两边都有条目但角度不同
2. **sensitivity 字段必填**：资源模板包含机密级字段，创建实例时必须评估

## 📊 当前状态
- 实体数量: 1 个（仅模板，YAML 已修复 ✅）
- 最后更新: 2026-04-18（重构修复+AGENT）
- 覆盖度: ⚠️ 空壳（待补充 Information/DataType 子类型）
