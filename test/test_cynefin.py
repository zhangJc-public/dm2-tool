"""Tests for the redesigned Cynefin analyzer: domain resolution and confidence."""
import pytest

from dm2.cognitive.cynefin_analyzer import (
    DIMENSION_IDS,
    CynefinAnalyzer,
    DimensionVote,
    Domain,
    ScaleProfile,
    Tendency,
)


def _vote(dim_id, tendency=None, source="derived", evidence=None):
    if tendency is None:
        ev = evidence or []
    elif evidence is not None:
        ev = evidence
    elif source == "user":
        ev = ["用户显式指定"]
    else:
        ev = ["文本证据"]
    return DimensionVote(dim_id, Tendency(tendency) if tendency else None,
                         evidence=ev, source=source)


def _all(tendency, source="derived"):
    return [_vote(d, tendency, source=source) for d in DIMENSION_IDS]


@pytest.fixture(scope="module")
def analyzer():
    return CynefinAnalyzer()


class TestDomainResolution:
    def test_all_clear_resolves_clear(self, analyzer):
        assert analyzer.assess(_all("clear")).domain == Domain.CLEAR

    def test_all_complex_hard_triggers_complex(self, analyzer):
        """Regression against the old 1-3 scale / 3.5 threshold dead zone."""
        result = analyzer.assess(_all("complex"))
        assert result.domain == Domain.COMPLEX

    def test_two_complex_three_complicated_is_complicated(self, analyzer):
        votes = [_vote(d, "complex" if i < 2 else "complicated")
                 for i, d in enumerate(DIMENSION_IDS)]
        # avg = (3+3+2+2+2)/5 = 2.4 → band Complicated; hard trigger not reached
        assert analyzer.assess(votes).domain == Domain.COMPLICATED

    def test_three_complex_hard_trigger_regardless_of_band(self, analyzer):
        votes = [_vote(d, "complex" if i < 3 else "clear")
                 for i, d in enumerate(DIMENSION_IDS)]
        # band avg would be 2.2 (Complicated), but 3 complex votes trigger Complex
        assert analyzer.assess(votes).domain == Domain.COMPLEX

    def test_crisis_veto_forces_chaotic(self, analyzer):
        result = analyzer.assess(_all("clear"), crisis=True)
        assert result.domain == Domain.CHAOTIC
        assert result.depth_tier == "full"

    def test_no_votes_is_disorder(self, analyzer):
        result = analyzer.assess([_vote(d) for d in DIMENSION_IDS])
        assert result.domain == Domain.DISORDER
        assert result.needs_clarification is True
        assert result.depth_tier == "none"

    def test_sparse_conflicting_votes_is_disorder(self, analyzer):
        # 2 informed dims, one clear one complex → cross-domain split, <3 informed
        votes = [_vote(DIMENSION_IDS[0], "clear"), _vote(DIMENSION_IDS[1], "complex")]
        votes += [_vote(d) for d in DIMENSION_IDS[2:]]
        assert analyzer.assess(votes).domain == Domain.DISORDER

    def test_sparse_agreement_resolves_normally(self, analyzer):
        # 2 informed, both clear → no cross-domain split → band resolves Clear
        votes = [_vote(DIMENSION_IDS[0], "clear"), _vote(DIMENSION_IDS[1], "clear")]
        votes += [_vote(d) for d in DIMENSION_IDS[2:]]
        assert analyzer.assess(votes).domain == Domain.CLEAR

    def test_explicit_user_values_count_as_evidence(self, analyzer):
        # 5 user-supplied values incl. clear+complex split must NOT be Disorder
        votes = [_vote(d, "complex" if i == 0 else "complicated", source="user")
                 for i, d in enumerate(DIMENSION_IDS)]
        result = analyzer.assess(votes)
        assert result.domain != Domain.DISORDER

    def test_abstentions_excluded_from_band(self, analyzer):
        # 3 complicated votes, 2 abstentions → avg 2.0 → Complicated
        votes = [_vote(d, "complicated" if i < 3 else None)
                 for i, d in enumerate(DIMENSION_IDS)]
        assert analyzer.assess(votes).domain == Domain.COMPLICATED


class TestConfidence:
    def test_full_evidence_uniform_reaches_high_confidence(self, analyzer):
        result = analyzer.assess(_all("clear"))
        assert result.confidence >= 0.85
        assert result.confidence == 0.95

    def test_no_evidence_cannot_reach_top_confidence(self, analyzer):
        result = analyzer.assess([_vote(d) for d in DIMENSION_IDS])
        assert result.confidence <= 0.40
        assert result.confidence == 0.20

    def test_confidence_varies_with_agreement(self, analyzer):
        uniform = analyzer.assess(_all("clear")).confidence
        mixed_votes = [_vote(d, "clear" if i < 3 else "complex")
                       for i, d in enumerate(DIMENSION_IDS)]
        mixed = analyzer.assess(mixed_votes).confidence
        assert uniform > mixed

    def test_confidence_breakdown_exposed(self, analyzer):
        result = analyzer.assess(_all("clear"))
        breakdown = result.confidence_breakdown
        assert breakdown["coverage"] == 1.0
        assert breakdown["agreement"] == 1.0
        assert breakdown["informed_dimensions"] == 5


class TestScaleProfile:
    def test_scale_does_not_move_domain(self, analyzer):
        votes = _all("complicated")
        small = analyzer.assess(votes, scale=ScaleProfile(systems=2, stakeholders=2))
        large = analyzer.assess(votes, scale=ScaleProfile(systems=20, stakeholders=50))
        assert small.domain == large.domain == Domain.COMPLICATED
        assert small.confidence == large.confidence

    def test_scale_profile_serialized(self, analyzer):
        result = analyzer.assess(
            _all("clear"), scale=ScaleProfile(systems=8, time_span="long", stakeholders=5)
        )
        payload = result.to_dict()
        assert payload["scale_profile"] == {
            "systems": 8, "time_span": "long", "stakeholders": 5
        }


class TestContract:
    def test_every_domain_has_depth_tier(self, analyzer):
        cases = {
            Domain.CLEAR: ("minimal", _all("clear")),
            Domain.COMPLICATED: ("core", _all("complicated")),
            Domain.CHAOTIC: ("full", _all("clear")),
            Domain.DISORDER: ("none", [_vote(d) for d in DIMENSION_IDS]),
        }
        for domain, (tier, votes) in cases.items():
            result = analyzer.assess(votes, crisis=(domain == Domain.CHAOTIC))
            assert result.domain == domain
            assert result.depth_tier == tier
            assert result.depth_guidance

    def test_to_dict_contains_full_contract(self, analyzer):
        result = analyzer.assess(_all("clear"))
        payload = result.to_dict()
        for key in ("domain", "domain_label", "confidence", "confidence_breakdown",
                    "crisis", "needs_clarification", "depth_tier", "depth_guidance",
                    "dimensions", "scale_profile", "reasoning"):
            assert key in payload
        dim = payload["dimensions"][0]
        assert set(dim) == {"id", "tendency", "evidence", "source"}

    def test_unknown_dimension_rejected(self):
        with pytest.raises(ValueError):
            CynefinAnalyzer(weights={"nope": 1.0})
        with pytest.raises(ValueError):
            CynefinAnalyzer().assess([DimensionVote("nope", Tendency.CLEAR)])
