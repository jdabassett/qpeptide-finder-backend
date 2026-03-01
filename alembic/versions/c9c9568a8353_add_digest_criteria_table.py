"""add_digest_criteria_table

Revision ID: <rev_id>
Revises: 8fec523735fd
Create Date: <date>

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op  # type: ignore[attr-defined]

revision: str = "<rev_id>"
down_revision: str | Sequence[str] | None = "8fec523735fd"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "digest_criteria",
        sa.Column("digest_id", sa.String(length=36), nullable=False),
        sa.Column("criteria_code", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(
            ["digest_id"],
            ["digests.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["criteria_code"],
            ["criteria.code"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "digest_id", "criteria_code", name="pk_digest_criteria"
        ),
    )
    op.create_index(
        op.f("ix_digest_criteria_digest_id"),
        "digest_criteria",
        ["digest_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_digest_criteria_criteria_code"),
        "digest_criteria",
        ["criteria_code"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_digest_criteria_criteria_code"),
        table_name="digest_criteria",
    )
    op.drop_index(
        op.f("ix_digest_criteria_digest_id"),
        table_name="digest_criteria",
    )
    op.drop_table("digest_criteria")
