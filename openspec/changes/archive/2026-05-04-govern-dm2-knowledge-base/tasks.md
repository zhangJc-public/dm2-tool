## 1. 清理冗余和垃圾

- [x] 1.1 删除 `详细分析/视图全集/images/` 目录（7 MB PNG 截图，102 个文件）
- [x] 1.2 删除 `.DS_Store` 文件
- [x] 1.3 合并重复文件 `00-基础模式/Common-Patterns.md` 和 `CommonPatterns.md`（保留其一）

## 2. 创建三层目录结构

- [x] 2.1 创建 `core/`、`reference/`、`examples/` 顶层目录
- [x] 2.2 移动 `_dm2_v202_extract.json` 和 `views.yaml` 到 `core/`
- [x] 2.3 移动 17 数据组目录到 `core/groups/`（重命名去除数字前缀：`00-基础模式` → `00-foundation` 等）
- [x] 2.4 移动 `总览文档/`、`详细分析/`、`研究/` 到 `reference/overview/`、`reference/analysis/`、`reference/research/`
- [x] 2.5 将项目示例数据从各组目录中提取到 `examples/`：
  - `01-Performer/Organization/Organization-Type/` → `examples/performer-instances/`
  - `01-Performer/System/System-Individual/` → `examples/system-instances/`
  - `05-Guidance/Standard/*.md`（具体法律） → `examples/guidance-standards/`
  - `05-Guidance/Rule/*.md`（具体法律） → `examples/guidance-rules/`
- [x] 2.6 移动 2 张参考图（DM2-WG-Page*.png）到 `reference/`

## 3. 更新代码引用

- [x] 3.1 更新 `src/dm2/kernel/indexer.py`：修改 `REFERENCE_PATH` 和文件加载逻辑，添加新旧结构自动检测
- [x] 3.2 更新 `src/dm2/cli/main.py`：修改 `REFERENCE_PATH` 指向 `core/`
- [x] 3.3 全局搜索所有引用 `dm2-reference/` 子路径的代码，更新为 `core/` 路径

## 4. 打包配置

- [x] 4.1 更新 `pyproject.toml`：`[tool.setuptools.package-data]` 只包含 `dm2-reference/core/**`
- [x] 4.2 创建 `MANIFEST.in`：精确控制 sdist 包含内容

## 5. 验证

- [x] 5.1 运行 `dm2 status` 验证知识库加载正常（术语数、概念数、视图数不变）
- [x] 5.2 运行 `dm2 knowledge search` 验证术语检索功能（dm2 knowledge 命令在 redesign-dm2-framework 中实现，底层 indexer.search_terms 已验证可用）
- [x] 5.3 运行 `dm2 generate --list` 验证 52 视图可用
- [x] 5.4 验证 `pip install -e .` 后 package 大小 < 2 MB（core/ = 296 KB）
- [x] 5.5 验证旧目录结构下 Indexer 仍可工作（fallback 路径）
