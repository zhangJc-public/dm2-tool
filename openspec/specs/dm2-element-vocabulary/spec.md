# dm2-element-vocabulary Specification

## Purpose
Define how dm2 models DM2 term names as standardized data elements and qualifiers
(GB/T 18391 / ISO/IEC 11179: object class + property + representation), composes
canonical Chinese names deterministically and without an LLM, and keeps that
composition reconciled against the curated Chinese alias layer.

## Requirements

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

### Requirement: Queries decompose into data elements and qualifiers
The vocabulary SHALL decompose a query into segments and classify each segment
as a data element, a qualifier, or unknown, carrying the candidate tokens for
every recognized segment. Decomposition SHALL be deterministic, zero-LLM, and
SHALL NOT guess for a segment with no vocabulary entry.

#### Scenario: A Chinese relation query decomposes into a token pattern
- **WHEN** the query `活动 属于 能力` is planned
- **THEN** the segments SHALL be classified as element (`活动` → `activity`/`action`),
  qualifier (`属于` → `part`), element (`能力` → `capability`)
- **AND** the plan SHALL expose the token pattern candidates for the query

#### Scenario: An unrecognized segment is reported, not guessed
- **WHEN** the query `资源流` is planned
- **THEN** that segment SHALL be classified as unknown with no candidate tokens
- **AND** the plan SHALL NOT invent a token for it

#### Scenario: An English vocabulary token is recognized
- **WHEN** the query `activity capability` is planned
- **THEN** both segments SHALL be classified as recognized (element/qualifier) tokens

### Requirement: A token pattern matches as an ordered subsequence
The system SHALL match a query token pattern against a term's decomposed tokens
as an **ordered subsequence**, allowing other tokens in between, and SHALL
report the matched token sequence. A pattern whose segments cannot all be
assigned in order SHALL NOT match.

#### Scenario: Structural words in between do not break the match
- **WHEN** the pattern `[activity, part, capability]` is matched against
  `activityPartOfCapability` (`[activity, part, of, capability]`)
- **THEN** it SHALL match, reporting `[activity, part, capability]`

#### Scenario: A different relation does not match the pattern
- **WHEN** the same pattern is matched against `activityMapsToCapabilityType`
  (`[activity, maps, to, capability, type]`)
- **THEN** it SHALL NOT match, because `part` is absent

#### Scenario: Word order matters
- **WHEN** the reversed query `能力 属于 活动` is matched against
  `activityPartOfCapability`
- **THEN** it SHALL NOT match as a pattern

### Requirement: Any term name can be described through the vocabulary
The vocabulary SHALL describe an arbitrary term name — one already in the
dictionary or one still being proposed — reporting its decomposed tokens, each
token's kind (data element, qualifier, or unknown) and Chinese, the composed
canonical name, and the list of unregistered tokens. Description SHALL be
deterministic, zero-LLM, and SHALL NOT guess a translation for an unregistered
token.

#### Scenario: A prospective name composed of registered tokens
- **WHEN** `CapabilityType` is described
- **THEN** the segments SHALL be `capability` (element → 能力) and `type`
  (qualifier → 类型)
- **AND** the composed name SHALL be `能力类型`
- **AND** `unregistered` SHALL be empty

#### Scenario: An unregistered token is reported, not guessed
- **WHEN** `ZzzThing` is described
- **THEN** `zzz` SHALL appear in `unregistered` with kind `unknown` and no Chinese
- **AND** the composed name SHALL be empty rather than a partial guess

#### Scenario: Description is deterministic
- **WHEN** the same name is described twice
- **THEN** the reported tokens, kinds, Chinese and composed name SHALL be identical
