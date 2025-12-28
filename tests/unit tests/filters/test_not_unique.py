"""
Tests for NotUniqueFilter.
"""

import pytest

from app.domain import PeptideDomain, ProteinDomain
from app.services import NotUniqueFilter


@pytest.mark.unit
def test_not_unique_filter_on_unique_peptide(
    good_universal_peptide: PeptideDomain,
    universal_protein: ProteinDomain,
):
    """Test that filter returns True when peptide is unique."""
    # setup
    filter_instance = NotUniqueFilter()

    # execute
    result = filter_instance.evaluate(good_universal_peptide, universal_protein)

    # validate
    assert result is False


@pytest.mark.unit
def test_not_unique_filter_on_non_unique_peptide(
    bad_universal_peptide1: PeptideDomain,
    universal_protein: ProteinDomain,
):
    """Test that filter returns False when peptide is not unique."""
    # setup
    filter_instance = NotUniqueFilter()

    # execute
    result = filter_instance.evaluate(bad_universal_peptide1, universal_protein)

    # validate
    assert result is True
