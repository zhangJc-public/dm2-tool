# dm2-element-vocabulary (delta)

This delta adds the naming-preview capability: describing an arbitrary term name
(already in the dictionary or still prospective) in terms of the vocabulary.

## ADDED Requirements

### Requirement: Any term name can be described through the vocabulary
The vocabulary SHALL describe an arbitrary term name — one already in the
dictionary or one still being proposed — reporting its decomposed tokens, each
token's kind (data element, qualifier, or unknown) and Chinese, the composed
canonical name, and the list of unregistered tokens. Description SHALL be
deterministic, zero-LLM, and SHALL NOT guess a translation for an unregistered
token.

#### Scenario: A prospective name composed of registered tokens
- **WHEN** `CapabilityType` is described
- **THEN** the segments SHALL be `capability` (element → 能力) and `type`
  (qualifier → 类型)
- **AND** the composed name SHALL be `能力类型`
- **AND** `unregistered` SHALL be empty

#### Scenario: An unregistered token is reported, not guessed
- **WHEN** `ZzzThing` is described
- **THEN** `zzz` SHALL appear in `unregistered` with kind `unknown` and no Chinese
- **AND** the composed name SHALL be empty rather than a partial guess

#### Scenario: Description is deterministic
- **WHEN** the same name is described twice
- **THEN** the reported tokens, kinds, Chinese and composed name SHALL be identical
