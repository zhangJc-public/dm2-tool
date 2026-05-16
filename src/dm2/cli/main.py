"""DM2 CLI - 系统工程辅助工具命令行入口"""

import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

import typer

app = typer.Typer(
    name="dm2",
    help="DoDAF Meta Model 2.02 系统工程辅助工具",
    no_args_is_help=True,
)

REFERENCE_PATH = Path(__file__).parent.parent.parent.parent / "dm2-reference"
_CORE_PATH = REFERENCE_PATH / "core"
if _CORE_PATH.exists():
    REFERENCE_PATH = _CORE_PATH


def _json_option():
    """Factory for --json flag shared across commands."""
    return typer.Option(False, "--json", "-j", help="输出结构化 JSON（供 AI Agent 使用）")


def _require_project():
    """确保当前在 .dm2 项目中"""
    from dm2.utils.paths import is_dm2_project
    if not is_dm2_project():
        typer.echo("错误: 当前目录不在 .dm2 项目中。请先运行 dm2 init")
        raise typer.Exit(1)


# Register subcommand groups
from dm2.cli.commands.knowledge import register_knowledge_commands
from dm2.cli.commands.change import register_change_commands
from dm2.cli.commands.view import register_view_commands
from dm2.cli.commands.concern import concern_app
register_knowledge_commands(app)
register_change_commands(app)
register_view_commands(app)
app.add_typer(concern_app, name="concern")


@app.command()
def init(
    name: str = typer.Argument(".", help="项目目录名"),
    vault: Optional[str] = typer.Option(None, "--vault", "-v", help="关联的 Obsidian vault 路径（可选）"),
    json_flag: bool = typer.Option(False, "--json", "-j", help="输出结构化 JSON（供 AI Agent 使用）"),
):
    """在当前目录创建新的 DM2 项目"""

    target = Path.cwd() / name

    # 创建目录结构
    (target / ".dm2").mkdir(parents=True, exist_ok=True)

    # 从内置模板复制默认配置（或生成）
    import yaml
    template_config = {
        "views": {"include_mermaid": True, "include_timestamps": True},
        "consistency": {"check_enabled": True, "strict_mode": False},
    }
    if vault:
        template_config["vault_path"] = vault

    (target / ".dm2" / "config.yaml").write_text(
        yaml.dump(template_config, allow_unicode=True, default_flow_style=False)
    )

    # 创建标准子目录
    created_dirs = []
    for subdir in ["dm2-changes", "dm2-archive"]:
        (target / subdir).mkdir(parents=True, exist_ok=True)
        created_dirs.append(subdir)

    # 从模板生成 .claude/ 配置（skills + commands）
    from dm2.core.templates.generator import generate_agent_config
    from dm2.core.adapters.claude import ClaudeCodeAdapter
    from dm2 import __version__
    generated = generate_agent_config(target, __version__, ClaudeCodeAdapter())

    import shutil
    _dm2_root = Path(__file__).parent.parent.parent.parent

    # 复制参考知识库（views.yaml, terms, groups）到项目本地
    _ref_src = _dm2_root / "dm2-reference" / "core"
    _ref_dst = target / ".dm2" / "reference"
    ref_copied = 0
    if _ref_src.exists():
        _ref_dst.mkdir(parents=True, exist_ok=True)
        # views.yaml
        _views_src = _ref_src / "views.yaml"
        if _views_src.exists():
            shutil.copy2(str(_views_src), str(_ref_dst / "views.yaml"))
            ref_copied += 1
        # groups/ 目录（17 数据组模板）
        _groups_src = _ref_src / "groups"
        if _groups_src.exists() and not (_ref_dst / "groups").exists():
            shutil.copytree(str(_groups_src), str(_ref_dst / "groups"))
            ref_copied += 1
        # _dm2_v202_extract.json（DM2 术语库）
        _terms_src = _ref_src / "_dm2_v202_extract.json"
        if _terms_src.exists():
            shutil.copy2(str(_terms_src), str(_ref_dst / "_dm2_v202_extract.json"))
            ref_copied += 1
    # group-to-views.yaml（在 dm2-reference/ 根目录而非 core/ 下）
    _g2v_src = _dm2_root / "dm2-reference" / "group-to-views.yaml"
    if _g2v_src.exists():
        shutil.copy2(str(_g2v_src), str(_ref_dst / "group-to-views.yaml"))

    if json_flag:
        from dm2.cli.json_output import json_success
        json_success({
            "project_path": str(target.resolve()),
            "directories": created_dirs,
            "vault_path": vault,
            "claude_config": generated > 0,
        })
        return

    typer.echo(f"✅ DM2 项目已创建: {target.resolve()}")
    typer.echo("   目录结构:")
    typer.echo("     .dm2/config.yaml    - 项目配置")
    typer.echo("     .dm2/reference/     - 参考知识库（术语/视图/数据组）")
    typer.echo("     dm2-changes/        - 架构变更")
    typer.echo("     dm2-archive/        - 已归档变更")
    if generated > 0:
        typer.echo("     .claude/skills/     - Claude Code AI 技能")
        typer.echo("     .claude/commands/   - Claude Code 斜杠命令")


@app.command()
def list(
    json_flag: bool = typer.Option(False, "--json", "-j", help="输出结构化 JSON（供 AI Agent 使用）"),
):
    """列出项目中的架构变更"""
    _require_project()
    from dm2.utils.paths import get_project_root

    root = get_project_root()
    changes_dir = root / "dm2-changes"

    if not changes_dir.exists():
        if json_flag:
            from dm2.cli.json_output import json_success
            json_success({"changes": [], "archived_count": 0})
            return
        typer.echo("暂无变更。")
        return

    changes = sorted([d for d in changes_dir.iterdir() if d.is_dir()])
    archive_count = sum(1 for _ in (root / 'dm2-archive').iterdir() if _.is_dir())

    if json_flag:
        from dm2.cli.json_output import json_success
        change_list = []
        for c in changes:
            tasks_file = c / "tasks.md"
            if tasks_file.exists():
                content = tasks_file.read_text()
                done = content.count("[x]")
                total = done + content.count("[ ]")
                progress = f"{done}/{total}" if total > 0 else "?"
            else:
                progress = "未开始"
            change_list.append({"name": c.name, "progress": progress})
        json_success({"changes": change_list, "archived_count": archive_count})
        return

    if not changes:
        typer.echo("暂无变更。")
        return

    typer.echo(f"项目变更 ({len(changes)}):")
    typer.echo()
    for c in changes:
        tasks_file = c / "tasks.md"
        if tasks_file.exists():
            content = tasks_file.read_text()
            done = content.count("[x]")
            total = done + content.count("[ ]")
            status = f"{done}/{total}" if total > 0 else "?"
        else:
            status = "未开始"
        typer.echo(f"  {c.name:<30} [{status}]")
    typer.echo()
    typer.echo(f"已归档: {archive_count} 项")


@app.command()
def status(
    json_flag: bool = typer.Option(False, "--json", "-j", help="输出结构化 JSON"),
):
    """显示项目状态概览"""
    _require_project()
    from dm2.kernel.indexer import DM2KnowledgeIndexer

    indexer = DM2KnowledgeIndexer()
    indexer.load_all()

    stats = indexer.get_statistics()

    # Load analysis state
    analysis_state = {}
    _asf = Path.cwd() / ".dm2" / "analysis-state.yaml"
    if _asf.exists():
        import yaml as _yaml
        _raw = _yaml.safe_load(_asf.read_text(encoding='utf-8')) or {}
        analysis_state = {
            "cynefin": _raw.get("cynefin"),
            "analyze": _raw.get("analyze"),
        }

    # Load view progress
    from dm2.core.views.manager import ViewManager
    vm = ViewManager()
    view_progress = vm.get_progress()
    views_list = vm.list_views()

    if json_flag:
        from dm2.cli.json_output import json_success
        json_success({
            "knowledge_base": {
                "total_terms": stats["total_terms"],
                "total_concepts": stats["total_concepts"],
                "total_views": stats["total_views"],
            },
            "analysis": analysis_state,
            "views": {
                "progress": view_progress,
                "total": len(views_list),
                "items": [
                    {"id": v.id, "status": v.status.value}
                    for v in views_list
                ],
            },
        })
        return

    typer.echo("DM2 知识库状态:")
    typer.echo(f"  术语: {stats['total_terms']}")
    typer.echo(f"  概念: {stats['total_concepts']}")
    typer.echo(f"  视图模板: {stats['total_views']}")
    typer.echo()

    # Analysis state
    if analysis_state.get("cynefin") or analysis_state.get("analyze"):
        typer.echo("分析状态:")
        c = analysis_state.get("cynefin")
        if c:
            typer.echo(f"  Cynefin 域: {c.get('domain', '?')} (置信度 {c.get('confidence', 0):.0%})")
        a = analysis_state.get("analyze")
        if a:
            typer.echo(f"  6W 分析: {a.get('primary_6w', '?')} (置信度 {a.get('confidence', 0):.0%})")
            recs = a.get("recommended_views", [])
            if recs:
                typer.echo(f"  推荐视图: {len(recs)} 个")
        typer.echo()

    # View progress
    typer.echo("视图进度:")
    typer.echo(f"  待处理: {view_progress.get('pending', 0)}")
    typer.echo(f"  进行中: {view_progress.get('in_progress', 0)}")
    typer.echo(f"  已生成: {view_progress.get('generated', 0)}")
    typer.echo(f"  已验证: {view_progress.get('verified', 0)}")
    if views_list:
        typer.echo()
        for v in views_list:
            typer.echo(f"  {v.id:<12} [{v.status.value}]")


@app.command()
def archive(
    change: str = typer.Argument(..., help="变更名称"),
    json_flag: bool = typer.Option(False, "--json", "-j", help="输出结构化 JSON（供 AI Agent 使用）"),
):
    """归档一个架构变更"""
    _require_project()
    from datetime import date

    from dm2.utils.paths import get_project_root

    root = get_project_root()
    src = root / "dm2-changes" / change
    dst = root / "dm2-archive" / f"{date.today()}-{change}"

    if not src.exists():
        if json_flag:
            from dm2.cli.json_output import json_error
            json_error("NOT_FOUND", f"找不到变更 '{change}'")
            raise typer.Exit(1)
        typer.echo(f"错误: 找不到变更 '{change}'")
        raise typer.Exit(1)

    dst.parent.mkdir(exist_ok=True)
    src.rename(dst)

    if json_flag:
        from dm2.cli.json_output import json_success
        json_success({"change": change, "archived_to": dst.name})
        return

    typer.echo(f"✅ 已归档: {change} → {dst.name}")


def _derive_cynefin_from_description(desc: str) -> dict:
    """从描述文本自动推导 Cynefin 评估参数"""
    text = desc.lower()

    # 系统数量: 按关键词估算
    system_indicators = ["系统", "子系统", "节点", "组件", "模块", "平台", "设备",
                         "service", "微服务", "api", "数据库", "网络"]
    count = 0
    for kw in system_indicators:
        count += text.count(kw)
    systems = 3 if count <= 2 else 5 if count <= 5 else 8

    # 干系人复杂度
    stakeholder_kw = ["组织", "部门", "科室", "机构", "干系人", "甲方", "乙方",
                      "监管", "团队", "stakeholder"]
    stakeholder_hit = sum(1 for kw in stakeholder_kw if kw in text)
    stakeholders = "simple" if stakeholder_hit <= 1 else "medium" if stakeholder_hit <= 3 else "complex"

    # 不确定性
    uncertainty_kw = ["未知", "不确定", "动态", "变化", "新兴", "新业务", "创新",
                      "预测", "unknown", "uncertain"]
    uncertainty_hit = sum(1 for kw in uncertainty_kw if kw in text)
    uncertainty = "simple" if uncertainty_hit <= 1 else "medium" if uncertainty_hit <= 3 else "complex"

    # 规则复杂度
    rules_kw = ["合规", "法规", "标准", "等保", "规则", "规范", "法律", "监管",
                "安全", "审计", "加密", "compliance", "regulation", "security"]
    rules_hit = sum(1 for kw in rules_kw if kw in text)
    rules = "simple" if rules_hit <= 2 else "medium" if rules_hit <= 5 else "complex"

    return {
        "systems": systems,
        "stakeholders": stakeholders,
        "uncertainty": uncertainty,
        "rules": rules,
    }


@app.command()
def cynefin(
    systems: int = typer.Option(3, "--systems", "-s", help="系统数量"),
    stakeholders: str = typer.Option("medium", "--stakeholders", help="干系人复杂度"),
    uncertainty: str = typer.Option("medium", "--uncertainty", help="不确定性"),
    rules: str = typer.Option("medium", "--rules", "-r", help="规则复杂度"),
    description: str = typer.Option("", "--desc", "-d", help="系统/架构描述（自动推导参数）"),
    json_flag: bool = typer.Option(False, "--json", "-j", help="输出结构化 JSON"),
):
    """运行 Cynefin 复杂度评估"""
    from dm2.cognitive.cynefin_analyzer import CynefinAnalyzer

    analyzer = CynefinAnalyzer()

    # 如果提供了描述文本，自动推导参数
    if description:
        derived = _derive_cynefin_from_description(description)
        systems = derived["systems"]
        stakeholders = derived["stakeholders"]
        uncertainty = derived["uncertainty"]
        rules = derived["rules"]

    values = {
        "system_count": "simple" if systems <= 2 else "medium" if systems <= 5 else "complex",
        "time_span": "medium",
        "stakeholders": stakeholders,
        "uncertainty": uncertainty,
        "rule_complexity": rules,
    }
    result = analyzer.assess(values)

    # Silently persist analysis state for cross-session context
    from dm2.utils.paths import is_dm2_project
    if is_dm2_project():
        import yaml as _yaml
        from datetime import datetime as _dt
        _sf = Path.cwd() / ".dm2" / "analysis-state.yaml"
        _sf.parent.mkdir(parents=True, exist_ok=True)
        _existing = {}
        if _sf.exists():
            _existing = _yaml.safe_load(_sf.read_text(encoding='utf-8')) or {}
        _existing["cynefin"] = {
            "domain": result.domain_label,
            "confidence": result.confidence,
            "recommended_view_count": result.recommended_view_count,
            "timestamp": _dt.now().isoformat(),
        }
        _sf.write_text(_yaml.dump(_existing, allow_unicode=True, default_flow_style=False), encoding='utf-8')

    if json_flag:
        from dm2.cli.json_output import json_success
        json_success({
            "domain": result.domain_label,
            "confidence": result.confidence,
            "recommended_view_count": result.recommended_view_count,
            "reasoning": result.reasoning_details,
        })
        return

    typer.echo(f"Cynefin 域: {result.domain_label}")
    typer.echo(f"置信度: {result.confidence:.0%}")
    typer.echo(f"推荐视图数: {result.recommended_view_count}")
    typer.echo()
    typer.echo(result.reasoning_details)


@app.command()
def generate(
    view_id: str = typer.Argument("", help="视图 ID，如 OV-1, CV-1"),
    description: str = typer.Option("", "--desc", "-d", help="系统/架构描述"),
    list_views: bool = typer.Option(False, "--list", "-l", help="列出所有可用视图"),
    json_flag: bool = typer.Option(False, "--json", "-j", help="输出结构化 JSON（供 AI Agent 使用）"),
):
    """生成 DoDAF 视图指令（供 AI Agent 使用，无需 LLM）"""
    from dm2.cognitive.six_w_analyzer import SixWAnalyzer
    from dm2.cognitive.view_recommender import ViewRecommender
    from dm2.core.agent.instructions import VIEW_RULES
    from dm2.kernel.indexer import DM2KnowledgeIndexer

    if list_views:
        indexer = DM2KnowledgeIndexer()
        indexer.load_all()
        views_data = [{"view_id": v.view_id, "view_name": v.view_name, "viewpoint": v.viewpoint} for v in indexer.get_all_views()]
        if json_flag:
            from dm2.cli.json_output import json_success
            json_success({"views": views_data})
            return
        typer.echo("可用视图:")
        typer.echo()
        for v in views_data:
            typer.echo(f"  {v['view_id']:<12} {v['view_name']:<30} [{v['viewpoint']}]")
        return

    if not view_id or not description:
        from dm2.cli.json_output import json_error
        json_error("MISSING_ARG", "请提供视图 ID 和 --desc 描述")
        raise typer.Exit(1)

    indexer = DM2KnowledgeIndexer()
    indexer.load_all()

    # 1. 获取视图模板
    template = indexer.get_view_template(view_id)
    if not template:
        from dm2.cli.json_output import json_error
        json_error("INVALID_VIEW", f"未知视图: {view_id}")
        raise typer.Exit(1)

    # 2. 6W 分析
    analyzer = SixWAnalyzer()
    six_w = analyzer.analyze(description)

    # 3. 数据组激活检测
    recommender = ViewRecommender(indexer)
    activations = recommender.get_data_group_activation(description)

    # 4. 构建指令输出
    rules = VIEW_RULES.get(view_id, [])
    output = {
        "view_id": view_id,
        "view_name": template.view_name,
        "viewpoint": template.viewpoint,
        "description": template.description,
        "dm2_groups": template.dm2_groups,
        "dependencies": template.dependencies,
        "priority": template.priority,
        "six_w_analysis": {
            "primary": six_w.primary_w.value,
            "secondary": [w.value for w in six_w.secondary_ws],
            "entities": six_w.extracted_entities,
        },
        "data_group_activation": {
            a.group_id: a.score for a in activations if a.score > 0
        },
        "rules": rules,
        "required_data": template.required_data,
    }

    if json_flag:
        from dm2.cli.json_output import json_success
        json_success(output)
        return

    import yaml as _yaml
    typer.echo(f"## 视图生成指令: {view_id} ({template.view_name})\n")
    typer.echo(_yaml.dump(output, allow_unicode=True, default_flow_style=False))
    typer.echo(f"\n将此指令传递给 AI Agent 以生成 {view_id} 视图内容。")


@app.command()
def config(
    show_user: bool = typer.Option(False, "--user", "-u", help="显示当前用户级配置"),
    show_project: bool = typer.Option(False, "--project", "-p", help="显示当前项目级配置"),
    show_resolved: bool = typer.Option(False, "--resolved", "-r", help="显示合并解析后的配置"),
    set_key: str = typer.Option("", "--set", "-s", help="设置用户级配置项 (如 llm.model=claude-opus-4-7)"),
    json_flag: bool = typer.Option(False, "--json", "-j", help="输出结构化 JSON（供 AI Agent 使用）"),
):
    """查看和设置配置"""
    import yaml

    from dm2.config.manager import (
        get_project_config,
        get_user_config,
        resolve_config,
        set_user_config,
    )

    if set_key:
        if "=" not in set_key:
            if json_flag:
                from dm2.cli.json_output import json_error
                json_error("INVALID_FORMAT", f"无效格式 '{set_key}'，请使用 key=value")
                raise typer.Exit(1)
            typer.echo(f"错误: 无效格式 '{set_key}'，请使用 key=value")
            raise typer.Exit(1)
        key, value = set_key.split("=", 1)

        # LLM 配置已由 AI Agent 管理，dm2 不接受 llm.* 设置
        if key.startswith("llm"):
            msg = "LLM 配置由 AI Agent 层管理，dm2 工具不直接调用 LLM API。请通过 AI Agent 配置 LLM。"
            if json_flag:
                from dm2.cli.json_output import json_error
                json_error("LLM_CONFIG_REJECTED", msg)
                raise typer.Exit(1)
            typer.echo(f"[INFO] {msg}")
            raise typer.Exit(0)

        keys = key.split(".")
        update = value
        for k in reversed(keys):
            update = {k: update}
        path = set_user_config(update)
        _require_project()
        if json_flag:
            from dm2.cli.json_output import json_success
            json_success({"key": key, "value": value, "config_path": str(path)})
            return
        typer.echo(f"✅ 已更新用户配置: {path}")
        typer.echo(f"   {key} = {value}")
        return

    if show_user:
        config_data = get_user_config()
        source = "user"
    elif show_project:
        config_data = get_project_config()
        source = "project"
    elif show_resolved:
        config_data = resolve_config()
        source = "resolved"
    else:
        config_data = resolve_config()
        source = "resolved"

    if json_flag:
        from dm2.cli.json_output import json_success
        json_success({"source": source, "config": config_data})
        return

    labels = {"user": "用户级配置 (~/.config/dm2/config.yaml)", "project": "项目级配置 (.dm2/config.yaml)", "resolved": "合并解析配置"}
    typer.echo(f"{labels.get(source, source)}:")
    typer.echo(yaml.dump(config_data, allow_unicode=True, default_flow_style=False))


@app.command()
def analyze(
    description: str = typer.Option("", "--desc", "-d", help="系统/架构描述"),
    json_flag: bool = typer.Option(False, "--json", "-j", help="输出结构化 JSON"),
):
    """运行架构分析（6W 分析 + 视图推荐）"""
    from dm2.cognitive.six_w_analyzer import SixWAnalyzer
    from dm2.cognitive.view_recommender import ViewRecommender
    from dm2.kernel.indexer import DM2KnowledgeIndexer

    if not description:
        if json_flag:
            from dm2.cli.json_output import json_error
            json_error("MISSING_ARG", "请提供 --desc 参数")
            raise typer.Exit(1)
        typer.echo("请输入系统描述，例如:")
        typer.echo('  dm2 analyze -d "我们需要建设一个网络安全态势感知系统"')
        raise typer.Exit(1)

    indexer = DM2KnowledgeIndexer()
    indexer.load_all()

    analyzer = SixWAnalyzer()
    result = analyzer.analyze(description)

    recommender = ViewRecommender(indexer)
    recs = recommender.recommend(result, raw_description=description)

    # 数据组激活检测 (增强 JSON 输出)
    activations = recommender.get_data_group_activation(description)
    active_groups = [a for a in activations if a.score > 0.0]

    # Silently persist analysis state for cross-session context
    from dm2.utils.paths import is_dm2_project as _is_proj
    if _is_proj():
        import yaml as _yaml
        from datetime import datetime as _dt
        _sf = Path.cwd() / ".dm2" / "analysis-state.yaml"
        _sf.parent.mkdir(parents=True, exist_ok=True)
        _existing = {}
        if _sf.exists():
            _existing = _yaml.safe_load(_sf.read_text(encoding='utf-8')) or {}
        _existing["analyze"] = {
            "primary_6w": result.primary_w.value,
            "secondary_6ws": [w.value for w in result.secondary_ws],
            "confidence": result.confidence,
            "data_group_activation": {
                a.group_id: a.score for a in activations
            },
            "recommended_views": [
                {"view_id": r.view_id, "view_name": r.view_name, "priority": r.priority}
                for r in recs[:10]
            ],
            "timestamp": _dt.now().isoformat(),
        }
        _sf.write_text(_yaml.dump(_existing, allow_unicode=True, default_flow_style=False), encoding='utf-8')

    if json_flag:
        from dm2.cli.json_output import json_success

        # 构建 group_to_views 映射
        group_to_views = {}
        for a in activations:
            meta = recommender.activator.get_group_meta(a.group_id)
            # 从 group-to-views.yaml 获取该组的视图
            group_views = []
            if recommender._group_to_views and "groups" in recommender._group_to_views:
                for g_entry in recommender._group_to_views["groups"]:
                    if g_entry["id"] == a.group_id:
                        group_views = [v["id"] for v in g_entry.get("group_views", [])]
                        break
            group_to_views[a.group_id] = {
                "name": meta.get("name", ""),
                "label": meta.get("label", ""),
                "description": meta.get("description", ""),
                "activation_score": a.score,
                "keywords_matched": a.keywords_matched,
                "mapped_views": group_views,
            }

        # 获取已完成的视图
        views_completed = []
        view_dependencies = {}
        from dm2.utils.paths import is_dm2_project as _is_proj2
        if _is_proj2():
            try:
                from dm2.core.views.manager import ViewManager, ViewStatus
                vm = ViewManager()
                views_completed = [
                    v.view_id for v in vm.list_views()
                    if v.status in (ViewStatus.GENERATED, ViewStatus.VERIFIED)
                ]
            except Exception:
                pass

        # 获取视图依赖关系
        deps = recommender._get_dependencies()
        for r in recs:
            view_dependencies[r.view_id] = deps.get(r.view_id, [])

        json_success({
            "primary_6w": result.primary_w.value,
            "secondary_6ws": [w.value for w in result.secondary_ws],
            "confidence": result.confidence,
            "extracted_entities": {
                k: v[:5] for k, v in result.extracted_entities.items() if v
            },
            "data_group_activation": {
                a.group_id: a.score for a in activations
            },
            "data_group_keywords_matched": {
                a.group_id: a.keywords_matched
                for a in activations if a.keywords_matched
            },
            "group_to_views": group_to_views,
            "candidate_views": [
                {
                    "view_id": r.view_id,
                    "view_name": r.view_name,
                    "relevance_score": r.relevance_score,
                    "dm2_groups": r.dm2_groups,
                }
                for r in recs
            ],
            "recommended_views": [
                {
                    "view_id": r.view_id,
                    "view_name": r.view_name,
                    "relevance_score": r.relevance_score,
                    "dm2_groups": r.dm2_groups,
                }
                for r in recs[:10]
            ],
            "views_completed": views_completed,
            "view_dependencies": view_dependencies,
            "suggested_views": result.suggested_views[:5],
        })
        return

    typer.echo()
    typer.echo(f"主要 6W: {result.primary_w.value}")
    typer.echo(f"次要 6W: {[w.value for w in result.secondary_ws]}")
    typer.echo(f"置信度: {result.confidence:.0%}")
    typer.echo()

    if result.extracted_entities:
        typer.echo("提取实体:")
        for entity_type, entities in result.extracted_entities.items():
            if entities:
                typer.echo(f"  {entity_type}: {', '.join(entities[:5])}")

    typer.echo()
    typer.echo(f"推荐视图 ({len(recs)} 个):")
    for r in recs[:10]:
        priority_label = ["", "必须", "推荐", "可选"][r.priority]
        typer.echo(f"  [{priority_label}] {r.view_id} {r.view_name} ({r.relevance_score:.0%})")

    typer.echo()
    typer.echo(f"建议视图: {', '.join(result.suggested_views[:5])}")


@app.command()
def validate(
    view_id: str = typer.Argument(None, help="要校验的视图 ID"),
    all_views: bool = typer.Option(False, "--all", help="校验所有已生成视图"),
    change: str = typer.Option("", "--change", "-c", help="变更名称（从 dm2-changes/<name>/views/ 读取视图）"),
    json_flag: bool = typer.Option(False, "--json", "-j", help="输出结构化 JSON（供 AI Agent 使用）"),
):
    """对已生成的 DoDAF 视图运行一致性检查"""
    from dm2.core.views.manager import ViewManager, ViewStatus
    from dm2.reasoning.consistency import ConsistencyChecker
    from dm2.utils.paths import get_project_root

    vm = ViewManager()

    # Determine which views to validate
    if all_views:
        views = vm.list_views()
        views = [v for v in views if v.status in (ViewStatus.GENERATED, ViewStatus.VERIFIED)]
    elif view_id:
        v = vm.get_view(view_id)
        if v is None:
            if json_flag:
                from dm2.cli.json_output import json_error
                json_error("VIEW_NOT_FOUND", f"视图 {view_id} 未找到")
                return
            typer.echo(f"错误: 视图 {view_id} 未找到")
            raise typer.Exit(1)
        views = [v]
    else:
        if json_flag:
            from dm2.cli.json_output import json_error
            json_error("NO_VIEW_SPECIFIED", "请指定视图 ID 或使用 --all")
            return
        typer.echo("请指定视图 ID 或使用 --all 校验所有视图")
        raise typer.Exit(1)

    if not views:
        if json_flag:
            from dm2.cli.json_output import json_success
            json_success({"issues": [], "summary": {"error": 0, "warning": 0, "info": 0}})
            return
        typer.echo("没有找到已生成的视图")
        return

    # Load view contents from change dir or output dir
    root = get_project_root()
    if change:
        views_dir = root / "dm2-changes" / change / "views"
    else:
        views_dir = Path.cwd() / "output"
    views_data = {}
    for v in views:
        # First try view-state tracked path, then search views dir
        view_path = None
        if v.output_path:
            p = Path(v.output_path)
            if p.exists():
                view_path = p
        if not view_path and views_dir.exists():
            for ext in (".html", ".md"):
                candidate = views_dir / f"{v.id}{ext}"
                if candidate.exists():
                    view_path = candidate
                    break
            if not view_path:
                for f in views_dir.glob(f"{v.id}*"):
                    view_path = f
                    break
        if view_path:
            views_data[v.id] = view_path.read_text(encoding='utf-8')

    # Run consistency check
    checker = ConsistencyChecker()
    issues = checker.check_views(views_data)

    # Auto-update verified status if no errors
    error_count = sum(1 for i in issues if i.severity.value == "error")
    if error_count == 0 and views_data:
        for v in views:
            vm.update_status(v.id, ViewStatus.VERIFIED)

    if json_flag:
        from dm2.cli.json_output import json_success
        json_success({
            "view_id": view_id if not all_views else None,
            "all_views": all_views,
            "views_checked": list(views_data.keys()),
            "issues": [
                {
                    "type": i.issue_type,
                    "severity": i.severity.value,
                    "message": i.message,
                    "view_id": i.view_id,
                    "related_views": i.related_views,
                    "suggestion": i.suggestion,
                }
                for i in issues
            ],
            "summary": {
                "error": sum(1 for i in issues if i.severity.value == "error"),
                "warning": sum(1 for i in issues if i.severity.value == "warning"),
                "info": sum(1 for i in issues if i.severity.value == "info"),
            },
            "verified": error_count == 0 and len(views_data) > 0,
        })
        return

    # Human-readable output
    if not issues:
        typer.echo("没有发现一致性问题")
        return

    typer.echo(f"\n一致性检查: {len(views_data)} 个视图, {len(issues)} 个问题\n")
    for severity in ["error", "warning", "info"]:
        sev_issues = [i for i in issues if i.severity.value == severity]
        if not sev_issues:
            continue
        label = {"error": "错误", "warning": "警告", "info": "信息"}[severity]
        typer.echo(f"## {label} ({len(sev_issues)})\n")
        for i in sev_issues:
            typer.echo(f"  [{severity.upper()}] {i.message}")
            if i.suggestion:
                typer.echo(f"         建议: {i.suggestion}")
            if i.view_id:
                typer.echo(f"         视图: {i.view_id}")
        typer.echo()


@app.command()
def completion(
    shell: str = typer.Argument("", help="Shell 类型 (bash/zsh/fish)，不指定则自动检测"),
    install: bool = typer.Option(False, "--install", "-i", help="自动安装到 shell 配置文件"),
):
    """生成 shell 自动补全脚本"""
    import os
    from pathlib import Path

    # 检测当前 shell
    if not shell:
        shell_path = Path(os.environ.get("SHELL", "/bin/bash"))
        shell = shell_path.stem
        if shell not in ("bash", "zsh", "fish"):
            shell = "bash"
            typer.echo(f"无法检测 shell，默认使用 {shell}")

    # 获取补全脚本
    if shell == "fish":
        result = _generate_fish_completion()
        rc_file = Path.home() / ".config" / "fish" / "completions" / "dm2.fish"
    elif shell == "zsh":
        result = _generate_zsh_completion()
        rc_file = Path.home() / ".zshrc"
    else:
        result = _generate_bash_completion()
        rc_file = Path.home() / ".bashrc"

    typer.echo(f"# {shell} 自动补全脚本")
    typer.echo(result)

    if install:
        if shell == "fish":
            rc_file.parent.mkdir(parents=True, exist_ok=True)
            rc_file.write_text(result)
        else:
            marker = "# >>> dm2 completion >>>"
            current = rc_file.read_text() if rc_file.exists() else ""
            if marker not in current:
                with open(rc_file, "a") as f:
                    f.write(f"\n{marker}\n{result}\n# <<< dm2 completion <<<\n")
        typer.echo()
        typer.echo(f"✅ 已安装到 {rc_file}，请运行 source {rc_file} 使其生效")


def _generate_bash_completion() -> str:
    return """_dm2_completion() {
    local IFS=$'\\n'
    COMPREPLY=($(dm2 __complete "${COMP_WORDS[@]:1}" 2>/dev/null))
}
complete -F _dm2_completion dm2"""


def _generate_zsh_completion() -> str:
    return """_dm2() {
    local completions=("${(@f)$(dm2 __complete "${words[@]:1}" 2>/dev/null)}")
    compadd -a completions
}
compdef _dm2 dm2"""


def _generate_fish_completion() -> str:
    return """function _dm2_completion
    dm2 __complete (commandline -cp) 2>/dev/null
end
complete -f -c dm2 -a '(_dm2_completion)'"""


@app.command(name="__complete", hidden=True)
def _complete_cmd(
    ctx: typer.Context,
    args: Optional[List[str]] = typer.Argument(None),
):
    """内部：生成补全候选项（供 shell completion 使用）"""
    cmd_args = args or []
    # 收集可用命令
    commands = []
    for cmd_info in app.registered_commands:
        if not cmd_info.hidden:
            commands.append(cmd_info.name or "")

    # 如果用户正在输入子命令，返回匹配的命令
    if len(cmd_args) == 0 or (len(cmd_args) == 1 and not cmd_args[0].startswith("-")):
        partial = cmd_args[0] if cmd_args else ""
        for cmd in commands:
            if cmd.startswith(partial) and cmd != "__complete":
                typer.echo(cmd)
    else:
        # 对于已输入的命令，尝试返回其选项
        command = cmd_args[0]
        for cmd_info in app.registered_commands:
            if cmd_info.name == command and not cmd_info.hidden:
                for param in cmd_info.params:
                    for opt in param.opts:
                        typer.echo(opt)
                break


@app.command()
def instructions(
    artifact_type: str = typer.Argument(..., help="构件类型: view/<view-id> 或 step/<step-id>"),
    change: str = typer.Option("", "--change", "-c", help="变更名称（view 类型需要）"),
    description: str = typer.Option("", "--desc", "-d", help="项目/系统描述"),
    json_flag: bool = typer.Option(False, "--json", "-j", help="输出结构化 JSON（供 AI Agent 使用）"),
):
    """生成 AI Agent 指令（供 Agent 使用的结构化任务描述）"""
    from dm2.core.agent.instructions import InstructionBuilder
    from dm2.core.knowledge.api import KnowledgeAPI
    from dm2.core.artifacts.graph import ArtifactGraph

    knowledge = KnowledgeAPI()
    graph = None
    from dm2.utils.paths import get_reference_path
    views_yaml = get_reference_path() / "views.yaml"
    if views_yaml.exists():
        graph = ArtifactGraph(str(views_yaml))

    builder = InstructionBuilder(knowledge, graph)

    # Resolve artifact type: accept "view/OV-2", "OV-2", "step/step1-intent-scope", "step1-intent-scope"
    is_step = False
    if artifact_type.startswith("view/"):
        view_id = artifact_type.split("/", 1)[1]
    elif artifact_type.startswith("step/"):
        step_id = artifact_type.split("/", 1)[1]
        is_step = True
    elif artifact_type.startswith(("OV-", "SV-", "CV-", "DIV-", "AV-", "PV-", "SvcV-", "StdV-")):
        view_id = artifact_type  # Bare view ID per spec convention
    elif artifact_type in ("step1-intent-scope", "step3-data-requirements", "step5-analysis", "step6-documentation"):
        step_id = artifact_type
        is_step = True
    else:
        if json_flag:
            from dm2.cli.json_output import json_error
            json_error("INVALID_TYPE", f"无效构件类型: {artifact_type}，应为 view/<id>、step/<id>、或视图 ID (OV-1 等)")
            raise typer.Exit(1)
        typer.echo(f"无效构件类型: {artifact_type}")
        raise typer.Exit(1)

    if is_step:
        if not description:
            from dm2.cli.json_output import json_error
            json_error("MISSING_ARG", "step 类型需要 --desc 参数描述系统")
            raise typer.Exit(1)
        instr = builder.build_step_instructions(step_id, description)
    else:
        if not description:
            description = "⚠️ 未提供 --desc 参数。建议使用 AskUserQuestion 工具与用户互动，提供几个讨论方向或预设选项，共同明确视图生成目标。"
        if change:
            from dm2.core.changes.manager import ChangeManager
            mgr = ChangeManager()
            state = mgr.load_state(change)
            completed = set()
            if state:
                for aid, ainfo in state.get("artifacts", {}).items():
                    if isinstance(ainfo, dict) and ainfo.get("status") == "done":
                        completed.add(aid)
            instr = builder.build_view_instructions(view_id, description, completed,
                                                       change_name=change)
        else:
            instr = builder.build_view_instructions(view_id, description)

    result = {
        "context": {
            "project_description": instr.context.project_description,
            "dm2_terms": instr.context.dm2_terms,
            "dm2_concepts": instr.context.dm2_concepts,
            "dependency_artifacts": instr.context.dependency_artifacts,
        },
        "rules": instr.rules,
        "template": instr.template,
        "output_path": instr.output_path,
    }

    if json_flag:
        from dm2.cli.json_output import json_success
        json_success(result)
        return

    import yaml
    typer.echo(yaml.dump(result, allow_unicode=True, default_flow_style=False))


@app.command()
def run(
    description: str = typer.Option("", "--desc", "-d", help="系统/架构描述"),
    resume: bool = typer.Option(False, "--resume", "-r", help="从上次中断处继续执行"),
    step: str = typer.Option("", "--step", "-s", help="单独执行指定步骤（step1-intent-scope / step3-data-requirements / step5-analysis / step6-documentation）"),
    show_progress: bool = typer.Option(False, "--progress", "-p", help="显示当前 pipeline 进度"),
    iterate: bool = typer.Option(False, "--iterate", "-i", help="触发迭代循环（重置所有步骤）"),
    agent: bool = typer.Option(False, "--agent", help="Agent 驱动模式（输出 JSON 指令供 AI Agent 执行）"),
    status_flag: bool = typer.Option(False, "--status", help="输出当前 pipeline 状态（JSON）"),
    instructions_flag: str = typer.Option("", "--instructions", help="获取指定步骤的 Agent 指令"),
    complete_step: str = typer.Option("", "--complete-step", help="标记步骤完成并推进 pipeline"),
    json_flag: bool = typer.Option(False, "--json", "-j", help="输出结构化 JSON（供 AI Agent 使用）"),
):
    """运行 DoDAF 6步融合流程（支持 Agent 驱动模式）"""

    # Agent mode: status query
    if status_flag:
        from dm2.core.pipeline.orchestrator import PipelineOrchestratorV2
        orch = PipelineOrchestratorV2()
        s = orch.get_status()
        if not s:
            from dm2.cli.json_output import json_error
            json_error("NO_PIPELINE", "无可恢复的 Pipeline，请先运行 dm2 run -d \"...\" --agent 启动")
            raise typer.Exit(1)
        from dm2.cli.json_output import json_success
        json_success(s)
        return

    # Agent mode: get instructions for a step
    if instructions_flag:
        from dm2.core.agent.instructions import InstructionBuilder
        from dm2.core.knowledge.api import KnowledgeAPI
        from dm2.core.pipeline.orchestrator import PipelineOrchestratorV2
        orch = PipelineOrchestratorV2()
        s = orch.get_status()
        knowledge = KnowledgeAPI()
        builder = InstructionBuilder(knowledge)
        instr = builder.build_step_instructions(instructions_flag, s.get("description", "") if s else "")
        from dm2.cli.json_output import json_success
        json_success({
            "context": {"project_description": instr.context.project_description},
            "rules": instr.rules,
            "template": instr.template,
            "output_path": instr.output_path,
        })
        return

    # Agent mode: mark step complete
    if complete_step:
        from dm2.core.pipeline.orchestrator import PipelineOrchestratorV2
        orch = PipelineOrchestratorV2()
        next_step = orch.complete_step(complete_step)
        if next_step is None:
            s = orch.get_status()
            from dm2.cli.json_output import json_success
            json_success({"status": "complete" if s and s["status"] == "complete" else "unknown", "next_step": None})
            return
        from dm2.cli.json_output import json_success
        json_success({"next_step": next_step})
        return

    # Agent mode: initialize pipeline with JSON output throughout
    if agent:
        from dm2.core.pipeline.orchestrator import PipelineOrchestratorV2
        from dm2.core.agent.instructions import InstructionBuilder
        from dm2.core.knowledge.api import KnowledgeAPI
        orch = PipelineOrchestratorV2()
        state = orch.init_pipeline(description)
        knowledge = KnowledgeAPI()
        builder = InstructionBuilder(knowledge)
        first_step = "step1-intent-scope"
        instr = builder.build_step_instructions(first_step, description)
        from dm2.cli.json_output import json_success
        json_success({
            "pipeline": orch.get_status(),
            "first_instructions": {
                "context": {"project_description": description},
                "rules": instr.rules,
                "template": instr.template,
                "output_path": instr.output_path,
            },
        })
        return

    # Legacy mode (backward compatible)
    from dm2.engine.pipeline import PipelineOrchestrator

    orchestrator = PipelineOrchestrator()

    if show_progress:
        if json_flag:
            from dm2.core.pipeline.orchestrator import PipelineOrchestratorV2
            orch = PipelineOrchestratorV2()
            s = orch.get_status()
            from dm2.cli.json_output import json_success
            json_success(s or {"status": "no_pipeline"})
            return
        orchestrator.show_progress()
        return

    if iterate:
        if json_flag:
            from dm2.core.pipeline.orchestrator import PipelineOrchestratorV2
            orch = PipelineOrchestratorV2()
            try:
                state = orch.iterate()
                from dm2.cli.json_output import json_success
                json_success({"status": state.status, "iteration": state.iteration, "current_step": state.current_step})
            except RuntimeError as e:
                from dm2.cli.json_output import json_error
                json_error("ITERATE_FAILED", str(e))
                raise typer.Exit(1)
            return
        if not orchestrator.state_mgr.is_resumable() and not orchestrator.state_mgr.load():
            typer.echo("❌ 无可迭代的 Pipeline（请先运行 dm2 run -d \"...\"）")
            raise typer.Exit(1)
        orchestrator.iterate()
        typer.echo("✅ 已重置，运行 dm2 run --resume 开始新一轮迭代")
        return

    if step:
        valid_steps = [
            "step1-intent-scope",
            "step3-data-requirements",
            "step5-analysis",
            "step6-documentation",
        ]
        if step not in valid_steps:
            if json_flag:
                from dm2.cli.json_output import json_error
                json_error("INVALID_STEP", f"无效步骤: {step}")
                raise typer.Exit(1)
            typer.echo(f"❌ 无效步骤: {step}")
            typer.echo(f"   有效步骤: {', '.join(valid_steps)}")
            raise typer.Exit(1)
        orchestrator.run(description, resume=True, step_only=step)
        return

    if resume:
        if json_flag:
            from dm2.core.pipeline.orchestrator import PipelineOrchestratorV2
            orch = PipelineOrchestratorV2()
            s = orch.get_status()
            if not s:
                from dm2.cli.json_output import json_error
                json_error("NO_PIPELINE", "无可恢复的 Pipeline")
                raise typer.Exit(1)
            from dm2.cli.json_output import json_success
            json_success(s)
            return
        if not orchestrator.state_mgr.is_resumable():
            typer.echo("❌ 无可恢复的 Pipeline（请先运行 dm2 run -d \"...\" 启动）")
            raise typer.Exit(1)
        orchestrator.run(description, resume=True)
        return

    if not description:
        if json_flag:
            from dm2.cli.json_output import json_error
            json_error("MISSING_ARG", "请提供 --desc 参数")
            raise typer.Exit(1)
        typer.echo("请输入架构描述，例如:")
        typer.echo('  dm2 run -d "我们需要建设一个云原生微服务系统的安全架构"')
        typer.echo()
        typer.echo("其他选项:")
        typer.echo("  dm2 run --resume   从上次中断处继续")
        typer.echo("  dm2 run --progress  查看当前进度")
        typer.echo("  dm2 run --iterate   触发迭代循环")
        typer.echo("  dm2 run --step step5-analysis  单独执行某一步骤")
        raise typer.Exit(0)

    if json_flag:
        from dm2.core.pipeline.orchestrator import PipelineOrchestratorV2
        from dm2.core.agent.instructions import InstructionBuilder
        from dm2.core.knowledge.api import KnowledgeAPI
        orch = PipelineOrchestratorV2()
        state = orch.init_pipeline(description)
        knowledge = KnowledgeAPI()
        builder = InstructionBuilder(knowledge)
        instr = builder.build_step_instructions("step1-intent-scope", description)
        from dm2.cli.json_output import json_success
        json_success({
            "pipeline": orch.get_status(),
            "first_instructions": {
                "rules": instr.rules,
                "template": instr.template,
                "output_path": instr.output_path,
            },
        })
        return

    orchestrator.run(description)


@app.command()
def uninstall(
    self_uninstall: bool = typer.Option(False, "--self", help="卸载 dm2-tool 包本身"),
    project_cleanup: bool = typer.Option(False, "--project", help="清理当前目录的 .dm2/ 项目"),
    user_config_cleanup: bool = typer.Option(False, "--user-config", help="删除用户配置文件 ~/.config/dm2/config.yaml"),
):
    """卸载 dm2-tool 或清理项目文件"""
    if not any([self_uninstall, project_cleanup, user_config_cleanup]):
        typer.echo("请指定卸载选项：")
        typer.echo()
        typer.echo("  dm2 uninstall --self          卸载 dm2-tool 程序包")
        typer.echo("  dm2 uninstall --project       删除当前目录的 .dm2/ 项目")
        typer.echo("  dm2 uninstall --user-config   删除用户配置文件")
        typer.echo()
        typer.echo("示例：dm2 uninstall --project")
        return

    if self_uninstall:
        typer.echo("即将执行: pip uninstall dm2-tool -y")
        typer.echo("这将删除 dm2 命令行工具，当前 shell 中 dm2 命令将不可用。")
        confirm = typer.prompt("确认卸载？(y/n)", default="n")
        if confirm.lower() == "y":
            subprocess.run([sys.executable, "-m", "pip", "uninstall", "dm2-tool", "-y"])
            typer.echo("✅ dm2-tool 已卸载")
        else:
            typer.echo("已取消")

    if project_cleanup:
        dm2_dir = Path.cwd() / ".dm2"
        if not dm2_dir.exists():
            typer.echo("未找到 .dm2 项目（当前目录不在 DM2 项目中）")
            return
        typer.echo(f"即将删除: {dm2_dir}")
        typer.echo("包括: config.yaml, state.yaml, steps/ 等所有项目文件")
        confirm = typer.prompt("确认删除？(y/n)", default="n")
        if confirm.lower() == "y":
            shutil.rmtree(dm2_dir)
            typer.echo("✅ .dm2 项目目录已删除")
        else:
            typer.echo("已取消")

    if user_config_cleanup:
        config_path = Path.home() / ".config" / "dm2" / "config.yaml"
        if not config_path.exists():
            typer.echo(f"未找到用户配置文件: {config_path}")
            return
        typer.echo(f"即将删除: {config_path}")
        confirm = typer.prompt("确认删除？(y/n)", default="n")
        if confirm.lower() == "y":
            config_path.unlink()
            typer.echo("✅ 用户配置文件已删除")
        else:
            typer.echo("已取消")


@app.command()
def version(
    json_flag: bool = typer.Option(False, "--json", "-j", help="输出结构化 JSON（供 AI Agent 使用）"),
):
    """显示版本信息"""
    from dm2 import __version__
    if json_flag:
        from dm2.cli.json_output import json_success
        json_success({"version": __version__})
        return
    typer.echo(f"dm2-tool v{__version__}")


def main():
    app()


if __name__ == "__main__":
    app()
