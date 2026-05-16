## 1. Fix --desc parameter handling

- [x] 1.1 Remove unconditional `--desc` check at lines 957-960 in `src/dm2/cli/main.py`
- [x] 1.2 After type resolution block (line ~991), add check: if `is_step` and `not description`, return `MISSING_ARG` error
- [x] 1.3 For view path (`!is_step`), inject guidance prompt into `description` when empty: `"⚠️ 未提供 --desc 参数。建议使用 AskUserQuestion 工具与用户互动，提供几个讨论方向或预设选项，共同明确视图生成目标。"`

## 2. Verify

- [x] 2.1 Test `dm2 instructions StdV-1 --json` without `--desc` → success with guidance prompt in project_description
- [x] 2.2 Test `dm2 instructions StdV-1 -d "test desc" --json` with `--desc` → normal behavior unchanged
- [x] 2.3 Test `dm2 instructions step1-intent-scope --json` without `--desc` → MISSING_ARG error
- [x] 2.4 Test `dm2 instructions step1-intent-scope -d "test" --json` with `--desc` → normal behavior
