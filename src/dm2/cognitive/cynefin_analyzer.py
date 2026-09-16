"""
Cynefin Complexity Analyzer — 基于因果可知性的复杂度评估

模型要点：
- 5 个语义维度（需求可知性 / 实践成熟度 / 环境动态性 / 目标一致性 / 约束清晰度），
  每个维度投出一张域倾向票（clear / complicated / complex）或弃权（None）。
- 域解析顺序：危机否决（Chaotic）→ 无证据 Disorder → 低证据+跨域矛盾 Disorder
  → ≥3 张 complex 硬触发（Complex）→ 加权带（Clear / Complicated / Complex）。
- 规模信号（系统数、时间跨度、干系人数）走独立的 ScaleProfile，不参与域判定。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

# 五个语义维度（ID → 中文名），顺序同时是输出顺序
DIMENSIONS: list[tuple[str, str]] = [
    ("requirement_knowability", "需求可知性"),
    ("practice_maturity", "实践成熟度"),
    ("environmental_dynamics", "环境动态性"),
    ("goal_alignment", "目标一致性"),
    ("constraint_clarity", "约束清晰度"),
]
DIMENSION_IDS = [dim_id for dim_id, _ in DIMENSIONS]
DIMENSION_LABELS = dict(DIMENSIONS)

# 维度默认权重（硬触发与带边界承担主要判别，权重保持均等以便解释）
DEFAULT_DIMENSION_WEIGHTS: dict[str, float] = {dim_id: 1.0 for dim_id in DIMENSION_IDS}

# 倾向 → 分数
TENDENCY_SCORES = {"clear": 1.0, "complicated": 2.0, "complex": 3.0}

# 加权带边界（投票维度的加权平均）
BAND_CLEAR_MAX = 1.5          # avg < 1.5 → Clear
BAND_COMPLICATED_MAX = 2.5    # 1.5 ≤ avg < 2.5 → Complicated；≥ 2.5 → Complex

# 硬触发：≥3 张 complex 票直接判 Complex
COMPLEX_HARD_TRIGGER = 3

# Disorder 证据门槛：携带证据（或用户显式赋值）的维度少于此值且跨域矛盾
MIN_INFORMED_DIMENSIONS = 3

# 置信度公式常量
CONFIDENCE_FLOOR = 0.20
CONFIDENCE_CEILING = 0.95
CONFIDENCE_BASE = 0.20
CONFIDENCE_COVERAGE_WEIGHT = 0.45
CONFIDENCE_AGREEMENT_WEIGHT = 0.30


class Tendency(str, Enum):
    """维度域倾向票"""
    CLEAR = "clear"
    COMPLICATED = "complicated"
    COMPLEX = "complex"


class Domain(str, Enum):
    """Cynefin 五域（含 Disorder 第 5 域）"""
    CLEAR = "Clear"
    COMPLICATED = "Complicated"
    COMPLEX = "Complex"
    CHAOTIC = "Chaotic"
    DISORDER = "Disorder"


_DOMAIN_LABELS = {
    Domain.CLEAR: "明晰（Clear）",
    Domain.COMPLICATED: "繁杂（Complicated）",
    Domain.COMPLEX: "复杂（Complex）",
    Domain.CHAOTIC: "混沌（Chaotic）",
    Domain.DISORDER: "不明（Disorder）",
}

# 域 → 视图深度档位
_DEPTH_TIERS: dict[Domain, tuple[str, str]] = {
    Domain.CLEAR: ("minimal", "2-4 个（OV-1 + CV-1）"),
    Domain.COMPLICATED: ("core", "12-17 个（P0 核心）"),
    Domain.COMPLEX: ("extended", "P0+P1 + 行为三件套"),
    Domain.CHAOTIC: ("full", "全量 + Fusion Views + 实时模拟"),
    Domain.DISORDER: ("none", "不推荐视图集，先完成需求澄清"),
}


@dataclass
class DimensionVote:
    """一个维度的投票结果。tendency=None 表示弃权（证据不足或平票）。"""
    dimension_id: str
    tendency: Optional[Tendency]
    evidence: list[str] = field(default_factory=list)
    source: str = "derived"  # derived | user

    @property
    def informed(self) -> bool:
        """该维度是否携带可依据的信息（证据或用户显式赋值）。"""
        return bool(self.evidence) or (self.source == "user" and self.tendency is not None)


@dataclass
class ScaleProfile:
    """规模剖面：工作量/广度信号，不参与域判定。"""
    systems: Optional[int] = None
    time_span: Optional[str] = None       # short | medium | long
    stakeholders: Optional[int] = None


@dataclass
class ComplexityAssessment:
    """复杂度评估结果"""
    domain: Domain
    confidence: float
    votes: list[DimensionVote]
    reasoning_details: str
    depth_tier: str
    depth_guidance: str
    needs_clarification: bool = False
    crisis: bool = False
    scale_profile: Optional[ScaleProfile] = None
    confidence_breakdown: dict = field(default_factory=dict)
    # heuristic：纯机械推导草案；adjudicated：经 Agent/人显式裁定
    resolution: str = "heuristic"
    warnings: list[str] = field(default_factory=list)
    signal_report: list[dict] = field(default_factory=list)
    # --domain 终裁时，机械规则原本建议的域（审计分歧用）
    mechanical_suggestion: Optional[str] = None

    @property
    def domain_label(self) -> str:
        return _DOMAIN_LABELS.get(self.domain, "未知")

    def to_dict(self, rubric: Optional[list[dict]] = None) -> dict:
        """序列化为结构化 JSON（CLI --json 与 analysis-state 持久化共用）。"""
        scale = self.scale_profile
        payload = {
            "domain": self.domain.value,
            "suggested_domain": (
                self.mechanical_suggestion
                if self.mechanical_suggestion is not None
                else self.domain.value
            ),
            "domain_label": self.domain_label,
            "resolution": self.resolution,
            "confidence": self.confidence,
            "confidence_breakdown": dict(self.confidence_breakdown),
            "crisis": self.crisis,
            "needs_clarification": self.needs_clarification,
            "depth_tier": self.depth_tier,
            "depth_guidance": self.depth_guidance,
            "warnings": list(self.warnings),
            "signal_report": list(self.signal_report),
            "dimensions": [
                {
                    "id": v.dimension_id,
                    "tendency": v.tendency.value if v.tendency else None,
                    "evidence": list(v.evidence),
                    "source": v.source,
                }
                for v in self.votes
            ],
            "scale_profile": {
                "systems": scale.systems if scale else None,
                "time_span": scale.time_span if scale else None,
                "stakeholders": scale.stakeholders if scale else None,
            },
            "reasoning": self.reasoning_details,
        }
        if self.mechanical_suggestion is not None:
            payload["mechanical_suggestion"] = self.mechanical_suggestion
        if rubric is not None:
            payload["rubric"] = rubric
        return payload


class CynefinAnalyzer:
    """Cynefin 域解析器：维度投票 + 硬触发 + 加权带。"""

    def __init__(self, weights: Optional[dict[str, float]] = None):
        self.weights = dict(DEFAULT_DIMENSION_WEIGHTS)
        if weights:
            unknown = set(weights) - set(DIMENSION_IDS)
            if unknown:
                raise ValueError(f"未知维度 ID: {sorted(unknown)}")
            self.weights.update(weights)

    def assess(
        self,
        votes: list[DimensionVote],
        crisis: bool = False,
        scale: Optional[ScaleProfile] = None,
        context: str = "",
        domain_override: Optional[Domain] = None,
        resolution: str = "heuristic",
        warnings: Optional[list[str]] = None,
        signal_report: Optional[list[dict]] = None,
    ) -> ComplexityAssessment:
        """
        解析 Cynefin 域。

        Args:
            votes: 各维度投票（可少于 5 个；缺失维度按弃权处理）
            crisis: 语境规则成立的危机信号（机械规则一票进 Chaotic）
            scale: 规模剖面（仅随结果报告）
            context: 附加上下文，写入理由文本
            domain_override: Agent/人终裁域；提供时跳过机械解析（证据卷宗仍保留）
            resolution: heuristic（推导草案）或 adjudicated（已裁定）
            warnings/signal_report: deriver 产出的证据卷宗，随结果透传
        """
        self._validate_votes(votes)
        by_id = {v.dimension_id: v for v in votes}
        ordered = [by_id[dim_id] for dim_id in DIMENSION_IDS if dim_id in by_id]

        # 机械解析（即使终裁也照算，作为 mechanical_suggestion 留痕）
        if crisis:
            mechanical = Domain.CHAOTIC
        else:
            mechanical = self._resolve_domain(ordered)

        mechanical_suggestion: Optional[str] = None
        if domain_override is not None:
            domain = domain_override
            mechanical_suggestion = mechanical.value
        else:
            domain = mechanical

        breakdown = self._confidence_breakdown(ordered)
        confidence = self._compute_confidence(breakdown)
        needs_clarification = domain == Domain.DISORDER
        depth_tier, depth_guidance = _DEPTH_TIERS[domain]

        reasoning = self._generate_reasoning(
            ordered, domain, confidence, breakdown, crisis, context,
            resolution, mechanical_suggestion,
        )

        return ComplexityAssessment(
            domain=domain,
            confidence=confidence,
            votes=ordered,
            reasoning_details=reasoning,
            depth_tier=depth_tier,
            depth_guidance=depth_guidance,
            needs_clarification=needs_clarification,
            crisis=crisis,
            scale_profile=scale,
            confidence_breakdown=breakdown,
            resolution=resolution,
            warnings=list(warnings or []),
            signal_report=list(signal_report or []),
            mechanical_suggestion=mechanical_suggestion,
        )

    # ── 域解析 ─────────────────────────────────────────────────────────
    @staticmethod
    def _validate_votes(votes: list[DimensionVote]) -> None:
        ids = [v.dimension_id for v in votes]
        unknown = set(ids) - set(DIMENSION_IDS)
        if unknown:
            raise ValueError(f"未知维度 ID: {sorted(unknown)}")
        if len(ids) != len(set(ids)):
            raise ValueError("维度投票存在重复 ID")
        for v in votes:
            if v.source not in ("derived", "user"):
                raise ValueError(f"未知 vote source: {v.source}")

    def _resolve_domain(self, votes: list[DimensionVote]) -> Domain:
        voting = [v for v in votes if v.tendency is not None]
        informed = [v for v in votes if v.informed]
        tendencies = [v.tendency for v in voting]

        # 2. 完全无依据：Disorder
        if len(voting) == 0:
            return Domain.DISORDER

        # 3. 低证据 + 跨域矛盾：Disorder
        if len(informed) < MIN_INFORMED_DIMENSIONS and self._cross_domain_split(tendencies):
            return Domain.DISORDER

        # 4. complex 硬触发
        complex_votes = sum(1 for t in tendencies if t == Tendency.COMPLEX)
        if complex_votes >= COMPLEX_HARD_TRIGGER:
            return Domain.COMPLEX

        # 5. 加权带（弃权维度不进分子分母）
        weighted_sum = sum(
            TENDENCY_SCORES[t.value] * self.weights[v.dimension_id]
            for v, t in ((v, v.tendency) for v in voting)
        )
        total_weight = sum(self.weights[v.dimension_id] for v in voting)
        avg = weighted_sum / total_weight if total_weight else 0.0

        if avg < BAND_CLEAR_MAX:
            return Domain.CLEAR
        if avg < BAND_COMPLICATED_MAX:
            return Domain.COMPLICATED
        return Domain.COMPLEX

    @staticmethod
    def _cross_domain_split(tendencies: list[Tendency]) -> bool:
        """票中同时含 clear 与 complex，或三档齐备。"""
        values = {t.value for t in tendencies}
        return ("clear" in values and "complex" in values) or len(values) == 3

    # ── 置信度 ─────────────────────────────────────────────────────────
    @staticmethod
    def _confidence_breakdown(votes: list[DimensionVote]) -> dict:
        informed = sum(1 for v in votes if v.informed)
        coverage = informed / len(DIMENSION_IDS)

        voting_tendencies = [v.tendency for v in votes if v.tendency is not None]
        if not voting_tendencies:
            agreement = 0.0
        else:
            dispersion = (len({t.value for t in voting_tendencies}) - 1) / 2
            agreement = max(0.0, 1.0 - dispersion)

        return {
            "coverage": round(coverage, 4),
            "agreement": round(agreement, 4),
            "informed_dimensions": informed,
            "voting_dimensions": len(voting_tendencies),
        }

    @staticmethod
    def _compute_confidence(breakdown: dict) -> float:
        confidence = (
            CONFIDENCE_BASE
            + CONFIDENCE_COVERAGE_WEIGHT * breakdown["coverage"]
            + CONFIDENCE_AGREEMENT_WEIGHT * breakdown["agreement"]
        )
        return round(
            min(CONFIDENCE_CEILING, max(CONFIDENCE_FLOOR, confidence)), 4
        )

    # ── 理由文本 ───────────────────────────────────────────────────────
    def _generate_reasoning(
        self,
        votes: list[DimensionVote],
        domain: Domain,
        confidence: float,
        breakdown: dict,
        crisis: bool,
        context: str,
        resolution: str = "heuristic",
        mechanical_suggestion: Optional[str] = None,
    ) -> str:
        status = "启发式草案（未裁定）" if resolution == "heuristic" else "已经裁定"
        lines = [f"复杂度评估（{_DOMAIN_LABELS[domain]}，{status}）："]

        if mechanical_suggestion and mechanical_suggestion != domain.value:
            lines.append(
                f"  ⚠ 机械规则建议 {mechanical_suggestion}，"
                f"裁定域为 {domain.value}（分歧已留痕）"
            )
        if crisis and domain == Domain.CHAOTIC:
            lines.append("  ⚠ 语境成立的危机信号触发：一票判定为混沌域")

        for v in votes:
            label = DIMENSION_LABELS.get(v.dimension_id, v.dimension_id)
            if v.tendency is None:
                lines.append(f"  - {label}：弃权（证据不足或倾向平票）")
            else:
                src = "用户指定" if v.source == "user" else "文本推导"
                lines.append(f"  - {label}：{v.tendency.value}（{src}）")
            for e in v.evidence[:3]:
                lines.append(f"      证据：{e}")

        lines.append(
            f"评估置信度：{confidence:.0%}"
            f"（证据覆盖 {breakdown['coverage']:.0%}，"
            f"维度一致度 {breakdown['agreement']:.0%}）"
        )

        if domain == Domain.DISORDER:
            lines.append("  → 证据不足且维度间跨域矛盾（或完全无依据），请先回答澄清问题再选视图。")

        if context:
            lines.append(f"上下文：{context[:100]}")

        return "\n".join(lines)
