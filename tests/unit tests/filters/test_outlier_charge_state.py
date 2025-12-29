"""
Tests for OutlierChargeStateFilter.
"""

import pytest

from app.domain import ProteinDomain
from app.enums import CriteriaEnum
from app.services import OutlierChargeStateFilter
from tests.factories import PeptideDomainFactory


@pytest.mark.parametrize(
    "charge_state,expected",
    [
        (0, True),
        (1, True),
        (2, False),
        (3, False),
        (4, True),
        (5, True),
    ],
)
@pytest.mark.unit
def test_outlier_charge_state_filter(
    charge_state: int,
    expected: bool,
    universal_protein: ProteinDomain,
) -> None:
    """Test that filter returns expected with given charge state."""
    # setup
    filter_instance = OutlierChargeStateFilter()
    peptide = PeptideDomainFactory.build(charge_state=charge_state)

    # execute
    result = filter_instance.evaluate(peptide, universal_protein)

    # validate
    assert result is expected


@pytest.mark.unit
def test_outlier_charge_state_filter_returns_proper_enum() -> None:
    """Test that filter returns proper enum."""
    # setup
    filter_instance = OutlierChargeStateFilter()

    # execute and validate
    assert filter_instance.criteria_enum == CriteriaEnum.OUTLIER_CHARGE_STATE
