"""
View Recommender - DoDAF 视图推荐引擎
基于 DM2 17 数据组激活检测驱动的视图推荐
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

from dm2.kernel.indexer import DM2KnowledgeIndexer, ViewTemplate
from dm2.utils.frontmatter import FrontmatterParser
from dm2.utils.paths import get_reference_path

from .six_w_analyzer import SixW, SixWAnalysis


@dataclass
class ViewRecommendation:
    """视图推荐结果"""
    view_id: str
    view_name: str
    viewpoint: str
    relevance_score: float  # 0.0 - 1.0
    reason: str
    priority: int  # 1 = 必须, 2 = 推荐, 3 = 可选
    dm2_groups: list[str]
    missing_data: list[str] = field(default_factory=list)  # 生成此视图可能缺失的数据


@dataclass
class DataGroupActivation:
    """数据组激活记录"""
    group_id: str
    group_name: str
    score: float  # 0.0 - 1.0
    keywords_matched: list[str] = field(default_factory=list)
    keyword_count: int = 0
    total_keywords: int = 0


@dataclass
class GroupViewMapping:
    """数据组到视图的映射条目"""
    group_id: str
    group_name: str
    group_label: str
    views: list[dict]


class DataGroupActivator:
    """
    数据组激活检测器
    从模板 frontmatter 加载 keywords, 匹配用户描述文本, 计算激活度
    """

    def __init__(self, reference_root: Optional[Path] = None):
        self.reference_root = reference_root or get_reference_path()
        self._group_templates: dict[str, Path] = {}  # group_id -> template_path
        self._group_keywords: dict[str, list[str]] = {}  # group_id -> [keywords]
        self._group_meta: dict[str, dict] = {}  # group_id -> {name, label, description}
        self._scan_templates()
        self._load_all_groups_from_yaml()

    def _scan_templates(self):
        """扫描 groups/ 下所有 *Template.md, 提取 group_id 和 keywords"""
        groups_dir = self.reference_root / "groups"
        if not groups_dir.exists():
            return

        for tmpl_path in sorted(groups_dir.glob("*/*Template.md")):
            group_id = tmpl_path.parent.name
            self._group_templates[group_id] = tmpl_path

            # 读取 keywords
            try:
                content = tmpl_path.read_text(encoding='utf-8')
                fm = FrontmatterParser.parse(content)
                if fm and "keywords" in fm:
                    kw = fm["keywords"]
                    if isinstance(kw, list):
                        self._group_keywords[group_id] = [str(k).lower() for k in kw if k]
                    else:
                        self._group_keywords[group_id] = [str(kw).lower()]
                else:
                    self._group_keywords[group_id] = []
            except Exception:
                self._group_keywords[group_id] = []

    def _load_all_groups_from_yaml(self):
        """从 group-to-views.yaml 加载全部 17 组的元数据，确保无模板的组也出现"""
        gtv = _load_group_to_views()
        if not gtv or "groups" not in gtv:
            return
        for g_entry in gtv["groups"]:
            gid = g_entry["id"]
            # 存储元数据（无论有无模板）
            self._group_meta[gid] = {
                "name": g_entry.get("name", ""),
                "label": g_entry.get("label", ""),
                "description": g_entry.get("description", ""),
            }
            # 确保无模板的组在 _group_keywords 中有条目
            if gid not in self._group_keywords:
                self._group_keywords[gid] = []

    def activate(self, description: str) -> list[DataGroupActivation]:
        """
        对描述文本做数据组激活检测，返回全部 17 组

        Args:
            description: 用户输入的描述文本

        Returns:
            所有数据组的激活记录列表 (按 score 降序)
        """
        text_lower = description.lower()
        results = []

        for group_id, keywords in self._group_keywords.items():
            meta = self._group_meta.get(group_id, {})
            group_name = meta.get("name") or (group_id.split("-", 1)[-1] if "-" in group_id else group_id)

            if not keywords:
                results.append(DataGroupActivation(
                    group_id=group_id,
                    group_name=group_name,
                    score=0.0,
                    keywords_matched=[],
                    keyword_count=0,
                    total_keywords=0,
                ))
                continue

            matched = [kw for kw in keywords if kw in text_lower]

            results.append(DataGroupActivation(
                group_id=group_id,
                group_name=group_name,
                score=round(len(matched) / len(keywords), 4) if keywords else 0.0,
                keywords_matched=matched,
                keyword_count=len(matched),
                total_keywords=len(keywords),
            ))

        results.sort(key=lambda x: -x.score)
        return results

    def get_group_keywords(self, group_id: str) -> list[str]:
        """获取指定数据组的关键词"""
        return self._group_keywords.get(group_id, [])

    def get_group_meta(self, group_id: str) -> dict:
        """获取指定数据组的元数据 (name, label, description)"""
        return self._group_meta.get(group_id, {})

    def get_all_group_meta(self) -> dict[str, dict]:
        """获取所有数据组的元数据"""
        return dict(self._group_meta)

    def get_loaded_groups(self) -> list[str]:
        """获取已加载的数据组 ID 列表（全部 17 组）"""
        return sorted(self._group_keywords.keys())


def _load_group_to_views() -> Optional[dict]:
    """加载外部 group-to-views.yaml 映射文件"""
    ref = get_reference_path()
    candidates = [
        ref / "group-to-views.yaml",
        ref.parent / "group-to-views.yaml",
    ]
    for path in candidates:
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
    return None


class ViewRecommender:
    """视图推荐引擎 — 数据组激活驱动"""

    def __init__(self, indexer: DM2KnowledgeIndexer):
        self.indexer = indexer
        self._activator: Optional[DataGroupActivator] = None
        self._group_to_views = _load_group_to_views()

    @property
    def activator(self) -> DataGroupActivator:
        if self._activator is None:
            self._activator = DataGroupActivator()
        return self._activator

    def _get_dependencies(self) -> dict[str, list[str]]:
        """从 indexer 的 ViewTemplate 中提取依赖关系"""
        deps = {}
        for vid, tmpl in self.indexer._view_templates.items():
            deps[vid] = tmpl.dependencies
        return deps

    def _get_priority(self) -> dict[str, int]:
        """从 indexer 的 ViewTemplate 中提取优先级"""
        return {vid: tmpl.priority for vid, tmpl in self.indexer._view_templates.items()}

    def recommend(self, six_w_analysis: SixWAnalysis,
                  extracted_concepts: dict = None,
                  target_viewpoints: list[str] = None,
                  raw_description: str = "") -> list[ViewRecommendation]:
        """
        推荐适合的 DoDAF 视图（数据组激活驱动，兼容 6W 输入）

        流程:
        1. 从 6W 提取实体关键词 + 原始描述, 做数据组激活检测
        2. 活跃数据组 → 候选视图
        3. 修正因子: 依赖就绪度 + 已生成视图过滤
        4. 输出 (不做优先级排序 — 交给 AI Agent)

        Args:
            six_w_analysis: 6W 分析结果
            extracted_concepts: 提取的 DM2 概念（如 {"performer": [...], "activity": [...]}）
            target_viewpoints: 目标视点过滤（如 ["OV", "SV"]）
            raw_description: 原始用户描述文本（优先用于数据组激活检测）

        Returns:
            未排序的视图推荐列表（CLI 不排序, AI Agent 做最终优先级排序）
        """
        # ---- 1. 构建描述文本用于激活检测 ----
        if raw_description.strip():
            description_text = raw_description
        else:
            description_parts = []
            description_parts.append(six_w_analysis.primary_w.value)
            for ent_type, entities in six_w_analysis.extracted_entities.items():
                description_parts.extend(entities)
            if extracted_concepts:
                for concepts in extracted_concepts.values():
                    if isinstance(concepts, list):
                        description_parts.extend(str(c) for c in concepts)
            description_text = " ".join(description_parts)

            if not description_text.strip():
                description_text = six_w_analysis.reasoning or ""

        # ---- 2. 数据组激活检测 ----
        activations = self.activator.activate(description_text)

        # ---- 3. 活跃数据组 → 候选视图 ----
        active_groups = [a for a in activations if a.score > 0.0]
        candidate_view_ids = set()
        view_group_score: dict[str, float] = {}  # view_id -> max group score
        view_source_groups: dict[str, list[str]] = {}  # view_id -> contributing group ids

        if self._group_to_views and "groups" in self._group_to_views:
            for ag in active_groups:
                for g_entry in self._group_to_views["groups"]:
                    if g_entry["id"] == ag.group_id:
                        for v in g_entry.get("group_views", []):
                            vid = v["id"]
                            candidate_view_ids.add(vid)
                            current = view_group_score.get(vid, 0.0)
                            if ag.score > current:
                                view_group_score[vid] = ag.score
                                view_source_groups[vid] = [ag.group_id]
                            elif ag.score == current:
                                view_source_groups.setdefault(vid, []).append(ag.group_id)
                        break

        # 回退: 对未在 group-to-views.yaml 中的活跃组, 用 indexer 的 dm2_groups 匹配
        for ag in active_groups:
            for vid, tmpl in self.indexer._view_templates.items():
                if any(ag.group_name.lower() in g.lower() for g in tmpl.dm2_groups):
                    candidate_view_ids.add(vid)
                    current = view_group_score.get(vid, 0.0)
                    if ag.score > current:
                        view_group_score[vid] = ag.score
                        view_source_groups[vid] = [ag.group_id]

        # 6W 补充: 数据组未覆盖的 6W 建议视图赋默认低分
        for vid in six_w_analysis.suggested_views:
            if vid not in candidate_view_ids:
                candidate_view_ids.add(vid)
                view_group_score[vid] = 0.1  # 低默认值, 不稀释数据组信号

        # ---- 4. 过滤视点 ----
        if target_viewpoints:
            filtered = set()
            for vid in candidate_view_ids:
                tmpl = self.indexer.get_view_template(vid)
                if tmpl and tmpl.viewpoint in target_viewpoints:
                    filtered.add(vid)
            candidate_view_ids = filtered

        # ---- 5. 生成推荐 ----
        recommendations = []
        for view_id in candidate_view_ids:
            template = self.indexer.get_view_template(view_id)
            if not template:
                continue

            score = view_group_score.get(view_id, 0.1)

            # 关联的源数据组 (仅记录贡献分数的)
            source_groups = view_source_groups.get(view_id, [])

            # 缺失数据检查
            missing = self._check_missing_data(template, extracted_concepts)
            reason = self._generate_reason(template, score, source_groups)

            recommendations.append(ViewRecommendation(
                view_id=view_id,
                view_name=template.view_name,
                viewpoint=template.viewpoint,
                relevance_score=round(score, 4),
                reason=reason,
                priority=template.priority,
                dm2_groups=template.dm2_groups,
                missing_data=missing,
            ))

        # ---- 6. CLI 不做排序, 输出原始列表供 AI Agent 决策 ----
        return recommendations

    def recommend_from_description(self, description: str,
                                    target_viewpoints: list[str] = None) -> list[ViewRecommendation]:
        """
        直接用描述文本做视图推荐 (不经过 6W)

        Args:
            description: 用户描述文本
            target_viewpoints: 目标视点过滤

        Returns:
            未排序的视图推荐列表
        """
        # 数据组激活
        activations = self.activator.activate(description)
        active_groups = [a for a in activations if a.score > 0.0]

        candidate_view_ids = set()
        view_group_score: dict[str, float] = {}
        view_source_groups: dict[str, list[str]] = {}

        if self._group_to_views and "groups" in self._group_to_views:
            for ag in active_groups:
                for g_entry in self._group_to_views["groups"]:
                    if g_entry["id"] == ag.group_id:
                        for v in g_entry.get("group_views", []):
                            vid = v["id"]
                            candidate_view_ids.add(vid)
                            current = view_group_score.get(vid, 0.0)
                            if ag.score > current:
                                view_group_score[vid] = ag.score
                                view_source_groups[vid] = [ag.group_id]
                        break

        # 回退: 对未在 group-to-views.yaml 中的活跃组, 用 indexer 的 dm2_groups 匹配
        for ag in active_groups:
            for vid, tmpl in self.indexer._view_templates.items():
                if any(ag.group_name.lower() in g.lower() for g in tmpl.dm2_groups):
                    candidate_view_ids.add(vid)
                    current = view_group_score.get(vid, 0.0)
                    if ag.score > current:
                        view_group_score[vid] = ag.score
                        view_source_groups[vid] = [ag.group_id]

        if target_viewpoints:
            filtered = set()
            for vid in candidate_view_ids:
                tmpl = self.indexer.get_view_template(vid)
                if tmpl and tmpl.viewpoint in target_viewpoints:
                    filtered.add(vid)
            candidate_view_ids = filtered

        recommendations = []
        for view_id in candidate_view_ids:
            template = self.indexer.get_view_template(view_id)
            if not template:
                continue

            score = view_group_score.get(view_id, 0.1)
            source_groups = view_source_groups.get(view_id, [])

            recommendations.append(ViewRecommendation(
                view_id=view_id,
                view_name=template.view_name,
                viewpoint=template.viewpoint,
                relevance_score=round(score, 4),
                reason=self._generate_reason(template, score, source_groups),
                priority=template.priority,
                dm2_groups=template.dm2_groups,
                missing_data=self._check_missing_data(template, None),
            ))

        return recommendations

    def get_data_group_activation(self, description: str) -> list[DataGroupActivation]:
        """
        对外接口: 获取数据组激活向量（供 CLI --json 使用）

        Args:
            description: 用户描述文本

        Returns:
            按 score 降序的数据组激活列表
        """
        return self.activator.activate(description)

    def filter_completed_views(self, recommendations: list[ViewRecommendation],
                                completed_view_ids: set[str]) -> list[ViewRecommendation]:
        """
        过滤已生成的视图 (修正因子)
        不再推荐已 generated/verified 的视图
        """
        return [r for r in recommendations if r.view_id not in completed_view_ids]

    def get_dependency_readiness(self, recommendations: list[ViewRecommendation],
                                  completed_view_ids: set[str]) -> dict[str, bool]:
        """
        检查推荐视图的依赖就绪度 (修正因子)
        返回 {view_id: ready_or_not}
        """
        deps = self._get_dependencies()
        readiness = {}
        for r in recommendations:
            view_deps = deps.get(r.view_id, [])
            ready = all(d in completed_view_ids for d in view_deps)
            readiness[r.view_id] = ready
        return readiness

    # ─── 以下为保留的兼容方法 ─────────────────────────────────

    CONCEPT_TO_VIEWS = {
        "performer": ["OV-4", "OV-2", "SV-1", "SvcV-1"],
        "activity": ["OV-5a", "OV-5b", "SV-4", "SvcV-4", "OV-6a", "OV-6b", "OV-6c"],
        "capability": ["CV-1", "CV-2", "CV-3", "CV-4", "CV-5", "CV-6", "CV-7"],
        "resource": ["OV-2", "OV-3", "DIV-1", "DIV-2", "DIV-3"],
        "information": ["DIV-1", "DIV-2", "DIV-3", "OV-2"],
        "location": ["OV-1", "OV-2", "OV-4"],
        "measure": ["SV-7", "SvcV-7", "OV-6b", "PV-2"],
        "service": ["SvcV-1", "SvcV-2", "SvcV-3a", "SvcV-3b", "SvcV-4", "SvcV-5"],
        "project": ["PV-1", "PV-2", "PV-3", "SV-8", "SvcV-8"],
        "rules": ["OV-6a", "StdV-1", "SV-10a", "SvcV-10a"],
        "standards": ["StdV-1", "StdV-2", "SV-9", "SvcV-9"],
        "guidance": ["StdV-1", "StdV-2", "AV-2"],
        "organization": ["OV-4", "PV-1", "CV-5"],
        "technology": ["SV-9", "SvcV-9", "StdV-2"],
        "system": ["SV-1", "SV-2", "SV-3", "SV-4", "SV-5a", "SV-5b"],
        "data": ["DIV-1", "DIV-2", "DIV-3", "OV-2", "OV-3"],
    }

    def _get_views_for_concepts(self, concepts: dict) -> set[str]:
        """根据概念类型获取相关视图 (保留兼容)"""
        views = set()
        for concept_type, v_list in self.CONCEPT_TO_VIEWS.items():
            if concept_type in concepts and concepts[concept_type]:
                views.update(v_list)
        return views

    def _check_missing_data(self, template: ViewTemplate,
                           concepts: dict = None) -> list[str]:
        """检查生成视图可能缺失的数据（从 ViewTemplate 读取）"""
        missing = []
        required = template.required_data
        if concepts:
            for req in required:
                found = False
                for concept_type, entities in concepts.items():
                    if req in concept_type or entities:
                        found = True
                        break
                if not found:
                    missing.append(req)
        else:
            missing = required
        return missing

    def _generate_reason(self, template: ViewTemplate,
                        score: float,
                        matched_groups: list[str] = None) -> str:
        """生成推荐理由 (数据组激活驱动)"""
        if score > 0.7:
            quality = "高度相关"
        elif score > 0.3:
            quality = "相关"
        elif score > 0.0:
            quality = "可能相关"
        else:
            quality = "基础推荐"

        groups_str = ", ".join(matched_groups[:3]) if matched_groups else ""
        if groups_str:
            return f"{quality} - 来自数据组 {groups_str} 激活"
        return f"{quality} - {template.view_id}（{template.view_name}）"

    def get_view_sequence(self, view_ids: list[str]) -> list[str]:
        """
        确定视图生成顺序（考虑依赖关系）

        Returns:
            拓扑排序后的视图列表
        """
        deps = self._get_dependencies()
        visited = set()
        result = []

        def visit(vid: str):
            if vid in visited:
                return
            visited.add(vid)
            for dep in deps.get(vid, []):
                if dep in deps:
                    visit(dep)
            result.append(vid)

        for vid in view_ids:
            if vid in deps:
                visit(vid)

        return result

    def get_minimal_view_set(self, six_w_analysis: SixWAnalysis,
                             complexity: str = "CLEAR") -> list[str]:
        """
        获取最小完整视图集（满足基本建模需求的最少视图）

        Args:
            six_w_analysis: 6W 分析结果
            complexity: 复杂度等级 (CLEAR/COMPLICATED/COMPLEX/CHAOTIC)

        Returns:
            推荐的最小视图集
        """
        # 根据复杂度确定视图集规模
        if complexity == "CLEAR":
            core_views = ["AV-2", "OV-1", "OV-4", "OV-5a"]
        elif complexity == "COMPLICATED":
            core_views = ["AV-2", "AV-1", "OV-1", "OV-4", "OV-5a", "OV-5b",
                         "CV-1", "CV-2", "DIV-1"]
        elif complexity == "COMPLEX":
            core_views = ["AV-2", "AV-1", "OV-1", "OV-2", "OV-4", "OV-5a", "OV-5b",
                         "CV-1", "CV-2", "CV-3", "DIV-1", "DIV-2",
                         "SV-1", "SV-4", "SvcV-1", "StdV-1"]
        else:  # CHAOTIC
            priorities = self._get_priority()
            core_views = [vid for vid, pri in priorities.items() if pri <= 2]

        # 根据 6W 添加特定视图
        six_w = six_w_analysis.primary_w
        if six_w == SixW.WHO:
            core_views.extend(["OV-2", "OV-4", "SV-1", "SvcV-1"])
        elif six_w == SixW.HOW:
            core_views.extend(["OV-5b", "SV-4", "SvcV-4"])
        elif six_w == SixW.WHAT:
            core_views.extend(["DIV-1", "DIV-2", "DIV-3", "AV-2"])
        elif six_w == SixW.WHERE:
            core_views.extend(["OV-2", "SV-2", "SvcV-2"])
        elif six_w == SixW.WHEN:
            core_views.extend(["PV-2", "OV-6b", "OV-6c"])
        elif six_w == SixW.WHY:
            core_views.extend(["CV-1", "CV-2", "StdV-1"])

        return list(set(core_views))

    def verify_and_supplement_views(
        self,
        recommended_views: list[ViewRecommendation],
        six_w_analysis: SixWAnalysis,
    ) -> list[ViewRecommendation]:
        """
        使用 VIEW-RELATIONS-FULL-MAP.md 校验路径完整性并补充缺失视图
        """
        view_ids = {r.view_id for r in recommended_views}
        missing = self._check_path_completeness(view_ids)

        for vid in missing:
            template = self.indexer.get_view_template(vid)
            if template:
                recommended_views.append(ViewRecommendation(
                    view_id=vid,
                    view_name=template.view_name,
                    viewpoint=template.viewpoint,
                    relevance_score=0.6,
                    reason=f"路径完整性补充 - {vid}（被 {template.dm2_groups} 数据组需要）",
                    priority=template.priority,
                    dm2_groups=template.dm2_groups,
                    missing_data=[],
                ))

        seen = set()
        unique = []
        for r in recommended_views:
            if r.view_id not in seen:
                seen.add(r.view_id)
                unique.append(r)
        unique.sort(key=lambda r: (r.priority, -r.relevance_score))

        return unique

    def _check_path_completeness(self, view_ids: set[str]) -> set[str]:
        """基于 views.yaml 依赖的传递闭包检查路径完整性"""
        deps = self._get_dependencies()

        def transitive_deps(vid: str, visited: set = None) -> set[str]:
            if visited is None:
                visited = set()
            if vid in visited:
                return set()
            visited.add(vid)
            result = set()
            for dep in deps.get(vid, []):
                result.add(dep)
                result.update(transitive_deps(dep, visited))
            return result

        all_needed = set()
        for vid in view_ids:
            all_needed.update(transitive_deps(vid))

        return all_needed - view_ids



if __name__ == "__main__":
    from .six_w_analyzer import SixWAnalyzer

    indexer = DM2KnowledgeIndexer()
    indexer.load_all()

    recommender = ViewRecommender(indexer)
    analyzer = SixWAnalyzer()

    test_queries = [
        "有哪些系统参与数据交换？",
        "防火墙如何检测威胁？",
    ]

    for q in test_queries:
        analysis = analyzer.analyze(q)
        recs = recommender.recommend(analysis)

        # 展示数据组激活
        activations = recommender.get_data_group_activation(q)
        print(f"\n查询: {q}")
        print(f"6W: {analysis.primary_w.value}")
        print("数据组激活 (top 5):")
        for a in activations[:5]:
            print(f"  {a.group_id}: score={a.score:.3f} ({a.keyword_count}/{a.total_keywords} kw)")
        print("推荐视图:")
        for r in recs[:5]:
            print(f"  {r.view_id} - {r.view_name} (相关度: {r.relevance_score:.3f})")
            print(f"       理由: {r.reason}")
