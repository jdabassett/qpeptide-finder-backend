"""
Tests for HasFlankingCutSitesFilter.
"""

import pytest

from app.domain import PeptideDomain, ProteinDomain
from app.enums import AminoAcidEnum, CriteriaEnum
from app.services import HasFlankingCutSitesFilter
from tests.factories import ProteinDomainFactory


@pytest.mark.unit
def test_has_flanking_cut_sites_filter_without_flanking_cut_sites(
    good_universal_peptide: PeptideDomain,
    universal_protein: ProteinDomain,
) -> None:
    """Test that filter returns False when peptide has no cut sites in flanking regions."""
    # setup
    filter_instance = HasFlankingCutSitesFilter()

    # execute
    result = filter_instance.evaluate(good_universal_peptide, universal_protein)

    # validate
    assert result is False


@pytest.mark.unit
def test_has_flanking_cut_sites_filter_with_flanking_cut_sites_left() -> None:
    """Test that filter returns True when peptide has cut sites in flanking regions."""
    # setup
    filter_instance = HasFlankingCutSitesFilter()

    protein = ProteinDomainFactory.build(
        sequence=AminoAcidEnum.to_amino_acids("AAARAAAKAAAAAAKAAAAAA"),
    )
    protein.digest_sequence()

    # execute
    result = filter_instance.evaluate(protein.peptides[2], protein)

    # validate
    assert result is True


@pytest.mark.unit
def test_has_flanking_cut_sites_filter_with_missed_cleavage_left() -> None:
    """Test that filter returns True when peptide has cut sites in flanking regions."""
    # setup
    filter_instance = HasFlankingCutSitesFilter()

    protein = ProteinDomainFactory.build(
        sequence=AminoAcidEnum.to_amino_acids("AAARPAAAKAAAAAAKAAAAAA"),
    )
    protein.digest_sequence()

    # execute
    result = filter_instance.evaluate(protein.peptides[1], protein)

    # validate
    assert result is True


@pytest.mark.unit
def test_has_flanking_cut_sites_filter_with_flanking_cut_sites_right() -> None:
    """Test that filter returns True when peptide has cut sites in flanking regions."""
    # setup
    filter_instance = HasFlankingCutSitesFilter()

    protein = ProteinDomainFactory.build(
        sequence=AminoAcidEnum.to_amino_acids("AAAAAAKAAAAAAKAAAKAAA"),
    )
    protein.digest_sequence()

    # execute
    result = filter_instance.evaluate(protein.peptides[1], protein)

    # validate
    assert result is True


@pytest.mark.unit
def test_has_flanking_cut_sites_filter_with_missed_cleavage_right() -> None:
    """Test that filter returns True when peptide has cut sites in flanking regions."""
    # setup
    filter_instance = HasFlankingCutSitesFilter()

    protein = ProteinDomainFactory.build(
        sequence=AminoAcidEnum.to_amino_acids("AAAAAAKAAAAAAKAAAKPAAA"),
    )
    protein.digest_sequence()

    # execute
    result = filter_instance.evaluate(protein.peptides[1], protein)

    # validate
    assert result is True


@pytest.mark.unit
def test_has_flanking_cut_sites_filter_returns_proper_enum() -> None:
    """Test that filter returns proper enum."""
    # setup
    filter_instance = HasFlankingCutSitesFilter()

    # execute and validate
    assert filter_instance.criteria_enum == CriteriaEnum.HAS_FLANKING_CUT_SITES
