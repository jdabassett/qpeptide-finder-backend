"""
Tests for ContainsCysteineFilter.
"""

import pytest

from app.domain import PeptideDomain, ProteinDomain
from app.enums import CriteriaEnum
from app.services import ContainsCysteineFilter


@pytest.mark.unit
def test_contains_cysteine_filter_without_cysteine(
    good_universal_peptide: PeptideDomain,
    universal_protein: ProteinDomain,
) -> None:
    """Test that filter returns False when peptide doesn't contain cysteine."""
    # setup
    filter_instance = ContainsCysteineFilter()

    # execute
    result = filter_instance.evaluate(good_universal_peptide, universal_protein)

    # validate
    assert result is False


@pytest.mark.unit
def test_contains_cysteine_filter_with_cysteine(
    bad_universal_peptide1: PeptideDomain,
    universal_protein: ProteinDomain,
) -> None:
    """Test that filter returns True when peptide contains cysteine."""
    # setup
    filter_instance = ContainsCysteineFilter()

    # execute
    result = filter_instance.evaluate(bad_universal_peptide1, universal_protein)

    # validate
    assert result is True


@pytest.mark.unit
def test_contains_cysteine_filter_returns_proper_enum() -> None:
    """Test that filter returns proper enum."""
    # setup
    filter_instance = ContainsCysteineFilter()

    # execute and validate
    assert filter_instance.criteria_enum == CriteriaEnum.CONTAINS_CYSTEINE
