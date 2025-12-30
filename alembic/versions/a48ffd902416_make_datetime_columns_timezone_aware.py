"""make_datetime_columns_timezone_aware

Revision ID: a48ffd902416
Revises: 1d3884dbeb40
Create Date: 2025-12-23 09:33:37.427796

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from alembic import op  # type: ignore[attr-defined]

# revision identifiers, used by Alembic.
revision: str = "a48ffd902416"
down_revision: str | Sequence[str] | None = "1d3884dbeb40"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Update users table
    op.alter_column(
        "users",
        "created_at",
        type_=sa.DateTime(timezone=True),
        existing_type=mysql.DATETIME(),
        existing_nullable=False,
    )
    op.alter_column(
        "users",
        "updated_at",
        type_=sa.DateTime(timezone=True),
        existing_type=mysql.DATETIME(),
        existing_nullable=False,
    )

    # Update digests table
    op.alter_column(
        "digests",
        "created_at",
        type_=sa.DateTime(timezone=True),
        existing_type=mysql.DATETIME(),
        existing_nullable=False,
    )
    op.alter_column(
        "digests",
        "updated_at",
        type_=sa.DateTime(timezone=True),
        existing_type=mysql.DATETIME(),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "users",
        "created_at",
        type_=mysql.DATETIME(),
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
    )
    op.alter_column(
        "users",
        "updated_at",
        type_=mysql.DATETIME(),
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
    )

    op.alter_column(
        "digests",
        "created_at",
        type_=mysql.DATETIME(),
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
    )
    op.alter_column(
        "digests",
        "updated_at",
        type_=mysql.DATETIME(),
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
    )
