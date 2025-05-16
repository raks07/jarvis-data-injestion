from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class IngestStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class DocumentIngest(BaseModel):
    """
    Schema for document ingestion request.
    """
    external_id: str = Field(..., description="External ID of the document from NestJS backend")
    title: str = Field(..., description="Title of the document")
    description: Optional[str] = Field(None, description="Description of the document")
    content: str = Field(..., description="Content of the document")

class DocumentIngestResponse(BaseModel):
    """
    Schema for document ingestion response.
    """
    external_id: str
    status: IngestStatus
    message: str

class DocumentIngestStatus(BaseModel):
    """
    Schema for document ingestion status.
    """
    external_id: str
    status: IngestStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    chunks_processed: int = 0
    total_chunks: int = 0

    class Config:
        orm_mode = True
