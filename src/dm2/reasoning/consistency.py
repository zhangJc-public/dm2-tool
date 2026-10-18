"""
Consistency Checker - 视图一致性检查器
检查 DoDAF 视图间的逻辑一致性
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List

#: A declared prerequisite / successor edge. The text before the marker is the
#: subject, the text after it is the target. An edge needs both ends, so a line
#: whose marker has nothing before it contributes nothing rather than inventing
#: a node.
_TEMPORAL_EDGE = re.compile(
    r"(?P<subject>[^\n:：]+?)"
    r"\s*(?P<kind>prerequisite|pre|前置|successor|post|后继)"
    r"\s*[:：]\s*(?P<target>[^\n,，]+)",
    re.IGNORECASE,
)

_SUCCESSOR_KINDS = {"successor", "post", "后继"}

#: An activity ID as authored in OV-5a/OV-5b (``A1``, ``A5.3``). The trailing
#: lookahead is what separates a real ID from a Mermaid node identifier
#: (``A53["A5.3 ..."]``) or edge syntax (``A1 --> A2``).
_ACTIVITY_ID = re.compile(r"(A\d+(?:\.\d+)?)\s+(?=[\w\u4e00-\u9fff])")
_PERFORMER_MARKER = re.compile(r"执行者|performer", re.IGNORECASE)
_TABLE_SEPARATOR = re.compile(r"^\s*\|[\s:|-]+\|\s*$")
#: Values that mean "no performer stated" rather than naming one.
_NO_PERFORMER = {"", "-", "—", "/", "n/a"}


def _performer_value(line: str) -> str:
    """Text actually stated after a performer marker on ``line``.

    Only the value counts: ``执行者：<br/>输入：...`` states no performer, and
    neither does a table header like ``执行者（activityPerformedByPerformer）``.
    """
    match = _PERFORMER_MARKER.search(line)
    if not match:
        return ""
    tail = re.split(r"<br\s*/?>|\||<", line[match.end():])[0]
    return tail.strip(" ：:·,，、（）()")


class IssueSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ConsistencyIssue:
    """一致性问题"""
    issue_type: str
    severity: IssueSeverity
    message: str
    view_id: str = ""
    related_views: List[str] = field(default_factory=list)
    suggestion: str = ""


class ConsistencyChecker:
    """
    DoDAF 视图一致性检查器

    检查规则：
    1. Activity-Performer 绑定：每个 Activity 必须有对应的 Performer
    2. Resource Flow 完整性：每个 Resource 必须有生产者和消费者
    3. Capability-Activity 映射：能力必须映射到具体活动
    4. 时序一致性：prerequisite/successor 不能形成环
    """

    def __init__(self):
        self._issues: List[ConsistencyIssue] = []

    def check_views(self, views_data: Dict[str, str]) -> List[ConsistencyIssue]:
        """
        检查多个视图的一致性

        Args:
            views_data: {view_id: view_content}

        Returns:
            发现的问题列表
        """
        self._issues = []

        # 1. 检查 Activity-Performer 绑定
        self._check_activity_performer_binding(views_data)

        # 2. 检查 Resource Flow 完整性
        self._check_resource_flow_integrity(views_data)

        # 3. 检查能力映射
        self._check_capability_mapping(views_data)

        # 4. 检查时序关系
        self._check_temporal_consistency(views_data)

        return self._issues

    def _check_activity_performer_binding(self, views_data: Dict[str, str]):
        """检查 Activity-Performer 绑定"""

        ov5b = views_data.get("OV-5b", "")
        ov5a = views_data.get("OV-5a", "")

        # 简单检查：如果有 OV-5a 但没有 OV-5b，报警告
        if ov5a and not ov5b:
            self._issues.append(ConsistencyIssue(
                issue_type="missing_mapping",
                severity=IssueSeverity.WARNING,
                message="存在 OV-5a（活动分解）但缺少 OV-5b（活动追踪）",
                view_id="OV-5b",
                suggestion="建议生成 OV-5b 将活动追踪到执行者",
            ))

        if not ov5b:
            return

        # Every activity OV-5b declares must name a performer. The check is
        # scoped to OV-5b on purpose: OV-5a is a decomposition tree whose leaves
        # are not necessarily tracked one by one, so comparing the two views
        # reports gaps that are not gaps. An activity the model claims to cover
        # without saying who performs it is the defect worth reporting.
        activities = self._extract_activities(ov5b)
        bound_activities = self._extract_bound_activities(ov5b)
        unbound = [a for a in activities if a not in bound_activities]

        if unbound:
            self._issues.append(ConsistencyIssue(
                issue_type="unbound_activity",
                severity=IssueSeverity.ERROR,
                view_id="OV-5b",
                message=f"发现 {len(unbound)} 个未分配执行者的活动",
                related_views=["OV-4"],
                suggestion=f"请为以下活动分配执行者: {', '.join(unbound[:5])}",
            ))

    def _check_resource_flow_integrity(self, views_data: Dict[str, str]):
        """检查 Resource Flow 完整性"""
        ov2 = views_data.get("OV-2", "")

        if not ov2:
            return

        # 提取资源
        resources = self._extract_resources(ov2)
        if not resources:
            return

        # 提取 produced 和 consumed
        produced = self._extract_by_pattern(ov2, [r'(?:产出|produces|输出)[:\s]*([^\n]+)'])
        consumed = self._extract_by_pattern(ov2, [r'(?:消耗|consumes|输入)[:\s]*([^\n]+)'])

        # 外部资源可能是正常的
        orphan = [r for r in resources if r not in produced and r not in consumed]

        if orphan:
            self._issues.append(ConsistencyIssue(
                issue_type="orphan_resource",
                severity=IssueSeverity.INFO,
                message=f"发现 {len(orphan)} 个可能孤立的资源",
                view_id="OV-2",
                suggestion=f"请确认以下资源的来源和去向: {', '.join(orphan[:5])}",
            ))

    def _check_capability_mapping(self, views_data: Dict[str, str]):
        """检查 Capability-Activity 映射"""
        cv2 = views_data.get("CV-2", "")
        ov5a = views_data.get("OV-5a", "")

        if not cv2:
            return

        capabilities = self._extract_capabilities(cv2)

        # 如果有多个能力但没有活动映射
        if len(capabilities) > 3 and not ov5a:
            self._issues.append(ConsistencyIssue(
                issue_type="capability_without_activity",
                severity=IssueSeverity.WARNING,
                message="定义了多个能力但缺少 OV-5a 活动分解",
                view_id="CV-2",
                related_views=["OV-5a"],
                suggestion="建议生成 OV-5a 建立能力到活动的映射",
            ))

    def _check_temporal_consistency(self, views_data: Dict[str, str]):
        """检查时序一致性（检查循环依赖）"""
        temporal_relations: Dict[str, Dict[str, List[str]]] = {}

        for content in views_data.values():
            for match in _TEMPORAL_EDGE.finditer(content):
                subject = match.group("subject").strip()
                target = match.group("target").strip()
                if not subject or not target:
                    continue
                kind = (
                    "successor"
                    if match.group("kind").lower() in _SUCCESSOR_KINDS
                    else "prerequisite"
                )
                temporal_relations.setdefault(subject, {}).setdefault(kind, []).append(target)

        # 检测循环
        cycles = self._find_cycles(temporal_relations)
        if cycles:
            self._issues.append(ConsistencyIssue(
                issue_type="circular_dependency",
                severity=IssueSeverity.ERROR,
                message="发现活动间存在循环依赖",
                view_id="OV-6c",
                suggestion=f"循环: {' -> '.join(cycles[0][:5])}",
            ))

    def _extract_activities(self, content: str) -> List[str]:
        """Activity IDs declared in OV-5b, from node labels and the activity table."""
        declared: List[str] = []
        for line in content.splitlines():
            for activity_id in _ACTIVITY_ID.findall(line):
                if activity_id not in declared:
                    declared.append(activity_id)
        return declared

    def _extract_bound_activities(self, content: str) -> set:
        """Activity IDs in OV-5b that carry a performer, in either authoring form."""
        bound: set = set()

        # Form 1 — Mermaid node label:
        #   A1["A1 侦测探测<br/>执行者：阵地 · C2<br/>输入：..."]
        for line in content.splitlines():
            if not _performer_value(line):
                continue
            bound.update(_ACTIVITY_ID.findall(line))

        # Form 2 — the activity table:
        #   | 活动 | 输入 | 输出 | 执行者 | 前置条件 |
        bound |= self._bound_activities_from_table(content)
        return bound

    def _bound_activities_from_table(self, content: str) -> set:
        """Activities whose row in the OV-5b activity table names a performer."""
        bound: set = set()
        block: List[str] = []

        def flush(rows: List[str]) -> None:
            if len(rows) < 2:
                return
            header = [cell.strip() for cell in rows[0].strip().strip("|").split("|")]
            activity_col = next((i for i, c in enumerate(header) if "活动" in c), None)
            performer_col = next(
                (i for i, c in enumerate(header) if _PERFORMER_MARKER.search(c)), None
            )
            if activity_col is None or performer_col is None:
                return
            for row in rows[1:]:
                if _TABLE_SEPARATOR.match(row):
                    continue
                cells = [c.strip() for c in row.strip().strip("|").split("|")]
                if max(activity_col, performer_col) >= len(cells):
                    continue
                performer = cells[performer_col].strip().lower()
                if performer in _NO_PERFORMER:
                    continue
                bound.update(_ACTIVITY_ID.findall(cells[activity_col]))

        for line in content.splitlines():
            if line.strip().startswith("|"):
                block.append(line)
            elif block:
                flush(block)
                block = []
        if block:
            flush(block)
        return bound

    def _extract_resources(self, content: str) -> List[str]:
        """提取资源列表

        Level-1 headings are the (bilingual) view title, not a resource list: the
        English word "Resource" inside a title such as
        "OV-2 作战资源流描述（Operational Resource Flow Description）" used to be
        extracted as a resource literally named ``Flow Description）``.
        """
        body = "\n".join(
            line for line in content.splitlines() if not re.match(r"^#\s", line)
        )
        patterns = [
            r'(?:Resource|资源)[:\s]+([^\n]+)',
            r'\[([^\]]+资源)\]',
        ]

        resources = []
        for p in patterns:
            matches = re.findall(p, body)
            resources.extend([m.strip() for m in matches if m.strip()])

        return list(set(resources))

    def _extract_capabilities(self, content: str) -> List[str]:
        """提取能力列表"""
        import re
        patterns = [
            r'(?:Capability|能力)[:\s]+([^\n]+)',
            r'CV-\d+[:\s]+([^\n]+)',
        ]

        capabilities = []
        for p in patterns:
            matches = re.findall(p, content)
            capabilities.extend([m.strip() for m in matches if m.strip()])

        return list(set(capabilities))

    def _extract_by_pattern(self, content: str, patterns: List[str]) -> List[str]:
        """通用模式提取"""
        import re
        results = []
        for p in patterns:
            matches = re.findall(p, content, re.IGNORECASE)
            results.extend([m.strip() for m in matches if m.strip()])
        return results

    def _find_cycles(self, relations: Dict) -> List[List[str]]:
        """检测循环依赖"""
        cycles = []

        def dfs(node, path, visited):
            if node in path:
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return

            if node in visited:
                return

            visited.add(node)
            path.append(node)

            if node in relations:
                for rel_type in ['prerequisite', 'successor']:
                    targets = relations[node].get(rel_type, [])
                    for target in targets:
                        dfs(target, path.copy(), visited)

        for node in relations:
            dfs(node, [], set())

        return cycles
