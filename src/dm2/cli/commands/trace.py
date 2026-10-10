"""`dm2 trace` — record and query view provenance (DM2 V2.02 Pedigree).

The command persists what the external AI Agent states; dm2 never infers
reasoning. Field validation is lenient about completeness (an incomplete record
is a meaningful audit state) but strict about shape: malformed decision factors
or alternatives are rejected with ``INVALID_ARG``.
"""

from __future__ import annotations

import sys
from pathlib import Path

import typer
import yaml

from dm2.cli.json_output import json_error, json_success
from dm2.core.pedigree import completeness
from dm2.core.pedigree.model import Pedigree, PedigreeValidationError
from dm2.core.pedigree.store import PedigreeStore
from dm2.core.views.manager import ViewManager
from dm2.utils.frontmatter import FrontmatterParser
from dm2.utils.paths import get_project_root, is_dm2_project

trace_app = typer.Typer(help="视图溯源（Pedigree）记录与查询", no_args_is_help=True)


def _require_project(json_flag: bool) -> Path:
    """Guard that returns the project root (not the CWD)."""
    if not is_dm2_project():
        message = "当前目录不在 .dm2 项目中。请先运行 dm2 init"
        if json_flag:
            json_error("NOT_IN_PROJECT", message)
            raise typer.Exit(1)
        typer.echo(f"错误: {message}")
        raise typer.Exit(1)
    return get_project_root()


def _read_payload(text: str) -> dict:
    data = yaml.safe_load(text)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError("YAML 顶层必须是映射（mapping）")
    return data


def _pick(nested: dict, payload: dict, key: str):
    if nested.get(key) is not None:
        return nested[key]
    return payload.get(key)


def _merge_payload(record: Pedigree, payload: dict, summary: str) -> Pedigree:
    """Merge Agent-supplied fields into a record; only supplied keys change."""
    data = record.to_dict()
    data["reasoning"] = data.get("reasoning") or {}
    nested = payload.get("reasoning") if isinstance(payload.get("reasoning"), dict) else {}

    if summary:
        data["reasoning"]["summary"] = summary
    elif _pick(nested, payload, "summary") is not None:
        data["reasoning"]["summary"] = _pick(nested, payload, "summary")
    for key in ("decision_factors", "alternatives_considered"):
        value = _pick(nested, payload, key)
        if value is not None:
            data["reasoning"][key] = value
    if payload.get("known_limitations") is not None:
        data["known_limitations"] = payload["known_limitations"]
    for key in ("reliability", "confidence", "change"):
        if payload.get(key) is not None:
            data[key] = payload[key]
    for key in ("source", "author"):
        value = payload.get(key)
        if isinstance(value, dict):
            data[key] = {**(data.get(key) or {}), **{k: v for k, v in value.items() if v is not None}}
    return Pedigree.from_dict(data)


def _change_from_disk(root: Path, view_id: str) -> str:
    """Fallback change lookup for views missing from view-state.yaml."""
    changes_dir = root / "dm2-changes"
    if not changes_dir.exists():
        return ""
    for change_dir in sorted(changes_dir.iterdir()):
        views_dir = change_dir / "views"
        if views_dir.exists() and any(views_dir.glob(f"{view_id}.*")):
            return change_dir.name
    return ""


def _view_change(root: Path, view_id: str, vm: ViewManager) -> str:
    info = vm.get_view(view_id)
    return (info.change_name if info else "") or _change_from_disk(root, view_id)


@trace_app.command(name="record")
def record(
    view_id: str = typer.Argument(..., help="视图 ID，如 CV-1"),
    summary: str = typer.Option("", "--summary", help="生成视图的理由摘要（Agent 自述）"),
    reasoning_file: str = typer.Option("", "--reasoning-file", help="包含 reasoning/source/author 的 YAML 文件"),
    use_stdin: bool = typer.Option(False, "--stdin", help="从标准输入读取 YAML"),
    json_flag: bool = typer.Option(False, "--json", "-j", help="输出结构化 JSON（供 AI Agent 使用）"),
):
    """记录视图溯源（Agent 提交理由层；dm2 只持久化，不推断）"""
    root = _require_project(True)
    from dm2.core.pedigree.completeness import trace_enabled

    if not trace_enabled(root):
        json_error("TRACE_DISABLED", "当前项目 trace.enabled=false，已禁用溯源写入")
        raise typer.Exit(1)
    if reasoning_file and use_stdin:
        json_error("INVALID_ARG", "--reasoning-file 与 --stdin 只能二选一")
        raise typer.Exit(1)
    if not summary and not reasoning_file and not use_stdin:
        json_error("MISSING_ARG", "请提供 --summary，或用 --reasoning-file/--stdin 提交结构化溯源")
        raise typer.Exit(1)

    payload: dict = {}
    try:
        if reasoning_file:
            file_path = Path(reasoning_file)
            if not file_path.exists():
                json_error("FILE_NOT_FOUND", f"未找到文件: {reasoning_file}")
                raise typer.Exit(1)
            payload = _read_payload(file_path.read_text(encoding="utf-8"))
        elif use_stdin:
            payload = _read_payload(sys.stdin.read())
    except ValueError as error:
        json_error("INVALID_ARG", f"无法解析溯源 YAML: {error}")
        raise typer.Exit(1)

    store = PedigreeStore(root)
    vm = ViewManager(project_root=root)
    pedigree = store.load(view_id)
    if pedigree is None:
        pedigree = Pedigree.stub(view_id, change=_view_change(root, view_id, vm))

    try:
        merged = _merge_payload(pedigree, payload, summary)
    except PedigreeValidationError as error:
        json_error("INVALID_ARG", str(error))
        raise typer.Exit(1)

    reasoning_supplied = bool(summary) or payload.get("reasoning") is not None or any(
        payload.get(key) is not None
        for key in ("summary", "decision_factors", "alternatives_considered", "known_limitations")
    )
    if reasoning_supplied:
        merged.append_modification("agent", "reasoning recorded")
    path = store.save(merged)

    json_success({
        "view_id": view_id,
        "pedigree_id": merged.pedigree_id,
        "pedigree_status": completeness.status(merged),
        "pedigree_missing": completeness.missing_core_fields(merged),
        "reasoning_recorded": reasoning_supplied,
        "path": str(path),
    })


@trace_app.command(name="show")
def show(
    view_id: str = typer.Argument(..., help="视图 ID，如 CV-1"),
    json_flag: bool = typer.Option(False, "--json", "-j", help="输出结构化 JSON（供 AI Agent 使用）"),
):
    """显示一个视图的完整溯源记录"""
    root = _require_project(json_flag)
    record_obj = PedigreeStore(root).load(view_id)
    state = completeness.status(record_obj)
    missing = completeness.missing_core_fields(record_obj)

    if json_flag:
        json_success({
            "view_id": view_id,
            "pedigree": record_obj.to_dict() if record_obj is not None else None,
            "pedigree_status": state,
            "pedigree_missing": missing,
        })
        return

    if record_obj is None:
        typer.echo(f"没有找到视图 {view_id} 的溯源记录（pedigree_status: {state}）")
        return
    typer.echo(record_obj.to_yaml().rstrip())
    if missing:
        typer.echo(f"\n# 缺失核心字段: {', '.join(missing)}")


def _capability_matches(name: str, record: Pedigree, vm: ViewManager) -> bool:
    needle = name.casefold()
    if needle in (record.reasoning.summary or "").casefold():
        return True
    info = vm.get_view(record.view_id)
    if info and info.output_path:
        path = Path(info.output_path)
        if path.exists():
            frontmatter = FrontmatterParser.parse(path.read_text(encoding="utf-8", errors="replace")) or {}
            if needle in yaml.safe_dump(frontmatter, allow_unicode=True).casefold():
                return True
    return False


@trace_app.command(name="lineage")
def lineage(
    term: str = typer.Option("", "--term", help="按 DM2 术语查询（source.dm2_terms_used）"),
    capability: str = typer.Option("", "--capability", help="按能力名查询（reasoning.summary / 视图 frontmatter）"),
    json_flag: bool = typer.Option(False, "--json", "-j", help="输出结构化 JSON（供 AI Agent 使用）"),
):
    """跨变更追溯某个术语/能力被哪些视图引用"""
    root = _require_project(json_flag)
    if bool(term) == bool(capability):
        json_error("INVALID_ARG", "请且仅请提供一个: --term 或 --capability")
        raise typer.Exit(1)

    store = PedigreeStore(root)
    vm = ViewManager(project_root=root)
    rows = []
    for view_id in store.list_all():
        record_obj = store.load(view_id)
        if record_obj is None:
            continue
        if term:
            terms = record_obj.source.dm2_terms_used if record_obj.source else []
            if not any(item.term.casefold() == term.casefold() for item in terms):
                continue
        elif not _capability_matches(capability, record_obj, vm):
            continue
        rows.append({
            "view_id": view_id,
            "change": _view_change(root, view_id, vm),
            "creation_date": record_obj.creation_date,
            "confidence": record_obj.confidence,
            "pedigree_status": completeness.status(record_obj),
        })

    by_change: dict[str, list[str]] = {}
    for row in rows:
        by_change.setdefault(row["change"] or "(unknown)", []).append(row["view_id"])

    data = {
        "criterion": "term" if term else "capability",
        "value": term or capability,
        "count": len(rows),
        "views": rows,
        "by_change": by_change,
    }
    if json_flag:
        json_success(data)
        return

    if not rows:
        typer.echo(f"没有视图引用 {data['value']}")
        return
    typer.echo(f"{len(rows)} 个视图引用 {data['value']}:")
    for row in rows:
        typer.echo(f"  {row['view_id']:<12} change={row['change'] or '-'} pedigree={row['pedigree_status']}")


@trace_app.command(name="migrate")
def migrate(
    json_flag: bool = typer.Option(False, "--json", "-j", help="输出结构化 JSON（供 AI Agent 使用）"),
):
    """为既有视图回填 pedigree_status（不创建溯源记录）"""
    root = _require_project(json_flag)
    statuses = ViewManager(project_root=root).sync_pedigree_state()
    counted: dict[str, int] = {}
    for state in statuses.values():
        counted[state] = counted.get(state, 0) + 1

    if json_flag:
        json_success({"views": statuses, "summary": counted})
        return
    typer.echo(f"已回填 {len(statuses)} 个视图的溯源状态: " + ", ".join(
        f"{state}={count}" for state, count in sorted(counted.items())
    ))


def register_trace_commands(app: typer.Typer) -> None:
    app.add_typer(trace_app, name="trace")
