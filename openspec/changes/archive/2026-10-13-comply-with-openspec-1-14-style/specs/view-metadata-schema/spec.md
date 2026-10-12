# view-metadata-schema (delta)

This delta only moves enumerations, tables and examples out of requirement
prose into scenarios so each requirement states one behaviour. No normative
content is added or removed; the OpenSpec 1.14 strict style rule requires the
requirement text itself to stay under 500 characters.

## MODIFIED Requirements

### Requirement: View definition includes pedigree metadata
Each generated view file (Markdown) SHALL include a `pedigree` block in its YAML frontmatter carrying the minimum information needed to identify the view's provenance and follow the full trace. The block's required fields and their shapes are fixed as tabulated.

#### Scenario: Generated view includes pedigree frontmatter
- **WHEN** a view is written to the output path
- **THEN** the file's frontmatter SHALL include a `pedigree:` section
- **AND** the section SHALL contain all four required sub-fields

#### Scenario: Pedigree frontmatter is parseable
- **WHEN** a view file is loaded by the indexer
- **THEN** the `pedigree` field SHALL parse as a YAML mapping
- **AND** the `dm2_terms_used` array SHALL be accessible programmatically

#### Scenario: Missing pedigree field is reported
- **WHEN** a view file lacks a `pedigree` block in frontmatter
- **THEN** the indexer SHALL mark the view as having `pedigree_status: absent`
- **AND** the ViewManager SHALL list the view in trace gaps

#### Scenario: Pedigree_id is unique per view
- **WHEN** multiple views exist in the project
- **THEN** each view's `pedigree.pedigree_id` SHALL be unique
- **AND** SHALL match the corresponding full record in `.dm2/pedigree/<view_id>.yaml`

#### Scenario: The pedigree frontmatter fields are fixed
- **THEN** the block SHALL contain:

- `pedigree_id` (string, required): UUID linking to the full record at `.dm2/pedigree/<view_id>.yaml`
- `author` (object, required): subset of the full record — `type`, `model` (when AI Agent), `operator`
- `creation_date` (ISO-8601 datetime, required)
- `source` (object, required): reference subset — `standard`, `section`, `dm2_terms_used` (array of `{term, definition_ref}`)
