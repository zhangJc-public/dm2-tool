# dm2-metamodel-knowledge (delta)

This delta makes term search explainable and order-sensitive: results carry a
machine-readable reason, and a query whose token pattern matches the term's
decomposition in order outranks a term that merely contains the same concepts.

## MODIFIED Requirements

### Requirement: Runtime loads derived indexes
Runtime components SHALL load the derived JSON indexes (via the standard
reference path resolution: local `.dm2/reference/` first, package fallback),
not the 840 KB source YAMLs.

#### Scenario: Term queries use the new store
- **WHEN** `DM2KnowledgeIndexer` initializes
- **THEN** it SHALL load `terms.json` as the term source
- **AND** `search_terms` SHALL match term names, standard aliases, curated
  Chinese aliases, and the composed canonical name

#### Scenario: Multi-token queries require every token
- **WHEN** a query contains more than one token (split on whitespace and common
  Chinese/English punctuation)
- **THEN** a term SHALL be returned only if every token is satisfied, either as
  a substring of its searchable text or through the vocabulary
- **AND** a single-token query SHALL keep the existing substring behaviour

#### Scenario: Query segments normalize through the vocabulary
- **WHEN** a query segment matches a vocabulary entry's Chinese text (or is an
  English vocabulary token)
- **THEN** a term whose decomposed token set contains any of that entry's
  candidate tokens SHALL rank above terms that only satisfy the segment as text
- **AND** a segment that matches no vocabulary entry SHALL fall back to
  substring matching, so recall never regresses

#### Scenario: Ranking prefers the query whose structure matches
- **WHEN** a query's token pattern matches a term's decomposition as an ordered
  subsequence
- **THEN** that term SHALL rank above terms that only match the same concepts
  in a different order or relation
- **AND** an exact whole-query match (name, alias, or canonical name) SHALL
  still rank first

#### Scenario: Structural matches rank above substring-only matches
- **WHEN** a query such as `能力 活动` matches relation terms structurally and
  other terms only by text
- **THEN** the structurally matched terms SHALL appear first, even when another
  term has a single token equal to one of its aliases

#### Scenario: Exact whole-query matches still rank first
- **WHEN** a term's name or a whole alias equals the entire query (for a
  single-token query, the token itself)
- **THEN** that term SHALL rank first

#### Scenario: Term-name and alias hits rank above definition hits
- **WHEN** a query matches both a term's name/Chinese alias and another term's
  definition
- **THEN** the name/alias match SHALL appear before the definition-only match

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

#### Scenario: Search results can explain themselves
- **WHEN** the agent executes `dm2 knowledge search "活动 属于 能力" --explain --json`
- **THEN** each result SHALL carry a `match` object with the match `tier` and
  `kind`, the matched token `pattern` where applicable, and one entry per query
  segment describing how that segment was routed (token or text)
- **AND** the `kind` SHALL be one of `exact`, `pattern`, `structural`,
  `substring`, `text`

#### Scenario: Explanation is opt-in
- **WHEN** `dm2 knowledge search "能力" --json` runs without `--explain`
- **THEN** each result SHALL NOT contain a `match` field
- **AND** the remaining result fields SHALL be unchanged from the previous release

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
