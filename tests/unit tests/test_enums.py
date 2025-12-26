"""
Tests for enum classes.
"""

import pytest

from app.enums import ProteaseEnum
from app.enums.enums import CleavageStatusEnum


@pytest.mark.parametrize(
    "protease,sequence,site,expected",
    [
        (ProteaseEnum.TRYPSIN, "MKPAYIAKQRQ", 7, CleavageStatusEnum.CLEAVAGE),
        (ProteaseEnum.TRYPSIN, "MKPAYIAKQRQ", 6, CleavageStatusEnum.NEUTRAL),
        (ProteaseEnum.TRYPSIN, "MKPAYIAKQRQ", 1, CleavageStatusEnum.MISSED),
    ],
)
@pytest.mark.unit
def test_site_status_at_successful(
    protease: ProteaseEnum, sequence: str, site: int, expected: CleavageStatusEnum
) -> None:
    """Test that protease would cut after provided site."""
    assert protease.site_status(sequence, site) is expected
