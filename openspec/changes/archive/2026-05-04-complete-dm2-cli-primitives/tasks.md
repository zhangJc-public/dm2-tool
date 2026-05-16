## 1. ViewManager 核心实现

- [x] 1.1 创建 `src/dm2/core/views/__init__.py` 和 `manager.py`
- [x] 1.2 实现 `ViewStatus` 枚举（PENDING, IN_PROGRESS, GENERATED, VERIFIED）
- [x] 1.3 实现 `ViewInfo` dataclass（id, status, generated_at, verified_at）
- [x] 1.4 实现 `ViewManager` 类（load/save YAML, update_status, list_views, get_progress）

## 2. dm2 view 子命令组

- [x] 2.1 创建 `src/dm2/cli/commands/view.py`，实现 `view list` 子命令
- [x] 2.2 在 `main.py` 中注册 view 子命令组（`register_view_commands`）

## 3. dm2 validate 命令

- [x] 3.1 在 `main.py` 中新增 `validate` 顶级命令（调用 `ConsistencyChecker`）
- [x] 3.2 实现 `--all` 标志（校验所有已生成视图）和单视图校验
- [x] 3.3 校验通过时自动更新 ViewManager 状态为 `verified`

## 4. 分析结果持久化

- [x] 4.1 修改 `dm2 cynefin` 命令，静默写入 `.dm2/analysis-state.yaml`
- [x] 4.2 修改 `dm2 analyze` 命令，静默写入 `.dm2/analysis-state.yaml`
- [x] 4.3 修改 `dm2 status` 命令，输出中包含 `analysis` 字段

## 5. Pipeline 集成

- [x] 5.1 修改 `step6_documentation.py`，完成时通过 ViewManager 注册生成的视图

## 6. dm2 status 增强

- [x] 6.1 增强 `dm2 status` 命令，输出中包含 view 进度统计（pending/in_progress/generated/verified 计数）
