"""remove_timestamps_from_protein_peptide_digest_proteases

Revision ID: 20b3aba2ba6c
Revises: 9bbe7cd011b9
Create Date: 2025-11-24 14:18:34.076951

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from alembic import op  # type: ignore[attr-defined]

# revision identifiers, used by Alembic.
revision: str = "20b3aba2ba6c"
down_revision: str | Sequence[str] | None = "9bbe7cd011b9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    protease_enum = sa.Enum(
        "trypsin",
        "chymotrypsin",
        "pepsin",
        "elastase",
        "proteinase_k",
        "thermolysin",
        name="proteaseenum",
    )

    op.create_table(
        "digest_proteases",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("digest_id", sa.String(length=36), nullable=False),
        sa.Column("protease", protease_enum, nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["digest_id"], ["digests.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("digest_id", "order", name="uq_digest_order"),
        sa.UniqueConstraint("digest_id", "protease", name="uq_digest_protease"),
    )

    op.create_index(
        op.f("ix_digest_proteases_digest_id"),
        "digest_proteases",
        ["digest_id"],
        unique=False,
    )

    op.drop_column("digests", "protease_3")
    op.drop_column("digests", "protease_2")
    op.drop_column("digests", "protease_1")

    op.drop_column("peptides", "updated_at")
    op.drop_column("peptides", "created_at")

    op.drop_column("proteins", "updated_at")
    op.drop_column("proteins", "created_at")


def downgrade() -> None:
    """Downgrade schema."""
    protease_enum = sa.Enum(
        "trypsin",
        "chymotrypsin",
        "pepsin",
        "elastase",
        "proteinase_k",
        "thermolysin",
        name="proteaseenum",
    )

    op.add_column(
        "proteins",
        sa.Column(
            "created_at",
            mysql.DATETIME(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.add_column(
        "proteins",
        sa.Column(
            "updated_at",
            mysql.DATETIME(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        ),
    )

    op.add_column(
        "peptides",
        sa.Column(
            "created_at",
            mysql.DATETIME(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.add_column(
        "peptides",
        sa.Column(
            "updated_at",
            mysql.DATETIME(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        ),
    )

    op.add_column(
        "digests",
        sa.Column(
            "protease_1",
            protease_enum,
            nullable=False,
            server_default=sa.text("'trypsin'"),
        ),
    )
    op.add_column("digests", sa.Column("protease_2", protease_enum, nullable=True))
    op.add_column("digests", sa.Column("protease_3", protease_enum, nullable=True))

    op.drop_index(op.f("ix_digest_proteases_digest_id"), table_name="digest_proteases")
    op.drop_table("digest_proteases")
