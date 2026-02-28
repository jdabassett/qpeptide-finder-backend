import pytest

from app.domain import ProteinDomain
from app.enums import AminoAcidEnum, ProteaseEnum
from app.schemas.digest import DigestJobRequest
from tests.factories import DigestFactory, ProteinDomainFactory


@pytest.mark.unit
def test_digest_sequence_successful() -> None:
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
    assert protein_domain.peptides[0].sequence == AminoAcidEnum.to_amino_acids("MK")
    assert protein_domain.peptides[0].position == 1
    assert protein_domain.peptides[1].sequence == AminoAcidEnum.to_amino_acids(
        "TAYIAKPR"
    )
    assert protein_domain.peptides[1].position == 3
    assert protein_domain.peptides[2].sequence == AminoAcidEnum.to_amino_acids("QAA")
    assert protein_domain.peptides[2].position == 11
    assert sorted(protein_domain.cut_sites) == [2, 10]
    assert sorted(protein_domain.missed_cut_sites) == [8]
    assert sorted(protein_domain.all_cut_sites) == [2, 8, 10]


@pytest.mark.unit
def test_protein_domain_length_property() -> None:
    """Test that length property returns correct sequence length."""
    # setup
    sequence = AminoAcidEnum.to_amino_acids("MKTAYIAKQR")
    protein = ProteinDomainFactory.build(sequence=sequence)

    # execute
    result = protein.length

    # validate
    assert result == 10


@pytest.mark.unit
def test_protein_domain_sequence_as_str_property() -> None:
    """Test that sequence_as_str property converts sequence to string."""
    # setup
    sequence = AminoAcidEnum.to_amino_acids("MKTAYIAKQR")
    protein = ProteinDomainFactory.build(sequence=sequence)

    # execute
    result = protein.sequence_as_str

    # validate
    assert result == "MKTAYIAKQR"


@pytest.mark.unit
def test_protein_domain_generate(db_session) -> None:
    """Test that 'generate' creates ProteinDomain."""
    # setup
    digest = DigestFactory.create(
        sequence="MKTAYIAKQR",
        protease=ProteaseEnum.TRYPSIN,
    )
    db_session.add(digest)
    db_session.commit()

    job_request = DigestJobRequest(
        user_id=digest.user_id,
        protein_name="test",
        protease=digest.protease,
        sequence=digest.sequence,
    )

    # execute
    protein_domain = ProteinDomain.generate(digest, job_request)

    # validate
    assert protein_domain.digest_id == digest.id
    assert protein_domain.sequence == AminoAcidEnum.to_amino_acids("MKTAYIAKQR")
    assert protein_domain.protease == ProteaseEnum.TRYPSIN
    assert protein_domain.criteria_ids == job_request.criteria_ids


@pytest.mark.unit
def test_protein_domain_digest_sequence_no_cut_sites() -> None:
    """Test that digest_sequence handles protein with no cut sites."""
    # setup
    protein = ProteinDomainFactory.create(
        sequence="AAAAA",
        protease=ProteaseEnum.TRYPSIN,
    )

    # execute
    protein.digest_sequence()

    # validate
    assert len(protein.peptides) == 1
    assert protein.peptides[0].sequence == AminoAcidEnum.to_amino_acids("AAAAA")
    assert protein.peptides[0].position == 1
    assert len(protein.cut_sites) == 0
    assert len(protein.missed_cut_sites) == 0
    assert len(protein.all_cut_sites) == 0
