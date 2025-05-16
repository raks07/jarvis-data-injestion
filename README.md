# Python Backend for Document Ingestion and RAG-based Q&A

This component handles document ingestion, embedding generation, and Retrieval-Augmented Generation (RAG) based question answering.

## Features

- Document ingestion and processing
- Embedding generation using LLM libraries
- Vector storage for efficient retrieval
- RAG-based Q&A functionality
- Document selection for Q&A context

## Technology Stack

- FastAPI: High-performance async API framework
- SQLAlchemy: ORM for database interactions
- pgvector: PostgreSQL extension for vector storage
- Sentence-Transformers or OpenAI API: For generating embeddings
- Hugging Face Transformers: For LLM integration
- pytest: For testing

## Setup

### Prerequisites

- Python 3.9+
- PostgreSQL with pgvector extension

### Installation

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment variables:

```bash
cp .env.example .env
# Edit .env file with your settings
```

4. Generate a secure SECRET_KEY:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
# Copy the output and use it as your SECRET_KEY in .env file
```

5. Run database migrations:

```bash
alembic upgrade head
```

### Running the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at <http://localhost:8000>.

## Project Structure

```
python-backend/
├── app/                    # Application package
│   ├── api/                # API endpoints
│   │   ├── ingestion.py    # Document ingestion endpoints
│   │   ├── qa.py           # Question answering endpoints
│   │   └── selection.py    # Document selection endpoints
│   ├── core/               # Core modules
│   │   ├── config.py       # Application configuration
│   │   └── security.py     # Security utilities
│   ├── db/                 # Database modules
│   │   ├── models.py       # Database models
│   │   └── session.py      # Database session management
│   ├── services/           # Business logic
│   │   ├── embedding.py    # Embedding generation
│   │   ├── ingestion.py    # Document processing
│   │   ├── retrieval.py    # Vector retrieval
│   │   └── llm.py          # Language model service
│   └── main.py             # Application entry point
├── tests/                  # Test directory
│   ├── conftest.py         # Test configuration
│   └── ...                 # Test modules
├── alembic/                # Database migrations
├── alembic.ini             # Alembic configuration
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker configuration
└── .env.example            # Example environment variables
```

## API Documentation

Once the application is running, API documentation is available at:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

## Development

### Running Tests

```bash
pytest
```

### Database Migrations

```bash
# Generate migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```
