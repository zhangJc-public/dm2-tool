## Context

Currently `dm2 init` copies skills and commands via `shutil.copytree()` from the dm2-tool developer's own `.claude/` directory. This conflates the developer's runtime Claude Code config with dm2's distributable assets. It also breaks when dm2-tool is installed via `pip install` (non-editable) because `Path(__file__).parent.parent.parent.parent` resolves relative to the dev repo root.

OpenSpec's architecture solves this with template functions + tool adapters. We adopt the same pattern for dm2, scoped to Claude Code initially.

## Goals / Non-Goals

**Goals:**
- Extract all 7 SKILL.md + 7 command .md contents into Python template dataclasses
- Create a `ToolAdapter` protocol with a concrete `ClaudeCodeAdapter` implementation
- Rewrite `dm2 init` to generate files from templates, not copy from `.claude/`
- Fix path resolution to work in both `pip install -e` and `pip install` modes
- Include `generatedBy: dm2-tool/<version>` in generated SKILL.md frontmatter

**Non-Goals:**
- Multi-tool support beyond Claude Code (design the interface for it, but only implement Claude)
- Dynamic workflow discovery — the 7 workflows are explicitly registered, not scanned from a directory
- Changing the skill/command content itself (just how it's stored and delivered)

## Decisions

**Decision 1: Templates as Python dataclasses**

Each workflow is represented by a `WorkflowTemplate` dataclass with `skill` and `command` fields. The template content is a multi-line string in Python code — same as OpenSpec's TypeScript template functions.

```python
@dataclass
class WorkflowTemplate:
    workflow_id: str           # e.g. "propose", "continue"
    skill: SkillTemplate       # name, description, instructions
    command: CommandTemplate   # name, description, category, tags, body

@dataclass
class SkillTemplate:
    name: str
    description: str
    instructions: str
    license: str = "MIT"
    compatibility: str = "Requires dm2-tool CLI."

@dataclass
class CommandTemplate:
    name: str
    description: str
    category: str = "Architecture"
    tags: list[str] = field(default_factory=list)
    body: str = ""
```

Location: `src/dm2/core/templates/workflows/` — one file per workflow (7 files).

**Decision 2: ToolAdapter protocol**

```python
class ToolAdapter(Protocol):
    tool_id: str
    def get_skills_dir(self) -> str: ...
    def get_commands_dir(self) -> str: ...
    def format_skill_frontmatter(self, template: SkillTemplate, version: str) -> str: ...
    def format_command_frontmatter(self, template: CommandTemplate) -> str: ...
```

`ClaudeCodeAdapter` implements:
- `skills_dir` → `.claude/skills/`
- `commands_dir` → `.claude/commands/dm2/`
- Skill format: YAML frontmatter with `name`, `description`, `license`, `compatibility`, `metadata: {author, version, generatedBy}`
- Command format: YAML frontmatter with `name`, `description`, `category`, `tags`

Location: `src/dm2/core/adapters/` — `protocol.py` + `claude.py`

**Decision 3: All 7 workflows explicitly registered**

A `WORKFLOWS` list in `src/dm2/core/templates/__init__.py` registers all 7:

| workflow_id | skill dir | command file |
|---|---|---|
| `propose` | `dm2-propose-workflow` | `propose.md` |
| `continue` | `dm2-continue-workflow` | `continue.md` |
| `new` | `dm2-new-workflow` | `new.md` |
| `ff` | `dm2-ff-workflow` | `ff.md` |
| `verify` | `dm2-verify-workflow` | `verify.md` |
| `onboard` | `dm2-onboard-workflow` | `onboard.md` |
| `bulk-archive` | `dm2-bulk-archive-workflow` | `bulk-archive.md` |

No dynamic file scanning. Adding a new workflow means adding a new dataclass file + registration entry.

**Decision 4: `dm2 init` generation logic is adapter-agnostic**

`dm2 init` calls a single function:
```python
def generate_claude_config(target_dir: Path, version: str, adapter: ToolAdapter = ClaudeCodeAdapter()) -> int
```

This iterates `WORKFLOWS`, generates SKILL.md and command .md for each, writes to target. The adapter handles path mapping and formatting. If we later add Cursor support, we add `CursorAdapter` and iterate with that instead.

**Decision 5: Version string from package metadata**

```python
from dm2 import __version__
```

Used in `generatedBy: "dm2-tool/<version>"` metadata. Works in both dev and installed modes.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| Template content getting out of sync with `.claude/` during development | After implementation, `.claude/` skills/commands become dev-only (not distribution). Dev runs `dm2 init` in test project to verify generation. |
| SKILL.md content as Python strings is harder to edit than .md files | Acceptable trade-off for proper packaging. Content changes are infrequent. Multi-line strings in dedicated files keep it readable. |
| `importlib.resources` API differences across Python 3.9-3.13 | Use `importlib.resources.files()` (3.9+) for reading package data. Dataclass templates don't need file I/O. |
