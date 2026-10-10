"""Pedigree data model — DM2 V2.02 provenance for AI-Agent-generated views.

Two layers are deliberately kept apart:

* **Facts** dm2 observes itself (view registration, lifecycle transitions,
  validation results) land in ``modification_history`` / ``validation``. The CLI
  owns those fields; ``dm2 trace record`` never rewrites them.
* **Reasoning** an external AI Agent states (``reasoning.*``,
  ``known_limitations``) is content dm2 persists but cannot verify. Audit output
  must label it as Agent-stated rather than presenting it as an observed fact.

Records loaded from disk may be incomplete: ``.dm2/view-state.yaml`` has to tell
``absent`` from ``incomplete`` pedigrees and audit reports list the missing core
fields, so loading passes ``strict=False``. The recording path
(:meth:`Pedigree.new` and the strict constructor) enforces every required field.
"""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Optional

import yaml

#: Allowed ``author.type`` values.
AUTHOR_TYPES = ("human", "agent-assisted", "agent-autonomous")
#: Allowed ``reliability`` values.
RELIABILITY_VALUES = ("low", "medium", "high")
#: Allowed ``validation.issues[].severity`` values.
SEVERITY_VALUES = ("error", "warning", "info")
#: Core fields a view's pedigree needs before the view may reach ``verified``.
CORE_FIELDS = ("author", "creation_date", "source")


class PedigreeValidationError(ValueError):
    """A pedigree violates the schema; the message names the field and the view."""

    def __init__(self, view_id: str, field_name: str, problem: str):
        self.view_id = view_id
        self.field_name = field_name
        super().__init__(f"pedigree {view_id or '<unknown>'}: invalid {field_name}: {problem}")


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


@dataclass
class Author:
    """Who produced the view."""

    type: str = ""
    model: str = ""
    operator: str = ""


@dataclass
class TermReference:
    """A DM2 term cited by the view, with a pointer to its canonical definition."""

    term: str = ""
    definition_ref: str = ""


@dataclass
class Source:
    """Standard provenance: what the view's content is grounded in."""

    standard: str = ""
    section: str = ""
    dm2_terms_used: list[TermReference] = field(default_factory=list)
    alignment_notes: str = ""


@dataclass
class DecisionFactor:
    """One factor the Agent weighed when generating the view."""

    factor: str = ""
    score: Optional[float] = None
    source: str = ""


@dataclass
class Alternative:
    """One content approach the Agent considered and rejected."""

    option: str = ""
    rejected_because: str = ""


@dataclass
class Reasoning:
    """Agent-stated rationale — persisted by dm2, never verified by dm2."""

    summary: str = ""
    decision_factors: list[DecisionFactor] = field(default_factory=list)
    alternatives_considered: list[Alternative] = field(default_factory=list)


@dataclass
class ModificationRecord:
    """One observed modification event (fact layer)."""

    date: str = ""
    actor: str = ""
    change_description: str = ""


@dataclass
class ValidationIssue:
    """One consistency issue persisted into the pedigree."""

    rule: str = ""
    severity: str = ""
    message: str = ""
    suggested_fix: Optional[str] = None


@dataclass
class ValidationRecord:
    """Validation history observed by the CLI (fact layer)."""

    ran_R1: bool = False
    ran_R2: bool = False
    ran_R3: bool = False
    ran_R4: bool = False
    ran_R5: bool = False
    issues: list[ValidationIssue] = field(default_factory=list)
    last_validated: Optional[str] = None


@dataclass
class Pedigree:
    """The DM2 V2.02 Pedigree record for one generated view."""

    view_id: str
    pedigree_id: str = ""
    author: Optional[Author] = None
    creation_date: str = ""
    source: Optional[Source] = None
    reasoning: Reasoning = field(default_factory=Reasoning)
    validation: ValidationRecord = field(default_factory=ValidationRecord)
    modification_history: list[ModificationRecord] = field(default_factory=list)
    reliability: str = "low"
    confidence: float = 0.0
    known_limitations: list[str] = field(default_factory=list)
    content_hash: str = ""
    change: str = ""
    #: ``False`` only while loading a record from disk: an incomplete pedigree has
    #: to stay representable so audit reports can list its missing core fields.
    strict: bool = field(default=True, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not self.view_id:
            raise PedigreeValidationError("", "view_id", "required")
        # Tolerate explicit nulls from partially written records before validating.
        if self.reasoning is None:
            self.reasoning = Reasoning()
        if self.validation is None:
            self.validation = ValidationRecord()
        if self.modification_history is None:
            self.modification_history = []
        if self.known_limitations is None:
            self.known_limitations = []

        if not isinstance(self.confidence, (int, float)) or isinstance(self.confidence, bool):
            raise PedigreeValidationError(self.view_id, "confidence", "must be a number between 0 and 1")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise PedigreeValidationError(
                self.view_id, "confidence", f"must be between 0 and 1, got {self.confidence}"
            )
        if self.reliability and self.reliability not in RELIABILITY_VALUES:
            raise PedigreeValidationError(
                self.view_id, "reliability", f"expected one of {list(RELIABILITY_VALUES)}"
            )
        if self.author is not None and self.author.type and self.author.type not in AUTHOR_TYPES:
            raise PedigreeValidationError(
                self.view_id, "author.type", f"expected one of {list(AUTHOR_TYPES)}"
            )

        self._validate_source()
        self._validate_reasoning()
        self._validate_validation()

        if self.strict:
            missing = self.missing_core_fields()
            if missing:
                raise PedigreeValidationError(self.view_id, missing[0], "required core field is missing")

    # ── validation ───────────────────────────────────────────────────────

    def _validate_source(self) -> None:
        if self.source is None:
            return
        for index, term in enumerate(self.source.dm2_terms_used or []):
            if not term.term:
                raise PedigreeValidationError(
                    self.view_id, f"source.dm2_terms_used[{index}].term", "required"
                )

    def _validate_reasoning(self) -> None:
        for index, factor in enumerate(self.reasoning.decision_factors or []):
            if not factor.factor:
                raise PedigreeValidationError(
                    self.view_id, f"reasoning.decision_factors[{index}].factor", "required"
                )
            if not factor.source:
                raise PedigreeValidationError(
                    self.view_id, f"reasoning.decision_factors[{index}].source", "required"
                )
            if factor.score is not None and not isinstance(factor.score, (int, float)):
                raise PedigreeValidationError(
                    self.view_id, f"reasoning.decision_factors[{index}].score", "must be a number"
                )
        for index, alternative in enumerate(self.reasoning.alternatives_considered or []):
            if not alternative.option:
                raise PedigreeValidationError(
                    self.view_id, f"reasoning.alternatives_considered[{index}].option", "required"
                )
            if not alternative.rejected_because:
                raise PedigreeValidationError(
                    self.view_id,
                    f"reasoning.alternatives_considered[{index}].rejected_because",
                    "required",
                )

    def _validate_validation(self) -> None:
        for index, issue in enumerate(self.validation.issues or []):
            if not issue.rule:
                raise PedigreeValidationError(self.view_id, f"validation.issues[{index}].rule", "required")
            if issue.severity not in SEVERITY_VALUES:
                raise PedigreeValidationError(
                    self.view_id,
                    f"validation.issues[{index}].severity",
                    f"expected one of {list(SEVERITY_VALUES)}",
                )
            if not issue.message:
                raise PedigreeValidationError(
                    self.view_id, f"validation.issues[{index}].message", "required"
                )

    def missing_core_fields(self) -> list[str]:
        """Core fields that are absent, in the canonical order of ``CORE_FIELDS``."""
        missing = []
        if self.author is None or not self.author.type:
            missing.append("author")
        if not self.creation_date:
            missing.append("creation_date")
        if self.source is None:
            missing.append("source")
        return missing

    # ── fact-layer mutation ──────────────────────────────────────────────

    def append_modification(
        self, actor: str, change_description: str, *, date: Optional[str] = None
    ) -> ModificationRecord:
        """Append one observed modification event and return it."""
        record = ModificationRecord(date=date or _now(), actor=actor, change_description=change_description)
        self.modification_history.append(record)
        return record

    # ── construction & serialization ─────────────────────────────────────

    @classmethod
    def new(
        cls,
        view_id: str,
        author: Author,
        source: Source,
        *,
        reasoning: Optional[Reasoning] = None,
        reliability: str = "low",
        confidence: float = 0.0,
        change: str = "",
    ) -> "Pedigree":
        """Create a new, strict pedigree record (generates id and creation date)."""
        return cls(
            view_id=view_id,
            pedigree_id=str(uuid.uuid4()),
            author=author,
            creation_date=_now(),
            source=source,
            reasoning=reasoning or Reasoning(),
            reliability=reliability,
            confidence=confidence,
            change=change,
        )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("strict", None)
        return data

    def to_yaml(self) -> str:
        return yaml.safe_dump(self.to_dict(), allow_unicode=True, sort_keys=False)

    def frontmatter_block(self) -> dict[str, Any]:
        """The minimal, human-readable provenance embedded in a view's frontmatter."""
        source = self.source or Source()
        return {
            "pedigree_id": self.pedigree_id,
            "author": {
                "type": self.author.type,
                "model": self.author.model,
                "operator": self.author.operator,
            }
            if self.author
            else {},
            "creation_date": self.creation_date,
            "source": {
                "standard": source.standard,
                "section": source.section,
                "dm2_terms_used": [
                    {"term": term.term, "definition_ref": term.definition_ref}
                    for term in source.dm2_terms_used or []
                ],
            },
        }

    @classmethod
    def from_dict(cls, data: Optional[dict], *, strict: bool = False) -> "Pedigree":
        """Load a record leniently (``strict=False``) or strictly."""
        raw = data or {}
        view_id = str(raw.get("view_id") or "")
        raw_confidence = raw.get("confidence")
        if isinstance(raw_confidence, bool):
            raise PedigreeValidationError(view_id, "confidence", "must be a number between 0 and 1")
        try:
            confidence = float(raw_confidence if raw_confidence is not None else 0.0)
        except (TypeError, ValueError):
            raise PedigreeValidationError(view_id, "confidence", "must be a number between 0 and 1")

        author = raw.get("author")
        source = raw.get("source")
        reasoning = raw.get("reasoning") or {}
        validation = raw.get("validation") or {}

        return cls(
            view_id=view_id,
            pedigree_id=str(raw.get("pedigree_id") or ""),
            author=Author(
                type=str(author.get("type") or ""),
                model=str(author.get("model") or ""),
                operator=str(author.get("operator") or ""),
            )
            if isinstance(author, dict)
            else None,
            creation_date=str(raw.get("creation_date") or ""),
            source=Source(
                standard=str(source.get("standard") or ""),
                section=str(source.get("section") or ""),
                dm2_terms_used=[
                    TermReference(
                        term=str(term.get("term") or ""),
                        definition_ref=str(term.get("definition_ref") or ""),
                    )
                    for term in (source.get("dm2_terms_used") or [])
                    if isinstance(term, dict)
                ],
                alignment_notes=str(source.get("alignment_notes") or ""),
            )
            if isinstance(source, dict)
            else None,
            reasoning=Reasoning(
                summary=str(reasoning.get("summary") or ""),
                decision_factors=[
                    DecisionFactor(
                        factor=str(factor.get("factor") or ""),
                        score=_optional_float(view_id, f"reasoning.decision_factors[{index}].score", factor.get("score")),
                        source=str(factor.get("source") or ""),
                    )
                    for index, factor in enumerate(reasoning.get("decision_factors") or [])
                    if isinstance(factor, dict)
                ],
                alternatives_considered=[
                    Alternative(
                        option=str(alternative.get("option") or ""),
                        rejected_because=str(alternative.get("rejected_because") or ""),
                    )
                    for alternative in (reasoning.get("alternatives_considered") or [])
                    if isinstance(alternative, dict)
                ],
            ),
            validation=ValidationRecord(
                ran_R1=bool(validation.get("ran_R1", False)),
                ran_R2=bool(validation.get("ran_R2", False)),
                ran_R3=bool(validation.get("ran_R3", False)),
                ran_R4=bool(validation.get("ran_R4", False)),
                ran_R5=bool(validation.get("ran_R5", False)),
                issues=[
                    ValidationIssue(
                        rule=str(issue.get("rule") or ""),
                        severity=str(issue.get("severity") or ""),
                        message=str(issue.get("message") or ""),
                        suggested_fix=issue.get("suggested_fix"),
                    )
                    for issue in (validation.get("issues") or [])
                    if isinstance(issue, dict)
                ],
                last_validated=validation.get("last_validated"),
            ),
            modification_history=[
                ModificationRecord(
                    date=str(record.get("date") or ""),
                    actor=str(record.get("actor") or ""),
                    change_description=str(record.get("change_description") or ""),
                )
                for record in (raw.get("modification_history") or [])
                if isinstance(record, dict)
            ],
            reliability=str(raw.get("reliability") or ""),
            confidence=confidence,
            known_limitations=[str(item) for item in (raw.get("known_limitations") or [])],
            content_hash=str(raw.get("content_hash") or ""),
            change=str(raw.get("change") or ""),
            strict=strict,
        )

    @classmethod
    def from_yaml(cls, text: str, *, strict: bool = False) -> "Pedigree":
        data = yaml.safe_load(text)
        if data is not None and not isinstance(data, dict):
            raise PedigreeValidationError("", "record", "expected a YAML mapping")
        return cls.from_dict(data, strict=strict)


def _optional_float(view_id: str, field_name: str, value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise PedigreeValidationError(view_id, field_name, "must be a number")
    return float(value)
