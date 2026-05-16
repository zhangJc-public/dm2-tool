## ADDED Requirements

### Requirement: Init provisions local reference knowledge base
The `dm2 init` command SHALL copy the DM2 reference knowledge base (views.yaml, _dm2_v202_extract.json, group-to-views.yaml, and 17 data group templates) into `.dm2/reference/` when creating a project, making the project self-contained.

#### Scenario: Reference files present after init
- **WHEN** `dm2 init <project-name>` completes successfully
- **THEN** `.dm2/reference/views.yaml` SHALL exist with all 52 view definitions
- **AND** `.dm2/reference/_dm2_v202_extract.json` SHALL exist with ~277 DM2 terms
- **AND** `.dm2/reference/group-to-views.yaml` SHALL exist with data group to view mappings
- **AND** `.dm2/reference/groups/` SHALL contain 17 data group subdirectories with templates

#### Scenario: Existing reference not overwritten on re-init
- **WHEN** `dm2 init` is run in a directory that already has `.dm2/reference/`
- **THEN** the command SHALL NOT overwrite the existing reference files
- **AND** the project SHALL continue to use its existing local reference data

### Requirement: Reference path resolution prefers project-local
The `get_reference_path()` function SHALL check for a project-local `.dm2/reference/` directory first, falling back to the built-in package `dm2-reference/core/` if no project-local copy exists.

#### Scenario: Project-local reference used when present
- **WHEN** a dm2 command runs within a project that has `.dm2/reference/`
- **THEN** `get_reference_path()` SHALL return the project-local `.dm2/reference/` path
- **AND** all knowledge loading (terms, concepts, views, groups) SHALL use the project-local data

#### Scenario: Package reference used as fallback
- **WHEN** a dm2 command runs outside a dm2 project, or within a project without `.dm2/reference/`
- **THEN** `get_reference_path()` SHALL return the built-in package `dm2-reference/core/` path
- **AND** commands SHALL function identically to before this change
