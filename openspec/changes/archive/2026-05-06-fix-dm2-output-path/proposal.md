## Why

dm2-tool 的 AI Agent 工作流在生成视图、分析和报告时，输出路径存在系统性错位。`instructions.py` 规定视图写入 `output/<View-ID>.md`，但 AI agent 实际行为（用户实测已验证）是将所有产物写入 `dm2-changes/<name>/` 根目录。同时 `dm2 init` 创建了两个无效目录 `output/` 和 `.dm2/steps/`，且验证命令 `dm2 validate` 硬编码读取 `output/`。变更归档时视图与规划文件散落两处，无法统一迁移。需要将输出路径体系对齐到 agent 的自然行为以消除脱节。

## What Changes

- **`instructions.py`**: `build_view_instructions()` 的 `output_path` 不再硬编码为 `output/<View-ID>.md`，改为基于 `dm2-changes/<name>/views/<View-ID>.<ext>` 的动态路径
- **`main.py:dm2 init`**: 不再创建 `output/` 和 `.dm2/steps/` 两个无人使用的目录
- **`main.py:validate`**: 不再硬编码 `Path.cwd() / "output"` 定位视图文件，改为通过 `--change` 参数从 `dm2-changes/<name>/views/` 读取
- **新增 CLI 命令**: `dm2 view register <view-id> --change <name> --path <path>` — AI agent 生成视图后调用，更新 `.dm2/view-state.yaml`
- **SKILL.md 模板更新 (ff, continue, verify)**: 明确指引 agent 将分析/视图/报告产物写入 `dm2-changes/<name>/` 子目录下（analysis/、views/、reports/），不再引用不存在的 `output/`
- **pipeline 模式**: `dm2 run --agent` 增加 `--change <name>` 参数，使其产出融入 change 体系而非独立路径

## Capabilities

### New Capabilities
- `view-register`: AI agent 在生成视图后调用 CLI 命令注册视图文件路径和格式到 view-state.yaml，实现生成结果与项目状态同步

### Modified Capabilities
<!-- No existing specs modified -->

## Impact

- **`src/dm2/core/agent/instructions.py`**: `build_view_instructions()` 签名变更，需增加 `change_name` 参数
- **`src/dm2/cli/main.py`**: `init` 命令删除两行目录创建；`validate` 命令重写文件路径解析逻辑
- **`src/dm2/cli/commands/view.py`**: 新增 `register` 子命令
- **`src/dm2/core/templates/workflows/ff.py`**: SKILL.md 模板中 `output_path` 引用和产物位置指引更新
- **`src/dm2/core/templates/workflows/continue_workflow.py`**: 补充 agent 输出路径指引
- **`src/dm2/core/templates/workflows/verify.py`**: 明确验证报告保存位置
- **`src/dm2/core/templates/workflows/propose.py`**: 增加分析结果持久化指引
- **`.claude/skills/dm2-*/SKILL.md`**: 所有工作流技能文件重新生成
- **`dm2-change` 与 `dm2-agent-run` 模式统一**: pipeline 6 步骤增加 change 感知
