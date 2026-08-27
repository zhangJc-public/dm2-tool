# DM2 View Dependency Graph Specification

## Purpose
Establish `views.yaml` as the single source of truth for all 52 DoDAF view dependencies. All dependency queries — topological sort, path completeness, readiness checks, downstream derivation — derive from this source. Eliminates hardcoded dependency rules and ensures consistency across all consuming subsystems.

## Requirements

### Requirement: Views.yaml is the single source of truth for view dependencies
All 52 DoDAF view dependency relationships SHALL be defined exclusively in `dm2-reference/core/views.yaml` via the `dependencies` field. No other file or code path SHALL independently maintain view dependency data.

#### Scenario: All dependencies sourced from views.yaml
- **WHEN** any subsystem queries view dependencies (topological sort, path completeness, readiness check, Agent instruction generation)
- **THEN** the dependency data SHALL originate from views.yaml
- **AND** no hardcoded `(target, required)` tuples SHALL exist in Python source code

#### Scenario: views.yaml dependency completeness
- **WHEN** views.yaml is loaded
- **THEN** every view's `dependencies` field SHALL be complete per DoDAF 2.02 specifications
- **AND** the dependency graph SHALL cover all 52 DoDAF views

### Requirement: Transitive closure for path completeness
The path completeness check SHALL compute the transitive closure of view dependencies via recursive traversal of views.yaml `dependencies`, replacing the previous hardcoded 31-tuple approach.

#### Scenario: Transitive dependency resolution
- **WHEN** ViewRecommender checks path completeness for a set of view IDs
- **THEN** it SHALL recursively traverse all transitive dependencies from views.yaml
- **AND** SHALL return the set of missing views (transitive deps not in the input set)
- **AND** SHALL use a visited set to prevent infinite recursion on cycles

#### Scenario: Hardcoded tuples removed
- **WHEN** `_check_path_completeness()` executes
- **THEN** the implementation SHALL NOT contain any hardcoded `path_rules` list of `(target_views, required_views)` tuples
- **AND** SHALL contain at most ~15 lines of code (down from ~48)

### Requirement: Downstream auto-derived from dependencies
The `downstream` field for each view template SHALL be automatically derived by reversing the `dependencies` field during indexer loading. YAML-declared downstream values SHALL take precedence over auto-derived ones.

#### Scenario: Downstream computed during load
- **WHEN** `DM2KnowledgeIndexer._load_view_templates()` processes views.yaml
- **THEN** for each view with explicit downstream declared in YAML, those values SHALL be preserved
- **AND** for any dependency edge A→B (A depends on B), B's downstream SHALL include A if not already present

#### Scenario: Downstream remains correct after dependency fix
- **WHEN** views.yaml dependencies are updated (added, removed, or corrected)
- **THEN** the downstream fields SHALL automatically reflect the new reverse relationship without manual YAML editing

### Requirement: DAG cycle detection on load
The knowledge indexer SHALL detect circular dependencies when loading views.yaml using Kahn's algorithm, raising an error if cycles exist.

#### Scenario: No cycles in valid views.yaml
- **WHEN** `load_all()` runs with a valid views.yaml containing no dependency cycles
- **THEN** the cycle detection SHALL complete silently without errors
- **AND** the topological order SHALL include all 52 views

#### Scenario: Cycle detected
- **WHEN** `load_all()` runs with a views.yaml containing a circular dependency (e.g., A→B→C→A)
- **THEN** the cycle detection SHALL raise a `ValueError` identifying the views involved in the cycle
- **AND** SHALL prevent downstream infinite recursion in transitive closure and topological sort

### Requirement: All dependency queries derive from the same source
All dependency-consuming code paths — topological sort in `ArtifactGraph`, path completeness in `ViewRecommender`, readiness checks, and Agent instruction dependency lists — SHALL derive their data from the same views.yaml source, guaranteeing consistency.

#### Scenario: ArtifactGraph uses views.yaml dependencies
- **WHEN** `ArtifactGraph.get_generation_order()` computes topological sort
- **THEN** it SHALL use only the `dependencies` field from views.yaml as the in-degree source

#### Scenario: Agent instructions reflect actual dependencies
- **WHEN** `InstructionBuilder.build_view_instructions()` generates dependency artifact lists
- **THEN** the listed dependencies SHALL match the views.yaml `dependencies` field exactly

#### Scenario: Readiness checks use views.yaml
- **WHEN** `ArtifactGraph.compute_status()` checks if a view's dependencies are satisfied
- **THEN** it SHALL compare against the views.yaml `dependencies` field

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
