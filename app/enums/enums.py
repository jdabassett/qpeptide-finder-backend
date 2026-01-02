from enum import Enum
from functools import lru_cache


class ChargeStateEnum(str, Enum):
    """Support amino acid charge state evaluation."""

    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"


class CleavageStatusEnum(str, Enum):
    """Support amino acid site cleavage status."""

    NEUTRAL = "neutral"
    MISSED = "missed"
    CLEAVAGE = "cleavage"


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
                return {AminoAcidEnum.LYSINE, AminoAcidEnum.ARGININE}
            case _:
                raise NotImplementedError(
                    f"Cleave aa set for {self.value} are not yet implemented."
                )

    @property
    def inhibitor_aas(self) -> set[str]:
        """Returns set of amino acid strings that would inhibit protease cleavage."""
        match self:
            case ProteaseEnum.TRYPSIN:
                return {AminoAcidEnum.PROLINE}
            case _:
                raise NotImplementedError(
                    f"Inhibit aa set for {self.value} are not yet implemented."
                )

    def site_status(
        self, sequence: list["AminoAcidEnum"], position: int
    ) -> CleavageStatusEnum:
        """
        Determine if this protease would cut after the given position.
        """
        if position < 0 or position >= len(sequence):
            raise IndexError(
                f"Position {position} is out of bounds the given sequence."
            )

        current_aa = sequence[position]

        match self:
            case ProteaseEnum.TRYPSIN:
                if current_aa not in self.cleavage_aas:
                    return CleavageStatusEnum.NEUTRAL

                next_aa = (
                    sequence[position + 1] if position + 1 < len(sequence) else None
                )
                if next_aa in self.inhibitor_aas:
                    return CleavageStatusEnum.MISSED

                return CleavageStatusEnum.CLEAVAGE

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

    @property
    def pKa(self) -> float:
        """Return acid dissociation constant for an amino acids side group."""
        pka_values = {
            AminoAcidEnum.LYSINE: 10.53,
            AminoAcidEnum.ARGININE: 12.48,
            AminoAcidEnum.HISTIDINE: 6.0,
            AminoAcidEnum.ASPARTIC_ACID: 3.86,
            AminoAcidEnum.GLUTAMIC_ACID: 4.25,
            AminoAcidEnum.CYSTEINE: 8.33,
            AminoAcidEnum.TYROSINE: 10.07,
        }
        if self not in pka_values:
            raise ValueError(f"pKa for {self} is undefined.")
        return pka_values[self]

    def n_terminal_pKa(self) -> float:
        """
        Return N-terminal pKa contribution for this amino acid
        when it is the N-terminal residue of a peptide.
        """
        DEFAULT_N_TERMINAL_PKA = 8.2
        N_TERMINAL_PKA_OFFSETS = {
            AminoAcidEnum.PROLINE: -1.0,
            AminoAcidEnum.GLYCINE: +0.1,
            AminoAcidEnum.SERINE: +0.1,
            AminoAcidEnum.THREONINE: +0.1,
            AminoAcidEnum.ASPARTIC_ACID: -0.2,
            AminoAcidEnum.GLUTAMIC_ACID: -0.2,
        }
        base_pka = DEFAULT_N_TERMINAL_PKA
        offset = N_TERMINAL_PKA_OFFSETS.get(self, 0.0)
        return base_pka + offset

    def c_terminal_pKa(self) -> float:
        """
        Return C-terminal pKa contribution for this amino acid
        when it is the C-terminal residue of a peptide.
        """
        DEFAULT_C_TERMINAL_PKA = 3.1
        C_TERMINAL_PKA_OFFSETS = {
            AminoAcidEnum.ASPARTIC_ACID: +0.2,
            AminoAcidEnum.GLUTAMIC_ACID: +0.2,
            AminoAcidEnum.LYSINE: -0.1,
            AminoAcidEnum.ARGININE: -0.1,
        }
        base_pka = DEFAULT_C_TERMINAL_PKA
        offset = C_TERMINAL_PKA_OFFSETS.get(self, 0.0)
        return base_pka + offset

    @property
    def kd_score(self) -> float:
        """Return Kyte-Doolittle max average hydrophobicity score for given amino acid."""
        kd_scores = {
            AminoAcidEnum.ALANINE: 1.8,
            AminoAcidEnum.CYSTEINE: 2.5,
            AminoAcidEnum.ASPARTIC_ACID: -3.5,
            AminoAcidEnum.GLUTAMIC_ACID: -3.5,
            AminoAcidEnum.PHENYLALANINE: 2.8,
            AminoAcidEnum.GLYCINE: -0.4,
            AminoAcidEnum.HISTIDINE: -3.2,
            AminoAcidEnum.ISOLEUCINE: 4.5,
            AminoAcidEnum.LYSINE: -3.9,
            AminoAcidEnum.LEUCINE: 3.8,
            AminoAcidEnum.METHIONINE: 1.9,
            AminoAcidEnum.ASPARAGINE: -3.5,
            AminoAcidEnum.PROLINE: -1.6,
            AminoAcidEnum.GLUTAMINE: -3.5,
            AminoAcidEnum.ARGININE: -4.5,
            AminoAcidEnum.SERINE: -0.8,
            AminoAcidEnum.THREONINE: -0.7,
            AminoAcidEnum.VALINE: 4.2,
            AminoAcidEnum.TRYPTOPHAN: -0.9,
            AminoAcidEnum.TYROSINE: -1.3,
        }
        if self not in kd_scores:
            raise ValueError(f"Kyte-Doolittle score for {self} is undefined.")
        return kd_scores[self]

    @staticmethod
    @lru_cache
    def valid_values() -> set[str]:
        """Return cached set of all valid amino acid single-letter codes."""
        return {aa.value for aa in AminoAcidEnum}

    @staticmethod
    def is_valid_amino_acid(value: str) -> bool:
        return value.upper() in AminoAcidEnum.valid_values()

    @classmethod
    def to_amino_acids(cls, sequence: str) -> list["AminoAcidEnum"]:
        """Convert to enum list."""
        return [AminoAcidEnum(char) for char in sequence]

    def charge_state(self) -> ChargeStateEnum:
        """Evaluate if amino acid is positive, negative, or neutrally charged."""
        if self in [
            AminoAcidEnum.HISTIDINE,
            AminoAcidEnum.LYSINE,
            AminoAcidEnum.ARGININE,
        ]:
            return ChargeStateEnum.POSITIVE
        elif self in [
            AminoAcidEnum.ASPARTIC_ACID,
            AminoAcidEnum.GLUTAMIC_ACID,
            AminoAcidEnum.CYSTEINE,
            AminoAcidEnum.TYROSINE,
        ]:
            return ChargeStateEnum.NEGATIVE
        else:
            return ChargeStateEnum.NEUTRAL


class CriteriaEnum(str, Enum):
    """All supported qpeptide criteria."""

    NOT_UNIQUE = "not_unique"
    CONTAINS_MISSED_CLEAVAGES = "contains_missed_cleavages"
    HAS_FLANKING_CUT_SITES = "has_flanking_cut_sites"
    OUTLIER_LENGTH = "outlier_length"
    CONTAINS_N_TERMINAL_GLUTAMINE_MOTIF = "contains_n_terminal_glutamine_motif"
    CONTAINS_ASPARAGINE_GLYCINE_MOTIF = "contains_asparagine_glycine_motif"
    CONTAINS_ASPARTIC_PROLINE_MOTIF = "contains_aspartic_proline_motif"
    CONTAINS_METHIONINE = "contains_methionine"
    OUTLIER_HYDROPHOBICITY = "outlier_hydrophobicity"
    OUTLIER_CHARGE_STATE = "outlier_charge_state"
    OUTLIER_PI = "outlier_pi"
    CONTAINS_LONG_HOMOPOLYMERIC_STRETCH = "contains_long_homopolymeric_stretch"
    LACKING_FLANKING_AMINO_ACIDS = "lacking_flanking_amino_acids"
    CONTAINS_CYSTEINE = "contains_cysteine"

    @classmethod
    def order_least_to_most_important(cls) -> list["CriteriaEnum"]:
        """Returns list of CriteriaEnums from least to most important."""
        return [
            CriteriaEnum.NOT_UNIQUE,
            CriteriaEnum.HAS_FLANKING_CUT_SITES,
            CriteriaEnum.CONTAINS_MISSED_CLEAVAGES,
            CriteriaEnum.CONTAINS_N_TERMINAL_GLUTAMINE_MOTIF,
            CriteriaEnum.CONTAINS_ASPARAGINE_GLYCINE_MOTIF,
            CriteriaEnum.CONTAINS_ASPARTIC_PROLINE_MOTIF,
            CriteriaEnum.CONTAINS_METHIONINE,
            CriteriaEnum.OUTLIER_LENGTH,
            CriteriaEnum.OUTLIER_HYDROPHOBICITY,
            CriteriaEnum.OUTLIER_CHARGE_STATE,
            CriteriaEnum.OUTLIER_PI,
            CriteriaEnum.CONTAINS_LONG_HOMOPOLYMERIC_STRETCH,
            CriteriaEnum.LACKING_FLANKING_AMINO_ACIDS,
            CriteriaEnum.CONTAINS_CYSTEINE,
        ]

    @classmethod
    @lru_cache
    def criteria_weights(cls) -> dict["CriteriaEnum", float]:
        """
        Calculate weights for each criteria enum based on importance.
        """

        ordered_enums = cls.order_least_to_most_important()
        n = len(ordered_enums)
        weights: dict[CriteriaEnum, float] = {}

        for i, enum in enumerate(ordered_enums):
            weights[enum] = 2 ** (n - 1 - i)

        return weights
