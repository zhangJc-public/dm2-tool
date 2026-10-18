"""Invariants of the view-format taxonomy.

`representation` (what a view conveys) and `format` (how it is carried) are
independent axes; the relation between them is a compatibility matrix, not a
mapping. These tests pin the matrix's internal consistency and its coverage of
the representations the reference corpus actually uses.
"""
import yaml

from dm2.kernel.formats import (
    COMPATIBLE_FORMATS,
    DEFAULT_FORMAT,
    EXTERNAL,
    LOSSY,
    NATIVE,
    compatible_formats,
    default_format,
    is_compatible,
)
from dm2.utils.paths import get_reference_path


def _reference_representations() -> set[str]:
    data = yaml.safe_load(
        (get_reference_path() / "views.yaml").read_text(encoding="utf-8")
    )
    views = data["views"] if isinstance(data, dict) and "views" in data else data
    return {v["representation"] for v in views if v.get("representation")}


class TestMatrixConsistency:
    def test_every_representation_has_a_default(self):
        assert set(COMPATIBLE_FORMATS) == set(DEFAULT_FORMAT)

    def test_every_default_is_compatible(self):
        for representation, fmt in DEFAULT_FORMAT.items():
            assert is_compatible(representation, fmt), f"{representation}/{fmt}"

    def test_every_default_is_native(self):
        for representation, fmt in DEFAULT_FORMAT.items():
            assert COMPATIBLE_FORMATS[representation][fmt] == NATIVE

    def test_matrix_covers_the_reference_corpus(self):
        unknown = _reference_representations() - set(COMPATIBLE_FORMATS)
        assert not unknown, f"representations without a format entry: {sorted(unknown)}"


class TestCarrierSemantics:
    def test_pictorial_defaults_to_svg(self):
        assert default_format("pictorial") == "svg"

    def test_pictorial_accepts_video(self):
        """Video is a carrier, not a representation — this is where it belongs."""
        assert is_compatible("pictorial", "mp4")

    def test_table_rejects_mermaid(self):
        assert not is_compatible("table", "mermaid")

    def test_diagram_views_reject_markdown(self):
        assert not is_compatible("state-diagram", "markdown")

    def test_tabular_external_formats_are_external(self):
        assert COMPATIBLE_FORMATS["table"]["xlsx"] == EXTERNAL
        assert COMPATIBLE_FORMATS["pictorial"]["mp4"] == EXTERNAL

    def test_pictorial_mermaid_is_lossy(self):
        assert COMPATIBLE_FORMATS["pictorial"]["mermaid"] == LOSSY

    def test_unknown_representation_has_no_formats(self):
        assert compatible_formats("not-a-representation") == set()

    def test_unknown_representation_falls_back_to_markdown(self):
        assert default_format("not-a-representation") == "markdown"
