from pydantic import BaseModel, EmailStr, Field, field_validator

from app.enums import AminoAcidEnum
from app.enums.proteases import ProteaseEnum, ProteaseOrderingEnum


class ProteinRequest(BaseModel):
    """Schema for protein data in digest job request."""

    uni_prot_accession_number: str | None = Field(
        None, max_length=20, description="UniProt accession number"
    )
    ncbi_protein_accession: str | None = Field(
        None, max_length=50, description="NCBI protein accession number"
    )
    protein_name: str = Field(
        ..., min_length=1, max_length=255, description="Protein name"
    )
    sequence: list[AminoAcidEnum] = Field(
        ..., min_length=1, max_length=2000, description="Protein sequence"
    )

    @field_validator("sequence", mode="before")
    @classmethod
    def validate_sequence(cls, v) -> list[AminoAcidEnum]:
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

        return [AminoAcidEnum(aa) for aa in cleaned]


class DigestRequest(BaseModel):
    """Schema for digest configuration in digest job request."""

    proteases: list[ProteaseEnum] = Field(
        ..., min_length=1, description="List of proteases to use for digestion"
    )
    ordering: ProteaseOrderingEnum = Field(
        ..., description="Ordering strategy for protease application"
    )

    @field_validator("proteases", mode="before")
    @classmethod
    def validate_proteases(cls, v) -> list[ProteaseEnum]:
        """Validate that all proteases are valid enum values."""
        if not isinstance(v, list):
            raise ValueError("Proteases must be a list")
        if len(v) < 1:
            raise ValueError("At least one protease per digest")
        if len(v) > 3:
            raise ValueError("No more than 3 proteases per digest")

        unique_proteases = set(v)
        if len(unique_proteases) != len(v):
            raise ValueError("Duplicate proteases are not allowed")

        try:
            return [ProteaseEnum(protease) for protease in v]
        except ValueError as e:
            raise ValueError(f"Invalid protease provided: {e}") from None


class DigestJobRequest(BaseModel):
    """Schema for creating a new digest job request."""

    user_email: EmailStr = Field(..., description="User email address")
    protein: ProteinRequest = Field(..., description="Protein information")
    digest: DigestRequest = Field(..., description="Digest configuration")

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_email": "user@example.com",
                "protein": {
                    "uni_prot_accession_number": "P12345",
                    "ncbi_protein_accession": None,
                    "protein_name": "Example Protein",
                    "sequence": "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVVHSLAKWKRQTLGQHDFSAGEGLYTHMKALRPDEDRLSPLHSVYVDQWDWYVYSQIAEEYEVHSSFLK",
                },
                "digest": {
                    "proteases": ["trypsin", "chymotrypsin"],
                    "ordering": "ordered",
                },
            }
        }
    }
