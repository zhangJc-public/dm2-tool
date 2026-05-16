# 12-Pedigree

## 📌 一句话说明
**血缘——实体来源追溯。** 万物的"出生证明"和生产流程追踪。

## 🎯 目录用途
- Pedigree 是 DM2 的通用血缘模型（适用于所有数据组）
- 追溯实体的：来源(source)、派生自(derivedFrom)、置信度(confidence)
- 支持生产流程网络：Consumes → Produces → Rules → Measures → Performers → Locations

## 📂 结构一览
```
12-Pedigree/
├── AGENT.md          ← 本文件
└── README.md         → 链接到 [[../详细分析/DM2-Pedigree详细分析]]
```

## 🔗 关联目录
| 关联 | 目录 | 关系 |
|------|------|------|
| 信息特化 | `13-InformationPedigree` | Pedigree 在信息领域的精炼版 |
| 所有实体 | 全部数据组 | 每个 Template 都有 pedigree 字段块 |

## 🤖 Agent 协作规则
1. **本目录是"横切关注点"**：Pedigree 不单独创建实例，而是嵌入到每个实体的 frontmatter 中
2. **生产流程网络是核心图景**：6 种节点（Consume/Produce/Rules/Measures/Perf/Loc）+ 若干有向边

## 📊 当前状态
- 实体数量: 0 个（纯参考目录）
- 最后更新: 2026-04-18（重构创建）
- 覆盖度: ✅ 完整
