"""
Pytest configuration and shared fixtures.
"""

from collections.abc import Generator

import pytest
from factory.alchemy import SQLAlchemyModelFactory
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import get_db
from app.main import app

# Import all models to ensure they're registered with BaseModel.metadata
from app.models import Digest, Peptide, Protein, User  # noqa: F401
from app.models.base import BaseModel

TEST_DATABASE_URL = "sqlite:///:memory:"


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
    BaseModel.metadata.create_all(bind=engine)

    yield engine

    BaseModel.metadata.drop_all(bind=engine)
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
