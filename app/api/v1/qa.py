from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.session import get_db
from app.schemas.qa import QuestionRequest, AnswerResponse, QASession
from app.services.qa import QAService

router = APIRouter()

@router.post("/", response_model=AnswerResponse)
async def ask_question(
    request: QuestionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Ask a question and get an answer based on the document content.
    """
    qa_service = QAService(db)
    return await qa_service.answer_question(request)

@router.get("/history", response_model=List[QASession])
async def get_qa_history(
    user_id: str,
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the history of question-answering sessions for a user.
    """
    qa_service = QAService(db)
    return await qa_service.get_qa_history(user_id, limit, offset)

@router.get("/history/{session_id}", response_model=QASession)
async def get_qa_session(
    session_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific question-answering session.
    """
    qa_service = QAService(db)
    session = await qa_service.get_qa_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"QA session {session_id} not found"
        )
    return session
