## Why

`views.yaml` 是 dm2-tool 驱动 AI Agent 生成 DoDAF 视图的核心元数据文件，当前仅包含视图的身份标识信息（id、name、viewpoint、dependencies），缺乏标准定义的输出形式（representation）、内容结构（sections）、模型分类（model_category）等关键元数据。这导致 InstructionBuilder 对 45 个视图使用同一套硬编码模板和规则，Agent 无法从元数据获知"这个视图该画成什么样的图、包含哪些章节、输出什么字段"。需要基于 DoDAF V2.02 标准对 52 个视图进行全面增强。

## What Changes

- **views.yaml 增强**：每个视图新增 6 个字段：`standard_name`、`model_category`、`representation`、`purpose`、`sections`、`required_fields`，全部从 DoDAF 标准文件（dodaf_v2-02_web.pdf + Vol. 2）中推导
- **view-representations.yaml**：保存 DoDAF 标准表达形式对照表（参考文件，已在 explore 阶段生成）
- **indexer.py ViewTemplate**：dataclass 新增对应字段，YAML 解析支持新字段
- **api.py ViewResult**：dataclass 新增对应字段，`get_view()` 输出包含新元数据
- **InstructionBuilder 重构**：`build_view_instructions()` 从 views.yaml 元数据动态生成 rules、sections、template，不再依赖硬编码 VIEW_RULES
- **逻辑校验**：views.yaml 加载时自动校验 `representation` 和 `model_category` 枚举值、`sections`/`required_fields` 非空、table/text 型视图不强制 Mermaid 图
- **cli/main.py knowledge view**：输出包含新字段
- 所有旧字段保持不变，向后兼容

## Capabilities

### New Capabilities

- `view-metadata-schema`: views.yaml 新增 `standard_name`、`model_category`、`representation`、`purpose`、`sections`、`required_fields` 字段，覆盖 52 个 DoDAF 视图，字段值从 DoDAF V2.02 标准推导，加载时自动校验合法性
- `metadata-driven-instructions`: InstructionBuilder 从 views.yaml 元数据动态生成规则和模板——`representation` 驱动图表类型规则，`sections` 驱动章节结构，`required_fields` 驱动内容校验，`model_category` 驱动分类提示——替换现有硬编码 VIEW_RULES

### Modified Capabilities

<!-- No existing dedicated specs to modify -->

## Impact

- `dm2-reference/core/views.yaml`：52 个视图全部增强（向后兼容，旧字段不变）
- `dm2-reference/view-representations.yaml`：新增参考文件（explore 阶段已创建）
- `src/dm2/kernel/indexer.py`：ViewTemplate dataclass + 解析逻辑
- `src/dm2/core/knowledge/api.py`：ViewResult dataclass + `get_view()` 透传
- `src/dm2/core/agent/instructions.py`：VIEW_RULES 硬编码变 fallback，元数据动态规则变为主要路径
- `src/dm2/cli/main.py`：`knowledge view` 输出新字段
- 不破坏现有 API 契约，所有旧代码字段名不变
