from typing import Any
from unittest.mock import Mock

import pytest

from app.enums import AminoAcidEnum
from tests.factories.domains import PeptideDomainFactory


@pytest.mark.unit
def test_peptide_domain_length_property() -> None:
    """Test that length property returns correct sequence length."""
    # setup
    peptide = PeptideDomainFactory.build()

    # execute
    result = peptide.length

    # validate
    assert result == len(peptide.sequence)


@pytest.mark.unit
def test_peptide_domain_sequence_as_str_property() -> None:
    """Test that sequence_as_str property converts sequence to string."""
    # setup
    peptide = PeptideDomainFactory.build()

    # execute
    result = peptide.sequence_as_str

    # validate
    assert result == "".join([aa.value for aa in peptide.sequence])


@pytest.mark.unit
def test_peptide_domain_get_pi_returns_cached_value(monkeypatch: Any) -> None:
    """Test that get_pI returns cached value if already set."""
    # setup
    cached_pi = 6.5
    peptide = PeptideDomainFactory.build(pI=cached_pi)

    mock_calculate_pi = Mock()
    monkeypatch.setattr(
        "app.domain.peptide.PeptideDomain.calculate_pI", mock_calculate_pi
    )

    # execute
    result = peptide.get_pI()

    # validate
    assert result == cached_pi
    assert peptide.pI == cached_pi
    mock_calculate_pi.assert_not_called()


@pytest.mark.unit
def test_peptide_domain_get_pi_calls_calculate_pi_when_not_cached(
    monkeypatch: Any,
) -> None:
    """Test that get_pI calls calculate_pI when pI is not cached."""
    # setup
    peptide = PeptideDomainFactory.build(pI=None)

    calculated_pI: float = 1.0
    mock_calculate_pi = Mock(return_value=calculated_pI)
    monkeypatch.setattr(
        "app.domain.peptide.PeptideDomain.calculate_pI", mock_calculate_pi
    )

    # execute
    result = peptide.get_pI()

    # validate
    assert result == calculated_pI
    assert peptide.pI == calculated_pI
    mock_calculate_pi.assert_called_once()


@pytest.mark.parametrize(
    "sequence,expected_pI",
    [
        ("ADSGEGDFLAEGGGVR", 3.6),  # Fibrinopeptide A (human) — acidic 3.9pI
        ("RELEELNVPGEIVESLSSSEESITR", 3.8),  # β-Casein (1–28) fragment — acidic 4.1pI
        ("DRVYIHPFHL", 7.2),  # Angiotensin I — near-neutral 7.1pI
        ("RPKPQQFFGLM", 11.3),  # Substance P — slightly basic neuropeptide 10.7pI
        ("RPPGFSPFR", 12.4),  # Bradykinin — strongly basic peptide 11.5pI
    ],
)
@pytest.mark.unit
def test_peptide_domain_calculate_pi(sequence: str, expected_pI: float) -> None:
    """Test that calculate_pI estimates isoelectric point."""
    # setup
    sequence_aa = AminoAcidEnum.to_amino_acids(sequence=sequence)
    peptide = PeptideDomainFactory.build(sequence=sequence_aa, pI=None)

    # execute
    result = peptide.calculate_pI()

    # validate
    assert result is not None
    assert isinstance(result, float)
    assert result == pytest.approx(expected_pI, abs=0.1)
    assert peptide.pI == pytest.approx(expected_pI, abs=0.1)


@pytest.mark.parametrize(
    "sequence,expected_charge_state",
    [
        ("ADSGEGDFLAEGGGVR", 2),  # Fibrinopeptide A (human) — acidic
        ("RELEELNVPGEIVESLSSSEESITR", 3),  # β-Casein (1–28) fragment — acidic
        ("DRVYIHPFHL", 4),  # Angiotensin I — near-neutral 7.1pI
        ("RPKPQQFFGLM", 3),  # Substance P — slightly basic neuropeptide
        ("RPPGFSPFR", 3),  # Bradykinin — strongly basic peptide
    ],
)
@pytest.mark.unit
def test_peptide_domain_charge_state_in_formic_acid(
    sequence: str, expected_charge_state: int
) -> None:
    """Test that charge_state_in_formic_acid calculates charge at pH 2.3."""
    # setup
    sequence_aa = AminoAcidEnum.to_amino_acids(sequence)
    peptide = PeptideDomainFactory.build(sequence=sequence_aa, charge_state=None)

    # execute
    result = peptide.charge_state_in_formic_acid()

    # validate
    assert result is not None
    assert isinstance(result, int)
    assert peptide.charge_state == expected_charge_state
    assert result == expected_charge_state


@pytest.mark.parametrize(
    "sequence,expected_score",
    [
        ("ADSGEGDFLAEGGGVR", 0.50),  # Fibrinopeptide A (human) — acidic
        ("RELEELNVPGEIVESLSSSEESITR", 0.77),  # β-Casein (1–28) fragment — acidic
        ("DRVYIHPFHL", 0.17),  # Angiotensin I — near-neutral 7.1pI
        ("RPKPQQFFGLM", -0.18),  # Substance P — slightly basic neuropeptide
        ("RPPGFSPFR", -1.05),  # Bradykinin — strongly basic peptide
        ("YGGFL", 0.9),  # Leucine enkephalin fragment — moderate hydrophobicity
        ("GIGAVLKVLTTGLPALIS", 2.00),  # Melittin hydrophobic core — amphipathic
        ("LALLLLLLL", 3.58),  # Poly-Leu transmembrane-like stretch — very hydrophobic
        ("AAVALLPAVLLALL", 2.84),  # Signal peptide–like hydrophobic region
    ],
)
@pytest.mark.unit
def test_peptide_domain_max_kyte_dolittle_score_over_sliding_window(
    sequence: str, expected_score: float
) -> None:
    """Test that max_kyte_dolittle_score_over_sliding_window calculates max KD score."""
    # setup
    sequence_aa = AminoAcidEnum.to_amino_acids(sequence)
    peptide = PeptideDomainFactory.build(sequence=sequence_aa, max_kd_score=None)

    # execute
    result = peptide.max_kyte_dolittle_score_over_sliding_window()

    # validate
    assert result is not None
    assert isinstance(result, float)
    assert peptide.max_kd_score == pytest.approx(expected_score, abs=0.1)
    assert result == pytest.approx(expected_score, abs=0.1)
