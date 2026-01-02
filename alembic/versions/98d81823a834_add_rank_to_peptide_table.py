"""add-rank-to-peptide-table

Revision ID: 98d81823a834
Revises: e618df5ee6cb
Create Date: 2026-01-01 16:59:24.536785

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op  # type: ignore[attr-defined]

revision: str = "98d81823a834"
down_revision: str | Sequence[str] | None = "e618df5ee6cb"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add rank column to peptides table."""
    op.add_column("peptides", sa.Column("rank", sa.Integer(), nullable=False))

    op.create_unique_constraint(
        "uq_peptide_digest_rank", "peptides", ["digest_id", "rank"]
    )


def downgrade() -> None:
    """Remove rank column from peptides table."""
    op.drop_constraint("uq_peptide_digest_rank", "peptides", type_="unique")
    op.drop_column("peptides", "rank")
