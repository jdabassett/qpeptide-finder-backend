"""Initial migration

Revision ID: 56e3897cf1af
Revises:
Create Date: 2025-11-11 00:27:54.009821

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "56e3897cf1af"
down_revision: str | Sequence[str] | None = None
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
    digest_status_enum = sa.Enum(
        "pending", "processing", "completed", "failed", name="digeststatusenum"
    )

    # users table
    op.create_table(
        "users",
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    # proteins table
    op.create_table(
        "proteins",
        sa.Column("uni_prot_accession_number", sa.String(length=20), nullable=True),
        sa.Column("ncbi_protein_accession", sa.String(length=50), nullable=True),
        sa.Column("protein_name", sa.String(length=255), nullable=False),
        sa.Column("sequence", sa.String(length=2000), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_proteins_user_id"), "proteins", ["user_id"], unique=False)

    # digests table
    op.create_table(
        "digests",
        sa.Column("protease_1", protease_enum, nullable=False),
        sa.Column("protease_2", protease_enum, nullable=True),
        sa.Column("protease_3", protease_enum, nullable=True),
        sa.Column("status", digest_status_enum, nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("protein_id", sa.String(length=36), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["protein_id"], ["proteins.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_digests_protein_id"), "digests", ["protein_id"], unique=False
    )
    op.create_index(op.f("ix_digests_user_id"), "digests", ["user_id"], unique=False)

    # peptides table
    op.create_table(
        "peptides",
        sa.Column("digest_id", sa.String(length=36), nullable=False),
        sa.Column("sequence", sa.String(length=500), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["digest_id"], ["digests.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_peptides_digest_id"), "peptides", ["digest_id"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(op.f("ix_peptides_digest_id"), table_name="peptides")
    op.drop_table("peptides")

    op.drop_index(op.f("ix_digests_user_id"), table_name="digests")
    op.drop_index(op.f("ix_digests_protein_id"), table_name="digests")
    op.drop_table("digests")

    op.drop_index(op.f("ix_proteins_user_id"), table_name="proteins")
    op.drop_table("proteins")

    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_table("users")

    sa.Enum(name="proteaseenum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="digeststatusenum").drop(op.get_bind(), checkfirst=True)
