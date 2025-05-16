from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert, update, delete
from typing import List, Optional

from app.db.models.models import DocumentSelection
from app.schemas.selection import DocumentSelectionRequest, DocumentSelectionResponse

class SelectionService:
    """
    Service for document selection.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def select_documents(self, request: DocumentSelectionRequest) -> DocumentSelectionResponse:
        """
        Select documents for Q&A context.
        """
        # Check if selection already exists
        stmt = select(DocumentSelection).where(DocumentSelection.user_id == request.user_id)
        result = await self.db.execute(stmt)
        existing_selection = result.scalars().first()
        
        if existing_selection:
            # Update existing selection
            existing_selection.document_ids = request.document_ids
            await self.db.commit()
            
            return DocumentSelectionResponse(
                user_id=request.user_id,
                document_ids=request.document_ids,
                updated_at=existing_selection.updated_at
            )
        else:
            # Create new selection
            stmt = insert(DocumentSelection).values(
                user_id=request.user_id,
                document_ids=request.document_ids
            ).returning(DocumentSelection)
            result = await self.db.execute(stmt)
            selection = result.scalar_one()
            
            await self.db.commit()
            
            return DocumentSelectionResponse(
                user_id=selection.user_id,
                document_ids=selection.document_ids,
                updated_at=selection.updated_at
            )
    
    async def get_selected_documents(self, user_id: str) -> Optional[DocumentSelectionResponse]:
        """
        Get the currently selected documents for a user.
        """
        stmt = select(DocumentSelection).where(DocumentSelection.user_id == user_id)
        result = await self.db.execute(stmt)
        selection = result.scalars().first()
        
        if not selection:
            return None
        
        return DocumentSelectionResponse(
            user_id=selection.user_id,
            document_ids=selection.document_ids,
            updated_at=selection.updated_at
        )
