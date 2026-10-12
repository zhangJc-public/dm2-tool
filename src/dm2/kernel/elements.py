"""数据元 / 限定词组合器（GB/T 18391 · ISO/IEC 11179）。

把 DM2 术语名按「对象类 + 限定词 + 组合语法」组合成规范中文名。

- 纯函数、零 LLM：只有词元查找、模板匹配与结构规则
- 词表是权威源：`dm2-reference/dm2-element-vocabulary.yaml`
- 未登记词元返回 ``None``（不猜、不静默降级）
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

#: 术语名 → 词元：CamelCase 边界，含全大写缩写段（如 GeoStationaryPoint）
_TOKEN_RE = re.compile(r"[A-Z]+(?![a-z])|[A-Z][a-z0-9]*|[a-z0-9]+")

#: 查询片段切分：空白 + 中英文标点（与 indexer._search_tokens 同一口径）
_QUERY_SPLIT_RE = re.compile(r"[\s,，、;；:：/\\|()（）\[\]【】\"'“”‘’]+")

#: 词表位于 dm2-reference/（与 src/ 同级），非运行时资产
DEFAULT_VOCABULARY_PATH = (
    Path(__file__).resolve().parents[3] / "dm2-reference" / "dm2-element-vocabulary.yaml"
)


def split_tokens(name: str) -> List[str]:
    """把术语名分解为 casefold 后的词元序列。"""
    return [match.casefold() for match in _TOKEN_RE.findall(name)]


@dataclass(frozen=True)
class RelationTemplate:
    """组合语法：connectors 必须连续出现，{A}/{B} 是连接词前后的槽位。"""

    id: str
    connectors: Tuple[str, ...]
    zh: str
    strip_leading_type: Tuple[str, ...] = ()
    #: 渲染后折叠重复的「类型类型」→「类型」（如 measureOfTypeEndBoundaryType）
    collapse_type: bool = False


@dataclass(frozen=True)
class QuerySegment:
    """查询分解出的一个片段。"""

    text: str
    #: element（对象类）/ qualifier（结构词或关系谓词）/ unknown（词表无此词条）
    kind: str
    #: 反查命中的中文词条（英文片段为其本身；unknown 为空串）
    entry: str = ""
    #: 候选词元（unknown 为空元组）
    tokens: Tuple[str, ...] = ()


@dataclass(frozen=True)
class QueryPlan:
    """查询的反向分解：片段序列 + 词元模式候选。"""

    query: str
    segments: Tuple[QuerySegment, ...]

    @property
    def recognized(self) -> bool:
        """每个片段都在词表中有条目时才算可解析（模式匹配的前提）。"""
        return bool(self.segments) and all(s.kind != "unknown" for s in self.segments)

    @property
    def token_patterns(self) -> List[Tuple[str, ...]]:
        """所有候选词元组合（笛卡尔积，片段与候选都很小）。"""
        if not self.recognized:
            return []
        patterns: List[Tuple[str, ...]] = [()]
        for segment in self.segments:
            patterns = [prefix + (token,) for prefix in patterns for token in segment.tokens]
        return patterns


def pattern_matches(tokens: List[str], pattern: Tuple[str, ...]) -> bool:
    """判断 pattern 是否为 tokens 的**顺序子序列**（允许中间夹其他词元）。"""
    position = 0
    for token in pattern:
        while position < len(tokens) and tokens[position] != token:
            position += 1
        if position == len(tokens):
            return False
        position += 1
    return True


def first_pattern_match(tokens: List[str], patterns: List[Tuple[str, ...]]) -> Optional[Tuple[str, ...]]:
    """返回第一个匹配成功的模式（保持词表给出的候选顺序）。"""
    for pattern in patterns:
        if pattern_matches(tokens, pattern):
            return pattern
    return None


@dataclass
class ElementVocabulary:
    """数据元（对象类）+ 限定词 + 关系模板。"""

    elements: Dict[str, str] = field(default_factory=dict)
    qualifiers: Dict[str, str] = field(default_factory=dict)
    templates: List[RelationTemplate] = field(default_factory=list)
    compounds: Dict[str, str] = field(default_factory=dict)
    #: 反查：中文词条 → 候选词元（一对多，如 区域 → [area, region]）
    reverse: Dict[str, List[str]] = field(default_factory=dict)

    # ── 加载 ──────────────────────────────────────────────────────────
    @classmethod
    def load(cls, path: Optional[Path] = None) -> "ElementVocabulary":
        source = Path(path) if path is not None else DEFAULT_VOCABULARY_PATH
        data = yaml.safe_load(source.read_text(encoding="utf-8")) or {}
        elements = {
            str(key).casefold(): str(value)
            for key, value in (data.get("elements") or {}).items()
        }
        qualifiers = {
            str(key).casefold(): str(value)
            for key, value in (data.get("qualifiers") or {}).items()
        }
        templates = [
            RelationTemplate(
                id=str(item.get("id", "")),
                connectors=tuple(str(c).casefold() for c in (item.get("connectors") or [])),
                zh=str(item.get("zh", "")),
                strip_leading_type=tuple(str(s) for s in (item.get("strip_leading_type") or [])),
                collapse_type=bool(item.get("collapse_type")),
            )
            for item in (data.get("templates") or [])
        ]
        compounds = {
            " ".join(str(key).casefold().split()): str(value)
            for key, value in (data.get("compounds") or {}).items()
        }
        reverse: Dict[str, List[str]] = {}

        def _add_reverse(zh: str, tokens: List[str]) -> None:
            if not zh:
                return
            bucket = reverse.setdefault(zh, [])
            for token in tokens:
                if token not in bucket:
                    bucket.append(token)

        for token, zh in elements.items():
            _add_reverse(zh, [token])
        for token, zh in qualifiers.items():
            _add_reverse(zh, [token])
        for phrase, zh in compounds.items():
            _add_reverse(zh, phrase.split())

        return cls(
            elements=elements,
            qualifiers=qualifiers,
            templates=templates,
            compounds=compounds,
            reverse=reverse,
        )

    # ── 查询 ──────────────────────────────────────────────────────────
    def registered(self, token: str) -> bool:
        return token in self.elements or token in self.qualifiers

    def translate(self, token: str) -> Optional[str]:
        if token in self.elements:
            return self.elements[token]
        return self.qualifiers.get(token)

    @property
    def token_count(self) -> int:
        return len(self.elements) + len(self.qualifiers)

    # ── 组合 ──────────────────────────────────────────────────────────
    def compose(self, name: str) -> Optional[str]:
        """组合规范中文名；含未登记词元时返回 None。"""
        return self._compose(split_tokens(name))

    def _compose(self, tokens: List[str]) -> Optional[str]:
        if not tokens:
            return ""

        # 整串复合数据元优先于模板（如 `measure of desire` → 期望度量）
        whole = self._match_compound(tokens, 0)
        if whole is not None and whole[0] == len(tokens):
            return whole[1]

        # 前缀复合数据元优先于模板（如 `measure of desire type` 不能走 `measure of`）
        prefix_compound = self._match_compound(tokens, 0)
        if prefix_compound is not None:
            size, zh = prefix_compound
            rest = self._compose(tokens[size:])
            return None if rest is None else zh + rest

        hit = self._match_template(tokens)
        if hit is not None:
            template, start, end = hit
            a_tokens = tokens[:start]
            b_tokens = tokens[end:]
            if "B" in template.strip_leading_type and b_tokens and b_tokens[0] == "type":
                b_tokens = b_tokens[1:]
            left = self._compose(a_tokens) if a_tokens else ""
            right = self._compose(b_tokens) if b_tokens else ""
            if left is None or right is None:
                return None
            rendered = template.zh.replace("{A}", left).replace("{B}", right)
            if template.collapse_type:
                rendered = rendered.replace("类型类型", "类型", 1)
            return rendered

        # 结构规则：XTypeType → 「XType的类型」；XType → 「X类型」
        if len(tokens) >= 2 and tokens[-2:] == ["type", "type"]:
            prefix = self._compose(tokens[:-1])
            return None if prefix is None else prefix + "的类型"
        if len(tokens) >= 2 and tokens[-1] == "type":
            prefix = self._compose(tokens[:-1])
            return None if prefix is None else prefix + "类型"

        # 回退：复合数据元（多词元整体）优先，再逐词元拼接
        pieces: List[str] = []
        index = 0
        while index < len(tokens):
            compound = self._match_compound(tokens, index)
            if compound is not None:
                size, zh = compound
                pieces.append(zh)
                index += size
                continue
            zh = self.translate(tokens[index])
            if zh is None:
                return None
            pieces.append(zh)
            index += 1
        return "".join(pieces)

    def _match_compound(self, tokens: List[str], start: int) -> Optional[Tuple[int, str]]:
        """在 start 处匹配最长的复合数据元（多词元整体，如 `planar surface`）。"""
        best: Optional[Tuple[int, str]] = None
        for phrase, zh in self.compounds.items():
            parts = phrase.split()
            size = len(parts)
            if size == 0 or start + size > len(tokens):
                continue
            if tokens[start:start + size] != parts:
                continue
            if best is None or size > best[0]:
                best = (size, zh)
        return best

    def _match_template(
        self, tokens: List[str]
    ) -> Optional[Tuple[RelationTemplate, int, int]]:
        """取 connectors 最长匹配；等长时取词表中靠前的模板。"""
        best: Optional[Tuple[int, RelationTemplate, int, int]] = None
        for template in self.templates:
            size = len(template.connectors)
            if size == 0 or size > len(tokens):
                continue
            for start in range(len(tokens) - size + 1):
                if tuple(tokens[start:start + size]) != template.connectors:
                    continue
                end = start + size
                if "{A}" not in template.zh and start > 0:
                    continue
                if "{B}" not in template.zh and end < len(tokens):
                    continue
                if best is None or size > best[0]:
                    best = (size, template, start, end)
                break
        if best is None:
            return None
        return best[1], best[2], best[3]

    def tokens_for(self, text: str) -> List[str]:
        """中文/英文片段 → 候选词元（一对多；无命中返回空列表）。

        检索归一用：查询片段先尝试中文反查（`能力` → ``['capability']``、
        `区域` → ``['area', 'region']``），再尝试英文词元本身。
        """
        key = text.strip()
        if not key:
            return []
        candidates = self.reverse.get(key)
        if candidates:
            return list(candidates)
        folded = key.casefold()
        if self.registered(folded):
            return [folded]
        return []

    def plan_query(self, query: str) -> QueryPlan:
        """把查询反向分解为「数据元 + 限定词」序列（零 LLM，纯词表查表）。"""
        segments: List[QuerySegment] = []
        for piece in _QUERY_SPLIT_RE.split(query.strip()):
            if not piece:
                continue
            tokens = self.tokens_for(piece)
            if not tokens:
                segments.append(QuerySegment(text=piece, kind="unknown"))
                continue
            entry = piece if piece in self.reverse else piece.casefold()
            kind = "element" if all(t in self.elements for t in tokens) else "qualifier"
            segments.append(
                QuerySegment(text=piece, kind=kind, entry=entry, tokens=tuple(tokens))
            )
        return QueryPlan(query=query, segments=tuple(segments))

    def unregistered_tokens(self, names: List[str]) -> Dict[str, List[str]]:
        """返回 ``{未登记词元: [来源术语名, ...]}``。"""
        missing: Dict[str, List[str]] = {}
        for name in names:
            for token in split_tokens(name):
                if not self.registered(token):
                    missing.setdefault(token, [])
                    if name not in missing[token]:
                        missing[token].append(name)
        return missing
