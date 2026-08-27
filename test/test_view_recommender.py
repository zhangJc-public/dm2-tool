"""Tests for ViewRecommender.verify_and_supplement_views — dependency-complete recommendations.

Covers the wiring contract behind `dm2 analyze`: recommended view sets must include the
transitive dependency ancestors declared in views.yaml (e.g. OV-2/OV-5a require OV-1,
which in turn requires CV-1/AV-1).
"""
import json
import subprocess
import sys

import pytest

from dm2.cognitive.view_recommender import ViewRecommendation, ViewRecommender
from dm2.kernel.indexer import DM2KnowledgeIndexer


@pytest.fixture(scope="module")
def recommender():
    indexer = DM2KnowledgeIndexer()
    indexer.load_all()
    return ViewRecommender(indexer)


def _make_rec(recommender, view_id, score=0.8):
    """Build a data-group-activated recommendation for a view."""
    tmpl = recommender.indexer.get_view_template(view_id)
    assert tmpl is not None, f"missing template for {view_id}"
    return ViewRecommendation(
        view_id=view_id,
        view_name=tmpl.view_name,
        viewpoint=tmpl.viewpoint,
        relevance_score=score,
        reason=f"测试激活 - {view_id}",
        priority=tmpl.priority,
        dm2_groups=tmpl.dm2_groups,
    )


class TestVerifyAndSupplementViews:
    def test_supplements_transitive_ancestors(self, recommender):
        """Set with OV-2/OV-5a but not OV-1 gains OV-1 (+CV-1/AV-1 and full closure)."""
        recs = [_make_rec(recommender, "OV-2"), _make_rec(recommender, "OV-5a")]
        out = recommender.verify_and_supplement_views(recs, None)
        ids = {r.view_id for r in out}

        # The pictorial communication baseline and its ancestors are restored
        assert "OV-1" in ids
        assert "CV-1" in ids
        assert "AV-1" in ids
        # Full transitive closure over views.yaml dependencies
        assert ids == {
            "OV-2", "OV-5a",        # originals
            "OV-1", "OV-4", "OV-5b",  # OV-2/OV-5a direct deps
            "CV-1", "AV-1", "AV-2",   # OV-1/AV-1 transitive deps
        }

    def test_supplemented_views_carry_marker_reason(self, recommender):
        recs = [_make_rec(recommender, "OV-2")]
        out = recommender.verify_and_supplement_views(recs, None)
        supplemented = [r for r in out if "路径完整性补充" in r.reason]
        assert {r.view_id for r in supplemented} >= {"OV-1", "CV-1", "AV-1"}
        for r in supplemented:
            assert r.relevance_score == 0.6

    def test_dedup_no_duplicate_view_ids(self, recommender):
        recs = [
            _make_rec(recommender, "OV-2", 0.9),
            _make_rec(recommender, "OV-5a", 0.3),
            _make_rec(recommender, "OV-2", 0.5),  # duplicate id
        ]
        out = recommender.verify_and_supplement_views(recs, None)
        ids = [r.view_id for r in out]
        assert len(ids) == len(set(ids))
        # first occurrence (higher score) is kept on dedup
        ov2 = next(r for r in out if r.view_id == "OV-2")
        assert ov2.relevance_score == 0.9

    def test_sorted_by_priority_then_score(self, recommender):
        recs = [_make_rec(recommender, "OV-2", 0.9), _make_rec(recommender, "OV-5a", 0.3)]
        out = recommender.verify_and_supplement_views(recs, None)
        keys = [(r.priority, -r.relevance_score) for r in out]
        assert keys == sorted(keys)

    def test_idempotent_when_ancestor_chain_complete(self, recommender):
        full = ["OV-2", "OV-5a", "OV-1", "OV-4", "OV-5b", "CV-1", "AV-1", "AV-2"]
        recs = [_make_rec(recommender, v) for v in full]
        out = recommender.verify_and_supplement_views(recs, None)
        assert {r.view_id for r in out} == set(full)
        assert all("路径完整性补充" not in r.reason for r in out)


class TestAnalyzeCliSmoke:
    """`dm2 analyze` SHALL emit dependency-complete recommended_views."""

    def test_analyze_recommends_ov1_with_reason(self):
        proc = subprocess.run(
            [
                sys.executable, "-m", "dm2.cli.main", "analyze",
                "-d", "作战节点连接、活动分解、资源流",
                "--json",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(proc.stdout)["data"]
        recommended = data["recommended_views"]
        ids = [r["view_id"] for r in recommended]

        # OV-1 (transitive ancestor of OV-2/OV-5a) is present after supplement
        assert "OV-1" in ids
        # reason field is emitted for agent consumption and carries the marker when supplemented
        assert all("reason" in r for r in recommended)
        candidates = data["candidate_views"]
        assert any("路径完整性补充" in r["reason"] for r in candidates)
