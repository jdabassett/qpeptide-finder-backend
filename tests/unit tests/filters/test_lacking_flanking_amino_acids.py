"""
Tests for LackingFlankingAminoAcidsFilter.
"""

import pytest

from app.domain import PeptideDomain, ProteinDomain
from app.enums import AminoAcidEnum, CriteriaEnum
from app.services import LackingFlankingAminoAcidsFilter
from tests.factories.domains import PeptideDomainFactory, ProteinDomainFactory


@pytest.mark.unit
def test_lacking_flanking_amino_acids_filter_with_sufficient_flanking(
    good_universal_peptide: PeptideDomain,
    universal_protein: ProteinDomain,
) -> None:
    """Test that filter returns False when peptide has sufficient flanking amino acids."""
    # setup
    filter_instance = LackingFlankingAminoAcidsFilter()

    # execute
    result = filter_instance.evaluate(good_universal_peptide, universal_protein)

    # validate
    assert result is False


@pytest.mark.unit
def test_lacking_flanking_amino_acids_filter_lacking_left_flanking() -> None:
    """Test that filter returns True when peptide lacks left flanking amino acids."""
    # setup
    filter_instance = LackingFlankingAminoAcidsFilter()

    protein = ProteinDomainFactory.build(
        sequence=AminoAcidEnum.to_amino_acids("AEDIHYK" + "A" * 20),
    )
    peptide = PeptideDomainFactory.build(
        position=1,
        sequence=AminoAcidEnum.to_amino_acids("AEDIHYK"),
    )

    # execute
    result = filter_instance.evaluate(peptide, protein)

    # validate
    assert result is True


@pytest.mark.unit
def test_lacking_flanking_amino_acids_filter_lacking_right_flanking() -> None:
    """Test that filter returns True when peptide lacks right flanking amino acids."""
    # setup
    filter_instance = LackingFlankingAminoAcidsFilter()

    protein = ProteinDomainFactory.build(
        sequence=AminoAcidEnum.to_amino_acids("A" * 20 + "AEDIHYK"),
    )
    peptide = PeptideDomainFactory.build(
        position=21,
        sequence=AminoAcidEnum.to_amino_acids("AEDIHYK"),
    )

    # execute
    result = filter_instance.evaluate(peptide, protein)

    # validate
    assert result is True


@pytest.mark.unit
def test_lacking_flanking_amino_acids_filter_with_exact_minimum_flanking() -> None:
    """Test that filter returns False when peptide has exactly 6 amino acids on each side."""
    # setup
    filter_instance = LackingFlankingAminoAcidsFilter()

    protein = ProteinDomainFactory.build(
        sequence=AminoAcidEnum.to_amino_acids("AAAAAA" + "AEDIHYK" + "AAAAAA"),
    )
    peptide = PeptideDomainFactory.build(
        position=7,
        sequence=AminoAcidEnum.to_amino_acids("AEDIHYK"),
    )

    # execute
    result = filter_instance.evaluate(peptide, protein)

    # validate
    assert result is False


@pytest.mark.unit
def test_lacking_flanking_amino_acids_filter_returns_proper_enum() -> None:
    """Test that filter returns proper enum."""
    # setup
    filter_instance = LackingFlankingAminoAcidsFilter()

    # execute and validate
    assert filter_instance.criteria_enum == CriteriaEnum.LACKING_FLANKING_AMINO_ACIDS
