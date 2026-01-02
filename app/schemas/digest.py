from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.enums import AminoAcidEnum, ProteaseEnum
from app.models import Criteria, Peptide


class DigestJobRequest(BaseModel):
    """Schema for creating a new digest job request."""

    user_id: str = Field(..., description="User's id")
    protease: ProteaseEnum = Field(..., description="Protease used for digest")

    protein_name: str | None = Field(None, max_length=255, description="Protein name")
    sequence: str = Field(
        ..., min_length=1, max_length=3000, description="Protein sequence"
    )

    @field_validator("sequence", mode="before")
    @classmethod
    def validate_sequence(cls, v) -> str:
        """Validate that sequence contains only valid amino acid characters."""
        if not isinstance(v, str):
            raise TypeError("Sequence must be a string")

        cleaned = v.replace(" ", "").replace("\n", "").upper()
        if not cleaned:
            raise ValueError("Sequence cannot be empty")

        invalid_chars = [
            aa for aa in cleaned if not AminoAcidEnum.is_valid_amino_acid(aa)
        ]

        if invalid_chars:
            raise ValueError(
                f"Invalid amino acid(s) in sequence: {', '.join(sorted(set(invalid_chars)))}."
            )

        return cleaned

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "fc502bbe-5a1b-4f99-b716-e1970db2aef7",
                "protein_name": "Example Protein",
                "protein_sequence": "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVVHSLAKWKRQTLGQHDFSAGEGLYTHMKALRPDEDRLSPLHSVYVDQWDWYVYSQIAEEYEVHSSFLK",
                "protease": "trypsin",
            }
        }
    }


class DigestJobResponse(BaseModel):
    """Schema for digest job creation response."""

    digest_id: str = Field(..., description="ID of the created digest job")


class DigestListRequest(BaseModel):
    """Schema for requesting digests by user id."""

    user_id: str = Field(..., description="User id")

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "fc502bbe-5a1b-4f99-b716-e1970db2aef7",
            }
        }
    }


class DigestResponse(BaseModel):
    """Schema for digest response (without peptides or peptide_criteria)."""

    id: str = Field(..., description="Digest ID")
    status: str = Field(..., description="Digest status")
    user_id: str = Field(..., description="User ID")
    protease: str = Field(..., description="Protease used")
    protein_name: str | None = Field(None, description="Protein name")
    sequence: str = Field(..., description="Protein sequence")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class DigestListResponse(BaseModel):
    """Schema for list of digests response."""

    digests: list[DigestResponse] = Field(..., description="List of digests")


class CriteriaResponse(BaseModel):
    """Schema for criteria response."""

    code: str = Field(..., description="Criteria code (enum value)")
    goal: str = Field(..., description="Goal of the criteria")
    rationale: str = Field(..., description="Rationale for the criteria")
    rank: int = Field(..., description="Rank/priority of the criteria")

    model_config = ConfigDict(from_attributes=True)


class PeptideResponse(BaseModel):
    """Schema for peptide response with criteria codes."""

    id: str = Field(..., description="Peptide ID")
    sequence: str = Field(..., description="Peptide sequence")
    position: int = Field(..., description="Position in the protein")
    pi: float | None = Field(None, description="Isoelectric point")
    charge_state: int | None = Field(None, description="Charge state")
    max_kd_score: float | None = Field(None, description="Max Kyte-Doolittle score")
    rank: int = Field(..., description="Peptide rank (lower is better)")
    criteria_ranks: list[int] = Field(
        default_factory=list, description="List of criteria ranks this peptide matches"
    )

    model_config = ConfigDict(from_attributes=True)


class DigestPeptidesResponse(BaseModel):
    """Schema for digest peptides response."""

    digest_id: str = Field(..., description="Digest ID")
    peptides: list[PeptideResponse] = Field(
        ..., description="List of peptides ordered by rank"
    )
    criteria: list[CriteriaResponse] = Field(
        ..., description="List of all available criteria"
    )

    @classmethod
    def from_peptides(
        cls,
        digest_id: str,
        peptides: list["Peptide"],  # type: ignore
        all_criteria: list["Criteria"],  # type: ignore
    ) -> "DigestPeptidesResponse":
        """
        Create a DigestPeptidesResponse from a list of peptide records.

        Args:
            digest_id: The digest ID
            peptides: List of Peptide model instances
            all_criteria: List of all Criteria model instances

        Returns:
            DigestPeptidesResponse instance
        """
        peptide_responses = []
        for peptide in peptides:
            criteria_ranks = [pc.criteria.rank for pc in peptide.criteria]
            criteria_ranks.sort()

            peptide_responses.append(
                PeptideResponse(
                    id=peptide.id,
                    sequence=peptide.sequence,
                    position=peptide.position,
                    pi=peptide.pi,
                    charge_state=peptide.charge_state,
                    max_kd_score=peptide.max_kd_score,
                    rank=peptide.rank,
                    criteria_ranks=criteria_ranks,
                )
            )

        return cls(
            digest_id=digest_id,
            peptides=peptide_responses,
            criteria=[CriteriaResponse.model_validate(c) for c in all_criteria],
        )
