# dm2-architecture-boundaries Specification

## Purpose
Define dm2's internal structure as enforceable invariants: five ordered package levels whose
dependencies point only downward (`utils` is a leaf, nothing imports `cli`), and the boundary
that dm2 produces state, instructions, and validation results rather than architecture content.
`test/test_architecture_boundaries.py` guards the dependency rule.

## Requirements

### Requirement: dm2 packages depend only downward
Every module under `src/dm2/` SHALL belong to one of five ordered dependency levels, and SHALL
import only modules at the same level or a lower one:

| Level | Packages |
|---|---|
| L0（叶子） | `utils` |
| L1 | `config`, `kernel` |
| L2 | `cognitive`, `reasoning`, `core` |
| L3 | `engine` |
| L4（入口） | `cli` |

This ordering is the package-level view of the four-layer model described in
`docs/foundation.md`; the layer names there are conceptual, the levels here are what the
architecture test enforces.

#### Scenario: No upward import exists
- **WHEN** the imports of every module under `src/dm2/` are scanned and mapped to levels
- **THEN** no module SHALL import a module from a higher level
- **AND** in particular `kernel` SHALL NOT import `core`, `engine`, or `cli`
- **AND** `core` SHALL NOT import `engine` or `cli`
- **AND** `cognitive` and `reasoning` SHALL NOT import `core`, `engine`, or `cli`
- **AND** `config` SHALL NOT import `cli` or `engine`
- **AND** no package SHALL import `cli`

#### Scenario: `utils` remains a leaf
- **WHEN** the imports of every module under `src/dm2/utils/` are scanned
- **THEN** none of them SHALL import another `dm2` subpackage

#### Scenario: A new module is placed at a valid level
- **WHEN** a new module is added under `src/dm2/`
- **THEN** its imports SHALL satisfy the level rule for the package it lives in
- **AND** a violation SHALL fail the architecture test rather than be waived

### Requirement: dm2 does not generate architecture content
dm2 SHALL produce state, structured instructions, and validation results, and SHALL NOT generate
DoDAF view content itself; content generation belongs to the AI Agent.

#### Scenario: Generation commands emit instructions, not content
- **WHEN** `dm2 generate` or `dm2 instructions` runs
- **THEN** its output SHALL be structured metadata and instructions addressed to an AI Agent
- **AND** it SHALL NOT contain rendered view content

#### Scenario: The agent-driven pipeline advances only on an agent acknowledgement
- **WHEN** `dm2 run --agent` initializes a pipeline
- **THEN** it SHALL return the current step's instructions and wait
- **AND** the pipeline SHALL advance only when the agent reports a step complete
