from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.schemas.selection import DocumentSelectionRequest, DocumentSelectionResponse
from app.services.selection import SelectionService

router = APIRouter()

@router.post("/", response_model=DocumentSelectionResponse)
async def select_documents(
    request: DocumentSelectionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Select documents for Q&A context.
    """
    selection_service = SelectionService(db)
    return await selection_service.select_documents(request)

@router.get("/", response_model=DocumentSelectionResponse)
async def get_selected_documents(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the currently selected documents for a user.
    """
    selection_service = SelectionService(db)
    selection = await selection_service.get_selected_documents(user_id)
    if not selection:
        return DocumentSelectionResponse(user_id=user_id, document_ids=[])
    return selection
