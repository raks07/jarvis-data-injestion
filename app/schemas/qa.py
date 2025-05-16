from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class QuestionRequest(BaseModel):
    """
    Schema for question request.
    """
    text: str = Field(..., description="Question text")
    user_id: str = Field(..., description="ID of the user asking the question")
    session_id: Optional[int] = Field(None, description="ID of the QA session (if continuing a session)")
    document_ids: Optional[List[str]] = Field(None, description="List of document IDs to include in the search context")

class Source(BaseModel):
    """
    Schema for answer source.
    """
    document_id: str
    document_title: str
    excerpt: str
    relevance_score: float

    class Config:
        orm_mode = True

class AnswerResponse(BaseModel):
    """
    Schema for answer response.
    """
    text: str
    sources: List[Source]
    session_id: int

    class Config:
        orm_mode = True

class QuestionAnswer(BaseModel):
    """
    Schema for a question and its answer.
    """
    id: int
    text: str
    timestamp: datetime
    answer: AnswerResponse

    class Config:
        orm_mode = True

class QASession(BaseModel):
    """
    Schema for a QA session.
    """
    id: int
    user_id: str
    questions: List[QuestionAnswer]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
