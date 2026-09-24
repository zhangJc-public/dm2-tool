# dm2-cynefin-model Specification

## Purpose
Define the Cynefin complexity domain model used by dm2: five cause-and-effect knowability dimensions, vote-plus-hard-trigger domain resolution (including the Disorder fifth domain), evidence-driven confidence, the scale profile kept separate from domain logic, and the domain-to-view-depth mapping.

## Requirements

### Requirement: Five semantic complexity dimensions

The Cynefin model SHALL assess problem complexity along exactly five semantic dimensions, each measuring the **knowability of cause-and-effect** rather than problem scale. Every dimension SHALL accept one of three tendency values — `clear`, `complicated`, `complex` — or be absent (abstaining) when no evidence supports a judgment:

| Dimension ID | Measures | `clear` anchor | `complicated` anchor | `complex` anchor |
|---|---|---|---|---|
| `requirement_knowability` | 问题空间可知性 | 需求明确、已冻结 | 部分演进但可收敛 | 模糊、持续涌现 |
| `practice_maturity` | 解空间知识 | 有最佳实践可照搬 | 需专家分析、好答案多个 | 无先例、业内首次 |
| `environmental_dynamics` | 答案的时效性 | 静态稳定 | 可预测演进 | 快速变化、答案会过期 |
| `goal_alignment` | 干系人目标冲突（非数量） | 各方接受同一目标 | 多元利益可协调 | 存在根本目标冲突 |
| `constraint_clarity` | 治理约束的一致性（非条文数） | 规则完备且一致 | 有框架但需解释 | 规则缺失或互相矛盾 |

Scale signals (system count, time span, stakeholder headcount) SHALL NOT be modeled as complexity dimensions — see the scale profile requirement.

#### Scenario: Dimension vocabulary is tendency-based
- **WHEN** an assessment is constructed with the five dimension IDs
- **THEN** every provided value SHALL be one of `clear`, `complicated`, `complex`
- **AND** unknown dimension IDs or invalid values SHALL be rejected rather than silently coerced

#### Scenario: Regulation completeness is not complexity
- **WHEN** a description indicates a complete, non-contradictory regulatory regime (e.g. 等保三级合规建设) with multiple aligned stakeholders
- **THEN** `constraint_clarity` and `goal_alignment` SHALL NOT tend toward `complex` merely because regulations or stakeholders are numerous

### Requirement: Hard-trigger domain resolution

The resolved domain SHALL be one of `Clear`, `Complicated`, `Complex`, `Chaotic`, or `Disorder`. Resolution SHALL apply, in order:

1. **Crisis veto** — when a **context-validated crisis signal** is present (an ongoing/realized emergency per the deriver's context rules — scope or aspect gate satisfied and not inside a planning compound such as 应急预案/应急演练/中断风险), the domain SHALL be `Chaotic` regardless of dimension votes. A raw candidate word alone (e.g. the substring 应急 inside 应急预案) SHALL NOT constitute a crisis signal.
2. **Complex hard trigger** — when at least 3 of the 5 dimensions vote `complex` and no crisis signal is present, the domain SHALL be `Complex`, regardless of the weighted band.
3. **Weighted band** — otherwise the weighted average score of *voting* dimensions (`clear=1`, `complicated=2`, `complex=3`; abstaining dimensions excluded from both numerator and denominator) SHALL resolve to `Clear` when `avg < 1.5`, `Complicated` when `1.5 ≤ avg < 2.5`, and `Complex` when `avg ≥ 2.5`.

Default dimension weights and band edges SHALL be defined as named constants so they are testable and tunable without changing the algorithm. A direct `--domain` verdict (see its requirement) bypasses all three rules.

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

### Requirement: Disorder fallback under insufficient conflicting evidence

When no crisis signal is present, the domain SHALL resolve to `Disorder` when EITHER:

- **fully uninformed**: no dimension casts an evidenced vote at all, or
- **insufficient and cross-domain conflicting**: fewer than 3 of the 5 dimensions carry supporting evidence (explicit user-supplied values SHALL count as evidence), AND the casting votes contain both a `clear` and a `complex` tendency, or all three tendency values occur.

Abstaining dimensions SHALL NOT vote, SHALL NOT default to a middle value, and SHALL NOT inflate agreement. A `Disorder` result SHALL carry a machine-readable `needs_clarification: true` flag.

#### Scenario: No information yields Disorder, not a fake middle domain
- **WHEN** an assessment is requested with no dimension values, no evidence, and no crisis signal
- **THEN** the domain SHALL be `Disorder` and `needs_clarification` SHALL be `true`

#### Scenario: Sparse conflicting votes yield Disorder
- **WHEN** only two dimensions are evidenced and one votes `clear` while the other votes `complex`
- **THEN** the domain SHALL be `Disorder`

#### Scenario: Explicit manual values count as evidence
- **WHEN** all five dimension values are supplied explicitly by the user without keyword evidence
- **THEN** the assessment SHALL NOT be `Disorder` on insufficient-evidence grounds

### Requirement: Evidence-driven confidence

Confidence SHALL be a value in `[0.20, 0.95]` derived from (a) evidence coverage — the fraction of the five dimensions carrying supporting evidence or explicit values — and (b) vote agreement — dispersion among voting dimensions only. Confidence SHALL be higher when coverage is complete and votes agree, and lower when evidence is sparse or votes split. The confidence decomposition (coverage and agreement components) SHALL be exposed in the structured output.

#### Scenario: Fully evidenced uniform votes reach high confidence
- **WHEN** all five dimensions carry evidence and cast identical votes
- **THEN** confidence SHALL be at least `0.85`

#### Scenario: Bare defaults cannot achieve top confidence
- **WHEN** no evidence is supplied and dimension values come solely from fallback defaults or abstention
- **THEN** confidence SHALL be at most `0.40`

#### Scenario: Confidence split is visible
- **WHEN** any assessment is serialized to structured output
- **THEN** the output SHALL include the numeric coverage and agreement components used to derive confidence

### Requirement: Scale profile separated from domain

The analyzer SHALL accept and report a separate **scale profile** containing at least: estimated system count, time span, and stakeholder count/level. The scale profile SHALL NOT participate in dimension votes, weighted scoring, or domain resolution. It SHALL be carried in the structured result as an advisory breadth signal for downstream consumers.

#### Scenario: Scale alone cannot move the domain
- **WHEN** two assessments differ only in scale profile (e.g. 2 vs 20 systems) and share identical dimension votes and evidence
- **THEN** both SHALL resolve to the same domain with identical confidence

#### Scenario: Scale profile is reported
- **WHEN** an assessment includes scale inputs
- **THEN** the structured result SHALL contain a `scale_profile` object distinct from the dimensions array

### Requirement: Domain-to-view-depth mapping

Each resolved domain SHALL map to a machine-readable view-depth tier and a human-readable description, exposed in the structured result:

| Domain | Tier ID | Guidance |
|---|---|---|
| `Clear` | `minimal` | 2-4 个（OV-1 + CV-1） |
| `Complicated` | `core` | 12-17 个（P0 核心） |
| `Complex` | `extended` | P0+P1 + 行为三件套 |
| `Chaotic` | `full` | 全量 + Fusion Views + 实时模拟 |
| `Disorder` | `none` | 不推荐视图集，先完成澄清 |

The mapping SHALL be advisory: it SHALL NOT alter ViewRecommender activation in this change; a stable tier ID is provided so a later change can consume it.

#### Scenario: Disorder recommends no view set
- **WHEN** the resolved domain is `Disorder`
- **THEN** the depth tier SHALL be `none` and the guidance SHALL direct the user to clarification before view selection

#### Scenario: Every domain has a depth tier
- **WHEN** any of the five domains is resolved
- **THEN** the structured result SHALL include both the tier ID and the human-readable guidance

### Requirement: Assessment resolution states

Every Cynefin assessment SHALL carry a machine-readable `resolution` field with one of two values:

- `heuristic` — produced solely by mechanical derivation from text; a suggestion, not a verdict.
- `adjudicated` — confirmed by an actor with context (the user or an in-loop AI agent), via at least one explicit dimension option or a direct domain verdict.

Persisted state and human-readable output SHALL distinguish the two; heuristic results MUST NOT be presented as settled facts.

#### Scenario: Text-only derivation is heuristic
- **WHEN** `dm2 cynefin -d "..."` runs without explicit dimension options or a domain verdict
- **THEN** the result SHALL carry `resolution: "heuristic"`

#### Scenario: Explicit options adjudicate
- **WHEN** any of `--knowability/--maturity/--dynamics/--alignment/--constraints` is supplied
- **THEN** the result SHALL carry `resolution: "adjudicated"` and the affected dimensions SHALL be marked `source: user`

#### Scenario: Status displays the distinction
- **WHEN** the latest persisted assessment is heuristic versus adjudicated
- **THEN** `dm2 status` SHALL render them differently (e.g. a draft marker versus a confirmed marker)

### Requirement: Rubric-based assessment is the canonical path

The system SHALL ship a five-dimension assessment rubric: for every dimension, three anchored level descriptions (`clear` / `complicated` / `complex`) and at least one elicitation question in the externalized YAML. A heuristic derivation SHALL be presented as a **prefill** of the rubric (suggested tendency plus matched evidence per dimension), never as a replacement for adjudication. The rubric SHALL be available both embedded in the `-d` JSON result and on its own without a description.

#### Scenario: JSON carries the rubric with prefill
- **WHEN** `dm2 cynefin -d "..." --json` runs
- **THEN** `data.rubric` SHALL contain, for each of the five dimensions, its elicitation question, the three anchored descriptions, the heuristic prefill tendency, and the prefill evidence

#### Scenario: Blank rubric without description
- **WHEN** `dm2 cynefin --rubric-only --json` runs
- **THEN** it SHALL output the rubric structure with empty prefill and SHALL exit successfully

#### Scenario: Rubric content is externalized
- **WHEN** the anchors or questions need editing
- **THEN** editing the shipped YAML SHALL be sufficient without Python changes

### Requirement: Direct domain verdict

The CLI SHALL accept a direct domain verdict (`--domain <Clear|Complicated|Complex|Chaotic|Disorder>`) from an adjudicator. When supplied, voting, hard triggers, weighted bands and crisis derivation for the final domain SHALL be bypassed, while the heuristic evidence pack (votes, signals, rubric prefill) SHALL still be computed from the description when one is given and retained for audit. The result SHALL be `resolution: "adjudicated"`.

#### Scenario: Agent overrides a false crisis
- **WHEN** a description mechanically matches a crisis signal but the adjudicator runs `--domain Complicated`
- **THEN** the persisted domain SHALL be `Complicated` and the evidence pack SHALL still record the mechanical crisis match

#### Scenario: Invalid verdict rejected
- **WHEN** `--domain NotADomain` is passed
- **THEN** the command SHALL fail with a structured INVALID_ARG error
