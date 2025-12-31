from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.enums import AminoAcidEnum, ProteaseEnum


class DigestJobRequest(BaseModel):
    """Schema for creating a new digest job request."""

    user_email: EmailStr = Field(..., description="User email address")
    protease: ProteaseEnum = Field(..., description="Protease used for digest")

    protein_name: str = Field(
        ..., min_length=1, max_length=255, description="Protein name"
    )
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
                "user_email": "user@example.com",
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
    """Schema for requesting digests by user email."""

    email: EmailStr = Field(..., description="User email address")

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
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
