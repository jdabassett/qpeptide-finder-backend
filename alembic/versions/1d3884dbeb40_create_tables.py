"""create tables

Revision ID: 1d3884dbeb40
Revises:
Create Date: 2025-12-11 20:49:48.104608

"""

import uuid
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op  # type: ignore[attr-defined]

# revision identifiers, used by Alembic.
revision: str = "1d3884dbeb40"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

PROTEASE_ENUM = sa.Enum(
    "trypsin",
    name="protease_enum",
    native_enum=False,
    length=50,
)

CRITERIA_ENUM = sa.Enum(
    "unique_sequence",
    "no_missed_cleavage",
    "avoid_flanking_cut_sites",
    "flanking_amino_acids",
    "peptide_length",
    "no_n-terminal_glutamine",
    "no_asp_pro_motif",
    "no_asn_gly_motif",
    "avoid_methionine",
    "avoid_cysteine",
    "peptide_pi",
    "avoid_ptm_prone_residues",
    "avoid_highly_hydrophobic_peptides",
    "avoid_long_homopolymeric_stretches",
    "prefer_typical_charge_states",
    name="criteria_enum",
    native_enum=False,
    length=50,
)

DIGEST_ENUM = sa.Enum(
    "processing",
    "completed",
    "failed",
    name="digest_status_enum",
    native_enum=False,
    length=25,
)

# order in table is significant
CRITERIA_DATA = [
    {
        "code": "unique_sequence",
        "goal": "The peptide must unique within the target protein.",
        "rationale": "Ensures that the measured signal reflects only one site from the protein of interest.",
    },
    {
        "code": "no_missed_cleavage",
        "goal": "Ensure the peptide is completely generated during digestion.",
        "rationale": "Missed cleavage sites (e.g., Lys-Pro, Arg-Pro) produce heterogeneous peptide populations, reducing reproducibility and quantitative accuracy.",
    },
    {
        "code": "avoid_flanking_cut_sites",
        "goal": "Do not choose peptides immediately adjacent to cleavage motifs (e.g., KP, RP, PP).",
        "rationale": "Proximity to other cut sites can reduce digestion efficiency, leading to missed cleavages or semi-tryptic peptides.",
    },
    {
        "code": "flanking_amino_acids",
        "goal": "Prioritizes peptides with at least 6 residues on both sides of the cleavage site in the intact protein.",
        "rationale": "Improves trypsin accessibility and digestion efficiency, producing more consistent peptide generation.",
    },
    {
        "code": "peptide_length",
        "goal": "7–30 amino acids.",
        "rationale": "Peptides shorter than 7 residues are often not unique and fragment poorly. Peptides longer than 30 residues ionize inefficiently and fragment unpredictably. This range provides optimal MS detectability and sequence coverage.",
    },
    {
        "code": "no_n-terminal_glutamine",
        "goal": "Exclude peptides with N-terminal glutamine.",
        "rationale": "N-terminal glutamine cyclizes to pyroglutamate or converts to glutamate post-digestion, producing multiple forms that complicate quantification.",
    },
    {
        "code": "no_asp_pro_motif",
        "goal": "Exclude Asp–Pro sequences.",
        "rationale": "Aspartic acid followed by proline causes preferential gas-phase cleavage, producing non-informative fragmentation spectra and reducing identification confidence.",
    },
    {
        "code": "no_asn_gly_motif",
        "goal": "Exclude Asparagine–Glycine sequences.",
        "rationale": "N–G motifs deamidate rapidly post-digestion, producing mixed modified/unmodified peptides that complicate quantitation.",
    },
    {
        "code": "avoid_methionine",
        "goal": "Avoid methionine-containing peptides.",
        "rationale": "Methionine oxidizes readily during sample handling, generating multiple peptide species with different masses and retention times, reducing quantitative precision.",
    },
    {
        "code": "avoid_cysteine",
        "goal": "Minimize peptides containing cysteine.",
        "rationale": "Cysteine requires alkylation; incomplete or over-alkylation creates heterogeneous populations, reducing quantitative reliability.",
    },
    {
        "code": "peptide_pi",
        "goal": "Select peptides with pI below ~4.5.",
        "rationale": "Acidic peptides ionize more efficiently in positive-mode electrospray and elute reproducibly in LC-MS, improving detectability.",
    },
    {
        "code": "avoid_ptm_prone_residues",
        "goal": "Avoid peptides likely to carry modifications.",
        "rationale": "PTMs create multiple peptide forms, reducing quantitative precision. Only necessary if the protein is known or suspected to be modified.",
    },
    {
        "code": "avoid_highly_hydrophobic_peptides",
        "goal": "Exclude transmembrane or very hydrophobic regions.",
        "rationale": "Hydrophobic peptides adhere to columns, elute poorly, and ionize inefficiently, lowering MS signal.",
    },
    {
        "code": "avoid_long_homopolymeric_stretches",
        "goal": "Avoid homopolymeric sequences.",
        "rationale": "Homopolymeric sequences produce weak, uninformative fragmentation spectra, reducing confidence in identification.",
    },
    {
        "code": "prefer_typical_charge_states",
        "goal": "Favor peptides that form 2+ or 3+ ions.",
        "rationale": "Very basic peptides (4+ or higher) or neutral peptides (1+) fragment less predictably, decreasing identification reliability.",
    },
]


def upgrade() -> None:
    """Upgrade schema."""
    PROTEASE_ENUM.create(op.get_bind(), checkfirst=True)
    CRITERIA_ENUM.create(op.get_bind(), checkfirst=True)
    DIGEST_ENUM.create(op.get_bind(), checkfirst=True)

    # users table
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=False)

    # digests table
    op.create_table(
        "digests",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("protease", PROTEASE_ENUM, nullable=False),
        sa.Column("protein_name", sa.String(length=200), nullable=True),
        sa.Column("sequence", sa.String(length=3000), nullable=False),
        sa.Column("status", DIGEST_ENUM, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_digests_user_id"), "digests", ["user_id"], unique=False)

    # peptides table
    op.create_table(
        "peptides",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("digest_id", sa.String(length=36), nullable=False),
        sa.Column("sequence", sa.String(length=500), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["digest_id"], ["digests.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_peptides_digest_id"), "peptides", ["digest_id"], unique=False
    )

    # criteria table
    op.create_table(
        "criteria",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("code", CRITERIA_ENUM, nullable=False),
        sa.Column("goal", sa.String(length=250), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("rank", name="uq_criteria_rank"),
    )
    op.create_index(op.f("ix_criteria_code"), "criteria", ["code"], unique=True)
    op.create_index(op.f("ix_criteria_rank"), "criteria", ["rank"], unique=True)

    criteria_table = sa.table(
        "criteria",
        sa.column("id", sa.String),
        sa.column("code", CRITERIA_ENUM),
        sa.column("goal", sa.String),
        sa.column("rationale", sa.Text),
        sa.column("rank", sa.Integer),
    )

    op.bulk_insert(
        criteria_table,
        [
            {
                "id": str(uuid.uuid4()),
                "code": item["code"],
                "goal": item["goal"],
                "rationale": item["rationale"],
                "rank": idx + 1,
            }
            for idx, item in enumerate(CRITERIA_DATA)
        ],
    )

    # peptide_criteria join table
    op.create_table(
        "peptide_criteria",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("peptide_id", sa.String(length=36), nullable=False),
        sa.Column("criteria_id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["peptide_id"], ["peptides.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["criteria_id"], ["criteria.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("peptide_id", "criteria_id", name="uq_peptide_criteria"),
    )
    op.create_index(
        op.f("ix_peptide_criteria_peptide_id"),
        "peptide_criteria",
        ["peptide_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_peptide_criteria_criteria_id"),
        "peptide_criteria",
        ["criteria_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_peptide_criteria_criteria_id"), table_name="peptide_criteria"
    )
    op.drop_index(op.f("ix_peptide_criteria_peptide_id"), table_name="peptide_criteria")
    op.drop_table("peptide_criteria")

    op.drop_index(op.f("ix_criteria_rank"), table_name="criteria")
    op.drop_index(op.f("ix_criteria_code"), table_name="criteria")
    op.drop_table("criteria")

    op.drop_index(op.f("ix_peptides_digest_id"), table_name="peptides")
    op.drop_table("peptides")

    op.drop_index(op.f("ix_digests_user_id"), table_name="digests")
    op.drop_table("digests")

    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_table("users")

    PROTEASE_ENUM.drop(op.get_bind(), checkfirst=True)
    CRITERIA_ENUM.drop(op.get_bind(), checkfirst=True)
    DIGEST_ENUM.drop(op.get_bind(), checkfirst=True)
