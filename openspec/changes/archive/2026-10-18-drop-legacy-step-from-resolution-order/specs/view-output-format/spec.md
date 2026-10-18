# Spec Delta

## MODIFIED Requirements

### Requirement: Format resolution order
The system SHALL resolve a view's format from, in order: a per-view override, the project default, and the representation's own default.

#### Scenario: Per-view override wins
- **WHEN** `views.formats.overrides` names the view
- **THEN** that format SHALL be used, and reported with `format_source: override`

#### Scenario: Project default applies to diagram views only
- **WHEN** `views.formats.default` is set
- **THEN** it SHALL apply to views whose representation is carried by a diagram
- **AND** it SHALL NOT change a `table` or `text` view away from markdown

#### Scenario: Unset configuration falls back to the representation default
- **WHEN** no override or project default is configured
- **THEN** the format SHALL be the representation's default, reported with `format_source: representation_default`
