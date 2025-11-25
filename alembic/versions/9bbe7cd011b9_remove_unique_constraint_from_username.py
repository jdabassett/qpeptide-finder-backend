"""remove_unique_constraint_from_username

Revision ID: 9bbe7cd011b9
Revises: 56e3897cf1af
Create Date: 2025-11-23 20:39:08.212146

"""

from collections.abc import Sequence

from alembic import op  # type: ignore[attr-defined]

# revision identifiers, used by Alembic.
revision: str = "9bbe7cd011b9"
down_revision: str | Sequence[str] | None = "56e3897cf1af"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Drop the old unique index
    op.drop_index("ix_users_username", table_name="users")

    # 2. Recreate a NON-UNIQUE index (optional)
    op.create_index("ix_users_username", "users", ["username"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_users_username", table_name="users")
    op.create_index("ix_users_username", "users", ["username"], unique=True)
