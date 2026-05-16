## 1. Phase 1: Agent Interface + Knowledge API

### 1.1 Agent Interface Layer

- [x] 1.1.1 Add `--json` flag support to all existing CLI commands (init, list, status, archive, cynefin, generate, config, analyze, run, version, uninstall)
- [x] 1.1.2 Implement unified JSON response helper (`{"status": "success"|"error", "data": {...}}`) in `src/dm2/cli/json_output.py`
- [x] 1.1.3 Define JSON Schema for each command's data payload (analyze, status, cynefin, generate, run)
- [x] 1.1.4 Update CLI help text to document `--json` flag for each command

### 1.2 Knowledge API

- [x] 1.2.1 Create `src/dm2/core/__init__.py` and `src/dm2/core/knowledge/` package
- [x] 1.2.2 Implement `dm2 knowledge search <query> --json` in `src/dm2/core/knowledge/api.py` — term name/alias/definition matching
- [x] 1.2.3 Implement `dm2 knowledge concept <name> --json` — full concept record with relationships
- [x] 1.2.4 Implement `dm2 knowledge views --type <viewpoint> --json` — filter by DoDAF viewpoint
- [x] 1.2.5 Implement `dm2 knowledge view <id> --json` — single view complete metadata
- [x] 1.2.6 Implement `dm2 knowledge stats --json` — aggregate counts
- [x] 1.2.7 Register `dm2 knowledge` command group in `cli/main.py`

## 2. Phase 2: Core Engine (Artifact Graph + Instructions Engine + Change Manager)

### 2.1 Artifact Graph

- [x] 2.1.1 Create `src/dm2/core/artifacts/` package with `graph.py` and `types.py`
- [x] 2.1.2 Load view dependency graph from `dm2-reference/views.yaml` on initialization
- [x] 2.1.3 Implement `compute_status(artifact_id, change_dir)` — pending/ready/in_progress/done logic
- [x] 2.1.4 Implement `get_ready_artifacts(change_dir)` — query all artifacts ready for generation
- [x] 2.1.5 Implement `get_artifact_info(artifact_id)` — full dependency/dependent lists
- [x] 2.1.6 Implement topological sort for view generation order (`get_generation_order()`)

### 2.2 Instructions Engine

- [x] 2.2.1 Create `src/dm2/core/agent/` package with `instructions.py` and `types.py`
- [x] 2.2.2 Implement `InstructionBuilder` class — assembles context + rules + template + outputPath
- [x] 2.2.3 Implement context assembly: load DM2 terms, concepts, dependency artifacts, project description
- [x] 2.2.4 Implement rules assembly: load DoDAF compliance rules per artifact type
- [x] 2.2.5 Implement template assembly: derive from views.yaml for views, from step specs for pipeline steps
- [x] 2.2.6 Implement `dm2 instructions <artifact-type> --change <name> --json` CLI command
- [x] 2.2.7 Add instruction templates for each of the 4 pipeline steps (step1, step3, step5, step6)

### 2.3 Change Manager

- [x] 2.3.1 Create `src/dm2/core/changes/` package with `manager.py` and `types.py`
- [x] 2.3.2 Implement `.change.yaml` state file format and read/write logic
- [x] 2.3.3 Implement `dm2 change new <name>` — create standardized change directory with state file
- [x] 2.3.4 Implement `dm2 change status --change <name> --json` — lifecycle state + artifact graph
- [x] 2.3.5 Implement `dm2 change list --json` — all active changes with status
- [x] 2.3.6 Implement `dm2 change archive <name>` — move to archive with date prefix
- [x] 2.3.7 Register `dm2 change` command group in `cli/main.py`

## 3. Phase 3: Pipeline V2 (Agent-Driven)

### 3.1 Pipeline Orchestrator V2

- [x] 3.1.1 Create `src/dm2/core/pipeline/` package separate from `src/dm2/engine/pipeline/`
- [x] 3.1.2 Implement `PipelineOrchestratorV2` — manages step state, generates instructions, accepts completions
- [x] 3.1.3 Implement `dm2 run --status --json` — current pipeline state for AI Agent
- [x] 3.1.4 Implement `dm2 run --instructions <step-id> --json` — step-specific agent instructions
- [x] 3.1.5 Implement `dm2 run --complete-step <step-id> --json` — mark step done, advance pipeline
- [x] 3.1.6 Implement `dm2 run --agent` flag — enable Agent-driven mode (off by default for backward compat)

### 3.2 Modified Step Specs Integration

- [x] 3.2.1 Update Step 1+2 output to include JSON-formatted clarification questions
- [x] 3.2.2 Update Step 3+4 to use Knowledge API internally (refactor to call `DM2KnowledgeIndexer` via public API)
- [x] 3.2.3 Update Step 5 output to include JSON Schema-conformant analysis data
- [x] 3.2.4 Update Step 6 to use Instructions Engine templates for view generation

### 3.3 CLI Reorganization

- [x] 3.3.1 Split `cli/main.py` into `cli/commands/` subpackage (knowledge.py, change.py)
- [x] 3.3.2 Update `main.py` to register command groups from subpackage
- [x] 3.3.3 Verify all existing commands work after split

## 4. Validation & Documentation

- [x] 4.1 Test `--json` output on all commands (parse with jq, verify schema)
- [x] 4.2 Test `dm2 knowledge` commands against dm2-reference data
- [x] 4.3 Test `dm2 change` full lifecycle (new → status → archive)
- [x] 4.4 Test `dm2 instructions` for a DoDAF view and a pipeline step
- [x] 4.5 Test Agent-driven pipeline loop (simulate AI Agent calling status → instructions → complete-step)
- [x] 4.6 Test backward compatibility: legacy `dm2 run` without --agent produces identical output
- [x] 4.7 Update README.md: new architecture diagram, AI Agent workflow, knowledge API reference, change lifecycle
- [x] 4.8 Update CLAUDE.md: new directory structure, development workflow
