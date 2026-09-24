"""dm2 concern * — 架构关切模板查询（供 AI Agent 做关切-视图匹配推荐）"""

from pathlib import Path

import typer
import yaml

from dm2.utils.paths import KnowledgeBaseNotFound

concern_app = typer.Typer(help="架构关切模板查询", no_args_is_help=True)


def _get_concerns_path() -> Path:
    """定位 concerns.yaml（随 dm2-reference/ 分发）。

    Raises:
        KnowledgeBaseNotFound: 两处候选都不存在时。静默返回 ``None`` 会让
            ``dm2 concern list`` 把「找不到知识库」说成「没有关切模板」——
            这正是 D10 实测到的静默空答案。
    """
    _root = Path(__file__).parent.parent.parent.parent.parent  # src/dm2/cli/commands/ → 5 levels up
    candidates = [
        _root / "dm2-reference" / "concerns.yaml",
        _root / "dm2-reference" / "core" / "concerns.yaml",
    ]
    for path in candidates:
        if path.exists():
            return path
    raise KnowledgeBaseNotFound(
        "未找到关切模板文件 concerns.yaml。已检查：\n"
        + "\n".join(f"  - {candidate}" for candidate in candidates)
        + "\n请运行 dm2 init 创建项目本地副本，或改用 editable 安装（pip install -e .）。"
    )


def _load_concerns() -> list[dict]:
    path = _get_concerns_path()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data.get("concerns", [])


@concern_app.command(name="list")
def list_concerns(
    query: str = typer.Option("", "--query", "-q", help="按关键词过滤关切模板"),
    json_flag: bool = typer.Option(False, "--json", "-j", help="输出结构化 JSON（供 AI Agent 使用）"),
):
    """列出架构关切模板"""
    concerns = _load_concerns()

    if query:
        q = query.lower()
        concerns = [
            c for c in concerns
            if q in c.get("name", "").lower()
            or q in c.get("description", "").lower()
            or q in c.get("category", "").lower()
            or any(q in kw.lower() for kw in c.get("keywords", []))
        ]

    result = {
        "total": len(concerns),
        "concerns": [
            {
                "id": c["id"],
                "name": c["name"],
                "category": c.get("category", ""),
                "description": c.get("description", "").strip().replace("\n", " "),
                "expected_data_groups": c.get("expected_data_groups", []),
                "core_views": c.get("core_views", []),
                "keywords": c.get("keywords", []),
            }
            for c in concerns
        ],
    }

    if json_flag:
        from dm2.cli.json_output import json_success
        json_success(result)
        return

    if not concerns:
        typer.echo("未找到匹配的关切模板。")
        return

    total = len(_load_concerns())
    typer.echo(f"关切模板 ({len(concerns)}/{total}):\n")
    for c in concerns:
        typer.echo(f"  [{c.get('category', '')}] {c['name']}")
        desc = c.get("description", "").strip().replace("\n", " ")
        typer.echo(f"    {desc[:100]}{'...' if len(desc) > 100 else ''}")
        typer.echo(f"    数据组: {', '.join(c.get('expected_data_groups', []))}")
        typer.echo(f"    核心视图: {', '.join(c.get('core_views', []))}")
        typer.echo()
