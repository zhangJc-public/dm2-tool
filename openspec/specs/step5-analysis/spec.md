# Step 5: Analysis

## Purpose

分析执行（SE 四算子），整合溯因推理、OODA 韧性分析、TOC 瓶颈识别和一致性检查。

<!-- TBD: 详细架构文档。 -->

## Requirements

### Requirement: Abductive reasoning for architecture completion
The system SHALL apply abductive reasoning to infer missing relationships and entities in the architecture based on observed patterns and DM2 association rules. Every inference SHALL name the architecture entities it concerns.

#### Scenario: Missing relationship is inferred
- **WHEN** an Activity exists without a linked Performer
- **THEN** the system SHALL flag the gap and suggest possible Performer types based on the Activity's characteristics

#### Scenario: An inference names its entities
- **WHEN** the system reports an inference
- **THEN** the inference SHALL identify the entities the missing relationship would connect
- **AND** SHALL NOT report an unnamed placeholder in place of an entity

#### Scenario: An inference explains itself
- **WHEN** the system reports an inference
- **THEN** it SHALL state the observed pattern that led to it and a confidence value

### Requirement: OODA resilience analysis
The system SHALL apply OODA loop analysis (Observe/Orient/Decide/Act) to assess the architecture's ability to respond to changes, threats, or disruptions.

#### Scenario: Architecture resilience is assessed
- **WHEN** Step 5 runs on a completed data set
- **THEN** the system SHALL identify OODA breakpoints where decision cycles are blocked by missing information or circular dependencies

### Requirement: TOC bottleneck identification
The system SHALL apply Theory of Constraints analysis to identify the primary bottleneck (约束瓶颈) in the architecture that limits overall system effectiveness.

#### Scenario: Bottleneck is identified
- **WHEN** the architecture involves a chain of activities with resource flows
- **THEN** the system SHALL identify the single most constraining node and quantify its impact

#### Scenario: Bottleneck degrees are derived from the architecture
- **WHEN** a bottleneck is reported
- **THEN** its inbound and outbound degree counts SHALL be derived from the architecture under analysis
- **AND** SHALL NOT be fixed values that are the same for every architecture

### Requirement: Consistency validation
The system SHALL run DM2 consistency checks across all architecture data, validating Activity-Performer bindings, resource flow completeness, capability mapping coverage, and circular dependency detection.

#### Scenario: Consistency issues are reported
- **WHEN** consistency checks find violations
- **THEN** each violation SHALL be reported with severity, affected entities, and suggested resolution

#### Scenario: Circular dependency is detected
- **WHEN** the architecture declares prerequisite or successor relationships that form a cycle
- **THEN** the checks SHALL report a circular-dependency violation naming the nodes on the cycle
- **AND** the violation SHALL be reported with ERROR severity

#### Scenario: Acyclic prerequisites are not reported
- **WHEN** the declared prerequisite relationships form no cycle
- **THEN** no circular-dependency violation SHALL be reported

### Requirement: Analysis output
Step 5 SHALL produce an analysis report containing: abductive inferences, OODA breakpoints, TOC bottleneck, consistency violations, and suggested architecture improvements.

#### Scenario: Analysis report is produced
- **WHEN** Step 5 completes
- **THEN** `.dm2/steps/step5-analysis.md` SHALL contain all analysis sections
