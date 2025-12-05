from enum import Enum as PyEnum

from pydantic import BaseModel


class ProteaseEnum(str, PyEnum):
    TRYPSIN = "trypsin"
    CHYMOTRYPSIN = "chymotrypsin"
    ELASTASE = "elastase"
    PROTEINASE_K = "proteinase_k"
    THERMOLYSIN = "thermolysin"


class OrderEnum(str, PyEnum):
    FIRST = "1"
    SECOND = "2"
    THIRD = "3"

    @staticmethod
    def valid_orderings() -> set[str]:
        """Return static set of valid sorted orders as strings."""
        return {"1", "11", "12", "111", "112", "123"}


class ProteaseAction(BaseModel):
    protease: ProteaseEnum
    order: OrderEnum
