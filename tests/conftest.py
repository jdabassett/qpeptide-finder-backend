"""
Pytest configuration and shared fixtures.
"""

import uuid
from collections.abc import Generator
from typing import Any

import pytest
from factory.alchemy import SQLAlchemyModelFactory
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import get_db
from app.domain import PeptideDomain, ProteinDomain
from app.enums import AminoAcidEnum, CriteriaEnum
from app.main import app

# Import all models to ensure they're registered with BaseModel.metadata
from app.models import Criteria, Digest, Peptide, User  # noqa: F401
from app.models.base import Base
from tests.factories.domains import PeptideDomainFactory, ProteinDomainFactory

TEST_DATABASE_URL = "sqlite:///:memory:"

# Criteria data from migration - must match alembic/versions/1d3884dbeb40_create_tables.py
CRITERIA_DATA = [
    {
        "code": "unique_sequence",
        "goal": "The peptide must unique within the target protein.",
        "rationale": "Ensures that the measured signal reflects only one site from the protein of interest.",
    },
    {
        "code": "no_missed_cleavage",
        "goal": "Ensure the peptide is completely generated during digestion.",
        "rationale": "Missed cleavage sites (e.g., Lys-Pro, Arg-Pro) produce heterogeneous peptide populations, reducing reproducibility and quantitative accuracy.",
    },
    {
        "code": "avoid_flanking_cut_sites",
        "goal": "Do not choose peptides immediately adjacent to cleavage motifs (e.g., KP, RP, PP).",
        "rationale": "Proximity to other cut sites can reduce digestion efficiency, leading to missed cleavages or semi-tryptic peptides.",
    },
    {
        "code": "flanking_amino_acids",
        "goal": "Prioritizes peptides with at least 6 residues on both sides of the cleavage site in the intact protein.",
        "rationale": "Improves trypsin accessibility and digestion efficiency, producing more consistent peptide generation.",
    },
    {
        "code": "peptide_length",
        "goal": "7–30 amino acids.",
        "rationale": "Peptides shorter than 7 residues are often not unique and fragment poorly. Peptides longer than 30 residues ionize inefficiently and fragment unpredictably. This range provides optimal MS detectability and sequence coverage.",
    },
    {
        "code": "no_n-terminal_glutamine",
        "goal": "Exclude peptides with N-terminal glutamine.",
        "rationale": "N-terminal glutamine cyclizes to pyroglutamate or converts to glutamate post-digestion, producing multiple forms that complicate quantification.",
    },
    {
        "code": "no_asp_pro_motif",
        "goal": "Exclude Asp–Pro sequences.",
        "rationale": "Aspartic acid followed by proline causes preferential gas-phase cleavage, producing non-informative fragmentation spectra and reducing identification confidence.",
    },
    {
        "code": "no_asn_gly_motif",
        "goal": "Exclude Asparagine–Glycine sequences.",
        "rationale": "N–G motifs deamidate rapidly post-digestion, producing mixed modified/unmodified peptides that complicate quantitation.",
    },
    {
        "code": "avoid_methionine",
        "goal": "Avoid methionine-containing peptides.",
        "rationale": "Methionine oxidizes readily during sample handling, generating multiple peptide species with different masses and retention times, reducing quantitative precision.",
    },
    {
        "code": "avoid_cysteine",
        "goal": "Minimize peptides containing cysteine.",
        "rationale": "Cysteine requires alkylation; incomplete or over-alkylation creates heterogeneous populations, reducing quantitative reliability.",
    },
    {
        "code": "peptide_pi",
        "goal": "Select peptides with pI below ~4.5.",
        "rationale": "Acidic peptides ionize more efficiently in positive-mode electrospray and elute reproducibly in LC-MS, improving detectability.",
    },
    {
        "code": "avoid_ptm_prone_residues",
        "goal": "Avoid peptides likely to carry modifications.",
        "rationale": "PTMs create multiple peptide forms, reducing quantitative precision. Only necessary if the protein is known or suspected to be modified.",
    },
    {
        "code": "avoid_highly_hydrophobic_peptides",
        "goal": "Exclude transmembrane or very hydrophobic regions.",
        "rationale": "Hydrophobic peptides adhere to columns, elute poorly, and ionize inefficiently, lowering MS signal.",
    },
    {
        "code": "avoid_long_homopolymeric_stretches",
        "goal": "Avoid homopolymeric sequences.",
        "rationale": "Homopolymeric sequences produce weak, uninformative fragmentation spectra, reducing confidence in identification.",
    },
    {
        "code": "prefer_typical_charge_states",
        "goal": "Favor peptides that form 2+ or 3+ ions.",
        "rationale": "Very basic peptides (4+ or higher) or neutral peptides (1+) fragment less predictably, decreasing identification reliability.",
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
        sequence=AminoAcidEnum.to_amino_acids("QCNGDPKPWWWWWWWWMCNGDPKPWWWWWWWWR"),
    )


@pytest.fixture(scope="session")
def bad_universal_peptide2() -> Any:
    """
    Create a peptide will not pass most filters.
    """
    return PeptideDomainFactory.build(
        position=41,
        sequence=AminoAcidEnum.to_amino_acids("QCNGDPKPWWWWWWWWMCNGDPKPWWWWWWWWR"),
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
    return ProteinDomainFactory.build(
        sequence=sequence,
        cut_sites={33, 40, 73},
        missed_cut_sites={7, 23, 47, 63},
        all_cut_sites={7, 23, 33, 40, 47, 63, 73},
        peptides=[
            bad_universal_peptide1,
            good_universal_peptide,
            bad_universal_peptide2,
        ],
    )
