import os
from dotenv import load_dotenv

load_dotenv()

config = {
    "env": os.getenv("NODE_ENV"),
    "port": os.getenv("PORT"),
    "mongodb": {
        "uri": os.getenv("MONGODB_URI"),
    },
    "jwt": {
        "secret": os.getenv("JWT_SECRET"),
        "refresh_secret": os.getenv("JWT_REFRESH_SECRET"),
        "expires_in": int(os.getenv("JWT_EXPIRES_IN", "3600")),
        "refresh_expires_in": int(os.getenv("JWT_REFRESH_EXPIRES_IN", "604800"))
    },
    "cors": {
        "origin": os.getenv("CORS_ORIGIN")
    },
    "openai": {
    "api_key": os.getenv("OPENAI_API_KEY"),
    "model": os.getenv("OPENAI_MODEL", "gpt-4"),
    "embedding_model": os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    },
    "chroma": {
        "host": os.getenv("CHROMA_HOST", "localhost"),
        "port": int(os.getenv("CHROMA_PORT", "8000")),
        "persist_directory": os.getenv("CHROMA_PERSIST_DIR", "./chroma_db"),
        "collection_name": os.getenv("CHROMA_COLLECTION_NAME", "documents")
    }
}
