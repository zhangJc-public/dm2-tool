## Why

DM2 is implemented in Python but depends on OpenSpec (TypeScript/Node.js) for its spec-driven change management workflow (`/opsx:*` commands). This dual-language dependency creates deployment friction, fragments the tool's identity, and adds long-term maintenance risk. We need to decide whether Python is the right long-term language for DM2, especially given that Claude Code orchestrates both tools at arm's length via bash.

## What Changes

- Evaluate Python vs TypeScript for DM2's domain (DoDAF systems engineering, LLM integration, knowledge management)
- Analyze the actual integration bottleneck: DM2 and OpenSpec don't call each other — Claude Code calls both via shell
- Assess whether re-implementing DM2 in TypeScript, re-implementing OpenSpec-equivalent logic in Python, or keeping the status quo is optimal
- Document the decision and rationale
- If action is warranted, produce an implementation plan for the migration or alternative approach

## Capabilities

### New Capabilities

- `language-decision`: Documented, reasoned decision on DM2's implementation language and relationship with OpenSpec/TypeScript tooling

### Modified Capabilities

<!-- No existing specs to modify -->

## Impact

- All Python source code (`src/dm2/`) if a rewrite is decided
- CLI entry points and packaging (`pyproject.toml`)
- Claude Code integration files (`.claude/commands/opsx/`, `.claude/skills/`)
- LLM integration (Anthropic SDK, OpenAI SDK usage)
- CI/CD pipeline (`.github/workflows/verify.yml`)
- Development setup documentation (`CLAUDE.md`, `README.md`)
- User environment requirements (Python + Node.js vs single runtime)
