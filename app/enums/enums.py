from enum import Enum
from functools import lru_cache


class ProteaseEnum(str, Enum):
    """Supported proteases."""

    TRYPSIN = "trypsin"
    # CHYMOTRYPSIN = "chymotrypsin"
    # ELASTASE = "elastase"
    # PROTEINASE_K = "proteinase_k"
    # THERMOLYSIN = "thermolysin"
    # LYS_C = "lys_c"
    # LYS_N = "lys_n"
    # ARG_C = "arg_c"
    # GLU_C = "glu_c"
    # ASP_N = "asp_n"
    # PEPSIN = "pepsin"
    # SUBTILISIN = "subtilisin"
    # PROLINE_ENDOPEPTIDASE = "proline_endopeptidase"

    @property
    def cleavage_aas(self) -> set[str]:
        """Returns set of amino acid strings that a given protease would cleave at."""
        match self:
            case ProteaseEnum.TRYPSIN:
                return {AminoAcidEnum.LYSINE.value, AminoAcidEnum.ARGININE.value}
            case _:
                raise NotImplementedError(
                    f"Cleave aa set for {self.value} are not yet implemented."
                )

    @property
    def inhibitor_aas(self) -> set[str]:
        """Returns set of amino acid strings that would inhibit protease cleavage."""
        match self:
            case ProteaseEnum.TRYPSIN:
                return {AminoAcidEnum.PROLINE.value}
            case _:
                raise NotImplementedError(
                    f"Inhibit aa set for {self.value} are not yet implemented."
                )

    def would_cut_at(self, sequence: str, position: int) -> bool:
        """
        Determine if this protease would cut after the given position.

        Returns:
            True if the protease would cut after this position, False otherwise
        """
        if position < 0 or position >= len(sequence):
            raise IndexError(
                f"Position {position} is out of bounds for sequence of length {len(sequence)}"
            )

        current_aa = sequence[position]

        match self:
            case ProteaseEnum.TRYPSIN:
                if current_aa not in self.cleavage_aas:
                    return False

                next_aa = (
                    sequence[position + 1] if position + 1 < len(sequence) else None
                )
                if next_aa is None:
                    return True

                return next_aa not in self.inhibitor_aas

            case _:
                raise NotImplementedError(
                    f"Cleavage rules for {self.value} are not yet implemented"
                )


class DigestStatusEnum(str, Enum):
    """All supported digestion states"""

    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AminoAcidEnum(str, Enum):
    """All valid amino acids."""

    ALANINE = "A"
    ARGININE = "R"
    ASPARAGINE = "N"
    ASPARTIC_ACID = "D"
    CYSTEINE = "C"
    GLUTAMIC_ACID = "E"
    GLUTAMINE = "Q"
    GLYCINE = "G"
    HISTIDINE = "H"
    ISOLEUCINE = "I"
    LEUCINE = "L"
    LYSINE = "K"
    METHIONINE = "M"
    PHENYLALANINE = "F"
    PROLINE = "P"
    SERINE = "S"
    THREONINE = "T"
    TRYPTOPHAN = "W"
    TYROSINE = "Y"
    VALINE = "V"

    @staticmethod
    @lru_cache(maxsize=1)
    def _valid_values() -> set[str]:
        return {aa.value for aa in AminoAcidEnum}

    @staticmethod
    def is_valid_amino_acid(value: str) -> bool:
        return value.upper() in AminoAcidEnum._valid_values()


class CriteriaEnum(str, Enum):
    """All supported qpeptide criteria."""

    UNIQUE_SEQUENCE = "unique_sequence"
    NO_MISSED_CLEAVAGE = "no_missed_cleavage"
    AVOID_FLANKING_CUT_SITES = "avoid_flanking_cut_sites"
    FLANKING_AMINO_ACIDS = "flanking_amino_acids"
    PEPTIDE_LENGTH = "peptide_length"
    NO_N_TERMINAL_GLUTAMINE = "no_n-terminal_glutamine"
    NO_ASP_PRO_MOTIF = "no_asp_pro_motif"
    NO_ASN_GLY_MOTIF = "no_asn_gly_motif"
    AVOID_METHIONINE = "avoid_methionine"
    AVOID_CYSTEINE = "avoid_cysteine"
    PEPTIDE_PI = "peptide_pi"
    AVOID_PTM_PRONE_RESIDUES = "avoid_ptm_prone_residues"
    AVOID_HIGHLY_HYDROPHOBIC_PEPTIDES = "avoid_highly_hydrophobic_peptides"
    AVOID_LONG_HOMOPOLYMERIC_STRETCHES = "avoid_long_homopolymeric_stretches"
    PREFER_TYPICAL_CHARGE_STATES = "prefer_typical_charge_states"
