"""
Cynefin Complexity Analyzer - 动态复杂度评估器
支持灵活的复杂度维度配置和动态评估
"""

from dataclasses import dataclass, field
from enum import Enum


class CynefinDomain(str, Enum):
    """Cynefin 域"""
    CLEAR = "Clear"       # 明晰 - 简单问题，最小视图集
    COMPLICATED = "Complicated"  # 繁杂 - 标准视图集
    COMPLEX = "Complex"   # 复杂 - 全量视图集
    CHAOTIC = "Chaotic"   # 混沌 - 全量 + Fusion


@dataclass
class ComplexityDimension:
    """复杂度评估维度"""
    name: str
    value: str  # "simple" / "medium" / "complex"
    weight: float = 1.0  # 权重，可动态调整
    evidence: list[str] = field(default_factory=list)  # 评估证据


@dataclass
class ComplexityAssessment:
    """复杂度评估结果"""
    domain: CynefinDomain
    confidence: float  # 0.0 - 1.0
    dimensions: list[ComplexityDimension]
    reasoning: str
    recommended_view_count: str
    reasoning_details: str

    @property
    def domain_label(self) -> str:
        labels = {
            CynefinDomain.CLEAR: "明晰（Simple）",
            CynefinDomain.COMPLICATED: "繁杂（Complicated）",
            CynefinDomain.COMPLEX: "复杂（Complex）",
            CynefinDomain.CHAOTIC: "混沌（Chaotic）",
        }
        return labels.get(self.domain, "未知")


class CynefinAnalyzer:
    """动态 Cynefin 复杂度分析器"""

    # 默认评估维度及其权重
    DEFAULT_DIMENSIONS = [
        ("system_count", "系统数量", 1.0),
        ("time_span", "时间跨度", 0.8),
        ("stakeholders", "干系人", 1.0),
        ("uncertainty", "不确定性", 1.2),  # 不确定性权重稍高
        ("rule_complexity", "规则复杂度", 1.0),
    ]

    # 域判定阈值（加权分数）
    DOMAIN_THRESHOLDS = {
        CynefinDomain.CLEAR: (0, 2.0),
        CynefinDomain.COMPLICATED: (2.0, 3.5),
        CynefinDomain.COMPLEX: (3.5, 5.0),
        CynefinDomain.CHAOTIC: (5.0, float('inf')),
    }

    def __init__(self, custom_dimensions: list[tuple[str, str, float]] = None):
        """
        初始化分析器

        Args:
            custom_dimensions: 自定义维度 [(id, name, weight), ...]
        """
        if custom_dimensions:
            self.dimensions_config = custom_dimensions
        else:
            self.dimensions_config = self.DEFAULT_DIMENSIONS

    def assess(
        self,
        dimension_values: dict[str, str],
        evidence: dict[str, list[str]] = None,
        context: str = ""
    ) -> ComplexityAssessment:
        """
        评估复杂度

        Args:
            dimension_values: {维度ID: "simple"/"medium"/"complex"}
            evidence: {维度ID: [证据列表]}
            context: 额外上下文信息

        Returns:
            ComplexityAssessment
        """
        dimensions = []
        total_weighted_score = 0.0
        total_weight = 0.0

        for dim_id, dim_name, weight in self.dimensions_config:
            value = dimension_values.get(dim_id, "medium")
            dim_evidence = evidence.get(dim_id, []) if evidence else []

            # 转换维度值为分数
            score = self._value_to_score(value)

            dimensions.append(ComplexityDimension(
                name=dim_name,
                value=value,
                weight=weight,
                evidence=dim_evidence,
            ))

            total_weighted_score += score * weight
            total_weight += weight

        # 计算加权平均分数
        avg_score = total_weighted_score / total_weight if total_weight > 0 else 0

        # 判定域
        domain = self._score_to_domain(avg_score)

        # 生成理由
        reasoning = self._generate_reasoning(dimensions, domain, context)

        # 推荐视图数量
        view_count = self._get_recommended_view_count(domain)

        return ComplexityAssessment(
            domain=domain,
            confidence=0.85,  # 固定置信度，可根据证据量调整
            dimensions=dimensions,
            reasoning=f"基于 {len(dimensions)} 个维度评估，判定为「{domain.value}」域",
            recommended_view_count=view_count,
            reasoning_details=reasoning,
        )

    def _value_to_score(self, value: str) -> float:
        """将维度值转换为分数"""
        mapping = {
            "simple": 1.0,
            "medium": 2.0,
            "complex": 3.0,
        }
        return mapping.get(value.lower(), 2.0)

    def _score_to_domain(self, avg_score: float) -> CynefinDomain:
        """根据平均分数判定域"""
        for domain, (lower, upper) in self.DOMAIN_THRESHOLDS.items():
            if lower <= avg_score < upper:
                return domain
        return CynefinDomain.COMPLEX

    def _generate_reasoning(
        self,
        dimensions: list[ComplexityDimension],
        domain: CynefinDomain,
        context: str
    ) -> str:
        """生成详细的评估理由"""
        lines = [f"复杂度评估（{domain.value}域）："]

        high_impact_dims = [d for d in dimensions if d.value == "complex" and d.weight >= 1.0]
        if high_impact_dims:
            lines.append("高影响维度：")
            for d in high_impact_dims:
                lines.append(f"  - {d.name}（复杂，权重 {d.weight}）")
                if d.evidence:
                    for e in d.evidence[:2]:  # 最多显示2条证据
                        lines.append(f"    证据：{e}")

        lines.append(f"加权平均分数：{sum(d.weight * self._value_to_score(d.value) for d in dimensions) / sum(d.weight for d in dimensions):.2f}")

        if context:
            lines.append(f"上下文：{context[:100]}")

        return "\n".join(lines)

    def _get_recommended_view_count(self, domain: CynefinDomain) -> str:
        """根据域获取推荐视图数量"""
        mapping = {
            CynefinDomain.CLEAR: "2-4 个（OV-1 + CV-1）",
            CynefinDomain.COMPLICATED: "12-17 个（P0 核心）",
            CynefinDomain.COMPLEX: "38+ 个（P0+P1）+ 行为三件套",
            CynefinDomain.CHAOTIC: "全量 + Fusion Views + 实时模拟",
        }
        return mapping.get(domain, "未知")

    def get_dynamic_thresholds(
        self,
        domain: CynefinDomain,
        adjustment: float = 0.0
    ) -> tuple[float, float]:
        """
        获取动态阈值（用于调整评估严格度）

        Args:
            domain: 目标域
            adjustment: 调整值（正数使评估更严格，负数使评估更容易）

        Returns:
            (下限, 上限)
        """
        lower, upper = self.DOMAIN_THRESHOLDS[domain]
        return lower + adjustment, upper + adjustment


@dataclass
class DynamicComplexityConfig:
    """动态复杂度配置"""
    enable_dynamic_weights: bool = True  # 是否启用动态权重
    enable_context_aware: bool = True   # 是否启用上下文感知
    enable_evidence_weighting: bool = True  # 是否启用证据加权

    # 上下文敏感的维度权重调整
    CONTEXT_WEIGHT_ADJUSTMENTS = {
        "security": {"uncertainty": 1.3, "rule_complexity": 1.2},
        "ai": {"uncertainty": 1.4, "system_count": 1.1},
        "compliance": {"rule_complexity": 1.3, "stakeholders": 1.1},
    }

    def get_adjusted_weights(
        self,
        base_dimensions: list[tuple[str, str, float]],
        context: str
    ) -> list[tuple[str, str, float]]:
        """根据上下文调整维度权重"""
        if not self.enable_dynamic_weights:
            return base_dimensions

        adjusted = []
        context_lower = context.lower()

        # 检查匹配的上下文
        matched_context = None
        for key in self.CONTEXT_WEIGHT_ADJUSTMENTS:
            if key in context_lower:
                matched_context = key
                break

        if matched_context:
            weight_adjs = self.CONTEXT_WEIGHT_ADJUSTMENTS[matched_context]
            for dim_id, dim_name, weight in base_dimensions:
                adj_weight = weight * weight_adjs.get(dim_id, 1.0)
                adjusted.append((dim_id, dim_name, adj_weight))
        else:
            adjusted = base_dimensions

        return adjusted


if __name__ == "__main__":
    # 测试
    analyzer = CynefinAnalyzer()

    test_cases = [
        {
            "name": "简单单系统",
            "values": {
                "system_count": "simple",
                "time_span": "simple",
                "stakeholders": "simple",
                "uncertainty": "simple",
                "rule_complexity": "simple",
            },
            "context": "单一系统部署"
        },
        {
            "name": "等保三级医院",
            "values": {
                "system_count": "complex",
                "time_span": "medium",
                "stakeholders": "complex",
                "uncertainty": "medium",
                "rule_complexity": "complex",
            },
            "context": "医院信息安全等保三级"
        },
        {
            "name": "AI系统复杂评估",
            "values": {
                "system_count": "medium",
                "time_span": "medium",
                "stakeholders": "medium",
                "uncertainty": "complex",
                "rule_complexity": "medium",
            },
            "context": "AI安全评估"
        },
    ]

    for case in test_cases:
        result = analyzer.assess(case["values"], context=case["context"])
        print(f"\n{'='*50}")
        print(f"测试：{case['name']}")
        print(f"域：{result.domain_label}")
        print(f"推荐视图数：{result.recommended_view_count}")
        print(f"理由：\n{result.reasoning_details}")
