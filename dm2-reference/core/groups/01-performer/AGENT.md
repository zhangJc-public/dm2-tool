# 01-Performer

## 📌 一句话说明
**执行者——谁在做。** DM2 中最核心的数据组，涵盖人、组织、系统、角色。

## 🎯 目录用途
- 存储所有 Performer 类型和实例（组织、人员角色、系统）
- 提供统一模板确保新建实例格式一致
- 管理组织类型分类和系统产品型号层次

## 📂 结构一览
```
01-Performer/
├── AGENT.md                           ← 本文件
├── Performer-Template.md              ← 主模板（Organization/System/PersonRole 统一入口）
├── Organization/
│   ├── Organization-Template.md        ← 组织专用模板
│   ├── Organization-Type/             ← ⚠️ 项目利益相关者角色（非DM2标准类型）
│   │   ├── 甲方.md ~ 监管方.md         ← 9 种项目角色
│   └── 启明星辰.md                     ← 组织实例
└── System/
    ├── System-Type/                   ← 系统类型（如：防火墙、下一代防火墙）
    │   └── 下一代防火墙/               ← 产品系列
    └── System-Individual/             ← 具体设备实例
        └── 下一代防火墙/               ← 具体型号
```

## 🔗 关联目录
| 关联 | 目录 | 关系 |
|------|------|------|
| 执行活动 | `02-Activity` | performs / performedBy |
| 具有能力 | `03-Capability` | hasCapability / performedBy |
| 消耗资源 | `04-Resource` | consumesResource |
| 位于 | `07-Location` | locatedAt |
| 被度量 | `06-Measure` | measuredBy |
| 提供服务 | `08-Services` | providesService |
| 组织结构 | `14-OrgStructure` | partOf / hasPart (Overlap) |
| 分析 | `../详细分析/DM2-Performer详细分析.md` | 深度理论 |

## 🤖 Agent 协作规则
1. **创建新实例**：必须使用 `Performer-Template.md` 或对应子模板
2. **⚠️ Organization-Type 注意**：当前 9 个角色（甲方/乙方等）是"项目利益相关者"分类，不是 DM2 标准的 OrganizationType。如需添加 DM2 标准组织类型，应新建子目录区分
3. **System 作为子类型**：System 是 Performer 的合法子类型（DM2 v2 定义），但需注意与 Services 的边界——System 是"执行者"，Service 是"接口"
4. **修改模板时**：同步更新 `相关分析` 链接

## 📊 当前状态
- 实体数量: ~27 个（1 主模板 + 1 组织模板 + 9 角色类型 + 1 组织实例 + 6 系统类型 + 10 产品实例）
- 最后更新: 2026-04-18（重构创建 AGENT）
- 覆盖度: ✅ 最完善的目录（有类型、子类型、实例三层）
