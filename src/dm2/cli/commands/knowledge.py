"""Knowledge subcommands — DM2 knowledge base queries for AI agents."""

from dataclasses import asdict

import typer

knowledge_app = typer.Typer(help="DM2 知识库查询", no_args_is_help=True)


@knowledge_app.command()
def search(
    query: str = typer.Argument(..., help="搜索关键词"),
    limit: int = typer.Option(10, "--limit", "-n", help="返回结果数量"),
    json_flag: bool = typer.Option(False, "--json", "-j", help="输出结构化 JSON（供 AI Agent 使用）"),
):
    """搜索 DM2 术语（名称、别名、定义）"""
    from dm2.core.knowledge.api import KnowledgeAPI
    api = KnowledgeAPI()
    results = api.search_terms(query)[:limit]
    data = [asdict(r) for r in results]
    if json_flag:
        from dm2.cli.json_output import json_success
        json_success({"query": query, "count": len(data), "results": data})
        return
    for r in data:
        typer.echo(f"\n{r['term']}")
        typer.echo(f"  {r['definition'][:120]}...")
        if r['aliases']:
            typer.echo(f"  别名: {', '.join(r['aliases'])}")


@knowledge_app.command()
def concept(
    name: str = typer.Argument(..., help="概念名称"),
    json_flag: bool = typer.Option(False, "--json", "-j", help="输出结构化 JSON（供 AI Agent 使用）"),
):
    """查看 DM2 概念详情（含关系）"""
    from dm2.core.knowledge.api import KnowledgeAPI
    api = KnowledgeAPI()
    c = api.get_concept(name)
    if not c:
        if json_flag:
            from dm2.cli.json_output import json_error
            json_error("NOT_FOUND", f"未找到概念: {name}")
            raise typer.Exit(1)
        typer.echo(f"未找到概念: {name}")
        raise typer.Exit(1)
    if json_flag:
        from dm2.cli.json_output import json_success
        json_success(asdict(c))
        return
    typer.echo(f"{c.name} [{c.dm2_type}]")
    typer.echo(f"  层级: {c.layer} / {c.subtype}")
    typer.echo(f"  定义: {c.definition}")
    typer.echo(f"  关系: {c.relationships}")
    typer.echo(f"  标签: {c.tags}")


@knowledge_app.command()
def views(
    viewpoint: str = typer.Option("", "--type", "-t", help="按视点过滤 (All/OV/SV/CV/DIV/StdV)"),
    json_flag: bool = typer.Option(False, "--json", "-j", help="输出结构化 JSON（供 AI Agent 使用）"),
):
    """列出 DoDAF 视图"""
    from dm2.core.knowledge.api import KnowledgeAPI
    api = KnowledgeAPI()
    if viewpoint:
        vlist = api.get_views_by_viewpoint(viewpoint)
    else:
        vlist = api.get_all_views()
    summary_fields = {"view_id", "view_name", "viewpoint", "description", "dependencies"}
    data = [{k: v for k, v in asdict(v).items() if k in summary_fields} for v in vlist]
    if json_flag:
        from dm2.cli.json_output import json_success
        json_success({"viewpoint": viewpoint or "all", "count": len(data), "views": data})
        return
    typer.echo(f"视图 ({len(data)}):")
    for v in data:
        typer.echo(f"  {v['view_id']:<12} {v['view_name']:<30} [{v['viewpoint']}]")


@knowledge_app.command()
def view(
    view_id: str = typer.Argument(..., help="视图 ID（如 OV-1, CV-2）"),
    json_flag: bool = typer.Option(False, "--json", "-j", help="输出结构化 JSON（供 AI Agent 使用）"),
):
    """查看单个视图完整元数据"""
    from dm2.core.knowledge.api import KnowledgeAPI
    api = KnowledgeAPI()
    v = api.get_view(view_id)
    if not v:
        if json_flag:
            from dm2.cli.json_output import json_error
            json_error("NOT_FOUND", f"未找到视图: {view_id}")
            raise typer.Exit(1)
        typer.echo(f"未找到视图: {view_id}")
        raise typer.Exit(1)
    data = asdict(v)
    if json_flag:
        from dm2.cli.json_output import json_success
        json_success(data)
        return
    typer.echo(f"{v.view_id} {v.view_name} [{v.viewpoint}]")
    typer.echo(f"  描述: {v.description}")
    typer.echo(f"  依赖: {v.dependencies}")
    typer.echo(f"  被依赖: {v.downstream}")
    typer.echo(f"  DM2 数据组: {v.dm2_groups}")
    typer.echo(f"  优先级: {v.priority}")


@knowledge_app.command()
def stats(
    json_flag: bool = typer.Option(False, "--json", "-j", help="输出结构化 JSON（供 AI Agent 使用）"),
):
    """DM2 知识库统计"""
    from dm2.core.knowledge.api import KnowledgeAPI
    api = KnowledgeAPI()
    s = api.get_statistics()
    if json_flag:
        from dm2.cli.json_output import json_success
        json_success(s)
        return
    typer.echo(f"术语: {s['total_terms']}")
    typer.echo(f"概念: {s['total_concepts']}")
    typer.echo(f"视图: {s['total_views']}")


def register_knowledge_commands(app: typer.Typer) -> None:
    """Register knowledge subcommands on the main app."""
    app.add_typer(knowledge_app, name="knowledge")
