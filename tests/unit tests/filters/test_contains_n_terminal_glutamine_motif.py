"""
Tests for ContainsNTerminalGlutamineMotifFilter.
"""

import pytest

from app.domain import PeptideDomain, ProteinDomain
from app.enums import CriteriaEnum
from app.services import ContainsNTerminalGlutamineMotifFilter


@pytest.mark.unit
def test_contains_n_terminal_glutamine_filter_without_n_terminal_glutamine(
    good_universal_peptide: PeptideDomain,
    universal_protein: ProteinDomain,
) -> None:
    """Test that filter returns False when peptide doesn't have N-terminal glutamine."""
    # setup
    filter_instance = ContainsNTerminalGlutamineMotifFilter()

    # execute
    result = filter_instance.evaluate(good_universal_peptide, universal_protein)

    # validate
    assert result is False


@pytest.mark.unit
def test_contains_n_terminal_glutamine_filter_with_n_terminal_glutamine(
    bad_universal_peptide1: PeptideDomain,
    universal_protein: ProteinDomain,
) -> None:
    """Test that filter returns True when peptide has N-terminal glutamine."""
    # setup
    filter_instance = ContainsNTerminalGlutamineMotifFilter()

    # execute
    result = filter_instance.evaluate(bad_universal_peptide1, universal_protein)

    # validate
    assert result is True


@pytest.mark.unit
def test_contains_n_terminal_glutamine_filter_returns_proper_enum() -> None:
    """Test that filter returns proper enum."""
    # setup
    filter_instance = ContainsNTerminalGlutamineMotifFilter()

    # execute and validate
    assert (
        filter_instance.criteria_enum
        == CriteriaEnum.CONTAINS_N_TERMINAL_GLUTAMINE_MOTIF
    )
