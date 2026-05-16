## 1. `instructions.py` — output_path 动态化

- [x] 1.1 `build_view_instructions()` 签名增加 `change_name: str = ""` 参数
- [x] 1.2 当 `change_name` 非空时，`output_path` 构造为 `dm2-changes/{change_name}/views/{view_id}.{ext}`（ext 默认 md）
- [x] 1.3 当 `change_name` 为空时，保持当前 `output/{view_id}.md` 作为降级行为（兼容已有调用）

## 2. `ViewManager` — 增加 output_path 追踪

- [x] 2.1 `ViewInfo` dataclass 增加 `output_path: str = ""` 和 `change_name: str = ""` 字段
- [x] 2.2 `register_view()` 增加 `output_path` 和 `change_name` 参数，写入 view-state.yaml
- [x] 2.3 `view-state.yaml` 的持久化格式增加两个新字段
- [x] 2.4 确保 `list_views()` 和 `get_view()` 能正确读取新字段

## 3. CLI: 新增 `dm2 view register` 命令

- [x] 3.1 `view.py` 中增加 `register` 子命令，接受 `view_id`、`--change`、`--path` 参数
- [x] 3.2 内部调用 `ViewManager.register_view()` + `ViewManager.update_status()`
- [x] 3.3 输出 JSON 供 AI Agent 消费（含 view_id、change、output_path）
- [x] 3.4 缺少 `--change` 时返回 `MISSING_ARG` 错误

## 4. `main.py:init` — 废止 `output/` + `.dm2/steps/`

- [x] 4.1 `init` 命令的 `subdir` 列表中删除 `"output"` 和 `".dm2/steps"`
- [x] 4.2 只保留 `["dm2-changes", "dm2-archive"]`
- [x] 4.3 `dm2 status` 命令中的相关输出行同步更新（如已提到这两个目录）

## 5. `main.py:validate` — 改为通过 `--change` 定位视图

- [x] 5.1 `validate` 命令增加 `--change <name>` 参数
- [x] 5.2 视图文件读取逻辑：不再硬编码 `Path.cwd() / "output"`，改为 `get_project_root() / "dm2-changes" / change / "views"`
- [x] 5.3 未提供 `--change` 时回退到 `output/`（兼容），但报 warning 提示"建议使用 --change"

## 6. SKILL.md 工作流模板更新 (ff)

- [x] 6.1 `ff.py` 模板中的步骤 5c：从 "Write to output_path from instructions" 改为写入 `dm2-changes/<name>/views/<View-ID>.<ext>`
- [x] 6.2 增加步骤：生成后调用 `dm2 view register <View-ID> --change <name> --path <path>`
- [x] 6.3 摘要表格中的 Output Path 列更新
- [x] 6.4 格式指引改为 ".md or .html, whichever renders best"

## 7. SKILL.md 工作流模板更新 (continue)

- [x] 7.1 `continue_workflow.py` 模板：view 生成步骤增加明确保存路径指引
- [x] 7.2 增加注册步骤：生成后调用 `dm2 view register`

## 8. SKILL.md 工作流模板更新 (verify)

- [x] 8.1 `verify.py` 模板：明确报告保存到 `dm2-changes/<name>/reports/verify.md`
- [x] 8.2 读取视图路径指引：改为从 change 的 views 目录读取
- [x] 8.3 如果在步骤中读取已有视图文件，更新文件位置提示

## 9. SKILL.md 工作流模板更新 (propose)

- [x] 9.1 `propose.py` 模板：cnyefin 和 6W 分析结果写入 `dm2-changes/<name>/analysis/`
- [x] 9.2 确保 planner artifacts (proposal/design/tasks) 路径不变

## 10. 技能文件重新生成

- [x] 10.1 运行 `dm2 init` 或模板生成器，重新生成 `.claude/skills/dm2-*/SKILL.md`
- [x] 10.2 验证生成的 SKILL.md 中不再引用 `output/` 或 `output_path`
- [x] 10.3 验证 commands/dm2/*.md 描述是否准确

## 11. pipeline 模式 — 增加 `--change` 支持（可选，后做）

- [ ] 11.1 `dm2 run --agent` 增加 `--change <name>` 参数
- [ ] 11.2 提供 `--change` 时，6 步产出写入 `dm2-changes/<name>/analysis/step-*.md`
- [ ] 11.3 pipeline 状态文件也放 change 目录：`dm2-changes/<name>/.pipeline-state.yaml`
- [ ] 11.4 未提供时保持当前 `.dm2/steps/` 行为不变

## 12. 工具适配器 (adapter) — 输出路径格式更新

- [x] 12.1 `ToolAdapter` 协议中检查是否需要增加输出路径相关方法 — 不需要，路径由 instructions.py 管理
- [x] 12.2 `ClaudeCodeAdapter` 适配 — 不需要修改

## 13. 测试

- [x] 13.1 验证 `dm2 view register` 命令：注册后 view-state.yaml 正确写入 output_path 字段
- [x] 13.2 验证 `instructions.py` 在有 `--change` 时的 output_path 正确
- [x] 13.3 验证 `dm2 validate --change <name>` 能正确读取 views 目录
- [x] 13.4 验证 `dm2 init` 不再创建 `output/` 和 `.dm2/steps/`
- [x] 13.5 回归：已有的 `output/` 使用场景不会崩溃 — 降级路径保留
