# SDD 开发计划：DoDAF 工具

> 基于 dm2-system-assistant 雏形的改进建议
> 创建日期：2026-05-01

---

## 1. 核心建议：先固化 DM2 元模型

SDD 第一步是数据建模：

```
DM2 元模型核心
├── 18个数据组 → 18张实体表
├── 原子关联类型 → 关系表
├── 视图模板 → 结构化定义
└── 约束规则 → R1~R5 硬约束逻辑
```

---

## 2. 分离"知识库"和"引擎"

| 模块 | 职责 | 优先级 |
|------|------|--------|
| **DM2 Kernel** | 元模型、关联规则、约束校验 | P0 |
| **View Engine** | 视图生成逻辑、模板渲染 | P0 |
| **KB Manager** | 知识库 CRUD、链接维护 | P1 |
| **CLI/UI** | 用户交互层 | P2 |

---

## 3. 关键实体设计

| 实体 | 说明 |
|------|------|
| **Concept** | Performer/Activity/Capability/Resource 等 DM2 概念 |
| **Relationship** | WholePart/BeforeAfter/Overlap/Couple/TemporalWholePart |
| **View** | OV/SV/CV/SvcV/DIV 等视图定义 |
| **Change** | 提案/实施/归档的完整生命周期 |

## 4. 关键流程

| 流程 | 说明 |
|------|------|
| `propose` | 创建变更 + 生成工件（scope/data-plan/view-proposal/tasks） |
| `apply` | 执行任务 + 更新状态 |
| `archive` | 归档 + 同步知识库 |

---

## 5. 建议的模块划分

```python
# 核心模块建议
dm2/
├── kernel/           # DM2 元模型核心
│   ├── meta_model.py # 18数据组定义
│   ├── constraints.py # R1~R5 约束
│   └── relationships.py # 原子关联
├── engine/           # 执行引擎
│   ├── explorer.py   # Cynefin + 7步法
│   ├── analyzer.py   # OODA/TOC/Abduction
│   └── view_gen.py   # 视图生成
├── kb/               # 知识库
│   ├── indexer.py    # Obsidian 同步
│   └── query.py      # 检索
└── cli/              # 命令行入口
```

---

## 6. 当前雏形的不足（改进方向）

| 现状 | 改进 |
|------|------|
| 视图是静态 Markdown | 结构化视图对象 + 模板引擎 |
| 约束靠人工检查 | 代码化的 R1~R5 校验器 |
| 任务状态靠编辑 checkbox | 状态机管理 |
| 知识库是散文件 | 索引 + 查询引擎 |

---

## 7. 技术栈建议

| 组件 | 推荐技术 |
|------|----------|
| Kernel | 纯 Python（无框架依赖） |
| 存储 | SQLite（轻量）+ Obsidian Vault（人类可读） |
| CLI | Click/Typer |
| 模板 | Jinja2（视图渲染） |
| 测试 | pytest（约束规则回归测试） |

---

## 8. 核心原则

> 先把 DM2 约束规则和视图生成逻辑做扎实，这些是工具的价值核心。UI/CLI 可以后期迭代。

---

## 9. 四条核心路径（约束校验）

```
1. 主追溯链: CV-1 → CV-2 → CV-6/CV-7 → OV-5b → SV-4/SvcV-4
2. 数据细化链: OV-2/OV-5b → DIV-1 → DIV-2 → DIV-3
3. 约束传播链: StdV-1 → OV-6a → SV-10a/SvcV-10a
4. 演进闭环链: SV-9 → PV-2 → CV-3/CV-5

路径完整性规则：
- 有 SV-4 → 必有 OV-5b 和 CV-1
- 有 DIV-3 → 必有 DIV-1 和 DIV-2
- 有 OV-1 → 必有 CV-1（R1约束）
- 有 SV-10a → 必有 StdV-1 和 OV-6a
```

---

## 10. R1~R5 硬约束（需代码化）

| 约束 | 说明 |
|------|------|
| R1 | OV-1 必须有 CV-1 |
| R2 | 有 SV-4 必须有 OV-5b |
| R3 | DIV-3 必须有 DIV-1 和 DIV-2 |
| R4 | ... |
| R5 | ... |

*（需从 VIEW-RELATIONS-FULL-MAP.md 提取完整定义）*