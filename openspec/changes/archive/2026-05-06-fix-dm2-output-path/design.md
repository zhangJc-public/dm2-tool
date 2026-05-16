## Context

当前 dm2-tool 的输出路径存在三处错位：

1. **`instructions.py`** 规定视图输出到 `output/<View-ID>.md`，但实测中 AI agent 将所有产物写入 `dm2-changes/<name>/` 根目录。`output/` 目录实际无人使用。

2. **`dm2 init`** 创建 `output/` 和 `.dm2/steps/` 两个目录，但 `.dm2/steps/` 仅 pipeline 模式使用（此模式与 change 体系不连通），`output/` 全无用途。

3. **`dm2 validate`** 硬编码 `Path.cwd() / "output"` 读取视图文件（main.py:777），且 `ViewManager` 没有跟踪输出路径。归档时文件散落，无法迁移。

4. **SKILL.md 工作流模板** 中输出指引模糊或错误：ff 写 `output/<View-ID>.md`，continue 什么也没写，verify 的报告无保存位置。

5. **pipeline 模式** (`dm2 run --agent`) 不创建 change，产出塞进 `.dm2/steps/`，与主流 change 体系平行但无交集。

## Goals / Non-Goals

**Goals:**
- 将所有 AI agent 产出的视图、分析、报告统一对齐到 `dm2-changes/<name>/` 下
- 废止废弃目录 `output/` 和 `.dm2/steps/` 的创建
- AI agent 在生成视图后能同步状态到 `view-state.yaml`
- `dm2 validate` 能正确读取变更内的视图文件
- SKILL.md 模板给出准确的输出路径指引

**Non-Goals:**
- 不改变 `dm2 run --agent` 的 legacy 模式行为（仅对齐到 change 的路径体系）
- 不重写 `ViewManager` 整体架构（仅新增输出路径追踪）
- 不约束文件格式（.md / .html 均可，agent 和用户自行决定）

## Decisions

### D1: `output_path` 动态化，不再硬编码

当前 `instructions.py:build_view_instructions()` 直接返回 `output_path = f"output/{view_id}.md"`。

改为从 `--change` 参数或 `ChangeManager` 获取 change name，构造：

```
dm2-changes/{change_name}/views/{view_id}.{ext}
```

扩展名 `.ext` 由调用方传入或默认 `.md`。`build_view_instructions()` 签名增加 `change_name: str` 和 `format: str = "md"` 参数。

**备选**: 不加 `format` 参数，让 SKILL.md 指引 agent 使用任何格式，`output_path` 只用 `.md` 后缀作为默认值。agent 在写入时可改为 `.html`。

→ 选择备选。路径由工具决定，格式由 agent 和用户协商。

### D2: 废止 `output/` 和 `.dm2/steps/` 目录创建

`main.py:init` 中删除这两行：

```python
for subdir in ["dm2-changes", "dm2-archive", "output", ".dm2/steps"]:
```

→ 改为 `["dm2-changes", "dm2-archive"]`

### D3: 新增 `dm2 view register` CLI 命令

AI agent 在生成每个视图文件后，调用此命令同步状态。

```bash
dm2 view register OV-1 --change boundary-security --dm2-changes/boundary-security/views/OV-1.html
```

执行流程：
1. 调用 `ViewManager.register_view(view_id)` 注册该视图（如果尚未存在）
2. 调用 `ViewManager.update_status(view_id, ViewStatus.GENERATED)`
3. 在 view-state.yaml 中额外存储 `output_path` 和 `change_name`

`ViewInfo` 增加字段：`output_path: str`、`change_name: str`

**不增加** `ViewManager.register_view()` 对文件的校验（不检查文件是否存在，只记录状态）。

### D4: `dm2 validate` 改为通过 `--change` 查找视图

当前代码：

```python
output_dir = Path.cwd() / "output"
```

改为：

```python
root = get_project_root()
base = root / "dm2-changes" / change / "views" if change else root / "output"
```

同时 `validate` 命令增加 `--change <name>` 参数。如果未提供 `--change` 且无 `output/` 目录，报错提示 "请指定 --change 参数"。

### D5: SKILL.md 工作流模板更新

**ff.py / SKILL.md**:
- 步骤 5c：从 "Write to output_path" 改为 "Write to `dm2-changes/<change-name>/views/<View-ID>.<ext>`"
- 添加：生成后调用 `dm2 view register <View-ID> --change <name> --path <path>`
- 摘要输出中的 Output Path 列改为 `dm2-changes/<name>/views/<View-ID>.html`
- 格式指引：".md or .html, whichever renders the diagram effectively"

**continue.py / SKILL.md**:
- 添加保存位置指引：将生成的视图写入 `dm2-changes/<change-name>/views/<View-ID>.<ext>`
- 添加注册步骤

**verify.py / SKILL.md**:
- 报告保存位置：明确为 `dm2-changes/<name>/reports/verify.md`
- 读取视图位置：改为从 change 的 views 目录而非 output/

**propose.py / SKILL.md**:
- 添加：cynefin 和 6W 分析结果写入 `dm2-changes/<name>/analysis/` 下
- 现有的 planning artifacts (proposal/design/tasks) 路径不变

### D6: pipeline 模式增加 `--change` 支持

`dm2 run --agent` 增加 `--change <name>` 参数：
- 如果提供：6 步产出写入 `dm2-changes/<name>/analysis/step-*.md`
- 如果未提供：保持当前 `.dm2/steps/` 行为不变
- pipeline 状态文件也放在 change 目录下：`dm2-changes/<name>/.pipeline-state.yaml`

### D7: 不动的部分

- `ViewManager` 的 `view-list` 命令已存在，无需修改
- `dm2 change new` 已创建 views/ analysis/ delta-specs/ 子目录，无需修改
- `dm2 archive` 的归档逻辑（移动整个 change 目录）无需修改
- `dm2-archive/` 目录的创建由 `ChangeManager.archive()` 触发，init 中可保留或删除（不影响功能）

## Risks / Trade-offs

- **[风险] AI agent 仍可能绕开 `dm2 view register` 命令**: SKILL.md 中加入 guardrail 要求；如果 agent 不执行，view-state 仍可能不同步 → 不严重，view-state 是降级使用（仍然可以从 change 目录扫描文件）
- **[风险] pipeline --change 增加复杂性**: 如果用户从未使用 pipeline 模式，这部分投入无产出 → 可后做，非阻塞
- **[风险] 遗留项目兼容性**: 已有项目的 `output/` 目录不会自动清除 → 不影响，手动删除即可
- **[权衡] 不再统一约束文件格式**: .md 和 .html 混用意味着 view-state.yaml 需要记录格式信息 → `output_path` 字段已包含扩展名，自然解决
