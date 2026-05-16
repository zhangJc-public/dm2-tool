## Concern Template Library Spec

### Purpose
Define architecture concern templates as external reference data that enable the AI Agent to match user descriptions against domain-specific architecture focus areas.

### Requirements

### Requirement: Concern template library
The system SHALL provide an external YAML file at `dm2-reference/concerns.yaml` defining architecture concern patterns. Each concern SHALL specify expected data group activation patterns, core views, and domain keywords.

#### Scenario: Concerns YAML has required structure
- **WHEN** concerns.yaml is loaded
- **THEN** each concern entry SHALL include `id`, `name`, `description`, `expected_groups`, `core_views`, and `keywords`
- **AND** `expected_groups` SHALL reference valid DM2 data group IDs
- **AND** `core_views` SHALL reference valid DoDAF view IDs

#### Scenario: CLI lists concerns
- **WHEN** `dm2 concern list --json` is run
- **THEN** the output SHALL include all concerns with their id, name, description, expected_groups, and core_views
- **AND** the output SHALL be valid JSON with status "success"

#### Scenario: CLI filters concern by keyword
- **WHEN** `dm2 concern list --json --query "auth"` is run
- **THEN** the output SHALL include only concerns whose keywords or name match the query

### Requirement: Data group template keywords expanded
All 17 data group template `keywords` arrays SHALL be reviewed and expanded to include domain-specific architecture terms beyond generic concept words. This ensures activation signals have sufficient differentiation for concern matching.

#### Scenario: Keywords include domain terms
- **WHEN** the data group activator loads any template keywords
- **THEN** each group's keywords SHALL include at least 3 domain-specific terms (e.g., "认证", "防火墙", "加密") alongside general concept words
- **AND** keywords with domain specificity SHALL distinguish between groups that would otherwise only activate on generic words like "系统" or "数据"

#### Scenario: Activation signals are differentiated
- **WHEN** `dm2 analyze -d "身份认证和访问控制系统，MFA+SSO" --json` is run
- **THEN** at least 3 data groups SHALL have non-zero activation scores
- **AND** the activated groups SHALL include groups relevant to authentication/authorization (08-services, 05-guidance, 10-rules)
