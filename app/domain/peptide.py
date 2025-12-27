# classes for protein digest job processing
from pydantic import BaseModel, Field

from app.enums import AminoAcidEnum, CriteriaEnum
from app.enums.enums import ChargeStateEnum


class PeptideDomain(BaseModel):
    """Data transfer object for peptide during digest processing."""

    position: int
    sequence: list[AminoAcidEnum] = Field(default_factory=list)
    criteria: list["CriteriaEnum"] = Field(default_factory=list)
    pI: float | None = Field(default=None)

    @property
    def length(self) -> int:
        return len(self.sequence)

    @property
    def sequence_as_str(self) -> str:
        """Convert protein sequence into a string."""
        return "".join([aa.value for aa in self.sequence])

    def add_criteria(self, criteria: "CriteriaEnum") -> None:
        if criteria not in self.criteria:
            self.criteria.append(criteria)

    def get_pI(self) -> float:
        """Get pI value, calculating if not already set."""
        if self.pI is not None:
            return self.pI
        self.pI = self.calculate_pI()
        return self.pI

    def net_charge(self, pH: float):
        """Calculate net charge of peptide at a given pH."""
        n_term_charge = 1 / (1 + 10 ** (pH - 8.0))
        c_term_charge = -1 / (1 + 10 ** (3.55 - pH))

        pos_charge = 0
        neg_charge = 0

        for aa in self.sequence:
            if aa.charge_state == ChargeStateEnum.POSITIVE:
                pos_charge += 1 / (1 + 10 ** (pH - aa.pKa))
            elif aa.charge_state == ChargeStateEnum.NEGATIVE:
                neg_charge += -1 / (1 + 10 ** (aa.pKa - pH))

        return n_term_charge + c_term_charge + pos_charge + neg_charge

    def calculate_pI(self, precision: float = 0.1):
        """Estimate the isoelectric point (pI) of a peptide."""
        low, high = 0.0, 14.0
        while (high - low) > precision:
            mid = (low + high) / 2
            if self.net_charge(mid) > 0:
                low = mid
            else:
                high = mid

        self.pI = (low + high) / 2
        return self.pI
