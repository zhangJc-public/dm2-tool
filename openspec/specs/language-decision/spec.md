## Purpose

评估 DM2 工具实现语言（Python vs TypeScript）的长期适用性，基于 DoDAF 领域需求、LLM 生态、CLI 成熟度和 OpenSpec 集成分析做出决策。

## Requirements

### Requirement: Language evaluation criteria
The evaluation SHALL assess Python vs TypeScript for DM2 against these criteria:
- Suitability for DoDAF/systems engineering domain (YAML, Markdown, data modeling)
- LLM/AI ecosystem quality (SDK availability, prompt engineering ergonomics)
- CLI framework maturity and user experience
- Claude Code agent integration overhead
- Deployment simplicity (single vs dual runtime)
- Long-term maintainability for a solo/small-team project

#### Scenario: Criteria are weighted by domain relevance
- **WHEN** evaluating languages against the criteria
- **THEN** domain-specific criteria (DoDAF/LLM) SHALL carry more weight than general-purpose criteria (CLI, deployment)

### Requirement: OpenSpec integration analysis
The evaluation SHALL analyze how DM2 and OpenSpec interact at the technical level, identifying the actual (not perceived) bottlenecks in the Python-TypeScript boundary.

#### Scenario: Integration is traced end-to-end
- **WHEN** analyzing the integration path
- **THEN** the evaluation SHALL trace every call chain involving both Python and Node.js runtimes and identify whether Claude Code's shell-level orchestration makes the language boundary irrelevant

### Requirement: Decision with recommendation
The evaluation SHALL produce a clear, reasoned decision with one of these outcomes:
- Keep Python, accept Node.js dependency for OpenSpec
- Rewrite DM2 in TypeScript
- Re-implement OpenSpec-equivalent workflow logic natively in Python
- Hybrid approach (e.g., keep core in Python, add TypeScript shims where needed)

#### Scenario: Decision is documented with rationale
- **WHEN** the evaluation concludes
- **THEN** the decision SHALL include rationale, trade-offs considered, and an implementation plan if action is required

### Requirement: No implementation without decision
No code changes SHALL be made to DM2's language or architecture until this evaluation is complete and the decision is approved.

#### Scenario: Evaluation precedes any rewrite
- **WHEN** a rewrite or migration is proposed
- **THEN** it SHALL reference this evaluation and the approved decision before any implementation tasks begin
