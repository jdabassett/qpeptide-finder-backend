# classes for protein digest job processing
from pydantic import BaseModel, Field

from app.core import settings
from app.enums import AminoAcidEnum, CriteriaEnum
from app.enums.enums import ChargeStateEnum


class PeptideDomain(BaseModel):
    """Data transfer object for peptide during digest processing."""

    position: int
    sequence: list[AminoAcidEnum] = Field(default_factory=list)
    criteria: list["CriteriaEnum"] = Field(default_factory=list)
    pI: float | None = Field(default=None)
    charge_state: int | None = Field(default=None)
    max_kd_score: float | None = Field(default=None)

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

    def _net_charge(self, pH: float):
        """Calculate net charge of peptide at a given pH."""
        n_term_aa: AminoAcidEnum = self.sequence[0]
        c_term_aa: AminoAcidEnum = self.sequence[-1]

        n_term_charge: float = 1 / (1 + 10 ** (pH - n_term_aa.n_terminal_pKa()))
        c_term_charge: float = -1 / (1 + 10 ** (c_term_aa.c_terminal_pKa() - pH))

        pos_charge: float = 0.0
        neg_charge: float = 0.0

        for i, aa in enumerate(self.sequence):
            if aa.charge_state() == ChargeStateEnum.POSITIVE:
                weight = 0.9 if i in (0, self.length - 1) else 1.0
                pos_charge += weight / (1 + 10 ** (pH - aa.pKa))
            elif aa.charge_state() == ChargeStateEnum.NEGATIVE:
                neg_charge += -1 / (1 + 10 ** (aa.pKa - pH))

        return n_term_charge + c_term_charge + pos_charge + neg_charge

    def calculate_pI(self, precision: float = 0.05):
        """Estimate the isoelectric point (pI) of a peptide."""
        low, high = 0.0, 14.0
        while (high - low) > precision:
            mid = (low + high) / 2
            if self._net_charge(mid) > 0:
                low = mid
            else:
                high = mid

        self.pI = round((low + high) / 2, 2)
        return self.pI

    def charge_state_in_formic_acid(self) -> int:
        """Predict charge state (as integer) at pH 2.3 (formic acid)."""
        if self.charge_state is not None:
            return self.charge_state
        self.charge_state = round(self._net_charge(2.3))
        return self.charge_state

    def _calculate_max_kyte_dolittle_score_over_sliding_window(self) -> float:
        """Calculate the max Kyte-Doolittle over the Max Hydrophobicity Sliding Window."""
        kd_values = [aa.kd_score for aa in self.sequence]
        window_size = settings.MAX_HYDROPHOBICITY_WINDOW

        if len(kd_values) <= window_size:
            self.max_kd_score = sum(kd_values) / len(kd_values)
            return self.max_kd_score

        max_score = float("-inf")

        for i in range(len(kd_values) - window_size + 1):
            window_avg = sum(kd_values[i : i + window_size]) / window_size
            max_score = max(window_avg, max_score)

        self.max_kd_score = round(max_score, 2)
        return self.max_kd_score

    def max_kyte_dolittle_score_over_sliding_window(self) -> float:
        """Return max Kyte-Dolittle Hydrophobicity score over a sliding window."""
        if self.max_kd_score is not None:
            return self.max_kd_score

        if not self.sequence:
            self.max_kd_score = 0.00
            return self.max_kd_score

        self.max_kd_score = (
            self._calculate_max_kyte_dolittle_score_over_sliding_window()
        )
        return self.max_kd_score
