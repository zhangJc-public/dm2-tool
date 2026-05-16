# 06-Measure

## 📌 一句话说明
**度量——怎么衡量。** 从质量到物理量再到效果的全谱系度量框架。

## 🎯 目录用途
- 存储度量指标类型和实例
- 覆盖 4 大类 11 种度量类型
- 连接到任意可度量实体（Performer/Capability/Activity 等）

## 📂 结构一览
```
06-Measure/
├── AGENT.md                  ← 本文件
├── Measure-Template.md       ← 操作模板
└── Measure-Type/             ← （待补充）11种度量类型速查卡片
```

## 11 种度量类型速查

| 类别 | 类型 | 说明 |
|------|------|------|
| **质量度量** | AdaptabilityMeasure | 适应性 |
| | MaintainabilityMeasure | 可维护性 |
| | NeedsSatisfactionMeasure | 需求满意度 |
| | PerformanceMeasure | 性能 |
| | OrganizationalMeasure | 组织运营成本 |
| **物理度量** | PhysicalMeasure | 时空范围（长度/质量/能量） |
| | SpatialMeasure | 位置坐标 |
| | TemporalMeasure | 时间跨度 |
| **技能度量** | MeasureableSkill | 可量化技能 |
| **效果度量** | MeasureOfDesire | 期望程度 |
| | MeasureOfEffect | 效果达成度 |

## 🔗 关联目录
| 关联 | 目录 | 关系 |
|------|------|------|
| 度量对象 | 几乎所有数据组 | measures (反向: measuredBy) |
| 时间边界 | `00-基础模式/TemporalPartAndBoundaries` | Measure 集成到时间边界上 |
| 分析 | `../详细分析/DM2-Measure详细分析.md` | 深度理论 |

## 🤖 Agent 协作规则
1. **direction 必填**：每个度量必须标明 higher-is-better / lower-is-better / target-is-best
2. **unit 必填**：即使是非物理度量也应有单位（如："分"、"%"、"级"）

## 📊 当前状态
- 实体数量: 1 个（仅模板）
- 最后更新: 2026-04-18（重构创建 AGENT）
- 覆盖度: ⚠️ 空壳（待补充 11 种度量类型卡片）
