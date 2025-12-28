"""
Tests for ContainsMissedCleavagesFilter.
"""

import pytest

from app.domain import PeptideDomain, ProteinDomain
from app.services import ContainsMissedCleavagesFilter


@pytest.mark.unit
def test_contains_missed_cleavages_without_missed_cleavage(
    good_universal_peptide: PeptideDomain,
    universal_protein: ProteinDomain,
) -> None:
    """Test that filter returns False when peptide doesn't contains a missed cleavage site."""
    # setup
    filter_instance = ContainsMissedCleavagesFilter()

    # execute
    result = filter_instance.evaluate(good_universal_peptide, universal_protein)

    # validate
    assert result is False


@pytest.mark.unit
def test_no_missed_cleavage_filter_with_missed_cleavage(
    bad_universal_peptide1: PeptideDomain,
    universal_protein: ProteinDomain,
) -> None:
    """Test that filter returns True when peptide contains a missed cleavage site."""
    # setup
    filter_instance = ContainsMissedCleavagesFilter()

    # execute
    result = filter_instance.evaluate(bad_universal_peptide1, universal_protein)

    # validate
    assert result is True
