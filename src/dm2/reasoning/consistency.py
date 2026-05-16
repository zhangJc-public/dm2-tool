"""
Consistency Checker - 视图一致性检查器
检查 DoDAF 视图间的逻辑一致性
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


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

        # 从内容中提取活动列表
        activities = self._extract_activities(ov5a or ov5b)

        # 检查悬空活动（没有执行者的活动）
        bound_activities = self._extract_bound_activities(ov5b)
        unbound = [a for a in activities if a not in bound_activities]

        if unbound:
            self._issues.append(ConsistencyIssue(
                issue_type="unbound_activity",
                severity=IssueSeverity.ERROR,
                message=f"发现 {len(unbound)} 个未分配执行者的活动",
                related_views=["OV-5b", "OV-4"],
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
        import re

        temporal_relations = {}
        for view_id, content in views_data.items():
            # 匹配前置和后继关系
            prereq_pattern = r'(?:prerequisite|pre|前置)[:\s]+([^\n,]+)'
            succ_pattern = r'(?:successor|post|后继)[:\s]+([^\n,]+)'

            for match in re.finditer(prereq_pattern, content, re.IGNORECASE):
                node = match.group(1).strip()
                temporal_relations.setdefault(node, {})['prerequisite'] = []

            for match in re.finditer(succ_pattern, content, re.IGNORECASE):
                node = match.group(1).strip()
                temporal_relations.setdefault(node, {})['successor'] = []

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
        """提取活动列表"""
        import re
        patterns = [
            r'A\d+[:\s]+([^\n]+)',
            r'###?\s+(\w+活动[^\n]*)',
            r'-\s*([^\n]*活动[^\n]*)',
        ]

        activities = []
        for p in patterns:
            matches = re.findall(p, content)
            activities.extend([m.strip() for m in matches if m.strip()])

        return list(set(activities))

    def _extract_performers(self, content: str) -> List[str]:
        """提取执行者列表"""
        import re
        patterns = [
            r'(?:Performer|执行者|系统|组织)[:\s]+([^\n]+)',
            r'\|\s*([^\|]+)\s*\|.*(?:Performer|执行者)',
        ]

        performers = []
        for p in patterns:
            matches = re.findall(p, content)
            performers.extend([m.strip() for m in matches if m.strip()])

        return list(set(performers))

    def _extract_bound_activities(self, content: str) -> set:
        """从 OV-5b 提取已绑定执行者的活动"""
        bound = set()
        for line in content.split('\n'):
            if '|' in line and '执行者' not in line[:10]:
                parts = [p.strip() for p in line.split('|')]
                if parts:
                    bound.add(parts[0])
        return bound

    def _extract_resources(self, content: str) -> List[str]:
        """提取资源列表"""
        import re
        patterns = [
            r'(?:Resource|资源)[:\s]+([^\n]+)',
            r'\[([^\]]+资源)\]',
        ]

        resources = []
        for p in patterns:
            matches = re.findall(p, content)
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
