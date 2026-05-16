## 1. ViewManager 状态追踪

- [ ] 1.1 创建 `src/dm2/core/views/__init__.py` 和 `manager.py`
- [ ] 1.2 实现 `ViewStatus` 枚举和 `ViewInfo` dataclass
- [ ] 1.3 实现 `ViewManager` 类（load/save state, update_status, list_views, get_progress）
- [ ] 1.4 更新 `dm2 status` 命令，集成 view 状态输出

## 2. Claude Code 技能文件

- [ ] 2.1 创建 `templates/init/.claude/skills/dm2-explore/SKILL.md`（架构探索工作流）
- [ ] 2.2 创建 `templates/init/.claude/skills/dm2-generate/SKILL.md`（视图生成工作流）
- [ ] 2.3 创建 `templates/init/.claude/skills/dm2-pipeline/SKILL.md`（Pipeline 工作流）

## 3. Claude Code 命令文件

- [ ] 3.1 创建 `templates/init/.claude/commands/dm2/explore.md`
- [ ] 3.2 创建 `templates/init/.claude/commands/dm2/generate.md`
- [ ] 3.3 创建 `templates/init/.claude/commands/dm2/pipeline.md`
- [ ] 3.4 创建 `templates/init/.claude/commands/dm2/status.md`

## 4. dm2 init 集成

- [ ] 4.1 更新 `dm2 init` 命令，复制 `.claude/` 模板到新项目
- [ ] 4.2 处理已有 `.claude/` 的合并逻辑（不覆盖已有文件）

## 5. dm2 setup-claude 命令

- [ ] 5.1 在 CLI 中新增 `setup-claude` 命令
- [ ] 5.2 实现检测 dm2 项目根目录、复制模板、冲突提示

## 6. 文档更新

- [ ] 6.1 更新 `CLAUDE.md`，添加 dm2 skills/commands 索引和 workflow 说明
- [ ] 6.2 更新 `templates/init/CLAUDE.md` 项目模板（如果有的话）
