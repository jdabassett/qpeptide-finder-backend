"""
Pytest configuration and shared fixtures.
"""

import uuid
from collections.abc import Generator
from typing import Any
from unittest.mock import patch

import pytest
from factory.alchemy import SQLAlchemyModelFactory
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import get_db
from app.domain import PeptideDomain, ProteinDomain
from app.enums import AminoAcidEnum, CriteriaEnum, DigestStatusEnum, ProteaseEnum
from app.main import app

# Import all models to ensure they're registered with BaseModel.metadata
from app.models import Criteria, Digest, Peptide, User  # noqa: F401
from app.models.base import Base
from app.tasks import process_digest_job
from tests.factories import PeptideDomainFactory, ProteinDomainFactory, UserFactory

TEST_DATABASE_URL = "sqlite:///:memory:"

# Criteria data from migration - must match alembic/versions/1d3884dbeb40_create_tables.py
CRITERIA_DATA = [
    {
        "code": "not_unique",
        "goal": "The peptide must unique within the target protein.",
        "rationale": "Ensures that the measured signal reflects only one site from the protein of interest.",
    },
    {
        "code": "has_flanking_cut_sites",
        "goal": "Do not choose peptides immediately adjacent to cleavage motifs (e.g., K, R, KP, RP).",
        "rationale": "Proximity to other cut sites can reduce digestion efficiency, leading to missed cleavages or semi-tryptic peptides.",
    },
    {
        "code": "contains_missed_cleavages",
        "goal": "Ensure the peptide is completely generated during digestion.",
        "rationale": "Missed cleavage sites (e.g., Lys-Pro, Arg-Pro) produce heterogeneous peptide populations, reducing reproducibility and quantitative accuracy.",
    },
    {
        "code": "outlier_length",
        "goal": "7–30 amino acids.",
        "rationale": "Peptides shorter than 7 residues are often not unique and fragment poorly. Peptides longer than 30 residues ionize inefficiently and fragment unpredictably. This range provides optimal MS detectability and sequence coverage.",
    },
    {
        "code": "lacking_flanking_amino_acids",
        "goal": "Prioritizes peptides with at least 6 residues on both sides of the cleavage site in the intact protein.",
        "rationale": "Improves trypsin accessibility and digestion efficiency, producing more consistent peptide generation.",
    },
    {
        "code": "outlier_hydrophobicity",
        "goal": "Exclude peptides with extreme hydrophobicity values (too hydrophobic or too hydrophilic).",
        "rationale": "Very hydrophobic peptides adhere to columns, elute poorly, and ionize inefficiently, lowering MS signal. Highly hydrophilic peptides are too soluble and won't bind to the column long enough to elute in the retention curve, also reducing detectability.",
    },
    {
        "code": "outlier_charge_state",
        "goal": "Favor peptides that form 2+ or 3+ ions.",
        "rationale": "Very basic peptides (4+ or higher) or neutral peptides (1+) fragment less predictably, decreasing identification reliability.",
    },
    {
        "code": "outlier_pi",
        "goal": "Select peptides with a pI between 4 and 9.",
        "rationale": "Peptides with pI between 4 and 9 reliably produce clean LC peaks, stable charge states, and informative MS/MS spectra under acidic RP-LC-ESI conditions.",
    },
    {
        "code": "contains_asparagine_glycine_motif",
        "goal": "Exclude Asparagine–Glycine sequences.",
        "rationale": "N–G motifs deamidate rapidly post-digestion, producing mixed modified/unmodified peptides that complicate quantitation.",
    },
    {
        "code": "contains_aspartic_proline_motif",
        "goal": "Exclude Aspartic–Proline sequences.",
        "rationale": "Aspartic acid followed by proline causes preferential gas-phase cleavage, producing non-informative fragmentation spectra and reducing identification confidence.",
    },
    {
        "code": "contains_long_homopolymeric_stretch",
        "goal": "Avoid homopolymeric sequences.",
        "rationale": "Homopolymeric sequences produce weak, uninformative fragmentation spectra, reducing confidence in identification.",
    },
    {
        "code": "contains_n_terminal_glutamine_motif",
        "goal": "Exclude peptides with N-terminal glutamine.",
        "rationale": "N-terminal glutamine cyclizes to pyroglutamate or converts to glutamate post-digestion, producing multiple forms that complicate quantification.",
    },
    {
        "code": "contains_methionine",
        "goal": "Avoid methionine-containing peptides.",
        "rationale": "Methionine oxidizes readily during sample handling, generating multiple peptide species with different masses and retention times, reducing quantitative precision.",
    },
    {
        "code": "contains_cysteine",
        "goal": "Minimize peptides containing cysteine.",
        "rationale": "Cysteine requires alkylation; incomplete or over-alkylation creates heterogeneous populations, reducing quantitative reliability.",
    },
]


@pytest.fixture(scope="session")
def test_engine():
    """
    Create a test database engine once per test session.
    This creates the database and tables before any tests run.
    """
    # Create in-memory SQLite engine with StaticPool to allow connections
    # from different threads (needed for FastAPI TestClient)
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield engine

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine) -> Generator[Session]:
    """
    Create a database session for each test function.
    Uses a transaction that rolls back after each test, ensuring data isolation.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()

    for factory_class in SQLAlchemyModelFactory.__subclasses__():
        factory_class._meta.sqlalchemy_session = session

    if session.query(Criteria).count() == 0:
        for idx, item in enumerate(CRITERIA_DATA, start=1):
            criteria = Criteria(
                id=str(uuid.uuid4()),
                code=CriteriaEnum(item["code"]),
                goal=item["goal"],
                rationale=item["rationale"],
                rank=idx,
            )
            session.add(criteria)
        session.commit()

    yield session

    for factory_class in SQLAlchemyModelFactory.__subclasses__():
        factory_class._meta.sqlalchemy_session = None

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session: Session):
    """
    Create a test client for the FastAPI application.
    Overrides the get_db dependency to use the test database session.
    """

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def bad_universal_peptide1() -> Any:
    """
    Create a peptide will not pass most filters.
    """
    return PeptideDomainFactory.build(
        position=1,
        sequence=AminoAcidEnum.to_amino_acids("QCNGDPWWWWWWWWKPMCNGDPKPWWWWWWWWR"),
    )


@pytest.fixture(scope="session")
def bad_universal_peptide2() -> Any:
    """
    Create a peptide will not pass most filters.
    """
    return PeptideDomainFactory.build(
        position=41,
        sequence=AminoAcidEnum.to_amino_acids("QCNGDPWWWWWWWWKPMCNGDPKPWWWWWWWWR"),
    )


@pytest.fixture(scope="session")
def good_universal_peptide() -> Any:
    """
    Create a peptide will pass most filters.
    """
    return PeptideDomainFactory.build(
        position=34,
        sequence=AminoAcidEnum.to_amino_acids("AEDIHYK"),
    )


@pytest.fixture(scope="session")
def universal_protein(
    bad_universal_peptide1: PeptideDomain,
    good_universal_peptide: PeptideDomain,
    bad_universal_peptide2: PeptideDomain,
) -> ProteinDomain:
    """
    Create a universal protein domain that can be used across multiple tests.
    """
    sequence: list[AminoAcidEnum] = (
        bad_universal_peptide1.sequence
        + good_universal_peptide.sequence
        + bad_universal_peptide2.sequence
    )
    protein = ProteinDomainFactory.build(
        sequence=sequence,
    )
    protein.digest_sequence()
    return protein


@pytest.fixture(scope="function")
def setup_digest_with_peptides(
    universal_protein: ProteinDomain,
    db_session: Session,
) -> tuple[str, str]:
    """
    Set up a complete digest with user, peptides, and criteria for testing.
    Returns (user, digest) tuple.
    """
    user = UserFactory.create()
    user_id = user.id

    digest_id = str(uuid.uuid4())
    universal_protein.digest_id = digest_id

    Digest.create(
        db_session,
        flush=True,
        status=DigestStatusEnum.PROCESSING,
        user_id=user.id,
        protease=ProteaseEnum.TRYPSIN,
        protein_name=None,
        sequence=universal_protein.sequence_as_str,
        id=digest_id,
    )

    with patch("app.tasks.digest_task.SessionLocal", return_value=db_session):
        process_digest_job(universal_protein)

    db_session.commit()

    return user_id, digest_id
