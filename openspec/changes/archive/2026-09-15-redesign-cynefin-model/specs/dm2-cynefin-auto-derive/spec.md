## MODIFIED Requirements

### Requirement: Auto-derive Cynefin parameters from description
The `dm2 cynefin` command SHALL support automatic derivation of Cynefin assessment inputs from a natural language description: all five semantic dimension tendency values (`clear` / `complicated` / `complex`, or abstaining), the matched evidence spans supporting each dimension, the crisis signal flag, and a scale profile (estimated system count, time span, stakeholder count). Derivation SHALL use the shared Cynefin deriver and SHALL be polarity-safe: negated lexemes (e.g. 「不确定」「不明确」「未稳定」) SHALL match their negated polarity and MUST NOT be re-matched by an inner positive lexeme (e.g. the substring 「确定」 inside 「不确定」).

#### Scenario: Derive with --desc flag
- **WHEN** user runs `dm2 cynefin --desc "..."` or `dm2 cynefin -d "..."`
- **THEN** the command SHALL derive dimension values, evidence spans, crisis flag, and scale profile from the description
- **AND** SHALL resolve and output a domain using the redesigned Cynefin model

#### Scenario: Combined with --json output
- **WHEN** user runs `dm2 cynefin -d "..." --json`
- **THEN** the JSON `data` object SHALL include `domain`, `domain_label`, `confidence`, a `confidence_breakdown` object, a `dimensions` array (each entry with dimension ID, tendency value, and matched evidence), `scale_profile`, `depth_tier`, `depth_guidance`, and `needs_clarification`

#### Scenario: Manual parameters still work
- **WHEN** user runs `dm2 cynefin` with explicit dimension options and without `--desc`
- **THEN** the command SHALL use the provided values, treat them as evidenced, and perform no keyword derivation

#### Scenario: Override auto-derived values
- **WHEN** user runs `dm2 cynefin -d "..."` together with an explicit dimension option (e.g. `--knowability complex`)
- **THEN** the explicit option value SHALL override only that derived dimension, while all other dimensions remain derived
- **AND** the overridden dimension SHALL carry evidence noting it was user-specified

#### Scenario: Negation is polarity-safe
- **WHEN** the description contains 「需求不确定」
- **THEN** `requirement_knowability` SHALL tend toward `complex` (or abstain), never toward `clear` via the substring 「确定」

#### Scenario: No input means Disorder
- **WHEN** user runs `dm2 cynefin` with neither `--desc` nor any explicit dimension option
- **THEN** the command SHALL succeed and output domain `Disorder` with `needs_clarification: true`, instead of fabricating a middle-value assessment

## ADDED Requirements

### Requirement: Single shared deriver for CLI and pipeline

The CLI cynefin command and the Step 1+2 pipeline (`Step1IntentScope`) SHALL invoke one shared deriver component for text analysis and one shared analyzer for domain resolution. The legacy implementations `_derive_cynefin_from_description` (CLI) and `_infer_cynefin_values` (pipeline) SHALL be removed. The deriver's lexicon and polarity rules SHALL live in an externalized YAML configuration (`dm2-reference/core/cynefin-keywords.yaml`, packaged with the wheel and copied to `.dm2/reference/` by `dm2 init`) rather than inline Python literals.

#### Scenario: Identical input yields identical assessment
- **WHEN** the same Chinese description is assessed once via `dm2 cynefin -d` and once through `Step1IntentScope.execute()`
- **THEN** both paths SHALL produce identical dimension values, crisis flag, scale profile, and resolved domain

#### Scenario: Lexicon is externalized
- **WHEN** the keyword lexicon needs to change
- **THEN** editing the shipped YAML configuration SHALL be sufficient; no Python source edit SHALL be required for lexicon changes

#### Scenario: Evidence spans are surfaced from matched lexicon
- **WHEN** derivation matches lexicon entries in the description
- **THEN** each cast dimension SHALL carry the matched term (or source fragment) in its evidence list

### Requirement: Crisis and Disorder CLI behavior

The cynefin command SHALL map crisis lexicon (e.g. 应急、中断、失控、战时、正在蔓延) to the crisis signal that forces the `Chaotic` domain, and SHALL surface Disorder results as a normal, successful outcome directing the user to clarification.

#### Scenario: Crisis description resolves Chaotic
- **WHEN** `dm2 cynefin -d "核心业务全站中断，正在应急处置，事态仍在蔓延"` is run
- **THEN** the output domain SHALL be `Chaotic` and the depth tier SHALL be `full`

#### Scenario: Disorder output is structurally marked
- **WHEN** a derivation yields `Disorder`
- **THEN** JSON output SHALL carry `needs_clarification: true` and depth tier `none`
- **AND** non-JSON text output SHALL print guidance to clarify requirements before selecting views

### Requirement: Step 1 pipeline surfaces Disorder via clarification questions

When the pipeline's Cynefin assessment resolves to `Disorder`, the Step 1+2 result SHALL retain the clarification questions already produced by 6W analysis and SHALL mark the scope output as needing clarification; pipeline execution SHALL NOT fail or block solely because the domain is Disorder.

#### Scenario: Pipeline run on thin contradictory description
- **WHEN** `Step1IntentScope.execute()` produces a Disorder assessment
- **THEN** the result SHALL include `cynefin_domain` labeled as Disorder and a positive clarification-needed indicator
- **AND** the pipeline SHALL continue producing its remaining Step 1+2 outputs normally
