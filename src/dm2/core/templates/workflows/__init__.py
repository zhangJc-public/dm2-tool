"""All dm2 workflow templates. Each module registers itself in WORKFLOWS on import."""

from dm2.core.templates import WORKFLOWS
from dm2.core.templates.workflows import (
    propose,
    continue_workflow,
    new_workflow,
    ff,
    verify,
    onboard,
    bulk_archive,
    explore,
    apply,
    archive,
)

_all_workflows = [
    propose,
    continue_workflow,
    new_workflow,
    ff,
    verify,
    onboard,
    bulk_archive,
    explore,
    apply,
    archive,
]

for wf in _all_workflows:
    WORKFLOWS.append(wf.get_workflow_template())
