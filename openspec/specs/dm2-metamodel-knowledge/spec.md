# dm2-metamodel-knowledge Specification

## Purpose
TBD - created by archiving change ground-kb-in-dm2-metamodel. Update Purpose after archive.
## Requirements
### Requirement: Knowledge indexes derived from authoritative sources
The system SHALL provide a deterministic, zero-LLM build script that reads
`dm2-reference/dm2-data-dictionary.yaml` and `dm2-reference/dm2-metamodel-2.02.yaml`
and emits four derived indexes under `dm2-reference/core/`: `terms.json`,
`associations.json`, `taxonomy.json`, and `view-content-spec.json`.

#### Scenario: Indexes regenerate from sources
- **WHEN** the build script runs against the two source YAMLs
- **THEN** it SHALL emit `terms.json` containing all 279 dictionary terms with
  CURIE id, definition, aliases, reconciled data groups, and association flag
- **AND** SHALL emit `associations.json` containing at least 60 binary
  associations, each with endpoint types, IDEAS place roles, and domain roles
  where present
- **AND** SHALL emit `taxonomy.json` with super-subtype parent/child maps and
  the 26 unique powertype pairs (deduped from 47 cross-submodel
  powertypeInstance relations)
- **AND** SHALL emit `view-content-spec.json` with necessary/optional terms and
  necessary associations for all 52 DoDAF views

#### Scenario: Stale indexes are detected
- **WHEN** a test run compares emitted indexes against the committed indexes
- **THEN** the test SHALL fail if the source YAMLs changed without index
  regeneration

### Requirement: Submodel to data group reconciliation
The build script SHALL apply an explicit reconciliation mapping from the
dictionary's submodel marks to the 17 data-group scheme, including the
rules/guidance name-based split and synthetic attribution for Activity and
Resource terms, and SHALL report term-to-group coverage.

#### Scenario: Rules terms split by name
- **WHEN** a term is marked in the `rules` submodel
- **THEN** terms whose names contain Guidance, Standard, or Agreement SHALL be
  attributed to `05-guidance`
- **AND** all other rules terms SHALL be attributed to `10-rules`

#### Scenario: Cross-group terms vote fractionally
- **WHEN** a term belongs to N reconciled groups
- **THEN** group-derived signals SHALL count the term with weight 1/N per group

### Requirement: Runtime loads derived indexes
Runtime components SHALL load the derived JSON indexes (via the standard
reference path resolution: local `.dm2/reference/` first, package fallback),
not the 840 KB source YAMLs.

#### Scenario: Term queries use the new store
- **WHEN** `DM2KnowledgeIndexer` initializes
- **THEN** it SHALL load `terms.json` as the term source
- **AND** `search_terms` SHALL match both term names and aliases

### Requirement: Knowledge API exposes dictionary and metamodel queries
The system SHALL provide `dm2 knowledge` subcommands for term, taxonomy,
association, and view-content-spec queries, all in the standard
`{status, data}` JSON envelope.

#### Scenario: Term lookup
- **WHEN** the AI agent executes `dm2 knowledge term Activity --json`
- **THEN** the response SHALL include the term definition, aliases, data
  groups, and the views marking the term necessary or optional
- **AND** when the term is an association, the response SHALL include its
  endpoint types and roles

#### Scenario: Taxonomy lookup
- **WHEN** the AI agent executes `dm2 knowledge taxonomy Performer --json`
- **THEN** the response SHALL include System, Service, OrganizationType,
  PersonRoleType, and Port (and their subtypes) as subtypes of Performer

#### Scenario: Association lookup
- **WHEN** the AI agent executes `dm2 knowledge associations --type Performer --json`
- **THEN** the response SHALL list associations whose endpoint types include
  Performer or its subtypes (e.g. activityPerformedByPerformer,
  materielPartOfPerformer, partiesToAnAgreement)

#### Scenario: View content spec lookup
- **WHEN** the AI agent executes `dm2 knowledge views OV-5b --json`
- **THEN** the response SHALL list necessary terms (Activity,
  DomainInformation) and necessary associations
  (activityConsumesResource, activityPerformedByPerformer,
  activityProducesResource) with endpoint types

