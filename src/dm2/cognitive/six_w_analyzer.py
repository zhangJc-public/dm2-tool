"""
6W Question Analyzer - DoDAF 标准问答分析器
基于 DoDAF Standard Interrogatives Matrix 实现
"""

import re
from dataclasses import dataclass, field
from enum import Enum


class SixW(str, Enum):
    WHAT = "What"      # 什么（资源、数据、活动）
    HOW = "How"       # 如何（方式、方法、过程）
    WHERE = "Where"   # 哪里（位置、部署）
    WHO = "Who"       # 谁（执行者、角色）
    WHEN = "When"     # 何时（时间、顺序）
    WHY = "Why"       # 为何（目的、原因、规则）


@dataclass
class SixWAnalysis:
    """6W 分析结果"""
    primary_w: SixW
    secondary_ws: list[SixW] = field(default_factory=list)
    confidence: float = 0.0
    reasoning: str = ""
    extracted_entities: dict[str, list[str]] = field(default_factory=dict)  # entity_type -> [entities]
    suggested_views: list[str] = field(default_factory=list)


# 6W 关键词模式
SIX_W_PATTERNS = {
    SixW.WHAT: [
        r"什么|what|哪个|哪些|哪个系统|哪些数据|什么资源|什么活动|什么能力|什么规则",
        r"是什么|is a|are|includes|consists of|contains",
        r"类型|type|分类|category|实例|instance",
        r"数据|information|resource|资源|信息",
    ],
    SixW.HOW: [
        r"如何|how|怎么|怎样|怎么样",
        r"方式|method|approach|means|手段",
        r"过程|process|procedure|步骤|流程|工作流",
        r"功能|function|capability|能力|功能",
        r"执行|perform|execute|conduct|实施",
    ],
    SixW.WHERE: [
        r"哪里|where|location|位置|部署|deployment|located|位于",
        r"环境|environment|physical|物理|设施|facility|网络|network",
        r"拓扑|topology|架构图|architecture",
    ],
    SixW.WHO: [
        r"谁|who|哪个组织|哪个系统|哪个角色|哪个人员",
        r"执行|perform|responsible|负责|承担",
        r"组织|organization|system|系统|角色|role|人员|personnel",
        r"提供|provide|支持|support|使用|use",
    ],
    SixW.WHEN: [
        r"何时|when|时间|timeline|时间线|schedule|计划",
        r"顺序|sequence|顺序|阶段|phase|里程碑|milestone|前置|prerequisite",
        r"先后|before|after|之前|之后|触发|trigger|启动|start|结束|end",
    ],
    SixW.WHY: [
        r"为何|why|为什么|原因|reason|purpose|目的|goal|目标|objective",
        r"依据|based on|依据|规则|rule|标准|standard|规范|regulation|政策|policy",
        r"要求|requirement|需求|必要|need|必须|must|应该|should",
    ],
}

# 6W 到 DoDAF 视图的映射
SIX_W_TO_VIEWS = {
    SixW.WHAT: ["AV-2", "DIV-1", "DIV-2", "DIV-3"],
    SixW.HOW: ["OV-5a", "OV-5b", "SV-4", "SvcV-4", "CV-2"],
    SixW.WHERE: ["OV-2", "SV-2", "SvcV-2", "OV-1"],
    SixW.WHO: ["OV-4", "OV-2", "SV-1", "SvcV-1"],
    SixW.WHEN: ["PV-2", "CV-3", "OV-6b", "OV-6c"],
    SixW.WHY: ["CV-1", "AV-1", "StdV-1", "OV-6a"],
}

# 6W 到 DM2 数据组的映射
SIX_W_TO_DM2_GROUPS = {
    SixW.WHAT: ["Resource", "Information", "Project", "Capability"],
    SixW.HOW: ["Activity", "Capability", "Service", "Measure"],
    SixW.WHERE: ["Location", "Performer"],
    SixW.WHO: ["Performer", "Organization"],
    SixW.WHEN: ["Project", "Activity", "Measure"],
    SixW.WHY: ["Rules", "Guidance", "Capability"],
}


class SixWAnalyzer:
    """6W 问题分析器"""

    def __init__(self):
        self._patterns = SIX_W_PATTERNS

    def analyze(self, query: str) -> SixWAnalysis:
        """
        分析用户查询，确定 6W 焦点

        Args:
            query: 用户输入的自然语言查询

        Returns:
            SixWAnalysis 分析结果
        """
        query_lower = query.lower()
        query_cn = query  # 保留中文原文

        # 统计每个 6W 的匹配次数
        scores = {w: 0 for w in SixW}
        matched_patterns = {w: [] for w in SixW}

        for w, patterns in self._patterns.items():
            for pattern in patterns:
                # 尝试中英文匹配
                if re.search(pattern, query_lower) or re.search(pattern, query_cn):
                    scores[w] += 1
                    matched_patterns[w].append(pattern)

        # 确定主要 6W
        if max(scores.values()) == 0:
            # 默认 What
            primary = SixW.WHAT
        else:
            primary = max(scores, key=scores.get)

        # 确定次要 6W（得分 > 0 但不是最高）
        secondary = [w for w, s in scores.items() if s > 0 and w != primary]
        secondary.sort(key=lambda w: scores[w], reverse=True)

        # 计算置信度
        total_score = sum(scores.values())
        if total_score > 0:
            confidence = scores[primary] / total_score
        else:
            confidence = 0.5  # 默认

        # 提取实体
        entities = self._extract_entities(query)

        # 生成建议视图
        suggested = self._get_suggested_views(primary, secondary)

        # 生成推理过程
        reasoning = self._generate_reasoning(primary, scores, matched_patterns)

        return SixWAnalysis(
            primary_w=primary,
            secondary_ws=secondary[:2],  # 最多2个次要
            confidence=confidence,
            reasoning=reasoning,
            extracted_entities=entities,
            suggested_views=suggested,
        )

    def _extract_entities(self, query: str) -> dict[str, list[str]]:
        """从查询中提取实体"""
        entities = {
            "system": [],
            "organization": [],
            "activity": [],
            "resource": [],
            "capability": [],
            "location": [],
            "measure": [],
        }

        # 简单的实体模式匹配
        system_patterns = [
            r"[一-龥]*(?:系统|防火墙|USG|网关|交换机|路由器|服务器|平台)[一-龥]*",
            r"\b(?:firewall|firewall|router|switch|server|platform|system)\b",
        ]
        org_patterns = [
            r"[一-龥]*(?:公司|部门|机构|组织|团队|厂商|集成商|甲方|乙方)[一-龥]*",
            r"\b(?:company|department|team|organization|vendor|integrator)\b",
        ]
        activity_patterns = [
            r"[一-龥]*(?:检测|防御|监控|审计|认证|授权|加密|传输|存储|处理|分析)[一-龥]*",
            r"\b(?:detect|defend|monitor|audit|authenticate|authorize|encrypt|transmit|process)\b",
        ]

        for pattern in system_patterns:
            entities["system"].extend(re.findall(pattern, query))
        for pattern in org_patterns:
            entities["organization"].extend(re.findall(pattern, query))
        for pattern in activity_patterns:
            entities["activity"].extend(re.findall(pattern, query))

        # 去重
        for key in entities:
            entities[key] = list(set(entities[key]))

        return entities

    def _get_suggested_views(self, primary: SixW, secondary: list[SixW]) -> list[str]:
        """获取建议的 DoDAF 视图"""
        views = set(SIX_W_TO_VIEWS[primary])
        for w in secondary:
            views.update(SIX_W_TO_VIEWS[w])
        return sorted(list(views))

    def _generate_reasoning(self, primary: SixW, scores: dict, matched: dict) -> str:
        """生成分析推理过程"""
        lines = [f"主要 6W: {primary.value} (得分: {scores[primary]})"]
        if matched[primary]:
            lines.append(f"  匹配模式: {matched[primary][0]}")
        if matched[primary]:
            secondary_ws = [w for w in matched.keys() if scores[w] > 0 and w != primary]
            secondary_ws.sort(key=lambda w: scores[w], reverse=True)
            lines.append(f"  次要 6W: {', '.join(w.value for w in secondary_ws[:2])}")
        return "\n".join(lines)

    def get_viewpoint_for_w(self, w: SixW) -> list[str]:
        """获取特定 6W 对应的视点"""
        view_mapping = {
            SixW.WHAT: ["AV", "DIV"],
            SixW.HOW: ["OV", "SV", "SvcV", "CV"],
            SixW.WHERE: ["OV", "SV", "SvcV"],
            SixW.WHO: ["OV", "SV", "SvcV"],
            SixW.WHEN: ["PV", "CV", "OV"],
            SixW.WHY: ["CV", "AV", "StdV"],
        }
        return view_mapping.get(w, [])


if __name__ == "__main__":
    analyzer = SixWAnalyzer()

    test_queries = [
        "防火墙如何检测网络威胁？",
        "有哪些系统参与数据交换？",
        "谁负责执行安全审计？",
        "资产梳理的活动流程是什么？",
        "为什么要实施等保 2.0？",
    ]

    for q in test_queries:
        result = analyzer.analyze(q)
        print(f"\n查询: {q}")
        print(f"  主要: {result.primary_w.value} (置信度: {result.confidence:.2f})")
        print(f"  次要: {[w.value for w in result.secondary_ws]}")
        print(f"  建议视图: {result.suggested_views}")
        print(f"  提取实体: {result.extracted_entities}")
