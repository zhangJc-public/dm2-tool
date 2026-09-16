"""
CynefinDeriver — 从自然语言描述提取 Cynefin 评估证据（v2）

CLI 的 `dm2 cynefin -d` 与 pipeline 的 Step1IntentScope 共用本模块，
保证同一描述在两条路径上产出完全一致的预填投票、危机信号与规模剖面。

本模块只做机械的证据提取，不做语义承诺：
- 维度词表产生启发式预填（prefill），最终域由 Agent/人按 rubric 量表裁定；
- 危机信号必须通过语境门控（候选词 + 窗口内门控词，且不落入排除复合词），
  被排除（excluded）或门控不足（weak）的候选全部写入 signal_report，不静默丢弃。

极性安全：
- clear / complicated 词表的正面词在编译时加否定前缀后顾断言
  （不|未|没|无|毫|并不|尚未|难以），「不确定」不会再被「确定」二次命中；
- 否定式（不确定、无先例、规则缺失）直接列在 complex 词表；
- 全部匹配按长度优先、去重叠：「难以协调」覆盖其包含的「协调」。

词库为外部 YAML（version: 2）：dm2-reference/core/cynefin-keywords.yaml。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
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
KEYWORDS_VERSION = 2
TENDENCY_KEYS = ("clear", "complicated", "complex")
_MAX_EVIDENCE_PER_VOTE = 3
MIN_INFORMED_FOR_WARNING = 3


class CynefinKeywordsError(RuntimeError):
    """词库配置缺失、损坏或版本不兼容。"""


@dataclass
class Derivation:
    """一次文本推导的完整结果（证据卷宗）。"""
    votes: list[DimensionVote]
    crisis: bool
    scale_profile: ScaleProfile
    crisis_evidence: list[str] = field(default_factory=list)
    signal_report: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _package_keyword_candidates() -> list[Path]:
    """包内置词库候选（editable/仓库检出可用；wheel 安装另需打包修复）。"""
    base = Path(__file__).resolve().parents[3] / "dm2-reference"
    return [base / "core" / KEYWORDS_FILENAME, base / KEYWORDS_FILENAME]


@lru_cache(maxsize=1)
def load_cynefin_keywords() -> dict:
    """加载外部词库 YAML：项目本地 .dm2/reference 优先，包内置 core 回退。

    老工程的本地参考库可能缺词库文件 → 回退包内置副本；
    若找到的是 v1 词库（扁平 crisis 列表）→ 明确报版本错误而非静默误判。
    """
    ref = get_reference_path()
    candidates = [
        ref / KEYWORDS_FILENAME,
        ref.parent / KEYWORDS_FILENAME,
        *_package_keyword_candidates(),
    ]
    searched: list[Path] = []
    for path in candidates:
        if not path.exists():
            searched.append(path)
            continue
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict) or "dimensions" not in data:
            raise CynefinKeywordsError(f"词库格式无效：{path}")
        if data.get("version") != KEYWORDS_VERSION:
            raise CynefinKeywordsError(
                f"词库版本不兼容：{path} 为 v{data.get('version')}，"
                f"需要 v{KEYWORDS_VERSION}。请重新同步参考库"
                f"（重新运行 dm2 init，或用包内置 {KEYWORDS_FILENAME} 覆盖本地副本）。"
            )
        return data
    raise CynefinKeywordsError(
        f"未找到 {KEYWORDS_FILENAME}，已查找：\n  "
        + "\n  ".join(str(p) for p in searched)
    )


def load_rubric(keywords: Optional[dict] = None) -> dict[str, dict]:
    """读取五维评估量表 {dim_id: {question, anchors:{clear,complicated,complex}}}。"""
    kw = keywords or load_cynefin_keywords()
    rubric: dict[str, dict] = {}
    for dim_id in DIMENSION_IDS:
        cfg = kw.get("dimensions", {}).get(dim_id, {}).get("rubric", {}) or {}
        rubric[dim_id] = {
            "question": cfg.get("question", ""),
            "anchors": {k: cfg.get("anchors", {}).get(k, "") for k in TENDENCY_KEYS},
        }
    return rubric


def build_rubric_payload(
    votes: Optional[list[DimensionVote]] = None,
    keywords: Optional[dict] = None,
) -> list[dict]:
    """组装量表 JSON：每维引导问题 + 三档锚点 + 启发式 prefill（无 votes 则空白）。"""
    rubric_cfg = load_rubric(keywords)
    by_id = {v.dimension_id: v for v in (votes or [])}
    payload: list[dict] = []
    for dim_id in DIMENSION_IDS:
        vote = by_id.get(dim_id)
        payload.append({
            "id": dim_id,
            "question": rubric_cfg[dim_id]["question"],
            "anchors": rubric_cfg[dim_id]["anchors"],
            "prefill": vote.tendency.value if vote and vote.tendency else None,
            "prefill_evidence": list(vote.evidence) if vote else [],
        })
    return payload


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
    """语境规则推导器（零 LLM 依赖）。"""

    def __init__(self, keywords: Optional[dict] = None):
        self.kw = keywords if keywords is not None else load_cynefin_keywords()
        # 允许测试注入无版本词库；生产加载已做版本校验
        self._negation_guard = self._build_negation_guard(
            self.kw.get("negation_prefixes", [])
        )

    # ── 公开接口 ─────────────────────────────────────────────────────
    def derive(self, text: str) -> Derivation:
        text = text or ""

        crisis_eval = self._evaluate_crisis(text)
        fired_spans = crisis_eval["fired_spans"]

        votes: list[DimensionVote] = []
        for dim_id in DIMENSION_IDS:
            votes.append(self._derive_dimension(text, dim_id, fired_spans))

        warnings = list(crisis_eval["warnings"])
        warnings.extend(self._vote_warnings(votes))

        return Derivation(
            votes=votes,
            crisis=crisis_eval["crisis"],
            crisis_evidence=crisis_eval["evidence"],
            signal_report=crisis_eval["report"],
            warnings=warnings,
            scale_profile=self._derive_scale(text),
        )

    # ── 危机语境规则 ─────────────────────────────────────────────────
    def _evaluate_crisis(self, text: str) -> dict:
        cfg = self.kw.get("crisis", {}) or {}
        signals = cfg.get("signals", []) or []

        # 全部排除复合词跨度（跨规则汇总，任一候选与之重叠即 excluded）
        exclusion_spans: list[tuple[int, int, str]] = []
        for sig in signals:
            for hit in self._iter_hits(text, sig.get("exclude", []) or [], False):
                exclusion_spans.append(hit)

        report: list[dict] = []
        fired_spans: list[tuple[int, int]] = []
        evidence: list[str] = []

        def overlaps_exclusion(s: int, e: int) -> Optional[str]:
            for xs, xe, phrase in exclusion_spans:
                if s < xe and e > xs:
                    return phrase
            return None

        def record(rule: str, matched: str, verdict: str,
                   reason: Optional[str], gate: Optional[str],
                   span: Optional[tuple[int, int]] = None) -> None:
            report.append({
                "rule": rule,
                "matched": matched,
                "verdict": verdict,
                "reason": reason,
                "gate": gate,
            })
            if verdict == "fired" and span is not None:
                fired_spans.append(span)

        for sig in signals:
            rule_id = sig.get("id", "crisis")
            window = int(sig.get("window", 6))
            gates = sig.get("require_near", []) or []
            for s, e, candidate in self._iter_hits(
                text, sig.get("candidates", []) or [], False
            ):
                excl = overlaps_exclusion(s, e)
                if excl is not None:
                    record(rule_id, candidate, "excluded",
                            f"命中规划/准备复合词「{excl}」", None)
                    continue
                gate_hit = self._find_gate(text, s, e, gates, window)
                if gate_hit:
                    record(rule_id, candidate, "fired", None, gate_hit, span=(s, e))
                else:
                    record(rule_id, candidate, "weak",
                            f"左右 {window} 字内无门控词（{'/'.join(gates)}）", None)

        # direct：门控语义内嵌的强短语，但同样受排除跨度否决
        for s, e, phrase in self._iter_hits(text, cfg.get("direct", []) or [], False):
            excl = overlaps_exclusion(s, e)
            if excl is not None:
                record("direct", phrase, "excluded",
                        f"命中规划/准备复合词「{excl}」", None)
            else:
                record("direct", phrase, "fired", None, None, span=(s, e))

        warnings: list[str] = []
        for entry in report:
            if entry["verdict"] == "fired":
                detail = f"「{entry['matched']}」"
                if entry.get("gate"):
                    detail += f"（门控词「{entry['gate']}」）"
                if detail not in evidence:
                    evidence.append(detail)
            elif entry["verdict"] == "excluded":
                warnings.append(
                    f"危机候选词「{entry['matched']}」{entry['reason']}，未计为危机；"
                    "若实际为正在发生的事件，请用 --domain 裁定"
                )
            else:
                warnings.append(
                    f"危机候选词「{entry['matched']}」{entry['reason']}，未计为危机；"
                    "若危机正在发生，请用 --domain 裁定"
                )

        return {
            "crisis": any(r["verdict"] == "fired" for r in report),
            "fired_spans": fired_spans,
            "evidence": evidence[:_MAX_EVIDENCE_PER_VOTE],
            "report": report,
            "warnings": warnings,
        }

    def _find_gate(
        self, text: str, start: int, end: int, gates: list[str], window: int
    ) -> Optional[str]:
        """在候选跨度左右 window 字符内查找门控词，返回命中的门控词。"""
        lo = max(0, start - window)
        hi = min(len(text), end + window)
        neighborhood = text[lo:hi]
        hits = self._match_group(neighborhood, gates, guard_negation=False)[1]
        return hits[0] if hits else None

    def _vote_warnings(self, votes: list[DimensionVote]) -> list[str]:
        warnings: list[str] = []
        informed = sum(1 for v in votes if v.informed)
        if informed < MIN_INFORMED_FOR_WARNING:
            warnings.append(
                f"仅 {informed}/5 个维度有证据，域判定依据不足，建议按量表澄清后裁定"
            )
        for v in votes:
            # 平票弃权维度携带双向证据（_derive_dimension 构造）
            if v.tendency is None and len(v.evidence) > 1:
                warnings.append(f"维度 {v.dimension_id} 倾向平票，已弃权：{'/'.join(v.evidence)}")
        return warnings

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
