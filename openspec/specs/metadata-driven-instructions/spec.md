## Purpose

InstructionBuilder generates DoDAF compliance rules and template sections dynamically from view metadata, eliminating hardcoded VIEW_RULES.

## Requirements

### Requirement: InstructionBuilder generates rules from view metadata
The `InstructionBuilder.build_view_instructions()` method SHALL generate DoDAF compliance rules dynamically from the view's metadata fields, prioritizing metadata over hardcoded rules.

#### Scenario: Representation rule generated for diagram view
- **WHEN** `build_view_instructions` is called for a view with `representation: node-link`
- **THEN** the returned `rules` SHALL include "该视图必须以节点-连接图 (node-link diagram) 形式呈现"
- **AND** the rule SHALL be generated from the `representation` field, not hardcoded

#### Scenario: Model category rule generated
- **WHEN** `build_view_instructions` is called for a view with `model_category: Behavioral`
- **THEN** the returned `rules` SHALL include a rule identifying the view as a Behavioral model describing dynamic process aspects

#### Scenario: Required field rules generated
- **WHEN** `build_view_instructions` is called for a view with `required_fields: [源活动, 目标活动, 资源类型]`
- **THEN** the returned `rules` SHALL include "必须包含: 源活动"
- **AND** the rules SHALL include "必须包含: 目标活动"
- **AND** the rules SHALL include "必须包含: 资源类型"

### Requirement: InstructionBuilder generates template sections from metadata
The `InstructionBuilder` SHALL use the view's `sections` field as the primary source for the instruction template's section outline, replacing the hardcoded generic sections.

#### Scenario: View-specific sections used in template
- **WHEN** `build_view_instructions` is called for OV-3 with `sections: [资源流矩阵, 交换属性分析, 关键资源流识别, 与 OV-2 一致性说明]`
- **THEN** `template.sections` SHALL equal the sections from views.yaml exactly
- **AND** the generic "## Mermaid 图表" section SHALL NOT be present (OV-3 has `representation: table`)

#### Scenario: Mermaid section injected for diagram views only
- **WHEN** `build_view_instructions` is called for OV-6b with `representation: state-diagram`
- **THEN** `template.sections` SHALL include a Mermaid diagram section with `stateDiagram-v2` syntax hint

### Requirement: Fallback to hardcoded rules when metadata missing
When a view lacks the new metadata fields (e.g., loaded from an unenhanced views.yaml), the InstructionBuilder SHALL fall back to the existing VIEW_RULES hardcoded dictionary and generic template.

#### Scenario: Old-format view uses hardcoded rules
- **WHEN** `build_view_instructions` is called for OV-2
- **AND** the view's `representation` field is `None` or absent
- **THEN** the returned `rules` SHALL use the existing VIEW_RULES["OV-2"] hardcoded entries
- **AND** the returned `template.sections` SHALL use the generic `["## 概述", ...]` fallback

### Requirement: Knowledge API exposes new metadata fields
The `KnowledgeAPI.get_view()` method and `knowledge view <id> --json` command SHALL include the new metadata fields in the response.

#### Scenario: knowledge view output includes new fields
- **WHEN** `dm2 knowledge view OV-2 --json` is called
- **THEN** the response SHALL include `standard_name`, `model_category`, `representation`, `purpose`, `sections`, `required_fields` in the data object
- **AND** all existing fields (view_name, viewpoint, dependencies, etc.) SHALL still be present with unchanged values
