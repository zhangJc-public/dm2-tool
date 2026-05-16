## ADDED Requirements

### Requirement: instructions command provides AI Agent with DM2 knowledge
The `dm2 instructions` command SHALL return structured JSON containing all information an AI Agent needs to generate DoDAF-compliant content: DM2 term definitions, compliance rules, output template structure, and output path.

#### Scenario: View instructions include DM2 terms
- **WHEN** `dm2 instructions view/OV-1 -d "system description" --json` is run
- **THEN** the response SHALL include `context.dm2_terms` with relevant DM2 term definitions
- **AND** SHALL include `rules` with DoDAF compliance rules for the specific view
- **AND** SHALL include `template.sections` with the expected output structure
- **AND** SHALL include `output_path` specifying where to write the generated file

#### Scenario: Step instructions include output sections
- **WHEN** `dm2 instructions step/step1-intent-scope -d "system description" --json` is run
- **THEN** the response SHALL include `template.sections` with all required step sections
- **AND** SHALL include `output_path` pointing to the step output location

### Requirement: VIEW_RULES is the single source for DoDAF compliance rules
The `VIEW_RULES` dictionary in `src/dm2/core/agent/instructions.py` SHALL be the single source of per-view DoDAF compliance rules, used by both the CLI `generate` command and the `InstructionBuilder`.

#### Scenario: generate command uses VIEW_RULES
- **WHEN** `dm2 generate OV-1 -d "..."` runs
- **THEN** the output SHALL include `rules` from the `VIEW_RULES["OV-1"]` entry

#### Scenario: instructions command uses VIEW_RULES
- **WHEN** `dm2 instructions view/OV-1 -d "..." --json` runs
- **THEN** the output SHALL include `rules` from the `VIEW_RULES["OV-1"]` entry

### Requirement: AI Agent skills define interaction protocol, not implementation
The `.claude/skills/dm2-*.md` files SHALL define how AI Agents interact with dm2 through CLI `--json` commands, without importing or depending on dm2's internal Python modules.

#### Scenario: dm2-ff-workflow uses CLI commands only
- **WHEN** the `dm2-ff-workflow` skill is executed by an AI Agent
- **THEN** all interactions with dm2 SHALL be via `python3 -m dm2.cli.main <command> --json`
- **AND** no Python import of dm2 internal modules SHALL be required
