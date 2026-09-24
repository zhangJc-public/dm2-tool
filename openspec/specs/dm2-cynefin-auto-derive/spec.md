# DM2 Cynefin Auto-Derive

## Purpose
Enable `dm2 cynefin` and the Step 1+2 pipeline to derive Cynefin dimension votes, evidence, crisis signals and scale profile from a natural language description through one shared polarity-safe deriver with an externalized YAML lexicon, while preserving manual dimension overrides.

## Requirements

### Requirement: Auto-derive Cynefin parameters from description
The `dm2 cynefin` command SHALL automatically derive an **evidence pack** from a natural language description: five semantic dimension tendency prefill values (`clear` / `complicated` / `complex`, or abstaining) with matched evidence, a context-validated crisis flag (see the context-rule lexicon requirement), a scale profile (estimated system count, time span, stakeholder count), and a signal report explaining candidate matches that were excluded or left unconfirmed. Purely derived results SHALL be labeled `resolution: "heuristic"`. Derivation SHALL remain polarity-safe: negated lexemes (e.g. 「不确定」「不明确」「未稳定」) SHALL match their negated polarity and MUST NOT be re-matched by an inner positive lexeme.

#### Scenario: Derive with --desc flag
- **WHEN** user runs `dm2 cynefin --desc "..."` or `dm2 cynefin -d "..."`
- **THEN** the command SHALL derive dimension prefill values, evidence spans, crisis flag, scale profile, and signal report
- **AND** SHALL suggest a domain, explicitly marked `resolution: "heuristic"`

#### Scenario: Combined with --json output
- **WHEN** user runs `dm2 cynefin -d "..." --json`
- **THEN** the JSON `data` object SHALL include `suggested_domain`, `domain` (same suggested value, kept for basic readers), `resolution`, `confidence`, `confidence_breakdown`, `dimensions` (each with ID, tendency, evidence, source), `scale_profile`, `depth_tier`, `depth_guidance`, `needs_clarification`, `warnings`, `signal_report`, and `rubric`

#### Scenario: Manual parameters still work
- **WHEN** user runs `dm2 cynefin` with explicit dimension options and without `--desc`
- **THEN** the command SHALL use the provided values, treat them as evidenced, and mark the result `adjudicated`

#### Scenario: Override auto-derived values
- **WHEN** user runs `dm2 cynefin -d "..."` together with an explicit dimension option (e.g. `--knowability complex`)
- **THEN** the explicit option SHALL override only that prefilled dimension while other dimensions stay derived
- **AND** the overall result SHALL be `adjudicated`

#### Scenario: Negation is polarity-safe
- **WHEN** the description contains 「需求不确定」
- **THEN** `requirement_knowability` SHALL prefill toward `complex` (or abstain), never toward `clear` via the substring 「确定」

#### Scenario: No input means Disorder
- **WHEN** user runs `dm2 cynefin` with neither `--desc`, rubric flags, nor any explicit dimension option
- **THEN** the command SHALL succeed and output domain `Disorder` with `needs_clarification: true`

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

Crisis detection SHALL use the v2 context-rule signals from the externalized lexicon (candidate term plus within-window aspect/scope gate, excluding planning compounds). Planning and preparedness language — 应急预案、应急演练、应急响应能力/体系建设、业务中断风险、中断处置流程、防失控措施 — SHALL NOT fire the crisis veto; such rejected candidate matches SHALL appear in `signal_report` as `excluded`, and gate-unsatisfied candidates as `weak`. Disorder results SHALL remain normal successful outcomes directing the user to clarification.

#### Scenario: Crisis description resolves Chaotic
- **WHEN** `dm2 cynefin -d "核心业务全站中断，正在应急处置，事态仍在蔓延"` runs
- **THEN** crisis SHALL be true, domain `Chaotic`, depth tier `full`

#### Scenario: Preparedness descriptions do not fire crisis
- **WHEN** the description only contains planning language (e.g. 「编制应急预案，开展应急演练，完善中断处置流程」)
- **THEN** crisis SHALL be false, no Chaotic veto applies, and `signal_report` SHALL record the rejected crisis candidate(s) with reason `excluded`

#### Scenario: Disorder output is structurally marked
- **WHEN** a derivation yields `Disorder`
- **THEN** JSON SHALL carry `needs_clarification: true` and depth tier `none`
- **AND** non-JSON text output SHALL print guidance to clarify requirements before selecting views

### Requirement: Step 1 pipeline surfaces Disorder via clarification questions

When the pipeline's Cynefin assessment resolves to `Disorder`, the Step 1+2 result SHALL retain the clarification questions already produced by 6W analysis and SHALL mark the scope output as needing clarification; pipeline execution SHALL NOT fail or block solely because the domain is Disorder.

#### Scenario: Pipeline run on thin contradictory description
- **WHEN** `Step1IntentScope.execute()` produces a Disorder assessment
- **THEN** the result SHALL include `cynefin_domain` labeled as Disorder and a positive clarification-needed indicator
- **AND** the pipeline SHALL continue producing its remaining Step 1+2 outputs normally

### Requirement: Versioned context-rule lexicon

The deriver's lexicon SHALL be a versioned externalized YAML (`dm2-reference/core/cynefin-keywords.yaml`, copied to `.dm2/reference/` by `dm2 init`). Version 2 SHALL support context rules: each crisis signal defines candidate terms, `require_near` gate terms matched within a character window, and `exclude` planning compounds whose spans veto overlapping candidates. Crisis candidates that fail a gate SHALL be reported `weak`; candidates overlapping an exclusion span SHALL be reported `excluded`. Dimension tendency lists remain supported and MAY also use the exclude/gate fields. A v1 lexicon lacking the v2 structure SHALL produce a clear error naming the file and the expected version, not a silent misparse.

#### Scenario: Gate makes a crisis candidate valid
- **WHEN** text contains 「应急处置中」or「全站中断」
- **THEN** the candidate satisfies its gate (aspect marker 中 / scope marker 全站 within window) and crisis fires

#### Scenario: Exclusion compound vetoes candidate
- **WHEN** text contains 「应急预案」or「业务中断风险」
- **THEN** the overlapping crisis candidate is vetoed and recorded as `excluded` in `signal_report`

#### Scenario: Candidate without gate is weak, not a crisis
- **WHEN** a bare candidate such as 中断 appears without any gate term within its window
- **THEN** crisis SHALL NOT fire and the candidate SHALL be recorded as `weak`

#### Scenario: v1 lexicon rejected clearly
- **WHEN** a project-local lexicon still uses the v1 flat crisis list
- **THEN** the deriver SHALL raise a version error instructing to resync the reference copy

### Requirement: Signal report and adjudicator warnings

The JSON output SHALL include a structured `signal_report` array (one entry per evaluated candidate/signal with `rule`, `matched`, `verdict` of `fired|excluded|weak`, and `reason`) and a `warnings` array of human-oriented notes whenever crisis candidates were rejected/weak, dimensions tied and abstained, or evidence coverage is low. The report drives the in-loop agent's adjudication step.

#### Scenario: Excluded candidate is auditable
- **WHEN** a planning description is assessed
- **THEN** `signal_report` SHALL contain the matched planning compound and the exclusion reason, allowing an adjudicator to reverse the decision with `--domain` if context proves an actual crisis

#### Scenario: Step1 pipeline keeps warnings
- **WHEN** `Step1IntentScope.execute()` produces warnings or a heuristic result
- **THEN** the Step 1+2 output SHALL surface the warnings and SHALL label the domain as heuristic; pipeline execution SHALL NOT be blocked

### Requirement: Rubric form delivery and adjudication commands

The CLI SHALL emit the assessment rubric (questions, three level anchors, prefill tendency and evidence per dimension) inside the `-d` JSON and standalone via `--rubric-only`. A completed adjudication SHALL be submitted either through explicit dimension options or through `--domain <Domain>` (direct verdict, evidence pack retained). Adjudicated results persisted to `.dm2/analysis-state.yaml` SHALL include `resolution: "adjudicated"` and, when `--domain` was used, the mechanically suggested domain for comparison.

#### Scenario: Agent fetches the form
- **WHEN** `dm2 cynefin --rubric-only --json` runs
- **THEN** it SHALL return five dimension entries with question + anchors and empty prefill, plus no domain suggestion

#### Scenario: Direct verdict records disagreement
- **WHEN** `-d "..."` suggests `Chaotic` and the command additionally carries `--domain Complicated`
- **THEN** persisted state SHALL record domain `Complicated`, `resolution: "adjudicated"`, and the mechanical suggestion (`suggested_domain: "Chaotic"`)
