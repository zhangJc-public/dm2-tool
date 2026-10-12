# dm2-cynefin-model (delta)

This delta only moves enumerations, tables and examples out of requirement
prose into scenarios so each requirement states one behaviour. No normative
content is added or removed; the OpenSpec 1.14 strict style rule requires the
requirement text itself to stay under 500 characters.

## MODIFIED Requirements

### Requirement: Five semantic complexity dimensions
The Cynefin model SHALL assess complexity along exactly five semantic dimensions, each measuring the **knowability of cause and effect** rather than problem scale. Every dimension SHALL accept one of `clear`, `complicated`, `complex`, or be absent (abstaining) when no evidence supports it. Scale signals (system count, time span, stakeholder headcount) SHALL NOT be modeled as complexity dimensions.

#### Scenario: Dimension vocabulary is tendency-based
- **WHEN** an assessment is constructed with the five dimension IDs
- **THEN** every provided value SHALL be one of `clear`, `complicated`, `complex`
- **AND** unknown dimension IDs or invalid values SHALL be rejected rather than silently coerced

#### Scenario: Regulation completeness is not complexity
- **WHEN** a description indicates a complete, non-contradictory regulatory regime (e.g. 等保三级合规建设) with multiple aligned stakeholders
- **THEN** `constraint_clarity` and `goal_alignment` SHALL NOT tend toward `complex` merely because regulations or stakeholders are numerous

#### Scenario: The five dimensions and their anchors are fixed
- **THEN** the dimensions and anchors SHALL be:

| Dimension ID | Measures | `clear` anchor | `complicated` anchor | `complex` anchor |
|---|---|---|---|---|
| `requirement_knowability` | 问题空间可知性 | 需求明确、已冻结 | 部分演进但可收敛 | 模糊、持续涌现 |
| `practice_maturity` | 解空间知识 | 有最佳实践可照搬 | 需专家分析、好答案多个 | 无先例、业内首次 |
| `environmental_dynamics` | 答案的时效性 | 静态稳定 | 可预测演进 | 快速变化、答案会过期 |
| `goal_alignment` | 干系人目标冲突（非数量） | 各方接受同一目标 | 多元利益可协调 | 存在根本目标冲突 |
| `constraint_clarity` | 治理约束的一致性（非条文数） | 规则完备且一致 | 有框架但需解释 | 规则缺失或互相矛盾 |

### Requirement: Hard-trigger domain resolution
The resolved domain SHALL be one of `Clear`, `Complicated`, `Complex`, `Chaotic` or `Disorder`, resolved by three ordered rules: a context-validated crisis signal SHALL force `Chaotic` regardless of votes; otherwise at least 3 of 5 dimensions voting `complex` SHALL force `Complex` regardless of the band; otherwise the weighted average of voting dimensions SHALL select the band. Weights and band edges SHALL be named constants, and a direct `--domain` verdict bypasses all three rules.

#### Scenario: All dimensions extreme is classifiable
- **WHEN** all five dimensions vote `complex`
- **THEN** the domain SHALL be `Complex` (via the ≥3-complex hard trigger), never `Complicated`

#### Scenario: Crisis signal forces Chaotic
- **WHEN** a context-validated crisis signal is present even if every dimension vote is `clear`
- **THEN** the domain SHALL be `Chaotic`

#### Scenario: Planning compounds are not crises
- **WHEN** the description only mentions 应急预案、应急演练、应急响应能力建设 or 业务中断风险
- **THEN** no crisis signal SHALL fire and the domain SHALL NOT be `Chaotic` by veto

#### Scenario: Clear majority resolves Clear
- **WHEN** all five dimensions vote `clear` with no crisis signal
- **THEN** the weighted average is 1.0 and the domain SHALL be `Clear`

#### Scenario: Two complex votes without hard trigger stay in band
- **WHEN** exactly two dimensions vote `complex` and the other three vote `complicated`, with default weights
- **THEN** the domain SHALL be `Complicated` (hard trigger not reached, band average below 2.5)

#### Scenario: Mature regulated practice is Complicated
- **WHEN** the 等保三级医院 anchor description is assessed (complete regulatory regime, established security practice, analyzable multi-system integration)
- **THEN** the resolved domain SHALL be `Complicated`

#### Scenario: Emerging uncertain requirements are Complex
- **WHEN** the AI-system anchor description is assessed (requirements uncertain, practice emerging, environment dynamic — at least three complex tendencies)
- **THEN** the resolved domain SHALL be `Complex`

#### Scenario: The weighted bands are fixed
- **THEN** scoring SHALL be `clear=1`, `complicated=2`, `complex=3`
- **AND** abstaining dimensions SHALL be excluded from both numerator and denominator
- **AND** the weighted average SHALL resolve to `Clear` when `avg < 1.5`, `Complicated` when `1.5 ≤ avg < 2.5`, and `Complex` when `avg ≥ 2.5`
- **AND** default weights and band edges SHALL be named constants, testable and tunable without changing the algorithm

### Requirement: Disorder fallback under insufficient conflicting evidence
When no crisis signal is present, the domain SHALL resolve to `Disorder` when either no dimension casts an evidenced vote, or fewer than 3 of 5 dimensions carry evidence while the casting votes span both `clear` and `complex` (or all three tendencies occur). Explicit user-supplied values SHALL count as evidence. Abstaining dimensions SHALL NOT vote, default to a middle value, or inflate agreement, and a `Disorder` result SHALL carry `needs_clarification: true`.

#### Scenario: No information yields Disorder, not a fake middle domain
- **WHEN** an assessment is requested with no dimension values, no evidence, and no crisis signal
- **THEN** the domain SHALL be `Disorder` and `needs_clarification` SHALL be `true`

#### Scenario: Sparse conflicting votes yield Disorder
- **WHEN** only two dimensions are evidenced and one votes `clear` while the other votes `complex`
- **THEN** the domain SHALL be `Disorder`

#### Scenario: Explicit manual values count as evidence
- **WHEN** all five dimension values are supplied explicitly by the user without keyword evidence
- **THEN** the assessment SHALL NOT be `Disorder` on insufficient-evidence grounds

### Requirement: Domain-to-view-depth mapping
Each resolved domain SHALL map to a machine-readable view-depth tier and a human-readable description, exposed in the structured result. The mapping SHALL be advisory: it SHALL NOT alter ViewRecommender activation. Stable tier IDs SHALL be provided so a later change can consume them.

#### Scenario: Disorder recommends no view set
- **WHEN** the resolved domain is `Disorder`
- **THEN** the depth tier SHALL be `none` and the guidance SHALL direct the user to clarification before view selection

#### Scenario: Every domain has a depth tier
- **WHEN** any of the five domains is resolved
- **THEN** the structured result SHALL include both the tier ID and the human-readable guidance

#### Scenario: Every domain has its depth tier
- **THEN** the mapping SHALL be:

| Domain | Tier ID | Guidance |
|---|---|---|
| `Clear` | `minimal` | 2-4 个（OV-1 + CV-1） |
| `Complicated` | `core` | 12-17 个（P0 核心） |
| `Complex` | `extended` | P0+P1 + 行为三件套 |
| `Chaotic` | `full` | 全量 + Fusion Views + 实时模拟 |
| `Disorder` | `none` | 不推荐视图集，先完成澄清 |
