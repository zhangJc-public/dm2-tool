# Spec Delta

## Purpose

The required-association check reports what a view's own structured data is missing.

## ADDED Requirements

### Requirement: Required associations are checked per view
The system SHALL evaluate a view's necessary associations against that view's own structured note only, so that another view's frontmatter cannot satisfy them.

#### Scenario: The view's own note satisfies its requirements
- **WHEN** the note keyed by the view's id declares every necessary association
- **THEN** the required-association check SHALL report nothing for that view

#### Scenario: A partial own note still reports the remainder
- **WHEN** the view's own note declares some but not all necessary associations
- **THEN** the check SHALL report the ones still missing

#### Scenario: Another view's note does not satisfy this view
- **WHEN** a different view declares every necessary association
- **AND** the view under test has no note of its own
- **THEN** the check SHALL report that view's associations as missing

#### Scenario: Vault note named after the view
- **WHEN** a note is keyed by a filename that begins with the view id followed by a separator
- **THEN** the check SHALL treat it as that view's note

#### Scenario: A similar view id is not matched
- **WHEN** a note is keyed `OV-20` and the view under test is `OV-2`
- **THEN** the check SHALL NOT use that note as the view's own

#### Scenario: No note at all
- **WHEN** a view has no structured note
- **THEN** the check SHALL report every necessary association as missing
