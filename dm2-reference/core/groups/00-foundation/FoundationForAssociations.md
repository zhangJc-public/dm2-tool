# Foundation For Associations（关联语法基础）

> 📄 **完整分析** → [[../详细分析/DM2-FoundationForAssociations详细分析]]

## 一句话
DM2 的"元素周期表"——5 种原子关联模式组合出所有复杂关系。

## 五大核心关联

| # | 模式 | 方向性 | 可重叠 | 典型用途 | 刚性 |
|---|------|--------|--------|---------|------|
| 1 | **WholePart** | 有向 | ❌ 不可 | 组成关系（部分→整体） | 🔴 强（互斥边界） |
| 2 | **BeforeAfter** | 有向 | ❌ 不可 | 时序/因果（前→后） | 🔴 强 |
| 3 | **Overlap** | 无向 | ✅ 可！ | 共享/交叉（运行时重叠） | 🟡 弱 |
| 4 | **Couple** | 有向 | 视情况 | 万能基类（任意语义关联） | ⚪ 最弱 |
| 5 | **TemporalWholePart** | 有向 | ✅ 可！ | 时间段组成（WP+BA混合） | 🟡 中 |

## 最重要区分：WholePart ≠ Overlap

```
WholePart:  A 是 B 的一部分 → A 不能同时属于 C（互斥）
            例：手指是手的一部分，不能同时属于另一只手

Overlap:    A 与 B 有交集 → A 可以同时与 C、D...重叠
            例：一个人同时在多个活动中扮演不同角色（用 Overlap 连接 Performer ↔ Activity）
```

## 三角关系（Instance 层）

```
superSubtype        ← 类型继承（父→子）
     ↕
typeinstance        ← Type 被实例化（模板→实例）
     ↕
powertypeInstance   ← Powertype 维度分类实例
```
这三个 instance 关系构成了 Instance 层的类型体系骨架。

## 90% 原则

这 5 种模式覆盖了 DM2 建模中 **90% 以上** 的关联需求。遇到新关系时，先问：
1. 是组成吗？→ WholePart
2. 是时序/因果吗？→ BeforeAfter  
3. 是共享/交叉吗？→ Overlap
4. 都不是但有语义关联？→ Couple
5. 是时间段？→ TemporalWholePart

---
*基于 DM2-FoundationForAssociations详细分析.md 提炼 | 2026-04-18*
