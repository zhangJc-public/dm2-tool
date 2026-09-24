"""View subcommands — DoDAF view lifecycle management."""

import typer

view_app = typer.Typer(help="DoDAF 视图管理", no_args_is_help=True)


def _require_project(json_flag: bool = False):
    """确保当前在 .dm2 项目中（JSON 模式输出错误信封）。

    view 命令读写 `<cwd>/.dm2/view-state.yaml`；ViewManager 以 CWD 作为
    project_root 回退，因此项目外调用会静默在任意目录创建 `.dm2/`。
    守卫必须发生在任何状态访问之前。
    """
    from dm2.utils.paths import is_dm2_project
    if not is_dm2_project():
        message = "当前目录不在 .dm2 项目中。请先运行 dm2 init"
        if json_flag:
            from dm2.cli.json_output import json_error
            json_error("NOT_IN_PROJECT", message)
            raise typer.Exit(1)
        typer.echo(f"错误: {message}")
        raise typer.Exit(1)


def register_view_commands(app: typer.Typer):
    app.add_typer(view_app, name="view")


@view_app.command(name="list")
def list_views(
    status: str = typer.Option(None, "--status", "-s", help="按状态过滤 (pending, in_progress, generated, verified)"),
    json_flag: bool = typer.Option(False, "--json", "-j", help="输出结构化 JSON（供 AI Agent 使用）"),
):
    """列出项目中的视图及其生成状态"""
    _require_project(json_flag)
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
    json_flag: bool = typer.Option(False, "--json", "-j", help="输出结构化 JSON（供 AI Agent 使用）"),
):
    """注册生成的视图（供 AI Agent 同步状态）"""
    from dm2.cli.json_output import json_error, json_success
    from dm2.core.views.manager import ViewManager

    # 该命令始终输出信封（无人类模式），但仍接受 --json，
    # 使技能模板中「总是传 --json」的约定普遍适用。
    # 守卫恒以信封形式报告失败。
    _require_project(True)
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
