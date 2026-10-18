# Spec Delta

## Purpose

Validation reports activity-performer and resource-flow defects from what a view actually states, not from syntax fragments.

## ADDED Requirements

### Requirement: Activity performer binding is checked within OV-5b
Validation SHALL report an activity that OV-5b declares without a stated performer, recognising activities by identifier in both the Mermaid node labels and the activity table, and SHALL NOT require OV-5a decomposition leaves to appear in OV-5b.

#### Scenario: Activity in the table with a performer
- **WHEN** the OV-5b activity table has a row for `A1` whose performer column names a performer
- **THEN** validation SHALL NOT report `A1` as an unbound activity

#### Scenario: Activity in the table with an empty performer
- **WHEN** the OV-5b activity table has a row for `A1` whose performer column is empty
- **THEN** validation SHALL report an `unbound_activity` error naming `A1`

#### Scenario: Activity in a Mermaid label with an empty performer
- **WHEN** an OV-5b node label reads `执行者：<br/>` and names no performer
- **THEN** validation SHALL report that activity as unbound

#### Scenario: OV-5a decomposes deeper than OV-5b tracks
- **WHEN** OV-5a contains `A1.1` and OV-5b tracks only `A1`
- **THEN** validation SHALL NOT report `A1.1` as unbound

#### Scenario: Mermaid node identifiers are not activities
- **WHEN** an OV-5b line reads `X --> A53["A5.3 双人确认"]`
- **THEN** the activity SHALL be reported by its identifier `A5.3`, never as `A53`

### Requirement: Resource extraction ignores the view title
Resource extraction SHALL ignore level-1 headings, so a bilingual view title containing the English word "Resource" is not reported as an orphan resource.

#### Scenario: Bilingual title with the word Resource
- **WHEN** OV-2 starts with `# OV-2 作战资源流描述（Operational Resource Flow Description）`
- **THEN** validation SHALL NOT report an `orphan_resource` issue for that title

#### Scenario: A section heading still yields resources
- **WHEN** OV-2 contains a level-2 heading naming resources followed by a list item
- **THEN** validation SHALL extract the resource and report it as orphaned when nothing produces or consumes it
