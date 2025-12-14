from logging.config import fileConfig

from sqlalchemy import create_engine, pool

from alembic import context  # type: ignore[attr-defined]
from app.core.config import settings

# Import all models to ensure they're registered with Base.metadata
from app.models import Criteria, Digest, Peptide, PeptideCriteria, User  # noqa: F401
from app.models.base import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Fix: Set URL directly to avoid configparser interpolation issues
# This prevents errors when DATABASE_URL contains special characters like %, #, etc.
config.attributes["sqlalchemy.url"] = settings.DATABASE_URL


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # Use DATABASE_URL directly from settings to avoid configparser issues
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Create engine directly from DATABASE_URL to avoid configparser interpolation
    # This prevents errors when passwords contain special characters like %, #, etc.
    connectable = create_engine(
        settings.DATABASE_URL,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
