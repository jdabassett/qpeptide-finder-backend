from enum import Enum as PyEnum


class ProteaseEnum(str, PyEnum):
    TRYPSIN = "trypsin"
    CHYMOTRYPSIN = "chymotrypsin"
    PEPSIN = "pepsin"
    ELASTASE = "elastase"
    PROTEINASE_K = "proteinase_k"
    THERMOLYSIN = "thermolysin"
