## 1. 创建 explore 工作流模板

- [x] 1.1 创建 `workflows/explore.py` — SkillTemplate + CommandTemplate + get_workflow_template()
- [x] 1.2 在 `workflows/__init__.py` 中 import explore 并注册到 `_all_workflows`

## 2. 部署与验证

- [x] 2.1 `dm2 init` 测试项目，确认 `.claude/skills/dm2-explore-workflow/SKILL.md` 已生成
- [x] 2.2 确认 `.claude/commands/dm2/explore.md` 已生成
- [x] 2.3 确认 Skill 指令中仅引用只读命令（knowledge *），无 generate/change/run/validate
- [x] 2.4 确认所有 8 个工作流均正常注册（WORKFLOWS 列表长度 = 8）
