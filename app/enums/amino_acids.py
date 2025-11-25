from enum import Enum as PyEnum
from functools import lru_cache


class AminoAcidEnum(str, PyEnum):
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
