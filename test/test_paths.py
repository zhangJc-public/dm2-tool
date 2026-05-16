"""Tests for path utilities"""
import pytest
from dm2.utils.paths import get_project_root, is_dm2_project


class TestIsDm2Project:
    def test_detects_project_in_cwd(self, tmp_dm2_project_cwd):
        assert is_dm2_project() is True

    def test_detects_project_in_parent_dir(self, tmp_dm2_project_cwd):
        subdir = tmp_dm2_project_cwd / "sub1" / "sub2"
        subdir.mkdir(parents=True)
        assert is_dm2_project(str(subdir)) is True

    def test_returns_false_when_no_project(self, tmp_path):
        assert is_dm2_project(str(tmp_path)) is False

    def test_get_project_root_returns_same_as_is_dm2_project_base(self, tmp_dm2_project_cwd):
        root = get_project_root()
        assert (root / ".dm2" / "config.yaml").exists()
        assert is_dm2_project(str(root)) is True
