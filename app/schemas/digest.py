from collections import Counter

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.enums import AminoAcidEnum
from app.enums.proteases import OrderEnum, ProteaseAction


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

    def sequence_to_str(self) -> str:
        """Convert list of AminoAcidEnums to str."""
        return "".join([aa.value for aa in self.sequence])


class DigestRequest(BaseModel):
    """Schema for digest configuration in digest job request."""

    proteases: list[ProteaseAction] = Field(..., min_length=1, max_length=3)

    @field_validator("proteases", mode="after")
    @classmethod
    def validate_proteases(cls, v) -> list[ProteaseAction]:
        """Validates there there are no duplicate proteases and that the order is accurate."""
        sorted_proteases: list[ProteaseAction] = sorted(v, key=lambda x: int(x.order))
        proteases_counter: Counter[str] = Counter(
            [each.protease.value for each in sorted_proteases]
        )
        if any(count > 1 for count in proteases_counter.values()):
            duplicate_proteases: list[str] = [
                protease for protease, count in proteases_counter.items() if count > 1
            ]
            raise ValueError(
                f"Duplicate proteases per digest not allowed: {', '.join(duplicate_proteases)}"
            )

        ordering: str = "".join(sorted([each.order.value for each in sorted_proteases]))
        if ordering not in OrderEnum.valid_orderings():
            current_ordering: str = ", ".join(
                [
                    f"{each.protease.value}:{each.order.value}"
                    for each in sorted_proteases
                ]
            )
            raise ValueError(
                f"Protease must be in a valid ordering. Current Ordering: {current_ordering}"
            )

        return sorted_proteases


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
                    "proteases": [
                        {"protease": "trypsin", "order": "1"},
                        {"protease": "chymotrypsin", "order": "2"},
                    ]
                },
            }
        }
    }


class DigestJobResponse(BaseModel):
    """Schema for digest job creation response."""

    digest_id: str = Field(..., description="ID of the created digest job")
