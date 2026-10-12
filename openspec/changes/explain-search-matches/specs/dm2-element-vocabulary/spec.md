# dm2-element-vocabulary (delta)

This delta adds the reverse direction of the model: decomposing a Chinese query
into data elements and qualifiers, so retrieval can match on word order rather
than only on "contains these concepts".

## ADDED Requirements

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
