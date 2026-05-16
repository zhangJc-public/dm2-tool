## Context

`views.yaml` 是 dm2-tool 的单一数据源，定义了 52 个 DoDAF 视图的元数据。当前 schema 仅有 9 个字段（id, name, viewpoint, groups, description, priority, dependencies, required_data, downstream），缺乏标准定义的输出形式、内容结构和模型分类。InstructionBuilder 依赖硬编码的 VIEW_RULES 字典（仅覆盖 8 个视图）和通用模板。

DoDAF V2.02 标准（dodaf_v2-02_web.pdf + Vol. 2）为每个视图定义了：

- **Standard Name**（正式英文名，通常含形式暗示如 "Matrix"/"Tree"/"Chart"）
- **Model Category**（Table 1.2-2: Structural / Behavioral / Tree / Mapping / Tabular / Pictorial / Timeline / Ontology）
- **Purpose**（视图要回答什么问题、用于什么决策场景）
- **Content Elements**（视图中应包含的关键要素）

## Goals / Non-Goals

**Goals:**
- 为 views.yaml 中 52 个视图添加标准驱动的元数据字段
- InstructionBuilder 从元数据动态生成 rules、sections、template，消除硬编码 VIEW_RULES
- 视图加载时自动校验元数据合法性
- 完全向后兼容，不破坏现有 API

**Non-Goals:**
- 不改变 views.yaml 的现有字段名或值
- 不改变 knowledge API 的 JSON 结构（只在已有字段旁新增字段）
- 不引入新的依赖库
- 不删除现有的硬编码 VIEW_RULES（保留为 fallback）

## Decisions

### 1. 新增字段 Schema

在 views.yaml 每个 view 下新增 6 个字段：

| Field | Type | Required | Source | Validation |
|-------|------|----------|--------|------------|
| `standard_name` | str | yes | DoDAF Table 1.2-1 | non-empty |
| `model_category` | str | yes | DoDAF Table 1.2-2 | enum: Structural/Behavioral/Tree/Mapping/Tabular/Pictorial/Timeline/Ontology |
| `representation` | str | yes | derived from standard_name + model_category | enum: node-link/tree/org-chart/flowchart/state-diagram/sequence-diagram/er-diagram/pictorial/gantt/table/text |
| `purpose` | str | yes | derived from standard + architect experience | non-empty, multi-line |
| `sections` | list[str] | yes | derived from purpose + required_fields | non-empty list, 2-6 items |
| `required_fields` | list[str] | yes | derived from standard content elements | non-empty list |

### 2. representation → mermaid_type 映射

存于代码层而非 YAML 层，因为 `representation` 是标准语义（人可读），`mermaid_type` 是技术实现细节：

| representation | mermaid_type | Mermaid Syntax |
|----------------|-------------|----------------|
| node-link | graph | `graph LR` / `graph TD` |
| tree | graph | `graph TD` + subgraphs |
| org-chart | graph | `graph TD` |
| flowchart | flowchart | `flowchart TD` |
| state-diagram | stateDiagram | `stateDiagram-v2` |
| sequence-diagram | sequenceDiagram | `sequenceDiagram` |
| er-diagram | erDiagram | `erDiagram` |
| pictorial | graph | `graph LR` (loose) |
| gantt | gantt | `gantt` |
| table | None | Markdown `\|...\|` table |
| text | None | Structured markdown |

### 3. InstructionBuilder 重构策略

```
build_view_instructions(view_id, description)
│
├─ 1. knowledge.get_view(view_id) → ViewResult (含新字段)
│
├─ 2. 生成 rules:
│   ├─ representation 规则: "以 {representation} 形式呈现"
│   ├─ model_category 规则: "属于 {model_category} 类模型"
│   ├─ required_fields 规则: 每个 field 一条 "必须包含 {field}"
│   └─ 依赖视图规则: "必须与 {dep} 保持一致"
│
├─ 3. 生成 template:
│   ├─ sections: 从 views.yaml sections 字段直接读取
│   ├─ mermaid block: 仅当 mermaid_type is not None 时插入
│   │   └─ type 由 representation 映射
│   └─ required_fields: 从 views.yaml 读取
│
└─ 4. Fallback: 如果 ViewResult 无新字段（老版本数据）
    → 使用原 VIEW_RULES 硬编码 + 通用 template
```

### 4. 校验逻辑

在 indexer.py 的 `_load_views()` 中增加校验函数 `_validate_view(view)`：

```python
VALID_REPRESENTATIONS = {...}  # 11 values
VALID_CATEGORIES = {...}       # 8 values

def _validate_view(view: dict) -> list[str]:
    errors = []
    # 1. standard_name 非空
    # 2. model_category 在枚举值中
    # 3. representation 在枚举值中
    # 4. sections 非空列表
    # 5. required_fields 非空列表
    # 6. 逻辑一致性: table/text → sections 不应含 "Mermaid 图表"
    return errors
```

校验仅在首次加载时运行一次，结果缓存。错误级别为 WARNING（不阻止加载），方便渐进增强。

### 5. 向后兼容

- indexer.py 中解析新字段使用 `.get("field", default)`，缺失时用空值
- ViewTemplate / ViewResult 新字段有默认值
- InstructionBuilder 检测新字段存在性，有则走新逻辑，无则回退旧逻辑
- `knowledge view` 的 `--json` 输出仅追加新字段，不改变现有字段结构

## Risks / Trade-offs

- [Risk] 52 个视图的 sections/required_fields 可能有遗漏或不精确 → 每视点选 1-2 个代表性视图做人工回查
- [Risk] representation 分类与某些视图的边界模糊 → 已在 explore 阶段识别 6 个疑惑点并确认
- [Trade-off] 字段增加使 views.yaml 文件大小翻倍 → 可读性和可维护性更优先
