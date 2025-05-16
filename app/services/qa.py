from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert, update, delete
from typing import List, Optional, Dict, Any

from app.db.models.models import QASession, Question, Answer, Source, Document, Chunk
from app.schemas.qa import QuestionRequest, AnswerResponse
from app.services.embedding import EmbeddingService
from app.services.llm import LLMService

class QAService:
    """
    Service for question answering.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.embedding_service = EmbeddingService(db)
        self.llm_service = LLMService()
    
    async def answer_question(self, request: QuestionRequest) -> AnswerResponse:
        """
        Answer a question based on document content.
        """
        # Get or create QA session
        session_id = request.session_id
        if not session_id:
            # Create new session
            stmt = insert(QASession).values(
                user_id=request.user_id
            ).returning(QASession.id)
            result = await self.db.execute(stmt)
            session_id = result.scalar_one()
        
        # Create question
        stmt = insert(Question).values(
            session_id=session_id,
            text=request.text,
            document_ids=request.document_ids
        ).returning(Question.id)
        result = await self.db.execute(stmt)
        question_id = result.scalar_one()
        
        # Commit to ensure we have IDs
        await self.db.commit()
        
        # Get similar chunks
        similar_chunks = await self.embedding_service.get_similar_chunks(
            request.text,
            limit=5,
            document_ids=request.document_ids
        )
        
        # Create context from similar chunks
        context = "\n\n".join([chunk["chunk"].content for chunk in similar_chunks])
        
        # Generate answer using LLM
        answer_text = await self.llm_service.generate_answer(request.text, context)
        
        # Create answer
        stmt = insert(Answer).values(
            question_id=question_id,
            text=answer_text
        ).returning(Answer.id)
        result = await self.db.execute(stmt)
        answer_id = result.scalar_one()
        
        # Store sources
        sources = []
        for item in similar_chunks:
            chunk = item["chunk"]
            score = item["score"]
            
            # Get document
            stmt = select(Document).where(Document.id == chunk.document_id)
            result = await self.db.execute(stmt)
            document = result.scalars().first()
            
            # Create source
            stmt = insert(Source).values(
                answer_id=answer_id,
                chunk_id=chunk.id,
                relevance_score=score
            )
            await self.db.execute(stmt)
            
            # Add to sources list for response
            sources.append({
                "document_id": document.external_id,
                "document_title": document.title,
                "excerpt": chunk.content,
                "relevance_score": score
            })
        
        # Commit changes
        await self.db.commit()
        
        # Return response
        return AnswerResponse(
            text=answer_text,
            sources=sources,
            session_id=session_id
        )
    
    async def get_qa_history(self, user_id: str, limit: int = 10, offset: int = 0) -> List[QASession]:
        """
        Get the history of question-answering sessions for a user.
        """
        stmt = select(QASession).where(QASession.user_id == user_id).order_by(QASession.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_qa_session(self, session_id: int) -> Optional[QASession]:
        """
        Get a specific question-answering session.
        """
        stmt = select(QASession).where(QASession.id == session_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()
