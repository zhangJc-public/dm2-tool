---
type: dm2/location
dm2-layer: Type | Individual
dm2-subtype: '# 物理位置 (Physical)

  Country |            # 政治国家

  RegionOfCountry |    # 国家的区域

  Site |              # 场地（拥有/租赁的物理位置）

  Installation |      # 设施（基地、营地、站等）

  Facility |          # 不动产（土地+建筑+设备）

  # 地缘特征 (Geo Features)

  GeoFeature |        # 地理特征（气象、地理、控制）

  GeoPoliticalExtent | # 地缘政治范围（边界由协议决定）

  GeoStationaryPoint | # 地理静止点

  # 几何位置 (Geometric)

  Point |             # 点

  Line |              # 线

  PlanarSurface |     # 平面

  CircularArea |      # 圆形区域

  EllipticalArea |    # 椭圆区域

  RectangularArea |   # 矩形区域

  PolygonArea |       # 多边形区域

  SolidVolume |      # 体积

  '
name: null
definition: null
synonyms: []
coordinates: ''
address: ''
relationships:
  hosts: []
  partOf: []
  hasPart: []
  adjacentTo: []
  connectedTo: []
pedigree:
  source: ''
  derivedFrom: []
  confidence: high | medium | low
  lastUpdated: ''
keywords:
- 位置
- 地点
- 场所
- location
- site
- facility
- 数据中心
- 机房
- 部署
- 网络区域
- 云
- 区域
- cloud
- region
- zone
- 部署点
related_dm2_views:
- OV-1
- OV-2
tags:
- dm2/location
- dm2/physical
- dm2/logical
- dm2/virtual
相关分析: '[[../详细分析/DM2-Location详细分析]]'
---

# {名称}

## 基本信息

| 属性 | 值 |
|------|-----|
| DM2 类型 | Location |
| 子类型 | {Physical | Logical | Virtual} |
| 地理坐标 | {coordinates} |
| 物理地址 | {address} |
| 同义词 | {synonyms} |

## 定义

{definition}

## 位置类型

### Physical（物理位置）
- 数据中心
- 办公楼
- 机房

### Logical（逻辑位置）
- 网络区域（DMZ、Intranet）
- 安全域
- VLAN

### Virtual（虚拟位置）
- 云区域
- 边缘节点
- 容器集群

## 托管对象

### hosts（托管）
- [[Performer-1]] — 类型：数据中心
- [[Resource-1]] — 类型：服务器集群

## 层级关系

```viz
graph TB
    L1[Location Parent] -->|hasPart| L2[Location: {名称}]
    L2 -->|hasPart| L3[Location Child 1]
    L2 -->|hasPart| L4[Location Child 2]
```

### partOf（所属）
- [[Parent-Location-1]]

### hasPart（包含）
- [[Child-Location-1]]
- [[Child-Location-2]]

## 连接关系

### connectedTo（连接）
- [[Location-1]] — 类型：专线
- [[Location-2]] — 类型：VPN

### adjacentTo（邻近）
- [[Adjacent-Location-1]]

## 安全边界

| 安全域 | 级别 | 说明 |
|--------|------|------|
| {安全域1} | 高 | 核心系统 |
| {安全域2} | 中 | 一般业务 |

## 网络拓扑

```viz
graph LR
    subgraph {位置名称}
        N1[Network Zone 1]
        N2[Network Zone 2]
    end
    
    N1 -->|防火墙| N2
```

## 备注

{additional notes}

---

**相关数据组**：[[Location]] | [[Performer]] | [[Resource]]
