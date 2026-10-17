# Spec Delta

## Purpose

InstructionBuilder generates DoDAF compliance rules and template sections dynamically from view metadata, and honours the project's diagram-output configuration.

## MODIFIED Requirements

### Requirement: InstructionBuilder generates template sections from metadata
The `InstructionBuilder` SHALL use the view's `sections` field as the primary source for the instruction template's section outline, replacing the hardcoded generic sections.

#### Scenario: View-specific sections used in template
- **WHEN** `build_view_instructions` is called for OV-3 with `sections: [资源流矩阵, 交换属性分析, 关键资源流识别, 与 OV-2 一致性说明]`
- **THEN** `template.sections` SHALL equal the sections from views.yaml exactly
- **AND** the generic "## Mermaid 图表" section SHALL NOT be present (OV-3 has `representation: table`)

#### Scenario: Mermaid section injected for diagram views only
- **WHEN** `build_view_instructions` is called for OV-6b with `representation: state-diagram`
- **THEN** `template.sections` SHALL include a Mermaid diagram section with `stateDiagram-v2` syntax hint

#### Scenario: Inline Mermaid suppressed by configuration
- **WHEN** the project config sets `views.include_mermaid: false`
- **AND** `build_view_instructions` is called for a view whose `representation` maps to a Mermaid type
- **THEN** `template.sections` SHALL NOT contain a "## Mermaid 图表" section
- **AND** the view's own `sections` SHALL otherwise be unchanged

#### Scenario: External figure channel under svg diagram output
- **WHEN** the project config sets `views.diagram_output: svg`
- **AND** `build_view_instructions` is called for a view whose `representation` maps to a Mermaid type
- **THEN** `template.sections` SHALL contain a section naming an independent SVG file for that view
- **AND** `template.sections` SHALL NOT contain a Mermaid section
- **AND** `rules` SHALL state that diagram content is drawn as standalone SVG rather than inline Mermaid

#### Scenario: Unknown diagram_output falls back to Mermaid
- **WHEN** the project config sets `views.diagram_output` to a value other than `mermaid` or `svg`
- **THEN** the builder SHALL behave as if the value were `mermaid`

#### Scenario: Diagram output ignored for diagram-free views
- **WHEN** `views.diagram_output: svg` and `build_view_instructions` is called for a view with `representation: table`
- **THEN** `template.sections` SHALL contain neither a Mermaid section nor a figure section
