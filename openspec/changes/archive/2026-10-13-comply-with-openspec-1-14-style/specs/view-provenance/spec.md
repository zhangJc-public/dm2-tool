# view-provenance (delta)

This delta only moves enumerations, tables and examples out of requirement
prose into scenarios so each requirement states one behaviour. No normative
content is added or removed; the OpenSpec 1.14 strict style rule requires the
requirement text itself to stay under 500 characters.

## MODIFIED Requirements

### Requirement: Pedigree data model
The system SHALL define a `Pedigree` data model in `dm2.core.pedigree.model` capturing the origin, history, source and confidence of every view generation event, as a YAML-serializable dataclass. The required and optional fields, their types and their enums are fixed as tabulated.

#### Scenario: Pedigree record is serializable to YAML
- **WHEN** a Pedigree object is created
- **THEN** it SHALL round-trip through `yaml.dump` and `yaml.load` without loss
- **AND** all required fields SHALL be present after round-trip

#### Scenario: Pedigree validates on construction
- **WHEN** a Pedigree object is constructed with missing required fields
- **THEN** the constructor SHALL raise a validation error identifying the missing field
- **AND** the error message SHALL include the field name and view_id

#### Scenario: The pedigree fields are fixed
- **THEN** the model SHALL carry:

- `view_id` (string, required): the DoDAF view identifier (e.g. "OV-1", "CV-1")
- `pedigree_id` (string, required): a UUID generated at first record creation
- `author` (object, required): `type` (enum: human, agent-assisted, agent-autonomous), `model` (string, model version when AI Agent), `operator` (string, triggering human user)
- `creation_date` (ISO-8601 datetime, required)
- `modification_history` (array of ModificationRecord, required): each entry has `date`, `actor`, `change_description`
- `source` (object, required): `standard` (e.g. "DoDAF V2.02 Vol 2"), `section`, `dm2_terms_used` (array of `{term, definition_ref}`), `alignment_notes` (free text)
- `reasoning` (object, required): `summary` (string), `decision_factors` (array of `{factor, score?, source}`), `alternatives_considered` (array of `{option, rejected_because}`)
- `validation` (object, required): `ran_R1`-`ran_R5` (booleans), `issues` (array of `{rule, severity, message, suggested_fix?}`), `last_validated` (ISO-8601 datetime or null)
- `reliability` (enum: low, medium, high, required)
- `confidence` (number 0-1, required)
- `known_limitations` (array of strings, optional)
