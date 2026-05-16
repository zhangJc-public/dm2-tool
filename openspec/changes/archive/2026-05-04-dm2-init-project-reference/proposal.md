## Why

`dm2 init` 生成的项目缺少参考知识库文件（views.yaml、术语、数据组模板），导致项目非自包含。AI Agent 在项目中无法直接读取视图定义，必须依赖 CLI 命令查询。此外，用户无法按项目自定义视图依赖。

## What Changes

- `dm2 init`: 复制 `dm2-reference/core/`（views.yaml、术语、数据组模板）和 `group-to-views.yaml` 到 `.dm2/reference/`
- `paths.py`: `get_reference_path()` 优先检查项目本地 `.dm2/reference/`，回退到包内置路径
- `main.py`: `instructions` 命令改用 `get_reference_path()` 替代硬编码路径
- README.md: 更新项目结构图，增加 `.dm2/reference/` 说明
- CLAUDE.md: 更新项目模式说明，补充参考知识库本地化信息

## Capabilities

### Modified Capabilities

- `dm2-project-init`: `dm2 init` 现在生成包含本地参考知识库的自包含项目
- `dm2-reference-path-resolver`: `get_reference_path()` 新增项目本地优先策略

## Impact

- `src/dm2/cli/main.py`: init 命令新增 25 行参考文件复制逻辑；instructions 命令路径解析简化（4 行 → 2 行）
- `src/dm2/utils/paths.py`: `get_reference_path()` 重构为本地优先（+8 行）
- README.md: 项目结构图增加 `.dm2/reference/`
- CLAUDE.md: 项目模式部分补充参考知识库说明
