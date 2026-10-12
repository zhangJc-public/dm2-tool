# dm2-metamodel-knowledge (delta)

This delta wires the P1 data element / qualifier model into runtime retrieval:
the derived index carries a composed canonical Chinese name, and term search
normalizes query segments through the vocabulary before falling back to
substring matching.

## MODIFIED Requirements

### Requirement: Knowledge indexes derived from authoritative sources
The system SHALL provide a deterministic, zero-LLM build script that reads
`dm2-reference/dm2-data-dictionary.yaml`, `dm2-reference/dm2-metamodel-2.02.yaml`,
the curated `dm2-reference/dm2-term-zh-aliases.yaml`, and the curated
`dm2-reference/dm2-element-vocabulary.yaml`, and emits four derived indexes under
`dm2-reference/core/`: `terms.json`, `associations.json`, `taxonomy.json`, and
`view-content-spec.json`.

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

#### Scenario: Alias keys must resolve to dictionary terms
- **WHEN** the alias source contains a key absent from the dictionary
- **THEN** the build SHALL fail with a non-zero exit code naming the unknown key(s)
- **AND** SHALL NOT emit a partially aliased `terms.json`

#### Scenario: Composition coverage is reported
- **WHEN** the build completes
- **THEN** it SHALL report how many entity and association terms composed a
  canonical name, so a vocabulary regression is visible in the build log

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
- **AND** a query is "fully structural" only when **every** vocabulary-resolvable
  segment is matched by tokens, so a term satisfying one segment as text cannot
  claim the structural rank

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
