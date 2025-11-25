"""update digest proteases table order column

Revision ID: f64815afb635
Revises: 20b3aba2ba6c
Create Date: 2025-11-24 18:22:29.906317

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from alembic import op  # type: ignore[attr-defined]

# revision identifiers, used by Alembic.
revision: str = "f64815afb635"
down_revision: str | Sequence[str] | None = "20b3aba2ba6c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    order_enum = sa.Enum("1", "2", "3", name="orderenum")
    order_enum.create(op.get_bind(), checkfirst=True)

    op.alter_column(
        "digest_proteases",
        "order",
        existing_type=mysql.INTEGER(),
        type_=order_enum,
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "digest_proteases",
        "order",
        existing_type=sa.Enum("1", "2", "3", name="orderenum"),
        type_=mysql.INTEGER(),
        existing_nullable=False,
    )

    sa.Enum(name="orderenum").drop(op.get_bind(), checkfirst=True)
