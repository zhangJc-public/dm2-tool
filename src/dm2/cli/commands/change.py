"""Change subcommands — architecture change lifecycle management."""

import typer

change_app = typer.Typer(help="架构变更管理", no_args_is_help=True)


def _require_project():
    """确保当前在 .dm2 项目中"""
    from dm2.utils.paths import is_dm2_project
    if not is_dm2_project():
        typer.echo("错误: 当前目录不在 .dm2 项目中。请先运行 dm2 init")
        raise typer.Exit(1)


@change_app.command()
def new(
    name: str = typer.Argument(..., help="变更名称"),
    json_flag: bool = typer.Option(False, "--json", "-j", help="输出结构化 JSON（供 AI Agent 使用）"),
):
    """创建新的架构变更"""
    _require_project()
    from dm2.core.changes.manager import ChangeManager
    mgr = ChangeManager()
    path = mgr.create(name)
    if json_flag:
        from dm2.cli.json_output import json_success
        json_success({"name": name, "path": str(path), "status": "open"})
        return
    typer.echo(f"✅ 变更已创建: {name}")
    typer.echo(f"   路径: {path}")


@change_app.command()
def status(
    name: str = typer.Option("", "--change", "-c", help="变更名称"),
    json_flag: bool = typer.Option(False, "--json", "-j", help="输出结构化 JSON（供 AI Agent 使用）"),
):
    """查看变更状态与产物进度"""
    _require_project()
    from dm2.core.changes.manager import ChangeManager
    mgr = ChangeManager()
    if name:
        state = mgr.load_state(name)
        if not state:
            if json_flag:
                from dm2.cli.json_output import json_error
                json_error("NOT_FOUND", f"未找到变更: {name}")
                raise typer.Exit(1)
            typer.echo(f"未找到变更: {name}")
            raise typer.Exit(1)
        if json_flag:
            from dm2.cli.json_output import json_success
            json_success(state)
            return
        typer.echo(f"变更: {name}")
        typer.echo(f"  状态: {state['change']['status']}")
        typer.echo(f"  产物: {state.get('artifacts', {})}")
    else:
        changes = mgr.list_changes()
        data = [{"name": c.name, "status": c.status.value, "created_at": c.created_at, "artifact_count": c.artifact_count, "artifact_done": c.artifact_done} for c in changes]
        if json_flag:
            from dm2.cli.json_output import json_success
            json_success({"changes": data})
            return
        typer.echo(f"变更 ({len(data)}):")
        for c in data:
            typer.echo(f"  {c['name']:<30} [{c['status']}] {c['artifact_done']}/{c['artifact_count']}")


@change_app.command()
def list_changes(
    json_flag: bool = typer.Option(False, "--json", "-j", help="输出结构化 JSON（供 AI Agent 使用）"),
):
    """列出所有活跃变更"""
    _require_project()
    from dm2.core.changes.manager import ChangeManager
    mgr = ChangeManager()
    changes = mgr.list_changes()
    data = [{"name": c.name, "status": c.status.value, "created_at": c.created_at, "modified_at": c.modified_at, "artifact_count": c.artifact_count, "artifact_done": c.artifact_done} for c in changes]
    if json_flag:
        from dm2.cli.json_output import json_success
        json_success({"changes": data})
        return
    if not data:
        typer.echo("暂无活跃变更。")
        return
    typer.echo(f"变更 ({len(data)}):")
    for c in data:
        typer.echo(f"  {c['name']:<30} [{c['status']}] {c['artifact_done']}/{c['artifact_count']}")


@change_app.command()
def archive_change(
    name: str = typer.Argument(..., help="变更名称"),
    json_flag: bool = typer.Option(False, "--json", "-j", help="输出结构化 JSON（供 AI Agent 使用）"),
):
    """归档变更（使用 ChangeManager）"""
    _require_project()
    from dm2.core.changes.manager import ChangeManager
    mgr = ChangeManager()
    try:
        dst = mgr.archive(name)
        if json_flag:
            from dm2.cli.json_output import json_success
            json_success({"name": name, "archived_to": str(dst)})
            return
        typer.echo(f"✅ 已归档: {name} → {dst.name}")
    except Exception as e:
        if json_flag:
            from dm2.cli.json_output import json_error
            json_error("ARCHIVE_FAILED", str(e))
            raise typer.Exit(1)
        typer.echo(f"错误: {e}")
        raise typer.Exit(1)


def register_change_commands(app: typer.Typer) -> None:
    """Register change subcommands on the main app."""
    app.add_typer(change_app, name="change")
