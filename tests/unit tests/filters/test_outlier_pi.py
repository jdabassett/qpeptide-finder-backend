"""
Tests for OutlierPIFilter.
"""

import pytest

from app.domain import ProteinDomain
from app.enums import CriteriaEnum
from app.services import OutlierPIFilter
from tests.factories.domains import PeptideDomainFactory


@pytest.mark.parametrize(
    "pi,expected",
    [
        (3.9, True),
        (4.0, False),
        (9.0, False),
        (9.1, True),
    ],
)
@pytest.mark.unit
def test_outlier_pi_filter(
    pi: float,
    expected: bool,
    universal_protein: ProteinDomain,
) -> None:
    """Test that filter returns expected with given pI value."""
    # setup
    filter_instance = OutlierPIFilter()
    peptide = PeptideDomainFactory.build(pI=pi)

    # execute
    result = filter_instance.evaluate(peptide, universal_protein)

    # validate
    assert result is expected


@pytest.mark.unit
def test_outlier_pi_filter_returns_proper_enum() -> None:
    """Test that filter returns proper enum."""
    # setup
    filter_instance = OutlierPIFilter()

    # execute and validate
    assert filter_instance.criteria_enum == CriteriaEnum.OUTLIER_PI
