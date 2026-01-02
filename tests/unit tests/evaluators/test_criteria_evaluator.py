import pytest

from app.domain import ProteinDomain
from app.tasks import create_default_criteria_evaluator


@pytest.mark.unit
def test_evaluate_peptides_assigns_ranks(universal_protein: ProteinDomain) -> None:
    """Test that evaluate_peptides assigns ranks to all peptides."""
    # setup
    evaluator = create_default_criteria_evaluator()

    # execute
    evaluator.evaluate_peptides(universal_protein)

    # validate
    assert len(universal_protein.peptides) > 0
    ranks = [p.rank for p in universal_protein.peptides]

    assert all(r is not None for r in ranks)
    assert all(isinstance(r, int) for r in ranks)

    int_ranks: list[int] = [r for r in ranks if r is not None]
    assert sorted(int_ranks) == list(range(1, len(int_ranks) + 1))
