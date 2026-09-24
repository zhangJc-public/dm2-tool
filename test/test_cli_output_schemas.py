"""Guard that dm2 CLI JSON output matches the schemas declared in ``schemas/``.

Spec: openspec/specs/cli-json-contract

The directory ``schemas/`` declares the machine-readable shape of dm2's JSON
output. Before this test existed those files had no consumer at all, so they
drifted silently: ``generate.json`` still described the removed LLM content
generation, ``analyze.json`` still required a ``priority`` field the recommender
no longer emits, and ``cynefin.json`` used Chinese domain labels for a field that
actually carries the enum name and was missing ``Disorder``.

``_validate`` implements the subset of JSON Schema draft 2020-12 that these
files use. It deliberately **fails loudly on any keyword it does not implement**,
so an unsupported assertion can never turn into a silent pass.
"""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from dm2.cli.main import app

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = REPO_ROOT / "schemas"

#: Keywords this validator implements. Anything else is a hard error.
_ANNOTATIONS = {"$schema", "$id", "title", "description"}
_ASSERTIONS = {
    "type",
    "required",
    "enum",
    "minimum",
    "maximum",
    "properties",
    "items",
    "additionalProperties",
    "oneOf",
}
SUPPORTED_KEYWORDS = _ANNOTATIONS | _ASSERTIONS

_PYTHON_TYPES = {
    "object": dict,
    "string": str,
    "array": list,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
}


def unsupported_keywords(schema, path="root"):
    """Return ``path.keyword`` for every keyword outside the implemented subset."""
    found = []
    if isinstance(schema, dict):
        for keyword, value in schema.items():
            if keyword not in SUPPORTED_KEYWORDS:
                found.append(f"{path}.{keyword}")
            if keyword == "properties":
                for name, sub in value.items():
                    found += unsupported_keywords(sub, f"{path}.properties.{name}")
            elif keyword == "items":
                found += unsupported_keywords(value, f"{path}.items")
            elif keyword == "additionalProperties" and isinstance(value, dict):
                found += unsupported_keywords(value, f"{path}.additionalProperties")
            elif keyword == "oneOf":
                for index, sub in enumerate(value):
                    found += unsupported_keywords(sub, f"{path}.oneOf[{index}]")
    return found


def validate(instance, schema, path="data"):
    """Return a list of human-readable contract violations (empty means valid)."""
    unsupported = unsupported_keywords(schema, path)
    assert not unsupported, f"schema 使用了未实现的关键字: {unsupported}"

    errors = []

    if "oneOf" in schema:
        matching = sum(
            1 for sub in schema["oneOf"] if not validate(instance, sub, path)
        )
        if matching != 1:
            errors.append(f"{path}: oneOf 匹配 {matching} 个分支（应恰好 1 个）")
        return errors

    declared = schema.get("type")
    if declared:
        expected = _PYTHON_TYPES.get(declared)
        if expected is not None:
            wrong = not isinstance(instance, expected)
            # bool is an int subclass; a JSON boolean is not a JSON integer.
            if declared == "integer" and isinstance(instance, bool):
                wrong = True
            if wrong:
                return [f"{path}: 期望 {declared}，实为 {type(instance).__name__}"]

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} 不在 enum {schema['enum']}")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: {instance} < minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: {instance} > maximum {schema['maximum']}")

    if isinstance(instance, dict):
        for name in schema.get("required", []):
            if name not in instance:
                errors.append(f"{path}: 缺 required 字段 '{name}'")
        properties = schema.get("properties", {})
        for name, sub in properties.items():
            if name in instance:
                errors += validate(instance[name], sub, f"{path}.{name}")
        additional = schema.get("additionalProperties")
        if isinstance(additional, dict):
            for name, value in instance.items():
                if name not in properties:
                    errors += validate(value, additional, f"{path}.{name}")

    if isinstance(instance, list) and "items" in schema:
        for index, value in enumerate(instance):
            errors += validate(value, schema["items"], f"{path}[{index}]")

    return errors


def load_schema(name):
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))


def _payload(result):
    """Parse a CliRunner result's stdout as a dm2 envelope."""
    return json.loads(result.stdout)


# ── validator self-tests ─────────────────────────────────────────────────────


def test_every_schema_uses_only_implemented_keywords():
    """A schema keyword the validator ignores would silently weaken the guard."""
    offenders = {
        path.name: unsupported_keywords(load_schema(path.name))
        for path in sorted(SCHEMA_DIR.glob("*.json"))
    }
    offenders = {name: keys for name, keys in offenders.items() if keys}
    assert not offenders, f"以下 schema 使用了未实现的关键字: {offenders}"


def test_validator_fails_loudly_on_unsupported_keyword():
    with pytest.raises(AssertionError):
        validate({"id": "OV-1"}, {"type": "object", "patternProperties": {}})


def test_validator_detects_violations():
    schema = {
        "type": "object",
        "properties": {"count": {"type": "integer", "minimum": 1}},
        "required": ["count", "name"],
    }
    assert validate({"count": 1, "name": "x"}, schema) == []
    assert any("缺 required" in e for e in validate({"count": 1}, schema))
    assert any("期望 integer" in e for e in validate({"count": "1", "name": "x"}, schema))
    assert any("minimum" in e for e in validate({"count": 0, "name": "x"}, schema))
    assert any("期望 integer" in e for e in validate({"count": True, "name": "x"}, schema))


# ── envelope contract (schemas/common.json) ──────────────────────────────────


def test_success_envelope_satisfies_common_schema(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["knowledge", "stats", "--json"])
    assert result.exit_code == 0, result.stdout
    assert validate(_payload(result), load_schema("common.json")) == []


def test_error_envelope_satisfies_common_schema(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["list", "--json"])
    assert result.exit_code != 0
    payload = _payload(result)
    assert payload["status"] == "error"
    assert validate(payload, load_schema("common.json")) == []


# ── per-command payload contracts ────────────────────────────────────────────


@pytest.fixture
def project(tmp_path, monkeypatch):
    """A freshly initialised .dm2 project; the state-bearing commands need one."""
    monkeypatch.chdir(tmp_path)
    assert CliRunner().invoke(app, ["init", ".", "-j"]).exit_code == 0
    return tmp_path


SCHEMA_CASES = [
    ("status.json", ["status", "--json"]),
    ("analyze.json", ["analyze", "-d", "作战节点连接与资源流", "--json"]),
    ("cynefin.json", ["cynefin", "-d", "作战节点连接与资源流", "--json"]),
    ("run.json", ["run", "--agent", "-d", "demo system", "--json"]),
]


@pytest.mark.parametrize("schema_name,args", SCHEMA_CASES, ids=[c[0] for c in SCHEMA_CASES])
def test_command_data_satisfies_declared_schema(schema_name, args, project):
    result = CliRunner().invoke(app, args)
    assert result.exit_code == 0, result.stdout
    errors = validate(_payload(result)["data"], load_schema(schema_name))
    assert errors == [], f"{schema_name} 与 {args[0]} 实际输出不符:\n" + "\n".join(errors)


def test_removed_generate_schema_is_gone():
    """`generate.json` described LLM content generation, which dm2 no longer does."""
    assert not (SCHEMA_DIR / "generate.json").exists()
    assert not any(SCHEMA_DIR.glob("generate*.json"))
