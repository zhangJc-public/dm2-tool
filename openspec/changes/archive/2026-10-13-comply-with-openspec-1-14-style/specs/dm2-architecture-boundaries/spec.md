# dm2-architecture-boundaries (delta)

This delta only moves enumerations, tables and examples out of requirement
prose into scenarios so each requirement states one behaviour. No normative
content is added or removed; the OpenSpec 1.14 strict style rule requires the
requirement text itself to stay under 500 characters.

## MODIFIED Requirements

### Requirement: dm2 packages depend only downward
Every module under `src/dm2/` SHALL belong to one of five ordered dependency levels and SHALL import only modules at the same level or a lower one. The levels are the enforceable form of the four-layer model in `docs/foundation.md`; that document's layer names are conceptual, the levels here are what the architecture test enforces.

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

#### Scenario: The five levels are fixed
- **THEN** L0 SHALL be `utils`; L1 `config`, `kernel`; L2 `cognitive`, `reasoning`, `core`; L3 `engine`; L4 `cli`
- **AND** an import SHALL be allowed only when the target level is lower than or equal to the source level
