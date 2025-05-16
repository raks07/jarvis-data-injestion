#!/usr/bin/env python
# filepath: /Users/user/Documents/dev/projects/misc/jarvis/python-backend/app/db/init_db.py
import asyncio
import sys
import os

# Add the parent directory to sys.path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text
from sqlalchemy import Table, Column, MetaData
from app.core.config import settings
from app.db.models.models import Base


async def init_db():
    """Initialize the database with tables and pgvector extension."""
    print("Creating database connection...")
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True,
    )

    async with engine.begin() as conn:
        print("Creating pgvector extension...")
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))

        print("Creating tables...")
        # Drop all tables if they exist
        await conn.run_sync(Base.metadata.drop_all)

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

        # Add vector column to embeddings table
        print("Adding vector column to embeddings table...")
        await conn.execute(
            text(
                """
            ALTER TABLE embeddings
            ADD COLUMN IF NOT EXISTS vector vector(768);
            """
            )
        )

    await engine.dispose()
    print("Database initialization completed!")


if __name__ == "__main__":
    print("Starting database initialization...")
    asyncio.run(init_db())
