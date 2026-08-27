# DM2 Explore Workflow (delta)

## ADDED Requirements

### Requirement: Explore hints trace dependency chains
The explore workflow instruction text SHALL include a dependency-chain hint: when examining
a view, the agent SHALL note its `dependencies` (prerequisites) and `downstream` (dependents)
so dependency-implied views are considered in discussions.

#### Scenario: OV-1 discussion surfaces its dependents
- **WHEN** the explore instructions are generated
- **THEN** they SHALL mention checking a view's `dependencies` and `downstream`
- **AND** SHALL give an example such as OV-1 being a prerequisite of OV-2 and OV-5a
