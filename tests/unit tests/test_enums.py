"""
Tests for enum classes.
"""

import pytest

from app.enums import AminoAcidEnum, ProteaseEnum
from app.enums.enums import CleavageStatusEnum


@pytest.mark.parametrize(
    "site,expected",
    [
        (7, CleavageStatusEnum.CLEAVAGE),
        (6, CleavageStatusEnum.NEUTRAL),
        (1, CleavageStatusEnum.MISSED),
    ],
)
@pytest.mark.unit
def test_site_status_at_successful(
    site: int,
    expected: CleavageStatusEnum,
) -> None:
    """Test that protease would cut after provided site."""
    # setup
    protease: ProteaseEnum = ProteaseEnum.TRYPSIN
    sequence: list[AminoAcidEnum] = AminoAcidEnum.to_amino_acids("MKPKYIAKQRQ")
    # execute and validate
    assert protease.site_status(sequence, site) is expected
