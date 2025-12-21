"""
Tests for enum classes.
"""

import pytest

from app.enums import ProteaseEnum


@pytest.mark.parametrize(
    "protease,sequence,site,expected",
    [
        (ProteaseEnum.TRYPSIN, "MKTAYIAKQRQ", 7, True),
        (ProteaseEnum.TRYPSIN, "MKTAYIAKQRQ", 6, False),
    ],
)
@pytest.mark.unit
def test_would_cut_at_successful(
    protease: ProteaseEnum, sequence: str, site: int, expected: bool
) -> None:
    """Test that protease would cut after provided site."""
    assert protease.would_cut_at(sequence, site) is expected
