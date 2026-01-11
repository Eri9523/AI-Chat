# AI Chatbot API

FastAPI-based  for an AI chatbot application with clean architecture, JWT authentication, and vector database integration.

## Features

- JWT-based authentication (register, login, refresh tokens)
- AI chat conversations with OpenAI integration
- Document upload and RAG (Retrieval Augmented Generation)
- Vector database with ChromaDB
- Clean Architecture implementation
- MongoDB integration with MongoEngine
- Input validation with Pydantic
- Auto-generated API documentation
- CORS middleware and error handling

## Tech Stack

- **Framework**: FastAPI
- **Database**: MongoDB
- **Vector Database**: ChromaDB
- **AI Service**: OpenAI GPT-4
- **ODM**: MongoEngine
- **Authentication**: JWT
- **Validation**: Pydantic
- **Server**: Uvicorn

## Architecture

```
├── application/use_cases/    # Business logic
│   ├── ai/                  # AI-related use cases
│   └── auth/                # Authentication use cases
├── domain/
│   ├── entities/            # Core entities (User, Conversation, Message, Document)
│   ├── repositories/        # Repository interfaces
│   └── services/           # Service interfaces (AI, Vector)
├── infrastructure/
│   ├── ai/                 # AI service implementations
│   ├── config/             # Environment & JWT config
│   ├── database/           # MongoDB models & repositories
│   └── http/               # Controllers, routes & middleware
```


## Testing

### Run the Test Suite

The project includes a comprehensive test suite for all authentication and AI endpoints using pytest and mongomock (in-memory MongoDB for tests).

**To run all tests:**

```bash
cd api
pytest -s -v
```

**Test features:**
- Covers all authentication endpoints (register, login, refresh, logout, get current user)
- Covers all AI endpoints (conversations, messages, document upload, document listing, document deletion)
- Uses mongomock for fast, isolated, and dependency-free testing
- Detects regressions and integration bugs automatically

**Test files:**
- `api/tests/test_auth.py`: Authentication endpoints
- `api/tests/test_ai.py`: AI, conversation, and document endpoints

**Requirements:**
- Python 3.12+
- pytest
- pytest-asyncio
- mongomock

You can install test dependencies with:

```bash
pip install -r requirements.txt
pip install pytest pytest-asyncio mongomock
```

---
## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Setup

Create `.env` file:

```bash
NODE_ENV=development
PORT=3001
MONGODB_URI=mongodb://localhost:27017/ai_chatbot
JWT_SECRET=your_super_secret_jwt_key_here
JWT_REFRESH_SECRET=your_super_secret_refresh_key_here
JWT_EXPIRES_IN=3600
JWT_REFRESH_EXPIRES_IN=604800
CORS_ORIGIN=http://localhost:3000

# Configuración de OpenAI
OPENAI_API_KEY=sk-your_openai_api_key_here
OPENAI_MODEL=gpt-4
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Configuración de ChromaDB
CHROMA_HOST=localhost
CHROMA_PORT=8000
CHROMA_PERSIST_DIR=./chroma_db
CHROMA_COLLECTION_NAME=documents
```

### 3. Start Dependencies

Start MongoDB:
```bash
docker run --name mongodb -p 27017:27017 -d mongo:latest
```

Start ChromaDB:
```bash
docker run --name chromadb -p 8000:8000 -d chromadb/chroma:latest
```

### 4. Run the API

```bash
cd api
python -m uvicorn app:app --host 0.0.0.0 --port 3001 --reload
```

## API Endpoints

### Authentication Endpoints
| Method | Endpoint             | Description           | Auth Required |
| ------ | -------------------- | --------------------- | ------------- |
| POST   | `/api/auth/register` | User registration     | ❌            |
| POST   | `/api/auth/login`    | User login            | ❌            |
| POST   | `/api/auth/refresh`  | Refresh access token  | ❌            |
| GET    | `/api/auth/me`       | Get current user info | ✅            |
| POST   | `/api/auth/logout`   | User logout           | ✅            |

### AI Chat Endpoints
| Method | Endpoint                           | Description                | Auth Required |
| ------ | ---------------------------------- | -------------------------- | ------------- |
| POST   | `/ai/conversations`                | Create new conversation    | ✅            |
| GET    | `/ai/conversations`                | Get user's conversations   | ✅            |
| POST   | `/ai/conversations/{id}/messages`  | Send message to AI         | ✅            |
| GET    | `/ai/conversations/{id}/messages`  | Get conversation messages  | ✅            |
| DELETE | `/ai/conversations/{id}`           | Delete conversation        | ✅            |
| POST   | `/ai/documents`                    | Upload document for RAG    | ✅            |
| GET    | `/ai/documents`                    | Get user's documents       | ✅            |
| DELETE | `/ai/documents/{id}`               | Delete document            | ✅            |

### Health Endpoints
| Method | Endpoint  | Description   | Auth Required |
| ------ | --------- | ------------- | ------------- |
| GET    | `/health` | Health check  | ❌            |

## Documentation

- **Swagger UI**: http://localhost:3001/docs
- **ReDoc**: http://localhost:3001/redoc

## Example Usage

### Register User

```bash
curl -X POST "http://localhost:3001/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "name": "John Doe",
    "password": "securepassword",
    "phone": "+1234567890"
  }'
```

### Login

```bash
curl -X POST "http://localhost:3001/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword"
  }'
```

### Create Conversation

```bash
curl -X POST "http://localhost:3001/ai/conversations" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "My AI Chat"
  }'
```

### Send Message

```bash
curl -X POST "http://localhost:3001/ai/conversations/{conversation_id}/messages" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "content": "Hello, how can you help me today?"
  }'
```

### Upload Document

```bash
curl -X POST "http://localhost:3001/ai/documents" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@/path/to/your/document.pdf"
```

## Development

- Uses lifespan events for database connection
- Clean separation between HTTP layer and business logic
- Repository pattern for data access
- JWT service abstraction for token management
- Vector database integration with ChromaDB
- OpenAI API integration for chat completion
- Document processing and embeddings for RAG

## Services

### AI Service
- **OpenAI Integration**: Chat completion and embeddings
- **Text Processing**: Document content extraction
- **Token Management**: Usage tracking and optimization

### Vector Service  
- **ChromaDB**: Vector storage and similarity search
- **RAG Support**: Document retrieval for context-aware responses
- **Embedding Management**: Document vectorization and storage

## Requirements

Make sure to have:
- Python 3.12+
- Docker (for MongoDB and ChromaDB)
- Valid OpenAI API key
- Sufficient OpenAI credits for API usage
