"""
Tests for OutlierHydrophobicityFilter.
"""

import pytest

from app.domain import ProteinDomain
from app.enums import CriteriaEnum
from app.services import OutlierHydrophobicityFilter
from tests.factories.domains import PeptideDomainFactory


@pytest.mark.parametrize(
    "max_kd_score,expected",
    [
        (0.0, True),
        (0.5, True),
        (0.6, False),
        (1.0, False),
        (1.9, False),
        (2.0, True),
        (3.0, True),
    ],
)
@pytest.mark.unit
def test_outlier_hydrophobicity_filter(
    max_kd_score: float,
    expected: bool,
    universal_protein: ProteinDomain,
) -> None:
    """Test that filter returns expected with given max_kd_score."""
    # setup
    filter_instance = OutlierHydrophobicityFilter()
    peptide = PeptideDomainFactory.build(max_kd_score=max_kd_score)

    # execute
    result = filter_instance.evaluate(peptide, universal_protein)

    # validate
    assert result is expected


@pytest.mark.unit
def test_outlier_hydrophobicity_filter_returns_proper_enum() -> None:
    """Test that filter returns proper enum."""
    # setup
    filter_instance = OutlierHydrophobicityFilter()

    # execute and validate
    assert filter_instance.criteria_enum == CriteriaEnum.OUTLIER_HYDROPHOBICITY
