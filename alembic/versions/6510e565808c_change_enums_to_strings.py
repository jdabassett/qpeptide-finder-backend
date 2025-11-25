"""change_enums_to_strings

Revision ID: 6510e565808c
Revises: f64815afb635
Create Date: 2025-11-24 22:44:35.415860

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from alembic import op  # type: ignore[attr-defined]

# revision identifiers, used by Alembic.
revision: str = "6510e565808c"
down_revision: str | Sequence[str] | None = "f64815afb635"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "digest_proteases",
        "protease",
        existing_type=mysql.ENUM(
            "trypsin",
            "chymotrypsin",
            "pepsin",
            "elastase",
            "proteinase_k",
            "thermolysin",
            name="proteaseenum",
        ),
        type_=sa.String(length=50),
        existing_nullable=False,
    )

    op.alter_column(
        "digest_proteases",
        "order",
        existing_type=sa.Enum("1", "2", "3", name="orderenum"),
        type_=sa.String(length=10),
        existing_nullable=False,
    )

    op.alter_column(
        "digests",
        "status",
        existing_type=mysql.ENUM(
            "pending", "processing", "completed", "failed", name="digeststatusenum"
        ),
        type_=sa.String(length=20),
        existing_nullable=False,
    )

    sa.Enum(name="proteaseenum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="orderenum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="digeststatusenum").drop(op.get_bind(), checkfirst=True)


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
    protease_enum.create(op.get_bind(), checkfirst=True)

    order_enum = sa.Enum("1", "2", "3", name="orderenum")
    order_enum.create(op.get_bind(), checkfirst=True)

    digest_status_enum = sa.Enum(
        "pending", "processing", "completed", "failed", name="digeststatusenum"
    )
    digest_status_enum.create(op.get_bind(), checkfirst=True)

    op.alter_column(
        "digests",
        "status",
        existing_type=sa.String(length=20),
        type_=digest_status_enum,
        existing_nullable=False,
    )

    op.alter_column(
        "digest_proteases",
        "order",
        existing_type=sa.String(length=10),
        type_=order_enum,
        existing_nullable=False,
    )

    op.alter_column(
        "digest_proteases",
        "protease",
        existing_type=sa.String(length=50),
        type_=protease_enum,
        existing_nullable=False,
    )
