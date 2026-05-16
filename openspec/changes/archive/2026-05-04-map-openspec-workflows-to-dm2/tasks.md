## 1. Skill 文件：new / continue / ff

- [x] 1.1 创建 `.claude/skills/dm2-new-workflow/SKILL.md`（遵循 openspec-new-change 结构）
- [x] 1.2 创建 `.claude/skills/dm2-continue-workflow/SKILL.md`（遵循 openspec-continue-change 结构）
- [x] 1.3 创建 `.claude/skills/dm2-ff-workflow/SKILL.md`（遵循 openspec-ff-change 结构）

## 2. Skill 文件：verify / bulk-archive / onboard

- [x] 2.1 创建 `.claude/skills/dm2-verify-workflow/SKILL.md`（遵循 openspec-verify-change 结构）
- [x] 2.2 创建 `.claude/skills/dm2-bulk-archive-workflow/SKILL.md`（遵循 openspec-bulk-archive-change 结构）
- [x] 2.3 创建 `.claude/skills/dm2-onboard-workflow/SKILL.md`（遵循 openspec-onboard 结构）

## 3. Command 文件

- [x] 3.1 创建 `.claude/commands/dm2/new.md`
- [x] 3.2 创建 `.claude/commands/dm2/continue.md`
- [x] 3.3 创建 `.claude/commands/dm2/ff.md`
- [x] 3.4 创建 `.claude/commands/dm2/verify.md`
- [x] 3.5 创建 `.claude/commands/dm2/bulk-archive.md`
- [x] 3.6 创建 `.claude/commands/dm2/onboard.md`

## 4. dm2 init 集成

- [x] 4.1 更新 `dm2 init` 模板，将 `.claude/skills/` 和 `.claude/commands/dm2/` 复制到新项目

## 5. 验证

- [x] 5.1 在测试项目 `md2_model/my-project` 中运行 `dm2 init`，验证 `.claude/` 正确生成
- [x] 5.2 通过 `/dm2:new` 斜杠命令手动触发一次工作流，验证流程正确
