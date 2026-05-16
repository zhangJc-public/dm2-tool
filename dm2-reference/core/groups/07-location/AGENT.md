# 07-Location

## 📌 一句话说明
**位置——在哪。** 物理位置、地缘政治范围、几何形状的三维位置模型。

## 🎯 目录用途
- 存储位置类型和实例
- 三类位置：物理（国家→场地→设施）、地缘（边界/静止点）、几何（点线面体）
- 支持 Performer/Resource 的 locatedAt / storedIn

## 📂 结构一览
```
07-Location/
├── AGENT.md                  ← 本文件
├── Location-Template.md      ← 操作模板
└── Location-Type/            ← （待补充）3类位置示例
```

## 3 类 15 种位置类型

| 类别 | 子类型 | 示例 |
|------|--------|------|
| **物理** | Country / RegionOfCountry / Site / Installation / Facility | 中国 → 华北区 → A园区 → 机房A → 机柜03 |
| **地缘** | GeoFeature / GeoPoliticalExtent / GeoStationaryPoint | 台风路径 / 领海边界 / 同步轨道定点 |
| **几何** | Point / Line / PlanarSurface / CircularArea / EllipticalArea / RectangularArea / PolygonArea / SolidVolume | 经纬度 / 路线 / 区域 / 圆形覆盖区 |

## 🔗 关联目录
| 关联 | 目录 | 关系 |
|------|------|------|
| 托管 | `01-Performer` | hosts |
| 存储 | `04-Resource` | storedAt |
| 位于 | `04-Resource` | locatedIn |
| 分析 | `../详细分析/DM2-Location详细分析.md` | 深度理论 |

## 🤖 Agent 协作规则
1. **坐标优先**：创建位置实例时优先填写 coordinates（几何坐标比文本地址更可计算）
2. **层次一致性**：Site → Installation → Facility 应保持地理包含关系

## 📊 当前状态
- 实体数量: 1 个（仅模板）
- 最后更新: 2026-04-18（重构创建 AGENT）
- 覆盖度: ⚠️ 空壳（待补充 3 类位置示例）
