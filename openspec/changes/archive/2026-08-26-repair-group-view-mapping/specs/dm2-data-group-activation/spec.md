# DM2 Data Group Activation (delta)

## ADDED Requirements

### Requirement: Mapping view IDs reference existing views
Every view ID in `group-to-views.yaml` `group_views` entries SHALL reference a
view that exists in `dm2-reference/core/views.yaml`. The literal `All` is
exempt (meta-group marker).

#### Scenario: Dead mapping ID is rejected
- **WHEN** the mapping file is loaded for tests or validation
- **THEN** every `group_views[].id` other than `All` SHALL be present in the set
  of view IDs defined by `views.yaml`
- **AND** an entry like `SvcV-3` (real IDs are `SvcV-3a`/`SvcV-3b`) SHALL fail
  the build/test run

### Requirement: Every non-meta view is claimed by at least one group
Every DoDAF view in `views.yaml` SHALL be claimed by at least one data group in
`group-to-views.yaml`, except the documented meta-view set {`AV-1`, `AV-2`}
which are delivered through the view dependency graph rather than activation.

#### Scenario: Blind-spot views fail the coverage test
- **WHEN** the mapping file is checked for coverage
- **THEN** every view ID except `AV-1` and `AV-2` SHALL appear in at least one
  group's `group_views` list
- **AND** systems-family views (`SV-1`, `SV-3`, `SV-5a`, `SV-5b`, `SV-8`,
  `SV-9`, `SV-10b`, `SV-10c`), behavioral views (`OV-6b`, `OV-6c`),
  `SvcV-3a`, `SvcV-3b`, and `StdV-2` SHALL be claimed

### Requirement: Mapping entries carry an evidence basis
Each `group_views` entry SHALL carry a `basis` field of value `matrix` or
`practice`. `matrix` means the DoDAF DM2 Data Dictionary monster matrix
(term × view n/o marks) contains necessary or optional terms of that group for
the view; `practice` means the mapping is practitioner judgment without matrix
support.

#### Scenario: Practice-based entries are on a documented allow-list
- **WHEN** mapping entries are validated
- **THEN** every entry SHALL have `basis: matrix` or `basis: practice`
- **AND** `basis: practice` entries SHALL be limited to the documented set
  {`07-location → OV-1`, `07-location → OV-2`} (the monster matrix contains
  zero location terms for these columns; OV-4 entries carry optional
  Organization/PersonRole terms and are `basis: matrix`)

#### Scenario: Rules model views belong to the Rules group
- **WHEN** mapping entries for operational/systems rules models are inspected
- **THEN** `OV-6a` SHALL be claimed by `10-rules` (alongside `SV-10a`,
  `SvcV-10a`)
- **AND** `OV-6a` SHALL NOT be claimed by `05-guidance` as a primary mapping
