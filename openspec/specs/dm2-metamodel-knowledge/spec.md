# dm2-metamodel-knowledge Specification

## Purpose
Define how dm2 grounds its knowledge base in the authoritative DM2 sources: derived indexes are generated from the data dictionary and metamodel YAML, data groups are reconciled against submodels, the runtime loads only the derived JSON, and the Knowledge API exposes dictionary and metamodel queries to agents.

## Requirements

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

### Requirement: An unresolvable knowledge base is a reported failure
When neither the project-local reference copy nor the packaged reference copy can be located,
dm2 SHALL fail with a non-zero exit code and report the condition, and SHALL NOT continue with an
empty knowledge base. The same applies to any other runtime knowledge asset resolved the same
way (`concerns.yaml`).

#### Scenario: Resolution raises instead of returning a phantom path
- **WHEN** `get_reference_path()` is called and neither `.dm2/reference/` nor the packaged
  `dm2-reference/core/` exists
- **THEN** it SHALL raise `KnowledgeBaseNotFound` rather than return a path that does not exist
- **AND** a caller SHALL NOT receive an empty result set as a success

#### Scenario: JSON mode reports the condition as an envelope
- **WHEN** a knowledge-dependent command runs with `--json` (or `-j`) and the knowledge base
  cannot be resolved
- **THEN** stdout SHALL contain the JSON envelope with `status` equal to `"error"`
- **AND** `error.code` SHALL be `KB_NOT_FOUND`
- **AND** the exit code SHALL be non-zero

#### Scenario: Human mode reports an actionable message
- **WHEN** the same condition occurs without a JSON flag
- **THEN** dm2 SHALL print a message naming what was not found and how to fix it
- **AND** the exit code SHALL be non-zero

#### Scenario: Both entry points behave identically
- **WHEN** the CLI is invoked as the `dm2` console script
- **THEN** it SHALL report the condition exactly as when invoked as `python -m dm2.cli.main`

#### Scenario: A missing concerns file is reported, not silently empty
- **WHEN** `dm2 concern list` runs and `concerns.yaml` cannot be located
- **THEN** it SHALL report the missing knowledge base rather than an empty template list

#### Scenario: Developer debugging still gets the traceback
- **WHEN** `DM2_DEBUG` is set and the knowledge base cannot be resolved
- **THEN** the underlying exception SHALL propagate instead of being converted into a message

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
