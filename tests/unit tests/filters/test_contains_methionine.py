"""
Tests for ContainsMethionineFilter.
"""

import pytest

from app.domain import PeptideDomain, ProteinDomain
from app.enums import CriteriaEnum
from app.services import ContainsMethionineFilter


@pytest.mark.unit
def test_contains_methionine_filter_without_methionine(
    good_universal_peptide: PeptideDomain,
    universal_protein: ProteinDomain,
) -> None:
    """Test that filter returns False when peptide doesn't contain methionine."""
    # setup
    filter_instance = ContainsMethionineFilter()

    # execute
    result = filter_instance.evaluate(good_universal_peptide, universal_protein)

    # validate
    assert result is False


@pytest.mark.unit
def test_contains_methionine_filter_with_methionine(
    bad_universal_peptide1: PeptideDomain,
    universal_protein: ProteinDomain,
) -> None:
    """Test that filter returns True when peptide contains methionine."""
    # setup
    filter_instance = ContainsMethionineFilter()

    # execute
    result = filter_instance.evaluate(bad_universal_peptide1, universal_protein)

    # validate
    assert result is True


@pytest.mark.unit
def test_contains_methionine_filter_returns_proper_enum() -> None:
    """Test that filter returns proper enum."""
    # setup
    filter_instance = ContainsMethionineFilter()

    # execute and validate
    assert filter_instance.criteria_enum == CriteriaEnum.CONTAINS_METHIONINE
