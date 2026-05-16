"""View subcommands — DoDAF view lifecycle management."""

import typer

view_app = typer.Typer(help="DoDAF 视图管理", no_args_is_help=True)


def register_view_commands(app: typer.Typer):
    app.add_typer(view_app, name="view")


@view_app.command(name="list")
def list_views(
    status: str = typer.Option(None, "--status", "-s", help="按状态过滤 (pending, in_progress, generated, verified)"),
    json_flag: bool = typer.Option(False, "--json", "-j", help="输出结构化 JSON（供 AI Agent 使用）"),
):
    """列出项目中的视图及其生成状态"""
    from dm2.core.views.manager import ViewManager, ViewStatus

    vm = ViewManager()

    status_filter = None
    if status:
        try:
            status_filter = ViewStatus(status)
        except ValueError:
            if json_flag:
                from dm2.cli.json_output import json_error
                json_error("INVALID_STATUS", f"无效的状态值: {status}，有效值: pending, in_progress, generated, verified")
                return
            typer.echo(f"无效的状态值: {status}")
            raise typer.Exit(1)

    views = vm.list_views(status_filter)

    if json_flag:
        from dm2.cli.json_output import json_success
        json_success({
            "views": [
                {
                    "id": v.id,
                    "status": v.status.value,
                    "generated_at": v.generated_at,
                    "verified_at": v.verified_at,
                    "output_path": v.output_path,
                    "change": v.change_name,
                }
                for v in views
            ],
            "count": len(views),
        })
        return

    if not views:
        typer.echo("(没有找到视图)")
        return

    typer.echo(f"{'View ID':<12} {'Status':<16} {'Generated':<22} {'Verified':<22}")
    typer.echo("-" * 72)
    for v in views:
        typer.echo(f"{v.id:<12} {v.status.value:<16} {v.generated_at[:19]:<22} {v.verified_at[:19]:<22}")


@view_app.command(name="register")
def register_view(
    view_id: str = typer.Argument(..., help="视图 ID，如 OV-1"),
    change: str = typer.Option("", "--change", "-c", help="变更名称（必填）"),
    path: str = typer.Option("", "--path", "-p", help="视图文件路径"),
):
    """注册生成的视图（供 AI Agent 同步状态）"""
    from dm2.cli.json_output import json_error, json_success
    from dm2.core.views.manager import ViewManager

    if not change:
        json_error("MISSING_ARG", "请提供 --change 参数")
        raise typer.Exit(1)

    vm = ViewManager()
    vm.register_view(view_id, output_path=path, change_name=change)
    json_success({
        "view_id": view_id,
        "change": change,
        "output_path": path,
    })
