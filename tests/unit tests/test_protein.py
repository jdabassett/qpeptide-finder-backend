import pytest

from app.domain import ProteinDomain
from app.enums import ProteaseEnum
from tests.factories.domains import ProteinDomainFactory


@pytest.mark.unit
def test_digest_sequence_successful():
    """Test that digest_sequence correctly digests a protein sequence."""
    # setup
    protein_domain: ProteinDomain = ProteinDomainFactory.create(
        sequence="MKTAYIAKPRQAA",
        protease=ProteaseEnum.TRYPSIN,
    )

    # execute
    protein_domain.digest_sequence()

    # validate
    assert len(protein_domain.peptides) == 3
    assert len(protein_domain.cut_sites) == 2
    assert protein_domain.peptides[0].sequence == "MK"
    assert protein_domain.peptides[0].position == 1
    assert protein_domain.peptides[1].sequence == "TAYIAKPR"
    assert protein_domain.peptides[1].position == 3
    assert protein_domain.peptides[2].sequence == "QAA"
    assert protein_domain.peptides[2].position == 11
    assert sorted(protein_domain.cut_sites) == [2, 10]
