# View Provenance

## Purpose
Record and retrieve the provenance of AI Agent-generated DoDAF views to support engineering
audit: the facts dm2 observes itself are kept distinct from the reasoning the external AI Agent
states. Implements the DM2 V2.02 **Pedigree** data group as a first-class artifact within the
dm2 project lifecycle.

## ADDED Requirements

### Requirement: Pedigree data model
The system SHALL define a `Pedigree` data model in `dm2.core.pedigree.model` that captures the origin, history, source, and confidence of every view generation event. The model SHALL be a YAML-serializable Pydantic/dataclass structure with the following fields:

- `view_id` (string, required): The DoDAF view identifier (e.g., "OV-1", "CV-1")
- `pedigree_id` (string, required): A UUID generated at first record creation
- `author` (object, required): Who created the view — fields `type` (enum: human, agent-assisted, agent-autonomous), `model` (string, model version when AI Agent), `operator` (string, triggering human user)
- `creation_date` (ISO-8601 datetime, required)
- `modification_history` (array of ModificationRecord, required): Each entry has `date`, `actor`, `change_description`
- `source` (object, required): Standard provenance — fields `standard` (e.g., "DoDAF V2.02 Vol 2"), `section`, `dm2_terms_used` (array of `{term, definition_ref}`), `alignment_notes` (free text)
- `reasoning` (object, required): The Agent's stated rationale — fields `summary` (string), `decision_factors` (array of `{factor, score?, source}`), `alternatives_considered` (array of `{option, rejected_because}`)
- `validation` (object, required): Validation history — fields `ran_R1`-`ran_R5` (booleans), `issues` (array of `{rule, severity, message, suggested_fix?}`), `last_validated` (ISO-8601 datetime or null)
- `reliability` (enum: low, medium, high, required)
- `confidence` (number 0-1, required)
- `known_limitations` (array of strings, optional)

#### Scenario: Pedigree record is serializable to YAML
- **WHEN** a Pedigree object is created
- **THEN** it SHALL round-trip through `yaml.dump` and `yaml.load` without loss
- **AND** all required fields SHALL be present after round-trip

#### Scenario: Pedigree validates on construction
- **WHEN** a Pedigree object is constructed with missing required fields
- **THEN** the constructor SHALL raise a validation error identifying the missing field
- **AND** the error message SHALL include the field name and view_id

### Requirement: Pedigree storage layout
The system SHALL store pedigree records at `.dm2/pedigree/<view_id>.yaml` within the dm2 project. The directory SHALL be created on `dm2 init`.

#### Scenario: Pedigree directory created on init
- **WHEN** user runs `dm2 init`
- **THEN** the system SHALL create `.dm2/pedigree/` directory
- **AND** the directory SHALL be added to `.dm2/.gitignore` patterns (or documented as committed)

#### Scenario: Read existing pedigree
- **WHEN** `PedigreeStore.load(view_id)` is called
- **THEN** the system SHALL load `.dm2/pedigree/<view_id>.yaml` if it exists
- **AND** SHALL return `None` if the file does not exist

#### Scenario: Write pedigree
- **WHEN** `PedigreeStore.save(pedigree)` is called
- **THEN** the system SHALL write the pedigree to `.dm2/pedigree/<view_id>.yaml`
- **AND** the write SHALL be atomic (write-to-temp-then-rename)
- **AND** the file SHALL be readable YAML

### Requirement: View frontmatter pedigree field
Generated view files (Markdown) SHALL include a `pedigree` block in their YAML frontmatter containing the minimal traceability fields needed to follow the full trace. The frontmatter pedigree SHALL contain:

- `pedigree_id` (string): Reference to full record in `.dm2/pedigree/<view_id>.yaml`
- `author` (object): Same as full record
- `creation_date` (ISO-8601 datetime)
- `source` (object): Reference fields only (standard + section + dm2_terms_used)

#### Scenario: View frontmatter contains pedigree block
- **WHEN** a view file is written by the agent-driven generation pipeline
- **THEN** the frontmatter SHALL include a `pedigree:` section
- **AND** the `pedigree.pedigree_id` SHALL match the full record in `.dm2/pedigree/<view_id>.yaml`
- **AND** the frontmatter pedigree SHALL be parseable as YAML

#### Scenario: Frontmatter pedigree is human-readable
- **WHEN** a human opens a view file
- **THEN** the `pedigree:` block SHALL be visible in the frontmatter
- **AND** SHALL contain enough information to understand the view's origin without reading the external YAML

### Requirement: Automatic fact capture by CLI
The system SHALL automatically record certain objective facts about view operations as pedigree entries, without requiring the AI Agent to declare them.

#### Scenario: View registration captured
- **WHEN** `dm2 view register <view_id>` is called
- **THEN** the system SHALL append a `ModificationRecord` to the pedigree with `actor=cli`, `change_description="view registered"`
- **AND** the `creation_date` SHALL be set to the current time if not previously set

#### Scenario: Analyze invocation captured
- **WHEN** `dm2 analyze --json -d "<description>"` is called
- **THEN** the system SHALL NOT write to pedigree (analyze is a query, not a view operation)

#### Scenario: Validation results captured
- **WHEN** `dm2 validate <view_id>` runs and completes
- **THEN** the system SHALL update the pedigree's `validation` field with the latest issues array
- **AND** SHALL set `validation.ran_R1`-`ran_R5` booleans based on which rules actually ran
- **AND** SHALL set `validation.last_validated` to the current time

#### Scenario: State transition captured
- **WHEN** a view's lifecycle state changes (pending → in_progress → generated → verified)
- **THEN** the system SHALL append a `ModificationRecord` to the pedigree
- **AND** the record SHALL include the new state in `change_description`

### Requirement: Agent-supplied reasoning fields
The system SHALL expose a CLI command `dm2 trace record` that the AI Agent (via skill instructions) can call to submit the agent-side reasoning fields (`reasoning.summary`, `reasoning.decision_factors`, `reasoning.alternatives_considered`, `known_limitations`).

#### Scenario: Basic trace record command
- **WHEN** user or AI Agent runs `dm2 trace record <view_id> --summary "..." --reasoning-file <yaml-path>`
- **THEN** the system SHALL load the existing pedigree for `<view_id>`
- **AND** SHALL merge the supplied reasoning fields into the pedigree
- **AND** SHALL save the merged pedigree to `.dm2/pedigree/<view_id>.yaml`

#### Scenario: Reasoning provided via stdin
- **WHEN** user or AI Agent runs `echo '<yaml>' | dm2 trace record <view_id> --stdin`
- **THEN** the system SHALL parse YAML from stdin
- **AND** SHALL merge the parsed fields into the existing pedigree
- **AND** SHALL save the merged pedigree

#### Scenario: Decision factors structured format
- **WHEN** `--reasoning-file` or `--stdin` is used to supply decision_factors
- **THEN** the system SHALL accept an array of `{factor: string, score?: number, source: string}` objects
- **AND** SHALL reject entries missing required `factor` or `source` fields with a clear error

#### Scenario: Alternatives considered structured format
- **WHEN** alternatives_considered is supplied
- **THEN** each entry SHALL have `option: string` and `rejected_because: string` fields
- **AND** the system SHALL reject malformed entries

### Requirement: Pedigree required for verified status
The system SHALL prevent a view from transitioning to `verified` state unless its pedigree has all required core fields populated.

#### Scenario: Verified blocked by missing core fields
- **WHEN** `dm2 validate <view_id>` completes with no ERROR-level issues
- **AND** the view's pedigree is missing `author`, `creation_date`, or `source` core fields
- **THEN** the system SHALL NOT transition the view to `verified`
- **AND** SHALL report "Pedigree incomplete: missing [field names]" as a validation issue
- **AND** SHALL keep the view in `generated` state

#### Scenario: Verified succeeds with complete pedigree
- **WHEN** `dm2 validate <view_id>` completes with no ERROR-level issues
- **AND** the view's pedigree has all core fields (author, creation_date, source) populated
- **THEN** the system SHALL transition the view to `verified` (existing behavior preserved)

#### Scenario: Force override
- **WHEN** user runs `dm2 validate <view_id> --force-pedigree`
- **THEN** the system SHALL bypass the pedigree completeness check
- **AND** SHALL log the override in the modification history

### Requirement: Trace lineage across changes
The system SHALL support querying the lineage of an entity (capability, term, performer) across multiple changes within a project.

#### Scenario: Query term lineage
- **WHEN** user runs `dm2 trace lineage --term "Capability"`
- **THEN** the system SHALL scan all `.dm2/pedigree/*.yaml` files
- **AND** SHALL return a list of view_ids that reference "Capability" in their `source.dm2_terms_used` array
- **AND** SHALL include the change name (from `dm2-changes/<name>/`) where each view was generated

#### Scenario: Query capability lineage across changes
- **WHEN** user runs `dm2 trace lineage --capability "Multi-Task Scheduling"`
- **THEN** the system SHALL return a list of views that reference this capability name in their `reasoning.summary` or frontmatter
- **AND** SHALL group results by change name
- **AND** SHALL output JSON suitable for further processing

### Requirement: Trace queryability via knowledge API
The system SHALL expose pedigree records through the existing knowledge API at `dm2.core.knowledge.api.KnowledgeAPI`.

#### Scenario: Get pedigree for view
- **WHEN** `KnowledgeAPI.get_pedigree(view_id)` is called
- **THEN** the system SHALL return the full Pedigree object for the view
- **AND** SHALL return `None` if no pedigree exists

#### Scenario: List pedigrees
- **WHEN** `KnowledgeAPI.list_pedigrees()` is called
- **THEN** the system SHALL return a list of all view_ids that have a pedigree record
- **AND** SHALL include each view's `author.type`, `creation_date`, and `confidence` for filtering

#### Scenario: Search by author type
- **WHEN** `KnowledgeAPI.list_pedigrees(author_type="agent-autonomous")` is called
- **THEN** the system SHALL return only pedigrees with `author.type == "agent-autonomous"`

### Requirement: Provenance recording introduces no LLM dependency
Recording provenance SHALL NOT make dm2 call an LLM or declare an LLM client library; the agent-side reasoning fields SHALL be treated as content submitted by the external AI Agent rather than inference performed by dm2.

#### Scenario: No LLM call is introduced
- **WHEN** `dm2 trace record` or `dm2 audit` runs
- **THEN** dm2 SHALL NOT invoke an LLM
- **AND** the distribution SHALL continue to declare no LLM client library, as required by `dm2-no-llm-dependency`

#### Scenario: Agent-stated reasoning is labelled as unverified
- **WHEN** an audit report or a pedigree record presents the reasoning layer
- **THEN** those fields SHALL be identified as stated by the agent and not validated by dm2
- **AND** they SHALL NOT be presented as facts observed by dm2
