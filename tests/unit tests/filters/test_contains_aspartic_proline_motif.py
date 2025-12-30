"""
Tests for ContainsAsparticProlineMotifFilter.
"""

import pytest

from app.domain import PeptideDomain, ProteinDomain
from app.enums import AminoAcidEnum, CriteriaEnum
from app.services import ContainsAsparticProlineMotifFilter
from tests.factories import PeptideDomainFactory


@pytest.mark.unit
def test_contains_asp_pro_motif_filter_without_motif(
    good_universal_peptide: PeptideDomain,
    universal_protein: ProteinDomain,
) -> None:
    """Test that filter returns False when peptide doesn't contain an Aspartic-Proline motif."""
    # setup
    filter_instance = ContainsAsparticProlineMotifFilter()

    # execute
    result = filter_instance.evaluate(good_universal_peptide, universal_protein)

    # validate
    assert result is False


@pytest.mark.unit
def test_contains_asp_pro_motif_filter_with_motif(
    bad_universal_peptide1: PeptideDomain,
    universal_protein: ProteinDomain,
) -> None:
    """Test that filter returns True when peptide contains an Aspartic-Proline motif."""
    # setup
    filter_instance = ContainsAsparticProlineMotifFilter()

    # execute
    result = filter_instance.evaluate(bad_universal_peptide1, universal_protein)

    # validate
    assert result is True


@pytest.mark.unit
def test_contains_asp_pro_motif_filter_with_overlapping_motif(
    universal_protein: ProteinDomain,
) -> None:
    """Test that filter returns True when peptide contains an Aspartic-Proline motif with overlapping pattern."""
    # setup
    filter_instance = ContainsAsparticProlineMotifFilter()
    peptide = PeptideDomainFactory.build(
        sequence=AminoAcidEnum.to_amino_acids("QDDPR"),
    )

    # execute
    result = filter_instance.evaluate(peptide, universal_protein)

    # validate
    assert result is True


@pytest.mark.unit
def test_contains_asp_pro_motif_filter_returns_proper_enum() -> None:
    """Test that filter returns proper enum."""
    # setup
    filter_instance = ContainsAsparticProlineMotifFilter()

    # execute and validate
    assert filter_instance.criteria_enum == CriteriaEnum.CONTAINS_ASPARTIC_PROLINE_MOTIF
