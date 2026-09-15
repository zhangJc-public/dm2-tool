"""
CynefinDeriver — 从自然语言描述推导 Cynefin 维度投票

CLI 的 `dm2 cynefin -d` 与 pipeline 的 Step1IntentScope 共用本模块，
保证同一描述在两条路径上产出完全一致的维度值、危机信号与规模剖面。

极性安全：
- clear / complicated 词表的正面词在编译时加否定前缀后顾断言
  （不|未|没|无|毫|并不|尚未|难以），「不确定」不会再被「确定」二次命中；
- 否定式（不确定、无先例、规则缺失）直接列在 complex 词表；
- 全部匹配按长度优先、去重叠：「难以协调」覆盖其包含的「协调」。

词库为外部 YAML：dm2-reference/core/cynefin-keywords.yaml。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Optional

import yaml

from dm2.cognitive.cynefin_analyzer import (
    DIMENSION_IDS,
    DimensionVote,
    ScaleProfile,
    Tendency,
)
from dm2.utils.paths import get_reference_path

KEYWORDS_FILENAME = "cynefin-keywords.yaml"
TENDENCY_KEYS = ("clear", "complicated", "complex")
_MAX_EVIDENCE_PER_VOTE = 3


class CynefinKeywordsError(RuntimeError):
    """词库配置缺失或损坏。"""


@dataclass
class Derivation:
    """一次文本推导的完整结果。"""
    votes: list[DimensionVote]
    crisis: bool
    scale_profile: ScaleProfile
    crisis_evidence: list[str] = field(default_factory=list)


@lru_cache(maxsize=1)
def load_cynefin_keywords() -> dict:
    """加载外部词库 YAML（本地 .dm2/reference 优先，包内置 core 回退）。"""
    ref = get_reference_path()
    candidates = [
        ref / KEYWORDS_FILENAME,
        ref.parent / KEYWORDS_FILENAME,
    ]
    for path in candidates:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if not isinstance(data, dict) or "dimensions" not in data:
                raise CynefinKeywordsError(f"词库格式无效：{path}")
            return data
    searched = "\n  ".join(str(p) for p in candidates)
    raise CynefinKeywordsError(f"未找到 {KEYWORDS_FILENAME}，已查找：\n  {searched}")


def votes_from_user(values: dict[str, str]) -> list[DimensionVote]:
    """从 CLI 显式选项构造用户投票；未提供的维度弃权。"""
    votes = []
    for dim_id in DIMENSION_IDS:
        raw = (values or {}).get(dim_id)
        if raw is None:
            votes.append(DimensionVote(dim_id, None, source="user"))
        else:
            votes.append(
                DimensionVote(
                    dim_id,
                    Tendency(raw),
                    evidence=["用户显式指定"],
                    source="user",
                )
            )
    return votes


class CynefinDeriver:
    """关键词/正则推导器（零 LLM 依赖）。"""

    def __init__(self, keywords: Optional[dict] = None):
        self.kw = keywords or load_cynefin_keywords()
        self._negation_guard = self._build_negation_guard(
            self.kw.get("negation_prefixes", [])
        )

    # ── 公开接口 ─────────────────────────────────────────────────────
    def derive(self, text: str) -> Derivation:
        text = text or ""

        crisis_spans, crisis_evidence = self._match_group(
            text, self.kw.get("crisis", []), guard_negation=False
        )
        crisis = bool(crisis_spans)

        votes: list[DimensionVote] = []
        blocked = crisis_spans  # 危机命中片段不回流维度匹配
        for dim_id in DIMENSION_IDS:
            votes.append(self._derive_dimension(text, dim_id, blocked))

        scale = self._derive_scale(text)

        return Derivation(
            votes=votes,
            crisis=crisis,
            crisis_evidence=crisis_evidence,
            scale_profile=scale,
        )

    # ── 单维度决策 ───────────────────────────────────────────────────
    def _derive_dimension(
        self, text: str, dim_id: str, blocked: list[tuple[int, int]]
    ) -> DimensionVote:
        dim_cfg = self.kw["dimensions"].get(dim_id, {})

        # 跨三档倾向收集命中，再做一次全局长度优先去重叠，
        # 保证「分阶段明确」(complicated) 压过其包含的「明确」(clear)
        hits: list[tuple[int, int, str, str]] = []  # start, end, phrase, tendency
        for tendency in TENDENCY_KEYS:
            phrases = dim_cfg.get(tendency, []) or []
            # 有序侧（clear/complicated）正面词需要否定保护；complex 侧为字面否定式
            for start, end, phrase in self._iter_hits(
                text, phrases, guard_negation=tendency != "complex"
            ):
                hits.append((start, end, phrase, tendency))

        hits.sort(key=lambda h: (h[0], -(h[1] - h[0])))
        counts: dict[str, int] = {t: 0 for t in TENDENCY_KEYS}
        evidence: dict[str, list[str]] = {t: [] for t in TENDENCY_KEYS}
        cursor = 0
        for start, end, phrase, tendency in hits:
            if start < cursor:
                continue
            if any(start < b_end and end > b_start for b_start, b_end in blocked):
                continue
            counts[tendency] += 1
            if phrase not in evidence[tendency]:
                evidence[tendency].append(phrase)
            cursor = end

        winner = max(counts, key=counts.get)
        if counts[winner] == 0:
            return DimensionVote(dim_id, None)
        tied = [t for t in TENDENCY_KEYS if counts[t] == counts[winner]]
        if len(tied) > 1:
            # 倾向平票：弃权，但保留双向证据（矛盾信号不过度解读）
            flat = self._merge_evidence(evidence, tied)
            return DimensionVote(dim_id, None, evidence=flat)

        return DimensionVote(
            dim_id, Tendency(winner), evidence=evidence[winner][:_MAX_EVIDENCE_PER_VOTE]
        )

    # ── 规模剖面 ─────────────────────────────────────────────────────
    def _derive_scale(self, text: str) -> ScaleProfile:
        scale_cfg = self.kw.get("scale", {})

        _, sys_terms = self._match_group(
            text, scale_cfg.get("system_terms", []), guard_negation=False
        )
        sys_count = len(sys_terms)
        systems = 1 if sys_count <= 1 else 3 if sys_count <= 5 else 8

        _, org_terms = self._match_group(
            text, scale_cfg.get("org_terms", []), guard_negation=False
        )
        stakeholders = len(org_terms) or None

        time_cfg = scale_cfg.get("time", {})
        time_span: Optional[str] = None
        for span_name in ("long", "medium", "short"):
            spans, _ = self._match_group(
                text, time_cfg.get(span_name, []), guard_negation=False
            )
            if spans:
                time_span = span_name
                break

        return ScaleProfile(
            systems=systems if sys_count else None,
            time_span=time_span,
            stakeholders=stakeholders,
        )

    # ── 匹配引擎 ─────────────────────────────────────────────────────
    def _iter_hits(
        self, text: str, phrases: list[str], guard_negation: bool
    ) -> list[tuple[int, int, str]]:
        """返回组词的全部原始命中 (start, end, phrase)，不做去重叠。"""
        hits: list[tuple[int, int, str]] = []
        for phrase in sorted({p for p in phrases if p}, key=len, reverse=True):
            pattern = self._compile_phrase(phrase, guard_negation)
            for m in pattern.finditer(text):
                hits.append((m.start(), m.end(), phrase))
        return hits

    def _match_group(
        self,
        text: str,
        phrases: list[str],
        guard_negation: bool,
        blocked: Optional[list[tuple[int, int]]] = None,
    ) -> tuple[list[tuple[int, int]], list[str]]:
        """对一组词做长度优先、去重叠匹配，返回 (跨度列表, 去重命中词)。"""
        blocked = blocked or []
        hits = self._iter_hits(text, phrases, guard_negation)

        # 长度优先 + 起始位置排序；去重叠，并剔除被封锁片段
        hits.sort(key=lambda h: (h[0], -(h[1] - h[0])))
        spans: list[tuple[int, int]] = []
        matched: list[str] = []
        cursor = 0
        for start, end, phrase in hits:
            if start < cursor:
                continue
            if any(start < b_end and end > b_start for b_start, b_end in blocked):
                continue
            spans.append((start, end))
            if phrase not in matched:
                matched.append(phrase)
            cursor = end
        return spans, matched

    def _compile_phrase(self, phrase: str, guard_negation: bool) -> re.Pattern:
        body = re.escape(phrase)
        if phrase.isascii():
            body = rf"\b{body}\b"
        pattern = (self._negation_guard if guard_negation else "") + body
        return re.compile(pattern, re.IGNORECASE)

    @staticmethod
    def _build_negation_guard(prefixes: list[str]) -> str:
        singles = "".join(p for p in prefixes if len(p) == 1)
        multis = [p for p in prefixes if len(p) > 1]
        parts = []
        if singles:
            parts.append(f"(?<![{re.escape(singles)}])")
        parts.extend(f"(?<!{re.escape(p)})" for p in multis)
        return "".join(parts)

    @staticmethod
    def _merge_evidence(evidence: dict[str, list[str]], tendencies: list[str]) -> list[str]:
        merged: list[str] = []
        for t in tendencies:
            for term in evidence.get(t, []):
                if term not in merged:
                    merged.append(term)
        return merged[:_MAX_EVIDENCE_PER_VOTE]
