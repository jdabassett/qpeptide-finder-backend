# from datetime import datetime
# from typing import List

# from pydantic import BaseModel, ConfigDict, Field

# from app.enums.digest_statuses import DigestStatusEnum
# from app.enums.proteases import ProteaseEnum

# TODO this needs work
# class DigestProteaseCreate(BaseModel):
#     """Schema for creating a digest protease entry."""

#     protease: ProteaseEnum = Field(..., description="Protease type")
#     order: int = Field(..., ge=0, description="Order of protease application (0, 1, 2, ...)")


# class DigestCreate(BaseModel):
#     """Schema for creating a new digest request."""

#     proteases: List[DigestProteaseCreate] = Field(..., min_length=1, description="List of proteases in order")
#     user_id: str = Field(..., description="User ID")
#     protein_id: str = Field(..., description="Protein ID")


# class DigestProteaseResponse(BaseModel):
#     """Schema for digest protease response."""

#     id: str
#     protease: ProteaseEnum
#     order: int
#     created_at: datetime
#     updated_at: datetime

#     model_config = ConfigDict(from_attributes=True)


# class DigestResponse(BaseModel):
#     """Schema for digest response."""

#     id: str
#     status: DigestStatusEnum
#     user_id: str
#     protein_id: str
#     proteases: List[DigestProteaseResponse]
#     created_at: datetime
#     updated_at: datetime

#     model_config = ConfigDict(from_attributes=True)
