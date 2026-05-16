# IDEAS Top Level（IDEAS 顶层本体）

> 📄 **完整分析** → [[../详细分析/DM2-IDEASTopLevel详细分析]]

## 一句话
DM2 的"创世神话"——世界由 Thing 分化为 Individual（具体物）、Type（类）、Tuple（关系组）三类，且 **Individual IS-A Type**。

## 四大根本分类

```
Thing (万物)
├── Individual    ← 具体的、可识别的单一实体（如：启明星辰公司）
│   └── IS-A → Type ✨ (每个 Individual 都是某个 Type 的实例)
├── Type          ← 类别/模板（如：组织类型）
│   ├── superSubtype → 父子类型继承
│   ├── typeinstance → Type 本身也可以被实例化
│   └── powertypeInstance → Powertype 分类实例化
└── TupleType     ← 关系组类型（如：一对多关联的抽象）
    └── Tuple     ← 具体关联实例
```

## 核心公理

| 公理 | 含义 | 与 OWL/UML 对比 |
|------|------|----------------|
| **Individual IS-A Type** | 单例模式的形式化——某个 Type 只有一个 Instance 时，它本身就是 Individual | UML 无此概念；OWL 用 owl:sameAs 勉强模拟 |
| **Tuple 是一等公民** | 关系本身也是实体，可以有自己的属性和血缘 | OWL 把属性当二等公民 |
| **Powertype 分类** | Type 的 Type——按维度分类（如：按行业分 Organization） | UML 无原生支持 |

## 关键洞察

1. **IDEAS 是 DM2 的"看不见的手"**——不在任何视图中直接出现，但定义了所有实体的存在方式
2. **Individual IS-A Type 解决了单例问题**——不需要为单个实体单独建 Type
3. **Tuple 让关系可追溯**——关联不是"线"而是"实体"，可以度量、约束、血缘追踪

## 快速决策

| 场景 | 选什么 | 示例 |
|------|--------|------|
| 有多个实例的事物 | Type + Individual | 防火墙类型 → 天清汉马-USG-NF |
| 只有一个实例的事物 | 直接用 Individual（IS-A Type） | 某特定 SOC 平台 |
| 需要对 Type 再分类 | Powertype | 组织按行业/规模/性质多维分类 |
| 关系本身有属性 | Tuple | "部署关系"需要记录部署时间、责任人 |

---
*基于 DM2-IDEASTopLevel详细分析.md 提炼 | 2026-04-18*
