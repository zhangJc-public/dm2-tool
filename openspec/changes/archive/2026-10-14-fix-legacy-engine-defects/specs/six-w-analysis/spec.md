# Spec Delta

## Purpose

Derives a description's 6W focus (What/How/Where/Who/When/Why) and the architecture entities it names. The dimension scores drive scope selection and view recommendation; the extracted entities are surfaced by `dm2 analyze --json` and required by `dm2 generate`.

## ADDED Requirements

### Requirement: 6W dimension scoring
The system SHALL score an architecture description against all six 6W dimensions and report a primary dimension, up to two secondary dimensions ranked by score, and a confidence value.

#### Scenario: A dominant dimension is identified
- **WHEN** one dimension's keywords dominate the description
- **THEN** that dimension SHALL be reported as primary
- **AND** the confidence SHALL be the primary dimension's share of the total score

#### Scenario: No dimension matches
- **WHEN** no dimension's keywords appear in the description
- **THEN** the system SHALL report `What` as primary with the default confidence rather than failing

#### Scenario: Secondary dimensions are ranked and capped
- **WHEN** more than two non-primary dimensions score above zero
- **THEN** only the two highest-scoring SHALL be reported

### Requirement: Entity extraction across seven buckets
The system SHALL extract architecture entities into seven typed buckets: `system`, `organization`, `activity`, `resource`, `capability`, `location`, and `measure`. Each bucket SHALL be populated when the description names an entity of that type.

#### Scenario: Capability and location are named
- **WHEN** the description names a capability and a location
- **THEN** the `capability` and `location` buckets SHALL each contain the corresponding entity

#### Scenario: Repeated entities are deduplicated
- **WHEN** the same entity appears more than once in the description
- **THEN** it SHALL appear once in its bucket

#### Scenario: Buckets with no match stay empty
- **WHEN** the description names no entity of a given type
- **THEN** that bucket SHALL be present and empty, not omitted from the result

### Requirement: Matches do not run past their anchor
Extraction is keyword-based, so a bucket records a keyword hit rather than a parsed entity and match boundaries are best-effort. Two things the extraction SHALL still guarantee: a match ends at the keyword it was anchored to rather than continuing to the end of the clause, and one matched text is not reported into several buckets.

#### Scenario: A clause containing a predicate
- **WHEN** the description joins an entity to a following verb phrase
- **THEN** the extracted match SHALL end at the entity's type suffix
- **AND** SHALL NOT continue into the following verb phrase

#### Scenario: A verb-anchored match carries no subject
- **WHEN** an activity keyword is preceded by its subject
- **THEN** the extracted activity match SHALL NOT include that subject

#### Scenario: Distinct buckets stay distinct
- **WHEN** a clause is scanned for several entity types
- **THEN** the same matched text SHALL NOT appear in more than one bucket
