"""add_new_criteria

Revision ID: 718ebad503d2
Revises: a48ffd902416
Create Date: 2025-12-27 19:12:35.174435

"""

import uuid
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op  # type: ignore[attr-defined]

# revision identifiers, used by Alembic.
revision: str = "718ebad503d2"
down_revision: str | Sequence[str] | None = "a48ffd902416"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Old criteria codes to remove
OLD_CRITERIA_VALUES = [
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
]

# New criteria enum values to add
NEW_CRITERIA_VALUES = [
    "not_unique",
    "has_flanking_cut_sites",
    "contains_missed_cleavages",
    "outlier_length",
    "lacking_flanking_amino_acids",
    "outlier_hydrophobicity",
    "outlier_charge_state",
    "outlier_pi",
    "contains_asparagine_glycine_motif",
    "contains_aspartic_proline_motif",
    "contains_long_homopolymeric_stretch",
    "contains_n_terminal_glutamine_motif",
    "contains_methionine",
    "contains_cysteine",
]

NEW_CRITERIA_ENUM = sa.Enum(
    *NEW_CRITERIA_VALUES,
    name="criteria_enum",
    native_enum=False,
    length=50,
)

# New criteria data to insert (ordered to match NEW_CRITERIA_VALUES)
NEW_CRITERIA_DATA = [
    {
        "code": "not_unique",
        "goal": "The peptide must unique within the target protein.",
        "rationale": "Ensures that the measured signal reflects only one site from the protein of interest.",
    },
    {
        "code": "has_flanking_cut_sites",
        "goal": "Do not choose peptides immediately adjacent to cleavage motifs (e.g., K, R, KP, RP).",
        "rationale": "Proximity to other cut sites can reduce digestion efficiency, leading to missed cleavages or semi-tryptic peptides.",
    },
    {
        "code": "contains_missed_cleavages",
        "goal": "Ensure the peptide is completely generated during digestion.",
        "rationale": "Missed cleavage sites (e.g., Lys-Pro, Arg-Pro) produce heterogeneous peptide populations, reducing reproducibility and quantitative accuracy.",
    },
    {
        "code": "outlier_length",
        "goal": "7–30 amino acids.",
        "rationale": "Peptides shorter than 7 residues are often not unique and fragment poorly. Peptides longer than 30 residues ionize inefficiently and fragment unpredictably. This range provides optimal MS detectability and sequence coverage.",
    },
    {
        "code": "lacking_flanking_amino_acids",
        "goal": "Prioritizes peptides with at least 6 residues on both sides of the cleavage site in the intact protein.",
        "rationale": "Improves trypsin accessibility and digestion efficiency, producing more consistent peptide generation.",
    },
    {
        "code": "outlier_hydrophobicity",
        "goal": "Exclude peptides with extreme hydrophobicity values (too hydrophobic or too hydrophilic).",
        "rationale": "Very hydrophobic peptides adhere to columns, elute poorly, and ionize inefficiently, lowering MS signal. Highly hydrophilic peptides are too soluble and won't bind to the column long enough to elute in the retention curve, also reducing detectability.",
    },
    {
        "code": "outlier_charge_state",
        "goal": "Favor peptides that form 2+ or 3+ ions.",
        "rationale": "Very basic peptides (4+ or higher) or neutral peptides (1+) fragment less predictably, decreasing identification reliability.",
    },
    {
        "code": "outlier_pi",
        "goal": "Select peptides with a pI between 4 and 9.",
        "rationale": "Peptides with pI between 4 and 9 reliably produce clean LC peaks, stable charge states, and informative MS/MS spectra under acidic RP-LC-ESI conditions.",
    },
    {
        "code": "contains_asparagine_glycine_motif",
        "goal": "Exclude Asparagine–Glycine sequences.",
        "rationale": "N–G motifs deamidate rapidly post-digestion, producing mixed modified/unmodified peptides that complicate quantitation.",
    },
    {
        "code": "contains_aspartic_proline_motif",
        "goal": "Exclude Aspartic–Proline sequences.",
        "rationale": "Aspartic acid followed by proline causes preferential gas-phase cleavage, producing non-informative fragmentation spectra and reducing identification confidence.",
    },
    {
        "code": "contains_long_homopolymeric_stretch",
        "goal": "Avoid homopolymeric sequences.",
        "rationale": "Homopolymeric sequences produce weak, uninformative fragmentation spectra, reducing confidence in identification.",
    },
    {
        "code": "contains_n_terminal_glutamine_motif",
        "goal": "Exclude peptides with N-terminal glutamine.",
        "rationale": "N-terminal glutamine cyclizes to pyroglutamate or converts to glutamate post-digestion, producing multiple forms that complicate quantification.",
    },
    {
        "code": "contains_methionine",
        "goal": "Avoid methionine-containing peptides.",
        "rationale": "Methionine oxidizes readily during sample handling, generating multiple peptide species with different masses and retention times, reducing quantitative precision.",
    },
    {
        "code": "contains_cysteine",
        "goal": "Minimize peptides containing cysteine.",
        "rationale": "Cysteine requires alkylation; incomplete or over-alkylation creates heterogeneous populations, reducing quantitative reliability.",
    },
]


def upgrade() -> None:
    bind = op.get_bind()

    op.execute(sa.text("DELETE FROM criteria"))

    try:
        op.execute(sa.text("ALTER TABLE criteria DROP CHECK criteria_code_check"))
    except Exception:
        # Constraint may not exist depending on previous migrations
        pass

    NEW_CRITERIA_ENUM.create(bind, checkfirst=True)

    criteria_table = sa.table(
        "criteria",
        sa.column("id", sa.String),
        sa.column("code", sa.String),
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
            for idx, item in enumerate(NEW_CRITERIA_DATA)
        ],
    )


def downgrade() -> None:
    # This migration is destructive and intentionally irreversible
    raise RuntimeError("Downgrade not supported for criteria replacement migration")
