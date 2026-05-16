## ADDED Requirements

### Requirement: Batch archive architecture changes
The system SHALL provide a Claude Code skill (`dm2-bulk-archive`) that archives multiple architecture changes in a single operation, detecting and resolving view conflicts, following openspec's "bulk-archive" pattern.

#### Scenario: Select changes to archive
- **WHEN** user invokes `/dm2:bulk-archive`
- **THEN** the AI Agent SHALL run `dm2 change list-changes --json` to get active changes
- **AND** SHALL present changes with their status for user multi-select

#### Scenario: Validate each change before archive
- **WHEN** changes are selected
- **THEN** the AI Agent SHALL run `dm2 change status --json` for each selected change
- **AND** SHALL check view state for each change (which views are generated vs pending)
- **AND** SHALL display a summary table showing artifact status, view counts, and any warnings

#### Scenario: Detect view conflicts across changes
- **WHEN** multiple changes reference the same view type (e.g., both generate OV-2)
- **THEN** the AI Agent SHALL flag this as a conflict
- **AND** SHALL display which changes conflict on which views

#### Scenario: Execute archive
- **WHEN** user confirms the batch operation
- **THEN** the AI Agent SHALL run `dm2 change archive-change <name>` for each selected change
- **AND** SHALL track success/failure for each
- **AND** SHALL display a summary of archived, skipped, and failed changes

#### Scenario: No active changes
- **WHEN** no active changes exist
- **THEN** the AI Agent SHALL report "No active changes to archive"
