from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Float,
    Boolean,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()


class Document(Base):
    """
    Represents a reference to a document in the NestJS backend.
    We store only the reference here, not the actual document content.
    """

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    chunks = relationship(
        "Chunk", back_populates="document", cascade="all, delete-orphan"
    )
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )


class Chunk(Base):
    """
    Represents a chunk of text from a document.
    """

    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    document = relationship("Document", back_populates="chunks")
    content = Column(Text, nullable=False)
    position = Column(Integer, nullable=False)
    embedding = relationship(
        "Embedding", back_populates="chunk", uselist=False, cascade="all, delete-orphan"
    )
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Embedding(Base):
    """
    Represents an embedding vector for a chunk of text.
    """

    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True, index=True)
    chunk_id = Column(Integer, ForeignKey("chunks.id"), nullable=False)
    chunk = relationship("Chunk", back_populates="embedding")
    # Import Vector column type only when creating tables to avoid import errors
    try:
        from pgvector.sqlalchemy import Vector

        vector = Column(
            Vector(384), nullable=True
        )  # Match the EMBEDDING_DIMENSION in config
    except ImportError:
        # This will allow the models to be imported without pgvector installed
        pass
    model_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class QASession(Base):
    """
    Represents a question-answering session.
    """

    __tablename__ = "qa_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)  # From NestJS backend
    questions = relationship(
        "Question", back_populates="session", cascade="all, delete-orphan"
    )
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )


class Question(Base):
    """
    Represents a question in a QA session.
    """

    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("qa_sessions.id"), nullable=False)
    session = relationship("QASession", back_populates="questions")
    text = Column(Text, nullable=False)
    answer = relationship(
        "Answer", back_populates="question", uselist=False, cascade="all, delete-orphan"
    )
    document_ids = Column(
        ARRAY(String), nullable=True
    )  # Array of external document IDs
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Answer(Base):
    """
    Represents an answer to a question.
    """

    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    question = relationship("Question", back_populates="answer")
    text = Column(Text, nullable=False)
    sources = relationship(
        "Source", back_populates="answer", cascade="all, delete-orphan"
    )
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Source(Base):
    """
    Represents a source for an answer.
    """

    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    answer_id = Column(Integer, ForeignKey("answers.id"), nullable=False)
    answer = relationship("Answer", back_populates="sources")
    chunk_id = Column(Integer, ForeignKey("chunks.id"), nullable=False)
    chunk = relationship("Chunk")
    relevance_score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class DocumentSelection(Base):
    """
    Represents a user's selection of documents for Q&A.
    """

    __tablename__ = "document_selections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)  # From NestJS backend
    document_ids = Column(
        ARRAY(String), nullable=False
    )  # Array of external document IDs
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )
