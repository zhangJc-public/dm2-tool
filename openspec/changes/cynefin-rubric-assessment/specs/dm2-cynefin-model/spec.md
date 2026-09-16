## ADDED Requirements

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

## MODIFIED Requirements

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
