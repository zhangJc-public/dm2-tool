# dm2-metamodel-knowledge (delta)

This delta adds a curated Chinese alias layer to the DM2 term knowledge so Chinese
and multi-token queries recall the right terms, without introducing an LLM or
altering the DoDAF provenance of the data dictionary.

## ADDED Requirements

### Requirement: Chinese term aliases are curated and searchable
The system SHALL ship a curated Chinese alias source at
`dm2-reference/dm2-term-zh-aliases.yaml` covering every dictionary term, and the
runtime term search SHALL match it. The alias layer is dm2-authored content: it
SHALL NOT be produced by translating definitions at runtime, and it SHALL NOT
alter the dictionary's own `aliases`.

#### Scenario: A Chinese query reaches the right term
- **WHEN** the agent executes `dm2 knowledge search "资源流" --json`
- **THEN** the response SHALL include the dictionary term whose curated alias matches
- **AND** `count` SHALL be greater than zero
- **AND** each result SHALL carry the term's `zh_aliases`

#### Scenario: A CamelCase association is reachable in Chinese
- **WHEN** the agent searches with the curated Chinese alias of an association term
  (e.g. the alias of `activityPartOfCapability`)
- **THEN** that association term SHALL be present in the results

#### Scenario: Every term carries at least one alias
- **WHEN** `terms.json` is inspected
- **THEN** each of the 279 terms SHALL have a non-empty `zh_aliases` list
- **AND** a term added to the dictionary without a Chinese alias SHALL fail the test suite

#### Scenario: The build refuses an inconsistent alias source
- **WHEN** the alias source names a key that is not a dictionary term
- **THEN** the build script SHALL exit non-zero and report the unknown key(s)
- **WHEN** an alias entry is an empty string or repeats within the same term
- **THEN** the build script SHALL exit non-zero and report the offending term

## MODIFIED Requirements

### Requirement: Knowledge indexes derived from authoritative sources
The system SHALL provide a deterministic, zero-LLM build script that reads
`dm2-reference/dm2-data-dictionary.yaml`, `dm2-reference/dm2-metamodel-2.02.yaml`,
and the curated `dm2-reference/dm2-term-zh-aliases.yaml`, and emits four derived
indexes under `dm2-reference/core/`: `terms.json`, `associations.json`,
`taxonomy.json`, and `view-content-spec.json`.

#### Scenario: Indexes regenerate from sources
- **WHEN** the build script runs against the source YAMLs
- **THEN** it SHALL emit `terms.json` containing all 279 dictionary terms with
  CURIE id, definition, aliases, reconciled data groups, association flag, and
  the curated `zh_aliases`
- **AND** SHALL emit `associations.json` containing at least 60 binary
  associations, each with endpoint types, IDEAS place roles, and domain roles
  where present
- **AND** SHALL emit `taxonomy.json` with super-subtype parent/child maps and
  the 26 unique powertype pairs (deduped from 47 cross-submodel
  powertypeInstance relations)
- **AND** SHALL emit `view-content-spec.json` with necessary/optional terms and
  necessary associations for all 52 DoDAF views

#### Scenario: Alias keys must resolve to dictionary terms
- **WHEN** the alias source contains a key absent from the dictionary
- **THEN** the build SHALL fail with a non-zero exit code naming the unknown key(s)
- **AND** SHALL NOT emit a partially aliased `terms.json`

#### Scenario: Stale indexes are detected
- **WHEN** a test run compares emitted indexes against the committed indexes
- **THEN** the test SHALL fail if the source YAMLs changed without index
  regeneration

### Requirement: Runtime loads derived indexes
Runtime components SHALL load the derived JSON indexes (via the standard
reference path resolution: local `.dm2/reference/` first, package fallback),
not the 840 KB source YAMLs.

#### Scenario: Term queries use the new store
- **WHEN** `DM2KnowledgeIndexer` initializes
- **THEN** it SHALL load `terms.json` as the term source
- **AND** `search_terms` SHALL match term names, standard aliases, and curated
  Chinese aliases

#### Scenario: Multi-token queries require every token
- **WHEN** a query contains more than one token (split on whitespace and common
  Chinese/English punctuation)
- **THEN** a term SHALL be returned only if every token appears somewhere in its
  searchable text (term name, definition, standard aliases, curated Chinese
  aliases, or data groups)
- **AND** a single-token query SHALL keep the existing substring behaviour

#### Scenario: Term-name and alias hits rank above definition hits
- **WHEN** a query matches both a term's name/Chinese alias and another term's
  definition
- **THEN** the name/alias match SHALL appear before the definition-only match
