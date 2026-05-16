## ADDED Requirements

### Requirement: No Python module in dm2 imports or calls any LLM API
The dm2 codebase under `src/dm2/` SHALL contain zero imports of LLM client libraries (anthropic, openai) and zero code paths that invoke external LLM APIs for content generation.

#### Scenario: Codebase scan for LLM imports
- **WHEN** a codebase scan is run for `anthropic`, `openai`, `ClaudeClient`, `AnthropicProvider`, `OpenAIProvider` imports in `src/dm2/`
- **THEN** zero results SHALL be returned for LLM client imports
- **AND** the `src/dm2/llm/` directory SHALL NOT contain `client.py`, `provider.py`, or `prompts.py`

#### Scenario: dm2 analyze has no --llm flag
- **WHEN** user runs `dm2 analyze --llm`
- **THEN** the command SHALL fail with an error indicating the flag is no longer available

#### Scenario: dm2 generate works without any LLM
- **WHEN** user runs `dm2 generate OV-1 -d "..."` without any LLM configuration
- **THEN** the command SHALL succeed and output structured instructions as before

### Requirement: ViewTemplateFiller is the sole content generation mechanism
All view content generation within dm2 SHALL use `ViewTemplateFiller` for template-based filling. The `DoDAFViewGenerator` class SHALL be removed.

#### Scenario: ViewTemplateFiller generates view content
- **WHEN** `ViewTemplateFiller.fill("OV-1", data)` is called
- **THEN** it SHALL return a Markdown document with the OV-1 template structure filled with provided data
- **AND** no LLM API SHALL be called

#### Scenario: DoDAFViewGenerator no longer exists
- **WHEN** any code attempts `from dm2.engine.view_generator import DoDAFViewGenerator`
- **THEN** it SHALL fail with ImportError

### Requirement: RAG engine is in kernel package
The `ObsidianRAGEngine` class SHALL reside in `src/dm2/kernel/rag.py`, reflecting its role as a file-based knowledge retrieval component rather than an LLM component.

#### Scenario: Import path reflects correct location
- **WHEN** code imports `ObsidianRAGEngine`
- **THEN** the import SHALL be `from dm2.kernel.rag import ObsidianRAGEngine`
- **AND** the import SHALL succeed

### Requirement: Config manager has no LLM defaults
The configuration system SHALL NOT include `llm` section in its default configuration. The `config_manager` module SHALL reside in `src/dm2/config/`.

#### Scenario: Default config has no llm section
- **WHEN** `resolve_config()` is called with no user or project overrides
- **THEN** the returned config SHALL NOT contain an `llm` key

#### Scenario: dm2 config rejects llm settings
- **WHEN** user runs `dm2 config -s llm.model=xxx`
- **THEN** the command SHALL output an informational message that LLM config is managed by the AI Agent layer
