"""add-peptide-attributes

Revision ID: e618df5ee6cb
Revises: 718ebad503d2
Create Date: 2025-12-28 12:31:57.454088

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from alembic import op  # type: ignore[attr-defined]

# revision identifiers, used by Alembic.
revision: str = "e618df5ee6cb"
down_revision: str | Sequence[str] | None = "718ebad503d2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "digests",
        "status",
        existing_type=mysql.VARCHAR(length=25),
        type_=sa.Enum(
            "PROCESSING",
            "COMPLETED",
            "FAILED",
            name="digeststatusenum",
            native_enum=False,
            length=20,
        ),
        existing_nullable=False,
    )

    op.add_column("peptides", sa.Column("pi", sa.Float(), nullable=True))
    op.add_column("peptides", sa.Column("charge_state", sa.Integer(), nullable=True))
    op.add_column("peptides", sa.Column("max_kd_score", sa.Float(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("peptides", "max_kd_score")
    op.drop_column("peptides", "charge_state")
    op.drop_column("peptides", "pi")

    op.alter_column(
        "digests",
        "status",
        existing_type=sa.Enum(
            "PROCESSING",
            "COMPLETED",
            "FAILED",
            name="digeststatusenum",
            native_enum=False,
            length=20,
        ),
        type_=mysql.VARCHAR(length=25),
        existing_nullable=False,
    )
