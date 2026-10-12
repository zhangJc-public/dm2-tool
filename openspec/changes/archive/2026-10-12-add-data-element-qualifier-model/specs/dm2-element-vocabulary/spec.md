# dm2-element-vocabulary (delta)

This delta introduces the data element / qualifier model: a curated vocabulary,
a deterministic composer, and a reconciliation gate against the curated alias layer.

## ADDED Requirements


### Requirement: Element vocabulary is a curated, complete source
The system SHALL ship a curated vocabulary at
`dm2-reference/dm2-element-vocabulary.yaml` declaring three kinds of entry:
data elements (object classes), qualifiers (structural words and relation
predicates), and relation templates. Every token produced by decomposing a
dictionary term name SHALL resolve to exactly one registered entry, and the
build SHALL fail with a non-zero exit code naming any unregistered token.

#### Scenario: Every term token is registered
- **WHEN** the vocabulary is loaded against the 279 dictionary term names
- **THEN** every decomposed token SHALL match an entry in `elements` or `qualifiers`
- **AND** the count of distinct tokens SHALL be reported by the build

#### Scenario: An unregistered token fails the build
- **WHEN** a term name contains a token absent from the vocabulary
- **THEN** the build SHALL exit non-zero and name the token and the offending term(s)
- **AND** SHALL NOT emit a partially modelled vocabulary

#### Scenario: A malformed template fails the build
- **WHEN** a relation template declares a placeholder missing from its Chinese
  template, or names a connector that is not registered
- **THEN** the build SHALL exit non-zero and identify the template

### Requirement: Compositional canonical names are deterministic and zero-LLM
The system SHALL compose a canonical Chinese name for a term from the vocabulary
alone: it SHALL match the longest contiguous connector sequence first, compose
the slot token runs recursively, fall back to object-class concatenation, and
apply the structural type rules (a trailing `type type` renders as
`{prefix}的类型`, a trailing `type` as `{prefix}类型`). Composition SHALL be a
pure function of the term name and the vocabulary, and SHALL NOT call an LLM.

#### Scenario: A relation term composes through its template
- **WHEN** `activityPartOfCapability` is composed
- **THEN** the result SHALL be `活动属于能力`

#### Scenario: A multi-token object slot composes recursively
- **WHEN** `activityPartOfProjectType` is composed
- **THEN** the result SHALL be `活动属于项目类型`

#### Scenario: Longest connector wins
- **WHEN** a term matches both a short connector (`by`) and a longer one (`is realized by`)
- **THEN** the longer connector SHALL be used

#### Scenario: Powertype structure follows the type rules
- **WHEN** `CountryType` and `CountryTypeType` are composed
- **THEN** the results SHALL be `国家类型` and `国家类型的类型` respectively

#### Scenario: Composition is repeatable
- **WHEN** the same term is composed twice in one process and across processes
- **THEN** the result SHALL be identical

### Requirement: Composition is reconciled against the curated alias layer
A test SHALL compose all 279 terms and compare each composed name against the
curated Chinese alias layer, requiring exact reproduction for at least 90% of
entity terms and at least 90% of association terms. Every mismatch SHALL be
reported with the term, the composed name, and the curated alias, so that the
vocabulary or the templates can be revised deliberately.

#### Scenario: Coverage thresholds are enforced
- **WHEN** the reconciliation test runs
- **THEN** entity coverage and association coverage SHALL each be at least 90%
- **AND** the test SHALL fail if either threshold is not met

#### Scenario: Mismatches are visible, not silent
- **WHEN** a composed name differs from every curated alias of that term
- **THEN** the term, composed name, and curated aliases SHALL appear in the failure output

#### Scenario: The alias layer is not replaced by composition
- **WHEN** the vocabulary is introduced
- **THEN** the curated `zh_aliases` SHALL remain available for retrieval and display
- **AND** composition SHALL NOT overwrite them
