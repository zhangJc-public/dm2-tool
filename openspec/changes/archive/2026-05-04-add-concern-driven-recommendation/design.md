## Context

当前 17 组激活检测的关键词偏向通用概念词（"系统"、"数据"、"服务"），缺少领域术语。一个"身份认证系统 MFA+SSO"的描述只匹配到 "系统" 一个词，导致 01-performer 以 0.071 微弱激活，其他 16 组全为 0.0。15 个候选视图无聚焦。

需要两层改进：(1) 数据层——扩充 keywords 增加领域术语 (2) 结构层——新增关切模板库，AI Agent 用模板 + 激活数据 + 对话上下文，与 Human 协同选择聚焦的视图集。

## Goals / Non-Goals

**Goals:**
- 扩充 17 个数据组模板的 keywords（每组合 5-8 个领域术语 + 保持原有通用词）
- 新增 `dm2-reference/concerns.yaml`（8-12 个关切模板）
- 新增 `dm2 concern list --json` CLI 子命令
- 更新 `dm2-propose-workflow` SKILL.md 增加关切匹配步骤

**Non-Goals:**
- 不改动 Python 端的匹配逻辑（匹配完全在 AI Agent 侧执行）
- 不改动 `dm2 analyze` 的输出结构
- 不引入机器学习或 embedding
- Concern 模板不做"自动推导"——匹配逻辑在 SKILL.md 中

## Decisions

**决定 1: 关切模板放在 dm2-reference，由 SKILL.md 加载**

concerns.yaml 与 group-to-views.yaml 并列，作为 DM2 领域参考数据。`dm2 concern list --json` 提供查询接口。AI Agent 通过 CLI 或直接读文件两种方式获取。

**决定 2: 关切匹配算法在 AI Agent 侧**

```
concern_score = α × group_activation_overlap + β × keyword_match
  where:
    group_activation_overlap = |active_groups ∩ concern.expected_groups| / |concern.expected_groups|
    keyword_match = |desc_words ∩ concern.keywords| / |concern.keywords|
    α = 0.6 (数据组激活权重), β = 0.4 (关键词权重)
```

这个算法在 SKILL.md 中描述，不编码到 Python。权重可调。

**决定 3: keywords 扩充策略**

每个组在保持原有通用词的基础上，增加领域术语：

```
01-performer +: 管理员, 运维, DevOps
02-activity  +: 认证流程, 审批, 审计跟踪
04-resource  +: 令牌, 凭证, 密钥, 证书
05-guidance  +: NIST, GDPR, 等保, ISO27001, SOC2
08-services  +: SSO, MFA, OAuth, LDAP, 认证, 授权
10-rules     +: 访问控制, RBAC, ABAC, ACL, 防火墙规则
11-resource-flow +: 认证流, 数据交换, 消息队列, ETL
```

**决定 4: 关切模板的初始集合**

从 ZeroTrust PDF 分析中提取的 8 个模式 + 常见架构关切：

| 关切 | 预期数据组 | 核心视图 |
|------|-----------|---------|
| 身份认证与访问控制 | 05, 08, 10, 11 | OV-1, OV-2, SV-1, StdV-1 |
| 网络安全与边界防护 | 07, 10, 11 | OV-1, OV-2, SV-2, SV-6 |
| 数据安全与合规 | 04, 05, 10, 16 | DIV-1, DIV-2, DIV-3, StdV-1 |
| 系统集成与互操作 | 01, 08, 11 | SV-1, SV-4, SvcV-1, SvcV-3 |
| 能力规划与演进 | 03, 06, 09 | CV-1, CV-3, CV-5, PV-2 |
| 威胁检测与响应 | 02, 06, 07, 10 | OV-1, OV-6a, SV-7, SV-10a |
| 组织与治理 | 01, 03, 14 | OV-4, PV-1, CV-5 |
| 项目管理与交付 | 06, 09, 12 | PV-1, PV-2, PV-3 |

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| keywords 扩充后通用词匹配过多导致假阳性 | 领域词增加量控制在 5-8 个/组，保持信号区分度 |
| 关切模板不够覆盖用户场景 | 模板外部 YAML，用户可自行扩充；AI Agent 可从对话中动态构造新关切 |
| 匹配算法权重 (`α=0.6 β=0.4`) 未经调优 | 初始值从直觉出发；在 SKILL.md 中参数化，迭代调整不需要改代码 |
