## Context

`ToolAdapter` (`src/dm2/core/adapters/__init__.py`) is a four-method ABC created by the
archived change `separate-skill-templates-from-claude-dir` so workflow skills could be
generated for more than one AI tool. `ClaudeCodeAdapter` was its only implementation, and
`dm2 init` hard-coded it (`src/dm2/cli/main.py`).

DSH's skill discovery (`packages/skill/skill-filesystem/src/index.ts` in the harness
checkout) differs from Claude Code in three ways that matter to this protocol:

| Aspect | Claude Code | DeepSeek Harness |
|---|---|---|
| Project skill root | `.claude/skills/` | `.dsh/skills/` |
| Command files | `.claude/commands/dm2/*.md` | no project-level command directory |
| Frontmatter | `name`, `description`, `license`, `compatibility`, `user-invocable`, `metadata` | requires kebab-case `name` + `description`; understands `user-invocable`; ignores other keys; preserves `metadata` |

DSH also rejects legacy camelCase invocation keys (`userInvocable`), so the existing
`user-invocable: false` spelling happens to already be correct.

## Goals / Non-Goals

**Goals:**

- A DSH session started in a dm2 project root discovers all 10 workflow skills from
  `.dsh/skills/` and loads them with no Claude-specific residue in the body.
- Claude Code output stays byte-identical, so existing consumers and pinned tests are unaffected.
- The protocol stays honest: each new capability is expressed as a protocol member rather than
  a tool check inside the generator.

**Non-Goals:**

- A DSH slash-command plugin (`ctx.commands.register`), native `dm2_*` model tools, or an agent
  preset package. Those are the separate "Phase B/C" items in
  `docs/dsh-adaptation-research.md`; this change only makes skills discoverable.
- Tokenizing the 10 workflow templates. Bodies are rewritten at generation time so the template
  sources (and the instruction-text assertions pinned in `test/test_workflow_templates.py`)
  stay untouched.
- Repairing the other seven specs that use `### Requirements`.
- Removing the residual `anthropic` dependency or the stale LLM section in the root README.

## Decisions

**Rewrite bodies at generation time, not in the templates.** Two of the 10 templates
(`apply`, `archive`) carry bare `/dm2:` references in their `SkillTemplate.description`, and
`apply` also has them inside fenced command examples — so a single regex family has to handle
backticked, bare, and description contexts anyway. Keeping the rewrite in the adapter means one
place owns tool differences, the templates stay human-readable source, and no pinned test
string changes.

**Order matters in `render_skill_body`.** `/dm2:knowledge` and the module invocation are
rewritten first, then `AskUserQuestion`, then the workflow slash references. `knowledge` is not
a workflow id, so if the workflow pass ran first it would be left as a dangling token; running
the specific rules first keeps the general rule unambiguous.

**Two slash-reference forms.** A backticked token (`` `/dm2:verify` ``) becomes
`` the `dm2-verify-workflow` skill ``, and a token carrying an angle argument
(`` `/dm2:propose <system-description>` ``) appends `(input: <system-description>)` so the
argument survives. Bare prose/fence references become `the dm2-verify-workflow skill` —
unbackticked, because they sit inside already-formatted sentences. Unknown ids are returned
unchanged so a future pseudo-command cannot be silently dropped.

**Descriptions are rendered too**, through the same method, because `apply`/`archive`
descriptions reference sibling slash commands. The result is YAML double-quoted with `\` and
`"` escaped, so backticks and em dashes cannot break parsing.

**DSH frontmatter drops `license`/`compatibility`.** DSH ignores them, and emitting fields a
consumer never reads would misrepresent the target's contract. `user-invocable: true` for all
10: under Claude each workflow was a user-facing slash command, and DSH has no command file to
replace that entry point. Model invocation remains enabled by default, so skill-body behaviour
is unchanged.

**`format_command_frontmatter` raises `NotImplementedError` in `DshAdapter`.** It is a dead
path — the generator never calls it when `supports_commands` is `False` — but implementing it
as a silent no-op would hide a future generator bug.

**`get_commands_dir()` returns `Optional[str]` plus a separate `supports_commands` property**
rather than overloading `None` alone. The generator needs both facts (where to write, whether
to write), and the explicit property reads better than a truthiness check on a path.

**Registry as a function, not a module constant.** `get_adapter(tool_id)` builds instances
lazily with the adapter imports inside the function body, avoiding a circular import between
`adapters/__init__.py` and the adapter modules that import `ToolAdapter` from it.

## Risks / Trade-offs

- **Instruction text now diverges per tool.** A Claude-oriented sentence that the renderer does
  not recognize reaches DSH unchanged. Mitigated by the hygiene test asserting no `/dm2:`,
  `AskUserQuestion`, or `python3 -m dm2.cli.main` survives in any generated DSH skill, plus a
  unit test per rewrite rule.
- **Regex rewrites can over-match prose.** Boundaries are chosen so tokens only match in
  command position, and unbackticked matches are excluded when preceded by a word character,
  backtick, or `/`. A negative test pins that dependency-chain prose (`OV-1`, `OV-2`) and
  already-correct `dm2 knowledge ...` invocations pass through untouched.
- **JSON contract change on `dm2 init --json`.** Pre-1.0 and consumer-free inside this repo;
  recorded in `CHANGELOG.md`. No compatibility alias is kept, since keeping one would freeze
  the Claude-only shape the change exists to remove.
- **DSH project root depends on `.git`.** `findProjectRoot` walks up to the git root and falls
  back to cwd, so a non-git project only works when the session starts in the project root.
  Documented in `docs/readme.md` rather than worked around in `init`.
- **Skill entry-point semantics differ.** A DSH user invokes a `user-invocable` skill rather
  than typing `/dm2:propose`; the workflows themselves are unchanged, but the documented
  invocation style in `README.md` is Claude-oriented.
