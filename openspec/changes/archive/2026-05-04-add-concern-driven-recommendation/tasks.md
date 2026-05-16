## 1. 扩充 17 个数据组模板 keywords

- [x] 1.1 扩充 01-performer: 添加 管理员/运维/DevOps/admin/operator
- [x] 1.2 扩充 02-activity: 添加 认证流程/审批/审计跟踪/audit/workflow
- [x] 1.3 扩充 03-capability: 添加 战略/规划/roadmap/成熟度/maturity
- [x] 1.4 扩充 04-resource: 添加 令牌/凭证/密钥/证书/token/credential
- [x] 1.5 扩充 05-guidance: 添加 NIST/GDPR/等保/ISO27001/SOC2/compliance
- [x] 1.6 扩充 06-measure: 添加 SLA/KPI/延迟/吞吐量/latency/throughput
- [x] 1.7 扩充 07-location: 添加 云/机房/区域/cloud/region/zone
- [x] 1.8 扩充 08-services: 添加 SSO/MFA/OAuth/LDAP/认证/授权/auth
- [x] 1.9 扩充 09-project: 添加 sprint/release/deploy/交付/迭代
- [x] 1.10 扩充 10-rules: 添加 访问控制/RBAC/ABAC/ACL/防火墙/firewall
- [x] 1.11 扩充 11-resource-flow: 添加 认证流/数据交换/消息队列/ETL/API网关
- [x] 1.12 扩充 12-pedigree: 添加 数据血缘/溯源/可信/trust/auditability
- [x] 1.13 扩充 13-information-pedigree: 添加 数据治理/governance/衍生/aggregate
- [x] 1.14 扩充 14-org-structure: 添加 RBAC/权限/职责分离/separation of duties
- [x] 1.15 扩充 15-reification: 添加 抽象层/具体化/泛化/specialization
- [x] 1.16 扩充 16-information-data: 添加 schema/元数据/metadata/字段映射/ER图

## 2. 创建关切模板库

- [x] 2.1 创建 `dm2-reference/concerns.yaml`，包含 8 个初始关切模板（身份认证、网络安全、数据安全、系统集成、能力规划、威胁检测、组织治理、项目管理）
- [x] 2.2 新增 `dm2 concern list --json` CLI 子命令

## 3. 更新 dm2-propose-workflow SKILL.md

- [x] 3.1 在 analyze 步骤后增加"关切匹配与选择"步骤：加载 concerns.yaml → 计算匹配度 → 呈现候选 → Human 选择
- [x] 3.2 更新视图推荐逻辑：用 Human 选择的关切替代原始 15+ 候选视图的"全量推荐"
- [x] 3.3 将未选中的视图标记为"附加候选"在 proposal.md 中单独列出

## 4. 验证

- [x] 4.1 `dm2 analyze -d "身份认证系统 MFA SSO" --json` 至少 3 个数据组非零激活
- [x] 4.2 `dm2 concern list --json` 返回 8 个关切模板
- [x] 4.3 `dm2 concern list --json --query auth` 返回匹配的关切
- [x] 4.4 `/dm2:propose` 全流程验证：cynefin → analyze → 关切匹配 → Human 选择 → 聚焦视图
- [x] 4.5 聚焦后的视图集 ≤ 12 个（对比当前 15+）
