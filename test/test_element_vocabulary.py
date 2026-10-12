"""数据元 / 限定词模型的对账测试（GB/T 18391 · ISO/IEC 11179）。

守护三件事：
1. 词表完备——术语名分解出的每个词元都已登记（缺一个就让构建失败）；
2. 组合器可用——规范中文名可确定性生成，幂类型家族符合结构规则；
3. 对账——组合名必须复现别名层首选名，覆盖率设门限，**分歧必须是显式清单**。
"""
import importlib.util
import json
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).parent.parent
VOCAB_PATH = ROOT / "dm2-reference" / "dm2-element-vocabulary.yaml"
ALIAS_PATH = ROOT / "dm2-reference" / "dm2-term-zh-aliases.yaml"
TERMS_PATH = ROOT / "dm2-reference" / "core" / "terms.json"
BUILD_SCRIPT = ROOT / "scripts" / "build_knowledge_indexes.py"

from dm2.kernel.elements import ElementVocabulary  # noqa: E402

#: 有意保留的分歧：组合层按词元直译，别名层保留更符合中文习惯的措辞。
#: 任何**新增**分歧都会让对账测试失败——要么修词表，要么在此登记理由。
EXPECTED_DIVERGENCES = {
    "beforeAfter": "别名层把关系术语写作「前后关系」，组合层直译为「前后」",
    "couple": "别名层写作「耦合关系」，组合层直译为「耦合」",
    "overlap": "别名层写作「重叠关系」，组合层直译为「重叠」",
    "ruleConstrainsActivityPerformedByPerformer": "相对从句「由执行者执行的活动」超出组合语法的表达能力",
}

ENTITY_MIN_COVERAGE = 0.90
ASSOCIATION_MIN_COVERAGE = 0.90


@pytest.fixture(scope="module")
def vocab():
    return ElementVocabulary.load(VOCAB_PATH)


@pytest.fixture(scope="module")
def terms():
    return json.loads(TERMS_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def aliases():
    return yaml.safe_load(ALIAS_PATH.read_text(encoding="utf-8"))["aliases"]


@pytest.fixture(scope="module")
def builder():
    spec = importlib.util.spec_from_file_location("build_knowledge_indexes", BUILD_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["build_knowledge_indexes"] = module
    spec.loader.exec_module(module)
    return module


def _reconcile(vocab, terms, aliases, association):
    exact, diverged = 0, []
    for term in terms:
        if bool(term["association"]) != association:
            continue
        composed = vocab.compose(term["term"])
        curated = aliases.get(term["term"]) or []
        if composed is not None and curated and composed == curated[0]:
            exact += 1
        else:
            diverged.append((term["term"], composed, curated[0] if curated else ""))
    return exact, diverged


class TestVocabularyCompleteness:
    def test_every_token_is_registered(self, vocab, terms):
        missing = vocab.unregistered_tokens([term["term"] for term in terms])
        assert missing == {}, f"未登记词元（中文名无法组合）: {missing}"

    def test_token_count_matches_the_measured_vocabulary(self, vocab):
        # 279 个术语名分解出的唯一词元总数；新术语引入新词元时必须显式登记
        assert vocab.token_count == 131

    def test_elements_and_qualifiers_are_disjoint(self, vocab):
        assert not (set(vocab.elements) & set(vocab.qualifiers))

    def test_compound_parts_are_registered(self, vocab):
        for phrase in vocab.compounds:
            for part in phrase.split():
                assert vocab.registered(part), f"复合数据元 {phrase} 的词元 {part} 未登记"

    def test_every_template_has_registered_connectors(self, vocab):
        for template in vocab.templates:
            assert template.connectors, f"模板 {template.id} 缺 connectors"
            assert template.zh, f"模板 {template.id} 缺 zh"
            for connector in template.connectors:
                assert vocab.registered(connector), f"模板 {template.id} 的连接词 {connector} 未登记"


class TestComposition:
    def test_relation_term_uses_its_template(self, vocab):
        assert vocab.compose("activityPartOfCapability") == "活动属于能力"

    def test_multi_token_object_slot_composes_recursively(self, vocab):
        assert vocab.compose("activityPartOfProjectType") == "活动属于项目类型"

    def test_longest_connector_wins(self, vocab):
        # is realized by 必须胜过 by
        assert vocab.compose("desiredEffectIsRealizedByProjectType") == "期望效果由项目类型实现"

    @pytest.mark.parametrize("name,expected", [
        ("CountryType", "国家类型"),
        ("CountryTypeType", "国家类型的类型"),
        ("PerformerType", "执行者类型"),
        ("PerformerType", "执行者类型"),
        ("GeoPoliticalExtentTypeType", "地缘政治范围类型的类型"),
    ])
    def test_powertype_structure_rules(self, vocab, name, expected):
        assert vocab.compose(name) == expected

    def test_composition_is_repeatable(self, vocab):
        first = [vocab.compose(t) for t in ("Activity", "activityPartOfCapability", "CountryTypeType")]
        second = [vocab.compose(t) for t in ("Activity", "activityPartOfCapability", "CountryTypeType")]
        assert first == second

    def test_unknown_token_returns_none_instead_of_guessing(self, vocab):
        assert vocab.compose("ActivityZzzUnknown") is None

    def test_compound_element_beats_single_token_concatenation(self, vocab):
        assert vocab.compose("PlanarSurface") == "平面"
        assert vocab.compose("GeoPoliticalExtent") == "地缘政治范围"
        assert vocab.compose("RegionOfCountryType") == "国家内区域类型"


class TestReconciliation:
    def test_entity_coverage(self, vocab, terms, aliases):
        exact, diverged = _reconcile(vocab, terms, aliases, association=False)
        total = exact + len(diverged)
        assert exact / total >= ENTITY_MIN_COVERAGE, f"实体覆盖不足：{exact}/{total}，分歧 {diverged}"

    def test_association_coverage(self, vocab, terms, aliases):
        exact, diverged = _reconcile(vocab, terms, aliases, association=True)
        total = exact + len(diverged)
        assert exact / total >= ASSOCIATION_MIN_COVERAGE, f"关联覆盖不足：{exact}/{total}，分歧 {diverged}"

    def test_divergences_are_the_documented_set(self, vocab, terms, aliases):
        names = set()
        for association in (False, True):
            _, diverged = _reconcile(vocab, terms, aliases, association)
            names.update(name for name, _, _ in diverged)
        assert names == set(EXPECTED_DIVERGENCES), (
            f"未登记的组合分歧: {sorted(names - set(EXPECTED_DIVERGENCES))}；"
            f"已消失的分歧（请从清单删除）: {sorted(set(EXPECTED_DIVERGENCES) - names)}"
        )

    def test_alias_layer_still_covers_every_term(self, aliases, terms):
        missing = [term["term"] for term in terms if not aliases.get(term["term"])]
        assert missing == []


class TestBuildValidation:
    @staticmethod
    def _write(tmp_path, data):
        path = tmp_path / "vocab.yaml"
        path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
        return path

    def test_complete_vocabulary_passes(self, builder, tmp_path):
        path = self._write(tmp_path, {
            "elements": {"activity": "活动"},
            "qualifiers": {"type": "类型"},
            "templates": [{"id": "t", "connectors": ["type"], "zh": "{A}类型"}],
        })
        stats = builder.validate_element_vocabulary(path, ["ActivityType"])
        assert stats["elements"] == 1 and stats["templates"] == 1

    def test_unregistered_token_fails_the_build(self, builder, tmp_path):
        path = self._write(tmp_path, {"elements": {"activity": "活动"}, "qualifiers": {}})
        with pytest.raises(SystemExit):
            builder.validate_element_vocabulary(path, ["ActivityCapability"])

    def test_token_registered_twice_fails_the_build(self, builder, tmp_path):
        path = self._write(tmp_path, {
            "elements": {"type": "类型"},
            "qualifiers": {"type": "类型"},
        })
        with pytest.raises(SystemExit):
            builder.validate_element_vocabulary(path, ["Activity"])

    def test_template_with_unregistered_connector_fails_the_build(self, builder, tmp_path):
        path = self._write(tmp_path, {
            "elements": {"activity": "活动"},
            "qualifiers": {},
            "templates": [{"id": "t", "connectors": ["part"], "zh": "{A}属于{B}"}],
        })
        with pytest.raises(SystemExit):
            builder.validate_element_vocabulary(path, ["Activity"])

    def test_duplicate_template_id_fails_the_build(self, builder, tmp_path):
        path = self._write(tmp_path, {
            "elements": {"activity": "活动"},
            "qualifiers": {"type": "类型"},
            "templates": [
                {"id": "t", "connectors": ["type"], "zh": "{A}类型"},
                {"id": "t", "connectors": ["type"], "zh": "{A}类型"},
            ],
        })
        with pytest.raises(SystemExit):
            builder.validate_element_vocabulary(path, ["Activity"])

    def test_real_vocabulary_passes(self, builder, terms):
        stats = builder.validate_element_vocabulary(
            VOCAB_PATH, [term["term"] for term in terms]
        )
        assert stats["elements"] + stats["qualifiers"] == 131
