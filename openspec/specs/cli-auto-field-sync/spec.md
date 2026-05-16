## Purpose

Ensure CLI knowledge commands automatically expose all dataclass fields in JSON output without manual field enumeration.

## Requirements

### Requirement: CLI knowledge commands use dataclasses.asdict() for JSON output
The `knowledge view`, `knowledge views`, `knowledge search`, and `knowledge concept` CLI commands SHALL use `dataclasses.asdict()` to construct their JSON output dicts instead of manually listing each field.

#### Scenario: knowledge view outputs all ViewResult fields automatically
- **WHEN** `dm2 knowledge view OV-2 --json` is called
- **THEN** the response SHALL contain every field defined in the `ViewResult` dataclass
- **AND** the field values SHALL be identical to the current manual dict construction

#### Scenario: knowledge views outputs filtered summary fields
- **WHEN** `dm2 knowledge views --json` is called
- **THEN** each view entry SHALL include `view_id`, `view_name`, `viewpoint`, `description`, `dependencies`
- **AND** dataclass-internal fields SHALL NOT appear (no `dm2_groups`, `priority`, `required_data`, `downstream`, `standard_name`, etc.)

#### Scenario: knowledge search outputs all KnowledgeSearchResult fields
- **WHEN** `dm2 knowledge search "resource" --json` is called
- **THEN** each result SHALL contain every field defined in `KnowledgeSearchResult`
- **AND** existing fields (`term`, `definition`, `aliases`, `groups`) SHALL retain current values

#### Scenario: knowledge concept outputs all ConceptResult fields
- **WHEN** `dm2 knowledge concept "Activity" --json` is called
- **THEN** the response SHALL contain every field defined in `ConceptResult`
- **AND** existing fields (`name`, `dm2_type`, `layer`, `subtype`, `definition`, `relationships`, `tags`, `synonyms`) SHALL retain current values

#### Scenario: New dataclass field auto-appears in CLI output
- **WHEN** a new field is added to `ViewResult` dataclass
- **THEN** `dm2 knowledge view <id> --json` SHALL include the new field automatically
- **AND** no manual update to `knowledge.py` SHALL be required for the field to appear
