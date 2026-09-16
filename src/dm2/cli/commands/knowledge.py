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
def term(
    name: str = typer.Argument(..., help="术语名称（支持别名匹配）"),
    json_flag: bool = typer.Option(False, "--json", "-j", help="输出结构化 JSON（供 AI Agent 使用）"),
):
    """查看术语详情（定义/别名/数据组/所需视图/关联端点）"""
    from dm2.core.knowledge.api import KnowledgeAPI
    api = KnowledgeAPI()
    detail = api.get_term_detail(name)
    if not detail:
        if json_flag:
            from dm2.cli.json_output import json_error
            json_error("NOT_FOUND", f"未找到术语: {name}")
            raise typer.Exit(1)
        typer.echo(f"未找到术语: {name}")
        raise typer.Exit(1)
    if json_flag:
        from dm2.cli.json_output import json_success
        json_success(detail)
        return
    typer.echo(f"{detail['term']}  {detail['id']}")
    typer.echo(f"  定义: {detail['definition'][:150]}")
    if detail["aliases"]:
        typer.echo(f"  别名: {', '.join(detail['aliases'])}")
    typer.echo(f"  数据组: {', '.join(detail['groups'])}")
    if detail.get("endpoints"):
        eps = " — ".join(f"{e['type']}({e['domain_role'] or e['ideas_role']})" for e in detail["endpoints"])
        typer.echo(f"  关联端点: {eps}")
    typer.echo(f"  必要视图 ({len(detail['views_necessary'])}): {', '.join(detail['views_necessary'])}")
    if detail["views_optional"]:
        typer.echo(f"  可选视图 ({len(detail['views_optional'])}): {', '.join(detail['views_optional'][:12])}")


@knowledge_app.command()
def taxonomy(
    type_name: str = typer.Argument(..., help="类型名（如 Performer、Guidance）"),
    json_flag: bool = typer.Option(False, "--json", "-j", help="输出结构化 JSON（供 AI Agent 使用）"),
):
    """查看类型分类学（父类/子类/Type-Individual 配对）"""
    from dm2.core.knowledge.api import KnowledgeAPI
    api = KnowledgeAPI()
    result = api.get_taxonomy(type_name)
    if not result:
        if json_flag:
            from dm2.cli.json_output import json_error
            json_error("NOT_FOUND", f"未找到类型: {type_name}")
            raise typer.Exit(1)
        typer.echo(f"未找到类型: {type_name}")
        raise typer.Exit(1)
    if json_flag:
        from dm2.cli.json_output import json_success
        json_success(result)
        return
    typer.echo(f"{result['type']}")
    if result["parents"]:
        typer.echo(f"  父类: {', '.join(result['parents'])}")
    typer.echo(f"  直接子类: {', '.join(result['subtypes_direct']) or '（无）'}")
    typer.echo(f"  全部子类: {', '.join(result['subtypes_transitive']) or '（无）'}")
    if result["powertype_pair"]:
        typer.echo(f"  Powertype 配对: {result['powertype_pair']}")


@knowledge_app.command()
def associations(
    type_name: str = typer.Option("", "--type", "-t", help="按端点类型过滤（分类学感知，如 Performer 含 System）"),
    group: str = typer.Option("", "--group", "-g", help="按数据组过滤（如 01-performer）"),
    json_flag: bool = typer.Option(False, "--json", "-j", help="输出结构化 JSON（供 AI Agent 使用）"),
):
    """查询 DM2 关联目录（端点类型 + IDEAS/领域角色）"""
    from dm2.core.knowledge.api import KnowledgeAPI
    api = KnowledgeAPI()
    results = api.get_associations(type_name=type_name, group_id=group)
    if json_flag:
        from dm2.cli.json_output import json_success
        json_success({"type": type_name, "group": group, "count": len(results), "associations": results})
        return
    typer.echo(f"关联 ({len(results)}):")
    for a in results:
        eps = " ─▶ ".join(
            f"{e['type']}({e['domain_role'] or e['ideas_role']})" if e["ideas_role"] or e["domain_role"]
            else e["type"]
            for e in a["endpoints"]
        )
        typer.echo(f"  {a['label']:<40} {eps}")


@knowledge_app.command()
def content(
    view_id: str = typer.Argument(..., help="视图 ID（如 OV-5b、CV-2）"),
    json_flag: bool = typer.Option(False, "--json", "-j", help="输出结构化 JSON（供 AI Agent 使用）"),
):
    """查看视图内容规范（必要术语/必要关联，源自怪物矩阵×元模型）"""
    from dm2.core.knowledge.api import KnowledgeAPI
    api = KnowledgeAPI()
    result = api.get_view_content(view_id)
    if not result:
        if json_flag:
            from dm2.cli.json_output import json_error
            json_error("NOT_FOUND", f"未找到视图: {view_id}")
            raise typer.Exit(1)
        typer.echo(f"未找到视图: {view_id}")
        raise typer.Exit(1)
    if json_flag:
        from dm2.cli.json_output import json_success
        json_success(result)
        return
    typer.echo(f"{result['view_id']} {result['view_name']}")
    typer.echo(f"  必要术语: {', '.join(result['necessary_terms'])}")
    typer.echo("  必要关联:")
    for a in result["necessary_associations"]:
        if a.get("endpoint_types"):
            typer.echo(f"    - {a['label']}: {' ─▶ '.join(a['endpoint_types'])}")
        else:
            typer.echo(f"    - {a['label']} (模式级，无端点定义)")
    typer.echo(f"  可选术语 (前 {len(result['optional_terms'])}): {', '.join(result['optional_terms'][:15])}")


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
