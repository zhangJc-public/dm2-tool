## ADDED Requirements

### Requirement: Three-dimensional architecture verification
The system SHALL provide a Claude Code skill (`dm2-verify`) that performs a three-dimensional gap analysis on generated DoDAF views, following openspec's "verify" pattern.

#### Scenario: Completeness check
- **WHEN** user invokes `/dm2:verify <change-name>`
- **THEN** the AI Agent SHALL compare recommended views (from analysis) against generated views (from ViewManager)
- **AND** SHALL report any recommended views that have NOT been generated as CRITICAL issues
- **AND** SHALL report views that are `in_progress` as WARNING issues

#### Scenario: Correctness check
- **WHEN** AI Agent evaluates a generated view for DM2 rule compliance
- **THEN** the AI Agent SHALL read the view content from the output path
- **AND** SHALL execute `dm2 instructions <view_id> --json` to get the expected template and rules
- **AND** SHALL compare generated content against DM2 rules from the instructions
- **AND** SHALL report deviations as WARNING issues with specific recommendations

#### Scenario: Coherence check
- **WHEN** AI Agent evaluates cross-view consistency
- **THEN** the AI Agent SHALL execute `dm2 validate --all --json` to run ConsistencyChecker
- **AND** SHALL group issues by related views
- **AND** SHALL report circular dependencies, orphan resources, unbound activities as per ConsistencyChecker rules

#### Scenario: Verification report format
- **WHEN** verification completes
- **THEN** the output SHALL include a summary scorecard with Completeness/Correctness/Coherence status
- **AND** SHALL group issues by severity: CRITICAL (must fix) / WARNING (should fix) / SUGGESTION (nice to fix)
- **AND** each issue SHALL include a specific, actionable recommendation

#### Scenario: All clear
- **WHEN** no issues are found across all three dimensions
- **THEN** the AI Agent SHALL report "All checks passed. Ready for archive."
