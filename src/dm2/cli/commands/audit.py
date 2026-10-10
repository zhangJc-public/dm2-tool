"""`dm2 audit` / `dm2 audit-report` — provenance reports for engineering review.

Distinct from `dm2 validate`: validate checks whether a view is correct, audit
explains why it exists. Everything an AI Agent stated is labelled as such; only
the fact layer (registration, transitions, validation results) is dm2-observed.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional

import typer

from dm2.cli.json_output import json_error, json_success
from dm2.core.pedigree import completeness
from dm2.core.pedigree.model import Pedigree
from dm2.core.pedigree.store import PedigreeStore
from dm2.core.views.manager import ViewInfo, ViewManager
from dm2.utils.paths import KnowledgeBaseNotFound, get_project_root, is_dm2_project

#: Every Agent-stated field carries this label in the reports.
AGENT_STATED = "Agent 自述、未经验证"

_RULES = ("R1", "R2", "R3", "R4", "R5")


def _require_project(json_flag: bool) -> Path:
    if not is_dm2_project():
        message = "当前目录不在 .dm2 项目中。请先运行 dm2 init"
        if json_flag:
            json_error("NOT_IN_PROJECT", message)
            raise typer.Exit(1)
        typer.echo(f"错误: {message}")
        raise typer.Exit(1)
    return get_project_root()


def _write_report(root: Path, target: str, text: str) -> Path:
    path = Path(target)
    if not path.is_absolute():
        path = root / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _approval_label(pedigree: Pedigree) -> str:
    author = pedigree.author
    if author is None or not author.type:
        return "NOT RECORDED"
    return author.type + (f" ({author.model})" if author.model else "")


def _validation_label(pedigree: Optional[Pedigree]) -> str:
    if pedigree is None or pedigree.validation.last_validated is None:
        return "未校验"
    errors = sum(1 for issue in pedigree.validation.issues if issue.severity == "error")
    if errors:
        return f"有错误（{errors}）"
    return "通过"


def _view_report(view_id: str, pedigree: Optional[Pedigree], info: Optional[ViewInfo]) -> str:
    lifecycle = info.status.value if info else "unknown"
    lines = [
        f"# 溯源审计：{view_id}",
        "",
        f"- 生命周期状态: `{lifecycle}`",
        f"- 溯源状态: `{completeness.status(pedigree)}`",
        "",
    ]
    if pedigree is None:
        lines += [
            f"**No pedigree record found for view {view_id}**",
            "",
            f"当前生命周期状态: `{lifecycle}`",
            "",
            f"建议: 运行 `dm2 trace record {view_id}` 补录溯源。",
        ]
        return "\n".join(lines).rstrip() + "\n"

    author = pedigree.author
    lines += [
        "## 作者与时间",
        "",
        f"- 作者类型: `{author.type if author and author.type else 'NOT RECORDED'}`",
        f"- 模型: `{(author.model if author else '') or '-'}`",
        f"- 操作者: `{(author.operator if author else '') or '-'}`",
        f"- 创建时间: `{pedigree.creation_date or 'NOT RECORDED'}`",
        f"- 可靠性: `{pedigree.reliability}`",
        f"- 置信度: `{pedigree.confidence}`",
        f"- pedigree_id: `{pedigree.pedigree_id}`",
        "",
        "## 标准引用（Standard Reference）",
        "",
    ]
    source = pedigree.source
    if source and source.standard:
        lines += [f"- 标准: {source.standard}", f"- 章节: {source.section or '-'}"]
    else:
        lines += ["Standard reference: NOT RECORDED"]
    lines += [""]
    if source and source.dm2_terms_used:
        lines += ["引用的 DM2 术语:", ""]
        for term in source.dm2_terms_used:
            suffix = f" — `{term.definition_ref}`" if term.definition_ref else ""
            lines += [f"- `{term.term}`{suffix}"]
        lines += [""]
    if source and source.alignment_notes:
        lines += ["对齐说明:", "", source.alignment_notes, ""]

    lines += [f"## 理由摘要（{AGENT_STATED}）", "", pedigree.reasoning.summary or "NOT RECORDED", ""]

    lines += [f"## 决策因素（{AGENT_STATED}）", ""]
    if pedigree.reasoning.decision_factors:
        lines += ["| 因素 | 评分 | 来源 |", "|---|---|---|"]
        for factor in pedigree.reasoning.decision_factors:
            score = "-" if factor.score is None else str(factor.score)
            lines += [f"| {factor.factor} | {score} | {factor.source} |"]
    else:
        lines += ["NOT RECORDED"]
    lines += [""]

    lines += [f"## 备选方案（{AGENT_STATED}）", ""]
    if pedigree.reasoning.alternatives_considered:
        for alternative in pedigree.reasoning.alternatives_considered:
            lines += [f"- **{alternative.option}** — 否决原因: {alternative.rejected_because}"]
    else:
        lines += ["NOT RECORDED"]
    lines += [""]

    lines += [f"## 已知局限（{AGENT_STATED}）", ""]
    lines += [f"- {item}" for item in pedigree.known_limitations] or ["NOT RECORDED"]
    lines += [""]

    lines += ["## 修改历史", ""]
    if pedigree.modification_history:
        lines += ["| 时间 | 参与方 | 变更 |", "|---|---|---|"]
        for entry in pedigree.modification_history:
            lines += [f"| {entry.date} | {entry.actor} | {entry.change_description} |"]
    else:
        lines += ["NOT RECORDED"]
    lines += [""]

    validation = pedigree.validation
    ran = ", ".join(rule for rule in _RULES if getattr(validation, f"ran_{rule}")) or "-"
    lines += [
        "## 校验历史",
        "",
        f"- 最近校验: `{validation.last_validated or 'NOT RECORDED'}`",
        f"- 运行规则: {ran}",
        "",
    ]
    if validation.issues:
        lines += ["| 规则 | 级别 | 问题 | 建议修复 |", "|---|---|---|---|"]
        for issue in validation.issues:
            fix = issue.suggested_fix or "No automated fix available"
            lines += [f"| {issue.rule} | {issue.severity} | {issue.message} | {fix} |"]
    else:
        lines += ["- 无已知问题"]
    return "\n".join(lines).rstrip() + "\n"


def audit(
    view_id: str = typer.Argument(..., help="视图 ID，如 CV-1"),
    output: str = typer.Option("", "--output", help="报告输出路径（默认 .dm2/audit/<view_id>-audit.md）"),
    json_flag: bool = typer.Option(False, "--json", "-j", help="输出结构化 JSON（供 AI Agent 使用）"),
):
    """审计一个视图：为什么它是这个样子（Markdown 报告）"""
    root = _require_project(json_flag)
    pedigree = PedigreeStore(root).load(view_id)
    info = ViewManager(project_root=root).get_view(view_id)
    markdown = _view_report(view_id, pedigree, info)
    target = output or f".dm2/audit/{view_id}-audit.md"
    path = _write_report(root, target, markdown)

    if json_flag:
        json_success({
            "view_id": view_id,
            "pedigree": pedigree.to_dict() if pedigree is not None else None,
            "lifecycle_state": info.status.value if info else "",
            "generated_at": info.generated_at if info else "",
            "pedigree_status": completeness.status(pedigree),
            "pedigree_missing": completeness.missing_core_fields(pedigree),
            "output_path": str(path),
        })
        return
    typer.echo(markdown.rstrip())


def _knowledge():
    """KnowledgeAPI, or ``None`` when the knowledge base is unavailable."""
    try:
        from dm2.core.knowledge.api import KnowledgeAPI

        return KnowledgeAPI()
    except KnowledgeBaseNotFound:
        return None


def _project_report(summary: dict, coverage: dict, entries: list, gaps: list, generated: str) -> str:
    lines = [
        f"# 项目溯源审计报告（{generated}）",
        "",
        "## 项目概要",
        "",
        f"- 视图总数: {summary['total_views']}",
        f"- 有溯源记录: {summary['with_pedigree']}",
        f"- 无溯源记录: {summary['without_pedigree']}",
    ]
    for state, count in sorted(summary["by_lifecycle_state"].items()):
        lines += [f"- 生命周期 `{state}`: {count}"]
    if summary["min_confidence"] is not None:
        lines += [f"- 置信度过滤: >= {summary['min_confidence']}（过滤掉 {summary['filtered_out']} 个视图）"]
    lines += ["", "## 数据组覆盖", ""]
    if coverage:
        for group, count in sorted(coverage.items()):
            lines += [f"- {group}: {count} 个视图"]
    else:
        lines += ["（无可统计的数据组）"]

    lines += ["", "## 逐视图", ""]
    if entries:
        lines += ["| 视图 | 名称 | 作者 | 创建时间 | 置信度 | 校验 | 溯源 |", "|---|---|---|---|---|---|---|"]
        for entry in entries:
            confidence = entry["confidence"] if entry["confidence"] is not None else "-"
            lines += [
                f"| {entry['view_id']} | {entry['title']} | {entry['author']} | "
                f"{entry['creation_date'] or '-'} | {confidence} | "
                f"{entry['validation_status']} | {entry['pedigree_status']} |"
            ]
    else:
        lines += ["（没有视图通过过滤条件）"]

    lines += ["", "## 溯源缺口（Trace gaps）", ""]
    if gaps:
        for view_id, reason in gaps:
            lines += [f"- `{view_id}`: {reason}"]
    else:
        lines += ["（无）"]
    return "\n".join(lines).rstrip() + "\n"


def audit_report(
    min_confidence: float = typer.Option(None, "--min-confidence", help="只列出 confidence >= 该值的视图"),
    output: str = typer.Option("", "--output", help="默认 .dm2/audit/project-audit-YYYYMMDD.md"),
    json_flag: bool = typer.Option(False, "--json", "-j", help="输出结构化 JSON（供 AI Agent 使用）"),
):
    """生成项目级溯源审计报告"""
    root = _require_project(json_flag)
    store = PedigreeStore(root)
    vm = ViewManager(project_root=root)
    views = vm.list_views()

    api = _knowledge()
    view_results = {info.id: (api.get_view(info.id) if api else None) for info in views}

    with_pedigree = 0
    filtered = 0
    by_state: dict[str, int] = {}
    entries: list[dict] = []
    gaps: list[tuple[str, str]] = []
    coverage: dict[str, int] = {}

    for info in views:
        by_state[info.status.value] = by_state.get(info.status.value, 0) + 1
        pedigree = store.load(info.id)
        state = completeness.status(pedigree)
        if pedigree is None:
            gaps.append((info.id, "无溯源记录（absent）"))
        else:
            with_pedigree += 1
            missing = completeness.missing_core_fields(pedigree)
            if missing:
                gaps.append((info.id, "缺核心字段: " + ", ".join(missing)))
            if not (pedigree.source and pedigree.source.standard):
                gaps.append((info.id, "标准出处未记录（source.standard 为空）"))
            result = view_results.get(info.id)
            for group in (result.dm2_groups if result else []) or []:
                coverage[group] = coverage.get(group, 0) + 1

        if min_confidence is not None and (pedigree is None or pedigree.confidence < min_confidence):
            filtered += 1
            continue
        result = view_results.get(info.id)
        entries.append({
            "view_id": info.id,
            "title": (result.view_name if result else "") or info.id,
            "author": _approval_label(pedigree) if pedigree else "NOT RECORDED",
            "creation_date": pedigree.creation_date if pedigree else "",
            "confidence": pedigree.confidence if pedigree else None,
            "validation_status": _validation_label(pedigree),
            "pedigree_status": state,
            "lifecycle_state": info.status.value,
        })

    summary = {
        "total_views": len(views),
        "by_lifecycle_state": by_state,
        "with_pedigree": with_pedigree,
        "without_pedigree": len(views) - with_pedigree,
        "filtered_out": filtered,
        "min_confidence": min_confidence,
    }
    generated = date.today().isoformat()
    markdown = _project_report(summary, coverage, entries, gaps, generated)
    target = output or f".dm2/audit/project-audit-{date.today():%Y%m%d}.md"
    path = _write_report(root, target, markdown)

    if json_flag:
        json_success({
            "summary": summary,
            "data_group_coverage": coverage,
            "views": entries,
            "trace_gaps": sorted({view_id for view_id, _ in gaps}),
            "output_path": str(path),
        })
        return
    typer.echo(markdown.rstrip())


def register_audit_commands(app: typer.Typer) -> None:
    """`dm2 audit <view>` and `dm2 audit-report` are both top-level commands."""
    app.command(name="audit")(audit)
    app.command(name="audit-report")(audit_report)
