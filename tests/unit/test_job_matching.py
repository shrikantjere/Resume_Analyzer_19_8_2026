"""Unit tests for the job matching logic."""

import pytest
from core.utils import jaccard_similarity


class TestJobMatching:
    """Test suite for job matching utilities."""

    def test_jaccard_perfect_match(self) -> None:
        skills = {"python", "sql", "docker", "aws", "git"}
        assert jaccard_similarity(skills, skills) == 1.0

    def test_jaccard_no_match(self) -> None:
        skills_a = {"python", "sql"}
        skills_b = {"java", "c++"}
        assert jaccard_similarity(skills_a, skills_b) == 0.0

    def test_jaccard_partial_match(self) -> None:
        resume = {"python", "sql", "docker", "aws"}
        required = {"python", "sql", "java", "kubernetes"}
        # Common: python, sql (2)
        # Union: python, sql, docker, aws, java, kubernetes (6)
        # similarity = 2/6 = 0.333
        sim = jaccard_similarity(resume, required)
        assert sim == pytest.approx(2 / 6, rel=0.01)

    def test_jaccard_subset(self) -> None:
        resume = {"python", "sql"}
        required = {"python", "sql", "java", "docker"}
        sim = jaccard_similarity(resume, required)
        assert sim == pytest.approx(2 / 4, rel=0.01)

    def test_fifty_percent_match(self) -> None:
        resume = {"a", "b", "c", "d"}
        required = {"a", "b", "e", "f"}
        # Common: a, b (2)
        # Union: a, b, c, d, e, f (6)
        sim = jaccard_similarity(resume, required)
        assert sim == pytest.approx(2 / 6, rel=0.01)