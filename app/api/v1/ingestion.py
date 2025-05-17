from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.session import get_db
from app.schemas.ingestion import (
    DocumentIngest,
    DocumentIngestResponse,
    DocumentIngestStatus,
)
from app.services.ingestion import IngestionService

router = APIRouter()


@router.post(
    "/", response_model=DocumentIngestResponse, status_code=status.HTTP_202_ACCEPTED
)
async def ingest_document(document: DocumentIngest, db: AsyncSession = Depends(get_db)):
    """
    Ingest a document and generate embeddings.
    """
    ingestion_service = IngestionService(db)
    return await ingestion_service.ingest_document(document)


@router.get("/{document_id}", response_model=DocumentIngestStatus)
async def get_ingestion_status(document_id: str, db: AsyncSession = Depends(get_db)):
    """
    Get the status of a document ingestion process.
    """
    ingestion_service = IngestionService(db)
    result_status = await ingestion_service.get_ingestion_status(document_id)
    if not result_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingestion for document {document_id} not found",
        )
    return result_status


@router.delete("/{document_id}")
async def cancel_ingestion(document_id: str, db: AsyncSession = Depends(get_db)):
    """
    Cancel an ongoing document ingestion process.
    """
    ingestion_service = IngestionService(db)
    try:
        await ingestion_service.cancel_ingestion(document_id)
        return {"detail": f"Ingestion for document {document_id} cancelled"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cannot cancel ingestion: {str(e)}",
        )
