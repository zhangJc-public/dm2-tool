## DM2 Generate No-LLM Spec

### Purpose
Ensure `dm2 generate` operates as a pure CLI tool without LLM dependency. It outputs structured metadata and AI Agent instructions rather than generating view content via LLM.

### Requirements

### Requirement: No LLM dependency for view generation
The `dm2 generate` command SHALL NOT require or call any LLM API. It SHALL output structured metadata and instructions for AI Agent consumption, not generated view content.

#### Scenario: Generate without API key
- **WHEN** user runs `dm2 generate <view> -d "..."` without configuring any LLM API key
- **THEN** the command SHALL succeed without errors
- **AND** SHALL output structured JSON/YAML containing view metadata, 6W analysis, data group activation, and AI Agent instructions

#### Scenario: Output includes AI Agent instructions
- **WHEN** `dm2 generate` completes successfully
- **THEN** the output SHALL include an `instruction` field with text directing an AI Agent to generate the view content
- **AND** SHALL include `six_w_analysis`, `data_group_activation`, `rules`, and `required_data` fields

#### Scenario: Removed --no-rag parameter
- **WHEN** user runs `dm2 generate --no-rag`
- **THEN** the command SHALL fail with an error indicating the parameter is no longer available

### Requirement: View template lookup via indexer
The `dm2 generate` command SHALL use the DM2 knowledge indexer to locate view template information.

#### Scenario: View found in index
- **WHEN** user runs `dm2 generate <known-view-id> -d "..."`
- **THEN** the command SHALL retrieve the view template from the DM2 indexer
- **AND** SHALL include the view's dm2_groups in the structured output

#### Scenario: View not found
- **WHEN** user runs `dm2 generate <unknown-view-id> -d "..."`
- **THEN** the command SHALL output an error indicating the view was not found
