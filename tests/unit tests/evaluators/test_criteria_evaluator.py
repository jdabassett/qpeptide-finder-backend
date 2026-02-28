"""
Unit tests for CriteriaEvaluator.
"""

from unittest.mock import MagicMock

import pytest

from app.domain import ProteinDomain
from app.enums import CriteriaEnum
from app.services import CriteriaEvaluator


@pytest.mark.unit
def test_evaluate_peptides_assigns_ranks(universal_protein: ProteinDomain) -> None:
    """Test that evaluate_peptides assigns ranks to all peptides."""
    evaluator = CriteriaEvaluator(CriteriaEvaluator._get_default_filters())

    evaluator.evaluate_peptides(universal_protein)

    assert len(universal_protein.peptides) > 0
    ranks = [p.rank for p in universal_protein.peptides]
    assert all(r is not None for r in ranks)
    assert all(isinstance(r, int) for r in ranks)
    int_ranks: list[int] = [r for r in ranks if r is not None]
    assert len(int_ranks) == len(ranks)
    assert sorted(int_ranks) == list(range(1, len(ranks) + 1))


@pytest.mark.unit
def test_evaluate_peptides_adds_criteria_to_peptides(
    universal_protein: ProteinDomain,
) -> None:
    """Test that evaluate_peptides adds criteria to peptides that pass filters."""
    evaluator = CriteriaEvaluator(CriteriaEvaluator._get_default_filters())

    evaluator.evaluate_peptides(universal_protein)

    criteria_counts = [len(p.criteria) for p in universal_protein.peptides]
    assert any(c > 0 for c in criteria_counts)


@pytest.mark.unit
def test_from_criteria_empty_list_yields_evaluator_with_no_filters() -> None:
    """Test that from_criteria([]) returns an evaluator with no filters."""
    evaluator = CriteriaEvaluator.from_criteria([])

    assert len(evaluator.filters) == 0


@pytest.mark.unit
def test_from_criteria_subset_yields_evaluator_with_matching_filters() -> None:
    """Test that from_criteria with one criterion returns an evaluator with one filter."""
    mock_criterion = MagicMock()
    mock_criterion.code = CriteriaEnum.NOT_UNIQUE

    evaluator = CriteriaEvaluator.from_criteria([mock_criterion])

    assert len(evaluator.filters) == 1
    assert evaluator.filters[0].criteria_enum == CriteriaEnum.NOT_UNIQUE
