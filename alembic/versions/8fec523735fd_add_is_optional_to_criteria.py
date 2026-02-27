"""add_is_optional_to_criteria

Revision ID: 8fec523735fd
Revises: 98d81823a834
Create Date: 2026-02-25 21:33:58.914620

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.exc import OperationalError

from alembic import op  # type: ignore[attr-defined]

# revision identifiers, used by Alembic.
revision: str = "8fec523735fd"
down_revision: str | Sequence[str] | None = "98d81823a834"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

NEW_CRITERIA_DATA = [
    {
        "code": "not_unique",
        "goal": "Uniqueness: The peptide must unique within the target protein.",
        "rationale": "Ensures that the measured signal reflects only one site from the protein of interest.",
        "is_optional": "False",
    },
    {
        "code": "has_flanking_cut_sites",
        "goal": "Flanking Cut Sites: Avoid peptides immediately adjacent to cleavage motifs (K, R, KP, RP).",
        "rationale": "Proximity to other cut sites can reduce digestion efficiency, leading to missed cleavages or semi-tryptic peptides.",
        "is_optional": "False",
    },
    {
        "code": "contains_missed_cleavages",
        "goal": "Missed Cleavages: Ensure complete digestion.",
        "rationale": "Missed cleavage sites (e.g., KP, RP) produce heterogeneous peptide populations, reducing reproducibility and quantitative accuracy.",
        "is_optional": "False",
    },
    {
        "code": "contains_n_terminal_glutamine_motif",
        "goal": "N-Terminal Glutamine(Q): Avoid peptides with N-terminal Glutamine.",
        "rationale": "N-terminal glutamine cyclizes to pyroglutamate or converts to glutamate post-digestion, producing multiple forms that complicate quantification.",
        "is_optional": "True",
    },
    {
        "code": "contains_asparagine_glycine_motif",
        "goal": "Asparagine-Glycine: Avoid NG motif.",
        "rationale": "NG motifs deamidate rapidly post-digestion, producing mixed modified/unmodified peptides.",
        "is_optional": "True",
    },
    {
        "code": "contains_aspartic_proline_motif",
        "goal": "Aspartic-Proline: Avoid DP motif.",
        "rationale": "Aspartic acid followed by proline causes preferential gas-phase cleavage, producing non-informative fragmentation spectra and reducing identification confidence.",
        "is_optional": "True",
    },
    {
        "code": "contains_methionine",
        "goal": "Methionine: Avoid methionine containing peptides.",
        "rationale": "Methionine oxidizes readily during sample handling, generating multiple peptide species with different masses and retention times, reducing quantitative precision.",
        "is_optional": "True",
    },
    {
        "code": "outlier_length",
        "goal": "Length: Optimal range 7–30 amino acids.",
        "rationale": "Shorter peptides are often non-unique and fragment poorly. Longer peptides ionize inefficiently. This range provides optimal MS detectability.",
        "is_optional": "True",
    },
    {
        "code": "outlier_hydrophobicity",
        "goal": "Hydrophobicity: Kyte-Doolittle score between 0.5 and 2.0 (9-residue window).",
        "rationale": "Very hydrophobic peptides adhere to columns and ionize inefficiently. Highly hydrophilic peptides elute too quickly, reducing detectability.",
        "is_optional": "True",
    },
    {
        "code": "outlier_charge_state",
        "goal": "Charge State: Favor 2+ or 3+ ions.",
        "rationale": "Other charge states often fragment less predictably, decreasing identification reliability.",
        "is_optional": "True",
    },
    {
        "code": "outlier_pi",
        "goal": "Isoelectric Point(pI): Select peptides with pI between 4 and 9.",
        "rationale": "Peptides in this range reliably produce clean LC peaks, stable charge states, and informative MS/MS spectra under acidic RP-LC-ESI conditions.",
        "is_optional": "True",
    },
    {
        "code": "contains_long_homopolymeric_stretch",
        "goal": "Homopolymeric Stretch: Avoid sequences with 3+ consecutive identical residues.",
        "rationale": "Homopolymeric sequences produce weak, uninformative fragmentation spectra, reducing identification confidence.",
        "is_optional": "True",
    },
    {
        "code": "lacking_flanking_amino_acids",
        "goal": "Flanking Amino Acids: Require at least 6 residues on both sides of the cleavage site.",
        "rationale": "Improves trypsin accessibility and digestion efficiency, producing more consistent peptide generation.",
        "is_optional": "True",
    },
    {
        "code": "contains_cysteine",
        "goal": "Cysteine: Avoid cysteine containing peptides.",
        "rationale": "Cysteine requires alkylation; incomplete or over-alkylation creates heterogeneous populations, reducing quantitative reliability.",
        "is_optional": "True",
    },
]


def upgrade() -> None:
    """Add is_optional column and update all criteria rows from NEW_CRITERIA_DATA (by rank)."""
    # 1) Add column, but ignore 'duplicate column' if it already exists
    try:
        op.add_column(
            "criteria",
            sa.Column(
                "is_optional",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),
        )
    except OperationalError as e:
        # MySQL duplicate-column error 1060 → column already exists; safe to ignore
        msg = str(getattr(e, "orig", e))
        if "1060" not in msg and "Duplicate column name 'is_optional'" not in msg:
            raise

    # 2) Then update all rows by rank
    conn = op.get_bind()
    for idx, row in enumerate(NEW_CRITERIA_DATA):
        rank = idx + 1
        is_optional = row["is_optional"] == "True"
        conn.execute(
            sa.text(
                "UPDATE criteria "
                "SET `goal` = :goal, `rationale` = :rationale, `is_optional` = :is_optional "
                "WHERE `rank` = :rank"
            ),
            {
                "rank": rank,
                "goal": row["goal"],
                "rationale": row["rationale"],
                "is_optional": is_optional,
            },
        )


def downgrade() -> None:
    """Remove is_optional column from criteria table."""
    op.drop_column("criteria", "is_optional")
