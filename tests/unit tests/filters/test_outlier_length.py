"""
Tests for OutlierLengthFilter.
"""

import pytest

from app.domain import ProteinDomain
from app.enums import AminoAcidEnum, CriteriaEnum
from app.services import OutlierLengthFilter
from tests.factories import PeptideDomainFactory


@pytest.mark.parametrize(
    "length,expected",
    [
        (6, True),
        (7, False),
        (30, False),
        (31, True),
    ],
)
@pytest.mark.unit
def test_outlier_length_filter(
    length: int,
    expected: bool,
    universal_protein: ProteinDomain,
) -> None:
    """Test that filter returns expected with given peptide length."""
    # setup
    filter_instance = OutlierLengthFilter()

    sequence = [AminoAcidEnum.ALANINE] * length
    peptide = PeptideDomainFactory.build(sequence=sequence)

    # execute
    result = filter_instance.evaluate(peptide, universal_protein)

    # validate
    assert result is expected


@pytest.mark.unit
def test_outlier_length_filter_returns_proper_enum() -> None:
    """Test that filter returns proper enum."""
    # setup
    filter_instance = OutlierLengthFilter()

    # execute and validate
    assert filter_instance.criteria_enum == CriteriaEnum.OUTLIER_LENGTH
