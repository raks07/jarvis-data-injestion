from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert, update, delete
from typing import List, Optional, Dict, Any
import asyncio

from app.db.models.models import Document, Chunk
from app.schemas.ingestion import (
    DocumentIngest,
    DocumentIngestResponse,
    DocumentIngestStatus,
    IngestStatus,
)
from app.services.embedding import EmbeddingService


class IngestionService:
    """
    Service for document ingestion and embedding generation.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.embedding_service = EmbeddingService(db)

    async def ingest_document(
        self, document_data: DocumentIngest
    ) -> DocumentIngestResponse:
        """
        Ingest a document and generate embeddings.
        """
        # Check if document already exists
        stmt = select(Document).where(Document.external_id == document_data.external_id)
        result = await self.db.execute(stmt)
        existing_doc = result.scalars().first()

        if existing_doc:
            # Update existing document
            existing_doc.title = document_data.title
            existing_doc.description = document_data.description

            # Delete existing chunks and embeddings
            await self.db.execute(
                delete(Chunk).where(Chunk.document_id == existing_doc.id)
            )

            # Commit changes
            await self.db.commit()
            document_id = existing_doc.id
        else:
            # Create new document
            stmt = (
                insert(Document)
                .values(
                    external_id=document_data.external_id,
                    title=document_data.title,
                    description=document_data.description,
                )
                .returning(Document.id)
            )
            result = await self.db.execute(stmt)
            document_id = result.scalar_one()

            # Commit changes
            await self.db.commit()

        # Process document content in the background
        # In a real implementation, this would be handled by a task queue like Celery
        asyncio.create_task(self._process_document(document_id, document_data))

        return DocumentIngestResponse(
            external_id=document_data.external_id,
            status=IngestStatus.PENDING,
            message="Document ingestion started",
        )

    async def _process_document(self, document_id: int, document_data: DocumentIngest):
        """
        Process document content and generate embeddings.
        This would typically be handled by a task queue in a production environment.
        """
        import httpx
        from app.core.config import settings

        try:
            # Update status to PROCESSING if we have a callback
            if document_data.callback_url:
                async with httpx.AsyncClient() as client:
                    await client.post(
                        document_data.callback_url,
                        json={
                            "externalId": document_data.external_id,
                            "status": IngestStatus.PROCESSING,
                        },
                        headers={"Content-Type": "application/json"},
                    )

            # Create chunks from document
            # In a real implementation, this would use a text splitter
            from langchain.text_splitter import RecursiveCharacterTextSplitter

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )

            chunks = text_splitter.split_text(document_data.content)
            total_chunks = len(chunks)

            for i, chunk_content in enumerate(chunks):
                # Insert chunk
                stmt = (
                    insert(Chunk)
                    .values(document_id=document_id, content=chunk_content, position=i)
                    .returning(Chunk.id)
                )
                result = await self.db.execute(stmt)
                chunk_id = result.scalar_one()

                # Generate embedding
                await self.embedding_service.generate_embedding(chunk_id)

                # Commit each chunk to avoid large transactions
                await self.db.commit()

                # Update progress if we have a callback URL
                if document_data.callback_url and (i % 5 == 0 or i == total_chunks - 1):
                    async with httpx.AsyncClient() as client:
                        await client.post(
                            document_data.callback_url,
                            json={
                                "externalId": document_data.external_id,
                                "status": IngestStatus.PROCESSING,
                                "chunksProcessed": i + 1,
                                "totalChunks": total_chunks,
                            },
                            headers={"Content-Type": "application/json"},
                        )

            # Final update to mark as completed
            if document_data.callback_url:
                async with httpx.AsyncClient() as client:
                    await client.post(
                        document_data.callback_url,
                        json={
                            "externalId": document_data.external_id,
                            "status": IngestStatus.COMPLETED,
                            "chunksProcessed": total_chunks,
                            "totalChunks": total_chunks,
                        },
                        headers={"Content-Type": "application/json"},
                    )

        except Exception as e:
            print(f"Error processing document: {str(e)}")

            # Send error if we have callback URL
            if document_data.callback_url:
                try:
                    async with httpx.AsyncClient() as client:
                        await client.post(
                            document_data.callback_url,
                            json={
                                "externalId": document_data.external_id,
                                "status": IngestStatus.FAILED,
                                "errorMessage": str(e),
                            },
                            headers={"Content-Type": "application/json"},
                        )
                except Exception as callback_err:
                    print(f"Error sending failure callback: {str(callback_err)}")

            # Re-raise the error
            raise

    async def get_ingestion_status(
        self, document_external_id: str
    ) -> Optional[DocumentIngestStatus]:
        """
        Get the status of a document ingestion process.
        """
        # In a real implementation, this would check a status table
        # For now, just return a placeholder status
        stmt = select(Document).where(Document.external_id == document_external_id)
        result = await self.db.execute(stmt)
        document = result.scalars().first()

        if not document:
            return None

        # Count chunks
        stmt = select(Chunk).where(Chunk.document_id == document.id)
        result = await self.db.execute(stmt)
        chunks = result.scalars().all()

        return DocumentIngestStatus(
            external_id=document_external_id,
            status=IngestStatus.COMPLETED if chunks else IngestStatus.PROCESSING,
            started_at=document.created_at,
            completed_at=document.updated_at if chunks else None,
            chunks_processed=len(chunks),
            total_chunks=len(chunks),
        )

    async def cancel_ingestion(self, document_external_id: str) -> None:
        """
        Cancel an ongoing ingestion process.
        """
        # Find the document by external ID
        stmt = select(Document).where(Document.external_id == document_external_id)
        result = await self.db.execute(stmt)
        document = result.scalars().first()

        if not document:
            raise ValueError(f"Document with ID {document_external_id} not found")

        # Delete all chunks for the document
        stmt = delete(Chunk).where(Chunk.document_id == document.id)
        await self.db.execute(stmt)
        await self.db.commit()

        # In a real application with a task queue, we would also need to cancel
        # any pending or running background tasks for this document
