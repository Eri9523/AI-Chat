from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from contextlib import asynccontextmanager
from infrastructure.config.environment import config
from infrastructure.http.routes.auth_routes import router as auth_router
from infrastructure.http.routes.ai_routes import router as ai_router
from infrastructure.http.middlewares.error_handler import add_error_handlers
from infrastructure.database.connection import connect_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_database()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Chatbot API",
        description="API for API Chatbot application",
        version="1.0.0",
        lifespan=lifespan  # Add lifespan here
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[config["cors"]["origin"]] if config["cors"]["origin"] else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "ok", "timestamp": datetime.now().isoformat()}

    # Include routers
    app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(ai_router, prefix="/api/ai", tags=["AI"])

    # Add error handlers
    add_error_handlers(app)

    return app

app = create_app()
