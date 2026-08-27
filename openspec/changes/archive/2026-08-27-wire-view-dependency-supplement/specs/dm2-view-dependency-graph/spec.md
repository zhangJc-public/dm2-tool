# View Dependency Graph (delta)

## ADDED Requirements

### Requirement: Analyze recommendations are dependency-complete
The `dm2 analyze` command SHALL run `ViewRecommender.verify_and_supplement_views()` on the
`recommend()` output before emitting `recommended_views`, so that every recommended view's
transitive dependency ancestors (from views.yaml) are present in the set.

#### Scenario: OV-1 is supplemented when OV-2/OV-5a are recommended
- **WHEN** `dm2 analyze` runs with a description that activates resource-flow / activity
  groups whose candidates include OV-2 or OV-5a
- **THEN** the `recommended_views` output SHALL include OV-1 (a transitive ancestor via
  OV-2/OV-5a dependencies)
- **AND** SHALL include the other ancestors (CV-1, AV-1) transitively
- **AND** supplemented views SHALL be deduplicated and sorted by (priority, -relevance_score)

#### Scenario: Supplement is idempotent
- **WHEN** the recommended set already contains a view's full ancestor chain
- **THEN** `verify_and_supplement_views()` SHALL add no duplicates and change nothing

### Requirement: Supplement reason labels the ancestor origin
Supplemented views SHALL carry a reason distinguishing them from data-group-activated
recommendations (e.g. "路径完整性补充 - {view_id}（被 {groups} 数据组需要）").

#### Scenario: Reason present in JSON output
- **WHEN** `dm2 analyze --json` outputs a supplemented view
- **THEN** the view's `reason` SHALL contain the supplement marker text
