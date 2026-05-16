## Context

dm2 的 CLI 已有 15 个命令，覆盖了 Knowledge、Analysis、View、Pipeline、Change、Project 六个领域对象的大部分操作。但对照 openspec 的 CLI 设计模式（每个领域对象有完整的 list/show/status/validate 原语），View 和 Analysis 两个领域存在缺口。此外，reasoning 模块的 `ConsistencyChecker` 已有 4 条检查规则但没有 CLI 暴露。

AI Agent 在真实工程中需要：
- 跨 session 记住分析上下文（当前的分析结果只输出到 stdout）
- 查询已生成视图的状态（当前 view 是 fire-and-forget）
- 验证生成视图的一致性（当前 reasoning 模块只能在代码中调用）

## Goals / Non-Goals

**Goals:**
- ViewManager 追踪视图生命周期状态，持久化到 `.dm2/view-state.yaml`
- `dm2 view list` 列出项目中的视图及状态
- `dm2 validate <view>` 调用 ConsistencyChecker 并输出结构化报告
- `cynefin`/`analyze` 结果自动持久化到 `.dm2/analysis-state.yaml`
- `dm2 status` 输出中包含 view 进度统计

**Non-Goals:**
- 不创建"工作流"命令（explore/generate/pipeline 等是 skill 层的事）
- 不修改现有 CLI 命令的签名（只增加新命令，不破坏已有接口）
- 不实现自动修复（validate 只检查，不修改视图内容）

## Decisions

### Decision 1: ViewManager 遵循 ChangeManager 模式

`ChangeManager` 已有成熟的设计：dataclass + Enum + YAML 持久化 + CRUD API。ViewManager 采用相同模式，确保代码风格一致：

```python
class ViewStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    GENERATED = "generated"
    VERIFIED = "verified"

class ViewManager:
    def __init__(self, project_root)
    def update_status(view_id, status)
    def list_views(status_filter=None) -> list[ViewInfo]
    def get_progress() -> dict  # {pending: N, ..., verified: N}
    def _state_file() -> Path   # .dm2/view-state.yaml
```

**Alternative**: 把 view state 并入 ChangeManager → 拒绝，因为 view 状态与 change 生命周期独立。一个 change 可以包含多个 view，view 也可以独立于 change 存在。

### Decision 2: `dm2 view` 作为新子命令组

遵循 `dm2 knowledge` 和 `dm2 change` 的模式，创建 `dm2 view` 子命令组：

```
dm2 view list              # 列出所有视图及状态
dm2 view show <view_id>    # 显示单个视图详情（后续扩展）
```

注册方式与 knowledge/change 一致：`register_view_commands(app)` → `app.add_typer(view_app, name="view")`

### Decision 3: `dm2 validate` 作为顶级命令

`dm2 validate <view_id>` 调用 `ConsistencyChecker.check_views()` 对指定视图运行一致性检查。支持 `--all` 标志检查所有已生成视图。

输出格式：
- 人类可读：Markdown 表格，按 severity 分组
- `--json`：结构化 `{"view_id": ..., "issues": [...]}` 

### Decision 4: 分析结果持久化为副作用

`dm2 cynefin --json` 和 `dm2 analyze --json` 在输出 JSON 到 stdout 的同时，自动将结果写入 `.dm2/analysis-state.yaml`。不需要新的 CLI 标志，作为静默副作用。

读取分析状态：`dm2 status --json` 的返回中包含 `analysis` 字段（最近一次分析结果摘要）。

## Risks / Trade-offs

- [Risk] `.dm2/` 目录下的状态文件增多 → 目前只有 2 个新文件（view-state.yaml, analysis-state.yaml），可接受
- [Risk] ConsistencyChecker 的检查规则是基于内容模式匹配的，可能产生 false positive → severity 用 INFO/WARNING/ERROR 三级区分，false positive 最多是 INFO
- [Trade-off] 分析结果持久化是静默副作用，用户可能不知道文件被写入 → 首次写入时输出提示，后续静默覆盖
