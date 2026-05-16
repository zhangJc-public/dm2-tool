## MODIFIED Requirements

### Requirement: InstructionBuilder benefits from aligned group names
With aligned group names, `InstructionBuilder.build_view_instructions()` SHALL retrieve DM2 terms through `search_terms(group)` that match the group field in `_dm2_v202_extract.json` via substring matching, providing more relevant context to the AI Agent even when DM2 term group names use prefixes (e.g., "DM2 Foundation").

#### Scenario: search_terms finds terms by matched group name
- **WHEN** InstructionBuilder searches for group `"ResourceFlow"` when building instructions for SV-4
- **THEN** the search SHALL return DM2 terms whose group field is `"Resource Flow"` (the DM2 term JSON uses space-separated naming)
- **AND** the number of matched terms SHALL be ≥ 5

#### Scenario: search_terms matches prefixed group names via substring
- **WHEN** InstructionBuilder searches for group `"Foundation"` when building instructions for AV-2, CV-1, or DIV-1
- **THEN** the search SHALL return DM2 terms whose group field contains `"Foundation"` as a substring (e.g., "DM2 Foundation", "IDEAS Foundation")
- **AND** the number of matched terms SHALL be ≥ 5
