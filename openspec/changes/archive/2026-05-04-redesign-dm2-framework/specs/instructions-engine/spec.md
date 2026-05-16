## ADDED Requirements

### Requirement: Generate instructions for artifact types
The system SHALL provide an `dm2 instructions <artifact-type> --change <name> --json` command that returns a structured JSON object containing all information an AI agent needs to generate the artifact: context, rules, template, output path, and dependency artifacts.

#### Scenario: AI agent requests view generation instructions
- **WHEN** `dm2 instructions OV-2 --change "security-audit" --json` is executed
- **THEN** the response SHALL include DM2 context (related terms, concepts), DoDAF rules for OV-2 generation, a section template, and paths to completed dependency views

### Requirement: Context injection from DM2 knowledge base
The instructions' `context` field SHALL include: relevant DM2 term definitions, related DM2 concepts with their relationships, the project description, and the content of all completed dependency artifacts.

#### Scenario: Context includes DM2 terminology
- **WHEN** generating instructions for OV-2 (resource flow)
- **THEN** the context SHALL include DM2 definitions for "ResourceFlow", "Activity", and "Performer" terms, plus content from completed OV-1

### Requirement: Rules injection from DoDAF standards
The instructions' `rules` field SHALL include DoDAF compliance rules specific to the artifact type, derived from the DM2 specification. Rules SHALL be imperative constraints (e.g., "视图必须包含图形化描述") not suggestions.

#### Scenario: Rules are artifact-specific
- **WHEN** generating instructions for OV-1
- **THEN** the rules SHALL include requirements about graphical depiction, system boundary clarity, and operational node labeling

### Requirement: Template with required sections
The instructions' `template` field SHALL provide a structured outline of required sections and fields for the artifact, derived from the DM2 view definition in views.yaml.

#### Scenario: Template guides artifact structure
- **WHEN** an AI agent receives instructions for SV-4
- **THEN** the template SHALL specify required sections (功能分解, 功能描述, 功能关系) and required metadata fields (view_id, view_name, generated_at)

### Requirement: Context and rules are not written to artifacts
The `context` and `rules` fields in the instructions JSON SHALL be used solely as AI agent constraints during generation. They SHALL NOT appear in the generated artifact file. This matches the OpenSpec principle of separating constraints from output.

#### Scenario: Generated artifact is clean
- **WHEN** an AI agent generates OV-2.md using instructions
- **THEN** the output file SHALL NOT contain DM2 term definitions, DoDAF compliance rules, or other instruction-level content not belonging to the view itself
