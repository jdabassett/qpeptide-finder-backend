# classes for protein digest job processing
from pydantic import BaseModel, Field

from app.enums import CriteriaEnum


class PeptideDomain(BaseModel):
    """Data transfer object for peptide during digest processing."""

    sequence: str
    position: int
    criteria: list["CriteriaEnum"] = Field(default_factory=list)

    @property
    def length(self) -> int:
        return len(self.sequence)

    def add_criteria(self, criteria: "CriteriaEnum") -> None:
        if criteria not in self.criteria:
            self.criteria.append(criteria)
