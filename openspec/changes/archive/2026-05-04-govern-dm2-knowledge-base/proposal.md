## Why

`dm2-reference/` 目录当前有 257 个文件、9.3 MB，其中 77%（7 MB）是 DoDAF PDF 截图，另外混杂了研究文档、项目示例数据、重复文件和 macOS 垃圾文件。直接作为 `package_data` 打包进 pip 包会导致：用户下载一个 10 MB 的包，但实际核心知识数据只有 ~700 KB。必须在打包前将核心知识数据与参考/研究内容分离。

## What Changes

- 将 `dm2-reference/` 重组为三层目录结构：`core/`（核心知识，打包）、`reference/`（参考资料，可选）、`examples/`（项目示例，不打包）
- 删除 7 MB PNG 截图（从 PDF 提取的视图示例图，AI 不需要）
- 删除 `.DS_Store` 等垃圾文件
- 合并重复文件：`Common-Patterns.md` / `CommonPatterns.md`
- 移除项目示例数据（具体防火墙型号、中国法律条文等硬编码实例）
- 更新 `pyproject.toml` 的 `package_data` 配置，只包含 core/ 目录
- **BREAKING**: `views.yaml` 和 `_dm2_v202_extract.json` 路径变更，需更新 `DM2KnowledgeIndexer` 的加载路径

## Capabilities

### New Capabilities

- `knowledge-base-structure`: 定义 dm2-reference 的标准目录结构和分层规范（core / reference / examples）

### Modified Capabilities

- `knowledge-api`: 更新 Knowledge API 中的文件加载路径以匹配新的目录结构

## Impact

- `dm2-reference/` — 目录结构重组，文件移动/删除
- `src/dm2/kernel/indexer.py` — 更新 `REFERENCE_PATH` 和文件加载逻辑
- `pyproject.toml` — 更新 `package-data` 配置
- `MANIFEST.in` — 新建，精确控制打包内容
