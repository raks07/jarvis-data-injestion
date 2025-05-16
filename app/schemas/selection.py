from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class DocumentSelectionRequest(BaseModel):
    """
    Schema for document selection request.
    """
    user_id: str = Field(..., description="ID of the user")
    document_ids: List[str] = Field(..., description="List of document IDs to include in the search context")

class DocumentSelectionResponse(BaseModel):
    """
    Schema for document selection response.
    """
    user_id: str
    document_ids: List[str]
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True
