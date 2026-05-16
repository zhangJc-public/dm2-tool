## Why

当前 17 组数据组激活检测的信号太弱——关键词覆盖不足导致典型系统描述（如"身份认证系统，MFA+SSO"）只激活 1 个数据组，产生 15 个无聚焦的候选视图。需要在激活信号之上增加一层"关切（Concern）模板"——每个关切定义了"这类架构工作通常激活哪些数据组、需要哪些核心视图"的模式。关切匹配由 AI Agent 执行，Human 选择/补充关切，形成 Human+Agent 编组的协同推荐模式。

## What Changes

- **扩充 17 个数据组模板的 keywords** — 添加领域术语（认证/授权/加密/网络/防火墙/SSO/MFA/NIST/GDPR 等），提高激活信号区分度
- **新增 `dm2-reference/concerns.yaml`** — 关切模板库，每个关切定义 expected_groups（预期激活的数据组）、core_views（核心视图集合）、keywords（关切关键词），作为领域参考数据
- **新增 `dm2 concern list --json`** — CLI 子命令，输出关切模板列表供 AI Agent 查询和匹配
- **更新 `dm2-propose-workflow` SKILL.md** — 在 analyze 之后增加"关切匹配与选择"步骤：Agent 比对激活向量与关切模板 → 呈现候选关切 → Human 选择/补充 → 聚焦视图集

## Capabilities

### New Capabilities
- `concern-template-library`: 关切模板库（concerns.yaml + 17 组模板 keywords 扩充），定义架构关切模式——预期数据组激活模式、核心视图集、领域关键词

### Modified Capabilities
- `dm2-propose-workflow`: /dm2:propose 工作流增加关切匹配与 Human 选择步骤，从 15+ 候选视图聚焦到 5-10 个关切视图
- `dm2-data-group-activation`: 17 个模板的 keywords 扩充（添加领域术语，提高激活区分度）

## Impact

- `dm2-reference/concerns.yaml` — 新文件（关切模板库）
- `dm2-reference/core/groups/*/*-Template.md` — 17 个模板 keywords 扩充
- `src/dm2/cli/main.py` — 新增 `dm2 concern list` 子命令
- `.claude/skills/dm2-propose-workflow/SKILL.md` — 增加关切匹配步骤
