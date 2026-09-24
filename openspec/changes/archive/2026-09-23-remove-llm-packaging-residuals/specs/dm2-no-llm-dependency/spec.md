# DM2 No LLM Dependency (delta)

## ADDED Requirements

### Requirement: No LLM client library is declared as a dm2 dependency
The `dm2-tool` distribution SHALL NOT declare any LLM client library (such as `anthropic` or
`openai`) as a runtime dependency or as an optional extra, because dm2 never calls an LLM.

#### Scenario: Runtime dependencies exclude LLM libraries
- **WHEN** packaging metadata is generated from `pyproject.toml`
- **THEN** `[project.dependencies]` SHALL contain no LLM client library
- **AND** the emitted `Requires-Dist` entries SHALL be limited to packages the dm2 code actually uses

#### Scenario: No LLM optional extra is offered
- **WHEN** `[project.optional-dependencies]` is read
- **THEN** it SHALL contain no extra whose purpose is installing an LLM client library

#### Scenario: A clean install pulls no LLM SDK
- **WHEN** `pip install dm2-tool` completes in a clean environment
- **THEN** no LLM client library SHALL be present as a consequence of that install

### Requirement: No dm2 module imports an LLM client
Every module under `src/dm2/` SHALL contain zero imports of LLM client libraries and zero code
paths that invoke an external LLM API for content generation.

#### Scenario: Import scan is clean
- **WHEN** the tree under `src/dm2/` is scanned for `anthropic`, `openai`, `ClaudeClient`, `AnthropicProvider`, or `OpenAIProvider`
- **THEN** zero LLM client imports SHALL be found

#### Scenario: The CLI runs without LLM libraries installed
- **WHEN** no LLM client library is available in the environment
- **THEN** every dm2 command SHALL still import and run

### Requirement: User-facing surfaces do not instruct LLM configuration
dm2 documentation, CLI help text, and source examples SHALL NOT instruct users to configure an
LLM model, endpoint, or provider API key, because LLM configuration belongs to the external AI
Agent rather than to dm2.

#### Scenario: README presents no LLM configuration
- **WHEN** `README.md` is read
- **THEN** its configuration section SHALL NOT present an `llm.*` setting example
- **AND** it SHALL NOT list LLM provider API-key environment variables as dm2 configuration

#### Scenario: CLI help advertises only accepted keys
- **WHEN** `dm2 config --help` is displayed
- **THEN** the `--set` example SHALL name a configuration key that dm2 still accepts

#### Scenario: Source examples name real keys
- **WHEN** help strings and docstrings under `src/dm2/` are scanned for configuration examples
- **THEN** no example SHALL reference `llm.model` or any other removed `llm.*` key

### Requirement: Configuration carries no LLM settings
The configuration system SHALL NOT define `llm.*` defaults and SHALL NOT persist an `llm.*`
setting, because that configuration is owned by the AI Agent layer.

#### Scenario: Default configuration has no llm section
- **WHEN** `resolve_config()` is called with no user or project overrides
- **THEN** the returned configuration SHALL NOT contain an `llm` key

#### Scenario: Setting an llm key is refused without persisting
- **WHEN** a user runs `dm2 config -s llm.model=<value>`
- **THEN** the command SHALL NOT write the setting to any configuration file
- **AND** in human mode it SHALL print an informational message that LLM configuration is managed by the AI Agent layer, and exit successfully
- **AND** with `--json` it SHALL report error code `LLM_CONFIG_REJECTED` and exit non-zero
