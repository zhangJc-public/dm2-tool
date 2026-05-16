## ADDED Requirements

### Requirement: Path completeness driven by views.yaml
The ViewRecommender's path completeness check SHALL derive all dependency relationships from `views.yaml` via transitive closure, eliminating the previous 31 hardcoded `(target, required)` tuples in `_check_path_completeness()`.

#### Scenario: Path completeness uses transitive closure
- **WHEN** `ViewRecommender.recommend()` or `verify_and_supplement_views()` calls `_check_path_completeness()`
- **THEN** the missing view calculation SHALL use recursive transitive closure over views.yaml `dependencies`
- **AND** the result SHALL be semantically equivalent to or more complete than the previous hardcoded rules

#### Scenario: Output consistency after migration
- **WHEN** `dm2 analyze -d "..." --json` runs after the migration
- **THEN** the `missing_dependencies` field in the output SHALL be derived from views.yaml rather than hardcoded tuples
- **AND** the recommended views and supplements SHALL be consistent with the views.yaml dependency graph
