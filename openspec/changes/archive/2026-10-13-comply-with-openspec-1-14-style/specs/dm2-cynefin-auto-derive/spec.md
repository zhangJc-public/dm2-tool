# dm2-cynefin-auto-derive (delta)

This delta only moves enumerations, tables and examples out of requirement
prose into scenarios so each requirement states one behaviour. No normative
content is added or removed; the OpenSpec 1.14 strict style rule requires the
requirement text itself to stay under 500 characters.

## MODIFIED Requirements

### Requirement: Auto-derive Cynefin parameters from description
The `dm2 cynefin` command SHALL derive an **evidence pack** from a natural-language description: five dimension tendency prefills with matched evidence, a context-validated crisis flag, a scale profile, and a signal report of excluded or unconfirmed candidates. Purely derived results SHALL be labeled `resolution: "heuristic"`, and derivation SHALL be polarity-safe — a negated lexeme SHALL match its negated polarity and MUST NOT be re-matched by an inner positive lexeme.

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
The CLI cynefin command and the Step 1+2 pipeline (`Step1IntentScope`) SHALL invoke one shared deriver for text analysis and one shared analyzer for domain resolution; the legacy `_derive_cynefin_from_description` and `_infer_cynefin_values` SHALL be removed. Lexicon and polarity rules SHALL live in `dm2-reference/core/cynefin-keywords.yaml` (packaged, and copied to `.dm2/reference/` by `dm2 init`), not in inline Python literals.

#### Scenario: Identical input yields identical assessment
- **WHEN** the same Chinese description is assessed once via `dm2 cynefin -d` and once through `Step1IntentScope.execute()`
- **THEN** both paths SHALL produce identical dimension values, crisis flag, scale profile, and resolved domain

#### Scenario: Lexicon is externalized
- **WHEN** the keyword lexicon needs to change
- **THEN** editing the shipped YAML configuration SHALL be sufficient; no Python source edit SHALL be required for lexicon changes

#### Scenario: Evidence spans are surfaced from matched lexicon
- **WHEN** derivation matches lexicon entries in the description
- **THEN** each cast dimension SHALL carry the matched term (or source fragment) in its evidence list

### Requirement: Versioned context-rule lexicon
The lexicon SHALL be a versioned externalized YAML. Version 2 SHALL support context rules: candidate terms, `require_near` gate terms within a character window, and `exclude` compounds that veto overlapping candidates — an unconfirmed candidate SHALL be reported `weak`, and a candidate inside an exclusion span SHALL be reported `excluded`. Dimension lists MAY use the same fields. A v1 lexicon SHALL fail with an error naming the file and the expected version, never a silent misparse.

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

### Requirement: Rubric form delivery and adjudication commands
The CLI SHALL emit the assessment rubric — questions, three level anchors, and per-dimension prefill tendency with evidence — inside the `-d` JSON and standalone via `--rubric-only`. Adjudication SHALL be submitted through explicit dimension options or `--domain <Domain>` (a direct verdict that retains the evidence pack). Persisted adjudications SHALL record `resolution: "adjudicated"`, plus the suggested domain when `--domain` was used.

#### Scenario: Agent fetches the form
- **WHEN** `dm2 cynefin --rubric-only --json` runs
- **THEN** it SHALL return five dimension entries with question + anchors and empty prefill, plus no domain suggestion

#### Scenario: Direct verdict records disagreement
- **WHEN** `-d "..."` suggests `Chaotic` and the command additionally carries `--domain Complicated`
- **THEN** persisted state SHALL record domain `Complicated`, `resolution: "adjudicated"`, and the mechanical suggestion (`suggested_domain: "Chaotic"`)
