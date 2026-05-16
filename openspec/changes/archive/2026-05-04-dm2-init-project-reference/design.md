## Context

`dm2 init` 当前仅创建 config + 空目录 + Claude skills，参考数据（views.yaml、术语、模板）仅存在于包中。项目不自包含，AI Agent 需调用 CLI 获取视图信息。

## Goals / Non-Goals

**Goals:**
- `dm2 init` 生成自包含项目，含本地参考知识库副本
- `get_reference_path()` 项目本地优先，包内置回退
- 消除 `instructions` 命令中的硬编码 dm2-reference 路径

**Non-Goals:**
- 不修改参考数据的加载逻辑（indexer 已使用 `get_reference_path()`）
- 不修改 ArtifactGraph（已参数化 views_yaml_path）

## Decisions

### 决策 1：参考文件复制到 `.dm2/reference/`

**方案**: `dm2 init` 将 `dm2-reference/core/` 内容（views.yaml、_dm2_v202_extract.json、groups/）和 `dm2-reference/group-to-views.yaml` 复制到 `.dm2/reference/`。

**理由**: 与 `.dm2/reference/` 命名一致（区别于 `.dm2/steps/` 中间产物），AI Agent 和用户均可直接读取。

### 决策 2：本地优先路径解析

**方案**: `get_reference_path()` 先通过 `get_project_root()` 查找 `.dm2/reference/`，存在则返回；否则回退到包路径。

```python
def get_reference_path() -> Path:
    try:
        project_root = get_project_root()
        project_ref = project_root / ".dm2" / "reference"
        if project_ref.exists():
            return project_ref
    except Exception:
        pass
    # fallback to package path
    ...
```

**理由**: 项目本地副本存在即使用，保证向后兼容（无 `.dm2/reference/` 时行为不变）。

## Files Changed

| 文件 | 改动 |
|------|------|
| `src/dm2/utils/paths.py` | `get_reference_path()` 新增本地优先解析 |
| `src/dm2/cli/main.py` | init 新增参考文件复制；instructions 改用 get_reference_path() |
| `README.md` | 项目结构图增加 `.dm2/reference/` |
| `CLAUDE.md` | 项目模式补充参考知识库说明 |
