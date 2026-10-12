# dm2-metamodel-knowledge (delta)

This delta moves the mandatory Chinese name from the hand-curated alias layer to
the composition layer: new dictionary terms are named automatically as long as
their tokens are registered, and curated aliases become optional supplements.

## MODIFIED Requirements

### Requirement: Knowledge indexes derived from authoritative sources
The system SHALL provide a deterministic, zero-LLM build script that reads
`dm2-data-dictionary.yaml`, `dm2-metamodel-2.02.yaml` and the curated
`dm2-term-zh-aliases.yaml` / `dm2-element-vocabulary.yaml`, and emits
`terms.json`, `associations.json`, `taxonomy.json` and `view-content-spec.json`
under `dm2-reference/core/`. It SHALL guarantee a non-empty composed Chinese name
(`canonical_zh`) for every dictionary term.

#### Scenario: Indexes regenerate from sources
- **WHEN** the build script runs against the source YAMLs
- **THEN** it SHALL emit `terms.json` containing all 279 dictionary terms with
  CURIE id, definition, aliases, curated `zh_aliases`, reconciled data groups,
  association flag, and a composed `canonical_zh`
- **AND** SHALL emit `associations.json` containing at least 60 binary
  associations, each with endpoint types, IDEAS place roles, and domain roles
  where present
- **AND** SHALL emit `taxonomy.json` with super-subtype parent/child maps and
  the 26 unique powertype pairs (deduped from 47 cross-submodel
  powertypeInstance relations)
- **AND** SHALL emit `view-content-spec.json` with necessary/optional terms and
  necessary associations for all 52 DoDAF views

#### Scenario: A new term is named automatically
- **WHEN** a term is added to the dictionary whose name decomposes only into
  registered data elements and qualifiers
- **THEN** the build SHALL compose its `canonical_zh` without any new curated
  alias
- **AND** the term SHALL be searchable by that composed name

#### Scenario: No term ships without a Chinese name
- **WHEN** the build computes `canonical_zh` for every dictionary term
- **THEN** it SHALL fail if any term's composed name is empty, rather than emit
  a term that cannot be found in Chinese

#### Scenario: Alias keys must resolve to dictionary terms
- **WHEN** the alias source contains a key absent from the dictionary
- **THEN** the build SHALL fail with a non-zero exit code naming the unknown key(s)
- **AND** SHALL NOT emit an index built from an inconsistent alias source

#### Scenario: Composition coverage is reported
- **WHEN** the build completes
- **THEN** it SHALL report how many entity and association terms composed a
  canonical name, and how many terms carry a curated alias, so a vocabulary
  regression or an alias coverage gap is visible in the build log

#### Scenario: Stale indexes are detected
- **WHEN** a test run compares emitted indexes against the committed indexes
- **THEN** the test SHALL fail if the source YAMLs changed without index
  regeneration

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

#### Scenario: Term name composition preview
- **WHEN** the agent executes `dm2 knowledge compose CapabilityType --json`
- **THEN** the response SHALL list the decomposed tokens with their kind
  (element or qualifier) and Chinese, and the composed canonical name
- **AND** when the name contains an unregistered token, the response SHALL
  report that token in `unregistered` with an empty `composed` value
- **AND** the command SHALL still succeed, because the answer is diagnostic

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

## ADDED Requirements

### Requirement: Curated aliases supplement the composed Chinese name
The system SHALL treat `dm2-reference/dm2-term-zh-aliases.yaml` as an optional
per-term supplement of Chinese synonyms, because the composed `canonical_zh` is
the mandatory Chinese name. The layer SHALL NOT be produced by translating
definitions at runtime and SHALL NOT alter the dictionary's own `aliases`.

#### Scenario: A Chinese query reaches the right term
- **WHEN** the agent executes `dm2 knowledge search "资源流" --json`
- **THEN** the response SHALL include the dictionary term whose curated alias matches
- **AND** `count` SHALL be greater than zero
- **AND** each result SHALL carry the term's `zh_aliases`

#### Scenario: A CamelCase association is reachable in Chinese
- **WHEN** the agent searches with the curated Chinese alias of an association term
  (e.g. the alias of `activityPartOfCapability`)
- **THEN** that association term SHALL be present in the results

#### Scenario: A curated alias is optional
- **WHEN** a dictionary term has no entry in the alias source
- **THEN** the build SHALL succeed and report the coverage gap
- **AND** the term SHALL remain searchable by its composed `canonical_zh`
- **AND** the group aliases it inherits SHALL still apply

### Requirement: The alias source and its group section are validated
The build SHALL validate the curated alias source: unknown keys, empty values
and duplicate aliases SHALL fail it, and its `groups` section SHALL name all 17
data groups with non-empty Chinese aliases.

#### Scenario: Group aliases are mandatory and complete
- **WHEN** the alias source omits the `groups` section, or leaves a data group
  without Chinese aliases
- **THEN** the build SHALL fail with a non-zero exit code

#### Scenario: The build refuses an inconsistent alias source
- **WHEN** the alias source names a key that is not a dictionary term
- **THEN** the build script SHALL exit non-zero and report the unknown key(s)
- **WHEN** an alias entry is an empty string or repeats within the same term
- **THEN** the build script SHALL exit non-zero and report the offending term

## REMOVED Requirements

### Requirement: Chinese term aliases are curated and searchable
**Reason**: superseded by "Curated aliases supplement the composed Chinese name" and
"The alias source and its group section are validated". The old requirement mandated a curated alias for every
dictionary term, which was necessary while the alias layer was the only source
of Chinese names. Composition now guarantees a Chinese name for every term, so
the per-term alias mandate is redundant and taxes every new term with
hand-written content that the model can derive.
