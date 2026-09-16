# View Metadata Schema (delta)

## ADDED Requirements

### Requirement: Group template relationship slots match the association catalog
The `relationships:` frontmatter slots in the 17 data-group templates (`dm2-reference/core/groups/*/*Template.md`) SHALL be projections of the associations in `associations.json` whose endpoint types include a type owned by the group. Vernacular slot names SHALL be mapped to catalog association labels; slots without catalog basis SHALL be removed.

#### Scenario: Performer template relationships are catalog-backed
- **WHEN** the Performer group template is reconciled
- **THEN** its relationship slots SHALL correspond to catalog associations
  with Performer-family endpoints (e.g. `activityPerformedByPerformer`,
  `capabilityOfPerformer`, `materielPartOfPerformer`,
  `personRoleTypePartOfPerformer`, `portPartOfPerformer`,
  `partiesToAnAgreement`)
- **AND** slots without metamodel basis (e.g. `measuredByOrg`) SHALL be
  removed
- **AND** associations misattributed from other types (e.g.
  `consumesResource`, which is the Activity association
  `activityConsumesResource`) SHALL not appear on the Performer template

#### Scenario: Every template slot resolves
- **WHEN** the template reconciliation test runs
- **THEN** every relationship slot in every group template SHALL resolve to a
  label in `associations.json`
- **AND** at least one endpoint of each resolved association SHALL be a type
  (or subtype, via `taxonomy.json`) attributed to that template's group

#### Scenario: Template prose is preserved
- **WHEN** templates are reconciled
- **THEN** only the `relationships:` frontmatter block SHALL be regenerated
- **AND** the template body text, other frontmatter fields, and keywords SHALL
  remain unchanged
